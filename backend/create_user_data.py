#!/usr/bin/env python3
"""
Script to create realistic data for a user in the Student Life Organizer database.
Usage: python create_user_data.py <email> <password>
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from main import create_app
from app.extensions import db
from app.models.user import User
from app.models.journal import JournalEntry
from app.models.chat import ChatThread, ChatMessage
from app.models.usage_log import UsageLog

def create_user_data(email, password):
    """Create realistic data for a user."""
    app = create_app()
    
    with app.app_context():
        # Check if user exists, if not create them
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created new user: {email}")
        else:
            print(f"Found existing user: {email}")
        
        # Create journal entries
        print("Creating journal entries...")
        create_journal_entries(user.id)
        
        # Create chat data
        print("Creating chat threads and messages...")
        create_chat_data(user.id)
        
        # Create usage logs
        print("Creating usage logs...")
        create_usage_logs(user.id)
        
        db.session.commit()
        print("✅ All data created successfully!")

def create_journal_entries(user_id):
    """Create realistic journal entries spanning the last few weeks."""
    
    journal_prompts = [
        "Today was a productive day. I managed to complete my assignments for calculus and started working on my history essay. The weather was perfect for a walk around campus, which helped clear my mind. I'm feeling more confident about the upcoming midterms.",
        
        "Had a challenging day in organic chemistry lab. The synthesis didn't go as planned, but my lab partner and I figured out what went wrong. It's frustrating when experiments fail, but I'm learning that failure is part of the scientific process.",
        
        "Joined the debate club today! I was nervous about speaking in front of everyone, but it went better than expected. The topic was about renewable energy policies, and I felt prepared thanks to my environmental science class.",
        
        "Stayed up too late working on my programming project. I finally got the algorithm working, but I need to be better about time management. Coffee is becoming too much of a crutch. Need to establish better sleep habits.",
        
        "Had a great study session with friends at the library. We formed a study group for statistics, and explaining concepts to others really helped me understand them better. Planning to make this a weekly thing.",
        
        "Feeling overwhelmed with all the deadlines coming up. Made a detailed schedule for the next two weeks to help manage everything. Sometimes breaking things down into smaller tasks makes them feel less daunting.",
        
        "Attended a career fair today. Talked to representatives from several tech companies and got some valuable advice about internships. Need to update my resume and start applying soon.",
        
        "Had an interesting discussion in philosophy class about ethics in artificial intelligence. It's fascinating how technology raises so many moral questions. Thinking about taking another philosophy elective next semester.",
        
        "Went to the gym for the first time in weeks. I've been so focused on academics that I forgot how good exercise makes me feel. Going to try to make this a regular habit again.",
        
        "Group project meeting didn't go as planned. One team member hasn't been contributing much, and we need to address this before our presentation next week. Learning that communication is key in collaborative work.",
        
        "Had a breakthrough moment in calculus today. The concept that's been confusing me for weeks suddenly clicked during office hours. Professor Martinez is really good at explaining things differently until they make sense.",
        
        "Feeling homesick today. Called my family and felt much better afterward. It's normal to feel this way sometimes, especially during stressful periods. Grateful for their support and encouragement.",
        
        "Discovered a new coffee shop near campus that's perfect for studying. The atmosphere is quiet but not too quiet, and they have amazing pastries. Found my new favorite study spot.",
        
        "Midterm in microeconomics went better than expected. All those hours of practice problems paid off. Celebrating with friends tonight, then back to studying for the next round of exams.",
        
        "Started reading a book outside of my coursework for the first time this semester. It feels good to read for pleasure again. Need to remember to make time for things I enjoy, not just academics."
    ]
    
    # Create entries over the last 30 days
    for i in range(15):  # 15 entries
        days_ago = random.randint(1, 30)
        entry_date = datetime.utcnow() - timedelta(days=days_ago)
        
        content = random.choice(journal_prompts)
        
        entry = JournalEntry(
            content=content,
            timestamp=entry_date,
            user_id=user_id
        )
        db.session.add(entry)

def create_chat_data(user_id):
    """Create realistic chat threads and messages."""
    
    # Create multiple chat threads
    threads_data = [
        {
            "title": "Study Schedule Help",
            "messages": [
                ("user", "I need help creating a study schedule for my upcoming midterms. I have exams in calculus, chemistry, history, and economics all within two weeks."),
                ("assistant", "I'd be happy to help you create an effective study schedule! Let's start by organizing your exams by date and difficulty level. Can you tell me the specific dates for each exam?"),
                ("user", "Calculus is on March 15th, Chemistry on March 18th, History on March 20th, and Economics on March 22nd."),
                ("assistant", "Perfect! Here's a suggested study plan:\n\n**Week 1 (March 8-14):**\n- Mon-Wed: Focus on Calculus (3 hours/day)\n- Thu-Fri: Chemistry (3 hours/day)\n- Weekend: Light review of History concepts\n\n**Week 2 (March 15-22):**\n- After Calculus exam: Intensive Chemistry review\n- After Chemistry: History deep dive\n- Final days: Economics focus\n\nWould you like me to break this down further?")
            ]
        },
        {
            "title": "Career Advice - Tech Industry",
            "messages": [
                ("user", "I'm interested in pursuing a career in tech after graduation. What skills should I focus on developing?"),
                ("assistant", "Great question! The tech industry values both technical and soft skills. Here are key areas to focus on:\n\n**Technical Skills:**\n- Programming languages (Python, JavaScript, Java)\n- Database management (SQL)\n- Version control (Git)\n- Cloud platforms (AWS, Azure, GCP)\n\n**Soft Skills:**\n- Problem-solving\n- Communication\n- Teamwork\n- Adaptability\n\nWhat specific area of tech interests you most?"),
                ("user", "I'm particularly interested in data science and machine learning."),
                ("assistant", "Excellent choice! For data science and ML, I'd recommend:\n\n**Programming:** Python (pandas, numpy, scikit-learn)\n**Statistics:** Probability, hypothesis testing, regression\n**Visualization:** Matplotlib, Seaborn, Tableau\n**ML Frameworks:** TensorFlow, PyTorch\n**Projects:** Build a portfolio on GitHub\n\nStart with online courses like Coursera's ML course or Kaggle Learn. Hands-on projects are crucial!")
            ]
        },
        {
            "title": "Time Management Tips",
            "messages": [
                ("user", "I'm struggling with time management. I feel like I'm always behind on assignments and stressed about deadlines."),
                ("assistant", "Time management challenges are very common for students. Let's work on some strategies:\n\n1. **Time Audit:** Track how you spend your time for a week\n2. **Prioritization:** Use the Eisenhower Matrix (urgent/important)\n3. **Time Blocking:** Schedule specific times for different activities\n4. **Pomodoro Technique:** 25-minute focused work sessions\n\nWhich of these resonates most with you?"),
                ("user", "The time blocking sounds interesting. How do I start?"),
                ("assistant", "Time blocking is very effective! Here's how to start:\n\n1. **List all activities:** Classes, study time, meals, exercise, sleep\n2. **Estimate time needed:** Be realistic about how long tasks take\n3. **Create blocks:** Use a calendar app or planner\n4. **Include buffer time:** Add 15-minute buffers between blocks\n5. **Color code:** Different colors for different types of activities\n\nStart with just one day, then expand. The key is consistency!")
            ]
        }
    ]
    
    for thread_data in threads_data:
        # Create thread
        thread = ChatThread(
            user_id=user_id,
            title=thread_data["title"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 14))
        )
        db.session.add(thread)
        db.session.flush()  # Get the thread ID
        
        # Create messages
        for i, (role, content) in enumerate(thread_data["messages"]):
            message_time = thread.created_at + timedelta(minutes=i * 2)
            message = ChatMessage(
                thread_id=thread.id,
                user_id=user_id,
                role=role,
                content=content,
                created_at=message_time
            )
            db.session.add(message)

def create_usage_logs(user_id):
    """Create realistic usage logs for analytics."""
    
    # These event types match what the dashboard expects
    events = [
        ("login", {}),
        ("journal_create", {"entry_length": 150}),
        ("journal_create", {"entry_length": 300}),
        ("journal_create", {"entry_length": 250}),
        ("journal_create", {"entry_length": 180}),
        ("journal_create", {"entry_length": 320}),
        ("chat_query", {"query_length": 50}),
        ("chat_query", {"query_length": 120}),
        ("chat_query", {"query_length": 80}),
        ("chat_query", {"query_length": 95}),
        ("calendar_sync", {"events_synced": 3}),
        ("calendar_sync", {"events_synced": 5}),
        ("notes_sync", {"notes_synced": 2}),
        ("notes_sync", {"notes_synced": 4}),
        ("dashboard_viewed", {}),
        ("settings_updated", {"setting": "theme"}),
        ("logout", {}),
        ("login", {}),
        ("dashboard_viewed", {}),
    ]
    
    # Create logs over the last 30 days
    for i in range(len(events) * 3):  # Multiple occurrences
        event_type, metadata = random.choice(events)
        days_ago = random.randint(1, 30)
        log_time = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        log = UsageLog(
            user_id=user_id,
            event_type=event_type,
            event_metadata=metadata,
            created_at=log_time
        )
        db.session.add(log)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user_data.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Creating data for user: {email}")
    create_user_data(email, password)
