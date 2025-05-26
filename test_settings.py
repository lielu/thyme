#!/usr/bin/env python3
"""
Test script for the Settings Manager module.

This script creates a simple window to test the settings manager
functionality without running the full kiosk clock application.
"""

import tkinter as tk
from settings_manager import SettingsManager


def main():
    """Test the settings manager."""
    root = tk.Tk()
    root.title("Settings Manager Test")
    root.geometry("400x200")
    
    # Create settings manager
    settings_manager = SettingsManager(root)
    
    # Create test button
    button_frame = tk.Frame(root)
    button_frame.pack(expand=True)
    
    tk.Label(button_frame, text="Settings Manager Test", 
             font=("Arial", 16, "bold")).pack(pady=20)
    
    tk.Button(button_frame, text="Open Settings", 
              command=settings_manager.show_settings,
              font=("Arial", 12),
              width=15, height=2).pack(pady=10)
    
    tk.Label(button_frame, text="Press F6 to open settings", 
             font=("Arial", 10)).pack(pady=5)
    
    # Bind F6 key
    root.bind('<F6>', lambda e: settings_manager.show_settings())
    
    # Info text
    info = tk.Text(root, height=4, wrap=tk.WORD)
    info.pack(fill="x", padx=10, pady=10)
    info.insert("1.0", 
                "This is a test window for the Settings Manager.\n"
                "Click 'Open Settings' or press F6 to test the settings interface.\n"
                "The settings will be saved to alarm_config.txt and .env files.")
    info.config(state="disabled")
    
    root.mainloop()


if __name__ == '__main__':
    main() 