#!/usr/bin/env python3
"""
Test Embedded Settings Interface

Simple test script to verify the embedded settings overlay functionality
works correctly without the full kiosk clock application.
"""

import tkinter as tk
import math
from settings_manager import SettingsManager

class TestEmbeddedSettings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Embedded Settings")
        self.root.geometry("1024x768")
        self.root.configure(bg='black')
        
        # Create canvas like the main app
        self.canvas = tk.Canvas(
            self.root,
            width=1024,
            height=768,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Screen dimensions
        self.screen_width = 1024
        self.screen_height = 768
        
        # Settings overlay variables
        self.settings_overlay_frame = None
        self.settings_overlay_window = None
        self.settings_visible = False
        
        # Initialize settings manager (for loading current settings)
        self.settings_manager = SettingsManager(self.root)
        
        # Create test UI
        self._create_test_ui()
        
        # Create settings icon
        self._create_settings_icon()
        
        # Bind F6 key
        self.root.bind('<F6>', self._on_open_settings)
        
    def _create_test_ui(self):
        """Create test UI elements."""
        # Title
        self.canvas.create_text(
            self.screen_width // 2, 100,
            text="Embedded Settings Test",
            font=('Arial', 24, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Instructions
        self.canvas.create_text(
            self.screen_width // 2, 150,
            text="Click the gear icon or press F6 to test embedded settings",
            font=('Arial', 14),
            fill='white',
            anchor='center'
        )
        
        # Mock clock display
        self.canvas.create_text(
            self.screen_width - 50, 50,
            text="12:34:56",
            font=('Arial', 48, 'bold'),
            fill='white',
            anchor='ne'
        )
        
        # Mock date display
        self.canvas.create_text(
            self.screen_width - 50, 120,
            text="Monday, January 1, 2024",
            font=('Arial', 16),
            fill='white',
            anchor='ne'
        )
        
    def _create_settings_icon(self):
        """Create a clickable settings gear icon."""
        # Position: top-right, well below the date text
        icon_x = self.screen_width - 50 - 30  
        icon_y = 50 + 120 + 80  # More space below the date
        
        # Create a solid, reliable clickable button area
        button_size = 40
        button_bg = self.canvas.create_rectangle(
            icon_x - button_size//2, icon_y - button_size//2,
            icon_x + button_size//2, icon_y + button_size//2,
            fill='#333333', outline='#666666', width=1
        )
        
        # Simple gear text icon (much more reliable than drawing)
        gear_text = self.canvas.create_text(
            icon_x, icon_y,
            text="⚙️",
            font=('Arial', 24),
            fill='white',
            anchor='center'
        )
        
        # Store the clickable elements
        self.settings_icon_items = [button_bg, gear_text]
        
        # Bind click events to both elements
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
            # Highlight the button background on hover
            self.canvas.itemconfig(self.settings_icon_items[0], fill='#555555', outline='#888888')
    
    def _on_settings_icon_leave(self, event=None):
        """Handle mouse leave settings icon."""
        if self.settings_icon_items:
            # Restore normal button appearance
            self.canvas.itemconfig(self.settings_icon_items[0], fill='#333333', outline='#666666')
    
    def _on_open_settings(self, event=None):
        """Handle settings open request."""
        try:
            self._create_settings_overlay()
        except Exception as e:
            print(f"Error opening embedded settings: {e}")
            
    def _create_settings_overlay(self):
        """Create an embedded settings overlay on the main canvas."""
        if self.settings_visible:
            return
        
        # Calculate overlay dimensions and position
        overlay_width = min(900, self.screen_width - 80)
        overlay_height = min(700, self.screen_height - 80)
        overlay_x = (self.screen_width - overlay_width) // 2
        overlay_y = (self.screen_height - overlay_height) // 2
        
        # Create semi-transparent background with better opacity
        bg_overlay = self.canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill='black', stipple='gray12', outline=''
        )
        
        # Create main settings frame with modern styling
        self.settings_overlay_frame = tk.Frame(
            self.canvas,
            bg='#1a1a1a',
            relief='flat',
            bd=0
        )
        
        # Embed frame in canvas
        self.settings_overlay_window = self.canvas.create_window(
            overlay_x + overlay_width//2,
            overlay_y + overlay_height//2,
            window=self.settings_overlay_frame,
            width=overlay_width,
            height=overlay_height
        )
        
        # Create settings UI inside the frame
        self._create_embedded_settings_ui()
        
        # Bind escape key to close
        self.root.bind('<Escape>', self._hide_settings_overlay)
        
        # Store overlay elements for cleanup
        self.settings_bg_overlay = bg_overlay
        self.settings_visible = True
        
        # Focus on the overlay
        self.settings_overlay_frame.focus_set()
    
    def _create_embedded_settings_ui(self):
        """Create the settings UI inside the embedded frame."""
        # Create modern shadow effect frame
        shadow_frame = tk.Frame(self.settings_overlay_frame, bg='#000000', bd=0)
        shadow_frame.place(x=8, y=8, relwidth=1, relheight=1)
        
        main_frame = tk.Frame(self.settings_overlay_frame, bg='#2d2d2d', bd=2, relief='solid')
        main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Modern title bar with gradient effect
        title_frame = tk.Frame(main_frame, bg='#0066cc', height=50)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)
        
        # Title with icon
        title_label = tk.Label(
            title_frame, 
            text="⚙️  Kiosk Clock Settings (Test Mode)",
            font=('Segoe UI', 18, 'bold'),
            fg='white', 
            bg='#0066cc'
        )
        title_label.pack(side='left', padx=20, pady=12)
        
        # Modern close button
        close_btn = tk.Button(
            title_frame,
            text="✕",
            font=('Segoe UI', 20, 'bold'),
            fg='white',
            bg='#ff4444',
            activebackground='#ff6666',
            activeforeground='white',
            bd=0,
            width=6,
            height=2,
            cursor='hand2',
            command=self._hide_settings_overlay
        )
        close_btn.pack(side='right', padx=20, pady=10)
        
        # Create scrollable content area with better styling
        content_frame = tk.Frame(main_frame, bg='#2d2d2d')
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Test content with modern card design
        test_card = tk.Frame(content_frame, bg='#3d3d3d', bd=1, relief='solid')
        test_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        test_label = tk.Label(
            test_card,
            text="🎉 Embedded Settings Interface Working!\n\n"
                 "This demonstrates the modern embedded settings overlay.\n\n"
                 "Features demonstrated:\n"
                 "• Modern dark theme with blue accents\n"
                 "• Large, touch-friendly buttons\n"
                 "• Better spacing for easier clicking\n"
                 "• Semi-transparent background overlay\n"
                 "• Shadow effects and modern styling\n"
                 "• Responsive layout\n\n"
                 "In the full application, this would contain:\n"
                 "• Quick Setup tab (Calendar, Discord, Weather)\n"
                 "• Alarms Management tab\n"
                 "• Advanced Settings tab\n\n"
                 "Click the X button or press Escape to close.",
            font=('Segoe UI', 12),
            fg='white',
            bg='#3d3d3d',
            justify='center'
        )
        test_label.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Modern button frame with larger buttons
        button_frame = tk.Frame(main_frame, bg='#333333', height=80)
        button_frame.pack(fill='x', side='bottom')
        button_frame.pack_propagate(False)
        
        # Modern action buttons - much larger and easier to click
        test_btn = tk.Button(
            button_frame,
            text="✨ Test Success",
            font=('Segoe UI', 14, 'bold'),
            fg='white',
            bg='#28a745',
            activebackground='#34ce57',
            activeforeground='white',
            bd=0,
            padx=40,
            pady=20,
            cursor='hand2',
            command=lambda: self._show_test_message("Modern settings interface test successful!")
        )
        test_btn.pack(side='right', padx=20, pady=20)
        
        # Close button with larger size
        close_btn2 = tk.Button(
            button_frame,
            text="Close",
            font=('Segoe UI', 14),
            fg='white',
            bg='#6c757d',
            activebackground='#868e96',
            activeforeground='white',
            bd=0,
            padx=40,
            pady=20,
            cursor='hand2',
            command=self._hide_settings_overlay
        )
        close_btn2.pack(side='right', padx=10, pady=20)
    
    def _hide_settings_overlay(self, event=None):
        """Hide the settings overlay."""
        if not self.settings_visible:
            return
        
        # Remove overlay elements
        if hasattr(self, 'settings_bg_overlay'):
            self.canvas.delete(self.settings_bg_overlay)
        
        if self.settings_overlay_window:
            self.canvas.delete(self.settings_overlay_window)
            self.settings_overlay_window = None
        
        if self.settings_overlay_frame:
            self.settings_overlay_frame.destroy()
            self.settings_overlay_frame = None
        
        # Reset state
        self.settings_visible = False
        
        # Restore original escape binding
        self.root.bind('<Escape>', lambda e: self.root.destroy())
    
    def _show_test_message(self, message):
        """Show a test success message."""
        # Create message overlay
        msg_bg = self.canvas.create_rectangle(
            self.screen_width//2 - 200, self.screen_height//2 - 50,
            self.screen_width//2 + 200, self.screen_height//2 + 50,
            fill='#006600', outline='white', width=2
        )
        
        msg_text = self.canvas.create_text(
            self.screen_width//2, self.screen_height//2,
            text=message, font=('Arial', 14, 'bold'),
            fill='white', anchor='center'
        )
        
        # Remove message after 3 seconds
        def remove_message():
            self.canvas.delete(msg_bg)
            self.canvas.delete(msg_text)
        
        self.root.after(3000, remove_message)
    
    def run(self):
        """Start the test application."""
        print("Starting Embedded Settings Test...")
        print("- Click the gear icon in the top-right to test embedded settings")
        print("- Press F6 for keyboard shortcut")
        print("- Press Escape to close settings or quit")
        
        # Bind escape to quit when not in settings
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        self.root.mainloop()

def main():
    """Main function."""
    app = TestEmbeddedSettings()
    app.run()

if __name__ == "__main__":
    main() 