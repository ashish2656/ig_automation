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
from mongo_tracker import MongoVideoTracker
from ai_caption import AICaptionGenerator


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
    print("Instagram Video Automation with AI")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load configuration
    config = load_config()
    
    ig_config = config.get('instagram', {})
    drive_config = config.get('google_drive', {})
    mongo_config = config.get('mongodb', {})
    ai_config = config.get('ai', {})
    posting_config = config.get('posting', {})
    
    max_videos_per_day = posting_config.get('videos_per_day', 4)
    
    # Initialize components
    print("Initializing components...\n")
    
    tracker = None
    ig = None
    
    try:
        # Initialize MongoDB tracker
        tracker = MongoVideoTracker(
            connection_string=mongo_config.get('connection_string'),
            database_name=mongo_config.get('database', 'ig_automation'),
            collection_name=mongo_config.get('collection', 'uploaded_videos')
        )
        
        # Check if we can upload more videos today
        if not tracker.can_upload_more(max_videos_per_day):
            print(f"✓ Daily limit reached ({max_videos_per_day} videos)")
            print("No more uploads for today!")
            stats = tracker.get_upload_stats()
            print(f"Total uploads: {stats['total_uploads']}")
            tracker.close()
            return
        
        remaining = tracker.get_remaining_today(max_videos_per_day)
        print(f"Videos to upload today: {remaining}\n")
        
        # Initialize AI caption generator
        ai_generator = AICaptionGenerator(
            gemini_key=ai_config.get('gemini_api_key'),
            openai_key=ai_config.get('openai_api_key'),
            default_caption=ai_config.get('default_caption', 'Check out this video!')
        )
        
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
        
        # Only get 1 video at a time for every-3-hours schedule
        videos_to_upload = drive.get_next_videos(
            count=1,
            exclude_ids=uploaded_ids
        )
        
        if not videos_to_upload:
            print("✗ No new videos found in Google Drive folder")
            tracker.close()
            return
        
        print(f"\nFound {len(videos_to_upload)} video(s) to upload\n")
        
        # Process each video
        success_count = 0
        for i, video in enumerate(videos_to_upload, 1):
            print(f"\n{'=' * 60}")
            print(f"Processing video {i}/{len(videos_to_upload)}: {video['name']}")
            print(f"{'=' * 60}\n")
            
            # Generate AI caption and title
            print("Generating AI caption...")
            ai_content = ai_generator.generate_caption_from_filename(video['name'])
            print(f"Title: {ai_content['title']}")
            print(f"Caption: {ai_content['caption'][:100]}...\n")
            
            # Download to temporary file (needed for Instagram API)
            temp_path = drive.download_to_temp(
                file_id=video['id'],
                file_name=video['name']
            )
            
            if not temp_path:
                print(f"✗ Failed to download: {video['name']}")
                continue
            
            # Upload to Instagram
            time.sleep(5)  # Brief delay before upload
            
            success = ig.upload_video(temp_path, ai_content['caption'])
            
            # Clean up temp file
            try:
                os.remove(temp_path)
                print(f"✓ Cleaned up temp file")
            except Exception as e:
                print(f"Note: Could not delete temp file: {e}")
            
            if success:
                # Mark as uploaded in MongoDB
                tracker.mark_uploaded(
                    file_id=video['id'],
                    file_name=video['name'],
                    caption=ai_content['caption'],
                    title=ai_content['title']
                )
                success_count += 1
                
                # Wait between uploads to avoid rate limiting
                if i < len(videos_to_upload):
                    wait_time = 300  # 5 minutes
                    print(f"\nWaiting {wait_time} seconds before next upload...")
                    time.sleep(wait_time)
            else:
                print(f"✗ Failed to upload: {video['name']}")
        
        # Logout
        if ig:
            ig.logout()
        
        # Summary
        stats = tracker.get_upload_stats()
        print("\n" + "=" * 60)
        print("UPLOAD SUMMARY")
        print("=" * 60)
        print(f"Successfully uploaded: {success_count}/{len(videos_to_upload)} videos")
        print(f"Daily total: {stats['today_uploads']}/{max_videos_per_day}")
        print(f"All-time total: {stats['total_uploads']}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if tracker:
            tracker.close()


if __name__ == "__main__":
    main()
