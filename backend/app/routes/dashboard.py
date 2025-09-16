from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta

from app.extensions import db
from app.models.usage_log import UsageLog
from app.services.analytics import series_usage, journal_streaks


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/metrics", methods=["GET"])
@jwt_required()
def metrics():
    uid = get_jwt_identity()

    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    # Count journal entries this week
    journal_count = db.session.query(func.count(UsageLog.id)).filter_by(user_id=uid, event_type="journal_create").filter(UsageLog.created_at >= week_start).scalar()

    # Count calendar syncs this week
    calendar_syncs = db.session.query(func.count(UsageLog.id)).filter_by(user_id=uid, event_type="calendar_sync").filter(UsageLog.created_at >= week_start).scalar()

    # Count chat queries this week
    chat_queries = db.session.query(func.count(UsageLog.id)).filter_by(user_id=uid, event_type="chat_query").filter(UsageLog.created_at >= week_start).scalar()

    # Notes syncs
    notes_syncs = db.session.query(func.count(UsageLog.id)).filter_by(user_id=uid, event_type="notes_sync").filter(UsageLog.created_at >= week_start).scalar()

    return jsonify({
        "week_start": week_start.isoformat(),
        "journal_entries": journal_count,
        "calendar_syncs": calendar_syncs,
        "chat_queries": chat_queries,
        "notes_syncs": notes_syncs,
    })


# GET /api/dashboard/series?from=YYYY-MM-DD&to=YYYY-MM-DD&bucket=day&events=journal_create,chat_query
@dashboard_bp.route("/series", methods=["GET"])
@jwt_required()
def series():
    uid = get_jwt_identity()
    try:
        from_s = request.args.get("from")
        to_s = request.args.get("to")
        bucket = request.args.get("bucket", "day")
        events_s = request.args.get("events")
        events = [e for e in events_s.split(",") if e] if events_s else None

        if not from_s or not to_s:
            # default last 7 days
            to_dt = datetime.utcnow()
            from_dt = to_dt - timedelta(days=6)
        else:
            from_dt = datetime.fromisoformat(from_s)
            to_dt = datetime.fromisoformat(to_s)

        data = series_usage(uid, from_dt, to_dt, bucket="hour" if bucket == "hour" else "day", events=events)
        return data, 200
    except Exception as e:
        return {"msg": f"bad_request: {e}"}, 400


# GET /api/dashboard/streaks
@dashboard_bp.route("/streaks", methods=["GET"])
@jwt_required()
def streaks():
    uid = get_jwt_identity()
    try:
        data = journal_streaks(uid)
        return data, 200
    except Exception as e:
        return {"msg": f"error: {e}"}, 400


# GET /api/dashboard/summary?window=7
@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    uid = get_jwt_identity()
    try:
        window = int(request.args.get("window", 7))
        to_dt = datetime.utcnow()
        from_dt = to_dt - timedelta(days=max(1, min(window, 60)))

        # reuse the Phase‑1 counters by calling /metrics logic quickly
        # (import locally to avoid circulars)
        from sqlalchemy import func
        from app.models.usage_log import UsageLog
        journal = (
            db.session.query(func.count(UsageLog.id))
            .filter(UsageLog.user_id == uid, UsageLog.event_type == "journal_create", UsageLog.created_at >= from_dt)
            .scalar()
        )
        chats = (
            db.session.query(func.count(UsageLog.id))
            .filter(UsageLog.user_id == uid, UsageLog.event_type == "chat_query", UsageLog.created_at >= from_dt)
            .scalar()
        )
        cals = (
            db.session.query(func.count(UsageLog.id))
            .filter(UsageLog.user_id == uid, UsageLog.event_type == "calendar_sync", UsageLog.created_at >= from_dt)
            .scalar()
        )
        notes = (
            db.session.query(func.count(UsageLog.id))
            .filter(UsageLog.user_id == uid, UsageLog.event_type == "notes_sync", UsageLog.created_at >= from_dt)
            .scalar()
        )
        streak = journal_streaks(uid)
        return {
            "from": from_dt.isoformat(),
            "to": to_dt.isoformat(),
            "totals": {
                "journal_entries": int(journal or 0),
                "chat_queries": int(chats or 0),
                "calendar_syncs": int(cals or 0),
                "notes_syncs": int(notes or 0),
            },
            "streaks": streak,
        }, 200
    except Exception as e:
        return {"msg": f"error: {e}"}, 400


# POST /api/dashboard/reflection { optional: user_goals }
@dashboard_bp.route("/reflection", methods=["POST"])
@jwt_required()
def reflection():
    uid = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    user_goals = body.get("user_goals")
    try:
        from app.services.reflection import generate_reflection
        from app.services.metrics import log_event
        
        out = generate_reflection(uid, user_goals=user_goals)
        # Log for analytics
        try:
            log_event("reflection_request", {"has_goals": bool(user_goals)})
        except Exception:
            pass
        return out, 200
    except Exception as e:
        return {"msg": f"reflection_error: {e}"}, 502


# GET /api/dashboard/heatmap?window=60&event=journal_create
@dashboard_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def heatmap():
    uid = get_jwt_identity()
    window = int(request.args.get("window", 60))
    window = max(1, min(window, 365))
    event = request.args.get("event")  # optional; if none -> all events combined

    to_dt = datetime.utcnow()
    from_dt = to_dt - timedelta(days=window - 1)

    # SQLite-compatible date truncation
    q = db.session.query(
        func.date(UsageLog.created_at).label("d"),
        func.count(UsageLog.id)
    ).filter(
        UsageLog.user_id == uid,
        UsageLog.created_at >= from_dt,
        UsageLog.created_at <= to_dt,
    )
    if event:
        q = q.filter(UsageLog.event_type == event)
    q = q.group_by("d").order_by("d")

    rows = q.all()
    # Build dense series with zeros
    from datetime import datetime as dt
    by_day = {}
    for date_str, count in rows:
        date_obj = dt.strptime(date_str, '%Y-%m-%d').date()
        by_day[date_obj] = int(count)
    
    out = []
    cur = from_dt.date()
    while cur <= to_dt.date():
        out.append({"date": cur.isoformat(), "count": by_day.get(cur, 0)})
        cur += timedelta(days=1)

    return {"from": from_dt.date().isoformat(), "to": to_dt.date().isoformat(), "points": out}, 200


# GET /api/dashboard/export?format=json&window=30
# Optional: &include=series,summary,streaks&bucket=day&events=journal_create,chat_query
@dashboard_bp.route("/export", methods=["GET"])
@jwt_required()
def export_data():
    from flask import send_file, Response
    from app.services.analytics import series_usage, journal_streaks  # reuse Phase 2 logic
    from app.services.exporter import rows_to_csv
    import io

    uid = get_jwt_identity()
    fmt = (request.args.get("format", "json") or "json").lower()
    window = int(request.args.get("window", 30))
    window = max(1, min(window, 365))
    bucket = request.args.get("bucket", "day")
    events_s = request.args.get("events")
    events = [e for e in events_s.split(",") if e] if events_s else None

    # include flags
    include_raw = request.args.get("include", "")
    includes = set([x.strip() for x in include_raw.split(",") if x.strip()])

    to_dt = datetime.utcnow()
    from_dt = to_dt - timedelta(days=window - 1)

    # Base totals (like /summary)
    journal = (
        db.session.query(func.count(UsageLog.id))
        .filter(UsageLog.user_id == uid, UsageLog.event_type == "journal_create", UsageLog.created_at >= from_dt)
        .scalar()
    ) or 0
    chats = (
        db.session.query(func.count(UsageLog.id))
        .filter(UsageLog.user_id == uid, UsageLog.event_type == "chat_query", UsageLog.created_at >= from_dt)
        .scalar()
    ) or 0
    cals = (
        db.session.query(func.count(UsageLog.id))
        .filter(UsageLog.user_id == uid, UsageLog.event_type == "calendar_sync", UsageLog.created_at >= from_dt)
        .scalar()
    ) or 0
    notes = (
        db.session.query(func.count(UsageLog.id))
        .filter(UsageLog.user_id == uid, UsageLog.event_type == "notes_sync", UsageLog.created_at >= from_dt)
        .scalar()
    ) or 0

    payload = {
        "from": from_dt.isoformat(),
        "to": to_dt.isoformat(),
        "totals": {
            "journal_entries": int(journal),
            "chat_queries": int(chats),
            "calendar_syncs": int(cals),
            "notes_syncs": int(notes),
        },
    }

    if "streaks" in includes:
        payload["streaks"] = journal_streaks(uid)

    if "series" in includes:
        payload["series"] = series_usage(uid, from_dt, to_dt, bucket="hour" if bucket == "hour" else "day", events=events)

    if fmt == "json":
        return payload, 200

    # CSV export (totals + optional series flattened)
    # We emit two CSVs concatenated with a blank line for simplicity, or a single series sheet if requested.
    rows = []
    # totals row
    t = payload["totals"]
    rows.append({
        "from": payload["from"],
        "to": payload["to"],
        "journal_entries": t["journal_entries"],
        "chat_queries": t["chat_queries"],
        "calendar_syncs": t["calendar_syncs"],
        "notes_syncs": t["notes_syncs"],
    })

    buf = io.BytesIO()
    # write totals
    buf.write(rows_to_csv(rows, ["from", "to", "journal_entries", "chat_queries", "calendar_syncs", "notes_syncs"]))

    # optionally append series
    if "series" in includes and payload.get("series"):
        buf.write("\n".encode("utf-8"))
        series = payload["series"]
        # flatten points: each row is t + each key value
        points = []
        # discover keys
        keys = set()
        for p in series.get("points", []):
            for k, v in (p.get("counts") or {}).items():
                keys.add(k)
        ordered = sorted(keys)
        for p in series.get("points", []):
            row = {"t": p["t"]}
            for k in ordered:
                row[k] = int((p.get("counts") or {}).get(k, 0))
            points.append(row)
        buf.write(rows_to_csv(points, ["t", *ordered]))

    buf.seek(0)
    filename = f"slo_export_{from_dt.date()}_to_{to_dt.date()}.csv"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="text/csv")
