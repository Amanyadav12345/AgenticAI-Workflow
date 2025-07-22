# 🤖 Agentic AI Workflow System

An intelligent workflow automation system that monitors Telegram chat messages and automatically executes complex workflows using specialized AI agents powered by CrewAI.

## 🌟 Features

- **Natural Language Processing**: Understands plain English instructions
- **Multi-Agent Orchestration**: Specialized AI agents for different workflow tasks
- **Real-time Monitoring**: Watches Telegram channels for user commands
- **Secure Operations**: Built-in security validation and audit logging
- **Flexible Integrations**: Connects to APIs, databases, and external systems
- **Error Handling**: Graceful error recovery with user feedback
- **Comprehensive Logging**: Detailed activity and security logs

## 🏗️ System Architecture

### Core Components

1. **Telegram Integration Layer**
   - Real-time message monitoring
   - User authentication and authorization
   - Natural language command parsing

2. **CrewAI Agent Orchestra**
   - **Message Interpreter Agent**: Analyzes user intent and extracts parameters
   - **Workflow Orchestrator Agent**: Plans and coordinates complex workflows
   - **API Integration Agent**: Handles external system interactions
   - **Validation Agent**: Ensures data quality and workflow integrity

3. **Security & Monitoring**
   - Input validation and sanitization
   - Comprehensive audit logging
   - User authorization and session management

4. **Integration Tools**
   - Database operations
   - API integrations
   - File operations
   - Notification services

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Telegram Bot API token
- Google Gemini API key
- Your Trip API endpoint (optional - system works with simulation mode)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd AgenticAI-Workflow
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Required environment variables:**
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   TRIP_API_URL=your_trip_api_endpoint_here
   API_AUTHENTICATION_TOKEN=your_api_token_here
   AUTHORIZED_USERS=user_id1,user_id2,user_id3
   ```

4. **Test the system:**
   ```bash
   python main.py test
   ```

5. **Start the bot:**
   ```bash
   python main.py start
   ```

6. **Start MCP Server (optional - for Claude Desktop integration):**
   ```bash
   python main.py mcp
   ```

## 💬 Usage Examples

Once the bot is running, you can send natural language commands:

### Trip Management
```
"Create a trip to Paris from 2025-08-01 to 2025-08-07 for 2 people with budget $3000"
"Book a business trip to New York departing tomorrow for 3 days"
"Plan a vacation to Tokyo from July 15-25 for 4 travelers, budget $8000"
"Update my trip to London, change the hotel to premium category"
```

### Data Operations
```
"Generate monthly sales report for December 2024"
"Update inventory for product SKU-123 to 50 units"
"Export customer data to CSV for marketing team"
```

### System Tasks
```
"Send notification to all team leads about the meeting"
"Create backup of user database"
"Run data validation check on customer records"
```

### API Integrations
```
"Sync customer data from CRM to analytics database"
"Post message to #general slack channel about system maintenance"
"Create ticket in JIRA for bug report from user feedback"
```

## 🔧 Commands

The bot supports several built-in commands:

- `/start` - Initialize the bot and show welcome message
- `/help` - Display help information and usage examples
- `/status` - Check system status and agent health
- `/history` - View recent workflow executions

## 🔌 MCP Server Integration

The system includes an MCP (Model Context Protocol) server that provides workflow tools to Claude Desktop and other MCP clients.

### Available MCP Tools

1. **create_trip** - Create new trips with validation
2. **call_api** - Make HTTP requests to external APIs
3. **validate_data** - Validate data against rules
4. **send_notification** - Send notifications via various channels
5. **process_file** - Handle file operations
6. **parse_trip_request** - Parse natural language trip requests

### Starting the MCP Server

```bash
python main.py mcp
```

### Configuring Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "workflow-tools": {
      "command": "python",
      "args": ["/path/to/your/project/main.py", "mcp"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## 🔒 Security

### Built-in Security Features

- **Input Validation**: All user inputs are validated for safety
- **Pattern Detection**: Dangerous command patterns are blocked
- **Audit Logging**: All actions are logged for security review
- **User Authorization**: Only authorized users can execute workflows
- **Data Sanitization**: Sensitive data is masked in logs

---

**⚠️ Security Notice**: This system can execute powerful automation workflows. Always review and test workflows in a safe environment before production use. Keep your API keys secure and regularly audit system access.