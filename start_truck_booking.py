#!/usr/bin/env python
"""
Truck Booking System Startup Script

This script helps you get started with the truck booking agent system.
It provides multiple ways to run and test the system.
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def print_banner():
    """Print the system banner"""
    print("=" * 60)
    print("TRUCK BOOKING AGENT SYSTEM")
    print("=" * 60)
    print("Two-Agent System for Truck Booking Workflow")
    print("- Agent 1: Trip Planning (Search, Select, Collect Details)")
    print("- Agent 2: Availability Verification (Contact Owners)")
    print("=" * 60)

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking Dependencies...")
    
    required_packages = [
        'crewai', 'python-telegram-bot', 'python-dotenv', 
        'google-generativeai', 'requests', 'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("All dependencies installed!")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking Environment...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 .env file not found. Copying from .env.example...")
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  IMPORTANT: Edit .env file with your API keys!")
            return False
        else:
            print("❌ No .env or .env.example file found")
            return False
    
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
            print(f"❌ {var} - Not configured")
        else:
            print(f"✅ {var}")
    
    if missing_vars:
        print(f"\n⚠️  Configure these in .env file: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configured!")
    return True

def ensure_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    dirs = ['logs', 'data', 'backups']
    
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    print("✅ Directories ready!")

def run_simple_test():
    """Run the simple test"""
    print("\n🧪 Running Simple Test...")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'simple_test.py'], 
                              capture_output=False, text=True, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_crewai_test():
    """Run CrewAI-based test"""
    print("\n🤖 Running CrewAI Agent Test...")
    print("-" * 40)
    
    try:
        # Add the amanfirstagent src to Python path
        agent_path = Path('amanfirstagent/src').absolute()
        env = os.environ.copy()
        env['PYTHONPATH'] = str(agent_path) + os.pathsep + env.get('PYTHONPATH', '')
        
        result = subprocess.run([
            sys.executable, '-m', 'amanfirstagent.main', 'truck_booking'
        ], capture_output=False, text=True, cwd=agent_path, env=env)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ CrewAI test failed: {e}")
        print("💡 Tip: Try the simple test first to verify the workflow logic")
        return False

def start_telegram_bot():
    """Start the Telegram bot"""
    print("\n🤖 Starting Telegram Bot...")
    print("-" * 40)
    print("Press Ctrl+C to stop the bot")
    
    try:
        subprocess.run([sys.executable, 'telegram_bot.py'])
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Check system readiness
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return False
    
    if not check_environment():
        print("\n❌ Please configure your environment first")
        print("💡 Edit .env file with your API keys")
        return False
    
    ensure_directories()
    
    print("\n🎯 WHAT WOULD YOU LIKE TO DO?")
    print("-" * 40)
    print("1. Run Simple Test (Recommended for first time)")
    print("2. Run CrewAI Agent Test")
    print("3. Start Telegram Bot")
    print("4. View System Guide")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            success = run_simple_test()
            if success:
                print("\n✅ Simple test completed successfully!")
                print("💡 Next: Try option 2 for the full CrewAI experience")
            break
            
        elif choice == '2':
            success = run_crewai_test()
            if success:
                print("\n✅ CrewAI test completed successfully!")
                print("💡 Next: Try option 3 to start the Telegram bot")
            break
            
        elif choice == '3':
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
                print("❌ Telegram bot token not configured in .env file")
                print("💡 Get a token from @BotFather and add it to .env")
            else:
                start_telegram_bot()
            break
            
        elif choice == '4':
            guide_file = Path('TRUCK_BOOKING_GUIDE.md')
            if guide_file.exists():
                print(f"\n📖 System guide available at: {guide_file.absolute()}")
                print("💡 Open this file in a text editor or markdown viewer")
            else:
                print("❌ System guide not found")
            break
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")
    
    return True

if __name__ == "__main__":
    main()