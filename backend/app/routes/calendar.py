from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
import os, requests
from app.models.oauth_token import OAuthToken
from app.extensions import db
from app.services.metrics import log_event

calendar_bp = Blueprint("calendar_bp", __name__, url_prefix="/api/calendar")
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def utcnow():
    return datetime.now(timezone.utc)

def ensure_token(token: OAuthToken):
    if token and token.expiry:
        # Make sure token.expiry is timezone-aware
        expiry = token.expiry if token.expiry.tzinfo else token.expiry.replace(tzinfo=timezone.utc)
        if expiry > utcnow() + timedelta(seconds=30):
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
        token.expiry = utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return token.access_token
    except Exception as e:
        print(f"Exception during token refresh: {e}")
        return None

@calendar_bp.get("/sync")
@jwt_required()
def sync_calendar():
    user_id = int(get_jwt_identity())
    tok = OAuthToken.get_for_user(user_id, "outlook")
    if not tok:
        return jsonify({"msg": "Outlook not connected. Start at /api/calendar/outlook/start"}), 400
    access = ensure_token(tok)
    if not access:
        # Check if environment variables are missing
        client_id = os.getenv("OUTLOOK_CLIENT_ID")
        client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
        redirect_uri = os.getenv("OUTLOOK_REDIRECT_URI")
        
        if not client_id or not client_secret or not redirect_uri:
            return jsonify({
                "msg": "Outlook integration not properly configured. Missing environment variables.",
                "error": "MISSING_CONFIG",
                "details": {
                    "client_id": bool(client_id),
                    "client_secret": bool(client_secret),
                    "redirect_uri": bool(redirect_uri)
                }
            }), 500
        
        return jsonify({"msg": "Failed to refresh Outlook access token. Please reconnect your account."}), 401

    # Next 7 days window
    start = utcnow()
    end = start + timedelta(days=7)
    # ISO8601 format with Z
    tmin = start.isoformat().replace("+00:00", "Z")
    tmax = end.isoformat().replace("+00:00", "Z")

    url = f"{GRAPH_BASE}/me/calendarView"
    params = {"startDateTime": tmin, "endDateTime": tmax, "$orderby": "start/dateTime"}
    headers = {"Authorization": f"Bearer {access}"}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 401:
            access = ensure_token(tok)
            if not access:
                return jsonify({"msg": "Failed to refresh token after 401. Please reconnect your Outlook account."}), 401
            r = requests.get(url, headers={"Authorization": f"Bearer {access}"}, params=params, timeout=20)
        
        if r.status_code != 200:
            error_msg = f"Microsoft Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Microsoft Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            
            return jsonify({
                "msg": error_msg,
                "status": r.status_code,
                "error": r.text[:500] if r.text else "No error details"
            }), 502

    except requests.exceptions.RequestException as e:
        return jsonify({
            "msg": f"Network error when calling Microsoft Graph API: {str(e)}",
            "error": "NETWORK_ERROR"
        }), 502
    except Exception as e:
        return jsonify({
            "msg": f"Unexpected error: {str(e)}",
            "error": "UNEXPECTED_ERROR"
        }), 500

    data = r.json().get("value", [])
    def norm(e):
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date")
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date")
        return {
            "id": e.get("id"),
            "title": e.get("subject") or "(no title)",
            "start_time": start,
            "end_time": end,
            "status": e.get("showAs"),
            "html_link": e.get("webLink"),
            "location": e.get("location", {}).get("displayName"),
            "description": e.get("bodyPreview"),
            "is_all_day": e.get("isAllDay", False),
        }
    events = [norm(e) for e in data]
    # Log the calendar sync event
    try:
        log_event("calendar_sync", {"count": len(events)})
    except Exception:
        pass  # Non-blocking, fail silently
    return jsonify({"events": events, "count": len(events)})

@calendar_bp.post("/events")
@jwt_required()
def create_event():
    user_id = int(get_jwt_identity())
    tok = OAuthToken.get_for_user(user_id, "outlook")
    if not tok:
        return jsonify({"msg": "Outlook not connected. Please connect your Outlook account first."}), 400
    
    access = ensure_token(tok)
    if not access:
        # Check if environment variables are missing
        client_id = os.getenv("OUTLOOK_CLIENT_ID")
        client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
        redirect_uri = os.getenv("OUTLOOK_REDIRECT_URI")
        
        if not client_id or not client_secret or not redirect_uri:
            return jsonify({
                "msg": "Outlook integration not properly configured. Missing environment variables.",
                "error": "MISSING_CONFIG",
                "details": {
                    "client_id": bool(client_id),
                    "client_secret": bool(client_secret),
                    "redirect_uri": bool(redirect_uri)
                }
            }), 500
        
        return jsonify({"msg": "Failed to refresh Outlook access token. Please reconnect your account."}), 401

    data = request.get_json() or {}
    title = data.get("title", "").strip()
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    
    if not all([title, start_time, end_time]):
        return jsonify({"msg": "title, start_time, and end_time are required"}), 400

    # Create event payload for Microsoft Graph
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
        "isAllDay": data.get("is_all_day", False),
        "location": {
            "displayName": data.get("location", "")
        },
        "body": {
            "contentType": "text",
            "content": data.get("description", "")
        }
    }

    url = f"{GRAPH_BASE}/me/events"
    headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=event_data, headers=headers, timeout=20)
        if r.status_code == 401:
            access = ensure_token(tok)
            if not access:
                return jsonify({"msg": "Failed to refresh token after 401. Please reconnect your Outlook account."}), 401
            r = requests.post(url, json=event_data, headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"}, timeout=20)
        
        if r.status_code not in [200, 201]:
            error_msg = f"Microsoft Graph API error: {r.status_code}"
            try:
                error_data = r.json()
                if "error" in error_data:
                    error_msg = f"Microsoft Graph API error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            
            return jsonify({
                "msg": error_msg,
                "status": r.status_code,
                "error": r.text[:500] if r.text else "No error details"
            }), 502

        created_event = r.json()
        return jsonify({
            "id": created_event.get("id"),
            "title": created_event.get("subject"),
            "start_time": created_event.get("start", {}).get("dateTime"),
            "end_time": created_event.get("end", {}).get("dateTime"),
            "status": created_event.get("showAs"),
            "html_link": created_event.get("webLink"),
            "location": created_event.get("location", {}).get("displayName"),
            "description": created_event.get("bodyPreview"),
            "is_all_day": created_event.get("isAllDay", False),
        }), 201
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "msg": f"Network error when calling Microsoft Graph API: {str(e)}",
            "error": "NETWORK_ERROR"
        }), 502
    except Exception as e:
        return jsonify({
            "msg": f"Unexpected error: {str(e)}",
            "error": "UNEXPECTED_ERROR"
        }), 500

@calendar_bp.put("/events/<event_id>")
@jwt_required()
def update_event(event_id):
    user_id = int(get_jwt_identity())
    tok = OAuthToken.get_for_user(user_id, "outlook")
    if not tok:
        return jsonify({"msg": "Outlook not connected"}), 400
    access = ensure_token(tok)
    if not access:
        return jsonify({"msg": "token refresh failed"}), 401

    data = request.get_json() or {}
    
    # Build update payload (only include fields that are provided)
    update_data = {}
    if "title" in data:
        update_data["subject"] = data["title"].strip()
    if "start_time" in data:
        update_data["start"] = {"dateTime": data["start_time"], "timeZone": "UTC"}
    if "end_time" in data:
        update_data["end"] = {"dateTime": data["end_time"], "timeZone": "UTC"}
    if "location" in data:
        update_data["location"] = {"displayName": data["location"]}
    if "description" in data:
        update_data["body"] = {"contentType": "text", "content": data["description"]}
    if "is_all_day" in data:
        update_data["isAllDay"] = data["is_all_day"]

    if not update_data:
        return jsonify({"msg": "no fields to update"}), 400

    url = f"{GRAPH_BASE}/me/events/{event_id}"
    headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
    
    r = requests.patch(url, json=update_data, headers=headers, timeout=20)
    if r.status_code == 401:
        access = ensure_token(tok)
        if not access:
            return jsonify({"msg": "unauthorized from outlook"}), 401
        r = requests.patch(url, json=update_data, headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"}, timeout=20)
    
    if r.status_code != 200:
        return jsonify({"msg": "failed to update event", "status": r.status_code, "error": r.text}), 502

    updated_event = r.json()
    return jsonify({
        "id": updated_event.get("id"),
        "title": updated_event.get("subject"),
        "start_time": updated_event.get("start", {}).get("dateTime"),
        "end_time": updated_event.get("end", {}).get("dateTime"),
        "status": updated_event.get("showAs"),
        "html_link": updated_event.get("webLink"),
        "location": updated_event.get("location", {}).get("displayName"),
        "description": updated_event.get("bodyPreview"),
        "is_all_day": updated_event.get("isAllDay", False),
    })

@calendar_bp.delete("/events/<event_id>")
@jwt_required()
def delete_event(event_id):
    user_id = int(get_jwt_identity())
    tok = OAuthToken.get_for_user(user_id, "outlook")
    if not tok:
        return jsonify({"msg": "Outlook not connected"}), 400
    access = ensure_token(tok)
    if not access:
        return jsonify({"msg": "token refresh failed"}), 401

    url = f"{GRAPH_BASE}/me/events/{event_id}"
    headers = {"Authorization": f"Bearer {access}"}
    
    r = requests.delete(url, headers=headers, timeout=20)
    if r.status_code == 401:
        access = ensure_token(tok)
        if not access:
            return jsonify({"msg": "unauthorized from outlook"}), 401
        r = requests.delete(url, headers={"Authorization": f"Bearer {access}"}, timeout=20)
    
    if r.status_code not in [200, 204]:
        return jsonify({"msg": "failed to delete event", "status": r.status_code, "error": r.text}), 502

    return jsonify({"msg": "Event deleted successfully"}), 200
