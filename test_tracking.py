#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
import uuid

# Your Gmail credentials
sender_email = "hassnainbaloch233@gmail.com"
app_password = "gylcjwluqvkkxeoa"

# Test recipient
recipient_email = "hassnain@digivine.us"

# Generate tracking ID
tracking_id = str(uuid.uuid4())
print(f"[TEST] Tracking ID: {tracking_id[:8]}...")

# Create HTML email with tracking pixel
tracking_pixel = f'<img src="http://localhost:5000/api/track/{tracking_id}" width="1" height="1" style="display:none;" />'

html_body = f"""<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<p>Hey Digivine Team,</p>

<p>This is a <strong>TEST EMAIL</strong> with open tracking enabled.</p>

<p>The tracking pixel is embedded below. When you open this email in HTML mode, the system will record it!</p>

<p style="margin-top: 30px; color: #999; font-size: 12px;">
<em>Test Campaign ID: {tracking_id[:8]}...</em>
</p>

{tracking_pixel}
</body>
</html>"""

try:
    # Create message as HTML ONLY
    msg = MIMEText(html_body, 'html')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'TEST: Email Open Tracking System'
    msg['X-Mailer'] = 'Email Tracking Test'
    
    # Connect and send via Gmail SMTP
    print("[SENDING] Connecting to Gmail SMTP...")
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, app_password)
    
    print("[SENDING] Sending email...")
    server.send_message(msg)
    server.quit()
    
    print(f"[SUCCESS] Email sent to {recipient_email}")
    print(f"[FORMAT] HTML with tracking pixel")
    print(f"[TRACKING ID] {tracking_id}")
    print("\n[NEXT] Open the email at hassnain@digivine.us")
    print("[CHECK] Then visit: http://localhost:5000/api/tracking-log")
    print("[EXPECTED] You should see the open recorded")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
