# app/agent/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.agent.router import run_agent_turn
from app.extensions import db
from app.models.chat import ChatThread, ChatMessage
from datetime import datetime
import json

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")

def get_or_create_agent_thread(user_id):
    """Get or create a default agent thread for the user."""
    # Look for existing agent thread
    agent_thread = ChatThread.query.filter_by(
        user_id=user_id, 
        title="Agent Conversations"
    ).first()
    
    if not agent_thread:
        # Create new agent thread
        agent_thread = ChatThread(
            user_id=user_id,
            title="Agent Conversations",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(agent_thread)
        db.session.commit()
    
    return agent_thread

def save_agent_message(thread_id, user_id, role, content, tools=None):
    """Save an agent conversation message to the database."""
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

@agent_bp.route("/chat", methods=["POST"])  # streaming can be added later
@jwt_required()
def agent_chat():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return {"msg": "message required"}, 400
    
    confirm_writes = bool(data.get("confirm_writes", True))
    
    # Get or create agent thread for conversation history
    thread = get_or_create_agent_thread(uid)
    thread_id = thread.id
    
    # Save user message to conversation history
    if current_app.config.get("CHAT_HISTORY_ENABLED", True):
        save_agent_message(thread_id, uid, "user", message)
    
    # Run agent with conversation context
    out = run_agent_turn(uid, message, confirm_writes=confirm_writes, thread_id=thread_id)
    
    # Save agent response to conversation history
    if current_app.config.get("CHAT_HISTORY_ENABLED", True):
        assistant_content = out.get("text", "")
        tools = out.get("tool_calls", [])
        save_agent_message(thread_id, uid, "assistant", assistant_content, tools if tools else None)
    
    return jsonify(out), 200

