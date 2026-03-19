# -*- coding: utf-8 -*-
"""
CRM helpers: dedup, send checks, recording, tracking. Wraps existing logic; does not replace it.
"""
import re
from datetime import datetime
from crm_models import db, Lead, Campaign, EmailsSent


def normalize_email(email):
    if not email or not isinstance(email, str):
        return ''
    return email.lower().strip()


def get_or_create_lead(email, name='', status='new'):
    """Get existing lead by email or create. Email must be normalized."""
    email = normalize_email(email)
    if not email:
        return None
    lead = Lead.query.filter(db.func.lower(Lead.email) == email).first()
    if lead:
        if name:
            lead.name = name
            lead.updated_at = datetime.utcnow()
            db.session.commit()
        return lead
    lead = Lead(email=email, name=(name or '').strip(), status=status or 'new')
    db.session.add(lead)
    db.session.commit()
    return lead


def lead_exists_by_email(email):
    """Check if lead exists by normalized email."""
    email = normalize_email(email)
    if not email:
        return False
    return Lead.query.filter(db.func.lower(Lead.email) == email).first() is not None


def create_campaign(campaign_id, name, description=None, scheduled_date=None):
    """Create CRM campaign row. Id is the same as in-memory campaign_id."""
    c = Campaign.query.get(campaign_id)
    if c:
        return c
    c = Campaign(
        id=campaign_id,
        name=name,
        description=description or '',
        scheduled_date=scheduled_date,
        status='pending'
    )
    db.session.add(c)
    db.session.commit()
    return c


def check_already_sent(lead_id, campaign_id):
    """True if this lead was already sent for this campaign."""
    if not lead_id or not campaign_id:
        return False
    return EmailsSent.query.filter_by(lead_id=lead_id, campaign_id=campaign_id).first() is not None


def record_sent_and_get_tracking_id(lead_id, campaign_id):
    """Create EmailsSent row and return its id for tracking pixel/links. Call before sending."""
    if not lead_id or not campaign_id:
        return None
    rec = EmailsSent(lead_id=lead_id, campaign_id=campaign_id, sent_at=datetime.utcnow())
    db.session.add(rec)
    db.session.commit()
    return rec.id


def mark_opened(emails_sent_id):
    """Mark email as opened (pixel hit). Idempotent."""
    print(f"[TRACKING] Mark Opened triggered for ID: {emails_sent_id}")
    import sys
    sys.stdout.flush()
    rec = EmailsSent.query.get(emails_sent_id)
    if rec:
        print(f"[TRACKING] Record found for ID {emails_sent_id}. Current opened_at: {rec.opened_at}")
        if not rec.opened_at:
            rec.opened_at = datetime.utcnow()
            db.session.commit()
            print(f"[TRACKING] Successfully marked ID {emails_sent_id} as OPENED at {rec.opened_at}")
    else:
        print(f"[TRACKING] CRITICAL: No record found in DB for ID: {emails_sent_id}")
    sys.stdout.flush()
    return rec


def mark_clicked(emails_sent_id):
    """Mark email as clicked. Idempotent."""
    rec = EmailsSent.query.get(emails_sent_id)
    if rec and not rec.clicked_at:
        rec.clicked_at = datetime.utcnow()
        db.session.commit()
    return rec


# URL pattern for wrapping links (plain text)
URL_PATTERN = re.compile(
    r'https?://[^\s<>"\']+',
    re.IGNORECASE
)


def wrap_links_for_tracking(body_plain, base_url, emails_sent_id):
    """Replace URLs in plain text with tracking redirect URL. base_url e.g. https://yoursite.com"""
    if not body_plain or not base_url or not emails_sent_id:
        return body_plain
    import base64
    def repl(m):
        url = m.group(0)
        enc = base64.urlsafe_b64encode(url.encode('utf-8')).decode('ascii').rstrip('=')
        return f'{base_url.rstrip("/")}/api/track/click/{emails_sent_id}?url={enc}'
    return URL_PATTERN.sub(repl, body_plain)


def inject_tracking_pixel(body_html_or_plain, base_url, emails_sent_id):
    """Append 1x1 tracking pixel. If body is plain text, wrap in minimal HTML."""
    if not base_url or not emails_sent_id:
        return body_html_or_plain
    pixel_url = f'{base_url.rstrip("/")}/api/track/open/{emails_sent_id}'
    print(f"[TRACKING] Injecting pixel: {pixel_url}")
    import sys
    sys.stdout.flush()
    pixel = f'<img src="{pixel_url}" width="1" height="1" style="display:none;" alt="" />'
    if body_html_or_plain.strip().lower().startswith('<'):
        return body_html_or_plain + '\n' + pixel
    # Plain text: escape and add pixel
    import html
    escaped = html.escape(body_html_or_plain).replace('\n', '<br>\n')
    return f'<div>{escaped}</div>\n{pixel}'


def update_campaign_status(campaign_id, status):
    """Update CRM Campaign.status after campaign completes. Does not affect sending."""
    if not campaign_id or not status:
        return None
    try:
        from crm_models import db, Campaign
        c = Campaign.query.get(campaign_id)
        if c:
            c.status = status
            db.session.commit()
            return True
    except Exception:
        pass
    return False


def update_email_status(emails_sent_id, status, error_msg=None):
    """Update CRM EmailsSent status (e.g. 'failed' or 'sent')."""
    if not emails_sent_id or not status:
        return False
    try:
        from crm_models import db, EmailsSent
        rec = EmailsSent.query.get(emails_sent_id)
        if rec:
            rec.status = status
            if error_msg:
                rec.error_message = error_msg
            db.session.commit()
            return True
    except Exception:
        pass
    return False


def get_leads_needing_followup(days=3, max_followup_count=3):
    """Return leads that were sent an email > `days` ago with no open/click
    and fewer than `max_followup_count` follow-ups. Does not trigger sends."""
    cutoff = datetime.utcnow() - __import__('datetime').timedelta(days=days)
    rows = EmailsSent.query.filter(
        EmailsSent.sent_at < cutoff,
        EmailsSent.opened_at.is_(None),
        EmailsSent.clicked_at.is_(None),
        EmailsSent.follow_up_count < max_followup_count,
    ).all()
    results = []
    for r in rows:
        lead = Lead.query.get(r.lead_id) if r.lead_id else None
        if lead:
            results.append({
                'lead_id': r.lead_id,
                'email': lead.email,
                'name': lead.name,
                'campaign_id': r.campaign_id,
                'emails_sent_id': r.id,
                'sent_at': r.sent_at.isoformat() if r.sent_at else None,
                'follow_up_count': r.follow_up_count,
            })
    return results

