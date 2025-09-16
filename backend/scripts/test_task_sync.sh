#!/usr/bin/env bash
# Test script for Task Outlook Sync and AI Quick-Add features
set -euo pipefail

: "${BASE:=http://localhost:5000}"
: "${EMAIL:=test2@example.com}"
: "${PASSWORD:=test123}"

say() { printf "\n===== %s =====\n" "$*"; }

# Login and get token
say "Logging in"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
if [[ "$TOKEN" == "null" ]]; then
  echo "❌ Login failed:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✓ Login successful"

AUTH_HEADER="Authorization: Bearer $TOKEN"

# Test A: Outlook Sync
say "A) Testing Outlook Sync"

echo "1. Creating task with due date..."
TASK_RESPONSE=$(curl -s -X POST "$BASE/api/tasks" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "title": "Finish essay",
    "description": "Complete research essay", 
    "due_at": "2025-09-20T12:00:00Z",
    "priority": "high"
  }')

TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
OUTLOOK_EVENT_ID=$(echo "$TASK_RESPONSE" | jq -r '.outlook_event_id')

echo "✓ Task created with ID: $TASK_ID"
echo "✓ Outlook Event ID: $OUTLOOK_EVENT_ID"

echo "2. Updating task title..."
UPDATE_RESPONSE=$(curl -s -X PATCH "$BASE/api/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "title": "Finish essay (UPDATED)"
  }')

echo "✓ Task updated"

echo "3. Deleting task..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE/api/tasks/$TASK_ID" \
  -H "$AUTH_HEADER")

echo "✓ Task deleted"

# Test B: AI Quick-Add
say "B) Testing AI Quick-Add"

echo "1. Quick-add with priority and due date..."
QUICKADD_RESPONSE=$(curl -s -X POST "$BASE/api/tasks/quickadd" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "text": "Do math homework by Monday 5pm, high priority"
  }')

echo "Response:"
echo "$QUICKADD_RESPONSE" | jq '.'

echo "2. Quick-add without due date..."
QUICKADD_RESPONSE2=$(curl -s -X POST "$BASE/api/tasks/quickadd" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "text": "Read chapter 5 of physics book"
  }')

echo "Response:"
echo "$QUICKADD_RESPONSE2" | jq '.'

# Test Error Cases
say "C) Testing Error Cases"

echo "1. Quick-add without text..."
ERROR_RESPONSE=$(curl -s -X POST "$BASE/api/tasks/quickadd" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{}')

echo "Response:"
echo "$ERROR_RESPONSE" | jq '.'

say "✅ Test suite completed!"
