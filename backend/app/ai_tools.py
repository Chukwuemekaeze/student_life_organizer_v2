from __future__ import annotations
from typing import Any, Dict, List
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.journal import JournalEntry
from datetime import datetime, timedelta
from app.services.calendar import sync_calendar, create_calendar_event

# ---------- Tool Schemas (Anthropic) ----------
TOOLS: List[Dict[str, Any]] = [
    {
        "name": "list_journals",
        "description": "List the current user's journal entries (most recent first). Optionally filter by search text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search text to match in content (optional)."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "name": "create_journal",
        "description": "Create a new journal entry for the current user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"],
            "additionalProperties": False
        }
    },
    {
        "name": "list_calendar_events",
        "description": "Return upcoming calendar events for the current user for the next N days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "minimum": 1, "maximum": 60, "default": 7}
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "name": "create_calendar_event",
        "description": "Create a new calendar event for the current user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the event"},
                "start_time": {"type": "string", "description": "Start time in ISO8601 UTC format with Z suffix (e.g., 2024-08-30T14:00:00Z). MUST be a string, not a datetime object."},
                "end_time": {"type": "string", "description": "End time in ISO8601 UTC format with Z suffix (e.g., 2024-08-30T15:00:00Z). MUST be a string, not a datetime object."},
                "location": {"type": "string", "description": "Location of the event (optional)"},
                "description": {"type": "string", "description": "Description of the event (optional)"},
                "is_all_day": {"type": "boolean", "description": "Whether this is an all-day event (optional)", "default": False}
            },
            "required": ["title", "start_time", "end_time"],
            "additionalProperties": False
        }
    }
]

# ---------- Executors (run inside Flask request context) ----------

def exec_list_journals(user: User, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        q = (JournalEntry.query.filter_by(user_id=user.id)
             .order_by(JournalEntry.timestamp.desc()))
        query = args.get("query")
        if query:
            like = f"%{query}%"
            q = q.filter(JournalEntry.content.ilike(like))
        limit = int(args.get("limit") or 20)
        rows = q.limit(limit).all()
        return {
            "entries": [
                {
                    "id": r.id,
                    "content": r.content[:200],  # Trim long content
                    "created_at": r.timestamp.isoformat() if r.timestamp else None,
                    "updated_at": r.timestamp.isoformat() if r.timestamp else None,
                }
                for r in rows
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def exec_create_journal(user: User, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from app.services.metrics import log_event
        content = (args.get("content") or "").strip()
        if not content:
            return {"error": "content required"}
        row = JournalEntry(user_id=user.id, content=content)
        db.session.add(row)
        db.session.commit()
        # Log the journal creation event
        try:
            log_event("journal_create", {"id": row.id, "via": "ai_chat"})
        except Exception:
            pass  # Non-blocking, fail silently
        return {
            "id": row.id,
            "content": row.content[:200],  # Trim long content
            "created_at": row.timestamp.isoformat(),
            "updated_at": row.timestamp.isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}

def exec_list_calendar_events(user: User, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        days = int(args.get("days") or 7)
        end = datetime.utcnow() + timedelta(days=days)
        events = sync_calendar(user.id, end)
        if isinstance(events, dict) and "error" in events:
            return events
        return {"events": events}
    except Exception as e:
        return {"error": str(e)}

def exec_create_calendar_event(user: User, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        title = args.get("title", "").strip()
        start_time_raw = args.get("start_time")
        end_time_raw = args.get("end_time")
        location = args.get("location", "").strip()
        description = args.get("description", "").strip()
        is_all_day = args.get("is_all_day", False)

        # Simple string conversion for datetime inputs
        start_time = str(start_time_raw).strip() if start_time_raw else ""
        end_time = str(end_time_raw).strip() if end_time_raw else ""

        if not all([title, start_time, end_time]):
            return {"error": "title, start_time, and end_time are required"}

        # Check if user has Outlook connected first
        from app.models.oauth_token import OAuthToken
        token = OAuthToken.get_for_user(user.id, "outlook")
        if not token:
            return {
                "error": "Outlook calendar not connected. Please connect your Outlook account first by going to the Calendar page and clicking 'Connect to Outlook'.",
                "suggestion": "You can create journal entries instead, or connect your calendar to use this feature."
            }
        
        result = create_calendar_event(
            user_id=user.id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            location=location,
            description=description,
            is_all_day=is_all_day
        )
        
        # Add helpful context if there's still an error
        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"]
            if "datetime" in error_msg.lower() or "timezone" in error_msg.lower():
                result["suggestion"] = f"There was a datetime formatting issue. The times provided were: start='{start_time}', end='{end_time}'. Please try specifying exact times like '2025-08-31T14:00:00Z'."
        
        return result
    except Exception as e:
        return {"error": str(e)}

# Export the executors
EXECUTORS = {
    "list_journals": exec_list_journals,
    "create_journal": exec_create_journal,
    "list_calendar_events": exec_list_calendar_events,
    "create_calendar_event": exec_create_calendar_event,
}

# Make sure EXECUTORS is exported
__all__ = ["TOOLS", "EXECUTORS"]