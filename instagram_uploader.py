"""
Instagram uploader module
"""
import os
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
import json


class InstagramUploader:
    def __init__(self, username, password, session_file='ig_session.json'):
        """
        Initialize Instagram uploader
        
        Args:
            username: Instagram username
            password: Instagram password
            session_file: Path to save/load session
        """
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        self.client.delay_range = [1, 3]
        self._login()
    
    def _login(self):
        """Login to Instagram with session persistence"""
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                print("Loading existing Instagram session...")
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(self.username, self.password)
                    
                    # Verify session is valid
                    self.client.get_timeline_feed()
                    print("✓ Successfully logged in using saved session")
                    return
                except Exception as e:
                    print(f"Saved session failed, logging in fresh: {e}")
            
            # Fresh login
            print("Logging in to Instagram...")
            self.client.login(self.username, self.password)
            
            # Save session
            self.client.dump_settings(self.session_file)
            print("✓ Successfully logged in and saved session")
            
        except Exception as e:
            print(f"✗ Error logging in to Instagram: {e}")
            raise
    
    def upload_video(self, video_path, caption=""):
        """
        Upload a video to Instagram
        
        Args:
            video_path: Path to video file
            caption: Caption for the post
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                print(f"✗ Video file not found: {video_path}")
                return False
            
            print(f"Uploading video to Instagram: {os.path.basename(video_path)}")
            
            # Upload video as reel (Instagram prefers reels for videos)
            media = self.client.clip_upload(
                video_path,
                caption=caption
            )
            
            if media:
                print(f"✓ Successfully uploaded video! Post ID: {media.pk}")
                return True
            else:
                print("✗ Upload failed - no media object returned")
                return False
                
        except ClientError as e:
            print(f"✗ Instagram API error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error uploading video: {e}")
            return False
    
    def upload_video_post(self, video_path, caption=""):
        """
        Upload a video as a regular post (alternative method)
        
        Args:
            video_path: Path to video file
            caption: Caption for the post
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                print(f"✗ Video file not found: {video_path}")
                return False
            
            print(f"Uploading video post to Instagram: {os.path.basename(video_path)}")
            
            media = self.client.video_upload(
                video_path,
                caption=caption
            )
            
            if media:
                print(f"✓ Successfully uploaded video post! Post ID: {media.pk}")
                return True
            else:
                print("✗ Upload failed")
                return False
                
        except Exception as e:
            print(f"✗ Error uploading video post: {e}")
            return False
    
    def logout(self):
        """Logout from Instagram"""
        try:
            self.client.logout()
            print("✓ Logged out from Instagram")
        except Exception as e:
            print(f"Note: Logout error (may be ignored): {e}")
