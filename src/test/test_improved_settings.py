#!/usr/bin/env python3
"""
Test Improved Settings Interface

Demonstrates the enhanced settings UI with modern design improvements.
Run this to see the new settings page in action without running the full app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from settings_manager import SettingsManager

class TestImprovedSettings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Improved Settings UI Test")
        self.root.geometry("1280x800")
        self.root.configure(bg='#0a0a0a')
        
        # Create canvas like the main app
        self.canvas = tk.Canvas(
            self.root,
            width=1280,
            height=800,
            bg='#0a0a0a',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Screen dimensions
        self.screen_width = 1280
        self.screen_height = 800
        
        # Settings overlay variables
        self.settings_overlay_frame = None
        self.settings_overlay_window = None
        self.settings_visible = False
        
        # Initialize settings manager (for loading current settings)
        self.settings_manager = SettingsManager(self.root)
        
        # Import the embedded settings UI methods from main app
        from kiosk_clock_app import KioskClockApp
        
        # Bind the methods we need
        self._create_settings_overlay = self._create_overlay_wrapper
        self._hide_settings_overlay = self._hide_overlay_wrapper
        self._create_embedded_settings_ui = KioskClockApp._create_embedded_settings_ui.__get__(self)
        self._create_quick_settings_tab = KioskClockApp._create_quick_settings_tab.__get__(self)
        self._create_alarms_settings_tab = KioskClockApp._create_alarms_settings_tab.__get__(self)
        self._create_advanced_settings_tab = KioskClockApp._create_advanced_settings_tab.__get__(self)
        self._create_settings_section = KioskClockApp._create_settings_section.__get__(self)
        self._save_embedded_settings = KioskClockApp._save_embedded_settings.__get__(self)
        self._save_config_to_file = KioskClockApp._save_config_to_file.__get__(self)
        self._update_environment = KioskClockApp._update_environment.__get__(self)
        self._show_success_message = KioskClockApp._show_success_message.__get__(self)
        self._show_error_message = KioskClockApp._show_error_message.__get__(self)
        self._show_temp_message = KioskClockApp._show_temp_message.__get__(self)
        self._add_alarm_embedded = KioskClockApp._add_alarm_embedded.__get__(self)
        self._edit_alarm_embedded = KioskClockApp._edit_alarm_embedded.__get__(self)
        self._delete_alarm_embedded = KioskClockApp._delete_alarm_embedded.__get__(self)
        self._quick_add_alarm = KioskClockApp._quick_add_alarm.__get__(self)
        self._simple_input_dialog = KioskClockApp._simple_input_dialog.__get__(self)
        self._reset_settings = KioskClockApp._reset_settings.__get__(self)
        
        # Create test UI
        self._create_test_ui()
        
        # Bind keyboard shortcuts
        self.root.bind('<F6>', lambda e: self._create_settings_overlay())
        self.root.bind('<Escape>', lambda e: self.root.destroy() if not self.settings_visible else None)
        
    def _create_test_ui(self):
        """Create test UI elements."""
        # Background gradient effect
        for i in range(0, self.screen_height, 50):
            alpha = i / self.screen_height
            gray = int(10 + alpha * 20)
            color = f'#{gray:02x}{gray:02x}{gray:02x}'
            self.canvas.create_rectangle(0, i, self.screen_width, i+50, 
                                        fill=color, outline='')
        
        # Title
        self.canvas.create_text(
            self.screen_width // 2, 100,
            text="✨ Improved Settings UI Demo ✨",
            font=('Segoe UI', 32, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Subtitle
        self.canvas.create_text(
            self.screen_width // 2, 160,
            text="Modern, Beautiful, and User-Friendly",
            font=('Segoe UI', 16),
            fill='#b8b8b8',
            anchor='center'
        )
        
        # Instructions box
        instructions_box = self.canvas.create_rectangle(
            self.screen_width // 2 - 300, 220,
            self.screen_width // 2 + 300, 380,
            fill='#2d7dd2',
            outline='#3d8de2',
            width=2
        )
        
        instructions = [
            "🖱️  Click the button below to open settings",
            "⌨️  Or press F6 for keyboard shortcut",
            "✏️  Try adding, editing, and deleting alarms",
            "🎨  Notice the modern design and smooth interactions",
            "💾  Test saving settings (writes to alarm_config.txt)"
        ]
        
        y_pos = 250
        for instruction in instructions:
            self.canvas.create_text(
                self.screen_width // 2, y_pos,
                text=instruction,
                font=('Segoe UI', 13),
                fill='white',
                anchor='center'
            )
            y_pos += 30
        
        # Large open settings button
        button_bg = self.canvas.create_rectangle(
            self.screen_width // 2 - 150, 420,
            self.screen_width // 2 + 150, 490,
            fill='#27ae60',
            outline='#2ecc71',
            width=2
        )
        
        button_text = self.canvas.create_text(
            self.screen_width // 2, 455,
            text="⚙️  Open Settings",
            font=('Segoe UI', 18, 'bold'),
            fill='white',
            anchor='center'
        )
        
        # Bind click to button
        self.canvas.tag_bind(button_bg, '<Button-1>', lambda e: self._create_settings_overlay())
        self.canvas.tag_bind(button_text, '<Button-1>', lambda e: self._create_settings_overlay())
        
        # Hover effects
        def on_hover(e):
            self.canvas.itemconfig(button_bg, fill='#2ecc71')
            self.root.config(cursor='hand2')
        
        def on_leave(e):
            self.canvas.itemconfig(button_bg, fill='#27ae60')
            self.root.config(cursor='')
        
        self.canvas.tag_bind(button_bg, '<Enter>', on_hover)
        self.canvas.tag_bind(button_bg, '<Leave>', on_leave)
        self.canvas.tag_bind(button_text, '<Enter>', on_hover)
        self.canvas.tag_bind(button_text, '<Leave>', on_leave)
        
        # Features list
        features_title = self.canvas.create_text(
            self.screen_width // 2, 540,
            text="✨ Key Features ✨",
            font=('Segoe UI', 20, 'bold'),
            fill='white',
            anchor='center'
        )
        
        features = [
            "Modern Dark Theme  •  Large Touch-Friendly Buttons  •  Hover Effects",
            "Tabbed Interface  •  Visual Icons  •  Color-Coded Actions",
            "Input Validation  •  Success Messages  •  Helpful Tips",
            "Keyboard Navigation  •  Focus Indicators  •  Smooth Interactions"
        ]
        
        y_pos = 580
        for feature in features:
            self.canvas.create_text(
                self.screen_width // 2, y_pos,
                text=feature,
                font=('Segoe UI', 12),
                fill='#cccccc',
                anchor='center'
            )
            y_pos += 30
        
        # Footer
        self.canvas.create_text(
            self.screen_width // 2, self.screen_height - 30,
            text="Press ESC to exit  •  Designed with ❤️ for the best user experience",
            font=('Segoe UI', 10),
            fill='#666666',
            anchor='center'
        )
    
    def _create_overlay_wrapper(self):
        """Wrapper for creating settings overlay."""
        if self.settings_visible:
            return
        
        # Calculate overlay dimensions and position
        overlay_width = min(950, self.screen_width - 80)
        overlay_height = min(750, self.screen_height - 50)
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
    
    def _hide_overlay_wrapper(self, event=None):
        """Wrapper for hiding settings overlay."""
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
        
        # Clear settings variables
        if hasattr(self, 'settings_vars'):
            del self.settings_vars
        
        # Restore original escape binding
        self.root.bind('<Escape>', lambda e: self.root.destroy())
    
    def run(self):
        """Start the test application."""
        print("=" * 70)
        print("IMPROVED SETTINGS UI TEST")
        print("=" * 70)
        print()
        print("Testing the enhanced settings interface with:")
        print("  ✓ Modern dark theme with blue accents")
        print("  ✓ Large, touch-friendly buttons")
        print("  ✓ Hover effects and visual feedback")
        print("  ✓ Tabbed interface with icons")
        print("  ✓ Improved spacing and layout")
        print("  ✓ Color-coded actions (green=save, orange=edit, red=delete)")
        print("  ✓ Help text and tips")
        print()
        print("Controls:")
        print("  - Click 'Open Settings' button or press F6")
        print("  - Navigate between tabs to explore")
        print("  - Try adding/editing/deleting alarms")
        print("  - Press ESC to close settings or exit")
        print()
        print("=" * 70)
        
        self.root.mainloop()

def main():
    """Main function."""
    app = TestImprovedSettings()
    app.run()

if __name__ == "__main__":
    main()

