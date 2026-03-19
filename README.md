# 🚀 Multi-Account Email Campaign Dashboard

**Advanced email sending system with 5 sender accounts, automatic rotation, and 30 emails per account per day.**

---

## ✨ Key Features

### 🔄 Multi-Account Sender Rotation
- Add up to **5 email accounts** (different providers)
- **Automatic rotation** between accounts
- **30 emails per account per day** (configurable)
- Each sender gets dedicated set of recipients

### 📧 Multi-Provider Email Support
- ✅ Gmail
- ✅ Zoho Mail
- ✅ Outlook/Office365
- ✅ Yahoo Mail
- ✅ SendGrid

### 📝 Email Customization
- Multiple email templates
- Template rotation (every 3 emails)
- Multiple subject lines (A/B testing)
- Personalization: [Business Name], [City], [Location]

### ⏰ Follow-up Automation
- Auto-scheduled follow-ups (1, 2, 3+ days)
- Background scheduler (runs in background)
- Continues even if browser closed

### 📊 Real-Time Dashboard
- Campaign progress tracking
- Sent/failed email count
- Active sender display
- Real-time updates (3s refresh)

### 🎮 Campaign Control
- Start/Stop/Resume buttons
- Pause between account rotations
- Manual or automatic continuation

### 💾 Portable & Standalone
- Download as ZIP file
- Run on any computer
- No installation required (just Python)

---

## 🎯 Use Cases

### Case 1: Agency with Multiple Sender Identities
- 5 different team members' emails
- Same campaign message
- Appears to come from different people
- Higher deliverability

### Case 2: Scale Outreach Safely
- 100+ leads without hitting daily limits
- Distribute across 5 accounts
- 30 emails per account = 150 total
- Avoid spam filters

### Case 3: Multi-Market Campaigns
- Different sender per geographic region
- Regional email addresses
- Rotate by location
- Better local response

### Case 4: Team-Based Outreach
- 5 sales reps' email accounts
- Coordinated campaign
- Track who sent what
- Same templates/timing

---

## 📋 How It Works

### Campaign Flow

```
┌─────────────────────────────────────────────┐
│ Step 1: Add Sender Accounts                 │
│ • Account 1 (Gmail)                         │
│ • Account 2 (Zoho)                          │
│ • Account 3 (Outlook)                       │
│ • Account 4 (Yahoo)                         │
│ • Account 5 (Gmail)                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 2: Upload Leads (CSV/Excel)            │
│ • 150 leads with emails                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 3: Configure Templates & Subjects      │
│ • 2-3 email templates                       │
│ • 3-5 subject lines                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 4: Set Emails Per Day                  │
│ • Default: 30 per account                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 5: Start Campaign                      │
│ Account 1 → 30 emails → Account 2 → 30     │
│ emails → Account 3 → 30 emails →            │
│ Account 4 → 30 emails → Account 5 → 30     │
│ emails → DONE                               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 6: Follow-ups Auto-Send (Background)  │
│ Day 1: Follow-up #1 (150 emails)            │
│ Day 2: Follow-up #2 (150 emails)            │
│ Day 3: Follow-up #3 (150 emails)            │
└─────────────────────────────────────────────┘
```

### Email Sending Example (100 leads)

```
Configuration:
- 5 sender accounts
- 30 emails per account
- 100 leads total

Execution:
├─ Account 1: Sends 30 emails (leads 1-30)
│  └─ Delay: 3-8s between each email
├─ Account 2: Sends 30 emails (leads 31-60)
│  └─ Delay: 3-8s between each email
├─ Account 3: Sends 30 emails (leads 61-90)
│  └─ Delay: 3-8s between each email
└─ Account 4: Sends 10 emails (leads 91-100)
   └─ Delay: 3-8s between each email

Total: 100 emails across 4 accounts
Time: ~1-2 hours (with anti-spam delays)
```

---

## 🚀 Getting Started

### Quick Setup (5 minutes)

1. **Open Dashboard**
   ```
   http://localhost:5000
   ```

2. **Add 5 Sender Accounts**
   - Click "Sender Accounts (Add 5)" section
   - Click "+ Add Sender Account"
   - Fill: Provider, Email, App Password
   - Repeat 5 times (or less if needed)

3. **Upload Leads**
   - CSV/Excel with: Business Name, Email, Location
   - Click "Upload Leads"
   - Confirm count shows

4. **Create Templates**
   - Add email content
   - Use [Business Name], [City], [Location] placeholders
   - Add 2-3 templates for variety

5. **Add Subject Lines**
   - Add 3-5 different subjects
   - Applied round-robin to emails
   - Helps A/B testing

6. **Configure Campaign**
   - Campaign Name
   - Emails Per Day: 30 (default)
   - Optional: Add follow-ups

7. **Start Campaign**
   - Click "🚀 Send Campaign"
   - Confirm
   - Watch dashboard for progress

---

## 🔐 Getting App Passwords

### Gmail
```
1. https://myaccount.google.com/apppasswords
2. Select: Mail + Windows Computer
3. Copy: 16-character password
4. Paste: Into Email Campaign Dashboard
```

### Zoho Mail
```
1. https://mail.zoho.com
2. Settings → Security → App Passwords
3. Generate: App Password
4. Copy and paste into dashboard
```

### Outlook/Office365
```
1. account.microsoft.com → Security
2. App passwords
3. Generate: For Mail + Windows
4. Copy and paste
```

### Yahoo Mail
```
1. Yahoo Account Security
2. Generate: App password for Yahoo Mail
3. Copy and paste
```

### SendGrid
```
1. https://app.sendgrid.com/settings/api_keys
2. Create: New API Key
3. Use: "apikey" as username, key as password
```

---

## 💾 Installation

### Option 1: Run Locally (Existing Installation)

```bash
# If server already running:
http://localhost:5000

# Add accounts and start sending
```

### Option 2: Download & Run Anywhere

```bash
# 1. Download ZIP from dashboard
http://localhost:5000/download

# 2. Extract to your folder
unzip email_campaign_dashboard.zip

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py

# 5. Open
http://localhost:5000
```

### System Requirements
- Python 3.7+
- pip (package manager)
- Internet connection
- 5 valid email accounts with app passwords

---

## 📊 Dashboard Overview

### Sender Accounts Section
- Add up to 5 email accounts
- Each with provider, email, password
- Visual feedback on configuration

### Campaign Setup
- Campaign name
- Emails per account per day (1-100, default 30)
- Lead file upload
- Status: "✓ N leads loaded"

### Email Templates
- Multiple template support
- Placeholders: [Business Name], [City], [Location]
- Rotate every 3 emails
- Add/Remove templates dynamically

### Subject Lines
- A/B testing via round-robin
- Multiple subjects
- Applied per email rotation

### Follow-ups
- Schedule 1, 2, 3+ day follow-ups
- Custom subject & message per follow-up
- Auto-send in background
- Can be stopped manually

### Active Campaigns
- Real-time dashboard
- Progress percentage
- Sent/failed count
- Sender account count
- Status: pending, running, paused, completed
- Action buttons: Resume, Stop

---

## ⚙️ Configuration

### Email Per Account Per Day
- **Default**: 30
- **Range**: 1-100
- **Recommended**: 30 (safe for all providers)
- **Adjustable**: Before sending campaign

### Email Delays (Anti-Spam)
- **Between emails**: 3-8 seconds (randomized)
- **Between account switches**: 2 seconds
- **Why**: Avoid hitting SMTP rate limits

### Template Rotation
- **Default**: Every 3 emails
- **Example**: 
  - Emails 1-3: Template A
  - Emails 4-6: Template B
  - Emails 7-9: Template A (loops)

### Subject Line Distribution
- **Method**: Round-robin
- **Example**: 
  - Email 1: Subject A
  - Email 2: Subject B
  - Email 3: Subject C
  - Email 4: Subject A (loops)

---

## 🎮 Using the Dashboard

### Adding Sender Accounts
1. Click "Sender Accounts (Add 5)"
2. Click "+ Add Sender Account" button
3. Select email provider from dropdown
4. Enter email address
5. Enter app password
6. Repeat for up to 5 accounts

### Uploading Leads
1. Prepare CSV/Excel with columns:
   - Business Name
   - Email
   - Location (optional)
2. Click "Choose File" or drag-drop
3. System validates and shows count
4. Status: "✓ 150 leads loaded"

### Creating Templates
1. Click "Templates" section
2. See default template
3. Click "+ Add Template" for more
4. Edit template content
5. Use [placeholders] for personalization
6. Remove template with ❌ button

### Setting Subject Lines
1. Click "Subject Lines" section
2. Edit existing or add new
3. Each row = one subject
4. Applied round-robin to emails
5. Add with "+ Add Subject Line"
6. Remove with ❌ button

### Adding Follow-ups
1. Click "Follow-up Sequences"
2. Configure each follow-up:
   - Days After (when to send)
   - Subject Line
   - Message template
3. Add more with "+ Add Follow-up"
4. All follow-ups schedule automatically

### Starting Campaign
1. Fill all required fields
2. Click "🚀 Send Campaign"
3. Confirm popup (shows lead count)
4. Campaign starts automatically
5. Watch dashboard for progress

### Monitoring Progress
1. Dashboard auto-refreshes every 3 seconds
2. See real-time sent/failed counts
3. View progress percentage
4. Click campaign for detailed results
5. See which sender is active

### Pausing/Resuming
1. After batch complete, click "▶️ Resume"
2. Campaign continues with next account
3. Click "⏹️ Stop" to stop campaign
4. Click "🔄 Restart" to resume stopped campaign

---

## 📈 Performance & Limits

### Safe Daily Limits by Provider
- **Gmail**: 30-50 emails per account per day
- **Zoho**: No daily limit (be respectful)
- **Outlook**: 30-50 emails per account per day
- **Yahoo**: 100 emails per account per day
- **SendGrid**: Per your plan

### Total Campaign Capacity (Example)
- 5 accounts × 30 emails each = **150 emails total per day**
- 5 accounts × 50 emails each = **250 emails total per day** (risky)

### Recommended Settings
- **Emails per account**: 30 (default)
- **Email delay**: 3-8 seconds (default)
- **Template variation**: 2-3 templates
- **Subject variation**: 3-5 subjects

---

## 🔍 Troubleshooting

### Authentication Failed
- Verify email address is correct
- Use APP PASSWORD (not regular password)
- Check provider settings for new app password
- Try account individually first

### Campaign Won't Start
- Check at least 1 sender added
- Check leads uploaded
- Check 1 template exists
- Verify 1 subject line added

### Slow Sending
- Intentional: 3-8 second delays prevent spam
- Edit app.py if faster needed
- Search: `random.uniform(3, 8)`

### Follow-ups Not Sending
- Keep Python window open
- Check scheduled time hasn't passed yet
- Wait for scheduler (checks every 60s)
- Look at campaign results for details

### Memory Issues
- Campaign data stored in RAM
- Large campaigns may use memory
- Restart server if needed
- Download results before stopping

---

## 📞 Support & Help

### Common Tasks

**Send 150 emails from 5 accounts**
- Add 5 accounts
- Upload 150 leads
- Set 30 per account
- Result: 30+30+30+30+30 = 150

**Send 500 emails (multi-day)**
- Add 3-5 accounts
- Upload 500 leads
- Set 30 per account
- Run multiple campaigns or adjust

**Test Before Full Campaign**
- Add 1 account
- Upload 5 test leads
- Run test campaign
- Review results before scaling

**Add Follow-ups**
- Configure initial campaign
- Add 3 follow-ups (1, 2, 3 days)
- System auto-sends at scheduled time
- Can stop anytime

---

## 🎁 What's Included

✅ Multi-account support (up to 5)  
✅ 30 emails per account per day  
✅ Automatic sender rotation  
✅ 5 email providers (SMTP)  
✅ Multiple templates  
✅ A/B subject testing  
✅ Follow-up scheduler  
✅ Real-time dashboard  
✅ Campaign control buttons  
✅ Results tracking  
✅ ZIP download export  
✅ Portable standalone version  

---

## 📝 License & Disclaimer

- For personal/business use
- Respect email provider terms
- Follow anti-spam laws (CAN-SPAM, GDPR)
- Always include unsubscribe option in real campaigns
- Test before sending large campaigns

---

## 🚀 Ready to Start?

1. Go to **http://localhost:5000**
2. Add your 5 sender accounts
3. Upload leads
4. Configure templates
5. Start campaign
6. Watch dashboard

**Questions?** Check QUICK_START.md for step-by-step guide.

---

*Multi-Account Email Campaign Dashboard - Production Ready*  
*Version: 2.0 (Multi-Sender)*  
*Last Updated: Current Session*
