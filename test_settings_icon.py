#!/usr/bin/env python3
"""
Test Settings Icon

Simple test script to verify the settings icon functionality
in a windowed mode instead of fullscreen.
"""

import tkinter as tk
import math
from settings_manager import SettingsManager

class TestSettingsIcon:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Settings Icon")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=800,
            height=600,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Initialize settings manager
        self.settings_manager = SettingsManager(self.root)
        
        # Create settings icon
        self.settings_icon_items = None
        self._create_settings_icon()
        
        # Add some test text
        self.canvas.create_text(
            400, 100,
            text="Kiosk Clock Test - Settings Icon",
            font=('Arial', 20, 'bold'),
            fill='white',
            anchor='center'
        )
        
        self.canvas.create_text(
            400, 150,
            text="Click the gear icon in the top-right to open settings",
            font=('Arial', 12),
            fill='white',
            anchor='center'
        )
        
        self.canvas.create_text(
            400, 200,
            text="Or press F6 for keyboard shortcut",
            font=('Arial', 12),
            fill='white',
            anchor='center'
        )
        
        # Bind F6 key
        self.root.bind('<F6>', self._on_open_settings)
        
    def _create_settings_icon(self):
        """Create a clickable settings gear icon."""
        # Position: top-right
        icon_x = 800 - 50  # 50px from right edge
        icon_y = 50  # 50px from top
        icon_size = 24  # Icon diameter
        
        # Create semi-transparent background circle
        bg_circle = self.canvas.create_oval(
            icon_x - icon_size//2 - 4, icon_y - icon_size//2 - 4,
            icon_x + icon_size//2 + 4, icon_y + icon_size//2 + 4,
            fill='#000000', outline='', stipple='gray50'
        )
        
        # Create gear icon using canvas drawing
        gear_parts = []
        
        # Main circle
        main_circle = self.canvas.create_oval(
            icon_x - 8, icon_y - 8,
            icon_x + 8, icon_y + 8,
            outline='white', width=2, fill=''
        )
        gear_parts.append(main_circle)
        
        # Center hole
        center_hole = self.canvas.create_oval(
            icon_x - 3, icon_y - 3,
            icon_x + 3, icon_y + 3,
            outline='white', width=1, fill=''
        )
        gear_parts.append(center_hole)
        
        # Gear teeth (8 small rectangles around the circle)
        for i in range(8):
            angle = i * math.pi / 4  # 8 teeth at 45-degree intervals
            tooth_x = icon_x + 12 * math.cos(angle)
            tooth_y = icon_y + 12 * math.sin(angle)
            
            # Create small rectangle for each tooth
            tooth = self.canvas.create_rectangle(
                tooth_x - 2, tooth_y - 1,
                tooth_x + 2, tooth_y + 1,
                outline='white', width=1, fill='white'
            )
            gear_parts.append(tooth)
        
        # Store all icon parts for click detection
        self.settings_icon_items = [bg_circle] + gear_parts
        
        # Bind click events to all parts of the icon
        for item in self.settings_icon_items:
            self.canvas.tag_bind(item, '<Button-1>', self._on_settings_icon_click)
            self.canvas.tag_bind(item, '<Enter>', self._on_settings_icon_hover)
            self.canvas.tag_bind(item, '<Leave>', self._on_settings_icon_leave)
    
    def _on_settings_icon_click(self, event=None):
        """Handle settings icon click."""
        self._on_open_settings(event)
    
    def _on_settings_icon_hover(self, event=None):
        """Handle mouse hover over settings icon."""
        if self.settings_icon_items:
            # Make the background circle more visible on hover
            self.canvas.itemconfig(self.settings_icon_items[0], stipple='gray25')
    
    def _on_settings_icon_leave(self, event=None):
        """Handle mouse leave settings icon."""
        if self.settings_icon_items:
            # Restore normal background opacity
            self.canvas.itemconfig(self.settings_icon_items[0], stipple='gray50')
    
    def _on_open_settings(self, event=None):
        """Handle settings open request."""
        try:
            self.settings_manager.show_settings()
        except Exception as e:
            print(f"Error opening settings: {e}")
    
    def run(self):
        """Start the test application."""
        self.root.mainloop()

def main():
    app = TestSettingsIcon()
    app.run()

if __name__ == "__main__":
    main() 