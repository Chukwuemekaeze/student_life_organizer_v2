import requests
from typing import List

NOTION_API = "https://api.notion.com/v1"
DEFAULT_VERSION = "2022-06-28"

class NotionAuthError(Exception):
    pass

class NotionAPIError(Exception):
    pass

class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.h = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": DEFAULT_VERSION,
            "Content-Type": "application/json",
        }

    def whoami(self) -> dict:
        # Notion doesn't have a perfect whoami for bots; we probe via search
        r = requests.post(f"{NOTION_API}/search", headers=self.h, json={"page_size": 1}, timeout=10)
        if r.status_code in (401, 403):
            raise NotionAuthError("Invalid Notion token")
        if not r.ok:
            raise NotionAPIError(r.text)
        data = r.json()
        return {
            "workspace_name": data.get("object", "list"),  # best-effort label
        }

    def list_recent_pages(self, limit: int = 10) -> List[dict]:
        payload = {
            "page_size": max(1, min(limit, 20)),
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }
        r = requests.post(f"{NOTION_API}/search", headers=self.h, json=payload, timeout=15)
        if r.status_code in (401, 403):
            raise NotionAuthError("Invalid Notion token")
        if not r.ok:
            raise NotionAPIError(r.text)
        items = []
        for res in r.json().get("results", []):
            if res.get("object") != "page":
                continue
            page_id = res.get("id")
            url = res.get("url")
            props = res.get("properties", {})
            title = None
            # Extract a reasonable title
            for v in props.values():
                if v.get("type") == "title" and v.get("title"):
                    title = "".join([t.get("plain_text", "") for t in v.get("title", [])]).strip()
                    break
            if not title:
                title = "Untitled"
            items.append({
                "page_id": page_id,
                "title": title,
                "url": url,
                "last_edited_time": res.get("last_edited_time"),
            })
        return items


