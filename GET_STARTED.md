# 🚀 GET STARTED - Truck Booking System

Your truck booking system is ready to run! Follow these simple steps to get started.

## ⚡ Quick Start (5 minutes)

### 1. Test the System
```bash
python quick_start.py
```
Select option **1** to run the basic workflow test.

### 2. See the Results
You should see:
- 🔍 **Truck Search**: Finds available trucks from Mumbai to Delhi
- 📋 **Trip Details**: Collects consigner, consignee, and parcel info
- 📞 **Owner Contact**: Simulates contacting truck owner
- ✅ **Booking Result**: Shows if booking was successful

### 3. Next Steps
- Try option **2** for the full CrewAI agent system
- Configure your API keys for real integrations

## 📋 Requirements

### Already Installed:
- ✅ Python 3.9+
- ✅ CrewAI and all dependencies
- ✅ Two-agent system (Trip Planner + Availability Verifier)

### Optional (for full features):
- Google Gemini API key (for AI agents)
- Telegram Bot token (for chat interface)

## 🏗️ System Architecture

Your system has **2 AI Agents** working together:

### Agent 1: Trip Planning Specialist
- Searches for available trucks
- Presents options to users
- Collects trip details (consigner, consignee, parcel info)
- Validates all required information

### Agent 2: Availability Verification Specialist
- Contacts truck owners to verify availability
- Confirms or declines bookings
- Handles alternative truck selection

## 🔧 Configuration (Optional)

### Basic Setup:
1. Copy `.env.example` to `.env`
2. Add your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Get API Keys:
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Telegram Bot**: Message @BotFather on Telegram

## 🧪 Test Options

### Option 1: Simple Test (Recommended First)
```bash
python simple_test.py
```
- Tests the core workflow logic
- No API keys required
- Shows simulated truck booking process

### Option 2: Full Agent System
```bash
python quick_start.py
# Select option 2
```
- Full CrewAI agent interaction
- Requires API keys for best experience
- Shows AI agents working together

### Option 3: Individual Components
```bash
# Test just the tools
python test_truck_booking.py
```

## 📱 Integration Options

### 1. Telegram Bot
```bash
python telegram_bot.py
```
Users can chat: "I need a truck from Mumbai to Delhi"

### 2. Web API
```bash
python main.py start
```
RESTful API for integration with websites/apps

### 3. MCP Server (for Claude Desktop)
```bash
python main.py mcp
```
Integrates with Claude Desktop as a tool

## 🔄 Complete Workflow

1. **User Request**: "I need a truck from A to B"
2. **Agent 1** searches and shows available trucks
3. **User** selects a truck
4. **Agent 1** collects trip details:
   - Consigner name and info
   - Consignee name and info  
   - Pickup address
   - Delivery address
   - Parcel size, weight, value
5. **Agent 2** contacts truck owner
6. **Result**: Booking confirmed or try another truck

## 📊 Sample Output

```
Found 2 trucks:
  - TRK001: ABC Transport (Medium Truck) - Rs.2500
  - TRK002: XYZ Logistics (Large Truck) - Rs.3500

Trip details collected:
  Consigner: John Doe
  Consignee: Jane Smith
  Pickup: 123 Main St, Mumbai
  Delivery: 456 Oak Ave, Delhi
  Parcel: 2m x 1m x 1m, 500kg

Contacting truck owner...
Status: Available
Booking Reference: BK19117
```

## 🚨 Troubleshooting

### "Module not found" error:
```bash
pip install -r requirements.txt
```

### "Unicode error" on Windows:
Use `quick_start.py` instead of `start_truck_booking.py`

### Agent test not working:
1. Try simple test first
2. Check if `.env` file has API keys
3. Make sure you're in the main project directory

## 🎯 Next Steps

1. **✅ Test the basic workflow** (you're here!)
2. **🔧 Add your API keys** for full AI features
3. **📱 Try the Telegram bot** for chat interface
4. **🌐 Connect real truck APIs** for live data
5. **💾 Add database** for persistent storage

## 📞 Support

- Check `TRUCK_BOOKING_GUIDE.md` for detailed system docs
- Run tests to verify everything works
- Each component has comprehensive error handling

**🎉 Your truck booking system is ready to use!**

Run `python quick_start.py` and select option 1 to see it in action.