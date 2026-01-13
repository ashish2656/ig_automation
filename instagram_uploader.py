"""
Instagram uploader module
"""
import os
import time
import base64
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
        
        # Configure client settings for better reliability
        self.client.delay_range = [2, 5]
        self.client.request_timeout = 10
        
        self._login()
    
    def _login(self):
        """Login to Instagram with session persistence"""
        try:
            # Check if running in CI environment
            is_ci = os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true'
            
            # Try to load session from environment variable (base64 encoded)
            session_b64 = os.environ.get('IG_SESSION_B64')
            
            if session_b64:
                print("Loading Instagram session from environment...")
                try:
                    session_json = base64.b64decode(session_b64).decode()
                    session_data = json.loads(session_json)
                    self.client.set_settings(session_data)
                    self.client.login(self.username, self.password)
                    print("✓ Successfully logged in using saved session")
                    return
                except Exception as e:
                    print(f"Session from env failed: {e}")
            
            # Try to load from session file
            if os.path.exists(self.session_file):
                print("Loading existing Instagram session from file...")
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(self.username, self.password)
                    print("✓ Successfully logged in using saved session")
                    return
                except Exception as e:
                    print(f"Session file failed: {e}")
                    if os.path.exists(self.session_file):
                        os.remove(self.session_file)
            
            # Fresh login (only works locally, not in CI due to IP blacklist)
            print("Logging in to Instagram (fresh login)...")
            self.client.login(self.username, self.password)
            
            # Verify login by getting account info
            try:
                account_info = self.client.account_info()
                print(f"✓ Successfully logged in as: {account_info.username}")
            except:
                print("✓ Successfully logged in")
            
            # Save session
            self.client.dump_settings(self.session_file)
            print("✓ Session saved")
            
        except Exception as e:
            print(f"✗ Error logging in to Instagram: {e}")
            print("\nPossible issues:")
            print("1. Check username and password are correct")
            print("2. Instagram may have flagged the account - try logging in via app/web first")
            print("3. You may need to verify your identity on Instagram")
            print("4. Consider using a different account for automation")
            print("\nFor GitHub Actions, run generate_session.py locally first!")
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
            
            # Try uploading as reel first
            try:
                media = self.client.clip_upload(
                    video_path,
                    caption=caption
                )
                
                if media:
                    print(f"✓ Successfully uploaded video as Reel! Post ID: {media.pk}")
                    return True
            except Exception as e:
                print(f"Reel upload failed, trying as video post: {e}")
                # Try regular video post
                media = self.client.video_upload(
                    video_path,
                    caption=caption
                )
                
                if media:
                    print(f"✓ Successfully uploaded as video post! Post ID: {media.pk}")
                    return True
            
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
