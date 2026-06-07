# 🔐 Secure Credential Mailer

> Enforces two-email compliance policy for credential distribution — eliminates manual handling risk and policy breaches.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-512BD4?style=flat-square&logo=dotnet&logoColor=white)
![Security](https://img.shields.io/badge/Security-Compliant-green?style=flat-square)
![Automation](https://img.shields.io/badge/Automation-Enabled-blue?style=flat-square)

---

## 🧩 Problem It Solves

Distributing temporary credentials (passwords, tokens, access keys) via email is a common IT operation — but doing it manually creates serious risks:

- Credentials sent in plain text in a single email
- No enforcement of split-delivery policy (username + password in separate emails)
- Human error leads to policy breaches and audit findings
- Manual process is slow during high-volume onboarding

**This tool enforces the two-email compliance policy automatically:**
- Username/credential details split across two separate encrypted emails
- Delivery enforced programmatically — no human can bypass it
- Full audit log of every credential distribution event
- Reduces distribution time from minutes to seconds

---

## ⚙️ Features

- ✅ **Split Delivery** — Username and credential sent in separate emails, enforced by code
- ✅ **Encryption** — Credentials encrypted before transmission
- ✅ **Audit Trail** — Every distribution logged with recipient, timestamp, delivery status
- ✅ **Bulk Mode** — Process multiple credential distributions from CSV
- ✅ **Expiry Notices** — Auto-send expiry reminders
- ✅ **Compliance Report** — Generate audit-ready distribution reports

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Core Language | Python 3.10+ |
| Encryption | Python cryptography library (Fernet) |
| Email | SMTP + HTML templates |
| Web UI (optional) | .NET Core / ASP.NET Razor Pages |
| Config | Pydantic Settings + .env |
| Audit Log | SQLite / CSV |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/jarjanaDev/secure-credential-mailer
cd secure-credential-mailer

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with SMTP settings

# Run single distribution
python mailer.py --user "John Doe" --email "john@company.com" --credential "TempPass@123"

# Run bulk from CSV
python mailer.py --bulk users.csv
```

---

## 📁 Project Structure

```
secure-credential-mailer/
├── mailer.py               # Main entry point (CLI)
├── core/
│   ├── encryptor.py        # Fernet encryption handler
│   ├── splitter.py         # Two-email split logic
│   └── smtp_client.py      # Email delivery
├── templates/
│   ├── email_part1.html    # Username/identity email template
│   └── email_part2.html    # Credential email template
├── audit/
│   └── logger.py           # Compliance audit logging
├── web/                    # Optional .NET web UI
│   └── CredentialPortal/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔒 How the Two-Email Policy Works

```
Email 1 (sent first):
  To: recipient@company.com
  Subject: Your account has been created — Part 1 of 2
  Body: Username, account details, instructions

  ← 30 second delay enforced by code →

Email 2 (sent after delay):
  To: recipient@company.com
  Subject: Your temporary credential — Part 2 of 2
  Body: Encrypted temporary password + expiry date
```

No single email ever contains both username and credential — policy enforced at code level, not process level.

---

## 📋 Compliance Benefits

- Eliminates credential policy breach risk
- Provides audit-ready distribution logs
- Enforces split-delivery without relying on human memory
- Reduces distribution time from ~3 minutes (manual) to ~5 seconds (automated)

---

## 👤 Author

**Santosh Dharma Jarjana**
[LinkedIn](https://linkedin.com/in/dharmasantosh0007) · [GitHub](https://github.com/jarjanaDev)
