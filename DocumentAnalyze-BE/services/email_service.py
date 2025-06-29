from imap_tools import MailBox, AND
from io import BytesIO

def fetch_email_attachments(email, password, imap_server='imap.gmail.com'):
    attachments = []
    with MailBox(imap_server).login(email, password) as mailbox:
        for msg in mailbox.fetch(AND(seen=False), reverse=True, limit=5):
            for att in msg.attachments:
                attachments.append({
                    "filename": att.filename,
                    "content": BytesIO(att.payload),
                    "subject": msg.subject,
                    "from": msg.from_,
                    "date": msg.date
                })

            # ✅ This is correct usage
            mailbox.flag(msg.uid, '\\Seen', True)

    return attachments
