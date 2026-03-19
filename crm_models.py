# -*- coding: utf-8 -*-
"""
CRM database models. Does not modify or replace existing email_logs.json / sent_leads.json.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, inspect, text
import os
import shutil

db = SQLAlchemy()


class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), default='')
    status = db.Column(db.String(64), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    scheduled_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(64), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailsSent(db.Model):
    __tablename__ = 'emails_sent'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    campaign_id = db.Column(db.String(128), db.ForeignKey('campaigns.id'), nullable=False, index=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    follow_up_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32), default='sent')
    error_message = db.Column(db.Text, nullable=True)

    __table_args__ = (
        Index('ix_emails_sent_lead_campaign', 'lead_id', 'campaign_id'),
    )


def init_db(app):
    """Create tables and indexes. Safe to call on existing DB."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Migration: older crm.db files may not have follow_up_count.
        # We add it non-destructively to keep CRM dashboard working.
        try:
            if db.engine.dialect.name == 'sqlite':
                inspector = inspect(db.engine)
                cols = [c.get('name') for c in inspector.get_columns('emails_sent')]
                if 'follow_up_count' not in cols:
                    # Best-effort backup before migration (optional if db file not accessible)
                    db_uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
                    if db_uri.startswith('sqlite:///'):
                        db_path = db_uri.replace('sqlite:///', '', 1)
                        db_path = db_path.strip()
                        if db_path and os.path.exists(db_path):
                            shutil.copy2(db_path, db_path + '.bak_before_migration')

                    with db.engine.connect() as conn:
                        if 'follow_up_count' not in cols:
                            conn.execute(text('ALTER TABLE emails_sent ADD COLUMN follow_up_count INTEGER DEFAULT 0'))
                        if 'status' not in cols:
                            conn.execute(text("ALTER TABLE emails_sent ADD COLUMN status VARCHAR(32) DEFAULT 'sent'"))
                        if 'error_message' not in cols:
                            conn.execute(text("ALTER TABLE emails_sent ADD COLUMN error_message TEXT"))
                        conn.commit()
        except Exception:
            # If migration fails, app will still run but CRM may show errors.
            pass
