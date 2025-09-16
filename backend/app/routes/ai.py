from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from app.models.user import User
from app.models.chat import ChatThread, ChatMessage
from app.extensions import db
from app.services.ai_client import ClaudeClient
from app.ai_tools import TOOLS, EXECUTORS
from app.services.metrics import log_event

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

from app.utils.date_utils import get_current_year

SYSTEM_PROMPT = (
    f"You are Student Life Organizer's assistant. The current year is {get_current_year()}. "
    "You have access to tools that let you manage journals and calendar events. "
    "You MUST use these tools when the user asks about their data or wants to make changes.\n\n"
    "IMPORTANT: When the user asks to create a journal entry, you MUST use the create_journal tool with the content they provide.\n"
    "When they ask to see their journals, you MUST use the list_journals tool.\n"
    "When they ask about their calendar, you MUST use the list_calendar_events tool.\n\n"
    "DO NOT try to simulate or pretend to use the tools - you must actually call them.\n"
    "DO NOT respond with placeholders or hypothetical responses - use the tools to get real data.\n\n"
    "Keep answers concise. If a tool returns an error, explain and suggest a fix."
)

def get_or_create_default_thread(user_id):
    """Get or create a default chat thread for the user."""
    # Look for an existing default thread (latest thread or one titled "Latest chat")
    default_thread = ChatThread.query.filter_by(user_id=user_id).order_by(ChatThread.updated_at.desc()).first()
    
    if not default_thread:
        # Create a new default thread
        default_thread = ChatThread(user_id=user_id, title="Latest chat")
        db.session.add(default_thread)
        db.session.commit()
    
    return default_thread

def save_message(thread_id, user_id, role, content, tools=None):
    """Save a chat message to the database."""
    message = ChatMessage(
        thread_id=thread_id,
        user_id=user_id,
        role=role,
        content=content,
        tools_json=(None if tools is None else json.dumps(tools))
    )
    db.session.add(message)
    
    # Update thread's updated_at timestamp
    thread = ChatThread.query.get(thread_id)
    if thread:
        thread.updated_at = datetime.utcnow()
    
    db.session.commit()
    return message

@ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    try:
        data = request.get_json() or {}
        user_msg = (data.get("message") or "").strip()
        if not user_msg:
            return jsonify({"msg": "message required"}), 400

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"msg": "user not found"}), 404

        # Handle thread_id - get existing or create default
        thread_id = data.get("thread_id")
        if thread_id:
            # Verify thread belongs to user
            thread = ChatThread.query.filter_by(id=thread_id, user_id=user_id).first()
            if not thread:
                return jsonify({"msg": "thread not found"}), 404
        else:
            # Create or get default thread
            thread = get_or_create_default_thread(user_id)
            thread_id = thread.id

        # Save user message to database if chat history is enabled
        if current_app.config.get("CHAT_HISTORY_ENABLED", True):
            save_message(thread_id, user_id, "user", user_msg)

        # Force tool usage in debug/test mode
        force_tool = None
        if current_app.debug and "force_tool" in data:
            force_tool = data["force_tool"]

        # Initial messages array
        messages = [{"role": "user", "content": user_msg}]

        # 1) Call Claude with tool definitions
        client = ClaudeClient()
        resp = client.chat(
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
            force_tool=force_tool
        )

        # Log full response content in debug mode
        if current_app.debug:
            print("Claude response content:", resp.content)

        # 2) If Claude requested tool calls, execute them and send back results
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":  # Changed from tool_calls to tool_use
                name = block.name
                # The input is already a dict, no need to parse it
                args = block.input
                fn = EXECUTORS.get(name)
                if not fn:
                    tool_results.append({"tool": name, "error": "tool not implemented"})
                    continue
                try:
                    out = fn(user=user, args=args)
                except Exception as e:  # keep errors visible
                    out = {"error": str(e)}
                tool_results.append({"tool": name, "result": out})

                # Add the assistant's tool use message to the conversation
                messages.append({
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": name,
                            "input": args
                        }
                    ]
                })

                # Send tool result back to Claude
                resp = client.send_tool_result(
                    system=SYSTEM_PROMPT,
                    messages=messages,
                    tool_use_id=block.id,
                    result=out,
                    tools=TOOLS  # Keep tools attached
                )

        # Extract final text response
        final_text = _extract_text(resp)
        
        # Save assistant message to database if chat history is enabled
        if current_app.config.get("CHAT_HISTORY_ENABLED", True):
            save_message(thread_id, user_id, "assistant", final_text, tools=tool_results if tool_results else None)
        
        # Log the chat query event
        try:
            log_event("chat_query", {"thread_id": thread_id, "tools_used": len(tool_results)})
        except Exception:
            pass  # Non-blocking, fail silently
        
        return jsonify({"reply": final_text, "tools": tool_results, "thread_id": thread_id})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _extract_text(message_obj) -> str:
    parts = message_obj.content
    texts = [p.text for p in parts if p.type == "text" and p.text]
    return "\n".join(texts) if texts else ""