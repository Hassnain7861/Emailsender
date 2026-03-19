#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to show how the campaign works
Run this to see the parallel sending simulation
"""

import random
import time
import threading
from datetime import datetime

class DemoSender:
    def __init__(self, sender_num, leads_start, leads_end, total_leads):
        self.sender_num = sender_num
        self.leads_start = leads_start
        self.leads_end = leads_end
        self.total_leads = total_leads
        self.emails_sent = 0
        
    def send_emails(self):
        """Simulate sending emails with random 25-45 second delays"""
        num_leads = self.leads_end - self.leads_start
        
        print(f"[SENDER {self.sender_num}] Starting - Will send 3 emails demo (Leads {self.leads_start + 1}-{self.leads_start + 3})")
        
        # Demo with just 3 emails per sender
        for i in range(min(3, num_leads)):
            lead_num = self.leads_start + i + 1
            email = f"lead{lead_num}@test.com"
            
            # Simulate email sending
            print(f"[SENDER {self.sender_num}] SENT Email {i + 1}/3 to {email}")
            self.emails_sent += 1
            
            # Random delay between 25-45 seconds
            if i < 2:  # Not after last email
                delay = random.uniform(25, 45)
                print(f"[SENDER {self.sender_num}] WAIT {delay:.1f}s before next email...")
                time.sleep(delay)
        
        print(f"[SENDER {self.sender_num}] DONE: {self.emails_sent} emails sent")

def run_demo():
    """Run the demo campaign"""
    print("\n" + "="*80)
    print("DEMO: Multi-Account Email Campaign (Parallel Mode)")
    print("="*80)
    print(f"\nStarting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n5 SENDERS x 30 EMAILS EACH = 150 TOTAL")
    print("DIFFERENT LEADS FOR EACH ACCOUNT")
    print("RANDOM 25-45 SECOND DELAYS BETWEEN EACH EMAIL")
    print("ALL SENDING SIMULTANEOUSLY")
    print("\n(Demo shows 3 emails per sender to illustrate)\n")
    
    # Create 5 senders
    senders = [
        DemoSender(1, 0, 30, 40),    # Sender 1: Leads 1-30
        DemoSender(2, 30, 60, 40),   # Sender 2: Leads 31-60
        DemoSender(3, 60, 90, 40),   # Sender 3: Leads 61-90
        DemoSender(4, 90, 120, 40),  # Sender 4: Leads 91-120
        DemoSender(5, 120, 150, 40), # Sender 5: Leads 121-150
    ]
    
    print("[CAMPAIGN] All 5 accounts starting SIMULTANEOUSLY...\n")
    
    # Create threads for each sender
    threads = []
    for sender in senders:
        thread = threading.Thread(target=sender.send_emails)
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Small delay between thread starts
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("\n" + "="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\nSUCCESS: All senders completed!")
    print("SUCCESS: Each account sent to DIFFERENT leads (no overlap)")
    print("SUCCESS: Each email had random 25-45 second delay")
    print("SUCCESS: All 5 accounts sent SIMULTANEOUSLY\n")

if __name__ == '__main__':
    run_demo()
