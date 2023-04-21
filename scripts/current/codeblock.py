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

def create_folder_if_not_exists(drive_service, folder_name):
    query = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{folder_name}'"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])

    if not items:
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = drive_service.files().create(body=file_metadata, fields="id").execute()
        print(f'Folder created: "{folder.get("id")}"')
        return folder.get("id")
    else:
        return items[0]["id"]

def check_file_exists(drive_service, folder_id, file_name):
    query = f"parents = '{folder_id}' and trashed = false and name = '{file_name}'"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])

    return True if items else False

def upload_txt_to_google_docs(txt_file_path, folder_id):
    try:
        credentials = get_credentials()
        drive_service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(txt_file_path),
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]  # Set the target directory ID here
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
    local_directory = '/home/chad/Desktop/code/terminalapp/files'  # Specify the local directory path here

    credentials = get_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    folder_name = "Terminal Logs"  # Specify the folder name here
    folder_id = create_folder_if_not_exists(drive_service, folder_name)

    # Iterate over all text files in the local directory
    for file_name in os.listdir(local_directory):
        if file_name.endswith(".txt"):
            txt_file_path = os.path.join(local_directory, file_name)

            # Check if the file with the same name exists in Google Drive
            if not check_file_exists(drive_service, folder_id, file_name):
                upload_txt_to_google_docs(txt_file_path, folder_id)
            else:
                print(f"Skipping {file_name} as it already exists in the Google Drive folder")

