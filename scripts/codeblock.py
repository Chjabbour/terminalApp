import os
import sys
import pickle
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def get_credentials():
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/drive'])
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def upload_txt_to_google_docs(txt_file_path):
    try:
        credentials = get_credentials()
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(txt_file_path),
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(txt_file_path,
                                mimetype='text/plain',
                                resumable=True)

        file = drive_service.files().create(body=file_metadata, media_body=media,
                                            fields='id').execute()
        print(f'File ID: "{file.get("id")}"')

        doc_id = file.get('id')
        format_document_as_code_block(doc_id, credentials)

    except HttpError as error:
        print(f'An error occurred: {error}')
        file = None

    return file


def format_document_as_code_block(doc_id, credentials):
    docs_service = build('docs', 'v1', credentials=credentials)
    document = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = document.get('body').get('content')
    doc_len = doc_content[-1].get('endIndex') if doc_content else 0

    newline_count = 1  # Adjust this value to change the number of newline characters inserted between each line

    requests = [
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': doc_len
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': 'Courier New'
                    },
                    'foregroundColor': {
                        'color': {
                            'rgbColor': {
                                'red': 0.87,
                                'green': 0.87,
                                'blue': 0.87
                            }
                        }
                    },
                    'baselineOffset': 'NONE',
                    'bold': False,
                    'italic': False,
                    'strikethrough': False,
                    'underline': False
                },
                'fields': 'weightedFontFamily,foregroundColor,baselineOffset,bold,italic,strikethrough,underline'
            }
        }
    ]

    for index in range(1, doc_len, 1):
        requests.append({
            'insertText': {
                'location': {
                    'index': index
                },
                'text': '\n'
            }
        })

    body = {
        'requests': requests
    }
    response = docs_service.documents().batchUpdate(documentId=doc_id, body=body).execute()
    return response

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python upload_txt_to_google_docs.py /path/to/your/file.txt')
        sys.exit(1)

    txt_file_path = sys.argv[1]
    if not os.path.exists(txt_file_path):
        print(f'File not found: {txt_file_path}')
        sys.exit(1)

    upload_txt_to_google_docs(txt_file_path)

