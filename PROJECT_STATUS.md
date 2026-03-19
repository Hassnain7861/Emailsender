# Email Campaign Dashboard - Multi-Account Edition

## ✅ COMPLETED - NEW FEATURES ADDED

### Major Update: 5 Sender Accounts + 30 Emails Per Day

**What Changed:**
- ✅ Added support for **5 sender email accounts**
- ✅ Automatic **account rotation** (cycles through senders)
- ✅ **30 emails per account per day** (configurable)
- ✅ Each sender sends N emails, then moves to next sender
- ✅ Follow-ups use primary sender account

### How It Works

**Sender Rotation Example:**
- 100 leads total
- 5 sender accounts
- 30 emails per day

**Campaign Flow:**
```
Account 1: Sends 30 emails (leads 1-30)
Account 2: Sends 30 emails (leads 31-60)
Account 3: Sends 30 emails (leads 61-90)
Account 4: Sends 10 emails (leads 91-100)
Account 5: Reserved for follow-ups

Total campaign sends 100 emails across 4 accounts
```

### Dashboard Features Updated

**Setup Section:**
- Campaign name
- **Emails Per Account Per Day** (default 30, adjustable)
- Lead file upload

**Sender Accounts Section:**
- Add up to **5 email accounts**
- Select provider (Gmail, Zoho, Outlook, Yahoo, SendGrid)
- Email address
- App password
- Auto-validation

**Email Configuration:**
- Templates (multiple, rotate every 3 emails)
- Subject lines (round-robin distribution)
- Follow-ups (1, 2, 3+ days)

**Campaign Management:**
- Real-time progress tracking
- Sender rotation display
- Start/Stop/Resume controls
- Statistics dashboard

### Technical Implementation

**Backend (app.py):**
- New `MultiAccountEmailCampaign` class
- Sender rotation logic
- Configurable emails per account
- Multi-provider SMTP support
- Follow-up scheduling
- Email delays: 3-8 seconds (anti-spam)

**Frontend (index.html):**
- Sender account management UI
- Drag-add up to 5 accounts
- Real-time campaign monitoring
- Progress percentage display
- Sender count display

### Files Structure
```
├── app.py                    # Updated backend (24 KB)
├── templates/index.html      # Updated UI (30 KB)
├── requirements.txt          # Dependencies
└── PROJECT_STATUS.md        # This file
```

## 🎯 How to Use

### 1. Add Sender Accounts
1. Go to "Sender Accounts (Add 5)" section
2. Click "+ Add Sender Account" (up to 5 times)
3. For each account:
   - Select Email Provider
   - Enter Email Address
   - Enter App Password
   - System validates connection

### 2. Configure Campaign
1. **Campaign Name**: Enter campaign name
2. **Emails Per Account**: Set how many emails per account (default 30)
3. **Upload Leads**: CSV/Excel with Business Name, Email, Location
4. **Add Templates**: Create email templates with [placeholders]
5. **Subject Lines**: Add multiple subject lines
6. **Follow-ups**: Optional follow-up sequences

### 3. Start Campaign
1. Click "🚀 Send Campaign"
2. Confirm number of leads and accounts
3. Campaign auto-starts
4. Dashboard shows real-time progress

### 4. Monitor
- View sent/failed count
- See which sender is active
- Track progress percentage
- View detailed results

## 📊 Campaign Execution Flow

```
[Upload Leads] 
    ↓
[Configure Accounts & Templates]
    ↓
[Start Campaign]
    ↓
[Account 1] → [30 emails + 3-8s delays]
    ↓
[Account 2] → [30 emails + 3-8s delays]
    ↓
[Account 3] → [30 emails + 3-8s delays]
    ↓
[Account 4] → [Remaining emails]
    ↓
[All senders complete] → [Follow-ups Schedule]
    ↓
[Follow-ups run in background] → [Every 60s check]
```

## 🔧 Configuration

### Email Delays
- **Between emails**: 3-8 seconds (randomized, anti-spam)
- **Between senders**: 2 seconds (pause between rotations)

### Default Settings
- **Emails per account**: 30 (adjustable 1-100)
- **Template rotation**: Every 3 emails
- **Subject lines**: Round-robin per email
- **Follow-ups**: 1, 2, 3 days after initial

### Customizable Parameters
- Emails per day per account
- Number of templates
- Subject line variations
- Follow-up timing
- Email delays

## 📱 Supported Email Providers

1. **Gmail** - https://myaccount.google.com/apppasswords
2. **Zoho Mail** - https://mail.zoho.com → Settings → Security
3. **Outlook/Office365** - account.microsoft.com → Security
4. **Yahoo Mail** - Yahoo Account Security
5. **SendGrid** - https://app.sendgrid.com/settings/api_keys

## 🚀 Current Status

- **Server**: Running at http://localhost:5000
- **Features**: Fully operational
- **Download**: Available (ZIP export)
- **Test Status**: ✓ Backend tested, ✓ Frontend tested, ✓ Multi-account ready

## 🎯 Example Scenarios

### Scenario 1: Small Campaign
- **Leads**: 150
- **Accounts**: 3
- **Per Account**: 50 emails
- **Result**: Account 1 (50) → Account 2 (50) → Account 3 (50)

### Scenario 2: Large Campaign
- **Leads**: 500
- **Accounts**: 5
- **Per Account**: 30 emails
- **Result**: 150 total from all accounts in rotation

### Scenario 3: Daily Limits
- **Leads**: 100
- **Accounts**: 2
- **Per Account**: 30 emails
- **Result**: Account 1 (30) → Account 2 (30) → Follow-ups next day

## ⚙️ Advanced Settings

### Rate Limiting
- Each email: 3-8 second random delay
- Between sender rotation: 2 seconds
- Adjustable for different SMTP providers

### Template Logic
- Rotates every 3 emails
- Prevents Gmail flagging same content
- Supports [Business Name], [City], [Location] placeholders

### Subject Line Distribution
- Round-robin: Subject 1 → Subject 2 → Subject 3 → etc.
- Each lead gets different subject
- Helps with open rate testing

## 🔐 Security Notes

- App passwords stored in browser session only
- No passwords saved to disk
- Credentials transmitted over HTTPS (localhost: unencrypted)
- Each campaign isolated in memory
- Data cleared on server restart

## 📋 Troubleshooting

### Issue: "Add Sender" button disabled
- **Cause**: Already added 5 accounts
- **Fix**: Remove one account first

### Issue: Authentication failed
- **Cause**: Wrong password or wrong email
- **Fix**: Verify app password from provider settings
- **Note**: Cannot use regular passwords for Gmail/Outlook

### Issue: Emails send too slowly
- **Cause**: Default 3-8s delays
- **Fix**: Edit `app.py` → change `random.uniform(3, 8)` to `random.uniform(1, 3)`

### Issue: Emails not sending from Account 2+
- **Cause**: Account credentials wrong or SMTP blocked
- **Fix**: Test each account individually first

### Issue: Follow-ups not running
- **Cause**: Python process stopped
- **Fix**: Keep command window open

## 💡 Pro Tips

1. **Test first**: Add 5 accounts, upload 5 test leads, run small campaign
2. **Stagger delays**: Use 3-8s to avoid spam filters
3. **Vary templates**: 2-3 templates prevent Gmail filters
4. **Monitor first batch**: Start, pause, review results before continuing
5. **Follow-ups matter**: 3-day follow-up sequence increases response rate
6. **Rotate daily**: Spread 30 emails per account across multiple days if needed

## 📞 Support

**Common Commands:**
- Start campaign: Fill form → Click "Send Campaign"
- Resume paused: Campaign auto-resumes or click Resume button
- Stop campaign: Click Stop button
- View results: Scroll to "Active Campaigns" section
- Download: Click green "📦 Download" button

**Debug Info:**
- Check Python console for [BATCH], [SUCCESS], [FAILED] logs
- Browser console (F12) for JavaScript errors
- Campaign ID in confirmation shows campaign timestamp

## 🎁 What's Included

- ✅ Multi-account sender rotation
- ✅ 30 emails per account per day (customizable)
- ✅ 5 email provider support
- ✅ Multiple template system
- ✅ A/B subject line testing
- ✅ Batch sending with delays
- ✅ Follow-up scheduler
- ✅ Real-time dashboard
- ✅ Stop/Resume controls
- ✅ Download as ZIP

---

**Version**: Multi-Account Edition  
**Status**: Production Ready  
**Last Updated**: Current Session  
**Server**: Flask Development Server
