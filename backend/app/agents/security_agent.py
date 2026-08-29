"""
Security & Privacy Agent.

Minimal real functionality now: structured audit logging for every
investigation query (who searched what, when). This is deliberately simple
and honest per docs/phoenix_master_prompt.md Section 1 - "no overclaiming":
this is NOT anomaly detection or access-pattern intrusion detection yet,
just a real, working audit trail, which is the credible baseline this kind
of system needs before any fancier claims are made.

Future (not yet built): suspicious-access-pattern detection (e.g. flagging
an unusually high volume of searches by one user/session in a short window).
"""
from __future__ import annotations

from datetime import datetime, timezone


class SecurityAgent:
    def __init__(self) -> None:
        # In-memory log for scaffold stage; replaced by audit_logs table
        # (see app/db/schema.sql) once Supabase is wired in.
        self._log: list[dict] = []

    def record_access(self, user_identifier: str, action: str, resource_accessed: str) -> dict:
        entry = {
            "user_identifier": user_identifier,
            "action": action,
            "resource_accessed": resource_accessed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log.append(entry)
        return entry

    def get_recent_log(self, limit: int = 50) -> list[dict]:
        return self._log[-limit:]
