# -*- coding: utf-8 -*-
"""
End-to-End Integration Test for CRM Upgrade.
Simulates a complete user journey:
1. Uploading a CSV with leads (including a duplicate).
2. Starting a campaign (mocking smtplib to prevent real emails).
3. Waiting for the campaign to finish sending.
4. Verifying the CRM database records the sends.
5. Simulating an "Open" and "Click" via the tracking API.
6. Verifying the Dashboard Stats and Follow-up APIs.
"""
import os
import sys
import time
import json
import base64
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['ENABLE_CRM'] = '1'
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'

# Prevent pytest guard conflicts if any
sys.modules.pop('app', None)
sys.modules.pop('crm', None)

from app import app as flask_app, campaigns
from crm_models import db, EmailsSent, Lead, Campaign

def run_e2e_test():
    flask_app.config['TESTING'] = True
    flask_app.config['ENABLE_CRM'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    print("==================================================")
    print("🚀 STARTING FULL E2E CRM INTEGRATION TEST")
    print("==================================================")

    with flask_app.app_context():
        db.create_all()
        client = flask_app.test_client()

        # Clear existing sent_emails so E2E test starts fresh
        client.delete('/api/sent-leads')

        # ---------------------------------------------------------
        # 1. UPLOAD CSV (Testing Deduplication)
        # ---------------------------------------------------------
        print("\n[1] Testing CSV Upload & Deduplication...")
        import time
        suffix = int(time.time())
        alice_email = f"alice_{suffix}@test.com"
        bob_email = f"bob_{suffix}@test.com"
        
        csv_data = (
            "Business Name,Email,Location\n"
            f"Company A, {alice_email}, NY\n"
            f"Company B, {bob_email}, LA\n"
            f"Company C, {alice_email.upper()}, NY\n"  # Duplicate of A
        ).encode('utf-8')

        import io
        res = client.post('/api/upload-leads', 
                          data={'file': (io.BytesIO(csv_data), 'leads.csv')},
                          content_type='multipart/form-data')
        
        data = res.get_json()
        assert data.get('success') is True, f"Upload failed: {data}"
        assert len(data['leads']) == 2, f"Expected 2 leads after dedup, got {len(data['leads'])}"
        assert data['crm_skipped'] == 1, "Expected 1 CRM duplicate skipped"
        print("✅ CSV Uploaded successfully. Deduplication worked (3 total -> 2 unique).")

        leads_to_send = data['leads']

        # ---------------------------------------------------------
        # 2. START CAMPAIGN (Mocking SMTP)
        # ---------------------------------------------------------
        print("\n[2] Starting Campaign...")
        payload = {
            "name": "E2E Test Campaign",
            "senders": [
                {"email": "sender1@test.com", "password": "pass", "provider": "gmail"}
            ],
            "leads": leads_to_send,
            "templates": [{"content": "Hello [Business Name] in [City]!"}],
            "subject_lines": ["Test Subject"],
            "speed_mode": "fast"
        }

        # Mock SMTP to avoid sending real emails, but simulate immediate success
        mock_smtp = MagicMock()
        with patch('smtplib.SMTP', return_value=mock_smtp):
            res = client.post('/api/send-campaign', json=payload)
            data = res.get_json()
            assert data.get('success') is True, f"Failed to start campaign: {data}"
            campaign_id = data['campaign_id']
            print(f"✅ Campaign '{campaign_id}' started.")

            # Wait for parallel threads to finish (should take ~1-2 seconds with fast mode + mock)
            print("⏳ Waiting for campaign workers to finish sending...")
            timeout = 30
            while timeout > 0:
                c = campaigns.get(campaign_id)
                if c and c.status in ('completed', 'failed'):
                    break
                time.sleep(1)
                timeout -= 1
            
            assert c.status == 'completed', f"Campaign did not complete. Status: {c.status}"
            assert c.sent == 2, f"Expected 2 emails sent, got {c.sent}"
            print("✅ Campaign finished successfully. 2 emails sent.")

        # ---------------------------------------------------------
        # 3. VERIFY CRM DATABASE (EmailsSent & Sync)
        # ---------------------------------------------------------
        print("\n[3] Verifying CRM Database Tracking...")
        cr_camp = Campaign.query.get(campaign_id)
        assert cr_camp is not None, "Campaign not synced to CRM DB"
        assert cr_camp.status == 'completed', f"Campaign CRM status is '{cr_camp.status}', expected 'completed'"

        sent_records = EmailsSent.query.filter_by(campaign_id=campaign_id).all()
        assert len(sent_records) == 2, "Expected 2 EmailsSent records in CRM DB"
        print("✅ CRM Database records verified (Campaign status synced, tracking IDs generated).")

        # ---------------------------------------------------------
        # 4. SIMULATE OPENS & CLICKS
        # ---------------------------------------------------------
        print("\n[4] Simulating Opens and Clicks...")
        # Get the first sent record (Alice)
        alice_record = next(r for r in sent_records if Lead.query.get(r.lead_id).email == alice_email)
        alice_eid = alice_record.id

        # Hit the open pixel
        res = client.get(f'/api/track/open/{alice_eid}')
        assert res.status_code == 200, "Open tracking pixel failed"

        # Hit the click redirect
        target_url = "https://example.com"
        enc_url = base64.urlsafe_b64encode(target_url.encode('utf-8')).decode('ascii').rstrip('=')
        res = client.get(f'/api/track/click/{alice_eid}?url={enc_url}')
        assert res.status_code == 302, "Click redirect failed"

        # Verify DB updated
        updated_alice = EmailsSent.query.get(alice_eid)
        assert updated_alice.opened_at is not None, "opened_at not set"
        assert updated_alice.clicked_at is not None, "clicked_at not set"
        print("✅ Open and Click tracking successful.")

        # ---------------------------------------------------------
        # 5. VERIFY DASHBOARD STATS
        # ---------------------------------------------------------
        print("\n[5] Verifying CRM Dashboard APIs...")
        res = client.get('/api/crm/stats')
        stats = res.get_json()
        assert stats['emails_sent_count'] == 2, "Stats mismatch: emails_sent_count"
        assert stats['opens_count'] == 1, "Stats mismatch: opens_count"
        assert stats['clicks_count'] == 1, "Stats mismatch: clicks_count"
        print("✅ Dashboard stats verified (50% Open/Click Rates accurately reflected).")

        # ---------------------------------------------------------
        # 6. VERIFY FOLLOW-UP LOGIC
        # ---------------------------------------------------------
        print("\n[6] Verifying Automated Follow-Up Queue...")
        flask_app.config['ENABLE_AUTO_FOLLOWUP'] = True

        # Need to backdate Bob's sent time to trigger follow-up
        bob_record = next(r for r in sent_records if Lead.query.get(r.lead_id).email == bob_email)
        import datetime
        bob_record.sent_at = datetime.datetime.utcnow() - datetime.timedelta(days=4)
        db.session.commit()

        # Trigger the scheduled background job manually
        from app import run_followup_job
        run_followup_job()

        res = client.get('/api/crm/followup-leads')
        fu_data = res.get_json()
        assert len(fu_data['leads']) == 1, f"Expected 1 lead for follow-up, got {len(fu_data['leads'])}"
        assert fu_data['leads'][0]['email'] == bob_email, "Wrong lead flagged for follow-up"
        print("✅ Follow-up queue correctly identified 'Bob' (No opens after 3+ days).")

        print("\n==================================================")
        print("🎉 ALL END-TO-END TESTS PASSED SUCCESSFULLY!")
        print("==================================================")

if __name__ == '__main__':
    run_e2e_test()
