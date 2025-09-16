"""
Chat message retention tasks.

This module provides functions to clean up old chat messages based on retention policies.
"""

from datetime import datetime, timedelta
from app.extensions import db
from app.models.chat import ChatThread, ChatMessage


def cleanup_expired_messages(retention_days=None):
    """
    Delete chat messages older than the specified retention period.
    
    Args:
        retention_days (int, optional): Number of days to retain messages.
                                       If None, uses the default from config.
    
    Returns:
        dict: Summary of cleanup operation with counts of deleted messages and threads.
    """
    from flask import current_app
    
    if retention_days is None:
        retention_days = current_app.config.get("CHAT_DEFAULT_RETENTION_DAYS", 60)
    
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    
    # Find messages older than cutoff date
    expired_messages = ChatMessage.query.filter(
        ChatMessage.created_at < cutoff_date
    ).all()
    
    message_count = len(expired_messages)
    thread_ids_affected = set()
    
    # Delete expired messages
    for message in expired_messages:
        thread_ids_affected.add(message.thread_id)
        db.session.delete(message)
    
    # Find threads that now have no messages and delete them
    empty_threads = []
    for thread_id in thread_ids_affected:
        remaining_messages = ChatMessage.query.filter_by(thread_id=thread_id).count()
        if remaining_messages == 0:
            thread = ChatThread.query.get(thread_id)
            if thread:
                empty_threads.append(thread)
                db.session.delete(thread)
    
    thread_count = len(empty_threads)
    
    # Commit all deletions
    db.session.commit()
    
    return {
        "messages_deleted": message_count,
        "threads_deleted": thread_count,
        "cutoff_date": cutoff_date.isoformat(),
        "retention_days": retention_days
    }


def cleanup_messages_by_thread(thread_id, retention_days=None):
    """
    Delete messages from a specific thread older than retention period.
    
    Args:
        thread_id (int): ID of the thread to clean up.
        retention_days (int, optional): Number of days to retain messages.
                                       If None, uses thread-specific or default retention.
    
    Returns:
        dict: Summary of cleanup operation.
    """
    from flask import current_app
    
    thread = ChatThread.query.get(thread_id)
    if not thread:
        return {"error": "Thread not found", "messages_deleted": 0}
    
    # Use thread-specific retention if available, otherwise use parameter or default
    if retention_days is None:
        retention_days = thread.retention_days or current_app.config.get("CHAT_DEFAULT_RETENTION_DAYS", 60)
    
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    
    # Find and delete expired messages in this thread
    expired_messages = ChatMessage.query.filter(
        ChatMessage.thread_id == thread_id,
        ChatMessage.created_at < cutoff_date
    ).all()
    
    message_count = len(expired_messages)
    
    for message in expired_messages:
        db.session.delete(message)
    
    # If thread is now empty, delete it
    thread_deleted = False
    remaining_messages = ChatMessage.query.filter_by(thread_id=thread_id).count() - message_count
    if remaining_messages == 0:
        db.session.delete(thread)
        thread_deleted = True
    
    db.session.commit()
    
    return {
        "thread_id": thread_id,
        "messages_deleted": message_count,
        "thread_deleted": thread_deleted,
        "cutoff_date": cutoff_date.isoformat(),
        "retention_days": retention_days
    }


def get_retention_stats():
    """
    Get statistics about message retention and storage usage.
    
    Returns:
        dict: Statistics about messages, threads, and potential cleanup.
    """
    from flask import current_app
    
    total_messages = ChatMessage.query.count()
    total_threads = ChatThread.query.count()
    
    # Count messages by age
    now = datetime.utcnow()
    retention_days = current_app.config.get("CHAT_DEFAULT_RETENTION_DAYS", 60)
    cutoff_date = now - timedelta(days=retention_days)
    
    expired_messages = ChatMessage.query.filter(
        ChatMessage.created_at < cutoff_date
    ).count()
    
    recent_messages = total_messages - expired_messages
    
    return {
        "total_messages": total_messages,
        "total_threads": total_threads,
        "recent_messages": recent_messages,
        "expired_messages": expired_messages,
        "retention_days": retention_days,
        "cutoff_date": cutoff_date.isoformat()
    }

