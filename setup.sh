#!/bin/bash
# Weather App Setup Script for macOS/Linux

echo ""
echo "================================================"
echo "Weather Dashboard - Setup Script"
echo "================================================"
echo ""

# Check if Python is available
echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERROR: Python 3 not found!"
    echo ""
    echo "Please install Python 3:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3"
    echo ""
    exit 1
fi

echo "Python found!"
python3 --version
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a minute..."
echo ""
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies!"
    echo "Please check your internet connection and try again."
    echo ""
    exit 1
fi

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""

# Ask user if they want to run the app now
read -p "Run app now? (y/n): " -n 1 -r run
echo
if [[ $run =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting Weather App..."
    echo ""
    echo "Navigate to: http://127.0.0.1:5000 in your browser"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 app.py
else
    echo ""
    echo "To run the app later, use:"
    echo "  python3 app.py"
    echo ""
    echo "Then open: http://127.0.0.1:5000"
    echo ""
fi
