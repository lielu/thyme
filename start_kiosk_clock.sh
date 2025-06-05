#!/bin/bash
# Activate the virtual environment and start the kiosk clock app

# Set DISPLAY environment variable
export DISPLAY=:0

# Get the directory of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to virtualenv (adjust if needed)
VENV="$DIR/../myenv"

# Run virtualenv kiosk_clock
virtualenv kiosk_clock

# Activate virtualenv
source "kiosk_clock/bin/activate"

# Install/update dependencies
python -m pip install -r requirements.txt

# Run the Python app
python "$DIR/run_kiosk.py" 