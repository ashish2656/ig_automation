"""
Email notification module for session expiry alerts
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_session_expired_email(recipient_email, error_details=""):
    """
    Send email notification when Instagram session expires
    
    Args:
        recipient_email: Email address to send notification to
        error_details: Details about the error
    """
    # Get email credentials from environment
    sender_email = os.environ.get('SMTP_EMAIL')
    sender_password = os.environ.get('SMTP_PASSWORD')
    
    if not sender_email or not sender_password:
        print("⚠️ Email credentials not configured - skipping notification")
        print("   Set SMTP_EMAIL and SMTP_PASSWORD secrets to enable email alerts")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🚨 Instagram Session Expired - Action Required'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Create email body
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        text_content = f"""
Instagram Session Expired - Action Required

Time: {timestamp}

Your Instagram automation session has expired and needs to be regenerated.

Error Details:
{error_details}

ACTION REQUIRED:
1. Open terminal on your Mac
2. Navigate to your IG_AUTOMATION folder
3. Run: python generate_session.py
4. Run: gh secret set IG_SESSION < ig_session_b64.txt -R ashish2656/ig_automation
5. Clean up: rm ig_session.json ig_session_b64.txt

The automation will resume automatically after you update the session.

---
This is an automated message from your IG Automation system.
"""

        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">🚨 Instagram Session Expired</h1>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
        <p style="color: #666; margin: 0;">Time: <strong>{timestamp}</strong></p>
    </div>
    
    <div style="padding: 20px; background: white; border: 1px solid #dee2e6; border-top: none;">
        <p>Your Instagram automation session has expired and needs to be regenerated.</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <strong>Error Details:</strong><br>
            <code style="font-size: 12px;">{error_details}</code>
        </div>
        
        <h3 style="color: #dc3545;">⚡ Action Required:</h3>
        <ol style="line-height: 1.8;">
            <li>Open terminal on your Mac</li>
            <li>Navigate to your IG_AUTOMATION folder</li>
            <li>Run: <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">python generate_session.py</code></li>
            <li>Run: <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">gh secret set IG_SESSION < ig_session_b64.txt</code></li>
            <li>Clean up: <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">rm ig_session.json ig_session_b64.txt</code></li>
        </ol>
        
        <p style="color: #28a745;">✓ The automation will resume automatically after you update the session.</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 10px 20px; border-radius: 0 0 10px 10px; border: 1px solid #dee2e6; border-top: none;">
        <p style="color: #999; font-size: 12px; margin: 0;">This is an automated message from your IG Automation system.</p>
    </div>
</body>
</html>
"""
        
        # Attach both plain text and HTML versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email using Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        print(f"✓ Session expiry notification sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to send email notification: {e}")
        return False


class SessionExpiredError(Exception):
    """Custom exception for session expiry"""
    pass
