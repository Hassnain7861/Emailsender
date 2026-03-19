# DEVELOPER PROMPT - BUILD MULTI-ACCOUNT EMAIL CAMPAIGN SYSTEM FROM SCRATCH

## SYSTEM REQUIREMENTS

Build a complete Flask-based email campaign management system with the following specifications:

### Core Functionality
- **5 Parallel Email Sender Accounts**: Support simultaneous sending from 5 different email accounts
- **30 Emails Per Account**: Each account sends 30 emails (configurable 1-100) to different leads
- **Different Lead Distribution**: Divide leads equally among 5 accounts with NO overlap
- **Random 25-45 Second Delays**: Between each email (not fixed, truly randomized)
- **Template Management**: Multiple email templates with auto-rotation every 3 emails
- **Subject Line A/B Testing**: Round-robin distribution of subject lines
- **Personalization**: Replace placeholders [Business Name], [City], [Location] in templates
- **Follow-up Automation**: Schedule automatic follow-ups 1, 2, 3+ days after initial send
- **Real-Time Dashboard**: Display live campaign progress (refresh every 3 seconds)
- **Campaign Control**: Start, Stop, Resume, Pause functionality

### Email Provider Support
Implement SMTP support for:
- Gmail (smtp.gmail.com:587)
- Zoho Mail (smtp.zoho.com:587)
- Outlook/Office365 (smtp.office365.com:587)
- Yahoo Mail (smtp.mail.yahoo.com:587)
- SendGrid (smtp.sendgrid.net:587)

### Architecture Requirements
- **Backend**: Flask (Python 3.7+)
- **Frontend**: HTML5 + CSS3 + JavaScript (no jQuery/React/Vue)
- **Threading**: Python threading for parallel execution (5 threads)
- **Data Storage**: In-memory (no database required)
- **File Upload**: CSV and Excel (.xlsx/.xls) support
- **Deployment**: Docker-ready with docker-compose

---

## USER INTERFACE REQUIREMENTS

### Main Dashboard Page
Display:
1. **Sender Accounts Section**: Add/manage up to 5 email accounts with provider selection, email, password
2. **Campaign Setup Section**: Campaign name, emails per account, lead file upload
3. **Email Templates Section**: Create/edit multiple templates with placeholders
4. **Subject Lines Section**: Add multiple subject lines for round-robin distribution
5. **Follow-up Configuration Section**: Schedule follow-ups with days, subject, message
6. **Active Campaigns Dashboard**: Show live stats (sent/failed/total), progress bar, campaign list
7. **Results Table**: Display email sending results with sender, recipient, subject, status, timestamp

### Features
- Real-time updates (AJAX polling every 3 seconds)
- Progress percentage display
- Per-account tracking (show progress for each of 5 accounts)
- Download entire system as ZIP
- Responsive design (works on desktop/mobile)

---

## BACKEND API REQUIREMENTS

### Endpoints to Implement

**GET /**: Return dashboard HTML page

**POST /api/upload-leads**:
- Accept CSV or Excel file
- Auto-detect columns: Business Name, Email, Location
- Return: {success: true, lead_count: N, leads: [...]}

**POST /api/send-campaign**:
- Input: {name, senders: [{email, password, provider}], leads: [...], templates, subject_lines, follow_ups, emails_per_account}
- Create unique campaign ID with timestamp
- Start parallel threads (one per sender)
- Return: {success: true, campaign_id, message}

**GET /api/campaigns**:
- Return all campaigns with status, sent count, failed count, total leads

**GET /api/campaigns/<id>**:
- Return detailed campaign info including results

**POST /api/campaigns/<id>/stop**:
- Stop running campaign

**POST /api/campaigns/<id>/resume**:
- Resume paused/stopped campaign

**GET /download**:
- Return entire system as ZIP file (app.py, index.html, requirements.txt, README.txt)

---

## EMAIL SENDING LOGIC

### Campaign Execution Flow
1. Accept 5 sender accounts + leads + templates + subjects + follow-ups
2. Divide leads equally among 5 accounts (NO overlap)
3. Create 5 threads (one per sender account)
4. Each thread:
   - Connect to SMTP server
   - For each assigned lead:
     - Get subject line (round-robin from list)
     - Get template (rotate every 3 emails)
     - Personalize template (replace placeholders)
     - Send email via SMTP
     - Record success/failure
     - Wait random 25-45 seconds
   - Close connection
5. After all threads complete, schedule follow-ups if enabled
6. Background scheduler checks every 60 seconds for due follow-ups

### Error Handling
- Gracefully handle authentication errors
- Continue on individual email failures (don't stop entire account)
- Retry with different templates on timeout
- Record all failures with reasons

---

## LEAD DISTRIBUTION EXAMPLE

**Input**: 150 leads, 5 accounts, 30 emails/account

**Distribution**:
- Account 1: Leads[0:30] = 30 emails
- Account 2: Leads[30:60] = 30 emails
- Account 3: Leads[60:90] = 30 emails
- Account 4: Leads[90:120] = 30 emails
- Account 5: Leads[120:150] = 30 emails

**Result**: NO OVERLAP - Each lead gets exactly ONE email

---

## DELAY LOGIC

Between each email from same account:
```
delay = random(25, 45)  // Generate random float between 25-45 seconds
wait(delay)
```

Examples: 30.5s, 35.2s, 42.1s, 25.8s, 38.9s (each different)

---

## TEMPLATE PERSONALIZATION

**Original**:
```
Hey [Business Name],

I noticed your business in [City].

You're missing rankings in [Location].

Interested?
```

**After Personalization**:
```
Hey Acme Corp,

I noticed your business in New York.

You're missing rankings in New York, NY.

Interested?
```

---

## SUBJECT LINE DISTRIBUTION

Use round-robin (cycle through list):
- Email 1 → Subject A
- Email 2 → Subject B
- Email 3 → Subject C
- Email 4 → Subject A (cycles back)
- Email 5 → Subject B

---

## TEMPLATE ROTATION

Rotate template every 3 emails:
- Emails 1-3 → Template A
- Emails 4-6 → Template B
- Emails 7-9 → Template C
- Emails 10-12 → Template A (cycles back)

---

## FOLLOW-UP SCHEDULER

Background process that:
1. Runs every 60 seconds
2. Checks all scheduled follow-ups
3. If current_time >= scheduled_time and status == pending:
   - Send follow-up email
   - Mark status as sent
4. Continue running even if browser is closed (as long as Python process runs)

---

## DEPENDENCIES

```
Flask==2.3.0
python-dotenv==1.0.0
openpyxl==3.10.0
```

---

## DEPLOYMENT REQUIREMENTS

### Docker Support
- Create Dockerfile that runs on Python 3.9-slim
- Create docker-compose.yml for easy local deployment
- Support volume mounts for uploads folder
- Expose port 5000

### Local Development
- python app.py should start Flask dev server
- Should be accessible at http://localhost:5000
- Should reload on code changes (debug mode)

---

## EXPECTED OUTPUT

After completion, system should:
1. Accept 5 email accounts with different providers
2. Accept CSV/Excel file with leads
3. Create multiple templates and subject lines
4. Send 150 emails simultaneously from 5 accounts (30 each)
5. Each email has 25-45 second random delay
6. Dashboard shows real-time progress
7. Follow-ups auto-send at scheduled times
8. Can download entire system as standalone ZIP
9. 100% success rate with valid credentials
10. Complete in 30-45 minutes for 150 leads

---

## TESTING REQUIREMENTS

Test with:
- 5 test accounts (can be dummy/simulated)
- 25 random-generated leads
- 3 email templates
- 3 subject lines
- 2 follow-ups
- Verify: All accounts send simultaneously, different leads per account, random delays work, follow-ups schedule correctly

---

## FILE STRUCTURE TO Create

```
email-campaign-system/
├── app.py                              # Flask backend
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker build
├── docker-compose.yml                  # Docker compose
├── .dockerignore                       # Docker ignore
├── .gitignore                          # Git ignore
├── templates/
│   └── index.html                      # Dashboard UI
└── uploads/                            # Auto-created (file storage)
```

---

## SPECIFIC CODE REQUIREMENTS

### Main Campaign Class
```
class ParallelMultiAccountCampaign:
    - __init__(campaign_id, name, senders, leads, templates, subject_lines, follow_ups, emails_per_account)
    - send_for_sender(sender_idx)  # Send from one account
    - send_email(lead, template, subject, server, sender_email)  # Send single email
    - personalize_template(template_text, business_name, location)  # Replace placeholders
    - send_batch()  # Coordinate all 5 senders in parallel
    - schedule_followups()  # Schedule follow-up emails
    - send_scheduled_followups()  # Check and send due follow-ups
    - stop_campaign()  # Stop running campaign
```

### Frontend Requirements
- No external frameworks (vanilla JavaScript only)
- AJAX calls to backend API
- Real-time progress updates
- Form validation
- File upload with drag-drop
- Responsive grid layout

---

## PERFORMANCE TARGETS

- 5 accounts sending simultaneously
- 30 emails per account = 150 total emails
- Execution time: 30-45 minutes (due to random delays)
- Memory: 50-100 MB
- CPU: 5-10%
- Success rate: 100% (with valid credentials)

---

## SECURITY NOTES

- No authentication required (local development)
- Passwords stored in browser session only
- Not saved to server/database
- HTTPS not required (local deployment)

---

## ADDITIONAL REQUIREMENTS

1. **ZIP Download**: Include app.py, index.html, requirements.txt, README.txt
2. **CSV/Excel Support**: Auto-detect columns for Business Name, Email, Location
3. **Multiple Providers**: Support 5 major email providers
4. **Batch Control**: Can start/stop/resume campaigns
5. **Real-time Monitoring**: Dashboard updates live
6. **Background Scheduler**: Follow-ups continue even if browser closed

---

## SUCCESS CRITERIA

The system is complete when:
1. ✅ 5 sender accounts can be added and managed
2. ✅ Leads can be uploaded from CSV/Excel
3. ✅ Multiple templates and subject lines supported
4. ✅ All 5 accounts send simultaneously (parallel threads)
5. ✅ Each account sends to DIFFERENT leads (no overlap)
6. ✅ Random 25-45 second delays work correctly
7. ✅ Follow-ups schedule and auto-send
8. ✅ Dashboard displays real-time progress
9. ✅ System can be downloaded as ZIP
10. ✅ Docker build works (docker-compose up --build)
11. ✅ Tested with 100% success rate
12. ✅ All 4 documentation files complete

---

## DELIVERABLES

1. **app.py** - Complete Flask backend (23 KB)
2. **templates/index.html** - Complete dashboard UI (28 KB)
3. **requirements.txt** - Dependencies (3 packages)
4. **Dockerfile** - Docker build configuration
5. **docker-compose.yml** - Docker compose configuration
6. **README.md** - Setup and usage instructions
7. **DOCUMENTATION.md** - Complete system documentation

---

## BUILD TIME ESTIMATE

- Flask backend: 2-3 hours
- Frontend dashboard: 2-3 hours
- Email logic: 1-2 hours
- Testing & debugging: 1-2 hours
- Documentation: 1 hour
- **Total: 7-11 hours**

---

## NOTES

- Use Python threading (built-in, no external async library)
- Use SMTP protocol directly (built-in smtplib)
- No database (all in-memory)
- Keep frontend simple (no npm/build process)
- Make it portable (single Python file executable)
- Production-ready code with error handling

---

END OF PROMPT

**Give this prompt to any developer and they can build the complete system from scratch.**
