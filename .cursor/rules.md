## Cursor Project Context & Rules — Student Life Organizer

**Goal:** Local‑first academic assistant with journals/notes/projects/study tasks, calendar sync, GitHub/Obsidian integrations, and “corpus‑aware” Claude queries (via local Flask MCP tools). Azure later; dev is fully local.

### Stack & Decisions

* **Backend:** Flask 3, Blueprints, App Factory `create_app()`, SQLAlchemy 2, Flask‑Migrate (Alembic), Flask‑CORS, Flask‑JWT‑Extended.
* **Auth:** JWT access tokens (no refresh yet).
* **DB:** SQLite for MVP → Postgres later.
* **Frontend:** Vite + React + Tailwind.
* **AI/MCP:** Claude Haiku via local MCP Flask endpoints.
* **Calendar:** Outlook (read‑only sync) using Microsoft Graph API.
* **Storage:** local only for content; OAuth tokens encrypted in DB.
* **Critical version pin:** **PyJWT==4.9.0** (do not bump). Keep **Flask‑JWT‑Extended 4.6.x** API.

### Directory Layout (backend)

```
backend/
  app/
    __init__.py
    extensions.py
    models/
      user.py
      journal.py
      oauth_token.py
    routes/
      auth.py
      hello.py
      journal.py
      calendar.py
      google_oauth.py
    error_handlers.py
  migrations/
  main.py
  .env
```

### Environment Variables (dev)

```
FLASK_ENV=development
SECRET_KEY=dev-secret
JWT_SECRET_KEY=dev-jwt
SQLALCHEMY_DATABASE_URI=sqlite:///instance/slo.db

OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...
OUTLOOK_REDIRECT_URI=http://localhost:5000/api/calendar/outlook/callback
```

### Dependencies (lock these)

```
Flask==3.0.3
Flask-JWT-Extended==4.6.0
PyJWT==4.9.0
Flask-Migrate==4.0.7
SQLAlchemy==2.0.31
Flask-Cors==4.0.1
requests==2.32.3
python-dotenv==1.0.1
```

### Current Status (DONE)

* App factory + blueprints wired.
* Env/config + secrets.
* JWT auth working end‑to‑end; version conflict resolved by pinning **PyJWT 4.9.0**.
* Models: `User`, `JournalEntry`, `OAuthToken`.
* Flask‑Migrate integrated.
* Journal CRUD operations implemented.
* Calendar integration with Microsoft Outlook using OAuth.
* CORS enabled.
* Request tracing + JWT error handlers.

### Conventions & Guardrails

* **Error shape:** JSON `{ "msg": "<reason>" }`.
* **Auth:** use `@jwt_required()` and enforce ownership.
* **Validation:** return **422** for invalid body/query.
* **Pagination:** `page`, `limit` → `{items, page, limit, total}`.
* **Dates:** UTC ISO 8601.
* **No breaking changes** without request.
* **No secret leakage** in logs.
* **No global state** beyond app context.

### API Contracts

#### Auth

* `POST /api/auth/register` → create user
* `POST /api/auth/login` → return access token

#### Journal

* `POST /api/journal` `{content}`
* `GET /api/journal` with pagination + search
* `GET /api/journal/<id>`
* `PUT/PATCH /api/journal/<id>` `{content}`
* `DELETE /api/journal/<id>`

#### Calendar

* `GET /api/calendar/outlook/start`
* `GET /api/calendar/outlook/callback`
* `GET /api/calendar/sync`

### What to Implement Next

1. Frontend scaffold (Vite + Tailwind).
2. Notes/Projects/StudyTasks CRUD.
3. Analytics dashboard skeleton.
4. Corpus‑aware MCP integration.

### How to Work (Cursor Instructions)

* Show diffs per file.
* **Do not** upgrade PyJWT beyond **4.9.0**.
* Propose breaking shifts before coding.
* After changes, print a manual test plan (curl commands).
* Include Alembic migrations for model changes.

### Acceptance Criteria (for this batch)

* Journal CRUD works with auth + ownership.
* Outlook OAuth persists tokens; `/api/calendar/sync` returns events.
* App starts clean with `flask run`.
* JSON responses with correct codes.
* Requirements remain compatible with **PyJWT 4.9.0**.
