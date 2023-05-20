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

calendar_service = build('calendar', 'v3', credentials=creds)

# イベント作成のパラメータを設定
event = {
    'summary': 'イベントのタイトル',
    'start': {
        'dateTime': '2023-05-19T10:00:00',  # 開始日時（ISO 8601形式）
        'timeZone': 'Asia/Tokyo',  # タイムゾーン
    },
    'end': {
        'dateTime': '2023-05-19T12:00:00',  # 終了日時（ISO 8601形式）
        'timeZone': 'Asia/Tokyo',  # タイムゾーン
    },
    'description': 'イベントの詳細情報',
    'location': 'イベントの場所',
}

# イベントを作成
created_event = calendar_service.events().insert(
    calendarId='primary', body=event).execute()
print('イベントが作成されました。イベントID:', created_event['id'])
