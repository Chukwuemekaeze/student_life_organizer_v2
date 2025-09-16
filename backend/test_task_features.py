#!/usr/bin/env python3
"""
Test script for Task Outlook Sync and AI Quick-Add features
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def login_and_get_token():
    """Login and return JWT token"""
    login_data = {
        "email": "test2@example.com", 
        "password": "test123"
    }
    r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} - {r.text}")
        return None
    return r.json()["access_token"]

def test_outlook_sync(token):
    """Test Outlook sync functionality"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n===== TESTING OUTLOOK SYNC =====")
    
    # A) Create task with due date (should sync to Outlook)
    print("\nA) Creating task with due date...")
    due_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    task_data = {
        "title": "Finish essay",
        "description": "Complete my research essay on climate change",
        "due_at": due_time,
        "priority": "high"
    }
    
    r = requests.post(f"{BASE_URL}/api/tasks", headers=headers, json=task_data)
    print(f"Response: {r.status_code}")
    if r.status_code == 201:
        task = r.json()
        task_id = task["id"]
        print(f"✓ Task created with ID: {task_id}")
        print(f"✓ Outlook Event ID: {task.get('outlook_event_id', 'None')}")
        
        # B) Update task title (should update Outlook event)
        print("\nB) Updating task title...")
        update_data = {"title": "Finish essay (UPDATED)"}
        r = requests.patch(f"{BASE_URL}/api/tasks/{task_id}", headers=headers, json=update_data)
        print(f"Response: {r.status_code}")
        if r.status_code == 200:
            print("✓ Task updated successfully")
        
        # C) Remove due date (should delete Outlook event)
        print("\nC) Removing due date...")
        update_data = {"due_at": None}
        r = requests.patch(f"{BASE_URL}/api/tasks/{task_id}", headers=headers, json=update_data)
        print(f"Response: {r.status_code}")
        if r.status_code == 200:
            updated_task = r.json()
            print("✓ Due date removed")
            print(f"✓ Outlook Event ID after removal: {updated_task.get('outlook_event_id', 'None')}")
        
        # D) Delete task (should clean up any remaining Outlook event)
        print("\nD) Deleting task...")
        r = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        print(f"Response: {r.status_code}")
        if r.status_code == 200:
            print("✓ Task deleted successfully")
    else:
        print(f"✗ Failed to create task: {r.text}")

def test_ai_quickadd(token):
    """Test AI Quick-Add functionality"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n===== TESTING AI QUICK-ADD =====")
    
    test_cases = [
        {
            "name": "Simple task with priority and due date",
            "text": "Do math homework by Monday 5pm, high priority"
        },
        {
            "name": "Task with relative date", 
            "text": "Call mom tomorrow at 3pm"
        },
        {
            "name": "Task without due date",
            "text": "Read chapter 5 of physics book"
        },
        {
            "name": "Complex task description",
            "text": "Prepare presentation for marketing meeting on Friday, include budget analysis and Q3 projections"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}) {test_case['name']}")
        print(f"Input: '{test_case['text']}'")
        
        quickadd_data = {"text": test_case["text"]}
        r = requests.post(f"{BASE_URL}/api/tasks/quickadd", headers=headers, json=quickadd_data)
        print(f"Response: {r.status_code}")
        
        if r.status_code == 201:
            task = r.json()
            print(f"✓ Created task: '{task['title']}'")
            print(f"✓ Priority: {task['priority']}")
            print(f"✓ Due date: {task['due_at'] or 'None'}")
            print(f"✓ Source: {task['source']}")
            print(f"✓ Outlook Event ID: {task.get('outlook_event_id', 'None')}")
        else:
            print(f"✗ Failed: {r.text}")
            
        time.sleep(1)  # Rate limit for API calls

def test_error_cases(token):
    """Test error handling"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n===== TESTING ERROR CASES =====")
    
    # Test quickadd without text
    print("\n1) Quick-add without text...")
    r = requests.post(f"{BASE_URL}/api/tasks/quickadd", headers=headers, json={})
    print(f"Response: {r.status_code}")
    if r.status_code == 400:
        print("✓ Correctly rejected empty text")
    else:
        print(f"✗ Unexpected response: {r.text}")
    
    # Test quickadd with empty text
    print("\n2) Quick-add with empty text...")
    r = requests.post(f"{BASE_URL}/api/tasks/quickadd", headers=headers, json={"text": ""})
    print(f"Response: {r.status_code}")
    if r.status_code == 400:
        print("✓ Correctly rejected empty text")
    else:
        print(f"✗ Unexpected response: {r.text}")

def main():
    print("🧪 Starting Task Features Test Suite...")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    print("✓ Authentication successful")
    
    # Run tests
    try:
        test_outlook_sync(token)
        test_ai_quickadd(token)
        test_error_cases(token)
        print("\n🎉 Test suite completed!")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
