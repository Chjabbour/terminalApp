import os
import sys
import httplib2
import pickle
import google.auth
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def upload_txt_to_google_docs(txt_file_path):
    try:
        credentials = get_credentials()
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(txt_file_path),
            'mimeType': 'application/vnd.google-apps.document'
        }

        media = MediaFileUpload(txt_file_path, mimetype='text/plain')

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: "{file.get("id")}"')

    except HttpError as error:
        print(f'An error occurred: {error}')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python upload_txt_to_google_docs.py /path/to/your/file.txt')
        sys.exit(1)

    txt_file_path = sys.argv[1]
    if not os.path.exists(txt_file_path):
        print(f'File not found: {txt_file_path}')
        sys.exit(1)

    upload_txt_to_google_docs(txt_file_path)
