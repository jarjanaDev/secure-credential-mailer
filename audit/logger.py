import os
import sqlite3
import uuid
from datetime import datetime
from typing import Optional


class AuditLogger:
    def __init__(self, db_path: str = "audit/audit.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS distributions (
                    id          TEXT PRIMARY KEY,
                    recipient_name  TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    system_name TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    part1_status TEXT DEFAULT 'PENDING',
                    part2_status TEXT DEFAULT 'PENDING',
                    completed_at TEXT,
                    error_info  TEXT
                )
            """)

    def start_distribution(
        self,
        recipient_name: str,
        recipient_email: str,
        system_name: str,
        expiry_date: str,
    ) -> str:
        dist_id = f"DIST-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO distributions (id, recipient_name, recipient_email, system_name, created_at, expiry_date) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (dist_id, recipient_name, recipient_email, system_name, now, expiry_date),
            )
        return dist_id

    def record_part(
        self,
        dist_id: str,
        part: int,
        status: str,
        error_type: Optional[str] = None,
    ):
        col = "part1_status" if part == 1 else "part2_status"
        with self._connect() as conn:
            if error_type:
                conn.execute(
                    f"UPDATE distributions SET {col}=?, error_info=? WHERE id=?",
                    (status, error_type, dist_id),
                )
            else:
                conn.execute(
                    f"UPDATE distributions SET {col}=? WHERE id=?",
                    (status, dist_id),
                )

    def complete_distribution(self, dist_id: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "UPDATE distributions SET completed_at=? WHERE id=?",
                (now, dist_id),
            )

    def get_expiring_soon(self, within_days: int = 1) -> list:
        """Return distributions expiring within `within_days` days."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM distributions "
                "WHERE date(expiry_date) <= date('now', ? || ' days') "
                "AND date(expiry_date) >= date('now') "
                "AND completed_at IS NOT NULL",
                (str(within_days),),
            ).fetchall()
        return [dict(r) for r in rows]

    def export_report(self, output_path: str = "audit/compliance_report.csv"):
        """Export all distributions to a CSV compliance report."""
        import csv
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, recipient_name, recipient_email, system_name, "
                "created_at, expiry_date, part1_status, part2_status, completed_at, error_info "
                "FROM distributions ORDER BY created_at DESC"
            ).fetchall()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Distribution ID", "Recipient Name", "Recipient Email",
                "System", "Created At", "Expiry Date",
                "Part 1 Status", "Part 2 Status", "Completed At", "Error Info",
            ])
            for row in rows:
                writer.writerow(list(row))

        return output_path
