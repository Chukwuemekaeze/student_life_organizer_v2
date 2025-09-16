from __future__ import annotations
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

import requests
from sqlalchemy import func

from app.extensions import db
from app.models.usage_log import UsageLog
from app.models.journal import JournalEntry  # adjust import if your model path differs
from app.models.notion import NotionNoteCache  # optional: to surface recent note titles

ANTHROPIC_BASE = os.getenv("ANTHROPIC_BASE", "https://api.anthropic.com")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

HEADERS = {
    "x-api-key": ANTHROPIC_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}


class ReflectionConfig:
    window_days: int = 7
    max_recent_notes: int = 10
    max_recent_journals: int = 10


def _weekly_usage_totals(user_id: int, since: datetime) -> Dict[str, int]:
    # Tally by event_type from UsageLog
    rows = (
        db.session.query(UsageLog.event_type, func.count(UsageLog.id))
        .filter(UsageLog.user_id == user_id, UsageLog.created_at >= since)
        .group_by(UsageLog.event_type)
        .all()
    )
    out = {k: int(v) for k, v in rows}
    # Normalize expected keys
    for key in ("journal_create", "chat_query", "calendar_sync", "notes_sync"):
        out.setdefault(key, 0)
    return out


def _recent_note_titles(user_id: int, limit: int) -> List[str]:
    try:
        q = (
            db.session.query(NotionNoteCache)
            .filter(NotionNoteCache.user_id == user_id)
            .order_by(NotionNoteCache.last_edited_time.desc())
            .limit(limit)
        )
        titles = [r.title or "Untitled" for r in q.all()]
        return titles
    except Exception:
        return []


def _recent_journal_snippets(user_id: int, limit: int) -> List[str]:
    try:
        q = (
            db.session.query(JournalEntry)
            .filter(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.timestamp.desc())
            .limit(limit)
        )
        # keep it short for prompt budget
        def trim(s: str, n: int = 180) -> str:
            s = s or ""
            return s[:n] + ("…" if len(s) > n else "")
        return [trim(r.content or "") for r in q.all() if (r.content or "").strip()]
    except Exception:
        return []


def build_reflection_prompt(payload: Dict[str, Any]) -> str:
    # payload keys: week_range, totals, streaks, notes, journals, user_goals (optional)
    week = payload.get("week_range", {})
    totals = payload.get("totals", {})
    streaks = payload.get("streaks", {})
    notes = payload.get("notes", [])
    journals = payload.get("journals", [])
    goals = payload.get("user_goals", "")

    lines = []
    lines.append("You are an academic coach for a university student. Be concise and practical.")
    lines.append("Summarize their past week and give 3 reflection prompts plus 3 specific actions for next week.")
    if goals:
        lines.append(f"Student goals: {goals}")
    lines.append("")
    lines.append(f"Week window: {week.get('from')} → {week.get('to')}")
    lines.append("Activity totals (last 7 days):")
    lines.append(json.dumps(totals, ensure_ascii=False))
    lines.append("")
    if streaks:
        lines.append(f"Journal streaks — current: {streaks.get('current',0)}, best: {streaks.get('best',0)}")
    if notes:
        lines.append("Recent note titles:")
        for t in notes[:10]:
            lines.append(f"- {t}")
    if journals:
        lines.append("Recent journal snippets:")
        for s in journals[:10]:
            lines.append(f"- {s}")

    lines.append("")
    lines.append("Output JSON with keys: summary, prompts (array), actions (array). Keep it short.")

    return "\n".join(lines)


def call_claude(prompt: str, temperature: float = 0.2, max_tokens: int = 700) -> Dict[str, Any]:
    if not ANTHROPIC_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    resp = requests.post(
        f"{ANTHROPIC_BASE}/v1/messages",
        headers=HEADERS,
        data=json.dumps(data),
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Claude API error: {resp.status_code}: {resp.text}")
    out = resp.json()
    # Anthropic returns list of content blocks; combine text
    try:
        blocks = out.get("content", [])
        text = "".join([b.get("text", "") for b in blocks if b.get("type") == "text"]) or json.dumps(out)
        # Try to parse JSON if model followed instruction; be forgiving
        try:
            return json.loads(text)
        except Exception:
            return {"summary": text, "prompts": [], "actions": []}
    except Exception:
        return {"summary": str(out), "prompts": [], "actions": []}


def generate_reflection(user_id: int, user_goals: str | None = None) -> Dict[str, Any]:
    cfg = ReflectionConfig()
    now = datetime.utcnow()
    since = now - timedelta(days=cfg.window_days)

    totals = _weekly_usage_totals(user_id, since)

    # streaks from journals — compute quickly using SQLite-compatible date functions
    rows = (
        db.session.query(func.date(JournalEntry.timestamp))
        .filter(JournalEntry.user_id == user_id)
        .group_by(func.date(JournalEntry.timestamp))
        .order_by(func.date(JournalEntry.timestamp))
        .all()
    )
    
    if not rows:
        streaks = {"current": 0, "best": 0}
    else:
        # Convert date strings to date objects
        days = [datetime.strptime(r[0], '%Y-%m-%d').date() for r in rows]
        
        # Calculate best streak
        best = cur = 1
        for i in range(1, len(days)):
            if (days[i] - days[i - 1]).days == 1:
                cur += 1
            else:
                best = max(best, cur)
                cur = 1
        best = max(best, cur)
        
        # Calculate current streak counting back from today
        from datetime import date, timedelta as td
        today = date.today()
        s = set(days)
        current = 0
        d = today
        while d in s:
            current += 1
            d = d - td(days=1)
        
        streaks = {"current": current, "best": int(best)}

    notes = _recent_note_titles(user_id, cfg.max_recent_notes)
    journals = _recent_journal_snippets(user_id, cfg.max_recent_journals)

    payload = {
        "week_range": {"from": since.isoformat(), "to": now.isoformat()},
        "totals": totals,
        "streaks": streaks,
        "notes": notes,
        "journals": journals,
        "user_goals": (user_goals or "").strip(),
    }

    prompt = build_reflection_prompt(payload)
    result = call_claude(prompt)
    return {
        "prompt": prompt,
        "result": result,
    }
