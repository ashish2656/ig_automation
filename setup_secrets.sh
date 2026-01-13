#!/bin/bash

# Script to set GitHub Secrets for Instagram Automation
# Run this script: chmod +x setup_secrets.sh && ./setup_secrets.sh

REPO="ashish2656/ig_automation"

echo "=========================================="
echo "GitHub Secrets Setup for IG Automation"
echo "=========================================="
echo ""
echo "This will set up all required secrets for GitHub Actions"
echo ""

# Instagram credentials
echo "Setting Instagram credentials..."
gh secret set IG_USERNAME -b "dangerscavenger" -R "$REPO"
gh secret set IG_PASSWORD -b "@Ashish5151" -R "$REPO"

# Google Drive
echo "Setting Google Drive folder ID..."
gh secret set GOOGLE_DRIVE_FOLDER_ID -b "1oRMIuzjT3lRA5xTN5SB-TTlqqX-srWBp" -R "$REPO"

# Google credentials (from file)
echo "Setting Google OAuth credentials..."
if [ -f "credentials.json" ]; then
    gh secret set GOOGLE_CREDENTIALS < credentials.json -R "$REPO"
    echo "✓ Google credentials set from credentials.json"
else
    echo "✗ credentials.json not found!"
    echo "  Please create credentials.json with your Google OAuth credentials"
fi

# MongoDB
echo "Setting MongoDB connection string..."
gh secret set MONGODB_CONNECTION_STRING -b "mongodb+srv://ashish:ashish5151@cluster0.kra8xz9.mongodb.net/?appName=Cluster0" -R "$REPO"

# AI API Keys
echo "Setting AI API keys..."
gh secret set GEMINI_API_KEY -b "YOUR_GEMINI_KEY_HERE" -R "$REPO"
gh secret set OPENAI_API_KEY -b "YOUR_OPENAI_KEY_HERE" -R "$REPO"

echo ""
echo "=========================================="
echo "✓ All secrets have been set!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/$REPO/actions"
echo "2. Enable workflows if needed"
echo "3. Manually trigger the workflow to test"
echo "4. The workflow will run automatically every 3 hours"
echo ""
echo "To manually trigger:"
echo "  gh workflow run daily-upload.yml -R $REPO"
echo ""
