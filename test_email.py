import smtplib
from email.mime.text import MIMEText

sender_email = "HASSNAINBALOCH233@GMAIL.COM"
app_password = "uxwl qavz ofuv blyd"
recipient = "DIGIVINE.HQ@GMAIL.COM"

try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.starttls()
    server.login(sender_email, app_password)
    print("[OK] Connected and authenticated")
    
    msg = MIMEText("Test message from Gordon")
    msg['Subject'] = "Test Subject"
    msg['From'] = sender_email
    msg['To'] = recipient
    
    server.send_message(msg)
    print("[OK] Email sent successfully")
    server.quit()
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)}")
