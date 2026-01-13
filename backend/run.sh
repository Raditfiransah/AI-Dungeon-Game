#!/bin/bash

# Script untuk menjalankan backend server
# Pastikan sudah activate conda environment: conda activate nlp_general

echo "Starting AI Driven Dungeon Backend..."
echo "Make sure you have activated virtual environment"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found in $SCRIPT_DIR!"
    echo "Please ensure .env exists."
    exit 1
fi

# Run uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
