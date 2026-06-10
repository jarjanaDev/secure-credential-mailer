"""
FastAPI REST wrapper for secure-credential-mailer.

Start: uvicorn api:app --host 0.0.0.0 --port 8000
Docs:  http://localhost:8000/docs
"""

import os
import secrets
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from audit.logger import AuditLogger
from core.encryptor import Encryptor
from core.splitter import split_deliver
from settings import settings

# ── Auth ──────────────────────────────────────────────────────────────────────
_security = HTTPBasic()
_API_USER = os.getenv("API_USER", "itops")
_API_PASS = os.getenv("API_PASSWORD", "changeme")


def require_auth(credentials: HTTPBasicCredentials = Depends(_security)):
    ok = secrets.compare_digest(credentials.username, _API_USER) and \
         secrets.compare_digest(credentials.password, _API_PASS)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Secure Credential Mailer",
    description="Split-delivery credential distribution API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://localhost:5001",
        "https://localhost:5001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class DistributeRequest(BaseModel):
    name: str
    email: str
    credential: str
    system_name: str = "Company Portal"
    account_login: str = ""
    expiry_days: int | None = None


class DistributeResult(BaseModel):
    success: bool
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.post(
    "/distribute",
    response_model=DistributeResult,
    dependencies=[Depends(require_auth)],
)
def distribute_single(req: DistributeRequest):
    """Distribute credentials via two-email split delivery."""
    enc = Encryptor(settings.fernet_key)
    audit = AuditLogger(settings.audit_db)
    ok = split_deliver(
        recipient_name=req.name,
        recipient_email=req.email,
        credential=req.credential,
        system_name=req.system_name,
        account_login=req.account_login,
        expiry_days=req.expiry_days,
        encryptor=enc,
        audit=audit,
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Distribution failed — check SMTP config")
    return DistributeResult(success=True, message=f"Credentials distributed to {req.email}")


@app.post(
    "/distribute/bulk",
    response_model=list[DistributeResult],
    dependencies=[Depends(require_auth)],
)
def distribute_bulk(items: list[DistributeRequest]):
    """Distribute credentials to multiple recipients in sequence."""
    enc = Encryptor(settings.fernet_key)
    audit = AuditLogger(settings.audit_db)
    results = []
    for req in items:
        ok = split_deliver(
            recipient_name=req.name,
            recipient_email=req.email,
            credential=req.credential,
            system_name=req.system_name,
            account_login=req.account_login,
            expiry_days=req.expiry_days,
            encryptor=enc,
            audit=audit,
        )
        results.append(DistributeResult(
            success=ok,
            message=f"Distributed to {req.email}" if ok else f"Failed for {req.email}",
        ))
    return results


@app.get("/audit", dependencies=[Depends(require_auth)])
def get_audit_log(limit: int = 100):
    """Fetch recent distribution audit records."""
    audit = AuditLogger(settings.audit_db)
    with audit._connect() as conn:
        rows = conn.execute(
            "SELECT * FROM distributions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/audit/expiring", dependencies=[Depends(require_auth)])
def get_expiring(days: int = 1):
    """Fetch distributions whose credentials expire within N days."""
    audit = AuditLogger(settings.audit_db)
    return audit.get_expiring_soon(within_days=days)


@app.post("/audit/report", dependencies=[Depends(require_auth)])
def export_report():
    """Export full compliance report as CSV."""
    audit = AuditLogger(settings.audit_db)
    path = audit.export_report()
    return {"path": path}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
