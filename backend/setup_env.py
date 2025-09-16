#!/usr/bin/env python3
"""
Setup script for Student Life Organizer Backend
This script helps you set up the required environment variables
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with the required environment variables"""
    env_content = """# Student Life Organizer Backend Environment Variables
# Copy this file to .env and fill in your actual values

# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_APP=main.py
FLASK_ENV=development

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///slo.db

# Outlook OAuth Configuration
# You need to register your application in the Azure Portal to get these values
OUTLOOK_CLIENT_ID=your-outlook-client-id
OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
OUTLOOK_REDIRECT_URI=http://localhost:5173/api/calendar/outlook/callback

# Server Configuration
FLASK_RUN_PORT=5000
FLASK_RUN_HOST=0.0.0.0
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file successfully!")
        print("📝 Please edit the .env file and fill in your actual values.")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "OUTLOOK_CLIENT_ID",
        "OUTLOOK_CLIENT_SECRET", 
        "OUTLOOK_REDIRECT_URI"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these environment variables or create a .env file.")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def main():
    print("🚀 Student Life Organizer Backend Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📁 No .env file found.")
        create_env_file()
    else:
        print("📁 .env file found.")
    
    print("\n🔍 Checking environment variables...")
    check_environment()
    
    print("\n📚 Next steps:")
    print("1. If you don't have Outlook OAuth credentials:")
    print("   - Go to https://portal.azure.com")
    print("   - Navigate to 'Azure Active Directory' > 'App registrations'")
    print("   - Create a new registration for your app")
    print("   - Set redirect URI to: http://localhost:5173/api/calendar/outlook/callback")
    print("   - Copy the Client ID and create a Client Secret")
    print("2. Update your .env file with the actual values")
    print("3. Restart your backend server")
    print("4. Try creating a calendar event again")

if __name__ == "__main__":
    main()
