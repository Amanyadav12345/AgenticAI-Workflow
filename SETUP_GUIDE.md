# 📋 Setup Guide for Agentic AI Workflow System

## 🎯 Overview

This guide helps you set up the Agentic AI Workflow System with:
- **Gemini API** for AI processing
- **Your Trip API** for actual trip bookings
- **MCP Server** for Claude Desktop integration
- **Telegram Bot** for natural language interaction

## 🔧 Step-by-Step Setup

### 1. Get Required API Keys

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token (format: `1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`)
4. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

#### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create a new project or select existing one
4. Generate API key
5. Save the API key (format: `AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`)

### 2. Configure Your Trip API

#### API Endpoint Setup
You need to provide:
- **API URL**: Your trip creation endpoint (e.g., `https://api.yourservice.com/trips`)
- **Authentication Token**: Bearer token for API access
- **Expected Payload Structure**: JSON format your API expects

#### Example Trip API Payload
```json
{
  "destination": "Paris, France",
  "start_date": "2025-08-01",
  "end_date": "2025-08-07",
  "travelers": 2,
  "budget": 3000,
  "preferences": {
    "hotel_category": "premium",
    "transport": "flight",
    "meal_preferences": "vegetarian"
  },
  "user_id": "user123",
  "created_via": "agentic_workflow"
}
```

### 3. Environment Configuration

Create your `.env` file:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AUTHORIZED_USERS=123456789,987654321  # Your Telegram user IDs

# Gemini Configuration
GOOGLE_API_KEY=AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
GEMINI_MODEL=gemini-1.5-pro

# Your Trip API Configuration
TRIP_API_URL=https://api.yourservice.com/trips
API_AUTHENTICATION_TOKEN=your_bearer_token_here

# Security
SECRET_KEY=change_this_to_a_secure_random_string
LOG_LEVEL=INFO
```

### 4. Installation & Testing

```bash
# 1. Run setup
./setup.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install additional requirements
pip install google-generativeai mcp mcp-server-stdio

# 4. Test configuration
python main.py status

# 5. Test workflow system
python main.py test
```

### 5. Usage Modes

#### Mode 1: Telegram Bot (Primary)
```bash
python main.py start
```
Send messages like:
- "Create a trip to Tokyo from 2025-08-01 to 2025-08-10 for 2 people with budget $5000"
- "Book a business trip to New York next week"

#### Mode 2: MCP Server (for Claude Desktop)
```bash
python main.py mcp
```
Then configure Claude Desktop (see MCP configuration below).

### 6. MCP Server Configuration for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "workflow-tools": {
      "command": "python",
      "args": ["/Users/aman/Desktop/projects/AgenticAI-Workflow/main.py", "mcp"],
      "cwd": "/Users/aman/Desktop/projects/AgenticAI-Workflow",
      "env": {
        "GOOGLE_API_KEY": "your_gemini_key_here",
        "TRIP_API_URL": "your_api_url_here",
        "API_AUTHENTICATION_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 🧪 Testing Your Setup

### Test 1: System Status
```bash
python main.py status
```
Should show:
- ✅ Telegram Bot: Configured
- ✅ Gemini API: Configured
- ✅ Trip API: Configured

### Test 2: Trip Creation (Simulation)
```bash
python main.py test
```
This runs a simulated workflow to verify all components work.

### Test 3: Real Trip API Test
Send this to your Telegram bot:
```
Create a test trip to Paris from 2025-08-01 to 2025-08-03 for 1 person with budget $1000
```

### Test 4: MCP Server Test
1. Start MCP server: `python main.py mcp`
2. In Claude Desktop, try: "Use the create_trip tool to plan a trip to London"

## 🔧 Customizing for Your API

### Modify Trip Payload Structure

Edit `amanfirstagent/src/amanfirstagent/tools/workflow_tools.py` in the `TripAPITool._create_trip()` method:

```python
# Customize this payload to match your API
payload = {
    "destination": trip_data.get("destination"),
    "start_date": trip_data.get("start_date"),
    "end_date": trip_data.get("end_date"),
    "travelers": trip_data.get("travelers"),
    "budget": trip_data.get("budget"),
    "preferences": trip_data.get("preferences", {}),
    # Add your custom fields here
    "booking_type": "standard",
    "currency": "USD",
    "source": "agentic_ai"
}
```

### Add Custom Headers

Modify the API call headers in the same file:

```python
headers={
    "Authorization": f"Bearer {self.config.api.api_authentication_token}",
    "Content-Type": "application/json",
    # Add your custom headers
    "X-API-Version": "v2",
    "X-Client-ID": "agentic-workflow"
}
```

## 🚨 Common Issues & Solutions

### Issue: "Gemini API key not working"
- Verify key at [Google AI Studio](https://aistudio.google.com/)
- Check if Gemini API is enabled for your project
- Ensure you have quota remaining

### Issue: "Trip API returning 401/403"
- Verify your authentication token
- Check if your API requires specific headers
- Test your API directly with curl first

### Issue: "Telegram bot not responding"
- Verify bot token with [@BotFather](https://t.me/botfather)
- Check that you've sent `/start` to the bot
- Verify your user ID is in AUTHORIZED_USERS

### Issue: "MCP server not connecting to Claude"
- Check the file paths in claude_desktop_config.json
- Ensure Python virtual environment is properly configured
- Check Claude Desktop console for error messages

## 📞 Support

If you encounter issues:

1. Check logs in the `logs/` directory
2. Run with debug mode: `python main.py start --debug`
3. Test each component individually
4. Verify all environment variables are set correctly

## 🎉 You're Ready!

Once everything is configured:

1. **Start the Telegram bot**: `python main.py start`
2. **Send a trip request**: "Plan a trip to Paris for next month"
3. **Watch the magic happen**: The system will parse your request, validate data, call your API, and respond with trip details!

Your agentic AI workflow system is now ready to automate trip bookings through natural language conversations! 🚀