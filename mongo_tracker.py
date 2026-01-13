"""
MongoDB video tracker - replaces JSON file tracking
"""
from pymongo import MongoClient
from datetime import datetime
import sys


class MongoVideoTracker:
    def __init__(self, connection_string, database_name='ig_automation', collection_name='uploaded_videos'):
        """
        Initialize MongoDB video tracker
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name
            collection_name: Collection name for uploaded videos
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for better performance
            self.collection.create_index("file_id", unique=True)
            self.collection.create_index("uploaded_at")
            
            print("✓ Successfully connected to MongoDB")
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {e}")
            raise
    
    def get_uploaded_ids(self):
        """Get list of all uploaded video IDs"""
        try:
            videos = self.collection.find({}, {"file_id": 1, "_id": 0})
            return [v['file_id'] for v in videos]
        except Exception as e:
            print(f"Error fetching uploaded IDs: {e}")
            return []
    
    def mark_uploaded(self, file_id, file_name, caption="", title=""):
        """
        Mark a video as uploaded in MongoDB
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the video file
            caption: Generated caption used
            title: Generated title
        """
        try:
            document = {
                'file_id': file_id,
                'file_name': file_name,
                'caption': caption,
                'title': title,
                'uploaded_at': datetime.utcnow(),
                'upload_date': datetime.utcnow().strftime('%Y-%m-%d')
            }
            
            self.collection.insert_one(document)
            print(f"✓ Marked as uploaded in MongoDB: {file_name}")
            
        except Exception as e:
            print(f"Error marking as uploaded: {e}")
    
    def get_daily_count(self):
        """Get number of uploads today"""
        try:
            today = datetime.utcnow().strftime('%Y-%m-%d')
            count = self.collection.count_documents({'upload_date': today})
            return count
        except Exception as e:
            print(f"Error getting daily count: {e}")
            return 0
    
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
    
    def get_upload_stats(self):
        """Get upload statistics"""
        try:
            total = self.collection.count_documents({})
            today = self.get_daily_count()
            
            return {
                'total_uploads': total,
                'today_uploads': today
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'total_uploads': 0, 'today_uploads': 0}
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            print("✓ MongoDB connection closed")
        except:
            pass
