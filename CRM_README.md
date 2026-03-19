# CRM Features (Add-on)

CRM layers on top of the existing Flask email system. **Existing sending and logging (email_logs.json, sent_leads.json) are unchanged.**

## Feature flags / environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CRM` | `1` | Set to `0` or `false` to disable all CRM features; app behaves as before. |
| `DATABASE_URI` | `sqlite:///crm.db` | SQLite DB for Leads, Campaigns, EmailsSent. |
| `TRACKING_BASE_URL` | `http://localhost:5000` | Base URL for open/click tracking (use your public URL in production). |
| `REMINDER_DAYS` | `3` | Days after send with no open/click to include in reminder alerts. |

## Backup before migration

- **Database:** Copy `crm.db` (or your `DATABASE_URI` path) before any schema change or upgrade.
- **Existing logs:** `email_logs.json` and `sent_leads.json` are **not** modified by CRM; no backup needed for them for CRM.

## What was added

1. **DB tables:** Leads, Campaigns, EmailsSent (indexes on email, lead_id, campaign_id). No changes to existing log files.
2. **Import dedup:** CSV/Excel import normalizes emails and deduplicates against the Leads table; skipped duplicates are logged to `crm_import_skipped.log`.
3. **Sending:** Before send, checks EmailsSent for that lead+campaign; skips unless "Allow resend" is checked. After send, records in EmailsSent and keeps existing `log_email_sent` / `add_to_sent_leads`.
4. **Reminders:** APScheduler job (hourly) finds leads with no open/click after `REMINDER_DAYS`; results appear under **CRM → Reminder alerts**.
5. **Dashboard:** `/crm` — campaigns, leads, stats, filters (today’s sends, not contacted).
6. **Tracking:** Open = 1×1 pixel (`/api/track/open/<id>`); click = redirect (`/api/track/click/<id>?url=<base64>`). Both update EmailsSent only; they do not affect sending.

## Running tests

```bash
cd default
pip install -r requirements.txt
pytest tests/test_crm.py -v
```

Tests use an in-memory SQLite DB and do not touch `crm.db` or existing logs.
