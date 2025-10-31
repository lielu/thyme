#!/usr/bin/env python3
"""
Quick test script for the improved settings UI.
Opens the settings overlay directly to test the new design.
"""

import sys
import os

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Change to src directory for relative file access
os.chdir(src_dir)

import tkinter as tk
from kiosk_clock_app import KioskClockApp

def main():
    """Test the settings UI."""
    print("=" * 60)
    print("Testing Improved Settings UI")
    print("=" * 60)
    print("\nInstructions:")
    print("1. The settings overlay should open automatically")
    print("2. Click the gear icon (⚙️) in the top-right to open settings")
    print("3. Press F6 to open settings via keyboard")
    print("4. Press Escape to close settings or quit")
    print("\nTesting:")
    print("- Check the new modern dark theme")
    print("- Verify improved spacing and typography")
    print("- Test input field focus highlights")
    print("- Check help text appears below labels")
    print("- Verify button styling and hover effects")
    print("=" * 60)
    
    try:
        app = KioskClockApp()
        
        # Auto-open settings after a short delay for testing
        def auto_open_settings():
            app._on_open_settings()
        
        app.root.after(500, auto_open_settings)
        app.run()
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())

