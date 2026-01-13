"""
Test Instagram login and basic upload functionality
"""
import json
from instagram_uploader import InstagramUploader

def main():
    print("=" * 60)
    print("Instagram Login Test")
    print("=" * 60)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    ig_config = config.get('instagram', {})
    
    try:
        # Test login
        print("\nAttempting to login...")
        ig = InstagramUploader(
            username=ig_config.get('username'),
            password=ig_config.get('password')
        )
        
        # Get account info
        try:
            info = ig.client.account_info()
            print(f"\n✓ Login successful!")
            print(f"Username: {info.username}")
            print(f"Full name: {info.full_name}")
            print(f"Followers: {info.follower_count}")
            print(f"Following: {info.following_count}")
            print(f"Media count: {info.media_count}")
        except Exception as e:
            print(f"\nWarning: Could not fetch account info: {e}")
        
        # Logout
        ig.logout()
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify credentials in config.json")
        print("2. Login to Instagram via browser/app and complete any security checks")
        print("3. Disable 2FA or use app-specific password")
        print("4. Wait a few minutes if you've tried multiple times")

if __name__ == "__main__":
    main()
