from __future__ import print_function

import datetime
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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

    # try:
    #     service = build('calendar', 'v3', credentials=creds)

    #     # Call the Calendar API
    #     now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    #     print('Getting the upcoming 10 events')
    #     events_result = service.events().list(calendarId='primary', timeMin=now,
    #                                           maxResults=10, singleEvents=True,
    #                                           orderBy='startTime').execute()
    #     events = events_result.get('items', [])

    #     if not events:
    #         print('No upcoming events found.')
    #         return

    #     # Prints the start and name of the next 10 events
    #     for event in events:
    #         start = event['start'].get('dateTime', event['start'].get('date'))
    #         print(start, event['summary'])
            
    #     events = events_result.get('items', [])

    #     if not events:
    #         print('No upcoming events found.')
    #     else:
    #         event_data = {}  # イベントデータを格納する辞書

    #         for event in events:
    #             start = event['start'].get('dateTime', event['start'].get('date'))
    #             summary = event['summary']

    #             # イベントの年、月、日を取得
    #             start_date = start.split('T')[0]
    #             year, month, day = start_date.split('-')

    #             # イベントデータの階層構造を作成
    #             if year not in event_data:
    #                 event_data[year] = {}
    #             if month not in event_data[year]:
    #                 event_data[year][month] = {}
    #             if day not in event_data[year][month]:
    #                 event_data[year][month][day] = []

    #             # イベントをデータ構造に追加
    #             event_data[year][month][day].append(
    #                 {'start': start, 'summary': summary})

    #         # event_dataを使って必要な操作を実行
    #         # 以下は例として全てのイベントを出力する場合
    #         for year, year_data in event_data.items():
    #             for month, month_data in year_data.items():
    #                 for day, day_data in month_data.items():
    #                     print(f'{year}-{month}-{day}:')
    #                     for event in day_data:
    #                         print(event['start'], event['summary'])
                            
    # except HttpError as error:
    #     print('An error occurred: %s' % error)
    
    
def create_event(calendar_id, event_summary, year, month, date, start_time, end_time):
    # Google Calendar API を初期化し、認証します
    credentials = Credentials.from_authorized_user_file('credentials.json')
    service = build('calendar', 'v3', credentials=credentials)

    # 予定のパラメータを指定
    event = {
        'summary': event_summary,
        'start': {
            'dateTime': f'{year}-{month}-{date}T{start_time}:00',
            'timeZone': 'UTC',  # タイムゾーンを適宜変更してください
        },
        'end': {
            'dateTime': f'{year}-{month}-{date}T{end_time}:00',
            'timeZone': 'UTC',  # タイムゾーンを適宜変更してください
        },
    }

    # 予定を作成
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")


def list_filtered_events(calendar_id, event_summary, year, month, date, year_flag, month_flag):
    if year_flag:
        list_events_by_year(calendar_id, event_summary, year)
        # print all events in the year

    elif month_flag:
        list_events_by_month(calendar_id, event_summary, year, month)
        # print all events in the month

    else:
        list_events_by_date(calendar_id, event_summary, year, month, date)
        # print all events in the day
        

def list_events_by_year(creds, calendar_id, year):
    service =  build('calendar', 'v3', credentials=creds)

    # イベントを取得
    events_result = service.events().list(calendarId=calendar_id).execute()
    events = events_result.get('items', [])

    # 指定した条件に合致するイベントを出力
    for event in events:
        if 'start' not in event:
            continue  # 'start' キーが存在しないイベントはスキップ
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_year, start_month, start_date = start[:10].split('-')
        if start_year == year:
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(f'{start} ~ {end} {event.get("summary", "")}')
                

def list_events_by_month(creds, calendar_id, year, month):
    service =  build('calendar', 'v3', credentials=creds)

    # イベントを取得
    events_result = service.events().list(calendarId=calendar_id).execute()
    events = events_result.get('items', [])

    # 指定した条件に合致するイベントを出力
    for event in events:
        if 'start' not in event:
            continue  # 'start' キーが存在しないイベントはスキップ
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_year, start_month, start_date = start[:10].split('-')
        if start_year == year and start_month == month:
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(f'{start} ~ {end} {event.get("summary", "")}') 


def list_events_by_date(creds, calendar_id, year, month, date):
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=f'{year}-{month}-{date}T00:00:00Z',
        timeMax=f'{year}-{month}-{date}T23:59:59Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    for event in events:
        start = event.get('start', {}).get(
            'dateTime', event.get('start', {}).get('date', ''))
        end = event.get('end', {}).get(
            'dateTime', event.get('end', {}).get('date', ''))
        summary = event.get('summary', '') 
        output = f'{start} ~ {end} {summary}'
        output = output.replace('T', ' ')
        output = output.replace(':00+09:00', '')
        print(output)



# def list_events_by_date(creds, calendar_id, year, month, date):
#     service = build('calendar', 'v3', credentials=creds)

#     # イベントを取得
#     events_result = service.events().list(calendarId=calendar_id).execute()
#     events = events_result.get('items', [])

#     # 指定した条件に合致するイベントを出力
#     for event in events:
#         if 'start' not in event:
#             continue  # 'start' キーが存在しないイベントはスキップ
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         start_year, start_month, start_date = start[:10].split('-')
#         if start_year == year:
#             print("Year matched", year)
#             if start_month == month:
#                 print("Month matched", month)
#                 if start_date == date:
#                     print("Date matched", date)

        
#         if start_year == year and start_month == month and start_date == date:
#             end = event['end'].get('dateTime', event['end'].get('date'))
#             print(f'{start} ~ {end} {event.get("summary", "")}') 
        
def main(creds):
    current_calendar_id = 'primary'
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime('%m')
    current_date = datetime.datetime.now().strftime('%d')

    year_flag = True
    month_flag = True
    date_flag = True
    
    while True:
        command = input(f'{current_calendar_id}/{current_year}/{current_month}/{current_date} % ')
        
        if command == "pwd":
            if year_flag:
                if month_flag:
                    if date_flag:
                        print(current_calendar_id, current_year, current_month, current_date)
                    else:
                        print(current_calendar_id, current_year, current_month)
                else:
                    print(current_calendar_id, current_year)
            else:
                print(current_calendar_id)
        
        if command == "ls":
            list_events_by_date(creds, current_calendar_id, current_year, current_month, current_date)
            
        if command == "clear":
            os.system('clear')        

        # 入力に応じた処理を実行
        if command == "exit":
            break  # ループを終了する条件
        elif command == "run_script":
            # 実行したいPythonコードを記述
            print("Running script...")
            # ここにコードを記述
            
        # 他のコマンドに対する処理も追加可能
                
            print("Exiting the program")

if __name__ == '__main__':
    # 初期化処理を実行
    creds = init()
    # ターミナルからの入力を取得
    main(creds)
    
        

  






