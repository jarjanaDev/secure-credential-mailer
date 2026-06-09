import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr
from typing import List

from settings import settings

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _sanitize_header(value: str) -> str:
    return value.replace("\r", "").replace("\n", "")


def _validate_email(address: str) -> str | None:
    _, addr = parseaddr(address)
    return addr if addr and _EMAIL_RE.match(addr) else None


class SMTPClient:
    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.sender_name = settings.sender_name

    def send(self, subject: str, recipient: str, html_body: str) -> bool:
        clean_recipient = _validate_email(recipient)
        if not clean_recipient:
            raise ValueError(f"Invalid recipient address: {recipient!r}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = _sanitize_header(subject)
        msg["From"] = f"{_sanitize_header(self.sender_name)} <{_sanitize_header(self.user)}>"
        msg["To"] = clean_recipient
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.host, self.port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, [clean_recipient], msg.as_string())

        return True


smtp_client = SMTPClient()
