#!/bin/bash
# Installation script for Sara AI Terminal Agent

set -e

echo "🤖 Installing Sara AI Terminal Agent..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if pipx is available
if ! command -v pipx &> /dev/null; then
    echo "❌ pipx is required but not found."
    echo "Installing pipx..."
    brew install pipx
fi

echo "✓ Found pipx"
echo ""

# Install Sara in development mode
echo "📦 Installing Sara and dependencies..."
pipx install -e .

echo ""
echo "✅ Sara has been installed successfully!"
echo ""
echo "🎯 Quick Start:"
echo "  1. Make sure LM Studio is running at http://127.0.0.1:1234"
echo "  2. Load the qwen3-coder-30b model (or any other model)"
echo "  3. Run: sara --interactive"
echo ""
echo "📖 Examples:"
echo "  sara \"What does this code do?\""
echo "  sara \"Review this file\" --file script.py"
echo "  sara -i  # Start interactive mode"
echo ""
echo "💡 Need help? Run: sara --help"
echo ""
