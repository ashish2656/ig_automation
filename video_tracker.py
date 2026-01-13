"""
Video tracking and history management
"""
import json
import os
from datetime import datetime


class VideoTracker:
    def __init__(self, history_file='video_history.json'):
        """
        Initialize video tracker
        
        Args:
            history_file: Path to JSON file storing upload history
        """
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        """Load upload history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return {"uploaded_videos": [], "last_upload_date": None, "daily_count": 0}
        return {"uploaded_videos": [], "last_upload_date": None, "daily_count": 0}
    
    def _save_history(self):
        """Save upload history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def get_uploaded_ids(self):
        """Get list of uploaded video IDs"""
        return [v['file_id'] for v in self.history.get('uploaded_videos', [])]
    
    def mark_uploaded(self, file_id, file_name):
        """
        Mark a video as uploaded
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the video file
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset daily count if it's a new day
        if self.history.get('last_upload_date') != today:
            self.history['daily_count'] = 0
            self.history['last_upload_date'] = today
        
        # Add to uploaded videos
        self.history['uploaded_videos'].append({
            'file_id': file_id,
            'file_name': file_name,
            'uploaded_at': datetime.now().isoformat()
        })
        
        # Increment daily count
        self.history['daily_count'] = self.history.get('daily_count', 0) + 1
        
        self._save_history()
        print(f"✓ Marked as uploaded: {file_name} (Daily count: {self.history['daily_count']})")
    
    def get_daily_count(self):
        """Get number of uploads today"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.history.get('last_upload_date') != today:
            return 0
        return self.history.get('daily_count', 0)
    
    def can_upload_more(self, max_daily=4):
        """
        Check if more videos can be uploaded today
        
        Args:
            max_daily: Maximum uploads per day
            
        Returns:
            True if more uploads allowed, False otherwise
        """
        return self.get_daily_count() < max_daily
    
    def get_remaining_today(self, max_daily=4):
        """Get number of remaining uploads for today"""
        return max(0, max_daily - self.get_daily_count())
    
    def reset_daily_count(self):
        """Reset daily upload count (for testing)"""
        self.history['daily_count'] = 0
        self.history['last_upload_date'] = None
        self._save_history()
