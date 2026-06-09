import time
from datetime import datetime, timedelta

from jinja2 import Environment, FileSystemLoader, select_autoescape

from audit.logger import AuditLogger
from core.encryptor import Encryptor
from core.smtp_client import smtp_client
from settings import settings

_jinja = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html"]),
)


def _render(template_name: str, **ctx) -> str:
    return _jinja.get_template(template_name).render(**ctx)


def split_deliver(
    recipient_name: str,
    recipient_email: str,
    credential: str,
    system_name: str = "Company Portal",
    account_login: str = "",
    expiry_days: int | None = None,
    encryptor: Encryptor | None = None,
    audit: AuditLogger | None = None,
) -> bool:
    if encryptor is None:
        encryptor = Encryptor(settings.fernet_key)
    if audit is None:
        audit = AuditLogger(settings.audit_db)

    expiry_days = expiry_days if expiry_days is not None else settings.credential_expiry_days
    expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
    login = account_login or recipient_email

    encrypted_credential = encryptor.encrypt(credential)
    dist_id = audit.start_distribution(
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        system_name=system_name,
        expiry_date=expiry_date,
    )

    # --- Part 1: username / account details ---
    part1_html = _render(
        "email_part1.html",
        recipient_name=recipient_name,
        system_name=system_name,
        account_login=login,
        expiry_date=expiry_date,
        dist_id=dist_id,
    )
    part1_ok = False
    try:
        smtp_client.send(
            subject=f"Your account has been created — Part 1 of 2 [{dist_id}]",
            recipient=recipient_email,
            html_body=part1_html,
        )
        part1_ok = True
    except Exception as e:
        audit.record_part(dist_id, part=1, status="FAILED", error_type=type(e).__name__)
        return False

    audit.record_part(dist_id, part=1, status="SENT")

    # --- enforced delay ---
    delay = settings.split_delay_seconds
    print(f"  Part 1 sent. Waiting {delay}s before sending Part 2...")
    time.sleep(delay)

    # --- Part 2: encrypted credential ---
    part2_html = _render(
        "email_part2.html",
        recipient_name=recipient_name,
        system_name=system_name,
        encrypted_credential=encrypted_credential,
        expiry_date=expiry_date,
        dist_id=dist_id,
    )
    try:
        smtp_client.send(
            subject=f"Your temporary credential — Part 2 of 2 [{dist_id}]",
            recipient=recipient_email,
            html_body=part2_html,
        )
    except Exception as e:
        audit.record_part(dist_id, part=2, status="FAILED", error_type=type(e).__name__)
        return False

    audit.record_part(dist_id, part=2, status="SENT")
    audit.complete_distribution(dist_id)
    print(f"  Part 2 sent. Distribution {dist_id} complete.")
    return True
