# Task Outlook Sync & AI Quick-Add Implementation

## 🎯 Overview

This patch extends the existing `/api/tasks` endpoints with two major features:

1. **Outlook Sync**: Automatically mirror tasks with `due_at` into Outlook calendar events
2. **AI Quick-Add**: Create tasks from natural language text using Claude AI

## 📁 Files Added/Modified

### New Services
- `app/services/outlook_tasks.py` - Outlook calendar integration for tasks
- `app/services/task_nlp.py` - Claude AI integration for natural language processing

### Modified Files
- `app/routes/tasks.py` - Added Outlook sync logic and `/quickadd` endpoint

### Test Files
- `backend/test_task_features.py` - Comprehensive Python test suite
- `backend/scripts/test_task_sync.sh` - Bash/curl test script

## 🔧 API Endpoints

### Existing Endpoints (Enhanced with Outlook Sync)

#### POST `/api/tasks`
Creates a task and automatically syncs to Outlook if `due_at` is provided.

**Request Body:**
```json
{
  "title": "Finish essay",
  "description": "Complete research essay",
  "due_at": "2025-09-20T12:00:00Z",
  "priority": "high"
}
```

**Response:**
```json
{
  "id": 123,
  "title": "Finish essay",
  "description": "Complete research essay",
  "due_at": "2025-09-20T12:00:00Z",
  "priority": "high",
  "status": "todo",
  "outlook_event_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T_L_tFXWAAAAAAENAAAiIsqMbYjsT5e-T_L_tFXWAABXJGhMAAA=",
  "source": "manual",
  "created_at": "2025-09-13T10:00:00Z",
  "updated_at": "2025-09-13T10:00:00Z"
}
```

#### PATCH `/api/tasks/{id}`
Updates a task and syncs changes to Outlook. If `due_at` is removed, deletes the Outlook event.

#### DELETE `/api/tasks/{id}`
Deletes a task and cleans up any associated Outlook event.

### New Endpoint

#### POST `/api/tasks/quickadd`
Creates a task from natural language text using Claude AI.

**Request Body:**
```json
{
  "text": "Do math homework by Monday 5pm, high priority",
  "description": "Optional additional description"
}
```

**Response:**
```json
{
  "id": 124,
  "title": "Do math homework",
  "description": "",
  "due_at": "2025-09-16T17:00:00Z",
  "priority": "high",
  "status": "todo",
  "outlook_event_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T_L_tFXWAAAAAAENAAAiIsqMbYjsT5e-T_L_tFXWAABXJGhNAAA=",
  "source": "chat_quickadd",
  "created_at": "2025-09-13T10:05:00Z",
  "updated_at": "2025-09-13T10:05:00Z"
}
```

**Error Response (400):**
```json
{
  "msg": "text required"
}
```

**Error Response (502):**
```json
{
  "msg": "nlp_error: ANTHROPIC_API_KEY not set"
}
```

## 🔄 Outlook Sync Behavior

### When Tasks Are Synced
- Tasks with `due_at` field populated
- Creates Outlook calendar events with subject `[Task] {title}`
- Event importance set based on task priority (high priority → high importance)
- Event start/end times both set to `due_at` (single point in time)

### Sync Lifecycle
1. **Create**: Task with `due_at` → Outlook event created
2. **Update**: Task changes → Outlook event updated
3. **Remove due date**: `due_at` set to null → Outlook event deleted
4. **Delete**: Task deleted → Outlook event deleted

### Error Handling
- All Outlook operations wrapped in try/catch
- Failures don't prevent task operations from completing
- Graceful degradation if Outlook is unavailable

## 🤖 AI Quick-Add Features

### Natural Language Processing
- Powered by Claude AI (configurable model)
- Extracts: title, priority, due date
- Handles relative dates ("tomorrow", "Monday", "next week")
- Fallback to manual values if AI extraction fails

### Input Examples
```
"Do math homework by Monday 5pm, high priority"
→ title: "Do math homework", priority: "high", due_at: "2025-09-16T17:00:00Z"

"Call mom tomorrow at 3pm"
→ title: "Call mom", priority: "medium", due_at: "2025-09-14T15:00:00Z"

"Read chapter 5 of physics book"
→ title: "Read chapter 5 of physics book", priority: "medium", due_at: null
```

## 🔧 Environment Variables

All required environment variables are already configured in `config_template.py`:

```bash
# Already required for calendar integration
OUTLOOK_CLIENT_ID=your-outlook-client-id
OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
OUTLOOK_REDIRECT_URI=http://localhost:5173/api/calendar/outlook/callback

# Already required for reflection features
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CLAUDE_MODEL=claude-3-haiku-20240307
ANTHROPIC_BASE=https://api.anthropic.com
```

## 🧪 Testing

### Run Python Test Suite
```bash
cd backend
python test_task_features.py
```

### Run Bash Test Script
```bash
cd backend
bash scripts/test_task_sync.sh
```

### Manual Postman Testing

#### Test A: Outlook Sync
1. **POST** `/api/tasks` with body:
   ```json
   { "title": "Finish essay", "due_at": "2025-09-20T12:00:00Z" }
   ```
   Expect: Task created + Outlook event appears

2. **PATCH** `/api/tasks/:id` to change title
   Expect: Outlook event subject updates

3. **DELETE** `/api/tasks/:id`
   Expect: Outlook event deleted

#### Test B: Quick-Add
1. **POST** `/api/tasks/quickadd` with body:
   ```json
   { "text": "Do math homework by Monday 5pm, high priority" }
   ```
   Expect: Task with title `Do math homework`, priority `high`, due date parsed

2. Check database and Outlook if due date present

## ✅ Success Criteria

- [x] Tasks with `due_at` sync seamlessly to Outlook events
- [x] Natural language quick-add creates usable tasks via Claude
- [x] No regressions to existing Task CRUD operations
- [x] No regressions to existing analytics functionality
- [x] Graceful error handling for Outlook and AI failures
- [x] Comprehensive test coverage

## 🔄 Integration Points

### With Existing Calendar System
- Reuses existing `ensure_token()` function from `app/services/calendar.py`
- Leverages existing OAuth flow and token management
- Compatible with existing Outlook integration

### With Existing Task System
- Extends existing Task model (uses reserved `outlook_event_id` field)
- Maintains all existing functionality
- Preserves existing analytics and logging

### With Existing AI System
- Uses same Anthropic configuration as reflection features
- Consistent error handling patterns
- Follows existing service architecture
