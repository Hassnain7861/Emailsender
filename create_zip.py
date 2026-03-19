import zipfile
import os

# Create ZIP file
with zipfile.ZipFile('email_campaign_dashboard.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add files
    zipf.write('app.py')
    zipf.write('templates/index.html')
    zipf.write('requirements.txt')
    zipf.write('test_tracking.py')
    
    # Create README
    readme = """EMAIL CAMPAIGN DASHBOARD
========================

INSTALLATION:
1. Extract this ZIP file
2. Install Python (if not already installed)
3. Open Command Prompt/PowerShell in this folder
4. Run: pip install -r requirements.txt
5. Run: python app.py

USAGE:
1. Open browser: http://localhost:5000
2. Fill in email provider (Gmail, Zoho, etc.)
3. Enter email and app password
4. Upload leads (CSV or Excel)
5. Customize templates and subject lines
6. Click Send Campaign

FEATURES:
- Multi-provider email support (Gmail, Zoho, Outlook, Yahoo, SendGL)
- Multiple templates with auto-rotation every 3 emails
- Subject line splitting (A/B testing)
- Batch sending (5 emails per batch)
- Random 25-65 second delays between emails (anti-spam)
- Follow-up sequences (1, 2, 3+ days later)
- Full campaign control (Start/Stop/Resume)

IMPORTANT:
- Keep the command window open for follow-ups to work
- Follow-ups continue even if you close the browser tab
- If you close the command window, follow-ups stop

GMAIL APP PASSWORD:
1. Go to https://myaccount.google.com/apppasswords
2. Select Mail and Windows Computer
3. Copy the 16-character password
4. Paste it in the dashboard

ZOHO APP PASSWORD:
1. Go to https://mail.zoho.com -> Settings -> Security
2. Generate app password
3. Paste it in the dashboard

TROUBLESHOOTING:
- Port 5000 already in use? Edit app.py, change port to 5001, 5002, etc.
- Authentication failed? Check your email and app password
- Emails not sending? Verify internet connection and SMTP access
"""
    
    zipf.writestr('README.txt', readme)
    
print('ZIP file created: email_campaign_dashboard.zip')
print('Size:', os.path.getsize('email_campaign_dashboard.zip'), 'bytes')
