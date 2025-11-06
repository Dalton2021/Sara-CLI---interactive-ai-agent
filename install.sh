#!/bin/bash

# Sara Installation Script
# This script installs Sara and sets it up for terminal use

set -e

echo "======================================"
echo "  Sara AI Assistant Installer"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ Found pip3"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✓ Dependencies installed"
echo ""

# Install the package
echo "📦 Installing Sara..."
pip3 install -e .

echo ""
echo "✓ Sara installed successfully!"
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set."
    echo ""
    echo "To use Sara, you need to set your API key:"
    echo ""
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Add this to your ~/.bashrc or ~/.zshrc to make it permanent:"
    echo ""
    echo "  echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
else
    echo "✓ OPENAI_API_KEY is set"
    echo ""
fi

echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "You can now use Sara by typing:"
echo ""
echo "  sara"
echo ""
echo "For help, use:"
echo ""
echo "  sara --help"
echo ""
echo "Enjoy chatting with Sara! 🎉"