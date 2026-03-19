# QUICK START - Multi-Account Email Campaign Dashboard

## 🎯 What You Can Do Now

Send 30 emails per day from 5 different email accounts with automatic rotation.

---

## ⚡ 5-Minute Setup

### Step 1: Open Dashboard
```
http://localhost:5000
```

### Step 2: Add Sender Accounts (5 max)
1. Go to **"Sender Accounts (Add 5)"** section (right column)
2. Click **"+ Add Sender Account"** 
3. For each account:
   - **Select Provider**: Gmail, Zoho, Outlook, Yahoo, or SendGrid
   - **Email Address**: your@email.com
   - **App Password**: (use app password, NOT regular password)
   - Click ✓ to confirm

**Example Setup:**
```
Account 1: gmail1@gmail.com (Gmail)
Account 2: gmail2@gmail.com (Gmail)
Account 3: business@zoho.com (Zoho)
Account 4: work@outlook.com (Outlook)
Account 5: office@yahoo.com (Yahoo)
```

### Step 3: Configure Campaign
1. **Campaign Name**: "Q1 2024 Campaign"
2. **Emails Per Account Per Day**: 30 (default)
3. **Upload Leads**: CSV/Excel file with columns:
   - Business Name
   - Email
   - Location

### Step 4: Create Templates
1. Go to **"Templates"** section
2. Click **"+ Add Template"** (optional - 1 default included)
3. Add email content with placeholders:
   - [Business Name]
   - [City]
   - [Location]

**Example:**
```
Hey [Business Name],

I noticed your business in [City].

You're missing out on [Location] Google rankings.

Reply if interested.

— Hassnain K
```

### Step 5: Add Subject Lines
1. Go to **"Subject Lines"** section
2. Add multiple subjects (applied round-robin):
   - "You're losing $7K/mo on Google"
   - "Quick SEO question about [City]"
   - "Missing: #1 position in [Location]"

### Step 6: Start Campaign
1. Click **"🚀 Send Campaign"**
2. Confirm when asked
3. **Campaign auto-rotates through accounts**

---

## 📊 What Happens During Campaign

**With 100 leads and 5 accounts at 30 emails per account:**

```
Account 1 (gmail1@gmail.com): Sends 30 emails
    ↓ [Each email: 3-8s delay]
Account 2 (gmail2@gmail.com): Sends 30 emails
    ↓ [Each email: 3-8s delay]
Account 3 (business@zoho.com): Sends 30 emails
    ↓ [Each email: 3-8s delay]
Account 4 (work@outlook.com): Sends 10 emails
    ↓ [Done]
```

**Total**: 100 emails sent across 4 accounts

---

## 🎮 Dashboard Controls

### Live Monitoring
- **Campaigns**: Shows all active campaigns
- **Progress**: Percentage of leads sent
- **Senders**: Which account is currently active
- **Sent/Failed**: Real-time counts

### Campaign Actions
- **▶️ Resume**: Continue from paused state
- **⏹️ Stop**: Stop sending (can restart later)
- **Status Badges**: pending, running, paused, completed, failed

---

## 💾 Getting App Passwords

### Gmail
1. Go: https://myaccount.google.com/apppasswords
2. Select: Mail + Windows Computer
3. Copy: 16-character password

### Zoho Mail
1. Go: https://mail.zoho.com
2. Click: Settings → Security
3. Generate: App Password
4. Copy: Password

### Outlook/Office365
1. Go: account.microsoft.com
2. Go to: Security
3. Find: App passwords
4. Generate: For Mail + Windows
5. Copy: Password

### Yahoo Mail
1. Go: Yahoo Account Security
2. Generate: App password for Yahoo Mail
3. Copy: Password

### SendGrid
1. Go: https://app.sendgrid.com/settings/api_keys
2. Create: New API Key
3. Copy: Use "apikey" as username, key as password

---

## 📈 Campaign Performance Tips

### To Maximize Delivery
1. **Vary templates**: Use 2-3 different templates (prevents Gmail filter)
2. **Multiple subjects**: 3-5 different subject lines
3. **Stagger senders**: Rotate through accounts every 30 emails
4. **Add delays**: 3-8 seconds between emails (built-in)

### To Get More Replies
1. **Personalize**: Use [Business Name], [City], [Location]
2. **Follow-ups**: Add 1, 2, 3 day follow-ups
3. **Test subjects**: A/B test different subject lines
4. **Short first email**: Keep initial message brief

---

## 🔄 Advanced: Follow-ups

Optional but recommended:

1. Go to **"Follow-up Sequences"** section
2. Click **"+ Add Follow-up"**
3. Set:
   - **Days After**: 1, 2, 3 (when to send)
   - **Subject**: "Following up on..."
   - **Message**: Different angle/CTA
4. System auto-sends at scheduled time

**Example 3-Day Sequence:**
```
Day 0: Initial email (30 emails across accounts)
Day 1: "Just following up..." (3-day sequence #1)
Day 2: "Question about [City]..." (3-day sequence #2)
Day 3: "Last thing..." (3-day sequence #3)
```

---

## 🚨 Important Notes

### Keep Command Window Open
- Python must keep running for follow-ups
- Don't close the terminal/cmd window
- Can close browser, server continues

### Each Account Can Send 30/Day
- Gmail: 30 emails safely per account
- Zoho: No daily limit (but respect provider)
- Outlook: 30/minute safe
- Yahoo: 100/day per account
- SendGrid: As per plan

### Email Delays
- **Between emails**: 3-8 seconds (randomized)
- **Between accounts**: 2 seconds
- Helps avoid spam filters

---

## ✅ Checklist Before Starting

- [ ] Added 5 sender accounts with correct passwords
- [ ] Uploaded leads CSV (has Email column)
- [ ] Created at least 1 template
- [ ] Added at least 1 subject line
- [ ] Set emails per day (default 30 is good)
- [ ] Optional: Added follow-up sequences

---

## 📞 Quick Troubleshooting

**"Authentication failed"**
- Check email address is correct
- Use APP PASSWORD, not regular password
- Go to provider settings and generate new app password

**"Cannot add 6th account"**
- System limited to 5 accounts max
- Remove one if needed

**"Campaign won't start"**
- Check all senders have email + password
- Check at least 1 lead uploaded
- Check 1 template exists

**"Follow-ups not sending"**
- Keep Python window open
- Check scheduled time (shows in results)
- Wait for scheduled time to pass

**"Emails sending too slow"**
- Default 3-8s is intentional (anti-spam)
- Edit app.py if you want faster

---

## 🎁 Premium Features in This Version

- ✅ 5 sender accounts (traditional: 1 account)
- ✅ 30 emails per account per day (traditional: 5 per batch)
- ✅ Automatic rotation (traditional: manual switching)
- ✅ Multi-provider support (Gmail, Zoho, Outlook, Yahoo, SendGrid)
- ✅ Follow-up scheduler (runs in background)
- ✅ Real-time dashboard
- ✅ Download as ZIP (run anywhere)
- ✅ A/B testing (subjects + templates)

---

## 📖 Common Tasks

### Send 150 emails from 5 accounts
- Add 5 accounts
- Upload 150 leads
- Set 30 per account
- Results: 30+30+30+30+30 = 150

### Send 500 emails (2-3 day campaign)
- Add 3-5 accounts
- Upload 500 leads
- Set 30 per account per day
- Results: Day 1 (150), Day 2 (150), Day 3 (150), Day 4 (50)

### Send with follow-ups
- Add 3 accounts
- Upload 50 leads
- Set 30 per account
- Add 3 follow-ups (1, 2, 3 day delays)
- Results: 50 initial + 50 follow-up #1 + 50 follow-up #2 + 50 follow-up #3

---

## 💬 Example Campaign

**Scenario**: Real Estate Agent, 100 leads

**Setup:**
- Leads: 100 real estate agents
- Accounts: 3 Gmail + 1 Zoho + 1 Outlook
- Template: Custom real estate angle
- Subject: "Missing: #1 position in [City] Google Maps"

**Execution:**
```
Account 1 (gmail1): 30 emails → agents 1-30
Account 2 (gmail2): 30 emails → agents 31-60
Account 3 (gmail3): 30 emails → agents 61-90
Account 4 (zoho):   10 emails → agents 91-100

Day 1: Total 100 emails sent across 4 accounts
Day 2: Follow-up #1 (50 replies potential)
Day 3: Follow-up #2 (20 replies potential)
Day 4: Follow-up #3 (10 replies potential)
```

---

**Ready to start?** Go to http://localhost:5000 and add your first sender account!
