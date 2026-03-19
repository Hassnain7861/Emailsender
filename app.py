#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
if 'pytest' not in sys.modules:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Multi-Account Email Campaign Dashboard - OPTIMIZED FOR PARALLEL SENDING
- 5 Independent Sender Workers (true parallelism)
- Even lead distribution (30 leads per worker)
- Smooth sending patterns (no bursts)
- Randomized delays per speed mode
- Persistent email_logs tracking
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from io import StringIO, BytesIO
import json
import os
from datetime import datetime, timedelta
import threading
import time
import random
import zipfile
import traceback
import queue
import html
from contextlib import nullcontext
import fnmatch

_here = os.path.dirname(os.path.abspath(__file__))

# DYNAMIC TEMPLATE LOCATOR (Anti-GitHub-Upload-Mistake Fix)
# Scans the entire /app container to find exactly where index.html ended up.
found_template_dir = os.path.join(_here, 'templates')
for root, dirs, files in os.walk(_here):
    if 'index.html' in files:
        found_template_dir = root
        break

app = Flask(__name__, template_folder=found_template_dir)

print(f"=== FLASK BOOTING ===")
print(f"Resolved template_folder to: {found_template_dir}")
print(f"Active Tracking Base: {app.config['TRACKING_BASE_URL']}")
import sys
sys.stdout.flush()
print(f"=====================")

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
# CRM: feature flag and config (does not change existing email_logs/sent_leads)
app.config['ENABLE_CRM'] = os.environ.get('ENABLE_CRM', '1').strip().lower() in ('1', 'true', 'yes')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///crm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Allow SQLite to work with Flask's multi-threaded dev server
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'check_same_thread': False}}

# Tracking fallback: 1. ENV, 2. Render auto-url, 3. localhost
app.config['TRACKING_BASE_URL'] = os.environ.get('TRACKING_BASE_URL') or \
                                  os.environ.get('RENDER_EXTERNAL_URL') or \
                                  'http://localhost:5000'

app.config['REMINDER_DAYS'] = int(os.environ.get('REMINDER_DAYS', '3'))
app.config['ENABLE_AUTO_FOLLOWUP'] = os.environ.get('ENABLE_AUTO_FOLLOWUP', '0').strip().lower() in ('1', 'true', 'yes')
app.config['MAX_FOLLOWUP_COUNT'] = int(os.environ.get('MAX_FOLLOWUP_COUNT', '3'))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# CRM DB (optional; existing logs unchanged)
if app.config['ENABLE_CRM']:
    from crm_models import init_db
    init_db(app)
    from crm import (
        normalize_email, get_or_create_lead, lead_exists_by_email,
        create_campaign, check_already_sent, record_sent_and_get_tracking_id,
        mark_opened, mark_clicked, wrap_links_for_tracking, inject_tracking_pixel,
        update_campaign_status, get_leads_needing_followup, update_email_status
    )
# In-memory reminder alerts (CRM job populates; does not affect sending)
REMINDER_ALERTS = []

campaigns = {}
EMAIL_LOGS_FILE = 'email_logs.json'
SENT_LEADS_FILE = 'sent_leads.json'

EMAIL_PROVIDERS = {
    'gmail': {'smtp_server': 'smtp.gmail.com', 'smtp_port': 587, 'name': 'Gmail'},
    'zoho': {'smtp_server': 'smtp.zoho.com', 'smtp_port': 587, 'name': 'Zoho Mail'},
    'outlook': {'smtp_server': 'smtp.office365.com', 'smtp_port': 587, 'name': 'Outlook'},
    'yahoo': {'smtp_server': 'smtp.mail.yahoo.com', 'smtp_port': 587, 'name': 'Yahoo Mail'},
    'sendgrid': {'smtp_server': 'smtp.sendgrid.net', 'smtp_port': 587, 'name': 'SendGrid'}
}

# 3 speed options: balance between deliverability and speed (5 mailboxes send in parallel)
SPEED_MODES = {
    'slow': {'min': 45, 'max': 60, 'label': 'Slow (45–60s between emails)'},
    'medium': {'min': 20, 'max': 35, 'label': 'Medium (20–35s between emails)'},
    'fast': {'min': 8, 'max': 18, 'label': 'Fast (8–18s between emails)'},
}

def log_to_file(filename, message):
    """Thread-safe file logging"""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
            f.flush()
    except Exception as e:
        print(f"[LOG_ERROR] {e}", file=sys.stderr)

def load_email_logs():
    """Load email sending history"""
    if os.path.exists(EMAIL_LOGS_FILE):
        try:
            with open(EMAIL_LOGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'logs': []}
    return {'logs': []}

def save_email_logs(logs):
    """Save email sending history"""
    try:
        with open(EMAIL_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save email logs: {e}")

def log_email_sent(lead_email, campaign_id, sender_email, status='sent'):
    """Log email send event"""
    logs = load_email_logs()
    logs['logs'].append({
        'lead_email': lead_email.lower().strip(),
        'campaign_id': campaign_id,
        'sender_email': sender_email,
        'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    })
    save_email_logs(logs)

def is_lead_already_sent(lead_email):
    """Check if lead was sent in previous campaigns"""
    logs = load_email_logs()
    lead_lower = lead_email.lower().strip()
    return any(log['lead_email'] == lead_lower for log in logs['logs'])

def load_sent_leads():
    """Load set of already-sent email addresses"""
    if os.path.exists(SENT_LEADS_FILE):
        try:
            with open(SENT_LEADS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('sent_emails', []))
        except:
            return set()
    return set()

def save_sent_leads(sent_set):
    """Save sent email addresses"""
    try:
        with open(SENT_LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'sent_emails': list(sent_set),
                'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_sent': len(sent_set)
            }, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save sent leads: {e}")

def add_to_sent_leads(email):
    """Add email to sent list"""
    sent_set = load_sent_leads()
    sent_set.add(email.lower().strip())
    save_sent_leads(sent_set)

def find_column(available_cols, possible_names):
    for col in available_cols:
        if col.lower().strip() in [p.lower().strip() for p in possible_names]:
            return col
    return None

class ParallelWorkerCampaign:
    """Campaign with true parallel workers - one worker per sender"""
    
    def __init__(self, campaign_id, name, senders, leads, templates, 
                 subject_lines, follow_ups, speed_mode='medium', custom_min=None, custom_max=None,
                 allow_resend=False, crm_campaign_id=None, tracking_base_url=''):
        self.campaign_id = campaign_id
        self.name = name
        self.senders = senders
        self.leads = leads
        self.templates = templates
        self.subject_lines = subject_lines
        self.follow_ups = follow_ups
        self.speed_mode = speed_mode
        self.allow_resend = allow_resend
        self.crm_campaign_id = crm_campaign_id or campaign_id
        self.tracking_base_url = (tracking_base_url or '').rstrip('/')
        
        # Speed configuration
        if speed_mode == 'custom' and custom_min is not None and custom_max is not None:
            self.delay_range = {'min': custom_min, 'max': custom_max}
        else:
            self.delay_range = SPEED_MODES.get(speed_mode, SPEED_MODES['medium'])
        
        self.status = 'pending'
        self.sent = 0
        self.failed = 0
        self.skipped = 0
        self.total = len(leads)
        self.results = []
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.should_stop = False
        self.sender_progress = {i: 0 for i in range(len(senders))}
        self.error_log = []
        self.log_file = f"campaign_{campaign_id}.log"
        self.worker_threads = {}
        
        # Distribute leads evenly across senders
        self.leads_per_sender = max(1, len(leads) // len(senders))
        self.distribute_leads()
    
    def distribute_leads(self):
        """Distribute leads evenly across workers"""
        self.sender_leads = {}
        for i, sender in enumerate(self.senders):
            start_idx = i * self.leads_per_sender
            end_idx = start_idx + self.leads_per_sender if i < len(self.senders) - 1 else len(self.leads)
            self.sender_leads[i] = self.leads[start_idx:end_idx]
    
    def get_smtp_config(self, provider):
        config = EMAIL_PROVIDERS.get(provider.lower())
        return config if config else EMAIL_PROVIDERS['gmail']
    
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
        template_idx = email_index % len(self.templates)
        return self.templates[template_idx]['content']
    
    def create_smtp_connection(self, config, email, password):
        """Create fresh SMTP connection"""
        try:
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=20)
            server.starttls()
            server.login(email, password)
            return server, None
        except Exception as e:
            return None, str(e)
    
    def send_email_with_retry(self, lead, template_text, subject_line, sender, sender_idx, max_retries=3):
        """Send single email with retry logic. CRM: optional EmailsSent check, record, and tracking."""
        config = self.get_smtp_config(sender['provider'])
        business_name = lead.get('Business Name', 'there').strip()
        email = lead.get('Email', '').strip()
        location = lead.get('Location', '').strip()
        lead_id = lead.get('lead_id') if isinstance(lead.get('lead_id'), int) else None

        if not email:
            return False, 'No email provided'

        # Safety: sender fields can accidentally be non-strings from malformed UI payload.
        sender_email = sender.get('email', '')
        sender_password = sender.get('password', '')
        if isinstance(sender_email, list):
            sender_email = "\n".join(str(x) for x in sender_email)
        if isinstance(sender_password, list):
            sender_password = "\n".join(str(x) for x in sender_password)
        sender_email = str(sender_email)
        sender_password = str(sender_password)
        email = str(email)

        # CRM: skip if already sent for this campaign (unless allow_resend)
        if app.config.get('ENABLE_CRM') and lead_id and self.crm_campaign_id:
            try:
                if check_already_sent(lead_id, self.crm_campaign_id) and not self.allow_resend:
                    self.skipped += 1
                    log_to_file(self.log_file, f"SENDER {sender_idx + 1}: ⏭️ Skipped {email} (already sent this campaign)")
                    return True, None
            except Exception as e:
                log_to_file('crm_tracking_errors.log', f"[CHECK_ALREADYSENT] lead_id={lead_id} campaign_id={self.crm_campaign_id} err={str(e)[:200]}")
                pass

        # Check if already sent (existing file-based check)
        if is_lead_already_sent(email):
            self.skipped += 1
            log_to_file(self.log_file, f"SENDER {sender_idx + 1}: ⏭️ Skipped {email} (already sent)")
            return True, None  # Mark as success to skip

        tracking_id = None
        if app.config.get('ENABLE_CRM') and lead_id and self.crm_campaign_id and self.tracking_base_url:
            try:
                tracking_id = record_sent_and_get_tracking_id(lead_id, self.crm_campaign_id)
            except Exception as e:
                log_to_file('crm_tracking_errors.log', f"[RECORD_SENT] lead_id={lead_id} campaign_id={self.crm_campaign_id} err={str(e)[:200]}")
                pass
        
        for attempt in range(max_retries):
            try:
                server, conn_error = self.create_smtp_connection(config, sender_email, sender_password)
                if not server:
                    if attempt < max_retries - 1:
                        wait_time = 5 + (attempt * 3)
                        log_to_file(self.log_file, f"SENDER {sender_idx + 1}: Retrying connection in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    if tracking_id and app.config.get('ENABLE_CRM'):
                        try:
                            with app.app_context():
                                update_email_status(tracking_id, 'failed', f"Connection failed: {conn_error}")
                        except Exception:
                            pass
                    return False, f"Connection failed: {conn_error}"

                # UI payload safety: template_text / subject_line might accidentally be non-string.
                # Coerce without changing the overall sending flow.
                if isinstance(template_text, list):
                    template_text = "\n".join(str(x) for x in template_text)
                elif not isinstance(template_text, str):
                    template_text = str(template_text)
                if isinstance(subject_line, list):
                    subject_line = " / ".join(str(x) for x in subject_line)
                elif not isinstance(subject_line, str):
                    subject_line = str(subject_line)

                body_plain = self.personalize_template(template_text, business_name, location)
                # Safety: template/body can accidentally become non-string (e.g. list) from malformed UI payload.
                # Coerce to string without changing the actual sending flow.
                if isinstance(body_plain, list):
                    log_to_file(self.log_file, f"WORKER {sender_idx + 1}: Body was list; coercing to string")
                    body_plain = "\n".join(str(x) for x in body_plain)
                elif not isinstance(body_plain, str):
                    body_plain = str(body_plain)
                body_plain = body_plain.encode('utf-8', errors='replace').decode('utf-8')

                if tracking_id and self.tracking_base_url:
                    body_with_links = wrap_links_for_tracking(body_plain, self.tracking_base_url, tracking_id)
                    body_html = inject_tracking_pixel(body_with_links, self.tracking_base_url, tracking_id)
                    msg = MIMEMultipart('alternative')
                    msg.attach(MIMEText(body_plain, 'plain', 'utf-8'))
                    msg.attach(MIMEText(body_html, 'html', 'utf-8'))
                else:
                    msg = MIMEText(body_plain, 'plain', 'utf-8')

                msg['From'] = sender_email
                msg['To'] = email
                msg['Subject'] = str(subject_line)

                server.send_message(msg)
                server.quit()

                if tracking_id and app.config.get('ENABLE_CRM'):
                    try:
                        with app.app_context():
                            update_email_status(tracking_id, 'sent')
                    except Exception:
                        pass

                return True, None
                
            except smtplib.SMTPServerDisconnected:
                if attempt < max_retries - 1:
                    time.sleep(5 + (attempt * 3))
                    continue
                if tracking_id and app.config.get('ENABLE_CRM'):
                    try:
                        with app.app_context():
                            update_email_status(tracking_id, 'failed', "Server disconnected")
                    except Exception:
                        pass
                return False, "Server disconnected"
            except Exception as e:
                if attempt < max_retries - 1:
                    import traceback as _tb
                    try:
                        body_plain_type = type(body_plain).__name__
                    except Exception:
                        body_plain_type = 'unknown'
                    try:
                        template_type = type(template_text).__name__
                    except Exception:
                        template_type = 'unknown'
                    try:
                        subj_type = type(subject_line).__name__
                    except Exception:
                        subj_type = 'unknown'
                    try:
                        sender_email_type = type(sender_email).__name__
                    except Exception:
                        sender_email_type = 'unknown'
                    try:
                        sender_password_type = type(sender_password).__name__
                    except Exception:
                        sender_password_type = 'unknown'
                    log_to_file(
                        self.log_file,
                        f"WORKER {sender_idx + 1}: send error template_type={template_type} subject_type={subj_type} body_plain_type={body_plain_type} sender_email_type={sender_email_type} sender_password_type={sender_password_type} err={str(e)[:200]}\n{_tb.format_exc()}"
                    )
                    time.sleep(5 + (attempt * 3))
                    continue
                if tracking_id and app.config.get('ENABLE_CRM'):
                    try:
                        with app.app_context():
                            update_email_status(tracking_id, 'failed', str(e)[:500])
                    except Exception:
                        pass
                return False, str(e)
        
        return False, f"Failed after {max_retries} attempts"
    
    def worker_process(self, sender_idx):
        """Independent worker process - one per sender"""
        sender = self.senders[sender_idx]
        sender_leads = self.sender_leads.get(sender_idx, [])
        
        log_to_file(self.log_file, f"WORKER {sender_idx + 1}: Starting - {sender['email']} ({len(sender_leads)} leads)")
        print(f"[WORKER {sender_idx + 1}] Started - {sender['email']} ({len(sender_leads)} leads)")

        # CRM DB writes require Flask app context (worker threads otherwise break silently).
        ctx = app.app_context() if app.config.get('ENABLE_CRM') else nullcontext()
        with ctx:
            for email_idx, lead in enumerate(sender_leads):
                if self.should_stop:
                    break

                subject_line = self.get_subject_line(email_idx)
                template_text = self.get_template(email_idx)

                success, error = self.send_email_with_retry(
                    lead, template_text, subject_line, sender, sender_idx
                )

                if success and not is_lead_already_sent(lead.get('Email', '')):
                    self.sent += 1
                    self.sender_progress[sender_idx] += 1
                    email = lead.get('Email', '')
                    log_email_sent(email, self.campaign_id, sender['email'], 'sent')
                    add_to_sent_leads(email)

                    self.results.append({
                        'email': email,
                        'business_name': lead.get('Business Name', ''),
                        'status': 'sent',
                        'subject': subject_line,
                        'sender': sender['email'],
                        'sender_num': sender_idx + 1,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    print(f"[WORKER {sender_idx + 1}] ✓ {self.sender_progress[sender_idx]}/{len(sender_leads)} → {email}")
                    log_to_file(self.log_file, f"WORKER {sender_idx + 1}: ✓ Sent to {email}")
                elif error and 'already sent' not in error:
                    self.failed += 1
                    self.results.append({
                        'email': lead.get('Email', ''),
                        'status': 'failed',
                        'reason': error,
                        'sender': sender['email'],
                        'sender_num': sender_idx + 1
                    })
                    print(f"[WORKER {sender_idx + 1}] ✗ {lead.get('Email', '')} - {error[:40]}")
                    log_to_file(self.log_file, f"WORKER {sender_idx + 1}: ✗ Failed to {lead.get('Email', '')} - {error}")

                # Smooth sending delay (no bursts)
                if email_idx < len(sender_leads) - 1:
                    delay = random.uniform(self.delay_range['min'], self.delay_range['max'])
                    print(f"[WORKER {sender_idx + 1}] ⏱️ {delay:.1f}s delay ({self.speed_mode})")
                    log_to_file(self.log_file, f"WORKER {sender_idx + 1}: Waiting {delay:.1f}s")
                    time.sleep(delay)

        print(f"[WORKER {sender_idx + 1}] ✓ Done - {self.sender_progress[sender_idx]}/{len(sender_leads)}")
        log_to_file(self.log_file, f"WORKER {sender_idx + 1}: DONE")
    
    def start_campaign(self):
        """Start all workers in parallel"""
        self.status = 'running'
        log_to_file(self.log_file, f"CAMPAIGN START - {len(self.senders)} workers, {self.total} leads")
        log_to_file(self.log_file, f"Speed mode: {self.speed_mode} ({self.delay_range['min']}-{self.delay_range['max']}s)")
        log_to_file(self.log_file, f"Leads per worker: {self.leads_per_sender}")
        
        print(f"[CAMPAIGN] 🚀 Starting parallel send")
        print(f"[CAMPAIGN] {len(self.senders)} workers × {self.leads_per_sender} leads = {self.total} total")
        print(f"[CAMPAIGN] Speed: {self.speed_mode} ({self.delay_range['min']}-{self.delay_range['max']}s delays)")
        
        # Verify all senders
        print("[CAMPAIGN] Verifying senders...")
        for idx in range(len(self.senders)):
            config = self.get_smtp_config(self.senders[idx]['provider'])
            server, error = self.create_smtp_connection(config, self.senders[idx]['email'], self.senders[idx]['password'])
            if not server:
                self.status = 'failed'
                self.error_log.append(f"Sender {idx + 1} verification failed: {error}")
                print(f"[ERROR] Sender {idx + 1} verification failed: {error}")
                return
            server.quit()
        
        print("[CAMPAIGN] ✓ All senders verified!")
        
        # Start workers
        for sender_idx in range(len(self.senders)):
            thread = threading.Thread(target=self.worker_process, args=(sender_idx,), name=f"Worker-{sender_idx}")
            thread.daemon = False
            self.worker_threads[sender_idx] = thread
            thread.start()
            time.sleep(0.1)  # Minimal stagger
        
        # Wait for all workers
        for thread in self.worker_threads.values():
            thread.join(timeout=3600)
        
        log_to_file(self.log_file, f"CAMPAIGN END - sent={self.sent}, failed={self.failed}, skipped={self.skipped}")
        print(f"\n[CAMPAIGN] ✓ All workers completed!")
        print(f"[CAMPAIGN] Results: {self.sent} sent, {self.failed} failed, {self.skipped} skipped")
        
        if self.sent > 0:
            self.status = 'completed'
        else:
            self.status = 'failed'

        # CRM: sync campaign status to database
        if app.config.get('ENABLE_CRM') and self.crm_campaign_id:
            try:
                with app.app_context():
                    update_campaign_status(self.crm_campaign_id, self.status)
            except Exception as e:
                print(f"[CRM] Status sync error: {e}", file=sys.stderr)
    
    def stop_campaign(self):
        self.should_stop = True
        self.status = 'stopped'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-sender', methods=['POST'])
def test_sender():
    data = request.json
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    provider = data.get('provider', 'gmail').lower()
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    config = EMAIL_PROVIDERS.get(provider)
    if not config:
        return jsonify({'success': False, 'error': f'Unknown provider: {provider}'}), 400
    
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=15)
        server.starttls()
        server.login(email, password)
        server.quit()
        
        return jsonify({
            'success': True,
            'message': f'Connected to {config["name"]}',
            'provider': provider,
            'email': email
        })
    except smtplib.SMTPAuthenticationError:
        return jsonify({'success': False, 'error': 'Auth failed - Check email/password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': f'Connection error: {str(e)[:100]}'}), 500

@app.route('/api/upload-leads', methods=['POST'])
def upload_leads():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        leads = []
        # Fix: SpooledTemporaryFile in Python 3.10 lacks 'seekable' which some parsers expect.
        # We read the stream into BytesIO to provide a standard seekable buffer.
        file_bytes = file.read()
        file_stream = BytesIO(file_bytes)
        
        if file.filename.endswith('.csv'):
            stream = StringIO(file_bytes.decode('utf-8'))
            reader = csv.DictReader(stream)
            leads = list(reader)
        elif file.filename.endswith(('.xlsx', '.xls')):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_stream)
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
                'error': f'Cannot find Business Name and/or Email columns',
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
            return jsonify({'error': 'No valid leads found'}), 400

        # CRM: normalize and dedup (in-file duplicates skipped; existing Leads get lead_id, new ones inserted)
        crm_skipped = []
        if app.config.get('ENABLE_CRM'):
            seen = set()
            deduped = []
            for lead in leads:
                email = lead.get('Email', '')
                norm = (email.lower().strip() if email else '')
                if not norm:
                    continue
                if norm in seen:
                    crm_skipped.append(norm)
                    continue
                seen.add(norm)
                lead_obj = get_or_create_lead(norm, lead.get('Business Name', ''), 'new')
                lead['lead_id'] = lead_obj.id
                lead['Email'] = norm
                lead['Business Name'] = lead.get('Business Name', '').strip()
                deduped.append(lead)
            leads = deduped
            if crm_skipped:
                log_to_file('crm_import_skipped.log', f"Skipped in-file duplicates: {', '.join(crm_skipped[:50])}{'...' if len(crm_skipped) > 50 else ''}")

        sent_emails = load_sent_leads()
        original_count = len(leads)
        leads = [lead for lead in leads if lead.get('Email', '').lower().strip() not in sent_emails]
        skipped_count = original_count - len(leads)

        out_msg = f'Loaded {len(leads)} leads'
        if skipped_count > 0:
            out_msg += f' (skipped {skipped_count} already sent)'
        if crm_skipped:
            out_msg += f'; {len(crm_skipped)} duplicate(s) skipped at import'

        return jsonify({
            'success': True,
            'lead_count': len(leads),
            'leads': leads,
            'skipped_count': skipped_count,
            'original_count': original_count,
            'crm_skipped': len(crm_skipped) if app.config.get('ENABLE_CRM') else 0,
            'message': out_msg
        })

    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 400

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
                'skipped': c.skipped,
                'total': c.total,
                'sender_count': len(c.senders),
                'sender_progress': c.sender_progress,
                'created_at': c.created_at,
                'log_file': c.log_file,
                'speed_mode': c.speed_mode
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
        'skipped': c.skipped,
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

@app.route('/api/send-campaign', methods=['POST'])
def send_campaign():
    data = request.json

    errors = []
    if not data.get('name'):
        errors.append('Campaign name required')
    if not data.get('senders') or len(data.get('senders', [])) < 1:
        errors.append('At least 1 sender account required')
    if not data.get('templates'):
        errors.append('At least one template required')
    if not data.get('leads') or len(data.get('leads', [])) == 0:
        errors.append('Leads required')

    if errors:
        return jsonify({'errors': errors}), 400

    campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    leads = list(data['leads'])

    if app.config.get('ENABLE_CRM'):
        try:
            create_campaign(campaign_id, data['name'], data.get('description'))
            for lead in leads:
                if lead.get('lead_id') is None:
                    email = (lead.get('Email') or '').strip().lower()
                    if email:
                        lead_obj = get_or_create_lead(email, lead.get('Business Name', ''))
                        if lead_obj:
                            lead['lead_id'] = lead_obj.id
        except Exception:
            pass

    custom_min = data.get('custom_speed_min')
    custom_max = data.get('custom_speed_max')
    tracking_url = app.config.get('TRACKING_BASE_URL', '') or request.url_root.rstrip('/')

    campaign = ParallelWorkerCampaign(
        campaign_id,
        data['name'],
        data.get('senders', []),
        leads,
        data.get('templates', []),
        data.get('subject_lines', []),
        data.get('follow_ups', []),
        speed_mode=data.get('speed_mode', 'medium'),
        custom_min=custom_min,
        custom_max=custom_max,
        allow_resend=data.get('allow_resend', False),
        crm_campaign_id=campaign_id,
        tracking_base_url=tracking_url
    )

    campaigns[campaign_id] = campaign

    thread = threading.Thread(target=campaign.start_campaign)
    thread.daemon = False
    thread.start()

    return jsonify({
        'success': True,
        'campaign_id': campaign_id,
        'message': f"Campaign started - {len(data.get('senders', []))} workers × {campaign.leads_per_sender} leads = {campaign.total} total",
        'log_file': campaign.log_file
    })

@app.route('/api/sent-leads', methods=['GET'])
def get_sent_leads():
    sent_set = load_sent_leads()
    return jsonify({
        'total_sent': len(sent_set),
        'sent_emails': sorted(list(sent_set))
    })

@app.route('/api/sent-leads', methods=['DELETE'])
def clear_sent_leads():
    try:
        if os.path.exists(SENT_LEADS_FILE):
            os.remove(SENT_LEADS_FILE)
        return jsonify({'success': True, 'message': 'Sent leads cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email-logs', methods=['GET'])
def get_email_logs():
    logs = load_email_logs()
    return jsonify(logs)


# ---- CRM: tracking (does not change existing sending) ----
@app.route('/api/track/open/<int:emails_sent_id>', methods=['GET'])
def track_open(emails_sent_id):
    """1x1 pixel: mark email as opened. Does not affect sending."""
    if app.config.get('ENABLE_CRM'):
        try:
            print(f"[HIT] Open hit for ID: {emails_sent_id}")
            mark_opened(emails_sent_id)
            import sys
            sys.stdout.flush()
        except Exception as e:
            print(f"[HIT] Open track error: {e}")
            import sys
            sys.stdout.flush()
            pass
    # 1x1 transparent GIF
    gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return send_file(BytesIO(gif), mimetype='image/gif', as_attachment=False)


@app.route('/api/track/click/<int:emails_sent_id>', methods=['GET'])
def track_click(emails_sent_id):
    """Redirect to original URL and mark as clicked. Does not affect sending."""
    target = request.args.get('url', '')
    if app.config.get('ENABLE_CRM'):
        try:
            print(f"[HIT] Click hit for ID: {emails_sent_id} -> {target}")
            mark_clicked(emails_sent_id)
            import sys
            sys.stdout.flush()
        except Exception as e:
            print(f"[HIT] Click track error: {e}")
            import sys
            sys.stdout.flush()
            pass
    if target:
        try:
            import base64
            pad = (4 - len(target) % 4) % 4
            target = base64.urlsafe_b64decode(target + ('=' * pad)).decode('utf-8')
        except Exception:
            target = ''
    if not target or not target.startswith(('http://', 'https://')):
        target = request.url_root or '/'
    return redirect(target)


# ---- CRM: dashboard API and automated reminders ----
def run_reminder_job():
    """Find leads with no response after REMINDER_DAYS. Does not touch sending."""
    global REMINDER_ALERTS
    if not app.config.get('ENABLE_CRM'):
        return
    try:
        from crm_models import EmailsSent, Lead
        from crm_models import db
        cutoff = datetime.utcnow() - timedelta(days=app.config.get('REMINDER_DAYS', 3))
        with app.app_context():
            rows = EmailsSent.query.filter(
                EmailsSent.sent_at < cutoff,
                EmailsSent.opened_at.is_(None),
                EmailsSent.clicked_at.is_(None)
            ).all()
        alerts = []
        for r in rows:
            lead = Lead.query.get(r.lead_id) if r.lead_id else None
            alerts.append({
                'lead_id': r.lead_id,
                'campaign_id': r.campaign_id,
                'email': lead.email if lead else '',
                'sent_at': r.sent_at.isoformat() if r.sent_at else None,
            })
        REMINDER_ALERTS[:] = alerts
    except Exception as e:
        print(f"[CRM] Reminder job error: {e}", file=sys.stderr)


@app.route('/api/crm/reminders', methods=['GET'])
def get_crm_reminders():
    """Leads with no open/click after REMINDER_DAYS. Does not affect sending."""
    return jsonify({'alerts': REMINDER_ALERTS, 'count': len(REMINDER_ALERTS)})


FOLLOWUP_ALERTS = []


def run_followup_job():
    """Identify leads needing follow-up. Does not auto-send unless ENABLE_AUTO_FOLLOWUP."""
    global FOLLOWUP_ALERTS
    if not app.config.get('ENABLE_CRM'):
        return
    try:
        days = app.config.get('REMINDER_DAYS', 3)
        max_fu = app.config.get('MAX_FOLLOWUP_COUNT', 3)
        with app.app_context():
            FOLLOWUP_ALERTS[:] = get_leads_needing_followup(days, max_fu)
    except Exception as e:
        print(f"[CRM] Follow-up job error: {e}", file=sys.stderr)


@app.route('/api/crm/followup-leads', methods=['GET'])
def get_crm_followup_leads():
    """Leads pending follow-up. Does not affect sending."""
    return jsonify({
        'leads': FOLLOWUP_ALERTS,
        'count': len(FOLLOWUP_ALERTS),
        'auto_followup_enabled': app.config.get('ENABLE_AUTO_FOLLOWUP', False)
    })


@app.route('/api/crm/campaigns', methods=['GET'])
def get_crm_campaigns():
    """CRM campaign list with status. Does not replace in-memory campaigns."""
    if not app.config.get('ENABLE_CRM'):
        return jsonify({'campaigns': []})
    try:
        from crm_models import Campaign, EmailsSent
        rows = Campaign.query.order_by(Campaign.created_at.desc()).limit(200).all()
        out = []
        for c in rows:
            sent_count = EmailsSent.query.filter_by(campaign_id=c.id).count()
            out.append({
                'id': c.id,
                'name': c.name,
                'description': c.description or '',
                'status': c.status,
                'scheduled_date': c.scheduled_date.isoformat() if c.scheduled_date else None,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'emails_sent_count': sent_count,
            })
        return jsonify({'campaigns': out})
    except Exception as e:
        return jsonify({'campaigns': [], 'error': str(e)})


@app.route('/api/crm/leads', methods=['GET'])
def get_crm_leads():
    """Leads with optional filters: campaign_id, today, follow_ups, not_contacted."""
    if not app.config.get('ENABLE_CRM'):
        return jsonify({'leads': []})
    try:
        from crm_models import Lead, EmailsSent
        campaign_id = request.args.get('campaign_id')
        today = request.args.get('today') == '1'
        not_contacted = request.args.get('not_contacted') == '1'
        q = Lead.query
        if campaign_id:
            sub = EmailsSent.query.filter_by(campaign_id=campaign_id).with_entities(EmailsSent.lead_id).distinct()
            q = q.filter(Lead.id.in_(sub))
        if today:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            sub = EmailsSent.query.filter(EmailsSent.sent_at >= today_start).with_entities(EmailsSent.lead_id).distinct()
            q = q.filter(Lead.id.in_(sub))
        if not_contacted:
            from crm_models import db
            sent_ids = db.session.query(EmailsSent.lead_id).distinct().all()
            sent_ids = [x[0] for x in sent_ids]
            q = q.filter(~Lead.id.in_(sent_ids)) if sent_ids else q
        leads = q.order_by(Lead.updated_at.desc()).limit(500).all()
        out = []
        for L in leads:
            sent = EmailsSent.query.filter_by(lead_id=L.id).order_by(EmailsSent.sent_at.desc()).first()
            out.append({
                'id': L.id,
                'email': L.email,
                'name': L.name,
                'status': L.status,
                'created_at': L.created_at.isoformat() if L.created_at else None,
                'last_sent_at': sent.sent_at.isoformat() if sent and sent.sent_at else None,
                'opened_at': sent.opened_at.isoformat() if sent and sent.opened_at else None,
                'clicked_at': sent.clicked_at.isoformat() if sent and sent.clicked_at else None,
                'email_status': sent.status if sent else None,
                'error_message': sent.error_message if sent else None
            })
        return jsonify({'leads': out})
    except Exception as e:
        return jsonify({'leads': [], 'error': str(e)})


@app.route('/api/crm/stats', methods=['GET'])
def get_crm_stats():
    """Aggregate counts for dashboard. Does not change sending."""
    if not app.config.get('ENABLE_CRM'):
        return jsonify({'enabled': False})
    try:
        from crm_models import Lead, Campaign, EmailsSent
        return jsonify({
            'enabled': True,
            'leads_count': Lead.query.count(),
            'campaigns_count': Campaign.query.count(),
            'emails_sent_count': EmailsSent.query.filter_by(status='sent').count(),
            'emails_failed_count': EmailsSent.query.filter_by(status='failed').count(),
            'opens_count': EmailsSent.query.filter(EmailsSent.opened_at.isnot(None)).count(),
            'clicks_count': EmailsSent.query.filter(EmailsSent.clicked_at.isnot(None)).count(),
            'reminder_alerts_count': len(REMINDER_ALERTS),
        })
    except Exception as e:
        return jsonify({'enabled': True, 'error': str(e)})


@app.route('/crm', methods=['GET'])
def crm_dashboard_page():
    """Minimal CRM dashboard. Does not replace main email UI."""
    try:
        reminder_days = app.config.get('REMINDER_DAYS', 3)
        if reminder_days is None:
            reminder_days = 3
        return render_template('crm_dashboard.html', reminder_days=int(reminder_days))
    except Exception as e:
        print(f"[CRM] Dashboard error: {e}", file=sys.stderr)
        from flask import Response
        body = f'<html><body><h1>CRM Dashboard</h1><p>Error: {html.escape(str(e))}</p><a href="/">Back to Campaign</a></body></html>'
        return Response(body, status=500, mimetype='text/html')


if __name__ == '__main__':
    # CRM: start reminder job scheduler (does not affect daily sending)
    # Kept behind a feature flag so `/crm` can render even if DB schema is mid-migration.
    if app.config.get('ENABLE_CRM'):
        enable_scheduler = os.environ.get('ENABLE_CRM_SCHEDULER', '0').strip().lower() in ('1', 'true', 'yes')
        if enable_scheduler:
            try:
                from apscheduler.schedulers.background import BackgroundScheduler
                scheduler = BackgroundScheduler()
                scheduler.add_job(run_reminder_job, 'interval', minutes=60, id='crm_reminders')
                scheduler.add_job(run_followup_job, 'interval', minutes=60, id='crm_followups')
                scheduler.start()
                run_reminder_job()
                run_followup_job()
                print('[CRM] Scheduler started')
            except Exception as e:
                print(f"[CRM] Scheduler not started: {e}", file=sys.stderr)
        else:
            print('[CRM] Scheduler disabled (set ENABLE_CRM_SCHEDULER=1 to enable)')
    print("[SERVER] Multi-Account Email Campaign Dashboard - OPTIMIZED")
    print("[MODE] 5 Parallel Workers (true parallelism)")
    print("[WORKERS] Each worker: 1 email → wait delay → next email")
    print("[INFO] http://localhost:5000")
    if app.config.get('ENABLE_CRM'):
        print("[CRM] Dashboard: http://localhost:5000/crm")
    sys.stdout.flush()
    app.run(debug=False, port=5000, use_reloader=False)
