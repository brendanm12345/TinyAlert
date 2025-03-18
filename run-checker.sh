#!/bin/bash

echo "[$(date)] Starting run-checker.sh"

# Source environment variables
ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.env"
if [ -f "$ENV_FILE" ]; then
    echo "[$(date)] Loading environment variables from $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "[$(date)] ⚠️  Environment file not found: $ENV_FILE"
    exit 1
fi

# Initial wait for system to fully wake up
sleep 10
echo "[$(date)] Initial wait complete"

# Path to your Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "[$(date)] Changed to directory: $SCRIPT_DIR"

# Use specific Python interpreter from environment
if [ -z "$PYTHON_PATH" ]; then
    echo "[$(date)] ⚠️  PYTHON_PATH not set in environment"
    exit 1
fi
echo "[$(date)] Using Python: $PYTHON_PATH"

# Ensure playwright is installed
if ! $PYTHON_PATH -c "import playwright" &>/dev/null; then
    echo "[$(date)] Installing playwright..."
    $PYTHON_PATH -m pip install playwright
    $PYTHON_PATH -m playwright install
fi

echo "[$(date)] Running main.py"
$PYTHON_PATH main.py
RESULT=$?
echo "[$(date)] main.py finished with exit code: $RESULT"