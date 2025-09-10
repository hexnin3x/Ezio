# In Backend/Email.py

import imaplib
import email
from email.header import decode_header
from dotenv import dotenv_values

# --- EMAIL FUNCTIONALITY ---

def check_emails(max_emails=5):
    """
    Checks for unread emails and returns a summary.
    """
    env_vars = dotenv_values(".env")
    EMAIL = env_vars.get("EMAIL_ADDRESS")
    PASSWORD = env_vars.get("EMAIL_PASSWORD")
    IMAP_SERVER = env_vars.get("IMAP_SERVER")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        if not email_ids:
            return "You have no new emails, Anshul."

        summary = f"You have {len(email_ids)} new emails. Here are the latest {min(len(email_ids), max_emails)}:\n"
        
        for e_id in reversed(email_ids[:max_emails]):
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            sender, encoding = decode_header(msg.get("From"))[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding if encoding else "utf-8")
            
            summary += f"- From {sender.split('<')[0].strip()}, subject: {subject}\n"
        
        mail.logout()
        return summary
    except Exception as e:
        print(f"Error checking email: {e}")
        return "I'm sorry, I couldn't check your email at the moment."