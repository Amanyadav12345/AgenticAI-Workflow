#!/usr/bin/env python3
"""
Main entry point for the Agentic AI Workflow System
"""

import argparse
import asyncio
import sys
from datetime import datetime

from config import get_config, reload_config
from telegram_bot import TelegramWorkflowBot
from utils.logger import setup_logger
from utils.security import SecurityManager

def check_requirements():
    """Check system requirements and configuration"""
    config = get_config()
    logger = setup_logger("main")
    
    logger.info("🔍 Checking system requirements...")
    
    # Validate configuration
    issues = config.validate_config()
    
    if issues:
        logger.error("❌ Configuration issues found:")
        for component, component_issues in issues.items():
            for issue in component_issues:
                logger.error(f"  - {component}: {issue}")
        
        if any('required' in str(issue).lower() for component_issues in issues.values() for issue in component_issues):
            logger.error("❌ Critical configuration issues found. Please fix before continuing.")
            return False
        else:
            logger.warning("⚠️  Configuration warnings found. System will continue but may have limited functionality.")
    
    # Check required packages
    try:
        import crewai
        import telegram
        logger.info("✅ Required packages available")
    except ImportError as e:
        logger.error(f"❌ Missing required package: {e}")
        logger.error("Please run: source venv/bin/activate && pip install -r requirements.txt")
        return False
    
    logger.info("✅ System requirements check completed")
    return True

async def run_telegram_bot():
    """Run the Telegram bot"""
    logger = setup_logger("main")
    
    try:
        logger.info("🚀 Starting Telegram Workflow Bot...")
        bot = TelegramWorkflowBot()
        await asyncio.to_thread(bot.run)
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise

def run_test_workflow():
    """Run a test workflow to verify system functionality"""
    logger = setup_logger("test")
    
    logger.info("🧪 Running test workflow...")
    
    try:
        from amanfirstagent.src.amanfirstagent.workflow_crew import WorkflowCrew
        
        workflow_crew = WorkflowCrew()
        
        # Test workflow context
        test_context = {
            'user_id': 'test_user',
            'message': 'Create a new user named Alice Smith with email alice@example.com',
            'timestamp': datetime.now().isoformat()
        }
        
        # Run workflow synchronously for testing
        result = asyncio.run(workflow_crew.execute_workflow(test_context))
        
        if result.get('success'):
            logger.info("✅ Test workflow completed successfully")
            logger.info(f"📋 Summary: {result.get('summary', 'N/A')}")
        else:
            logger.error(f"❌ Test workflow failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test workflow crashed: {e}")
        return False

def show_status():
    """Show system status and configuration"""
    config = get_config()
    logger = setup_logger("status")
    
    print("\n🤖 Agentic AI Workflow System Status")
    print("=" * 50)
    
    # Configuration status
    print(f"📋 Configuration:")
    print(f"  - Telegram Bot: {'✅ Configured' if config.telegram.bot_token else '❌ Missing token'}")
    print(f"  - Gemini API: {'✅ Configured' if config.api.google_api_key else '❌ Missing key'}")
    print(f"  - Trip API: {'✅ Configured' if config.api.trip_api_url else '❌ Missing URL'}")
    print(f"  - Authorized Users: {len(config.telegram.authorized_users)} users")
    print(f"  - Model: {config.api.gemini_model}")
    print(f"  - Log Level: {config.logging.level}")
    
    # Security status
    security_manager = SecurityManager()
    try:
        security_report = security_manager.get_security_report()
        print(f"\n🔒 Security:")
        print(f"  - Total Events: {security_report.get('total_events', 0)}")
        print(f"  - High Severity: {security_report.get('high_severity_events', 0)}")
    except Exception as e:
        print(f"  - Security Report: ❌ Error: {e}")
    
    # Workflow capabilities
    print(f"\n⚙️  Workflow Capabilities:")
    print(f"  - Max Concurrent: {config.workflow.max_concurrent_workflows}")
    print(f"  - Timeout: {config.workflow.workflow_timeout}s")
    print(f"  - Memory: {'✅ Enabled' if config.workflow.enable_memory else '❌ Disabled'}")
    print(f"  - Planning: {'✅ Enabled' if config.workflow.enable_planning else '❌ Disabled'}")
    
    # External integrations
    integrations = config.get_external_integrations()
    print(f"\n🔗 External Integrations:")
    for service, service_config in integrations.items():
        if service == 'database_connections':
            continue
        
        configured = any(bool(value) for value in service_config.values() if isinstance(value, str))
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"  - {service.replace('_', ' ').title()}: {status}")
    
    print("\n" + "=" * 50)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic AI Workflow System")
    parser.add_argument("command", choices=["start", "test", "status", "config", "mcp"], 
                       help="Command to execute")
    parser.add_argument("--reload-config", action="store_true", 
                       help="Reload configuration before executing")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Reload config if requested
    if args.reload_config:
        reload_config()
    
    # Set debug logging if requested
    if args.debug:
        import os
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Execute command
    if args.command == "start":
        if not check_requirements():
            sys.exit(1)
        
        print("🤖 Starting Agentic AI Workflow System...")
        print("Press Ctrl+C to stop")
        
        try:
            asyncio.run(run_telegram_bot())
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)
    
    elif args.command == "test":
        if not check_requirements():
            sys.exit(1)
        
        success = run_test_workflow()
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        show_status()
    
    elif args.command == "config":
        config = get_config()
        print("💾 Saving current configuration to config.json...")
        config.save_config()
        print("✅ Configuration saved")
    
    elif args.command == "mcp":
        print("🔌 Starting MCP Server for workflow tools...")
        print("This server provides tools via MCP protocol for Claude Desktop and other MCP clients")
        print("Press Ctrl+C to stop")
        
        try:
            from start_mcp_server import main as mcp_main
            mcp_main()
        except KeyboardInterrupt:
            print("\n👋 MCP Server stopped!")
        except Exception as e:
            print(f"\n❌ MCP Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()