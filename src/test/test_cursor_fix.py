#!/usr/bin/env python3
"""
Test Cursor Behavior in Settings Interface

Simple test to verify that the cursor properly disappears in kiosk mode
and reappears when the settings interface is opened.
"""

import tkinter as tk
import time

class CursorTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cursor Behavior Test")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Start with hidden cursor (like kiosk mode)
        self.root.config(cursor="none")
        self.original_cursor = "none"
        
        self.canvas = tk.Canvas(
            self.root,
            width=800,
            height=600,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        self.settings_visible = False
        
        # Create test UI
        self._create_test_ui()
        
        # Bind keys
        self.root.bind('<F6>', self._toggle_settings)
        self.root.bind('<Escape>', self._on_escape)
        
    def _create_test_ui(self):
        """Create test UI elements."""
        # Title
        self.canvas.create_text(
            400, 100,
            text="Cursor Behavior Test",
            font=('Arial', 24, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Instructions
        instructions = [
            "🖱️ Cursor should be HIDDEN in kiosk mode",
            "Press F6 to open settings",
            "🖱️ Cursor should APPEAR in settings",
            "Press Escape to close settings",
            "🖱️ Cursor should be HIDDEN again",
            "",
            "Current state: Kiosk Mode (cursor hidden)"
        ]
        
        y_start = 200
        for i, text in enumerate(instructions):
            color = 'yellow' if 'Current state' in text else 'white'
            self.canvas.create_text(
                400, y_start + i * 30,
                text=text,
                font=('Arial', 14),
                fill=color,
                anchor='center'
            )
        
        # Status indicator
        self.status_text = self.canvas.create_text(
            400, 500,
            text="Status: Kiosk Mode - Cursor Hidden",
            font=('Arial', 16, 'bold'),
            fill='green',
            anchor='center'
        )
    
    def _toggle_settings(self, event=None):
        """Toggle settings interface."""
        if not self.settings_visible:
            self._show_settings()
        else:
            self._hide_settings()
    
    def _show_settings(self):
        """Show settings and restore cursor."""
        # Store original cursor and show normal cursor
        self.original_cursor = self.root.cget('cursor')
        self.root.config(cursor="")
        
        # Create simple settings overlay
        overlay = self.canvas.create_rectangle(
            100, 150, 700, 450,
            fill='#2d2d2d', outline='white', width=2
        )
        
        title = self.canvas.create_text(
            400, 200,
            text="⚙️ Settings Interface",
            font=('Arial', 18, 'bold'),
            fill='white',
            anchor='center'
        )
        
        message = self.canvas.create_text(
            400, 250,
            text="Settings interface is open!\n\n"
                 "✅ Cursor should now be VISIBLE\n"
                 "Move your mouse to verify\n\n"
                 "Press Escape to close",
            font=('Arial', 12),
            fill='white',
            anchor='center'
        )
        
        close_btn = self.canvas.create_rectangle(
            350, 350, 450, 390,
            fill='#cc0000', outline='white'
        )
        
        close_text = self.canvas.create_text(
            400, 370,
            text="Close",
            font=('Arial', 12, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Store overlay items
        self.overlay_items = [overlay, title, message, close_btn, close_text]
        
        # Bind click to close button
        self.canvas.tag_bind(close_btn, '<Button-1>', lambda e: self._hide_settings())
        self.canvas.tag_bind(close_text, '<Button-1>', lambda e: self._hide_settings())
        
        self.settings_visible = True
        
        # Update status
        self.canvas.itemconfig(self.status_text, 
                              text="Status: Settings Mode - Cursor Visible",
                              fill='orange')
    
    def _hide_settings(self, event=None):
        """Hide settings and restore kiosk cursor."""
        if not self.settings_visible:
            return
        
        # Remove overlay items
        for item in self.overlay_items:
            self.canvas.delete(item)
        
        # Restore original cursor (hidden)
        self.root.config(cursor=self.original_cursor)
        
        self.settings_visible = False
        
        # Update status
        self.canvas.itemconfig(self.status_text, 
                              text="Status: Kiosk Mode - Cursor Hidden",
                              fill='green')
    
    def _on_escape(self, event=None):
        """Handle escape key."""
        if self.settings_visible:
            self._hide_settings()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the test."""
        print("Starting Cursor Behavior Test...")
        print("- F6: Toggle settings interface")
        print("- Escape: Close settings or exit")
        print("- Watch cursor visibility change!")
        
        self.root.mainloop()

def main():
    """Main function."""
    app = CursorTest()
    app.run()

if __name__ == "__main__":
    main() 