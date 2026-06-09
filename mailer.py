"""
Secure Credential Mailer — CLI Entry Point

Usage:
  # Generate a Fernet key (do this once, save to .env)
  python mailer.py --keygen

  # Single distribution
  python mailer.py --user "John Doe" --email "john@company.com" --credential "TempPass@123"

  # Single distribution with custom system name
  python mailer.py --user "Jane Smith" --email "jane@company.com" --credential "Key#456" --system "HR Portal"

  # Bulk from CSV (columns: name,email,credential[,system_name])
  python mailer.py --bulk users.csv

  # Send expiry reminders for credentials expiring within N days (default 1)
  python mailer.py --expiry-reminders --days 2

  # Export compliance report to CSV
  python mailer.py --report
"""

import argparse
import csv
import sys

from settings import settings


def cmd_keygen():
    from core.encryptor import generate_key
    key = generate_key()
    print("Generated Fernet key (add to .env as FERNET_KEY):\n")
    print(f"FERNET_KEY={key}")


def cmd_single(user: str, email: str, credential: str, system: str):
    from core.encryptor import Encryptor
    from core.splitter import split_deliver
    from audit.logger import AuditLogger

    enc = Encryptor(settings.fernet_key)
    audit = AuditLogger(settings.audit_db)

    print(f"Distributing credentials for {user} <{email}>...")
    ok = split_deliver(
        recipient_name=user,
        recipient_email=email,
        credential=credential,
        system_name=system,
        encryptor=enc,
        audit=audit,
    )
    if ok:
        print("Done.")
    else:
        print("Distribution failed — check logs.", file=sys.stderr)
        sys.exit(1)


def cmd_bulk(csv_path: str, system: str):
    from core.encryptor import Encryptor
    from core.splitter import split_deliver
    from audit.logger import AuditLogger

    enc = Encryptor(settings.fernet_key)
    audit = AuditLogger(settings.audit_db)

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    required = {"name", "email", "credential"}
    if not required.issubset({c.lower() for c in (reader.fieldnames or [])}):
        print(
            f"[ERROR] CSV must have columns: name, email, credential (got: {reader.fieldnames})",
            file=sys.stderr,
        )
        sys.exit(1)

    success, failed = 0, 0
    for i, row in enumerate(rows, 1):
        name = row.get("name", "").strip()
        email = row.get("email", "").strip()
        credential = row.get("credential", "").strip()
        sys_name = row.get("system_name", system).strip() or system

        if not name or not email or not credential:
            print(f"  Row {i}: skipped (missing fields)")
            failed += 1
            continue

        print(f"  [{i}/{len(rows)}] {name} <{email}>")
        ok = split_deliver(
            recipient_name=name,
            recipient_email=email,
            credential=credential,
            system_name=sys_name,
            encryptor=enc,
            audit=audit,
        )
        if ok:
            success += 1
        else:
            failed += 1

    print(f"\nBulk complete: {success} sent, {failed} failed.")


def cmd_expiry_reminders(within_days: int):
    from core.encryptor import Encryptor
    from core.smtp_client import smtp_client
    from audit.logger import AuditLogger
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    audit = AuditLogger(settings.audit_db)
    expiring = audit.get_expiring_soon(within_days=within_days)

    if not expiring:
        print(f"No credentials expiring within {within_days} day(s).")
        return

    jinja = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"]),
    )

    print(f"Sending expiry reminders for {len(expiring)} distribution(s)...")
    for dist in expiring:
        html = jinja.get_template("expiry_reminder.html").render(
            recipient_name=dist["recipient_name"],
            system_name=dist["system_name"],
            expiry_date=dist["expiry_date"],
            dist_id=dist["id"],
        )
        try:
            smtp_client.send(
                subject=f"[ACTION REQUIRED] Your {dist['system_name']} credential expires on {dist['expiry_date']}",
                recipient=dist["recipient_email"],
                html_body=html,
            )
            print(f"  Reminder sent to {dist['recipient_email']} | {dist['id']}")
        except Exception as e:
            print(f"  Failed for {dist['recipient_email']}: {type(e).__name__}", file=sys.stderr)


def cmd_report():
    from audit.logger import AuditLogger

    audit = AuditLogger(settings.audit_db)
    path = audit.export_report()
    print(f"Compliance report exported to: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Secure Credential Mailer — split-delivery compliance tool"
    )
    parser.add_argument("--keygen", action="store_true", help="Generate a new Fernet key")
    parser.add_argument("--user", help="Recipient full name")
    parser.add_argument("--email", help="Recipient email address")
    parser.add_argument("--credential", help="Temporary credential to distribute")
    parser.add_argument("--system", default="Company Portal", help="System/application name")
    parser.add_argument("--bulk", metavar="CSV", help="Bulk distribute from CSV file")
    parser.add_argument("--expiry-reminders", action="store_true", help="Send expiry reminder emails")
    parser.add_argument("--days", type=int, default=1, help="Days ahead for expiry reminders (default: 1)")
    parser.add_argument("--report", action="store_true", help="Export compliance report CSV")

    args = parser.parse_args()

    if args.keygen:
        cmd_keygen()
    elif args.bulk:
        cmd_bulk(args.bulk, args.system)
    elif args.expiry_reminders:
        cmd_expiry_reminders(args.days)
    elif args.report:
        cmd_report()
    elif args.user and args.email and args.credential:
        cmd_single(args.user, args.email, args.credential, args.system)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
