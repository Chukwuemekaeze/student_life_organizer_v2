#!/usr/bin/env bash
set -euo pipefail

: "${BASE:=http://localhost:5000}"          # Override as needed
: "${TOKEN:=}"                               # Optional JWT; leave empty if your API doesn't require it
CHAT_PATH="/api/ai/chat"                     # Actual chat endpoint path

AUTH_HEADER=()
if [[ -n "$TOKEN" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer $TOKEN")
fi

say() { printf "\n===== %s =====\n" "$*"; }

# A) List Journals (expect tool_use: list_journals -> limit 5)
say "A) List last 5 journals containing 'gym'"
curl -sS -X POST "$BASE$CHAT_PATH" \
  -H "Content-Type: application/json" \
  "${AUTH_HEADER[@]}" \
  -d '{
    "message": "Show my last 5 journals with gym."
  }' | tee /dev/stderr | jq '.' >/dev/null

# B) Create Journal (expect tool_use: create_journal)
say "B) Create a journal entry"
curl -sS -X POST "$BASE$CHAT_PATH" \
  -H "Content-Type: application/json" \
  "${AUTH_HEADER[@]}" \
  -d '{
    "message": "Create a journal: Push workout felt great."
  }' | tee /dev/stderr | jq '.' >/dev/null

# C) Calendar Window (expect tool_use: list_calendar_events with days=3)
say "C) List events for next 3 days"
curl -sS -X POST "$BASE$CHAT_PATH" \
  -H "Content-Type: application/json" \
  "${AUTH_HEADER[@]}" \
  -d '{
    "message": "What's on my calendar for the next 3 days?"
  }' | tee /dev/stderr | jq '.' >/dev/null

say "Done. Check server logs for tool_use -> tool_result sequence and final assistant text."

