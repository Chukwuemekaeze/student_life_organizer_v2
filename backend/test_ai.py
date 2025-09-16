import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_ai():
    # 1. Login
    login_data = {
        "email": "test2@example.com",
        "password": "test123"
    }
    r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print("Login response:", r.status_code)
    if r.status_code != 200:
        print(r.text)
        return
    
    token = r.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test AI chat - create calendar event
    # Use actual dates for the event
    tomorrow = datetime.utcnow() + timedelta(days=1)
    event_start = tomorrow.replace(hour=14, minute=0, second=0).isoformat() + "Z"  # 2 PM tomorrow
    event_end = tomorrow.replace(hour=15, minute=0, second=0).isoformat() + "Z"    # 3 PM tomorrow
    
    chat_data = {
        "message": f"Please create a calendar event for a Math Study Session tomorrow from {event_start} to {event_end}. It will be in Room 101."
    }
    r = requests.post(f"{BASE_URL}/api/ai/chat", headers=headers, json=chat_data)
    print("\nAI Chat response (create calendar event):", r.status_code)
    print(json.dumps(r.json(), indent=2))
    
    # 3. Test AI chat - list calendar events
    chat_data = {
        "message": "What events do I have scheduled for tomorrow?"
    }
    r = requests.post(f"{BASE_URL}/api/ai/chat", headers=headers, json=chat_data)
    print("\nAI Chat response (list calendar events):", r.status_code)
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    test_ai()