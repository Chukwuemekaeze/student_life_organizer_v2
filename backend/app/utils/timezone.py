# Timezone utilities for Nigeria (WAT - UTC+1)
from datetime import datetime, timezone, timedelta
from typing import Optional

# Nigeria timezone (West Africa Time - UTC+1)
NIGERIA_TZ = timezone(timedelta(hours=1))

def utcnow() -> datetime:
    """Get current UTC time (replacement for deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

def nigeria_now() -> datetime:
    """Get current Nigeria time (WAT - UTC+1)"""
    return datetime.now(NIGERIA_TZ)

def to_nigeria_time(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to Nigeria time"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(NIGERIA_TZ)

def to_utc(nigeria_dt: datetime) -> datetime:
    """Convert Nigeria time to UTC"""
    if nigeria_dt.tzinfo is None:
        nigeria_dt = nigeria_dt.replace(tzinfo=NIGERIA_TZ)
    return nigeria_dt.astimezone(timezone.utc)

def parse_iso_to_utc(iso_string: str) -> Optional[datetime]:
    """Parse ISO string to UTC datetime, handling timezone info"""
    if not iso_string:
        return None
    
    try:
        # Handle different ISO formats
        if iso_string.endswith('Z'):
            # Already UTC
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        elif '+' in iso_string or iso_string.count('-') > 2:
            # Has timezone info
            return datetime.fromisoformat(iso_string).astimezone(timezone.utc)
        else:
            # Assume naive datetime is in Nigeria timezone
            naive_dt = datetime.fromisoformat(iso_string)
            nigeria_dt = naive_dt.replace(tzinfo=NIGERIA_TZ)
            return nigeria_dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None

def format_for_frontend(utc_dt: Optional[datetime]) -> Optional[str]:
    """Format UTC datetime for frontend (as ISO string with Z suffix)"""
    if not utc_dt:
        return None
    
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    elif utc_dt.tzinfo != timezone.utc:
        utc_dt = utc_dt.astimezone(timezone.utc)
    
    return utc_dt.isoformat().replace('+00:00', 'Z')

def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC, converting if necessary"""
    if dt.tzinfo is None:
        # Assume naive datetime is UTC (for backward compatibility)
        return dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        return dt.astimezone(timezone.utc)
    return dt



