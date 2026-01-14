# app/agent/tools.py
from __future__ import annotations
from typing import Any, Dict
from app.agent.guard import require_scope, audit_log
from app.extensions import db

# Import your existing services / models
from app.models.journal import JournalEntry
from app.models.task import Task
from app.models.notification import Notification
from app.models.notion import NotionNoteCache
from app.services.metrics import log_event

# Import calendar services
from app.services.calendar import sync_calendar, create_calendar_event
from app.services.outlook_tasks import graph_create_event, graph_update_event, graph_delete_event

# ---- Tool registry (names -> callables) ----
# Each tool MUST accept (user_id:int, scopes:set[str], **kwargs) and return a JSON‑serializable dict.

def t_list_journals(user_id: int, scopes: set[str], limit: int = 10, query: str | None = None, since_iso: str | None = None) -> Dict[str, Any]:
    require_scope(scopes, "journals:read")
    q = JournalEntry.query.filter_by(user_id=user_id)
    if query:
        q = q.filter(JournalEntry.content.ilike(f"%{query}%"))
    if since_iso:
        from datetime import datetime
        try:
            since = datetime.fromisoformat(since_iso.replace("Z","+00:00"))
            q = q.filter(JournalEntry.timestamp >= since)
        except Exception:  # ignore parse errors
            pass
    items = q.order_by(JournalEntry.timestamp.desc()).limit(max(1, min(limit, 50))).all()
    return {"items": [{"id": j.id, "content": j.content, "created_at": j.timestamp.isoformat()} for j in items]}


def t_create_journal(user_id: int, scopes: set[str], content: str) -> Dict[str, Any]:
    require_scope(scopes, "journals:write")
    j = JournalEntry(user_id=user_id, content=content)
    db.session.add(j)
    db.session.commit()
    log_event("journal_create", {"id": j.id})
    return {"id": j.id}


def t_delete_journal(user_id: int, scopes: set[str], id: int) -> Dict[str, Any]:
    require_scope(scopes, "journals:write")
    try:
        journal = JournalEntry.query.filter_by(id=id, user_id=user_id).first()
        if not journal:
            return {"error": "Journal entry not found or you don't have permission to delete it"}
        
        # Store info for response
        deleted_info = {
            "id": journal.id,
            "content_preview": (journal.content or "")[:100] + "..." if len(journal.content or "") > 100 else journal.content,
            "created_at": journal.timestamp.isoformat() if journal.timestamp else None
        }
        
        # Delete the journal entry
        db.session.delete(journal)
        db.session.commit()
        log_event("journal_delete", {"id": id})
        
        return {
            "success": True,
            "deleted_journal": deleted_info,
            "message": f"Successfully deleted journal entry (ID: {id})"
        }
    except Exception as e:
        return {"error": f"Failed to delete journal entry: {str(e)}"}


def t_list_tasks(user_id: int, scopes: set[str], status: str | None = None, q: str | None = None, due_before: str | None = None, due_after: str | None = None, limit: int = 20) -> Dict[str, Any]:
    require_scope(scopes, "tasks:read")
    from sqlalchemy import or_
    from datetime import datetime
    query = Task.query.filter_by(user_id=user_id)
    if status in {"todo","in_progress","done"}:
        query = query.filter(Task.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Task.title.ilike(like), Task.description.ilike(like)))
    def _dt(s):
        if not s: return None
        try: return datetime.fromisoformat(s.replace("Z","+00:00"))
        except Exception: return None
    dbefore, dafter = _dt(due_before), _dt(due_after)
    if dbefore: query = query.filter(Task.due_at != None, Task.due_at <= dbefore)
    if dafter: query = query.filter(Task.due_at != None, Task.due_at >= dafter)
    items = query.order_by(Task.due_at.is_(None), Task.due_at.asc(), Task.created_at.desc()).limit(max(1, min(limit, 50))).all()
    return {"items": [t.to_dict() for t in items]}


def t_create_task(user_id: int, scopes: set[str], title: str, description: str | None = None, priority: str = "medium", due_at: str | None = None) -> Dict[str, Any]:
    require_scope(scopes, "tasks:write")
    from datetime import datetime
    def _dt(s):
        if not s: return None
        try: return datetime.fromisoformat(s.replace("Z","+00:00"))
        except Exception: return None
    t = Task(user_id=user_id, title=title.strip()[:200], description=(description or None), priority=priority if priority in {"low","medium","high"} else "medium", status="todo", due_at=_dt(due_at), source="agent")
    db.session.add(t)
    db.session.commit()
    log_event("task_create", {"id": t.id, "priority": t.priority, "source": "agent"})
    return {"id": t.id}


def t_update_task(user_id: int, scopes: set[str], id: int, **patch) -> Dict[str, Any]:
    require_scope(scopes, "tasks:write")
    t = Task.query.filter_by(id=id, user_id=user_id).first()
    if not t: return {"error": "not_found"}
    from datetime import datetime
    if "title" in patch and patch["title"]: t.title = patch["title"].strip()[:200]
    if "description" in patch: t.description = (patch["description"] or None)
    if "priority" in patch and patch["priority"] in {"low","medium","high"}: t.priority = patch["priority"]
    if "status" in patch and patch["status"] in {"todo","in_progress","done"}:
        prev = t.status
        t.status = patch["status"]
        if prev != "done" and t.status == "done":
            from datetime import datetime
            t.completed_at = utcnow()
            log_event("task_complete", {"id": t.id})
    if "due_at" in patch:
        try: t.due_at = datetime.fromisoformat(patch["due_at"].replace("Z","+00:00")) if patch["due_at"] else None
        except Exception: pass
    db.session.commit()
    log_event("task_update", {"id": t.id})
    return {"id": t.id, "status": t.status}


def t_list_notes(user_id: int, scopes: set[str], limit: int = 10, query: str | None = None) -> Dict[str, Any]:
    require_scope(scopes, "notes:read")
    q = NotionNoteCache.query.filter_by(user_id=user_id)
    if query:
        # Search in both title and content
        q = q.filter(
            db.or_(
                NotionNoteCache.title.ilike(f"%{query}%"),
                NotionNoteCache.content.ilike(f"%{query}%")
            )
        )
    rows = q.order_by(NotionNoteCache.last_edited_time.desc()).limit(max(1, min(limit, 20))).all()
    notes = [{
        "page_id": r.page_id,
        "title": r.title,
        "url": r.url,
        "content": r.content,
        "last_edited_time": r.last_edited_time.isoformat() if r.last_edited_time else None,
    } for r in rows]
    return {"items": notes}

def t_delete_note(user_id: int, scopes: set[str], page_id: str) -> Dict[str, Any]:
    require_scope(scopes, "notes:write")
    from app.models.notion import NotionNoteCache, NotionLink
    from app.services.notion_client import NotionClient, NotionAuthError, NotionAPIError
    from app.services.metrics import log_event
    
    # Check if user has Notion connection
    link = NotionLink.query.filter_by(user_id=user_id).first()
    if not link:
        return {"error": "Not connected to Notion"}
    
    # Check if the note belongs to this user
    note = NotionNoteCache.query.filter_by(page_id=page_id, user_id=user_id).first()
    if not note:
        return {"error": "Note not found or access denied"}
    
    try:
        # Delete from Notion
        client = NotionClient(link.access_token)
        client.delete_page(page_id)
        
        # Delete from local cache
        db.session.delete(note)
        db.session.commit()
        
        # Log the deletion event
        try:
            log_event("note_delete", {"page_id": page_id, "title": note.title, "via": "agent_chat"})
        except Exception:
            pass  # Non-blocking, fail silently
        
        return {
            "success": True,
            "message": f"Note '{note.title}' deleted successfully from both SLO and Notion",
            "page_id": page_id,
            "title": note.title
        }
        
    except NotionAuthError as e:
        return {"error": f"Notion authentication error: {str(e)}"}
    except NotionAPIError as e:
        return {"error": f"Notion API error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

# Calendar tools (list/create/update/delete) — reuse your Outlook helpers

def t_calendar_list(user_id: int, scopes: set[str], range_days: int = 7) -> Dict[str, Any]:
    require_scope(scopes, "calendar:read")
    from datetime import datetime, timedelta
    try:
        end_dt = utcnow() + timedelta(days=range_days)
        events = sync_calendar(user_id=user_id, end_dt=end_dt)
        
        # Handle error cases from sync_calendar
        if isinstance(events, dict) and "error" in events:
            error_msg = events["error"]
            if "No valid Outlook token" in error_msg:
                return {"items": [], "message": "Calendar access not configured. Please connect your Outlook account to view calendar events."}
            return {"items": [], "error": error_msg}
        
        # Handle successful response
        if isinstance(events, list):
            return {"items": events}
        
        # Fallback for unexpected response format
        return {"items": [], "message": "Unable to fetch calendar events at this time."}
        
    except Exception as e:
        return {"items": [], "error": f"Calendar service error: {str(e)}"}


def t_calendar_create(user_id: int, scopes: set[str], subject: str, start_iso: str, end_iso: str, body: str | None = None) -> Dict[str, Any]:
    require_scope(scopes, "calendar:write")
    try:
        result = create_calendar_event(
            user_id=user_id,
            title=subject[:120],
            start_time=start_iso,
            end_time=end_iso,
            description=body or ""
        )
        if "error" in result:
            return result
        return {"event_id": result.get("id")}
    except Exception as e:
        return {"error": str(e)}


def t_calendar_update(user_id: int, scopes: set[str], event_id: str, subject: str | None = None, start_iso: str | None = None, end_iso: str | None = None, body: str | None = None) -> Dict[str, Any]:
    require_scope(scopes, "calendar:write")
    patch = {}
    if subject: patch["subject"] = subject[:120]
    if body is not None: patch["body"] = {"contentType": "Text", "content": body}
    if start_iso: patch["start"] = {"dateTime": start_iso, "timeZone": "UTC"}
    if end_iso: patch["end"] = {"dateTime": end_iso, "timeZone": "UTC"}
    try:
        graph_update_event(user_id, event_id, patch)
        return {"event_id": event_id}
    except Exception as e:
        return {"error": str(e)}


def t_calendar_delete(user_id: int, scopes: set[str], event_id: str) -> Dict[str, Any]:
    require_scope(scopes, "calendar:write")
    try:
        # Validate event_id is provided
        if not event_id or not event_id.strip():
            return {"error": "Event ID is required for deletion"}
        
        # Attempt to delete the event
        result = graph_delete_event(user_id, event_id.strip())
        
        # Check if graph_delete_event returned an error dict
        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"]
            if "No valid Outlook token" in error_msg:
                return {"error": "Calendar access not configured. Please connect your Outlook account to manage calendar events."}
            if "not found" in error_msg.lower() or "404" in error_msg:
                return {"error": "Event not found. It may have already been deleted."}
            return {"error": error_msg}
        
        return {"event_id": event_id, "deleted": True, "message": "Event successfully deleted"}
        
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "not found" in error_str.lower():
            return {"error": "Event not found. It may have already been deleted."}
        if "401" in error_str or "unauthorized" in error_str.lower():
            return {"error": "Calendar access unauthorized. Please reconnect your Outlook account."}
        return {"error": f"Failed to delete event: {error_str}"}

# Notifications

def t_notifications_unread(user_id: int, scopes: set[str]) -> Dict[str, Any]:
    require_scope(scopes, "notifications:read")
    items = Notification.query.filter_by(user_id=user_id).filter(Notification.read_at == None).order_by(Notification.created_at.desc()).limit(20).all()  # noqa: E711
    return {"items": [n.to_dict() for n in items]}

TOOL_REGISTRY = {
    "get_journals": t_list_journals,
    "create_journal": t_create_journal,
    "delete_journal": t_delete_journal,
    "list_tasks": t_list_tasks,
    "create_task": t_create_task,
    "update_task": t_update_task,
    "list_notes": t_list_notes,
    "delete_note": t_delete_note,
    "calendar_list": t_calendar_list,
    "calendar_create_event": t_calendar_create,
    "calendar_update_event": t_calendar_update,
    "calendar_delete_event": t_calendar_delete,
    "notifications_unread": t_notifications_unread,
}

# JSON Schemas (sent to the model)
TOOL_SCHEMAS = [
    {"name": "get_journals", "description": "Fetch local journal entries (written directly in SLO app). Use this when user specifically mentions 'journal', 'journal entry', or personal reflections. NOT for Notion notes.", "input_schema": {"type": "object", "properties": {"limit": {"type": "integer"}, "query": {"type": "string"}, "since_iso": {"type": "string"}}, "required": []}},
    {"name": "create_journal", "description": "Create a new journal entry.", "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}},
    {"name": "delete_journal", "description": "Delete a journal entry by ID. Use this when user confirms deletion.", "input_schema": {"type": "object", "properties": {"id": {"type": "integer", "description": "Journal entry ID to delete"}}, "required": ["id"]}},
    {"name": "list_tasks", "description": "List tasks with filters.", "input_schema": {"type": "object", "properties": {"status": {"type": "string"}, "q": {"type": "string"}, "due_before": {"type": "string"}, "due_after": {"type": "string"}, "limit": {"type": "integer"}}, "required": []}},
    {"name": "create_task", "description": "Create a task.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}, "due_at": {"type": "string"}}, "required": ["title"]}},
    {"name": "update_task", "description": "Update a task.", "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}, "status": {"type": "string"}, "due_at": {"type": "string"}}, "required": ["id"]}},
    {"name": "list_notes", "description": "Search and list Notion notes (synced from user's Notion workspace). Use this when user asks about 'notes', 'my note about X', class notes, etc. NOT for journal entries.", "input_schema": {"type": "object", "properties": {"limit": {"type": "integer"}, "query": {"type": "string", "description": "Search query to find specific notes by title"}}, "required": []}},
    {"name": "delete_note", "description": "Delete a Notion note from both SLO and Notion workspace. Use when user wants to delete a specific note.", "input_schema": {"type": "object", "properties": {"page_id": {"type": "string", "description": "The page_id of the note to delete"}}, "required": ["page_id"]}},
    {"name": "calendar_list", "description": "List calendar events for next N days. Returns empty list with helpful message if calendar not connected.", "input_schema": {"type": "object", "properties": {"range_days": {"type": "integer", "description": "Number of days to look ahead (default: 7)"}}, "required": []}},
    {"name": "calendar_create_event", "description": "Create a new calendar event. Requires Outlook calendar connection.", "input_schema": {"type": "object", "properties": {"subject": {"type": "string", "description": "Event title/subject"}, "start_iso": {"type": "string", "description": "Start time in ISO format"}, "end_iso": {"type": "string", "description": "End time in ISO format"}, "body": {"type": "string", "description": "Event description (optional)"}}, "required": ["subject","start_iso","end_iso"]}},
    {"name": "calendar_update_event", "description": "Update an existing calendar event. Requires event ID and Outlook connection.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string", "description": "Unique event identifier"}, "subject": {"type": "string", "description": "New event title"}, "start_iso": {"type": "string", "description": "New start time"}, "end_iso": {"type": "string", "description": "New end time"}, "body": {"type": "string", "description": "New event description"}}, "required": ["event_id"]}},
    {"name": "calendar_delete_event", "description": "Delete a calendar event by ID. Provides helpful error messages if event not found.", "input_schema": {"type": "object", "properties": {"event_id": {"type": "string", "description": "Unique event identifier to delete"}}, "required": ["event_id"]}},
    {"name": "notifications_unread", "description": "Fetch unread notifications.", "input_schema": {"type": "object", "properties": {} , "required": []}},
]

