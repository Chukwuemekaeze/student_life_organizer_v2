# app/services/outlook_tasks.py
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import requests

from app.models.task import Task
from app.models.oauth_token import OAuthToken

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def ensure_token(token: OAuthToken) -> str | None:
    """Refresh token if needed and return access token."""
    # Import the existing function from calendar service
    from app.services.calendar import ensure_token as calendar_ensure_token
    return calendar_ensure_token(token)

def _iso(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def _event_payload_from_task(t: Task) -> Dict[str, Any]:
    subject = f"[Task] {t.title}"
    body = (t.description or "")[:8000]
    start = t.due_at or t.created_at
    end = t.due_at or t.created_at
    start_iso, end_iso = _iso(start), _iso(end)
    return {
        "subject": subject,
        "body": {"contentType": "Text", "content": body or " "},
        "start": {"dateTime": start_iso, "timeZone": "UTC"},
        "end": {"dateTime": end_iso, "timeZone": "UTC"},
        "isReminderOn": False,
        "importance": "high" if t.priority == "high" else "normal",
    }

def graph_create_event(user_id: int, payload: Dict[str, Any]) -> Optional[str]:
    """Create an event in Outlook calendar and return event ID."""
    token = OAuthToken.get_for_user(user_id, "outlook")
    if not token:
        raise Exception("No valid Outlook token")
    
    access_token = ensure_token(token)
    if not access_token:
        raise Exception("Failed to refresh token")

    url = f"{GRAPH_BASE}/me/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        if r.status_code == 401:
            access_token = ensure_token(token)
            if not access_token:
                raise Exception("Failed to refresh token after 401")
            headers["Authorization"] = f"Bearer {access_token}"
            r = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if r.status_code not in [200, 201]:
            error_msg = f"Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            raise Exception(error_msg)

        created_event = r.json()
        return created_event.get("id")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error when calling Microsoft Graph API: {str(e)}")

def graph_update_event(user_id: int, event_id: str, payload: Dict[str, Any]) -> None:
    """Update an existing event in Outlook calendar."""
    token = OAuthToken.get_for_user(user_id, "outlook")
    if not token:
        raise Exception("No valid Outlook token")
    
    access_token = ensure_token(token)
    if not access_token:
        raise Exception("Failed to refresh token")

    url = f"{GRAPH_BASE}/me/events/{event_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.patch(url, json=payload, headers=headers, timeout=20)
        if r.status_code == 401:
            access_token = ensure_token(token)
            if not access_token:
                raise Exception("Failed to refresh token after 401")
            headers["Authorization"] = f"Bearer {access_token}"
            r = requests.patch(url, json=payload, headers=headers, timeout=20)
        
        if r.status_code not in [200, 201]:
            error_msg = f"Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error when calling Microsoft Graph API: {str(e)}")

def graph_delete_event(user_id: int, event_id: str) -> None:
    """Delete an event from Outlook calendar."""
    token = OAuthToken.get_for_user(user_id, "outlook")
    if not token:
        raise Exception("No valid Outlook token")
    
    access_token = ensure_token(token)
    if not access_token:
        raise Exception("Failed to refresh token")

    url = f"{GRAPH_BASE}/me/events/{event_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.delete(url, headers=headers, timeout=20)
        if r.status_code == 401:
            access_token = ensure_token(token)
            if not access_token:
                raise Exception("Failed to refresh token after 401")
            headers["Authorization"] = f"Bearer {access_token}"
            r = requests.delete(url, headers=headers, timeout=20)
        
        if r.status_code not in [200, 204]:
            error_msg = f"Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error when calling Microsoft Graph API: {str(e)}")

def ensure_task_event(user_id: int, t: Task) -> Optional[str]:
    if not t.due_at:
        return t.outlook_event_id
    payload = _event_payload_from_task(t)
    if t.outlook_event_id:
        try:
            graph_update_event(user_id, t.outlook_event_id, payload)
            return t.outlook_event_id
        except Exception:
            pass
    eid = graph_create_event(user_id, payload)
    return eid

def delete_task_event(user_id: int, t: Task) -> None:
    if t.outlook_event_id:
        try:
            graph_delete_event(user_id, t.outlook_event_id)
        except Exception:
            pass
