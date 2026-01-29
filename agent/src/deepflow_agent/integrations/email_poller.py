import os
import time
import imaplib
import smtplib
import email
import logging
import asyncio
from email.mime.text import MIMEText
from email.header import decode_header
from typing import Optional, List, Tuple

from ..agents.react_agent import process_message
from ..tools.base import get_redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailPoller:
    def __init__(self):
        self.imap_server = os.environ.get("EMAIL_IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.username = os.environ.get("EMAIL_USER")
        self.password = os.environ.get("EMAIL_PASSWORD")
        self.check_interval = int(os.environ.get("EMAIL_CHECK_INTERVAL", "60"))
        
        if not self.username or not self.password:
             raise ValueError("EMAIL_USER and EMAIL_PASSWORD must be set")

        self.redis = get_redis_client()

    def connect_imap(self) -> imaplib.IMAP4_SSL:
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.username, self.password)
        return imap

    def send_email(self, recipient: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = recipient

        try:
            with smtplib.SMTP_SSL(self.smtp_server, 465) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(msg)
            logger.info(f"📧 Sent email to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def _decode_header(self, header_value):
        if not header_value:
            return ""
        decoded_list = decode_header(header_value)
        decoded_str = ""
        for token, encoding in decoded_list:
            if isinstance(token, bytes):
                if encoding:
                    decoded_str += token.decode(encoding)
                else:
                    decoded_str += token.decode("utf-8", errors="ignore")
            else:
                decoded_str += token
        return decoded_str

    def process_emails(self):
        logger.info(f"Checking for emails on {self.imap_server}...")
        try:
            imap = self.connect_imap()
            imap.select("INBOX")
            
            # Search for all unread emails
            status, messages = imap.search(None, "UNSEEN")
            if status != "OK":
                return

            email_ids = messages[0].split()
            
            for e_id in email_ids:
                try:
                    res, msg_data = imap.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            subject = self._decode_header(msg["Subject"])
                            from_ = self._decode_header(msg["From"])
                            # Extract email address roughly
                            if "<" in from_:
                                sender_email = from_.split("<")[1].split(">")[0]
                            else:
                                sender_email = from_
                            
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    pass
                                    
                            logger.info(f"📩 New Email from {sender_email}: {subject}")
                            
                            # Handle binding
                            self.handle_incoming_email(sender_email, subject, body)

                except Exception as e:
                    logger.error(f"Error processing email {e_id}: {e}")

            imap.close()
            imap.logout()
            
        except Exception as e:
            logger.error(f"IMAP polling error: {e}")

    def handle_incoming_email(self, sender: str, subject: str, content: str):
        # 1. Check Binding
        deepflow_user_id = self.redis.get(f"email_binding:{sender}")
        
        # Simple linking command via email subject
        if "Link DeepFlow" in subject:
             # Content might be "User ID: 123"
             if "User ID:" in content:
                 uid = content.split("User ID:")[1].strip().split("\n")[0]
                 self.redis.set(f"email_binding:{sender}", uid)
                 self.send_email(sender, "DeepFlow Linked", f"✅ Successfully linked email {sender} to DeepFlow user {uid}")
                 return
        
        if not deepflow_user_id:
            # Auto-reply with instruction
            self.send_email(sender, "Action Required: Link Account", 
                            "Your email is not linked to DeepFlow.\n\n"
                            "To link, reply with Subject: 'Link DeepFlow' and Body: 'User ID: <your_id>'")
            return

        # 2. Get User State
        user_state = self.redis.get(f"user_state:{deepflow_user_id}") or "FLOW"
        
        # 3. Process with Agent
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                process_message(
                    user_id=deepflow_user_id,
                    user_state=user_state,
                    message_content=f"Subject: {subject}\n\n{content}",
                    sender=sender,
                    source="email"
                )
            )
            loop.close()
            
            output = result.get("output", "")
            # Only send generic output if it wasn't handled by a tool or if it's a direct response
            if output and output != "Agent completed":
                 self.send_email(sender, f"Re: {subject}", output)
                 
        except Exception as e:
            logger.error(f"Agent Processing Error: {e}")

    def start(self):
        logger.info(f"📧 Email Poller started. Checking every {self.check_interval}s")
        while True:
            self.process_emails()
            time.sleep(self.check_interval)

if __name__ == "__main__":
    poller = EmailPoller()
    poller.start()
