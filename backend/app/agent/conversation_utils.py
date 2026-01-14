# app/agent/conversation_utils.py
import re
from typing import List, Dict, Any

def is_confirmation_message(user_text: str) -> bool:
    """Detect if a user message is a confirmation/agreement."""
    text = user_text.lower().strip()
    
    # Direct confirmations
    confirmations = [
        "yes", "yep", "yeah", "y", "yup", "sure", "ok", "okay", "alright", "all right",
        "go ahead", "proceed", "do it", "go for it", "that's right", "correct",
        "exactly", "absolutely", "definitely", "of course", "indeed", "confirm",
        "confirmed", "approved", "agreed", "agree", "sounds good", "looks good",
        "perfect", "right", "true", "affirmative", "👍", "✓", "✅"
    ]
    
    # Check for exact matches
    if text in confirmations:
        return True
    
    # Check for phrases that indicate confirmation
    confirmation_phrases = [
        r"^yes,?\s*(please|go ahead|do it|proceed)",
        r"^that'?s?\s*(correct|right|good|perfect)",
        r"^sounds?\s*good",
        r"^looks?\s*good",
        r"^i\s*(want|would like)\s*to\s*(proceed|continue|go ahead)",
        r"please\s*(go ahead|proceed|do it)",
        r"^(go|do)\s*(ahead|it)",
    ]
    
    for pattern in confirmation_phrases:
        if re.search(pattern, text):
            return True
    
    return False

def is_denial_message(user_text: str) -> bool:
    """Detect if a user message is a denial/disagreement."""
    text = user_text.lower().strip()
    
    denials = [
        "no", "nope", "nah", "n", "never", "not", "cancel", "stop", "abort",
        "don't", "dont", "never mind", "nevermind", "forget it", "no thanks",
        "no thank you", "i changed my mind", "actually no", "wait", "hold on",
        "❌", "✗", "❎"
    ]
    
    if text in denials:
        return True
    
    denial_phrases = [
        r"^no,?\s*(don'?t|stop|cancel|wait)",
        r"^(don'?t|stop|cancel)\s*(do|go)",
        r"i\s*(don'?t|do not)\s*want",
        r"^actually,?\s*no",
        r"^on second thought",
        r"^wait,?\s*(no|stop)",
    ]
    
    for pattern in denial_phrases:
        if re.search(pattern, text):
            return True
    
    return False

def extract_pending_action_from_history(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract the most recent pending action from conversation history."""
    
    # Look for recent user request that might need action
    user_request = None
    assistant_asked_confirmation = False
    
    # Scan recent messages (last 6 messages should cover most confirmation flows)
    recent_messages = messages[-6:] if len(messages) > 6 else messages
    
    for msg in reversed(recent_messages):
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            
            # Check if assistant asked for confirmation
            confirmation_patterns = [
                r"are you sure.*want.*delete",
                r"confirm.*delete", 
                r"want.*proceed.*delet",
                r"should i.*delete",
                r"let me confirm.*are you sure",
                r"want me to.*delete",
                r"this seems to be.*delete.*confirm",
                r"make sure.*intended.*before proceeding",
                r"proceed with deleting"
            ]
            
            for pattern in confirmation_patterns:
                if re.search(pattern, content):
                    assistant_asked_confirmation = True
                    break
                    
        elif msg.get("role") == "user" and not user_request:
            content = msg.get("content", "").lower()
            
            # Look for user requests that need action
            if "delete" in content:
                if "journal" in content:
                    user_request = {
                        "action": "delete_journal",
                        "context": "User requested to delete a journal entry",
                        "content": content,
                        "confidence": "high"
                    }
                elif "calendar" in content:
                    user_request = {
                        "action": "delete_calendar_event",
                        "context": "User requested to delete a calendar event", 
                        "content": content,
                        "confidence": "high"
                    }
                elif "task" in content:
                    user_request = {
                        "action": "delete_task",
                        "context": "User requested to delete a task",
                        "content": content,
                        "confidence": "high"
                    }
                else:
                    user_request = {
                        "action": "delete_something",
                        "context": "User requested to delete something",
                        "content": content,
                        "confidence": "medium"
                    }
    
    # If we found both a user request and assistant confirmation, return the request
    if user_request and assistant_asked_confirmation:
        return user_request
    
    return {"action": None, "context": None, "confidence": "none"}
