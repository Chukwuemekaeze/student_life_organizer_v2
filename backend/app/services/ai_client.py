import os
import json
from typing import Any, Dict, List, Optional
from anthropic import Anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))

class ToolCallError(Exception):
    pass

class ClaudeClient:
    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY missing in environment")
        self.client = Anthropic(api_key=api_key)

    def chat(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        force_tool: Optional[str] = None
    ) -> Any:
        """Send a messages.create request with optional tool definitions."""
        payload: Dict[str, Any] = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        if force_tool:
            payload["tool_choice"] = {"type": "tool", "name": force_tool}

        return self.client.messages.create(**payload)

    def send_tool_result(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tool_use_id: str,
        result: Any,
        tools: List[Dict[str, Any]] | None = None,
    ) -> Any:
        """Send a follow-up message with tool result."""
        # Ensure result is JSON-serializable
        if not isinstance(result, (dict, list, str, int, float, bool)):
            result = {"result": str(result)}

        # Log tool result for debugging
        print(f"Sending tool result for {tool_use_id}: {len(str(result))} bytes")

        # Add the tool result message to the conversation
        all_messages = [
            *messages,
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result)
                    }
                ]
            }
        ]

        return self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=tools,  # Keep tools attached
            messages=all_messages
        )