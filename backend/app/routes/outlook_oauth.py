# backend/app/routes/outlook_oauth.py
from flask import Blueprint, request, jsonify, session, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
import os, uuid, requests
from app.extensions import db
from app.models.oauth_token import OAuthToken

outlook_bp = Blueprint("outlook_oauth", __name__, url_prefix="/api/calendar/outlook")

AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
SCOPES = "offline_access Calendars.ReadWrite"

def utcnow():
    return datetime.now(timezone.utc)

@outlook_bp.get("/start")
@jwt_required()
def start():
    client_id = os.getenv("OUTLOOK_CLIENT_ID")
    redirect_uri = os.getenv("OUTLOOK_REDIRECT_URI")
    if not client_id or not redirect_uri:
        return jsonify({"msg": "outlook oauth env not set"}), 500
    
    # Create a state that includes the user_id
    user_id = get_jwt_identity()
    # Create a combined state that includes user_id and a random UUID
    raw_state = f"{user_id}:{uuid.uuid4()}"
    # Store the raw state in session as backup
    session["oauth_state"] = raw_state
    # Base64 encode the state to make it URL-safe
    import base64
    encoded_state = base64.urlsafe_b64encode(raw_state.encode()).decode()
    
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": SCOPES,
        "state": encoded_state,
    }
    # Return URL so frontend can open it
    from urllib.parse import urlencode
    return jsonify({"auth_url": f"{AUTH_URL}?{urlencode(params)}"})

@outlook_bp.get("/callback")
def callback():
    state = request.args.get("state")
    if not state:
        return jsonify({"msg": "missing state parameter"}), 400
    
    try:
        # Decode the state parameter
        import base64
        decoded_state = base64.urlsafe_b64decode(state.encode()).decode()
        user_id, _ = decoded_state.split(":", 1)
        user_id = int(user_id)
        
        # Verify against session if available
        stored_state = session.get("oauth_state")
        if stored_state and stored_state != decoded_state:
            return jsonify({"msg": "state mismatch"}), 400
            
    except Exception as e:
        print(f"State decode error: {e}")
        return jsonify({"msg": "invalid state format"}), 400
    
    code = request.args.get("code")
    if not code:
        return jsonify({"msg": "missing code"}), 400

    client_id = os.getenv("OUTLOOK_CLIENT_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
    redirect_uri = os.getenv("OUTLOOK_REDIRECT_URI")
    if not all([client_id, client_secret, redirect_uri]):
        return jsonify({"msg": "outlook oauth env not set"}), 500

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=20)
    if resp.status_code != 200:
        return jsonify({"msg": "token exchange failed", "status": resp.status_code}), 502
    
    tok = resp.json()
    access_token = tok.get("access_token")
    refresh_token = tok.get("refresh_token")
    expires_in = tok.get("expires_in")
    expiry = utcnow() + timedelta(seconds=int(expires_in or 0))

    existing = OAuthToken.get_for_user(user_id, "outlook")
    if not existing:
        existing = OAuthToken(user_id=user_id, provider="outlook")
        db.session.add(existing)
    existing.access_token = access_token
    existing.refresh_token = refresh_token
    existing.expiry = expiry
    existing.scopes = SCOPES
    db.session.commit()
    
    # Clear the session data
    session.pop("oauth_state", None)
    session.pop("oauth_user_id", None)
    
    # Return a success page
    return """
    <html>
        <body>
            <h1>Successfully connected to Outlook!</h1>
            <p>You can close this window and return to the application.</p>
            <script>
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
    </html>
    """
