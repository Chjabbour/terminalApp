import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
import dotenv

dotenv.load_dotenv()

# Set up credentials for the Google Drive API
credentials = Credentials.from_service_account_file('/home/chad/Desktop/terminalapp/credentials/keyfile.json')
service = build('drive', 'v3', credentials=credentials)

# Define a function to upload a file to Google Docs
def upload_to_google_docs(file_path):
    file_name = os.path.basename(file_path)
    file_mime_type = 'application/vnd.google-apps.document'

    with io.open(file_path, 'r', encoding='utf8') as f:
        file_contents = f.read()

    file_metadata = {'name': file_name, 'mimeType': file_mime_type}
    media = io.BytesIO(file_contents.encode('utf-8'))
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    logging.info(f'File "{file_name}" uploaded to Google Docs with ID: {file["id"]}')

# Define a subclass of FileSystemEventHandler to handle file creation events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            logging.info(f'File "{file_path}" created')
            upload_to_google_docs(file_path)

# Set up a watchdog Observer to monitor the folder for file creation events
folder_to_monitor = '/home/chad/Desktop/terminalapp/content'

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, folder_to_monitor)
observer.start()

logging.info(f'Monitoring folder "{folder_to_monitor}" for new files')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
