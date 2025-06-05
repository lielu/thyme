#!/usr/bin/env python3
"""
Kiosk Clock Launcher

Simple launcher script to run the kiosk clock application from the reorganized src directory.
"""

import sys
import os

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Change to src directory for relative file access
os.chdir(src_dir)

if __name__ == '__main__':
    try:
        from kiosk_clock_app import main
        main()
    except KeyboardInterrupt:
        print("\nKiosk clock stopped by user")
    except Exception as e:
        print(f"Error starting kiosk clock: {e}")
        sys.exit(1) 