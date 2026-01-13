"""
Main automation script
"""
import os
import json
import time
import sys
from datetime import datetime
from google_drive import GoogleDriveDownloader
from instagram_uploader import InstagramUploader
from video_tracker import VideoTracker


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Config file not found: {config_file}")
        print("Please copy config.json.example to config.json and fill in your details")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        sys.exit(1)


def main():
    """Main automation workflow"""
    print("=" * 60)
    print("Instagram Video Automation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load configuration
    config = load_config()
    
    ig_config = config.get('instagram', {})
    drive_config = config.get('google_drive', {})
    posting_config = config.get('posting', {})
    
    max_videos_per_day = posting_config.get('videos_per_day', 4)
    caption = posting_config.get('caption', 'Check out this video!')
    
    # Initialize components
    print("Initializing components...\n")
    
    try:
        # Initialize video tracker
        tracker = VideoTracker()
        
        # Check if we can upload more videos today
        if not tracker.can_upload_more(max_videos_per_day):
            print(f"✓ Daily limit reached ({max_videos_per_day} videos)")
            print("No more uploads for today!")
            return
        
        remaining = tracker.get_remaining_today(max_videos_per_day)
        print(f"Videos to upload today: {remaining}\n")
        
        # Initialize Google Drive downloader
        drive = GoogleDriveDownloader(
            credentials_file=drive_config.get('credentials_file', 'credentials.json'),
            folder_id=drive_config.get('folder_id')
        )
        
        # Initialize Instagram uploader
        ig = InstagramUploader(
            username=ig_config.get('username'),
            password=ig_config.get('password')
        )
        
        # Get videos to upload
        uploaded_ids = tracker.get_uploaded_ids()
        videos_to_upload = drive.get_next_videos(
            count=remaining,
            exclude_ids=uploaded_ids
        )
        
        if not videos_to_upload:
            print("✗ No new videos found in Google Drive folder")
            return
        
        print(f"\nFound {len(videos_to_upload)} video(s) to upload\n")
        
        # Process each video
        success_count = 0
        for i, video in enumerate(videos_to_upload, 1):
            print(f"\n{'=' * 60}")
            print(f"Processing video {i}/{len(videos_to_upload)}: {video['name']}")
            print(f"{'=' * 60}\n")
            
            # Download video
            video_path = drive.download_video(
                file_id=video['id'],
                file_name=video['name']
            )
            
            if not video_path:
                print(f"✗ Failed to download: {video['name']}")
                continue
            
            # Upload to Instagram
            time.sleep(5)  # Brief delay before upload
            
            success = ig.upload_video(video_path, caption)
            
            if success:
                # Mark as uploaded
                tracker.mark_uploaded(video['id'], video['name'])
                success_count += 1
                
                # Delete local file to save space
                try:
                    os.remove(video_path)
                    print(f"✓ Cleaned up local file: {video['name']}")
                except Exception as e:
                    print(f"Note: Could not delete local file: {e}")
                
                # Wait between uploads to avoid rate limiting
                if i < len(videos_to_upload):
                    wait_time = 300  # 5 minutes
                    print(f"\nWaiting {wait_time} seconds before next upload...")
                    time.sleep(wait_time)
            else:
                print(f"✗ Failed to upload: {video['name']}")
        
        # Logout
        ig.logout()
        
        # Summary
        print("\n" + "=" * 60)
        print("UPLOAD SUMMARY")
        print("=" * 60)
        print(f"Successfully uploaded: {success_count}/{len(videos_to_upload)} videos")
        print(f"Daily total: {tracker.get_daily_count()}/{max_videos_per_day}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
