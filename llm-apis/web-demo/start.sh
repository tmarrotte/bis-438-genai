#!/bin/bash
# Setup and test script for the Web Demo

echo "========================================="
echo "Web Demo Setup & Test"
echo "========================================="
echo

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "Error: Please run this script from the web-demo directory"
    exit 1
fi

# Check for .env file in parent directory
if [ ! -f "../.env" ]; then
    echo "Error: .env file not found in parent directory"
    echo "Please create it with your BEDROCK_API_KEY"
    exit 1
fi

# Check for prompt file
if [ ! -f "../prompt_ANSWER_KEY.txt" ]; then
    echo "Warning: prompt_ANSWER_KEY.txt not found in parent directory"
    echo "The server will use this file for analysis"
fi

echo "✓ All required files found"
echo
echo "========================================="
echo "Testing Backend Server"
echo "========================================="
echo

# Test Python and required packages
python3 -c "import requests; from dotenv import load_dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Required Python packages not installed"
    echo "Run: pip install requests python-dotenv"
    exit 1
fi

echo "✓ Python packages OK"
echo
echo "========================================="
echo "Starting Server"
echo "========================================="
echo
echo "Server will start on http://localhost:5000"
echo
echo "In another terminal, run:"
echo "  cd web-demo"
echo "  python -m http.server 8000"
echo
echo "Then open: http://localhost:8000"
echo
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo

# Start the server
python3 server.py
