"""
Google Drive video downloader module
"""
import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json
import pickle


class GoogleDriveDownloader:
    def __init__(self, credentials_file, folder_id):
        """
        Initialize Google Drive downloader
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON
            folder_id: Google Drive folder ID containing videos
        """
        self.folder_id = folder_id
        self.credentials_file = credentials_file
        self.token_file = 'token.pickle'
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API using OAuth"""
        try:
            creds = None
            # Token file stores the user's access and refresh tokens
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no valid credentials, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        scopes=['https://www.googleapis.com/auth/drive.readonly']
                    )
                    # Use port 8080 to match your OAuth configuration
                    creds = flow.run_local_server(port=8080)
                
                # Save the credentials for the next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            print("✓ Successfully authenticated with Google Drive")
        except Exception as e:
            print(f"✗ Error authenticating with Google Drive: {e}")
            raise
    
    def list_videos(self):
        """
        List all video files in the specified folder
        
        Returns:
            List of video file objects with id, name, and mimeType
        """
        try:
            query = f"'{self.folder_id}' in parents and (mimeType contains 'video/' or name contains '.mp4' or name contains '.mov' or name contains '.avi')"
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, size)",
                orderBy='createdTime'
            ).execute()
            
            videos = results.get('files', [])
            print(f"✓ Found {len(videos)} videos in Google Drive folder")
            return videos
        except Exception as e:
            print(f"✗ Error listing videos: {e}")
            return []
    
    def download_video(self, file_id, file_name, download_path='downloads'):
        """
        Download a specific video file
        
        Args:
            file_id: Google Drive file ID
            file_name: Name to save the file as
            download_path: Directory to save the file
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Create download directory if it doesn't exist
            os.makedirs(download_path, exist_ok=True)
            
            # Full path for the downloaded file
            file_path = os.path.join(download_path, file_name)
            
            # Check if file already exists
            if os.path.exists(file_path):
                print(f"✓ Video already exists: {file_name}")
                return file_path
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            print(f"Downloading {file_name}...")
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"  Progress: {int(status.progress() * 100)}%")
            
            print(f"✓ Successfully downloaded: {file_name}")
            return file_path
            
        except Exception as e:
            print(f"✗ Error downloading video {file_name}: {e}")
            return None
    
    def get_video_stream(self, file_id):
        """
        Get video file as bytes stream without saving to disk
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            BytesIO object containing video data or None if failed
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            print(f"Streaming video from Google Drive...")
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"  Progress: {int(status.progress() * 100)}%")
            
            fh.seek(0)  # Reset to beginning
            print(f"✓ Successfully streamed video")
            return fh
            
        except Exception as e:
            print(f"✗ Error streaming video: {e}")
            return None
    
    def download_to_temp(self, file_id, file_name):
        """
        Download video to temporary file
        
        Args:
            file_id: Google Drive file ID
            file_name: Original filename
            
        Returns:
            Path to temporary file or None if failed
        """
        try:
            import tempfile
            
            # Create temp file with same extension
            ext = os.path.splitext(file_name)[1]
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_path = temp_file.name
            temp_file.close()
            
            # Download to temp file
            request = self.service.files().get_media(fileId=file_id)
            with open(temp_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                print(f"Downloading {file_name} to temp...")
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"  Progress: {int(status.progress() * 100)}%")
            
            print(f"✓ Downloaded to temp file")
            return temp_path
            
        except Exception as e:
            print(f"✗ Error downloading to temp: {e}")
            return None
    
    def get_next_videos(self, count=1, exclude_ids=None):
        """
        Get the next videos to upload
        
        Args:
            count: Number of videos to get
            exclude_ids: List of file IDs to exclude (already uploaded)
            
        Returns:
            List of video file objects
        """
        if exclude_ids is None:
            exclude_ids = []
        
        videos = self.list_videos()
        
        # Filter out already uploaded videos
        available_videos = [v for v in videos if v['id'] not in exclude_ids]
        
        # Return the requested number of videos
        return available_videos[:count]
