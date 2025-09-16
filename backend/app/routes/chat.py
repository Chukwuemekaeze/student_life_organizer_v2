import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.chat import ChatThread, ChatMessage

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/api/chat')

@chat_bp.route('/threads', methods=['GET'])
@jwt_required()
def list_threads():
    uid = get_jwt_identity()
    threads = ChatThread.query.filter_by(user_id=uid).order_by(ChatThread.updated_at.desc()).all()
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'created_at': t.created_at.isoformat(),
            'updated_at': t.updated_at.isoformat(),
        } for t in threads
    ])

@chat_bp.route('/threads', methods=['POST'])
@jwt_required()
def create_thread():
    uid = get_jwt_identity()
    title = (request.json or {}).get('title') or 'New chat'
    t = ChatThread(user_id=uid, title=title)
    db.session.add(t)
    db.session.commit()
    return jsonify({'id': t.id, 'title': t.title}), 201

@chat_bp.route('/threads/<int:thread_id>', methods=['PATCH'])
@jwt_required()
def rename_thread(thread_id):
    uid = get_jwt_identity()
    title = (request.json or {}).get('title', '').strip()
    t = ChatThread.query.filter_by(id=thread_id, user_id=uid).first_or_404()
    if title:
        t.title = title
        db.session.commit()
    return jsonify({'id': t.id, 'title': t.title})

@chat_bp.route('/threads/<int:thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    uid = get_jwt_identity()
    t = ChatThread.query.filter_by(id=thread_id, user_id=uid).first_or_404()
    db.session.delete(t)
    db.session.commit()
    return jsonify({'ok': True})

@chat_bp.route('/threads/<int:thread_id>/messages', methods=['GET'])
@jwt_required()
def list_messages(thread_id):
    uid = get_jwt_identity()
    q = ChatMessage.query.filter_by(thread_id=thread_id, user_id=uid).order_by(ChatMessage.created_at.asc())
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    items = q.offset(offset).limit(limit).all()
    return jsonify([
        {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'tools': m.tools_json and json.loads(m.tools_json)
        } for m in items
    ])

@chat_bp.route('/threads/<int:thread_id>/messages', methods=['POST'])
@jwt_required()
def append_message(thread_id):
    uid = get_jwt_identity()
    body = request.get_json() or {}
    role = body.get('role')
    content = (body.get('content') or '').strip()
    tools = body.get('tools')
    if role not in ['user', 'assistant', 'system'] or not content:
        return jsonify({'msg': 'Invalid role/content'}), 400
    t = ChatThread.query.filter_by(id=thread_id, user_id=uid).first_or_404()
    m = ChatMessage(
        thread_id=thread_id,
        user_id=uid,
        role=role,
        content=content,
        tools_json=(None if tools is None else json.dumps(tools))
    )
    db.session.add(m)
    # Update thread's updated_at timestamp
    t.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'id': m.id}), 201

@chat_bp.route('/threads/<int:thread_id>/messages/<int:msg_id>', methods=['DELETE'])
@jwt_required()
def delete_message(thread_id, msg_id):
    uid = get_jwt_identity()
    m = ChatMessage.query.filter_by(id=msg_id, thread_id=thread_id, user_id=uid).first_or_404()
    db.session.delete(m)
    db.session.commit()
    return jsonify({'ok': True})

@chat_bp.route('/threads/<int:thread_id>/export', methods=['GET'])
@jwt_required()
def export_thread(thread_id):
    uid = get_jwt_identity()
    t = ChatThread.query.filter_by(id=thread_id, user_id=uid).first_or_404()
    msgs = ChatMessage.query.filter_by(thread_id=t.id, user_id=uid).order_by(ChatMessage.created_at.asc()).all()
    return jsonify({
        'thread': {'id': t.id, 'title': t.title, 'created_at': t.created_at.isoformat()},
        'messages': [
            {'role': m.role, 'content': m.content, 'created_at': m.created_at.isoformat(), 'tools': m.tools_json and json.loads(m.tools_json)}
            for m in msgs
        ]
    })
