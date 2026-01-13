"""
Generate Instagram session for GitHub Actions
Run this locally to create a session that can be used in CI
"""
import json
import base64
from instagrapi import Client


def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    ig_config = config.get('instagram', {})
    
    print("=" * 60)
    print("Instagram Session Generator")
    print("=" * 60)
    print(f"\nLogging in as: {ig_config.get('username')}")
    
    client = Client()
    client.delay_range = [2, 5]
    
    try:
        # Login
        client.login(ig_config.get('username'), ig_config.get('password'))
        print("✓ Login successful!")
        
        # Save session to file
        client.dump_settings('ig_session.json')
        print("✓ Session saved to ig_session.json")
        
        # Create base64 encoded session for GitHub secret
        with open('ig_session.json', 'r') as f:
            session_data = f.read()
        
        session_b64 = base64.b64encode(session_data.encode()).decode()
        
        # Save base64 session to file
        with open('ig_session_b64.txt', 'w') as f:
            f.write(session_b64)
        
        print("✓ Base64 session saved to ig_session_b64.txt")
        print("\n" + "=" * 60)
        print("NEXT STEP:")
        print("=" * 60)
        print("\nRun this command to add the session to GitHub:")
        print(f"\ngh secret set IG_SESSION < ig_session_b64.txt -R ashish2656/ig_automation")
        print("\nThen delete the session files:")
        print("rm ig_session.json ig_session_b64.txt")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Login to Instagram via browser first")
        print("2. Complete any security challenges")
        print("3. Wait a few minutes and try again")


if __name__ == "__main__":
    main()
