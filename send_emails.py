#!/usr/bin/env python3
"""
Zoho Mail - Bulk Email Sender
Sends personalized emails from your Zoho account to contacts in a CSV/TSV
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from io import StringIO
import sys

def create_email_body(business_name, location):
    """Generate personalized email body"""
    # Extract city from location
    city = location.split(',')[-1].strip() if ',' in location else location
    
    body = f"""Hey {business_name},

When I Searched "plumber in {city}" today.

You're not in the top 10.

97% of people never scroll past position 3. So every day you're invisible — a competitor is taking a job that should've been yours.

I found 5 things killing your ranking. Fixed two of them already as a demo:

→ Your meta title is costing you clicks
→ Your page content isn't matching what Google wants to rank

The other 3 fixes are bigger. And faster to implement than you think.

Reply "interested" and I'll send them over. No call needed, no pitch deck — just the fixes.

— Hassnain K"""
    
    return body

def send_emails(sender_email, app_password, contacts):
    """Send emails via Zoho SMTP"""
    
    smtp_server = "smtp.zoho.com"
    smtp_port = 587
    
    try:
        # Connect to Zoho SMTP
        print(f"\n📧 Connecting to Zoho Mail ({smtp_server}:{smtp_port})...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login
        print(f"🔑 Authenticating as {sender_email}...")
        server.login(sender_email, app_password)
        print("✓ Authentication successful!\n")
        
        # Send emails
        success_count = 0
        for idx, contact in enumerate(contacts, 1):
            business_name = contact['Business Name'].strip()
            email = contact['Email'].strip()
            location = contact['Location'].strip()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "You're losing ~$7K/mo on Google (not an exaggeration)*"
            
            body = create_email_body(business_name, location)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send
            try:
                server.send_message(msg)
                print(f"[{idx}] ✓ Sent to {email}")
                print(f"    Business: {business_name} | Location: {location}\n")
                success_count += 1
            except Exception as e:
                print(f"[{idx}] ❌ Failed to send to {email}: {e}\n")
        
        server.quit()
        
        print("=" * 60)
        print(f"✓ Successfully sent {success_count}/{len(contacts)} emails!")
        print("=" * 60)
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication failed!")
        print("   - Check your Zoho email address")
        print("   - Generate a new app password at: https://mail.zoho.com/zm/#settings/security")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def main():
    print("\n" + "=" * 60)
    print("ZOHO MAIL - BULK EMAIL SENDER")
    print("=" * 60)
    
    # Get Zoho credentials
    print("\n📝 Enter your Zoho Mail credentials:")
    sender_email = input("Zoho email address: ").strip()
    app_password = input("Zoho app password: ").strip()
    
    if not sender_email or not app_password:
        print("❌ Email and password are required!")
        sys.exit(1)
    
    # Sample data
    data = """Business Name	Email	Location
Digivine	hassnainbaloch233@gmail.com	Block17, Dera ghazi khan"""
    
    # Parse contacts
    reader = csv.DictReader(StringIO(data), delimiter='\t')
    contacts = list(reader)
    
    if not contacts:
        print("❌ No contacts found!")
        sys.exit(1)
    
    print(f"\n📋 Found {len(contacts)} contact(s):")
    for contact in contacts:
        print(f"   • {contact['Business Name']} ({contact['Email']})")
    
    # Confirm before sending
    confirm = input("\n⚠️  Send emails? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)
    
    # Send emails
    send_emails(sender_email, app_password, contacts)

if __name__ == "__main__":
    main()
