# Configuration Template for Student Life Organizer Backend
# Copy this file to config.py and fill in your actual values
# Or set these as environment variables

import os

# Flask Configuration
SECRET_KEY = "your-secret-key-here"  # Change this to a secure random string
JWT_SECRET_KEY = "your-jwt-secret-key-here"  # Change this to a secure random string

# Database Configuration
SQLALCHEMY_DATABASE_URI = "sqlite:///slo.db"

# Outlook OAuth Configuration
# You need to register your application in the Azure Portal to get these values
OUTLOOK_CLIENT_ID = "your-outlook-client-id"  # From Azure App Registration
OUTLOOK_CLIENT_SECRET = "your-outlook-client-secret"  # From Azure App Registration
OUTLOOK_REDIRECT_URI = "http://localhost:5173/api/calendar/outlook/callback"

# Anthropic Claude Configuration (for reflection endpoint)
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"  # Get from https://console.anthropic.com
CLAUDE_MODEL = "claude-3-haiku-20240307"  # Optional: override default model
ANTHROPIC_BASE = "https://api.anthropic.com"  # Optional: override API base URL

# Server Configuration
FLASK_RUN_PORT = 5000
FLASK_RUN_HOST = "0.0.0.0"

def load_config():
    """Load configuration from environment variables or use defaults"""
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", SECRET_KEY),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", JWT_SECRET_KEY),
        "SQLALCHEMY_DATABASE_URI": os.getenv("SQLALCHEMY_DATABASE_URI", SQLALCHEMY_DATABASE_URI),
        "OUTLOOK_CLIENT_ID": os.getenv("OUTLOOK_CLIENT_ID", OUTLOOK_CLIENT_ID),
        "OUTLOOK_CLIENT_SECRET": os.getenv("OUTLOOK_CLIENT_SECRET", OUTLOOK_CLIENT_SECRET),
        "OUTLOOK_REDIRECT_URI": os.getenv("OUTLOOK_REDIRECT_URI", OUTLOOK_REDIRECT_URI),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
        "CLAUDE_MODEL": os.getenv("CLAUDE_MODEL", CLAUDE_MODEL),
        "ANTHROPIC_BASE": os.getenv("ANTHROPIC_BASE", ANTHROPIC_BASE),
        "FLASK_RUN_PORT": int(os.getenv("FLASK_RUN_PORT", FLASK_RUN_PORT)),
        "FLASK_RUN_HOST": os.getenv("FLASK_RUN_HOST", FLASK_RUN_HOST),
    }

# Instructions for setting up Outlook OAuth:
# 1. Go to https://portal.azure.com
# 2. Navigate to "Azure Active Directory" > "App registrations"
# 3. Click "New registration"
# 4. Give your app a name (e.g., "Student Life Organizer")
# 5. Set the redirect URI to: http://localhost:5173/api/calendar/outlook/callback
# 6. After registration, go to "Certificates & secrets"
# 7. Create a new client secret and copy the value
# 8. Copy the Application (client) ID
# 9. Set these values in your environment variables or update this file

# Instructions for setting up Anthropic Claude API:
# 1. Go to https://console.anthropic.com
# 2. Sign up or log in to your account
# 3. Navigate to "API Keys" section
# 4. Create a new API key
# 5. Copy the API key and set it as ANTHROPIC_API_KEY
# 6. The reflection endpoint will use this to generate weekly study summaries
