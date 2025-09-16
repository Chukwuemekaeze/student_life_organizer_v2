import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
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
    
    # 2. Test AI chat - create journal
    chat_data = {
        "message": "Please use the create_journal tool to add this entry: Today I studied for 2 hours and completed my math homework."
    }
    r = requests.post(f"{BASE_URL}/api/ai/chat", headers=headers, json=chat_data)
    print("\nAI Chat response (create journal):", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print("Raw response:", r.text)
    
    # 3. Test AI chat - list journals
    chat_data = {
        "message": "Please use the list_journals tool to show my last 3 entries"
    }
    r = requests.post(f"{BASE_URL}/api/ai/chat", headers=headers, json=chat_data)
    print("\nAI Chat response (list journals):", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print("Raw response:", r.text)

if __name__ == "__main__":
    test_endpoints()