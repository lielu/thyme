#!/usr/bin/env python3
"""
Test Settings on Raspberry Pi

Simple test script to verify the settings window works correctly
on Raspberry Pi and other Linux systems where grab_set() might fail.
"""

import tkinter as tk
from settings_manager import SettingsManager

def test_settings_window():
    """Test the settings window without the full kiosk clock app."""
    root = tk.Tk()
    root.title("Settings Test for Raspberry Pi")
    root.geometry("400x300")
    root.configure(bg='black')
    
    # Create a simple interface
    label = tk.Label(
        root,
        text="Settings Window Test\n\nClick 'Open Settings' to test the settings window.\nThis should work without the 'grab failed' error.",
        font=('Arial', 12),
        fg='white',
        bg='black',
        justify='center'
    )
    label.pack(expand=True)
    
    # Initialize settings manager
    settings_manager = SettingsManager(root)
    
    # Create button to open settings
    button = tk.Button(
        root,
        text="Open Settings",
        font=('Arial', 14, 'bold'),
        command=settings_manager.show_settings,
        bg='blue',
        fg='white',
        padx=20,
        pady=10
    )
    button.pack(pady=20)
    
    # Add instruction label
    instruction = tk.Label(
        root,
        text="Press F6 or click the button to open settings",
        font=('Arial', 10),
        fg='gray',
        bg='black'
    )
    instruction.pack()
    
    # Bind F6 key
    root.bind('<F6>', lambda e: settings_manager.show_settings())
    
    # Bind ESC to close
    root.bind('<Escape>', lambda e: root.destroy())
    
    print("Starting Raspberry Pi settings test...")
    print("- Click 'Open Settings' button or press F6")
    print("- Settings window should open without 'grab failed' error")
    print("- Press ESC to exit")
    
    root.mainloop()

if __name__ == "__main__":
    test_settings_window() 