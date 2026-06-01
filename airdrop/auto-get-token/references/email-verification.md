# Email Verification for Airdrops

## Overview

Many airdrops require email verification. This guide covers how to handle email verification workflows.

## Gmail IMAP Setup

### App Password (Required)

Gmail requires App Password for IMAP access (not regular password).

1. Go to: https://myaccount.google.com/apppasswords
2. Login with 2FA
3. Select App: **Mail**
4. Click **Generate**
5. Copy 16-character password: `xxxx xxxx xxxx xxxx`

### IMAP Connection

```python
import imaplib
import email

EMAIL = "your@gmail.com"
APP_PASSWORD = "xxxx xxxx xxxx xxxx"

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, APP_PASSWORD)
mail.select("INBOX")

# Search for emails
result, data = mail.search(None, "ALL")
email_ids = data[0].split()

# Get latest email
latest_id = email_ids[-1]
result, msg_data = mail.fetch(latest_id, "(RFC822)")
raw = msg_data[0][1]
msg = email.message_from_bytes(raw)

print(f"From: {msg['From']}")
print(f"Subject: {msg['Subject']}")

# Get body
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode()
            print(body)
            break
else:
    body = msg.get_payload(decode=True).decode()
    print(body)

mail.logout()
```

## Email Verification Workflow

### Step 1: Submit Email

```python
# Navigate to airdrop page
page.goto("https://airdrop.example.com")

# Find email input
email_input = page.locator('input[type="email"]')
email_input.fill("your@gmail.com")

# Click submit
submit_btn = page.locator('button:has-text("Send"), button:has-text("Submit")')
submit_btn.click()
```

### Step 2: Wait for Verification Email

```python
import time

def wait_for_email(email_address, app_password, subject_keyword, max_wait=300):
    """Wait for email with specific subject"""
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, app_password)
        mail.select("INBOX")
        
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()
        
        # Check last 10 emails
        for eid in email_ids[-10:]:
            result, msg_data = mail.fetch(eid, "(BODY[HEADER.FIELDS (FROM SUBJECT)])")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            
            if subject_keyword.lower() in str(msg['Subject']).lower():
                mail.logout()
                return msg
        
        mail.logout()
        time.sleep(10)  # Wait 10 seconds before checking again
    
    return None
```

### Step 3: Extract Verification Code

```python
import re

def extract_code_from_email(msg):
    """Extract 6-digit code from email"""
    
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()
    
    # Look for 6-digit code
    code_match = re.search(r'\b(\d{6})\b', body)
    if code_match:
        return code_match.group(1)
    
    return None
```

### Step 4: Enter Verification Code

```python
# Find code input
code_input = page.locator('input[placeholder*="code"], input[type="number"]')
code_input.fill(code)

# Click verify
verify_btn = page.locator('button:has-text("Verify"), button:has-text("Submit")')
verify_btn.click()
```

## Common Issues

### 1. Email Not Arriving

**Possible causes:**
- Email filtered to spam
- Email delivery delayed (can take 5-10 minutes)
- Wrong email address submitted
- Airdrop system issues

**Solutions:**
- Check spam folder
- Wait longer (up to 10 minutes)
- Resend verification email
- Try different email address

### 2. Verification Code Expired

**Solution:**
- Request new code
- Enter code immediately after receiving

### 3. IMAP Connection Failed

**Possible causes:**
- Wrong App Password
- 2FA not enabled
- IMAP not enabled in Gmail settings

**Solutions:**
- Generate new App Password
- Enable 2FA in Google Account
- Enable IMAP in Gmail Settings → Forwarding and POP/IMAP

## Email Folder Structure

```
INBOX          - Main inbox
[Gmail]/Spam   - Spam folder
[Gmail]/All Mail - All emails
[Gmail]/Starred - Starred emails
[Gmail]/Trash  - Deleted emails
```

## Search Emails

```python
# Search by sender
result, data = mail.search(None, 'FROM "airdrop@example.com"')

# Search by subject
result, data = mail.search(None, 'SUBJECT "verification"')

# Search by date
result, data = mail.search(None, 'SINCE "01-Jan-2026"')

# Search unread
result, data = mail.search(None, 'UNSEEN')
```

## Best Practices

1. **Use dedicated email for airdrops** - Separate from personal email
2. **Check spam folder** - Verification emails often go to spam
3. **Save verification codes** - May need for future reference
4. **Document email submissions** - Track which airdrops you've signed up for
5. **Use App Password** - More secure than regular password
6. **Handle timeouts** - Email delivery can be slow
