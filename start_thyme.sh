#!/bin/bash
# Activate the virtual environment and start Thyme

# Set DISPLAY environment variable
export DISPLAY=:0

# Get the directory of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to virtualenv (adjust if needed)
VENV="$DIR/../myenv"

# Run virtualenv thyme
virtualenv thyme

# Activate virtualenv
source "thyme/bin/activate"

# Install/update dependencies
python -m pip install -r requirements.txt

# Run the Python app
python "$DIR/run_thyme.py" 