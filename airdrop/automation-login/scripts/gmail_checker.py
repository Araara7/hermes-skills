#!/usr/bin/env python3
"""
Gmail Checker - Check Gmail via IMAP with App Password
Usage: python gmail_checker.py [--count N]
"""

import sys
import imaplib
import email
from datetime import datetime

def check_gmail(email_addr, app_password, count=5):
    """Check Gmail via IMAP"""
    
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_addr, app_password)
        print(f"✅ Login berhasil!")
        
        # Select inbox
        mail.select("INBOX")
        
        # Search for emails
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()
        print(f"📧 Total emails: {len(email_ids)}")
        
        # Get last N emails
        print(f"\n📩 {count} Email Terakhir:")
        print("-" * 50)
        
        for eid in email_ids[-count:]:
            result, msg_data = mail.fetch(eid, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            
            # Parse date
            date_str = msg['Date']
            try:
                date_obj = email.utils.parsedate_to_datetime(date_str)
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = date_str
            
            print(f"From: {msg['From'][:50]}")
            print(f"Subject: {msg['Subject'][:50]}")
            print(f"Date: {formatted_date}")
            print("-" * 50)
        
        mail.logout()
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ Login gagal: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Load from .env
    import os
    from pathlib import Path
    
    env_file = Path.home() / "airdrop-agent" / "config" / "credentials" / ".env"
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("EMAIL_ADDRESS="):
                    email_addr = line.strip().split("=", 1)[1]
                elif line.startswith("EMAIL_APP_PASSWORD="):
                    app_password = line.strip().split("=", 1)[1]
    
    count = 5
    if "--count" in sys.argv:
        idx = sys.argv.index("--count")
        if idx + 1 < len(sys.argv):
            count = int(sys.argv[idx + 1])
    
    check_gmail(email_addr, app_password, count)
