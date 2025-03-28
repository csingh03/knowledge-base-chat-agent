import os
import io
import tempfile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import List, Dict, Any, Optional

# Scopes required for Google Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def create_oauth_flow() -> Flow:
    """Create OAuth flow for Google authentication."""
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
        }
    }
    
    return Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )

def get_drive_service(credentials: Dict[str, Any]) -> Any:
    """Create a Google Drive service with the given credentials."""
    creds = Credentials.from_authorized_user_info(credentials, SCOPES)
    return build('drive', 'v3', credentials=creds)

def list_files(drive_service, query: str = None, max_results: int = 100) -> List[Dict[str, Any]]:
    """List files from Google Drive, optionally filtered by query."""
    results = []
    page_token = None
    
    query = query or "mimeType='application/pdf' or mimeType='text/csv' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    
    while True:
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token,
            pageSize=min(max_results, 100)
        ).execute()
        
        results.extend(response.get('files', []))
        
        page_token = response.get('nextPageToken')
        if not page_token or len(results) >= max_results:
            break
    
    return results[:max_results]

def download_file(drive_service, file_id: str) -> str:
    """Download a file from Google Drive and return its local path."""
    # Get file metadata to determine file name
    file_metadata = drive_service.files().get(fileId=file_id).execute()
    file_name = file_metadata.get('name', 'downloaded_file')
    
    # Create a temporary directory to store the file
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, file_name)
    
    # Download the file
    request = drive_service.files().get_media(fileId=file_id)
    with open(local_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    
    return local_path 