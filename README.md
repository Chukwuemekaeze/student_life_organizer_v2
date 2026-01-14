# 📚 Student Life Organizer (SLO)

A local-first academic assistant designed to help students manage their journals, notes, tasks, and calendar events with integrated AI capabilities powered by Claude.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.x-cyan.svg)

## ✨ Features

### Core Functionality
- **📓 Journal Management** - Create, edit, and search journal entries with streak tracking
- **✅ Task Management** - Full CRUD operations with priority levels, due dates, and status tracking
- **📅 Calendar Integration** - Sync with Microsoft Outlook calendar via OAuth 2.0
- **📝 Notes Sync** - Integration with Notion for note syncing
- **📊 Analytics Dashboard** - Activity metrics, heatmaps, and journal streaks visualization

### AI-Powered Features
- **🤖 AI Chat Agent** - Conversational interface powered by Claude (Anthropic)
- **🔧 Tool-based Actions** - AI can create journals, manage tasks, and interact with your calendar
- **💡 Weekly Reflections** - AI-generated summaries and study recommendations
- **🎯 Natural Language Task Input** - Quick-add tasks using natural language (e.g., "Finish essay by Friday 5pm, high priority")

### User Experience
- **🔐 JWT Authentication** - Secure user registration and login
- **🔔 Notifications** - In-app notification system
- **📱 Responsive Design** - Mobile-first UI with Tailwind CSS
- **💬 Modern Chat Interface** - ChatGPT-like experience for AI interactions

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Flask 3.x | Web framework |
| SQLAlchemy 2.x | ORM & database management |
| Flask-Migrate | Database migrations (Alembic) |
| Flask-JWT-Extended | JWT authentication |
| Flask-CORS | Cross-origin resource sharing |
| Anthropic SDK | Claude AI integration |
| SQLite | Database (MVP) |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type-safe development |
| Vite | Build tool & dev server |
| Tailwind CSS | Styling |
| React Router | Client-side routing |
| Zustand | State management |
| Jotai | Atomic state management |
| Axios | HTTP client |
| Recharts | Data visualization |
| Lucide React | Icon library |

## 📁 Project Structure

```
student_life_organizer_v2/
├── backend/
│   ├── app/
│   │   ├── agent/           # AI agent implementation
│   │   │   ├── context.py   # Agent context management
│   │   │   ├── guard.py     # Permission & scope handling
│   │   │   ├── router.py    # Agent routing logic
│   │   │   ├── routes.py    # Agent API endpoints
│   │   │   └── tools.py     # Agent tool definitions
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── journal.py
│   │   │   ├── task.py
│   │   │   ├── chat.py
│   │   │   └── ...
│   │   ├── routes/          # API blueprints
│   │   │   ├── auth.py
│   │   │   ├── journal.py
│   │   │   ├── tasks.py
│   │   │   ├── calendar.py
│   │   │   ├── dashboard.py
│   │   │   ├── ai.py
│   │   │   └── ...
│   │   ├── services/        # Business logic
│   │   │   ├── ai_client.py
│   │   │   ├── calendar.py
│   │   │   ├── reflection.py
│   │   │   └── ...
│   │   └── utils/           # Utility functions
│   ├── migrations/          # Alembic migrations
│   ├── main.py              # Application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── journal/
│   │   │   ├── tasks/
│   │   │   ├── chat/
│   │   │   └── ...
│   │   ├── services/        # API service functions
│   │   ├── store/           # State management
│   │   ├── hooks/           # Custom React hooks
│   │   └── types/           # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```powershell
   python setup_env.py
   ```
   
   Or manually create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   SQLALCHEMY_DATABASE_URI=sqlite:///slo.db
   ANTHROPIC_API_KEY=your-anthropic-api-key
   OUTLOOK_CLIENT_ID=your-outlook-client-id
   OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
   OUTLOOK_REDIRECT_URI=http://localhost:5173/api/calendar/outlook/callback
   ```

5. **Initialize the database:**
   ```powershell
   flask db upgrade
   ```

6. **Start the backend server:**
   ```powershell
   python main.py
   ```
   The API will be available at `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Start the development server:**
   ```powershell
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create a new user account |
| POST | `/api/auth/login` | Login and receive JWT token |

### Journal
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/journal` | List journal entries (paginated) |
| POST | `/api/journal` | Create a new journal entry |
| GET | `/api/journal/:id` | Get a specific journal entry |
| PUT | `/api/journal/:id` | Update a journal entry |
| DELETE | `/api/journal/:id` | Delete a journal entry |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks with filters |
| POST | `/api/tasks` | Create a new task |
| POST | `/api/tasks/quickadd` | Create task from natural language |
| PATCH | `/api/tasks/:id` | Update a task |
| DELETE | `/api/tasks/:id` | Delete a task |

### Calendar
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/outlook/start` | Start Outlook OAuth flow |
| GET | `/api/calendar/outlook/callback` | OAuth callback handler |
| GET | `/api/calendar/sync` | Sync calendar events |

### AI / Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Chat with AI assistant |
| POST | `/api/agent/chat` | Agent-based chat with tools |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/metrics` | Get weekly activity metrics |
| GET | `/api/dashboard/series` | Get time-series activity data |
| GET | `/api/dashboard/streaks` | Get journal streak data |
| GET | `/api/dashboard/heatmap` | Get activity heatmap data |
| POST | `/api/dashboard/reflection` | Generate AI weekly reflection |

## ⚙️ Configuration

### Outlook OAuth Setup (Optional)
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Create a new registration
4. Set redirect URI to `http://localhost:5173/api/calendar/outlook/callback`
5. Create a client secret
6. Copy Client ID and Secret to your `.env` file

### Anthropic API Setup
1. Go to [Anthropic Console](https://console.anthropic.com)
2. Create an API key
3. Add to your `.env` file as `ANTHROPIC_API_KEY`

## 🧪 Testing

### Creating Test Data
```powershell
cd backend
python create_user_data.py test@example.com password123
```

### API Testing with cURL
Example scripts are available in `backend/scripts/`:
- `curl_tests.sh` - General API tests
- `test_task_sync.sh` - Task synchronization tests

## 📝 Development Notes

### Database Migrations
```powershell
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

### Environment
- Development runs on SQLite
- JWT tokens are used for authentication
- CORS is configured for localhost ports 5173-5175

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational and personal use.

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude AI
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/) for Outlook integration
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [shadcn/ui](https://ui.shadcn.com/) for UI components inspiration
