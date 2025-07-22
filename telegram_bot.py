#!/usr/bin/env python3
"""
Telegram Bot Integration for Agentic AI Workflow System
Monitors chat messages and triggers workflow execution via CrewAI agents
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

from amanfirstagent.src.amanfirstagent.workflow_crew import WorkflowCrew
from utils.security import SecurityManager
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

class TelegramWorkflowBot:
    """
    Telegram bot that monitors messages and executes workflows via CrewAI agents
    """
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.authorized_users = self._load_authorized_users()
        self.security_manager = SecurityManager()
        self.workflow_crew = WorkflowCrew()
        self.logger = setup_logger("telegram_bot")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    def _load_authorized_users(self) -> List[str]:
        """Load authorized user IDs from environment"""
        users_env = os.getenv("AUTHORIZED_USERS", "")
        return [user.strip() for user in users_env.split(",") if user.strip()]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        
        if not self._is_authorized_user(user_id):
            await update.message.reply_text("⚠️ You are not authorized to use this bot.")
            self.logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        
        welcome_message = """
🤖 **Agentic AI Workflow Bot**

I can help you automate complex workflows by understanding your natural language instructions!

**Available Commands:**
• `/help` - Show this help message
• `/status` - Check system status
• `/history` - View recent workflow executions

**Usage:**
Just type your workflow request in natural language. For example:
• "Create a new user John Doe with email john@example.com in the CRM"
• "Generate a report for last month's sales data"
• "Update inventory for product ABC-123 to 50 units"

Let's get started! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        self.logger.info(f"Start command executed by user {user_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """
🔧 **Workflow Bot Commands**

• `/start` - Initialize the bot
• `/help` - Show this help message
• `/status` - Check system status and agent health
• `/history` - View your recent workflow executions
• `/cancel` - Cancel current running workflow

**How to use:**
1. Type your request in natural language
2. The bot will interpret your intent
3. Specialized AI agents will execute the workflow
4. You'll receive real-time updates and results

**Example requests:**
• "Add new customer: Name: Alice Smith, Email: alice@company.com"
• "Check inventory status for all products"
• "Send weekly report to management team"
• "Update user permissions for john.doe@company.com"
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command - show system status"""
        user_id = str(update.effective_user.id)
        
        if not self._is_authorized_user(user_id):
            await update.message.reply_text("⚠️ Unauthorized access.")
            return
        
        status_info = await self._get_system_status()
        await update.message.reply_text(status_info, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle incoming messages and process workflow requests
        """
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Security check
        if not self._is_authorized_user(user_id):
            await update.message.reply_text("⚠️ You are not authorized to use this bot.")
            self.security_manager.log_unauthorized_access(user_id, message_text)
            return
        
        # Log incoming message
        self.logger.info(f"Message from user {user_id}: {message_text}")
        
        # Security validation
        if not self.security_manager.validate_message(message_text):
            await update.message.reply_text("⚠️ Message contains potentially unsafe content.")
            return
        
        # Send initial acknowledgment
        processing_msg = await update.message.reply_text("🔄 Processing your request...")
        
        try:
            # Process the workflow request
            result = await self._process_workflow_request(
                user_id=user_id,
                message=message_text,
                update=update
            )
            
            # Update the processing message with results
            await processing_msg.edit_text(result)
            
        except Exception as e:
            error_msg = f"❌ Error processing your request: {str(e)}"
            await processing_msg.edit_text(error_msg)
            self.logger.error(f"Error processing workflow for user {user_id}: {e}")
    
    async def _process_workflow_request(self, user_id: str, message: str, update: Update) -> str:
        """
        Process workflow request using CrewAI agents
        """
        try:
            # Create workflow context
            workflow_context = {
                'user_id': user_id,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'chat_id': update.effective_chat.id
            }
            
            # Execute workflow via CrewAI
            result = await self.workflow_crew.execute_workflow(workflow_context)
            
            # Format response
            if result.get('success'):
                response = f"✅ **Workflow Completed Successfully**\n\n"
                response += f"**Summary:** {result.get('summary', 'Task completed')}\n"
                
                if result.get('details'):
                    response += f"**Details:** {result['details']}\n"
                
                if result.get('actions_taken'):
                    response += f"**Actions Taken:**\n"
                    for action in result['actions_taken']:
                        response += f"• {action}\n"
            else:
                response = f"⚠️ **Workflow Completed with Issues**\n\n"
                response += f"**Summary:** {result.get('summary', 'Task had issues')}\n"
                response += f"**Error:** {result.get('error', 'Unknown error')}\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            return f"❌ **Workflow Failed**\n\nError: {str(e)}"
    
    def _is_authorized_user(self, user_id: str) -> bool:
        """Check if user is authorized"""
        if not self.authorized_users:
            return True  # If no users configured, allow all (for development)
        return user_id in self.authorized_users
    
    async def _get_system_status(self) -> str:
        """Get system status information"""
        try:
            # Check agent status
            agent_status = await self.workflow_crew.get_agents_status()
            
            status_text = "🔧 **System Status**\n\n"
            status_text += f"**Bot Status:** ✅ Online\n"
            status_text += f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            status_text += "**Agent Status:**\n"
            for agent_name, status in agent_status.items():
                status_emoji = "✅" if status == "healthy" else "⚠️"
                status_text += f"• {agent_name}: {status_emoji} {status}\n"
            
            return status_text
            
        except Exception as e:
            return f"❌ **Status Check Failed**\n\nError: {str(e)}"
    
    def run(self):
        """Start the bot"""
        try:
            # Create application
            application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            self.logger.info("Telegram bot starting...")
            
            # Start the bot
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise

def main():
    """Main entry point"""
    bot = TelegramWorkflowBot()
    bot.run()

if __name__ == "__main__":
    main()