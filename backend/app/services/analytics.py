from __future__ import annotations
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict, List, Literal

from sqlalchemy import func

from app.extensions import db
from app.models.usage_log import UsageLog
from app.models.journal import JournalEntry  # assumes your model file name

Bucket = Literal["day", "hour"]


def _dt_utc(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _date_range(from_dt: datetime, to_dt: datetime, bucket: Bucket) -> List[datetime]:
    cur = _dt_utc(from_dt)
    end = _dt_utc(to_dt)
    out = []
    step = timedelta(hours=1) if bucket == "hour" else timedelta(days=1)
    
    if bucket == "day":
        # For day buckets, normalize to start of day to match aggregation
        cur = cur.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end.replace(hour=0, minute=0, second=0, microsecond=0)
    
    while cur <= end:
        out.append(cur)
        cur += step
    return out


def series_usage(
    user_id: int,
    from_dt: datetime,
    to_dt: datetime,
    bucket: Bucket = "day",
    events: List[str] | None = None,
) -> Dict:
    """Return time‑bucket counts per event_type from UsageLog.
    Shape: { bucket: "day", from, to, points: [{ t:"2025-09-01", counts:{journal_create:2,...}}] }
    """
    from_dt = _dt_utc(from_dt)
    to_dt = _dt_utc(to_dt)

    # SQLite-compatible date truncation
    if bucket == "hour":
        date_format = func.strftime('%Y-%m-%d %H:00:00', UsageLog.created_at)
    else:  # day
        date_format = func.date(UsageLog.created_at)

    q = db.session.query(
        UsageLog.event_type,
        date_format.label("bucket_ts"),
        func.count(UsageLog.id),
    ).filter(
        UsageLog.user_id == user_id,
        UsageLog.created_at >= from_dt,
        UsageLog.created_at <= to_dt,
    ).group_by("bucket_ts", UsageLog.event_type)

    if events:
        q = q.filter(UsageLog.event_type.in_(events))

    rows = q.all()

    # index rows by timestamp
    agg = defaultdict(dict)
    for et, ts_str, c in rows:
        if bucket == "hour":
            # Parse the hour string back to datetime
            ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        else:
            # Parse date and set to start of day
            ts = datetime.strptime(str(ts_str), '%Y-%m-%d').replace(tzinfo=timezone.utc)
        agg[ts][et] = int(c)

    # fill missing buckets with 0s
    buckets = []
    for ts in _date_range(from_dt, to_dt, bucket):
        counts = agg.get(ts, {})
        if events:
            counts = {e: int(counts.get(e, 0)) for e in events}
        else:
            # keep whatever is present
            counts = {k: int(v) for k, v in counts.items()}
        buckets.append({
            "t": ts.isoformat(),
            "counts": counts,
        })

    return {
        "bucket": bucket,
        "from": from_dt.isoformat(),
        "to": to_dt.isoformat(),
        "points": buckets,
    }


def journal_streaks(user_id: int) -> Dict[str, int]:
    """Compute current and best day‑streaks from JournalEntry.created_at."""
    # Pull distinct dates with at least one entry - SQLite compatible
    rows = (
        db.session.query(func.date(JournalEntry.timestamp))
        .filter(JournalEntry.user_id == user_id)
        .group_by(func.date(JournalEntry.timestamp))
        .order_by(func.date(JournalEntry.timestamp))
        .all()
    )
    
    if not rows:
        return {"current": 0, "best": 0}
    
    # Convert date strings to date objects
    from datetime import datetime
    days = [datetime.strptime(r[0], '%Y-%m-%d').date() for r in rows]
    
    # Best streak
    best = cur = 1
    for i in range(1, len(days)):
        if (days[i] - days[i - 1]).days == 1:
            cur += 1
        else:
            best = max(best, cur)
            cur = 1
    best = max(best, cur)

    # Current streak counting back from today
    from datetime import date, timedelta as td
    today = date.today()
    s = set(days)
    current = 0
    d = today
    while d in s:
        current += 1
        d = d - td(days=1)

    return {"current": current, "best": int(best)}
