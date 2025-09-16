# User Data Creation Script

This script creates realistic sample data for a user in the Student Life Organizer database.

## Usage

```bash
cd backend
python create_user_data.py <email> <password>
```

## Example

```bash
python create_user_data.py "student@university.edu" "mypassword123"
```

## What Data Gets Created

The script creates the following realistic data for the specified user:

### 📝 Journal Entries (15 entries)
- Realistic student journal entries spanning the last 30 days
- Covers topics like:
  - Academic challenges and successes
  - Study sessions and group work
  - Career planning and internships
  - Time management struggles
  - Campus life experiences
  - Personal growth moments

### 💬 Chat Data (3 threads with multiple messages)
- **Study Schedule Help**: Conversation about creating midterm study plans
- **Career Advice - Tech Industry**: Discussion about tech career paths and data science
- **Time Management Tips**: Advice on productivity and time blocking techniques

### 📊 Usage Logs (45+ entries)
- Login/logout events
- Journal creation and editing activities
- Chat interactions
- Dashboard and settings usage
- Distributed across the last 30 days for realistic analytics

## Database Tables Populated

- `user` - Creates or finds existing user
- `journal_entry` - Student journal entries
- `chat_thread` - Conversation threads
- `chat_message` - Individual messages in conversations
- `usage_log` - User activity tracking for analytics

## Requirements

- The Flask app must be properly configured
- Database must be initialized (`python init_db.py`)
- All required environment variables should be set

## Notes

- If the user already exists, the script will add data to the existing user
- All timestamps are realistic and distributed over the past 30 days
- The data is designed to showcase all features of the Student Life Organizer

