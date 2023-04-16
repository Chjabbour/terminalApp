import os
import sys
import pickle
import google.auth
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']

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

def change_font_to_times_new_roman(doc_id, credentials):
    docs_service = build('docs', 'v1', credentials=credentials)
    document = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = document.get('body').get('content')
    doc_len = doc_content[-1].get('endIndex') if doc_content else 0

    requests = [
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,  # Change startIndex to 1
                    'endIndex': doc_len
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': 'Times New Roman'
                    }
                },
                'fields': 'weightedFontFamily'
            }
        }
    ]
    body = {
        'requests': requests
    }
    response = docs_service.documents().batchUpdate(documentId=doc_id, body=body).execute()
    return response

def upload_txt_to_google_docs(txt_file_path):
    try:
        credentials = get_credentials()
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(txt_file_path),
            'mimeType': 'application/vnd.google-apps.document'
        }

        media = MediaFileUpload(txt_file_path, mimetype='text/plain')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        doc_id = file.get("id")
        print(f'File ID: "{doc_id}"')

        change_font_to_times_new_roman(doc_id, credentials)
        print("Changed font to Times New Roman.")

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
