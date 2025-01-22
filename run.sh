#!/bin/bash

# Path to project directory
PROJECT_DIR="/home/terrastride/terrastride"

# Change into directory
cd "$PROJECT_DIR" || { echo "Failed to cd into $PROJECT_DIR"; exit 1; }

# Source the environment setup script
echo "Setting up environment..."
source ./setup_env.sh || { echo "Failed to source ./setup_env.sh"; exit 1; }

# Start robot
echo "Running detection..."
python3 basic_pipelines/detection.py || { echo "Failed to run detection.py"; exit 1; }

echo "Detection process complete!"
