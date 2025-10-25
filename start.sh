#!/bin/bash
# Startup script for Telethon Userbot (Linux/Mac)

echo "===================================="
echo "  Telethon Userbot Launcher"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please create a .env file with your credentials."
    echo "You can copy env.template to .env and fill in your values."
    echo ""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3 from your package manager."
    echo ""
    exit 1
fi

echo "[INFO] Checking dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to install some dependencies."
    echo "Trying to continue anyway..."
    echo ""
fi

echo ""
echo "[INFO] Starting userbot..."
echo "[INFO] Press Ctrl+C to stop"
echo ""

python3 userbot.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Userbot stopped with an error."
    exit 1
fi

