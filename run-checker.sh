#!/bin/bash

# Wait for network connectivity
wait_for_network() {
    while ! ping -c 1 google.com &> /dev/null; do
        echo "Waiting for network connection..."
        sleep 5
    done
}

# Path to your Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure we have network before running
wait_for_network

# Run the campsite checker
python3 main.py

