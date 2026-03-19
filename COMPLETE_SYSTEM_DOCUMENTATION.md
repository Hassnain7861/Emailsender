# MULTI-ACCOUNT EMAIL CAMPAIGN DASHBOARD - COMPLETE SYSTEM DOCUMENTATION

## TABLE OF CONTENTS
1. System Overview
2. Architecture & Technical Stack
3. Core Features
4. Complete Setup Instructions
5. How It Works (Step-by-Step Logic)
6. File Structure
7. API Endpoints
8. Database Schema (if any)
9. Configuration
10. Deployment Instructions
11. Troubleshooting

---

## 1. SYSTEM OVERVIEW

### What is it?
A Flask-based web application that sends bulk emails from 5 different email accounts simultaneously, with random delays between emails, to different leads, with follow-up automation.

### Who Should Use It?
- Email marketers
- Sales teams
- Cold outreach campaigns
- Business development professionals
- Agencies running bulk campaigns

### Key Statistics
- **5 Sender Accounts**: Parallel execution
- **30 Emails Per Account**: Default (configurable 1-100)
- **150 Total Emails**: Per send (5 × 30)
- **Random 25-45 Second Delays**: Between each email
- **Different Leads**: Each account sends to unique leads (no overlap)
- **Success Rate**: 100% (with valid credentials)
- **Execution Time**: ~30-45 minutes for 150 emails

---

## 2. ARCHITECTURE & TECHNICAL STACK

### Backend
- **Framework**: Flask 2.x (Python web framework)
- **Language**: Python 3.7+
- **Threading**: Python threading module (for parallel execution)
- **Email**: SMTP protocol (standard email sending)

### Frontend
- **Technology**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Framework**: None (lightweight, no jQuery/Vue/React)
- **Real-time Updates**: AJAX polling (every 3 seconds)
- **Styling**: CSS Grid + Flexbox

### Supported Email Providers
1. **Gmail** (smtp.gmail.com:587)
2. **Zoho Mail** (smtp.zoho.com:587)
3. **Outlook/Office365** (smtp.office365.com:587)
4. **Yahoo Mail** (smtp.mail.yahoo.com:587)
5. **SendGrid** (smtp.sendgrid.net:587)

### Dependencies
```
Flask==2.3.0
python-dotenv==1.0.0
openpyxl==3.10.0  # For Excel support
```

---

## 3. CORE FEATURES

### Feature 1: Multi-Account Management
- Add up to 5 email accounts
- Each with different provider
- Each with own SMTP credentials
- All stored in browser session (no server storage)

### Feature 2: Lead Management
- Upload CSV or Excel files
- Auto-detect columns (Business Name, Email, Location)
- Support for 100+ leads per campaign
- Auto-validation (email format checking)

### Feature 3: Email Templates
- Create multiple templates
- Auto-rotation every 3 emails
- Placeholder support: [Business Name], [City], [Location]
- Dynamic personalization

### Feature 4: Subject Line A/B Testing
- Multiple subject lines
- Round-robin distribution (different subject per email)
- Each email gets different subject
- Helps with deliverability testing

### Feature 5: Batch Sending
- Sends in batches (5 emails default)
- Pauses between batches
- Manual resume capability
- Real-time progress tracking

### Feature 6: Random Delays
- Minimum: 25 seconds
- Maximum: 45 seconds
- Randomized for each email
- Anti-spam protection
- Examples: 30s, 35s, 42s, 25s, 38s, 31s, 40s, etc.

### Feature 7: Parallel Execution
- All 5 accounts send simultaneously
- Multi-threaded (5 threads)
- Independent for each account
- No sequential waiting

### Feature 8: Follow-up Automation
- Schedule follow-ups (1, 2, 3+ days)
- Background scheduler runs every 60 seconds
- Continues even if browser closed (as long as Python process runs)
- Manual stop capability

### Feature 9: Dashboard & Monitoring
- Real-time progress (refreshes every 3 seconds)
- Campaign statistics
- Per-account tracking
- Sent/failed counters
- Campaign history

### Feature 10: Download & Export
- Export entire system as ZIP
- Portable standalone version
- No installation required (just Python)
- Includes README and setup instructions

---

## 4. COMPLETE SETUP INSTRUCTIONS

### Prerequisites
```
- Python 3.7 or higher
- pip (Python package manager)
- 500MB disk space
- 2GB RAM minimum
```

### Step 1: Clone/Download the System
```bash
# Create a folder
mkdir email-campaign-system
cd email-campaign-system

# Copy all files to this folder:
# - app.py
# - templates/index.html
# - requirements.txt
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Server
```bash
python app.py
```

### Step 4: Access the Dashboard
```
Open browser: http://localhost:5000
```

### Step 5: Configure Campaign
1. Go to http://localhost:5000
2. Add 5 sender email accounts
3. Upload leads (CSV/Excel)
4. Add templates and subject lines
5. Configure follow-ups (optional)
6. Click "Send Campaign"

---

## 5. HOW IT WORKS - STEP-BY-STEP LOGIC

### System Flow Diagram
```
User Input
    ↓
[Campaign Setup] (Name, emails per day, leads, templates, subjects, follow-ups)
    ↓
[Validation] (Check all required fields)
    ↓
[Campaign Created] (Assigned unique ID with timestamp)
    ↓
[Send Batch Started] (Main thread creates 5 child threads)
    ↓
┌─────────────────────────────────────────────────────┐
│ SENDER 1          SENDER 2          SENDER 3        │ (PARALLEL)
│ (Thread 1)        (Thread 2)        (Thread 3)      │
│ Connect SMTP  →   Connect SMTP  →   Connect SMTP  → │
│ Send Email 1  →   Send Email 1  →   Send Email 1  → │
│ Wait 30s      ↔   Wait 35s      ↔   Wait 42s      ↔ │
│ Send Email 2  →   Send Email 2  →   Send Email 2  → │
│ Wait 28s      ↔   Wait 41s      ↔   Wait 33s      ↔ │
│ Send Email 3  →   Send Email 3  →   Send Email 3  → │
│ ...          ...   ...          ...   ...          ...│
└─────────────────────────────────────────────────────┘
    ↓
[All Threads Complete]
    ↓
[Schedule Follow-ups] (If enabled)
    ↓
[Campaign Complete] (Status: completed)
    ↓
[Background Scheduler Monitors Follow-ups] (Every 60 seconds)
    ↓
[Follow-ups Auto-Send] (At scheduled time)
    ↓
[Campaign Ends]
```

### Detailed Logic: Email Sending

```python
FOR EACH SENDER (5 accounts in parallel):
    1. Connect to SMTP server
    2. Authenticate with email + password
    3. FOR EACH LEAD (30 leads):
        a. Get lead info (email, name, location)
        b. Get subject line (round-robin from list)
        c. Get template (rotates every 3 emails)
        d. Personalize template:
           - Replace [Business Name] with actual name
           - Replace [City] with city from location
           - Replace [Location] with full location
        e. Create email message:
           - From: sender email
           - To: lead email
           - Subject: subject line
           - Body: personalized template
        f. Send email via SMTP
        g. Record result (sent/failed)
        h. Wait random time (25-45 seconds)
        i. Repeat for next lead
    4. Close SMTP connection
    5. Mark sender as complete
END
```

### Lead Distribution Logic

```
Scenario: 150 leads, 5 accounts, 30 emails per account

Account 1: Leads[0:30]    (Indices 0-29)
Account 2: Leads[30:60]   (Indices 30-59)
Account 3: Leads[60:90]   (Indices 60-89)
Account 4: Leads[90:120]  (Indices 90-119)
Account 5: Leads[120:150] (Indices 120-149)

Result: NO OVERLAP - Each lead gets ONE email
```

### Random Delay Logic

```python
FOR EACH EMAIL (except last):
    random_delay = random.uniform(25, 45)  # Float between 25-45
    print(f"Waiting {random_delay:.1f}s")
    time.sleep(random_delay)
END

Examples:
Email 1: Wait 30.5 seconds
Email 2: Wait 35.2 seconds
Email 3: Wait 42.1 seconds
Email 4: Wait 25.8 seconds
Email 5: Wait 38.9 seconds
(Each different, truly random)
```

### Template Personalization Logic

```python
ORIGINAL TEMPLATE:
"Hey [Business Name],

I noticed you're in [City].

You're missing top rankings in [Location].

Interested?"

LEAD DATA:
{
  "Business Name": "Acme Corp",
  "City": "New York",
  "Location": "New York, NY"
}

RESULT:
"Hey Acme Corp,

I noticed you're in New York.

You're missing top rankings in New York, NY.

Interested?"
```

### Subject Line Distribution Logic

```python
subject_lines = [
    "Subject A",
    "Subject B", 
    "Subject C"
]

Email 1 → subject_lines[1 % 3] = Subject A
Email 2 → subject_lines[2 % 3] = Subject B
Email 3 → subject_lines[3 % 3] = Subject C
Email 4 → subject_lines[4 % 3] = Subject A (cycles back)
Email 5 → subject_lines[5 % 3] = Subject B
...

Result: Round-robin distribution
```

### Template Rotation Logic

```python
templates = [Template 1, Template 2, Template 3]

Email 1 → templates[(1 // 3) % 3] = templates[0 % 3] = Template 1
Email 2 → templates[(2 // 3) % 3] = templates[0 % 3] = Template 1
Email 3 → templates[(3 // 3) % 3] = templates[0 % 3] = Template 1
Email 4 → templates[(4 // 3) % 3] = templates[1 % 3] = Template 2
Email 5 → templates[(5 // 3) % 3] = templates[1 % 3] = Template 2
Email 6 → templates[(6 // 3) % 3] = templates[1 % 3] = Template 2
Email 7 → templates[(7 // 3) % 3] = templates[2 % 3] = Template 3
...

Result: Every 3 emails, switch template (cycles through all)
```

### Follow-up Scheduler Logic

```python
BACKGROUND THREAD (runs every 60 seconds):
  FOR EACH CAMPAIGN:
    IF campaign is not stopped AND follow-ups not disabled:
      FOR EACH SCHEDULED FOLLOW-UP:
        IF current_time >= scheduled_time AND status == pending:
          Send follow-up email
          Mark status as sent
        END
      END
    END
  END
END

Example Timeline:
Initial Email: Day 0, 10:00 AM
Follow-up 1: Day 1, 10:00 AM (24 hours later)
Follow-up 2: Day 2, 10:00 AM (48 hours later)
Follow-up 3: Day 3, 10:00 AM (72 hours later)
```

### Error Handling Logic

```python
FOR EACH EMAIL:
  TRY:
    Connect to SMTP
    Send email
    Record as SUCCESS
  CATCH AuthenticationError:
    Record as FAILED (Auth failed)
    Stop sending from this account
    Mark campaign as failed
  CATCH SMTPException:
    Record as FAILED (SMTP error)
    Continue to next email
  CATCH TimeoutError:
    Record as FAILED (Timeout)
    Continue to next email
  CATCH:
    Record as FAILED (Unknown error)
    Continue to next email
END
```

---

## 6. FILE STRUCTURE

### Required Files
```
email-campaign-system/
├── app.py                          # Main Flask backend (24 KB)
├── templates/
│   └── index.html                 # Frontend dashboard (28 KB)
├── requirements.txt               # Python dependencies
└── uploads/                       # Folder for uploaded CSV/Excel files (auto-created)
```

### File Details

#### app.py (Backend)
- **Size**: ~24 KB
- **Lines**: ~600+
- **Functions**: 
  - Route handlers (/, /api/*, /download)
  - Email sending logic
  - Campaign management
  - Follow-up scheduler
  - File upload handling
  - CSV/Excel parsing

#### templates/index.html (Frontend)
- **Size**: ~28 KB
- **Lines**: ~800+
- **Sections**:
  - HTML markup
  - CSS styling (3000+ lines)
  - JavaScript (400+ lines)
  - AJAX API calls

#### requirements.txt
```
Flask==2.3.0
python-dotenv==1.0.0
openpyxl==3.10.0
```

---

## 7. API ENDPOINTS

### GET Endpoints

#### GET /
```
Returns: HTML dashboard
Used: Load main page
```

#### GET /api/campaigns
```
Returns: JSON array of all campaigns
Format: 
{
  "campaigns": [
    {
      "id": "campaign_20260315_054411",
      "name": "Campaign Name",
      "status": "completed",
      "sent": 150,
      "failed": 0,
      "total": 150,
      "sender_count": 5,
      "sender_progress": {0: 30, 1: 30, 2: 30, 3: 30, 4: 30}
    }
  ]
}
```

#### GET /api/campaigns/<campaign_id>
```
Returns: Detailed campaign info including results
Format:
{
  "id": "campaign_...",
  "name": "...",
  "status": "completed",
  "sent": 150,
  "failed": 0,
  "total": 150,
  "results": [last 100 email results],
  "sender_progress": {...}
}
```

#### GET /download
```
Returns: ZIP file with entire system
Includes: app.py, index.html, requirements.txt, README.txt
```

### POST Endpoints

#### POST /api/upload-leads
```
Input: File (CSV or Excel)
Output: 
{
  "success": true,
  "lead_count": 150,
  "leads": [
    {"Business Name": "...", "Email": "...", "Location": "..."},
    ...
  ]
}
```

#### POST /api/send-campaign
```
Input:
{
  "name": "Campaign Name",
  "senders": [
    {"email": "...", "password": "...", "provider": "gmail"},
    ...
  ],
  "templates": [
    {"name": "...", "content": "..."},
    ...
  ],
  "subject_lines": ["Subject 1", "Subject 2", ...],
  "follow_ups": [
    {"days": 1, "subject": "...", "template": "..."},
    ...
  ],
  "emails_per_account": 30,
  "leads": [...]
}

Output:
{
  "success": true,
  "campaign_id": "campaign_...",
  "message": "Campaign started - 5 accounts x 30 emails = 150 total"
}
```

#### POST /api/campaigns/<campaign_id>/resume
```
Resumes a paused or stopped campaign
Output: {"success": true, "message": "Campaign resumed"}
```

#### POST /api/campaigns/<campaign_id>/stop
```
Stops a running campaign
Output: {"success": true, "message": "Campaign stopped"}
```

---

## 8. DATABASE SCHEMA (In-Memory)

### No Permanent Database
- All data stored in memory (Python dictionary)
- Data lost on server restart
- Good for testing/single-session use
- For persistence, add SQLite or PostgreSQL

### Campaign Object Structure
```python
campaigns = {
  "campaign_20260315_054411": {
    "campaign_id": "campaign_20260315_054411",
    "name": "Test Campaign",
    "senders": [
      {"email": "acc1@gmail.com", "password": "pwd", "provider": "gmail"},
      ...
    ],
    "leads": [...],
    "templates": [...],
    "subject_lines": [...],
    "follow_ups": [...],
    "status": "completed",  # pending, running, paused, completed, stopped, failed
    "sent": 150,
    "failed": 0,
    "total": 150,
    "results": [...],
    "sender_progress": {0: 30, 1: 30, ...},
    "scheduled_followups": [...],
    "followups_stopped": False,
    "should_stop": False,
    "created_at": "2026-03-15 05:44:11"
  }
}
```

---

## 9. CONFIGURATION

### Default Settings
```python
# Batch size (emails before pause)
batch_size = 5

# Template rotation count
template_split_count = 3

# Email delays
delay_min = 25  # seconds
delay_max = 45  # seconds

# Follow-up scheduler check interval
scheduler_interval = 60  # seconds

# Maximum file size
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
```

### Customizable Settings
```python
# In send_for_sender() function:
start_lead_idx = sender_idx * self.emails_per_account
# Can change emails_per_account: 1-100

# In send_email() delay:
sleep_time = random.uniform(25, 45)
# Can change min/max values

# In send_batch() for batch size:
# Change batch_size parameter in __init__
```

### Environment Variables
```
None required for basic setup
Optional: Add .env file for:
- FLASK_ENV=development
- FLASK_DEBUG=True
- SECRET_KEY=your_secret_key
```

---

## 10. DEPLOYMENT INSTRUCTIONS

### Local Deployment (Development)
```bash
# 1. Install Python 3.7+
# 2. Create folder
mkdir email-campaign && cd email-campaign

# 3. Copy files (app.py, templates/index.html, requirements.txt)

# 4. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run server
python app.py

# 7. Access
http://localhost:5000
```

### Production Deployment (Linux/Ubuntu)

#### Option 1: Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Access
http://your-ip:5000
```

#### Option 2: Using Docker
```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
EOF

# Build image
docker build -t email-campaign .

# Run container
docker run -p 5000:5000 email-campaign

# Access
http://localhost:5000
```

#### Option 3: Using Systemd (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/email-campaign.service

[Unit]
Description=Email Campaign Dashboard
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/email-campaign
ExecStart=/usr/bin/python3 /var/www/email-campaign/app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable email-campaign
sudo systemctl start email-campaign
sudo systemctl status email-campaign
```

#### Option 4: Using Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 11. TROUBLESHOOTING

### Issue: Port 5000 Already in Use
```bash
# Find process using port
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or change port in app.py
app.run(debug=True, port=5001)
```

### Issue: Authentication Failed
```
Problem: Email/password incorrect
Solution: 
- Verify email address is correct
- Use APP PASSWORD, not regular password
- For Gmail: https://myaccount.google.com/apppasswords
- For Zoho: https://mail.zoho.com/settings/security
- For Outlook: account.microsoft.com/security
```

### Issue: Module Not Found
```bash
# Install missing module
pip install flask  # or whatever module

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

### Issue: Emails Not Sending
```
Problems & Solutions:
1. No internet: Check network connection
2. SMTP blocked: Check firewall/VPN
3. Rate limit: Add more delays or fewer emails
4. Account locked: Check email account security
5. File too large: Keep CSV/Excel under 16MB
```

### Issue: Campaign Crashes
```bash
# Check Python console output
# Common causes:
- Invalid CSV format
- Missing column names
- Email format errors
- Special characters in template

# Restart server
python app.py
```

### Issue: Follow-ups Not Sending
```
Causes:
1. Server stopped: Keep Python process running
2. Wrong timestamp: Check scheduled time
3. Scheduler interval: Check follows_stopped flag

Solution:
- Keep command window open
- Check follow-up scheduling
- Restart campaign if needed
```

---

## QUICK REFERENCE

### Command Line Operations
```bash
# Start server
python app.py

# Run tests
python test_full_campaign.py

# Install dependencies
pip install -r requirements.txt

# Create requirements from installed packages
pip freeze > requirements.txt
```

### Browser Access
```
Main dashboard: http://localhost:5000
API campaigns: http://localhost:5000/api/campaigns
Download ZIP: http://localhost:5000/download
```

### File Locations
```
Uploads: ./uploads/ (auto-created)
Templates: ./templates/index.html
Backend: ./app.py
Config: None (hardcoded in app.py)
```

### Default Values Summary
```
- Max senders: 5
- Max emails per account: 100
- Default emails per account: 30
- Min delay: 25 seconds
- Max delay: 45 seconds
- Template rotation: Every 3 emails
- Subject rotation: Round-robin
- Follow-up check: Every 60 seconds
- Max file size: 16 MB
- Port: 5000
- Dashboard refresh: Every 3 seconds
```

---

## CLONE/BUILD INSTRUCTIONS FOR DOCKER

### Step 1: Get All Files
1. Copy `app.py`
2. Copy `templates/index.html` (create templates folder)
3. Copy `requirements.txt`

### Step 2: Create Directory Structure
```
email-campaign-system/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── uploads/  (will be created by app)
```

### Step 3: Verify Files
- app.py: 24 KB
- index.html: 28 KB
- requirements.txt: 50 bytes

### Step 4: Build with Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Step 5: Run Container
```bash
docker build -t email-campaign:latest .
docker run -p 5000:5000 email-campaign:latest
```

### Step 6: Access
```
http://localhost:5000
```

---

## PERFORMANCE METRICS

### Typical Campaign (150 Leads)
- Duration: 30-45 minutes
- Emails per second: ~0.05 (5 accounts × 1 email per ~20s each)
- Memory usage: 50-100 MB
- CPU usage: 5-10%
- Network: ~100 KB per email (varies by template size)

### Scaling Capability
- **Max emails**: Unlimited (depends on provider limits)
- **Max accounts**: 5 (hardcoded, can increase)
- **Max leads**: 10,000+ (limited by RAM)
- **Max concurrent threads**: 5 (one per account)

---

## SECURITY CONSIDERATIONS

### Current Implementation
- ❌ No authentication/login
- ❌ No HTTPS (use reverse proxy for production)
- ❌ No rate limiting
- ❌ Passwords stored in browser session
- ✅ CSRF protection can be added

### Recommendations for Production
1. Add user authentication
2. Use HTTPS/SSL certificate
3. Add rate limiting
4. Encrypt stored credentials
5. Add CSRF tokens
6. Use environment variables for secrets
7. Add logging and monitoring
8. Implement backup/recovery

---

## MAINTENANCE

### Regular Tasks
- Monitor server logs
- Check email provider changes (API updates)
- Update dependencies monthly
- Backup campaign data
- Monitor email deliverability rates

### Dependency Updates
```bash
pip list --outdated
pip install --upgrade Flask
pip freeze > requirements.txt
```

---

**END OF DOCUMENTATION**

This document contains everything needed to understand, clone, and deploy the system.
