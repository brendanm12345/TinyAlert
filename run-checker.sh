#!/bin/bash

echo "[$(date)] Starting run-checker.sh"

# Initial wait for system to fully wake up
sleep 10
echo "[$(date)] Initial wait complete"

# Path to your Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "[$(date)] Changed to directory: $SCRIPT_DIR"

# Use specific Python interpreter
PYTHON_PATH="/Users/brendanmclaughlin/venvs/agents/bin/python3"
echo "[$(date)] Using Python: $PYTHON_PATH"

echo "[$(date)] Running main.py"
$PYTHON_PATH main.py
RESULT=$?
echo "[$(date)] main.py finished with exit code: $RESULT"