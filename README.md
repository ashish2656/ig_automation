# Instagram Video Automation

Automatically upload videos from Google Drive to Instagram using GitHub Actions. Uploads 4 videos daily at scheduled times.

## Features

- 📹 Automatically downloads videos from Google Drive
- 📱 Uploads videos to Instagram as Reels
- ⏰ Scheduled uploads (4 times daily)
- 📊 Tracks uploaded videos to avoid duplicates
- 🔄 Runs automatically via GitHub Actions
- 💾 Persistent upload history

## Setup Instructions

### 1. Google Drive Setup

1. Create a Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Drive API

2. Create Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Create a new service account
   - Download the JSON credentials file
   - Rename it to `credentials.json`

3. Share your Google Drive folder:
   - Create a folder with your videos
   - Share it with the service account email (found in credentials.json)
   - Copy the folder ID from the URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

### 2. Instagram Setup

1. Use a dedicated Instagram account (recommended)
2. Make sure 2FA is disabled or use an app-specific password
3. Keep your username and password ready

### 3. Local Testing

1. Clone the repository:
```bash
git clone https://github.com/ashish2656/ig_automation.git
cd ig_automation
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `config.json`:
```bash
cp config.json.example config.json
```

5. Edit `config.json` with your credentials:
```json
{
  "instagram": {
    "username": "your_instagram_username",
    "password": "your_instagram_password"
  },
  "google_drive": {
    "folder_id": "your_google_drive_folder_id",
    "credentials_file": "credentials.json"
  },
  "posting": {
    "videos_per_day": 4,
    "caption": "Your default caption here! #hashtags"
  }
}
```

6. Add your Google credentials:
   - Place your `credentials.json` file in the project root

7. Test the automation:
```bash
python main.py
```

### 4. GitHub Actions Setup

1. Add the following secrets to your GitHub repository:
   - Go to Settings > Secrets and variables > Actions > New repository secret

   Required secrets:
   - `IG_USERNAME`: Your Instagram username
   - `IG_PASSWORD`: Your Instagram password
   - `GOOGLE_DRIVE_FOLDER_ID`: Your Google Drive folder ID
   - `GOOGLE_CREDENTIALS`: Contents of your credentials.json file (paste entire JSON)
   - `POST_CAPTION`: (Optional) Default caption for posts

2. Enable GitHub Actions:
   - Go to Actions tab
   - Enable workflows if disabled

3. The workflow will run automatically at:
   - 9:00 AM UTC
   - 1:00 PM UTC
   - 5:00 PM UTC
   - 9:00 PM UTC

4. Adjust schedule in `.github/workflows/daily-upload.yml` if needed

### 5. Customize Upload Schedule

Edit `.github/workflows/daily-upload.yml` to change upload times:

```yaml
schedule:
  - cron: '0 9 * * *'   # 9:00 AM UTC
  - cron: '0 13 * * *'  # 1:00 PM UTC
  - cron: '0 17 * * *'  # 5:00 PM UTC
  - cron: '0 21 * * *'  # 9:00 PM UTC
```

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

## Project Structure

```
ig_automation/
├── .github/
│   └── workflows/
│       └── daily-upload.yml    # GitHub Actions workflow
├── google_drive.py             # Google Drive integration
├── instagram_uploader.py       # Instagram upload logic
├── video_tracker.py            # Track uploaded videos
├── main.py                     # Main automation script
├── requirements.txt            # Python dependencies
├── config.json.example         # Example configuration
└── README.md                   # This file
```

## How It Works

1. **GitHub Actions triggers** the workflow at scheduled times
2. **Google Drive module** lists available videos
3. **Video Tracker** checks which videos haven't been uploaded
4. **Downloads** the next video(s) from Google Drive
5. **Uploads** to Instagram as a Reel
6. **Tracks** the upload in video_history.json
7. **Cleans up** temporary files
8. **Commits** updated history back to the repo

## Troubleshooting

### Instagram Login Issues
- Make sure 2FA is disabled
- Use a dedicated account for automation
- Check if Instagram flagged your account (verify via app/web)

### Google Drive Issues
- Verify service account has access to the folder
- Check folder ID is correct
- Ensure Google Drive API is enabled

### Rate Limiting
- Instagram may block too many uploads
- The script includes delays between uploads
- Adjust `VIDEOS_PER_DAY` if needed

### GitHub Actions Fails
- Check secrets are set correctly
- Review action logs for specific errors
- Ensure video_history.json is committed

## Daily Limit

By default, the system uploads 4 videos per day. To change this:

1. Edit `config.json`:
```json
"posting": {
  "videos_per_day": 4
}
```

2. Adjust GitHub Actions schedule to match

## Video Requirements

- **Format**: MP4, MOV, or AVI
- **Duration**: 3-90 seconds (Instagram Reels)
- **Resolution**: 1080x1920 (9:16 ratio recommended)
- **Size**: Under 650MB

## License

MIT License - Feel free to use and modify!

## Disclaimer

This tool is for educational purposes. Use responsibly and follow Instagram's Terms of Service. Excessive automation may result in account restrictions.

## Support

For issues or questions, please open an issue on GitHub.

---

Made with ❤️ for content creators
