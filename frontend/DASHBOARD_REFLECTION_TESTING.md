# Dashboard Phase 3 Reflection UI - Testing Guide

This guide will walk you through testing the new AI-powered Weekly Reflection feature that integrates with Claude AI.

## 🎯 What You're Testing

The new reflection feature provides:
- **AI-generated weekly summaries** based on your activity data
- **3 reflection prompts** to help you think about your study habits
- **3 actionable recommendations** for the upcoming week
- **Optional goal setting** for personalized advice

---

## 📋 Prerequisites

### 1. Anthropic API Key (Required)
You need a Claude AI API key for the reflection feature to work.

**Get your API key:**
1. Go to https://console.anthropic.com
2. Sign up or log in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### 2. Set Environment Variable
Set the API key in your environment:

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key-here"
```

**Windows Command Prompt:**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## 🚀 Step-by-Step Testing Instructions

### Step 1: Start the Backend Server
```powershell
# Navigate to backend directory
cd backend

# Start the Flask server
python main.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**⚠️ Important:** Keep this terminal window open - the backend must stay running.

### Step 2: Start the Frontend Server
Open a **new terminal window** and run:

```powershell
# Navigate to frontend directory
cd frontend

# Start the development server
npm run dev
```

**Expected output:**
```
  Local:   http://localhost:5173/
  Network: use --host to expose
```

### Step 3: Access the Application
1. Open your web browser
2. Go to `http://localhost:5173`
3. You should see the login page

### Step 4: Login or Register
**Option A - Use existing account:**
- Email: `test2@example.com`
- Password: `test123`

**Option B - Register new account:**
- Click "Register"
- Fill in your details
- Create account and login

### Step 5: Navigate to Dashboard
1. After login, you should see the sidebar navigation
2. Click on **"Dashboard"** in the sidebar
3. You should be redirected to `/dashboard`

### Step 6: Locate the Reflection Section
1. Scroll down to the bottom of the dashboard
2. You should see a section titled **"Weekly Reflection"**
3. The section should contain:
   - A text input field labeled "Optional: set study goals for context"
   - A black button labeled "Generate Reflection"

### Step 7: Test Without Goals
1. Leave the goals field empty
2. Click **"Generate Reflection"** button
3. **Expected behavior:**
   - Button changes to "Generating…"
   - After 2-5 seconds, you should see a success toast
   - Three sections appear below the button:
     - **Summary**: AI-generated overview of your week
     - **Prompts**: 3 bulleted reflection questions
     - **Actions**: 3 bulleted action items

**Example output:**
```
Summary: Based on your activity data, you've had minimal journal entries this week...

Prompts:
• How can you build more consistency in your study routine?
• What obstacles are preventing regular journaling?
• What are your top priorities for next week?

Actions:
• Schedule daily 2-hour study blocks in your calendar
• Set a reminder to write one journal entry each evening
• Review your course syllabi and create weekly study plans
```

### Step 8: Test With Goals
1. Clear any existing reflection by refreshing the page
2. In the goals field, enter something like:
   ```
   Target 14h/week for Algorithms and improve note recall
   ```
3. Click **"Generate Reflection"** again
4. **Expected behavior:**
   - The AI should incorporate your goals into the response
   - Prompts and actions should be more specific to your stated goals

### Step 9: Test Error Handling
**Test missing API key:**
1. Stop the backend server (Ctrl+C)
2. Remove the ANTHROPIC_API_KEY environment variable:
   ```powershell
   Remove-Item Env:ANTHROPIC_API_KEY
   ```
3. Restart the backend server
4. Try generating a reflection
5. **Expected:** You should see an error toast saying "Failed to generate reflection"

**Test network issues:**
1. Stop the backend server while frontend is running
2. Try generating a reflection
3. **Expected:** Error toast about connection failure

---

## ✅ Success Criteria

Your implementation is working correctly if:

- ✅ **UI Renders**: Reflection card appears at bottom of dashboard
- ✅ **Input Works**: Can type goals in the text field
- ✅ **Button States**: Button shows "Generating…" during API calls
- ✅ **API Integration**: Successfully calls `/api/dashboard/reflection` endpoint
- ✅ **Data Display**: Shows summary, prompts, and actions in structured format
- ✅ **Goal Context**: Responses change based on provided goals
- ✅ **Error Handling**: Shows appropriate error messages for failures
- ✅ **Toast Notifications**: Success and error toasts appear
- ✅ **Loading States**: UI properly indicates when processing

---

## 🐛 Troubleshooting

### Issue: "Failed to generate reflection"
**Causes & Solutions:**
1. **Missing API Key**
   - Check environment variable: `echo $env:ANTHROPIC_API_KEY`
   - Ensure it starts with `sk-ant-`
   - Restart backend after setting

2. **Invalid API Key**
   - Verify key is correct from Anthropic console
   - Check for extra spaces or characters

3. **API Rate Limits**
   - Wait a few minutes and try again
   - Check Anthropic console for usage limits

### Issue: Reflection card not visible
**Solutions:**
1. **Clear browser cache** and refresh
2. **Check browser console** for JavaScript errors
3. **Verify build** by running `npm run build`
4. **Check imports** in DashboardPage.tsx

### Issue: Button doesn't respond
**Solutions:**
1. **Check network tab** in browser dev tools
2. **Verify backend is running** on port 5000
3. **Check authentication** - try logging out and back in
4. **Look for console errors** in browser dev tools

### Issue: Malformed responses
**Solutions:**
1. **Check backend logs** for Claude API errors
2. **Verify API key permissions** in Anthropic console
3. **Try with simpler goals** (shorter text)

---

## 🔍 Advanced Testing

### Test Different Scenarios
1. **Empty activity data** (new user)
2. **Rich activity data** (after using journal, chat, etc.)
3. **Very long goals** (test input limits)
4. **Special characters** in goals field
5. **Multiple rapid requests** (test loading states)

### Inspect API Calls
1. Open browser **Developer Tools** (F12)
2. Go to **Network** tab
3. Generate a reflection
4. Look for POST request to `/api/dashboard/reflection`
5. Check request payload and response data

### Test Mobile Responsiveness
1. Open browser dev tools
2. Enable **device emulation**
3. Test on various screen sizes
4. Verify reflection card layout adapts properly

---

## 📊 Sample Data for Testing

If you want more realistic testing data, you can:

1. **Create journal entries** via the Journal page
2. **Use the chat feature** to generate chat_query events
3. **Sync calendar** to generate calendar_sync events
4. **Connect notes** to generate notes_sync events

This will give the AI more data to work with for richer reflections.

---

## 🎉 What's Next?

Once testing is complete, you have a fully functional AI-powered reflection system that:
- Analyzes user activity patterns
- Provides personalized study insights
- Offers actionable recommendations
- Integrates seamlessly with the existing dashboard

The reflection feature helps students develop better self-awareness and study habits through AI-powered coaching!
