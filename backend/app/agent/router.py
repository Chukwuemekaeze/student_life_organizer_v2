# app/agent/router.py
from __future__ import annotations
import os, json, requests
from typing import Dict, Any
from app.agent.guard import AgentPolicy, user_scopes, rate_limit, audit_log
from app.agent.tools import TOOL_REGISTRY, TOOL_SCHEMAS
from app.agent.context import build_context_pack

def get_anthropic_config():
    """Get Anthropic configuration dynamically to ensure .env is loaded"""
    return {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "model": os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
        "base_url": os.getenv("ANTHROPIC_BASE", "https://api.anthropic.com")
    }

SYSTEM_PROMPT = (
    "You are SLO's study agent. You can read and write journals, tasks, notes, calendar, notifications. "
    "CRITICAL: Always check the provided context_pack first - it contains the current date and time. "
    "Use the current_time info for all date/time references. When users say 'tomorrow', 'next week', etc., "
    "calculate dates relative to the current_datetime provided in context. "
    "Always use proper current dates - never use old dates like 2023. "
    "Use ISO8601 UTC datetimes in tool calls. "
    "If planning to make more than 2 writes, summarize and ask for confirmation unless 'confirm_writes' is false. "
    "\n\nIMPORTANT DATA DISTINCTION: "
    "- NOTES = Notion notes (synced from user's Notion workspace) - use 'list_notes' tool "
    "- JOURNALS = Local journal entries (written directly in SLO) - use 'get_journals' tool "
    "When users say 'notes', they mean Notion notes unless they specifically mention 'journal'. "
    "When users say 'my OOP in Java note' or similar, search Notion notes, not journals. "
    "\n\nCONVERSATION INTELLIGENCE: "
    "You maintain conversation context across turns. When a user responds with confirmations like 'yes', 'go ahead', "
    "'do it', 'proceed', etc., understand what they're confirming based on the conversation history. "
    "Don't ask follow-up questions when the user has already provided clear confirmation. "
    "Be intelligent about understanding user intent - if they ask to delete something specific and then confirm, proceed immediately. "
    "Only ask clarifying questions when genuinely ambiguous. "
    "\n\nERROR HANDLING: When tool calls return errors, provide helpful context to the user. "
    "If calendar access fails, explain they need to connect their Outlook account. "
    "If operations fail, suggest practical next steps. Never expose raw technical errors. "
    "When you can't complete a requested action due to missing setup (like calendar access), "
    "explain what the user needs to do and offer alternative ways to help them. "
    "If you encounter errors fetching data, work with what you have and inform the user gracefully."
)


def call_claude(messages: list[dict], tools: list[dict]) -> Dict[str, Any]:
    config = get_anthropic_config()
    headers = {
        "x-api-key": config["api_key"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": config["model"],
        "max_tokens": 1200,
        "temperature": 0.2,
        "system": SYSTEM_PROMPT,
        "messages": messages,
        "tools": tools,
    }
    r = requests.post(f"{config['base_url']}/v1/messages", headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    return r.json()


def run_agent_turn(user_id: int, user_text: str, confirm_writes: bool = True, thread_id: int = None) -> Dict[str, Any]:
    config = get_anthropic_config()
    if not config["api_key"] or not config["api_key"].startswith("sk-"):
        return {"error": "anthropic_key_missing", "text": "❌ ANTHROPIC_API_KEY environment variable not set or invalid. Please configure your Claude API key to use the agent.", "tool_calls": []}

    scopes = user_scopes(user_id)
    policy = AgentPolicy()

    # rate limit per user
    rate_limit(f"agent:{user_id}", max_calls=60, per_seconds=60)

    context_pack = build_context_pack(user_id)

    # Get conversation history if thread_id is provided
    messages = []
    if thread_id:
        # Import here to avoid circular imports
        from app.models.chat import ChatMessage
        
        # Get recent conversation history (last 10 messages for context)
        recent_messages = ChatMessage.query.filter_by(
            user_id=user_id, 
            thread_id=thread_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        # Reverse to get chronological order
        recent_messages = list(reversed(recent_messages))
        
        # Add conversation history to messages
        for msg in recent_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

    # Check if this is a confirmation to a previous request
    from app.agent.conversation_utils import is_confirmation_message, is_denial_message, extract_pending_action_from_history
    
    is_confirmation = is_confirmation_message(user_text)
    is_denial = is_denial_message(user_text)
    pending_action = extract_pending_action_from_history(messages) if messages else {"action": None}
    
    # Enhanced context for confirmation handling
    conversation_context = ""
    if is_confirmation and pending_action.get("action"):
        action_details = ""
        if pending_action.get("action") == "delete_journal":
            action_details = "Use the delete_journal tool with the appropriate journal ID to delete the journal entry."
        elif pending_action.get("action") == "delete_calendar_event":
            action_details = "Use the calendar_delete_event tool with the appropriate event ID to delete the calendar event."
        elif pending_action.get("action") == "delete_task":
            action_details = "Use the appropriate task deletion tool to delete the task."
        
        conversation_context = f"\n\nCONVERSATION CONTEXT: The user is confirming a previous request. " \
                              f"EXECUTE ACTION NOW: {pending_action.get('action')} - {pending_action.get('context')}. " \
                              f"Original request: '{pending_action.get('content', '')}'. " \
                              f"Action required: {action_details} " \
                              f"Do NOT ask for further confirmation - the user has already confirmed. " \
                              f"Take the action immediately and report success."
    elif is_denial and pending_action.get("action"):
        conversation_context = f"\n\nCONVERSATION CONTEXT: The user is declining/canceling a previous request. " \
                              f"Do not proceed with the pending action: {pending_action.get('action')}. " \
                              f"Acknowledge the cancellation and ask how else you can help."

    # Add current user message with enhanced context
    messages.append({
        "role": "user", 
        "content": f"Context: {json.dumps(context_pack)}\n\nUser request: {user_text}\n\nSettings: confirm_writes={confirm_writes}{conversation_context}"
    })

    tool_calls = []
    writes = 0

    # Tool loop (bounded)
    for step in range(policy.max_tool_calls):
        resp = call_claude(messages, tools=[{"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]} for t in TOOL_SCHEMAS])
        content = resp.get("content", [])
        # Scan for tool_use blocks or final text
        next_tool = None
        final_text = []
        for block in content:
            if block.get("type") == "tool_use":
                next_tool = block
                break
            if block.get("type") == "text":
                final_text.append(block.get("text",""))
        if not next_tool:
            # No tool call; return final text
            return {"text": "\n".join(final_text), "tool_calls": tool_calls}

        # Execute tool
        tool_name = next_tool["name"]
        tool_input = next_tool.get("input", {})
        f = TOOL_REGISTRY.get(tool_name)
        if not f:
            messages.append({
                "role": "assistant", 
                "content": [{"type": "tool_use", "id": next_tool["id"], "name": tool_name, "input": tool_input}]
            })
            messages.append({
                "role": "user", 
                "content": [{"type": "tool_result", "tool_use_id": next_tool["id"], "content": json.dumps({"error": "unknown_tool"})}]
            })
            continue

        # Count writes
        if tool_name in {"create_journal","create_task","update_task","calendar_create_event","calendar_update_event","calendar_delete_event"}:
            writes += 1
            if writes > policy.max_writes_per_turn:
                messages.append({
                    "role": "assistant", 
                    "content": [{"type": "tool_use", "id": next_tool["id"], "name": tool_name, "input": tool_input}]
                })
                messages.append({
                    "role": "user", 
                    "content": [{"type": "tool_result", "tool_use_id": next_tool["id"], "content": json.dumps({"error": "write_limit_exceeded"})}]
                })
                continue
            if confirm_writes and writes > policy.require_confirm_threshold:
                # Ask model to confirm with user instead of proceeding
                messages.append({
                    "role": "assistant", 
                    "content": [{"type": "tool_use", "id": next_tool["id"], "name": tool_name, "input": tool_input}]
                })
                messages.append({
                    "role": "user", 
                    "content": [{"type": "tool_result", "tool_use_id": next_tool["id"], "content": json.dumps({"error": "confirmation_required"})}]
                })
                continue

        try:
            result = f(user_id=user_id, scopes=scopes, **tool_input)
            audit_log(user_id, tool_name, tool_input, result)
            tool_calls.append({"name": tool_name, "input": tool_input, "result": result})
            
            # Add assistant message with tool use
            messages.append({
                "role": "assistant", 
                "content": [{"type": "tool_use", "id": next_tool["id"], "name": tool_name, "input": tool_input}]
            })
            
            # Add user message with tool result
            messages.append({
                "role": "user", 
                "content": [{"type": "tool_result", "tool_use_id": next_tool["id"], "content": json.dumps(result)}]
            })
        except Exception as e:
            error_msg = str(e)
            
            # Provide more user-friendly error messages for common issues
            if "No valid Outlook token" in error_msg:
                error_msg = "Calendar access not configured. Please connect your Outlook account in settings."
            elif "rate limit" in error_msg.lower():
                error_msg = "Service temporarily busy. Please try again in a moment."
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                error_msg = "Service temporarily unavailable. Please try again later."
            elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_msg = "Access denied. Please check your account permissions."
            
            audit_log(user_id, tool_name, tool_input, None, error=error_msg)
            
            # Create a more informative error result
            error_result = {
                "error": error_msg,
                "tool_name": tool_name,
                "suggestion": "The operation couldn't be completed. You may need to check your settings or try again later."
            }
            
            messages.append({
                "role": "assistant", 
                "content": [{"type": "tool_use", "id": next_tool["id"], "name": tool_name, "input": tool_input}]
            })
            messages.append({
                "role": "user", 
                "content": [{"type": "tool_result", "tool_use_id": next_tool["id"], "content": json.dumps(error_result)}]
            })
            continue

    return {"text": "Tool loop ended (max steps reached).", "tool_calls": tool_calls}
