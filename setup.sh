#!/bin/bash

# Agentic AI Workflow System Setup Script

set -e

echo "🤖 Agentic AI Workflow System Setup"
echo "=================================="

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups

# Copy environment template
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
else
    echo "✅ Environment file already exists"
fi

# Set executable permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod +x telegram_bot.py

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - Add your Telegram bot token"
echo "   - Add your OpenAI API key"
echo "   - Configure authorized users"
echo ""
echo "2. Test the system:"
echo "   python main.py test"
echo ""
echo "3. Check system status:"
echo "   python main.py status"
echo ""
echo "4. Start the bot:"
echo "   python main.py start"
echo ""
echo "For more information, see README.md"