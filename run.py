from __future__ import print_function

import datetime
import os
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']



def init():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def create_event(creds, calendar_id, event_summary, year, month, date, start_time, end_time):
    service = build('calendar', 'v3', credentials=creds)

    if not start_time and not end_time:
        event = {
            'summary': event_summary,
            'start': {
                'date': f'{year}-{month}-{date}',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
            'end': {
                'date': f'{year}-{month}-{date}',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
        }
    elif not end_time:
        event = {
            'summary': event_summary,
            'start': {
                'dateTime': f'{year}-{month}-{date}T{start_time}:00',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
            'end': {
                'dateTime': f'{year}-{month}-{date}T{start_time}:00',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
        }
    else:
        # 予定のパラメータを指定
        event = {
            'summary': event_summary,
            'start': {
                'dateTime': f'{year}-{month}-{date}T{start_time}:00',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
            'end': {
                'dateTime': f'{year}-{month}-{date}T{end_time}:00',
                'timeZone': 'JST',  # タイムゾーンを適宜変更してください
            },
        }

    # 予定を作成
    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
    except HttpError as e:
        print(f"Error: {e}")
    
    return

def remove_event(creds, calendar_id, event_id):
    service = build('calendar', 'v3', credentials=creds)

    # 予定を削除
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"Event deleted")
    except HttpError as e:
        print(f"Error: {e}")

    return

def list_events_by_date(creds, calendar_id, year, month, date):
    jst = pytz.timezone('Asia/Tokyo')
    service = build('calendar', 'v3', credentials=creds)
    
    year = int(year)
    month = int(month)
    date = int(date)
    
    # 指定された日付をJSTに変換
    start_dt = jst.localize(datetime.datetime(year, month, date, 0, 0, 0))
    end_dt = jst.localize(datetime.datetime(year, month, date, 23, 59, 59))
    
    # JSTでの開始日時と終了日時を文字列に変換
    start_str = start_dt.astimezone(pytz.utc).isoformat()
    end_str = end_dt.astimezone(pytz.utc).isoformat()
    
    # JSTでのイベント取得
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_str,
        timeMax=end_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    # events_result = service.events().list(
    #     calendarId=calendar_id,
    #     timeMin=f'{year}-{month}-{date}T00:00:00Z',
    #     timeMax=f'{year}-{month}-{date}T23:59:59Z',
    #     singleEvents=True,
    #     orderBy='startTime'
    # ).execute()

    events = events_result.get('items', [])

    # for event in events:
    #     start = event.get('start', {}).get(
    #         'dateTime', event.get('start', {}).get('date', ''))
    #     end = event.get('end', {}).get(
    #         'dateTime', event.get('end', {}).get('date', ''))
    #     summary = event.get('summary', '')
    #     output = f'{start} ~ {end} {summary}'
    #     output = output.replace('T', ' ')
    #     output = output.replace(':00+09:00', '')
    #     print(output)
    
    # 年-月-日を出力
    print(f'{year}-{month}-{date}')

    for event in events:
        start = event.get('start', {}).get(
            'dateTime', event.get('start', {}).get('date', ''))
        end = event.get('end', {}).get(
            'dateTime', event.get('end', {}).get('date', ''))
        summary = event.get('summary', '')
        id = event.get('id', '')
        
        flag_all_day = 'T' not in start and 'T' not in end
        if flag_all_day:
            # 終日の予定の場合はsummaryのみ出力
            all_day_str = 'All Day'.ljust(12)
            summary = summary.ljust(30)
            print(f'{all_day_str} {summary} {id}')
        else:
            # 時間帯とsummaryを一行ずつ出力
            start_dt = datetime.datetime.strptime(
                start, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
            end_dt = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
            time_range = f'{start_dt.strftime("%H:%M")}~{end_dt.strftime("%H:%M")}'
            time_range = time_range.ljust(12)
            summary = summary.ljust(30)
            print(f'{time_range} {summary} {id}')
    return

def move_to_parent_directory(current_year, current_month, current_date):
    if current_date:
        current_date = None
    elif current_month:
        current_month = None
    elif current_year:
        current_year = None
    else:
        print("You are already at the top directory")
    return current_year, current_month, current_date

def change_directory(current_year, current_month, current_date, command):
    print(command)
    if command.startswith('...'):
        if len(command) == 3:
            current_year, current_month, current_date = move_to_parent_directory(current_year, current_month, current_date)
            return current_year, current_month, current_date
        if len(command) == 4:
            if command[3] == '/':
                current_year, current_month, current_date = move_to_parent_directory(current_year, current_month, current_date)
                return current_year, current_month, current_date
            else:
                print("Invalid command : 1")
        new_command = command[4:]
        current_year, current_month, current_date = move_to_parent_directory(current_year, current_month, current_date)
        current_year, current_month, current_date = move_to_parent_directory(
            current_year, current_month, current_date)
        return change_directory(current_year, current_month, current_date, new_command)
    if command.startswith('..'):
        if len(command) == 2:
            return move_to_parent_directory(current_year, current_month, current_date)
        if len(command) == 3:
            if command[2] == '/':
                return move_to_parent_directory(current_year, current_month, current_date)
            else:
                print("Invalid command : 2")
        new_command = command[3:]
        current_year, current_month, current_date = move_to_parent_directory(current_year, current_month, current_date)
        current_year, current_month, current_date = change_directory(current_year, current_month, current_date, new_command)
        return current_year, current_month, current_date

    elif command.startswith('.'):
        if len(command) == 1:
            return current_year, current_month, current_date
        if len(command) == 2:
            if command[1] == '/':
                return current_year, current_month, current_date
            else:
                print("Invalid command : 1")
        new_command = command[2:]
        return change_directory(current_year, current_month, current_date, new_command)
    else:
        if not current_year:
            if command.isdigit():
                if int(command) < 0 or int(command) > 9999:
                    print("Invalid command : 3")
                current_year = command
            else:
                print("Invalid command : 4")
        elif not current_month:
            if command[:2] not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                print("Invalid command : 5")
            else:
                current_month = command[:2]
                if len(command) > 2:
                    new_command = command[3:]
                    current_year, current_month, current_date = change_directory(current_year, current_month, current_date, new_command)
        elif not current_date:
            if command[:2] not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', \
                                    '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', \
                                    '25', '26', '27', '28', '29', '30', '31']:
                print("Invalid command : 6")
            else:
                current_date = command[:2]
                if len(command) > 2:
                    new_command = command[3:]
                    current_year, current_month, current_date = change_directory(current_year, current_month, current_date, new_command)
        else:
            print("You are already at the bottom level")
        return current_year, current_month, current_date
    
def week_to_num(week):
    if week == "Mon":
        return 0
    elif week == "Tue":
        return 1
    elif week == "Wed":
        return 2
    elif week == "Thu":
        return 3
    elif week == "Fri":
        return 4
    elif week == "Sat":
        return 5
    elif week == "Sun":
        return 6
    
def get_week_events(creds, calendar_id, year, month, week):
    jst = pytz.timezone('Asia/Tokyo')
    service = build('calendar', 'v3', credentials=creds)

    year = int(year)
    month = int(month)
    
    # 指定した月の最初の日を取得
    start_date = datetime.date(year, month, 1)

    # 最初の日から最後の日までの日付を生成
    dates = [
        start_date + datetime.timedelta(days=i)
        for i in range((datetime.date(year, month+1, 1) - start_date).days)
    ]

    weeks = [date for date in dates if date.weekday() == week_to_num(week)]

    # 月曜日の日付を文字列に変換
    start_dates = [date.strftime('%Y-%m-%d') for date in weeks]

    # イベントを取得
    events = []
    current_date = None
    for start_date in start_dates:
        
        # 日付が変わったら日付を出力
        if current_date != start_date:
            current_date = start_date
            # 空白の行を挿入して日付を出力
            print()
            print(f'{start_date}')
            events = []
            
        start_datetime = datetime.datetime.strptime(
            start_date, '%Y-%m-%d').replace(tzinfo=jst).isoformat()

        end_datetime = (datetime.datetime.strptime(
            start_date, '%Y-%m-%d') + datetime.timedelta(days=1)).replace(tzinfo=jst).isoformat()
        
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        except:
            print("Error")
            return

        events.extend(events_result.get('items', []))
        
        for event in events:
            start = event.get('start', {}).get(
                'dateTime', event.get('start', {}).get('date', ''))
            end = event.get('end', {}).get(
                'dateTime', event.get('end', {}).get('date', ''))
            summary = event.get('summary', '')
            id = event.get('id', '')

            flag_all_day = 'T' not in start and 'T' not in end
            if flag_all_day:
                # 終日の予定の場合はsummaryのみ出力
                all_day_str = 'All Day'.ljust(12)
                summary = summary.ljust(30)
                print(f'{all_day_str} {summary} {id}')
            else:
                # 時間帯とsummaryを一行ずつ出力
                start_dt = datetime.datetime.strptime(
                    start, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
                end_dt = datetime.datetime.strptime(
                    end, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
                time_range = f'{start_dt.strftime("%H:%M")}~{end_dt.strftime("%H:%M")}'
                time_range = time_range.ljust(12)
                summary = summary.ljust(30)
                print(f'{time_range} {summary} {id}')
    return

def num_to_week(num):
    if num == 0:
        return "Mon"
    elif num == 1:
        return "Tue"
    elif num == 2:
        return "Wed"
    elif num == 3:
        return "Thu"
    elif num == 4:
        return "Fri"
    elif num == 5:
        return "Sat"
    elif num == 6:
        return "Sun"

def get_one_week_events(creds, calendar_id, year, month, week_num):
    jst = pytz.timezone('Asia/Tokyo')
    service = build('calendar', 'v3', credentials=creds)

    year = int(year)
    month = int(month)

    # 指定した月の最初の日を取得
    start_date = datetime.date(year, month, 1)

    # 最初の日から最後の日までの日付を生成
    dates = [
        start_date + datetime.timedelta(days=i)
        for i in range((datetime.date(year, month+1, 1) - start_date).days)
    ]

    week_dates = []
    
    for date in dates:
        if date.day > 7 * (week_num-1) and date.day <= 7 * week_num:
            week_dates.append(date)

    # 1週間の日付を文字列に変換
    start_dates = [[date.strftime('%Y-%m-%d'), date.weekday()] for date in week_dates]

    # イベントを取得
    events = []
    current_date = None
    for start_date in start_dates:

        # 日付が変わったら日付を出力
        if current_date != start_date[0]:
            current_date = start_date[0]
            week = num_to_week(start_date[1])
            # 空白の行を挿入して日付を出力
            print()
            print(f'{start_date[0]} {week}')
            events = []

        start_datetime = datetime.datetime.strptime(
            start_date[0], '%Y-%m-%d').replace(tzinfo=jst).isoformat()

        end_datetime = (datetime.datetime.strptime(
            start_date[0], '%Y-%m-%d') + datetime.timedelta(days=1)).replace(tzinfo=jst).isoformat()

        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        except:
            print("Error")
            return

        events.extend(events_result.get('items', []))

        for event in events:
            start = event.get('start', {}).get(
                'dateTime', event.get('start', {}).get('date', ''))
            end = event.get('end', {}).get(
                'dateTime', event.get('end', {}).get('date', ''))
            summary = event.get('summary', '')
            id = event.get('id', '')

            flag_all_day = 'T' not in start and 'T' not in end
            if flag_all_day:
                # 終日の予定の場合はsummaryのみ出力
                all_day_str = 'All Day'.ljust(12)
                summary = summary.ljust(30)
                print(f'{all_day_str} {summary} {id}')
            else:
                # 時間帯とsummaryを一行ずつ出力
                start_dt = datetime.datetime.strptime(
                    start, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
                end_dt = datetime.datetime.strptime(
                    end, '%Y-%m-%dT%H:%M:%S%z').astimezone(jst)
                time_range = f'{start_dt.strftime("%H:%M")}~{end_dt.strftime("%H:%M")}'
                time_range = time_range.ljust(12)
                summary = summary.ljust(30)
                print(f'{time_range} {summary} {id}')
    return

def main(creds):
    current_calendar_id = 'primary'
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now().astimezone(jst)
    current_year = now.year
    current_month = now.strftime('%m')
    current_date = now.strftime('%d')

    while True:
        path = f'({current_calendar_id}) {current_year}/{current_month}/{current_date}'
        if current_year and current_month and current_date:
            print_path = path
        elif current_year and current_month:
            print_path = f'({current_calendar_id}) {current_year}/{current_month}/'
        elif current_year:
            print_path = f'({current_calendar_id}) {current_year}/'
        command = input(f'{print_path} >>> ')

        # current_dirの予定を表示
        if command == "ls":
            if current_year and current_month and current_date:
                list_events_by_date(creds, current_calendar_id,
                                    current_year, current_month, current_date)
                
        elif command.startswith("ls -"):
            week = command[4:]
            if week in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                if current_year and current_month:
                    get_week_events(creds, current_calendar_id, current_year, current_month, week)
                    print()
            elif week in ["1", "2", "3", "4", "5"]:
                if current_year and current_month:
                    get_one_week_events(creds, current_calendar_id, current_year, current_month, int(week))
                    print()
            else:
                print("Invalid command")
        
        # dirを指定してls
        elif command.startswith("ls"):
            command = command[3:]
            ls_commands = command.split(" ")
            for ls_command in ls_commands:                              
                year, month, date = change_directory(current_year, current_month, current_date, ls_command)
                list_events_by_date(creds, current_calendar_id, year, month, date)
        
        # 予定をidで削除 
        if command.startswith("rm"):
            rm_command = command[3:]
            remove_event(creds, current_calendar_id, rm_command)

        if command.startswith("cd"):
            mv_command = command[3:]
            current_year, current_month, current_date = change_directory(current_year, current_month, current_date, mv_command)

        # create_event(creds, calendar_id, event_summary, year, month, date, start_time, end_time)
                
        if command.startswith("add"):
            add_command = command.split(" ")
            if current_year and current_month:
                if len(add_command) == 2:
                    # 終日の場合
                    summary = add_command[1]
                    create_event(creds, current_calendar_id, summary, current_year, current_month, current_date, None, None)
                elif len(add_command) == 3:
                    # 開始時間のみ指定
                    start_time = add_command[1]
                    summary = add_command[2]
                    if ":" not in start_time:
                        print("Invalid time format")
                        continue
                    if len(start_time) != 5:
                        print("Invalid time format")
                        continue
                    start_hour = int(start_time[:2])
                    start_minute = int(start_time[3:])
                    if start_hour > 23 or start_hour < 0 or start_minute > 59 or start_minute < 0:
                        print("Invalid time format")
                        continue
                    create_event(creds, current_calendar_id, summary, current_year, current_month, current_date, start_time, None)
                elif len(add_command) == 4:
                    # 開始時間と終了時間の指定
                    start_time = add_command[1]
                    end_time = add_command[2]
                    summary = add_command[3]
                    if ":" not in start_time or ":" not in end_time:
                        print("Invalid time format")
                        continue
                    if len(start_time) != 5 or len(end_time) != 5:
                        print("Invalid time format")
                        continue
                    if start_time > end_time:
                        print("Invalid time format")
                        continue
                    start_hour = int(start_time[:2])
                    start_minute = int(start_time[3:])
                    end_hour = int(end_time[:2])
                    end_minute = int(end_time[3:])
                    if start_hour > 23 or start_hour < 0 or start_minute > 59 or start_minute < 0:
                        print("Invalid time format")
                        continue
                    if end_hour > 23 or end_hour < 0 or end_minute > 59 or end_minute < 0:
                        print("Invalid time format")
                        continue
                    create_event(creds, current_calendar_id, summary, current_year, current_month, current_date, start_time, end_time)
            else:
                print("Invalid command")

        if command == "clear":
            os.system('clear')

        # 入力に応じた処理を実行
        if command == "exit":
            break  # ループを終了する条件
        elif command == "run_script":
            # 実行したいPythonコードを記述
            print("Running script...")
            # ここにコードを記述

    print("Exiting the program")


if __name__ == '__main__':
    # 初期化処理を実行
    creds = init()
    # ターミナルからの入力を取得
    main(creds)
