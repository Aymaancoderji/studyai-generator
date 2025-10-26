#!/bin/bash

echo "🧠 StudyAI Setup Script"
echo "======================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p output
mkdir -p temp
mkdir -p config
mkdir -p core
mkdir -p database
mkdir -p utils

# Create __init__.py files
echo ""
echo "Creating module files..."
touch config/__init__.py
touch core/__init__.py
touch database/__init__.py
touch utils/__init__.py

# Setup .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file and add your API keys!"
    echo ""
    echo "To get API keys:"
    echo "  - OpenAI: https://platform.openai.com/api-keys"
    echo "  - Groq: https://console.groq.com"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "     source venv/Scripts/activate"
else
    echo "     source venv/bin/activate"
fi
echo "  3. Run the CLI tool:"
echo "     python studyai.py --help"
echo "  4. Or launch the dashboard:"
echo "     streamlit run streamlit_app.py"
echo ""
echo "Happy learning! 🎓"
