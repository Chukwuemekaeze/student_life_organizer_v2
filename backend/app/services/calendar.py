from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.models.oauth_token import OAuthToken
import requests
import os

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def ensure_token(token: OAuthToken) -> str | None:
    """Refresh token if needed and return access token."""
    if token and token.expiry:
        # Make sure token.expiry is timezone-aware
        expiry = token.expiry if token.expiry.tzinfo else token.expiry.replace(tzinfo=timezone.utc)
        if expiry > datetime.now(timezone.utc) + timedelta(seconds=30):
            return token.access_token

    # refresh
    client_id = os.getenv("OUTLOOK_CLIENT_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    redirect_uri = os.getenv("OUTLOOK_REDIRECT_URI")
    
    if not client_id or not client_secret or not redirect_uri:
        print(f"Missing environment variables: CLIENT_ID={bool(client_id)}, CLIENT_SECRET={bool(client_secret)}, REDIRECT_URI={bool(redirect_uri)}")
        return None
        
    if not token or not token.refresh_token:
        print("Missing token or refresh_token")
        return None
        
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "scope": "offline_access Calendars.ReadWrite",
        "redirect_uri": redirect_uri,
    }
    
    try:
        r = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data, timeout=20)
        if r.status_code != 200:
            print(f"Token refresh failed with status {r.status_code}: {r.text}")
            return None
        j = r.json()
        token.access_token = j.get("access_token")
        token.refresh_token = j.get("refresh_token", token.refresh_token)
        expires_in = int(j.get("expires_in", 0))
        token.expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        db.session.commit()
        return token.access_token
    except Exception as e:
        print(f"Exception during token refresh: {e}")
        return None

def sync_calendar(user_id: int, end_dt: datetime | None = None) -> List[Dict[str, Any]]:
    """Return upcoming events for user up to end_dt."""
    token = OAuthToken.get_for_user(user_id, "outlook")
    if not token or not token.access_token:
        return {"error": "No valid Outlook token"}
        
    # Get events from now until end_dt
    start = datetime.utcnow()
    end = end_dt or (start + timedelta(days=7))
    
    url = f"{GRAPH_BASE}/me/calendar/events"
    params = {
        "$select": "id,subject,start,end,webLink,status,location,bodyPreview,isAllDay",
        "$filter": f"start/dateTime ge '{start.isoformat()}Z' and end/dateTime le '{end.isoformat()}Z'",
        "$orderby": "start/dateTime",
        "$top": 50,  # Limit results
    }
    headers = {"Authorization": f"Bearer {token.access_token}"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return {"error": f"Graph API error: {resp.status_code}"}
            
        data = resp.json()
        events = []
        
        for evt in data.get("value", []):
            events.append({
                "id": evt["id"],
                "title": evt["subject"],
                "start_time": evt["start"]["dateTime"],
                "end_time": evt["end"]["dateTime"],
                "status": evt.get("showAs", "busy"),
                "html_link": evt.get("webLink"),
                "location": evt.get("location", {}).get("displayName", ""),
                "description": evt.get("bodyPreview", ""),
                "is_all_day": evt.get("isAllDay", False),
            })
        
        return events
    except Exception as e:
        return {"error": str(e)}

def create_calendar_event(user_id: int, title: str, start_time: str, end_time: str, location: str = "", description: str = "", is_all_day: bool = False) -> Dict[str, Any]:
    """Create a new calendar event."""
    token = OAuthToken.get_for_user(user_id, "outlook")
    if not token:
        return {"error": "No valid Outlook token"}
    
    access_token = ensure_token(token)
    if not access_token:
        return {"error": "Failed to refresh token"}

    event_data = {
        "subject": title,
        "start": {
            "dateTime": start_time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "UTC"
        },
        "isAllDay": is_all_day,
        "location": {
            "displayName": location
        },
        "body": {
            "contentType": "text",
            "content": description
        }
    }

    url = f"{GRAPH_BASE}/me/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(url, json=event_data, headers=headers, timeout=20)
        if r.status_code == 401:
            access_token = ensure_token(token)
            if not access_token:
                return {"error": "Failed to refresh token after 401"}
            headers["Authorization"] = f"Bearer {access_token}"
            r = requests.post(url, json=event_data, headers=headers, timeout=20)
        
        if r.status_code not in [200, 201]:
            error_msg = f"Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            return {"error": error_msg}

        created_event = r.json()
        return {
            "id": created_event.get("id"),
            "title": created_event.get("subject"),
            "start_time": created_event.get("start", {}).get("dateTime"),
            "end_time": created_event.get("end", {}).get("dateTime"),
            "status": created_event.get("showAs"),
            "html_link": created_event.get("webLink"),
            "location": created_event.get("location", {}).get("displayName"),
            "description": created_event.get("bodyPreview"),
            "is_all_day": created_event.get("isAllDay", False),
        }
    except Exception as e:
        return {"error": str(e)}