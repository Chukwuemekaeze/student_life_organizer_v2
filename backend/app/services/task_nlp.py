# app/services/task_nlp.py
import os, json, requests
from datetime import datetime, timezone, timedelta

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
ANTHROPIC_BASE = os.getenv("ANTHROPIC_BASE", "https://api.anthropic.com")

HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

PROMPT = """You extract a single task from a short text. Respond ONLY in JSON with keys:
title (string), priority (low|medium|high), due_at (ISO8601 or empty).

Context: Today is {{TODAY}}. When parsing relative dates like "Friday", "tomorrow", "next week", etc., use this as reference.
For dates without a year specified, assume the current year {{YEAR}}.

If no clear due date, set due_at to empty.
Text: <<<{{TEXT}}>>>"""

def quick_extract_task(text: str):
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    
    # Get current date context
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %B %d, %Y")  # e.g., "Monday, September 15, 2025"
    year_str = str(now.year)
    
    # Replace placeholders in prompt
    prompt_with_context = PROMPT.replace("{{TODAY}}", today_str).replace("{{YEAR}}", year_str).replace("{{TEXT}}", text[:1000])
    
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 300,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": prompt_with_context}],
    }
    r = requests.post(f"{ANTHROPIC_BASE}/v1/messages", headers=HEADERS, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    out = r.json()
    text_out = "".join([b.get("text","") for b in out.get("content",[]) if b.get("type")=="text"])
    try:
        data = json.loads(text_out)
    except Exception:
        return {"title": text[:100].strip() or "Untitled task", "priority": "medium", "due_at": ""}
    title = (data.get("title") or "Untitled task").strip()[:100]
    priority = (data.get("priority") or "medium").lower()
    if priority not in ("low","medium","high"):
        priority = "medium"
    due_at = (data.get("due_at") or "").strip()
    
    # Post-process due_at to fix potential year issues
    if due_at:
        due_at = _fix_date_year(due_at, now)
    
    return {"title": title, "priority": priority, "due_at": due_at}

def _fix_date_year(date_str: str, current_time: datetime) -> str:
    """Fix dates that may have incorrect years by ensuring they're not in the past."""
    try:
        from datetime import datetime
        # Try to parse the date
        if 'T' in date_str:
            # ISO format with time
            parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_str  # Can't parse, return as-is
        
        # If the parsed date is more than 30 days in the past, assume wrong year
        if parsed_date < current_time.replace(tzinfo=None) - timedelta(days=30):
            # Replace with current year
            fixed_date = parsed_date.replace(year=current_time.year)
            # If still in the past, try next year
            if fixed_date < current_time.replace(tzinfo=None):
                fixed_date = fixed_date.replace(year=current_time.year + 1)
            return fixed_date.isoformat()
        
        return date_str
    except Exception:
        # If anything goes wrong, return original
        return date_str
