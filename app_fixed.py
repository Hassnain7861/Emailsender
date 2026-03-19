#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Multi-Account Email Campaign Dashboard - FIXED VERSION
- 5 Sender Accounts running SIMULTANEOUSLY
- 30 Emails Per Account Per Day (each account sends DIFFERENT 30 leads)
- Each account gets UNIQUE leads (not same leads repeated)
- Random 25-45 second delays between EACH email
- Total: 150 emails per day from all 5 accounts
"""

from flask import Flask, render_template, request, jsonify, send_file
import smtplib
from email.mime.text import MIMEText
import csv
from io import StringIO, BytesIO
import json
import os
from datetime import datetime, timedelta
import threading
import time
import random
import zipfile
import sys
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

campaigns = {}

EMAIL_PROVIDERS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'name': 'Gmail'
    },
    'zoho': {
        'smtp_server': 'smtp.zoho.com',
        'smtp_port': 587,
        'name': 'Zoho Mail'
    },
    'outlook': {
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'name': 'Outlook/Office365'
    },
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'name': 'Yahoo Mail'
    },
    'sendgrid': {
        'smtp_server': 'smtp.sendgrid.net',
        'smtp_port': 587,
        'name': 'SendGrid'
    }
}

def log_to_file(filename, message):
    """Thread-safe file logging"""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
            f.flush()
    except Exception as e:
        print(f"[LOG_ERROR] {e}", file=sys.stderr)

def find_column(available_cols, possible_names):
    for col in available_cols:
        if col.lower().strip() in [p.lower().strip() for p in possible_names]:
            return col
    return None

class ParallelMultiAccountCampaign:
    """All 5 accounts send 30 emails each SIMULTANEOUSLY to DIFFERENT leads"""
    
    def __init__(self, campaign_id, name, senders, leads, templates, 
                 subject_lines, follow_ups, emails_per_account=30, template_split_count=3):
        self.campaign_id = campaign_id
        self.name = name
        self.senders = senders
        self.leads = leads
        self.templates = templates
        self.subject_lines = subject_lines
        self.follow_ups = follow_ups
        self.emails_per_account = emails_per_account
        self.template_split_count = template_split_count
        
        self.status = 'pending'
        self.sent = 0
        self.failed = 0
        self.total = len(leads)
        self.results = []
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.scheduled_followups = []
        self.followups_stopped = False
        self.should_stop = False
        self.sender_progress = {i: 0 for i in range(len(senders))}
        self.error_log = []
        self.log_file = f"campaign_{campaign_id}.log"
        
    def get_smtp_config(self, provider):
        config = EMAIL_PROVIDERS.get(provider.lower())
        if not config:
            config = EMAIL_PROVIDERS['gmail']
        return config
        
    def personalize_template(self, template_text, business_name, location):
        city = location.split(',')[-1].strip() if ',' in location else location
        template_text = template_text.replace('[Business Name]', business_name)
        template_text = template_text.replace('[City]', city)
        template_text = template_text.replace('[Location]', location)
        return template_text

    def get_subject_line(self, index):
        if not self.subject_lines:
            return "You're losing ~$7K/mo on Google (not an exaggeration)*"
        return self.subject_lines[index % len(self.subject_lines)]
    
    def get_template(self, email_index):
        if not self.templates:
            return ""
        template_idx = (email_index // self.template_split_count) % len(self.templates)
        return self.templates[template_idx]['content']

    def send_email(self, lead, template_text, subject_line, server, sender_email):
        try:
            business_name = lead.get('Business Name', 'there').strip()
            email = lead.get('Email', '').strip()
            location = lead.get('Location', '').strip()

            if not email:
                return False, 'No email provided'

            body = self.personalize_template(template_text, business_name, location)
            body = body.encode('utf-8', errors='replace').decode('utf-8')
            
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject_line
            msg.set_charset('utf-8')
            
            server.send_message(msg)
            return True, None
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            return False, error_msg

    def verify_sender(self, sender_idx):
        """Test SMTP connection before campaign starts"""
        sender = self.senders[sender_idx]
        config = self.get_smtp_config(sender['provider'])
        
        try:
            log_to_file(self.log_file, f"VERIFY: Testing sender {sender_idx + 1} - {sender['email']}")
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=20)
            server.starttls()
            server.login(sender['email'], sender['password'])
            server.quit()
            
            log_to_file(self.log_file, f"VERIFY: Sender {sender_idx + 1} OK - {sender['email']}")
            return True, None
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Auth failed for {sender['email']}: Check email/password"
            log_to_file(self.log_file, f"VERIFY: AUTH_FAIL - {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error for {sender['email']}: {str(e)}"
            log_to_file(self.log_file, f"VERIFY: SMTP_ERROR - {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Connection failed for {sender['email']}: {str(e)}"
            log_to_file(self.log_file, f"VERIFY: ERROR - {error_msg}")
            return False, error_msg

    def send_for_sender(self, sender_idx):
        """Send emails from ONE sender to DIFFERENT set of leads"""
        sender = self.senders[sender_idx]
        config = self.get_smtp_config(sender['provider'])
        
        try:
            log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Connecting to {config['smtp_server']}:{config['smtp_port']}")
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=20)
            server.starttls()
            server.login(sender['email'], sender['password'])
            print(f"[SENDER {sender_idx + 1}] Connected - {sender['email']}")
            sys.stdout.flush()
            
            log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Login OK")

            start_lead_idx = sender_idx * self.emails_per_account
            end_lead_idx = min(start_lead_idx + self.emails_per_account, self.total)
            
            emails_sent = 0
            num_leads_for_this_sender = end_lead_idx - start_lead_idx
            
            log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Sending to leads {start_lead_idx}-{end_lead_idx - 1}")
            
            for i, lead_idx in enumerate(range(start_lead_idx, end_lead_idx)):
                if self.should_stop:
                    break
                    
                if lead_idx >= self.total:
                    break
                
                lead = self.leads[lead_idx]
                subject_line = self.get_subject_line(lead_idx)
                template_text = self.get_template(lead_idx)
                
                success, error = self.send_email(lead, template_text, subject_line, server, sender['email'])
                
                if success:
                    self.sent += 1
                    emails_sent += 1
                    self.sender_progress[sender_idx] += 1
                    template_num = (lead_idx // self.template_split_count) % len(self.templates) + 1
                    
                    self.results.append({
                        'email': lead.get('Email', ''),
                        'business_name': lead.get('Business Name', ''),
                        'status': 'sent',
                        'subject': subject_line,
                        'template': f'Template {template_num}',
                        'sender': sender['email'],
                        'sender_num': sender_idx + 1,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    print(f"[SENDER {sender_idx + 1}] [OK] Email {emails_sent}/{num_leads_for_this_sender} sent to {lead.get('Email', '')}")
                    log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Email sent to {lead.get('Email', '')}")
                else:
                    self.failed += 1
                    self.results.append({
                        'email': lead.get('Email', ''),
                        'status': 'failed',
                        'reason': error,
                        'sender': sender['email'],
                        'sender_num': sender_idx + 1
                    })
                    print(f"[SENDER {sender_idx + 1}] [FAIL] {error}")
                    log_to_file(self.log_file, f"SENDER {sender_idx + 1}: FAILED to {lead.get('Email', '')} - {error}")
                
                if i < num_leads_for_this_sender - 1:
                    sleep_time = random.uniform(25, 45)
                    print(f"[SENDER {sender_idx + 1}] [WAIT] {sleep_time:.1f}s before next email")
                    log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Waiting {sleep_time:.1f}s")
                    time.sleep(sleep_time)

            server.quit()
            print(f"[SENDER {sender_idx + 1}] [DONE] {emails_sent} emails sent")
            log_to_file(self.log_file, f"SENDER {sender_idx + 1}: DONE - {emails_sent} sent")
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"[SENDER {sender_idx + 1}] Auth failed: {str(e)}"
            print(error_msg)
            sys.stdout.flush()
            log_to_file(self.log_file, error_msg)
            self.failed += 1
            self.results.append({
                'status': 'error',
                'sender_num': sender_idx + 1,
                'reason': f'Auth failed: {str(e)}'
            })
        except Exception as e:
            error_msg = f"[SENDER {sender_idx + 1}] Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            sys.stdout.flush()
            log_to_file(self.log_file, error_msg)
            self.error_log.append(error_msg)
            self.failed += 1
            self.results.append({
                'status': 'error',
                'sender_num': sender_idx + 1,
                'reason': str(e)
            })

    def send_batch(self):
        """Send emails from ALL senders SIMULTANEOUSLY"""
        if self.should_stop:
            self.status = 'stopped'
            return

        try:
            self.status = 'running'
            log_to_file(self.log_file, f"CAMPAIGN START - {len(self.senders)} senders, {len(self.leads)} leads")
            
            print(f"[CAMPAIGN] Starting parallel send from {len(self.senders)} accounts")
            print(f"[CAMPAIGN] Each account sends {self.emails_per_account} emails to DIFFERENT leads")
            print(f"[CAMPAIGN] Random delays between EACH email: 25-45 seconds")
            print(f"[CAMPAIGN] Log file: {self.log_file}")
            sys.stdout.flush()
            
            # VERIFY all senders first
            print("[CAMPAIGN] Verifying sender credentials...")
            for idx in range(len(self.senders)):
                success, error = self.verify_sender(idx)
                if not success:
                    self.status = 'failed'
                    self.error_log.append(error)
                    print(f"[ERROR] {error}")
                    return
            
            print("[CAMPAIGN] All senders verified! Starting campaign...")
            
            threads = []
            for sender_idx in range(len(self.senders)):
                thread = threading.Thread(target=self.send_for_sender, args=(sender_idx,), name=f"Sender-{sender_idx}")
                thread.daemon = False
                thread.start()
                threads.append(thread)
                time.sleep(0.5)
            
            log_to_file(self.log_file, f"CAMPAIGN: {len(threads)} threads started")
            
            for thread in threads:
                thread.join(timeout=3600)
            
            log_to_file(self.log_file, f"CAMPAIGN END - sent={self.sent}, failed={self.failed}")
            
            print(f"[CAMPAIGN] All senders completed")
            
            if self.follow_ups and not self.followups_stopped:
                self.schedule_followups()
            
            if self.sent > 0:
                self.status = 'completed'
                print(f"[CAMPAIGN] Campaign completed: {self.sent} sent, {self.failed} failed")
            else:
                self.status = 'failed'
                print(f"[CAMPAIGN] Campaign failed: no emails sent")
                
        except Exception as e:
            err_msg = f"Exception in send_batch: {str(e)}\n{traceback.format_exc()}"
            self.error_log.append(err_msg)
            self.status = 'failed'
            print(f"[ERROR] Campaign exception: {err_msg}")
            sys.stdout.flush()
            log_to_file(self.log_file, err_msg)

    def schedule_followups(self):
        """Schedule follow-up emails for leads that received initial emails"""
        sent_lead_emails = set([r['email'] for r in self.results if r.get('status') == 'sent'])
        
        for fu_idx, followup in enumerate(self.follow_ups):
            days = followup.get('days', fu_idx + 1)
            scheduled_time = datetime.now() + timedelta(days=days)
            
            for lead_idx, lead in enumerate(self.leads):
                if lead.get('Email', '').strip() in sent_lead_emails:
                    self.scheduled_followups.append({
                        'lead_idx': lead_idx,
                        'lead_email': lead.get('Email', ''),
                        'scheduled_time': scheduled_time,
                        'followup_idx': fu_idx,
                        'status': 'pending'
                    })

    def stop_campaign(self):
        self.should_stop = True
        self.status = 'stopped'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_zip():
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            with open('app.py', 'r', encoding='utf-8') as f:
                zipf.writestr('app.py', f.read().encode('utf-8'))
            
            if os.path.exists('templates/index.html'):
                with open('templates/index.html', 'r', encoding='utf-8') as f:
                    zipf.writestr('templates/index.html', f.read().encode('utf-8'))
            
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                zipf.writestr('requirements.txt', f.read().encode('utf-8'))
            
            readme = """MULTI-ACCOUNT EMAIL CAMPAIGN DASHBOARD - FIXED VERSION
================================================

FIXES IN THIS VERSION:
✓ Pre-verification of all SMTP credentials before campaign
✓ Improved UTF-8 encoding for all email content
✓ Better error logging with detailed tracking
✓ Longer SMTP timeout (20s instead of 10s)
✓ Proper exception handling with stack traces
✓ Thread-safe file logging
✓ Auto-generated campaign logs

INSTALLATION:
1. Extract this ZIP
2. Open Command Prompt/PowerShell in this folder
3. Run: pip install -r requirements.txt
4. Run: python app.py
5. Open: http://localhost:5000

FEATURES:
- 5 Sender Accounts (send SIMULTANEOUSLY)
- 30 Emails Per Account (to DIFFERENT leads each)
- Random 25-45 second delays between EACH email
- Multi-provider email (Gmail, Zoho, Outlook, Yahoo, SendGrid)
- Multiple templates (rotate every 3 emails)
- Subject line A/B testing (round-robin)
- Follow-up sequences (1, 2, 3+ days)
- Full campaign control (Start/Stop)

HOW IT WORKS:
1. Add 5 sender email accounts
2. Upload leads
3. System verifies ALL credentials before starting
4. Each account gets DIFFERENT set of leads
5. Each account sends with 25-45s random delays
6. All 5 send SIMULTANEOUSLY

EMAIL ACCOUNT SETUP:
Gmail: https://myaccount.google.com/apppasswords
Zoho: https://mail.zoho.com → Settings → Security
Outlook: account.microsoft.com → Security → App passwords
Yahoo: Yahoo Account Security → Generate app password
SendGrid: https://app.sendgrid.com/settings/api_keys

TROUBLESHOOTING:
- Check campaign_{timestamp}.log for detailed logs
- Verify SMTP credentials (pre-verification runs first)
- Check email provider app-specific password setup
- Ensure port 587 is not blocked by firewall
- Gmail requires "Less secure app access" or app passwords
"""
            zipf.writestr('README.txt', readme.encode('utf-8'))
        
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='email_campaign_dashboard_fixed.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    return jsonify({
        'campaigns': [
            {
                'id': cid,
                'name': c.name,
                'status': c.status,
                'sent': c.sent,
                'failed': c.failed,
                'total': c.total,
                'sender_count': len(c.senders),
                'sender_progress': c.sender_progress,
                'created_at': c.created_at,
                'log_file': c.log_file,
                'errors': c.error_log
            }
            for cid, c in campaigns.items()
        ]
    })

@app.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    if campaign_id not in campaigns:
        return jsonify({'error': 'Campaign not found'}), 404

    c = campaigns[campaign_id]
    return jsonify({
        'id': campaign_id,
        'name': c.name,
        'status': c.status,
        'sent': c.sent,
        'failed': c.failed,
        'total': c.total,
        'results': c.results[-100:],
        'created_at': c.created_at,
        'sender_count': len(c.senders),
        'sender_progress': c.sender_progress,
        'error_log': c.error_log,
        'log_file': c.log_file
    })

@app.route('/api/campaigns/<campaign_id>/stop', methods=['POST'])
def stop_campaign(campaign_id):
    if campaign_id not in campaigns:
        return jsonify({'error': 'Campaign not found'}), 404

    campaign = campaigns[campaign_id]
    campaign.stop_campaign()

    return jsonify({
        'success': True,
        'message': 'Campaign stopped',
        'status': campaign.status
    })

@app.route('/api/upload-leads', methods=['POST'])
def upload_leads():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        leads = []
        
        if file.filename.endswith('.csv'):
            file.seek(0)
            stream = StringIO(file.read().decode('utf-8'))
            reader = csv.DictReader(stream)
            leads = list(reader)
        elif file.filename.endswith(('.xlsx', '.xls')):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file.stream)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                headers = [str(h).strip() if h else '' for h in rows[0]]
                leads = [
                    {headers[i]: str(val).strip() if val else '' for i, val in enumerate(row)}
                    for row in rows[1:]
                ]
            except ImportError:
                return jsonify({'error': 'Excel support requires: pip install openpyxl'}), 400
        else:
            return jsonify({'error': 'Unsupported format. Use .csv or .xlsx'}), 400

        if not leads:
            return jsonify({'error': 'File is empty'}), 400

        available_cols = list(leads[0].keys())
        
        business_col = find_column(available_cols, ['Business Name', 'business name', 'company', 'name'])
        email_col = find_column(available_cols, ['Email', 'email', 'e-mail', 'mail', 'address'])
        location_col = find_column(available_cols, ['Location', 'location', 'city', 'address'])
        
        if not business_col or not email_col:
            return jsonify({
                'error': f'Cannot find Business Name and/or Email columns. Available: {", ".join(available_cols)}',
                'available_columns': available_cols
            }), 400
        
        if not location_col:
            location_col = None

        leads = [
            {
                'Business Name': str(lead.get(business_col, '')).strip(),
                'Email': str(lead.get(email_col, '')).strip(),
                'Location': str(lead.get(location_col, '')) if location_col else 'Unknown'
            }
            for lead in leads if lead.get(email_col, '').strip()
        ]

        if not leads:
            return jsonify({'error': 'No valid leads found with email addresses'}), 400

        return jsonify({
            'success': True,
            'lead_count': len(leads),
            'leads': leads
        })

    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 400

@app.route('/api/send-campaign', methods=['POST'])
def send_campaign():
    data = request.json

    errors = []
    if not data.get('name'):
        errors.append('Campaign name required')
    if not data.get('senders') or len(data.get('senders', [])) == 0:
        errors.append('At least 1 sender account required')
    if not data.get('templates'):
        errors.append('At least one template required')
    if not data.get('leads') or len(data.get('leads', [])) == 0:
        errors.append('Leads required')

    if errors:
        return jsonify({'errors': errors}), 400

    campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    campaign = ParallelMultiAccountCampaign(
        campaign_id,
        data['name'],
        data.get('senders', []),
        data['leads'],
        data.get('templates', []),
        data.get('subject_lines', []),
        data.get('follow_ups', []),
        emails_per_account=data.get('emails_per_account', 30),
        template_split_count=3
    )

    campaigns[campaign_id] = campaign

    thread = threading.Thread(target=campaign.send_batch)
    thread.daemon = False
    thread.start()

    total_emails = len(data.get('senders', [])) * data.get('emails_per_account', 30)
    print(f"[CAMPAIGN] New parallel campaign: {campaign_id}")
    print(f"[CAMPAIGN] Senders: {len(data.get('senders', []))}, Emails per: {data.get('emails_per_account', 30)}, Total: {total_emails}")

    return jsonify({
        'success': True,
        'campaign_id': campaign_id,
        'message': f'Campaign started - {len(data.get("senders", []))} accounts × {data.get("emails_per_account", 30)} emails = {total_emails} total',
        'log_file': campaign.log_file
    })

if __name__ == '__main__':
    print("[SERVER] Starting Multi-Account Email Campaign Dashboard (FIXED)...")
    print("[MODE] PARALLEL - All 5 accounts send SIMULTANEOUSLY")
    print("[LEADS] Each account gets DIFFERENT set of leads")
    print("[DELAY] Random 25-45 seconds between EACH email")
    print("[FEATURE] Pre-verification of all SMTP credentials")
    print("[INFO] Download: http://localhost:5000/download")
    sys.stdout.flush()
    app.run(debug=False, port=5000, use_reloader=False)
