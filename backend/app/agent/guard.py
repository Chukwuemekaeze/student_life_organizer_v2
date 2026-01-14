# app/agent/guard.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any
from app.extensions import db

# Simple in‑memory rate limiter (per process). Replace with Redis if needed.
_rate: Dict[str, list[datetime]] = {}

SCOPES_ALL = {
    "journals:read", "journals:write",
    "tasks:read", "tasks:write",
    "notes:read",
    "calendar:read", "calendar:write",
    "notifications:read", "notifications:write",
    "analytics:read",
}

@dataclass
class AgentPolicy:
    max_tool_calls: int = 12
    max_writes_per_turn: int = 5
    require_confirm_threshold: int = 2  # if >2 writes, ask confirm unless disabled


def user_scopes(user_id: int) -> set[str]:
    # MVP: grant full access; later, fetch from user prefs/roles
    return set(SCOPES_ALL)


def require_scope(scopes: set[str], needed: str):
    if needed not in scopes:
        raise PermissionError(f"scope_denied:{needed}")


def rate_limit(key: str, max_calls: int = 30, per_seconds: int = 60) -> None:
    now = datetime.utcnow()
    buf = _rate.setdefault(key, [])
    window = now - timedelta(seconds=per_seconds)
    while buf and buf[0] < window:
        buf.pop(0)
    if len(buf) >= max_calls:
        raise RuntimeError("rate_limited")
    buf.append(now)


def audit_log(user_id: int, tool: str, params: Dict[str, Any], result: Dict[str, Any] | None, error: str | None = None) -> None:
    # Minimal: print; you already log analytics elsewhere. You can persist in DB if needed.
    print({
        "ts": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "tool": tool,
        "params": params,
        "error": error,
        "ok": error is None,
    })

