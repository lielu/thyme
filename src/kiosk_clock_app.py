# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Main Kiosk Clock Application.

A full-screen digital clock with Google Calendar integration, 
alarms, weather display, and dynamic backgrounds.
"""

import tkinter as tk
import time
import datetime
import atexit
import logging
import math
from typing import Optional
from PIL import ImageTk
import os

# Import our modules
from config import (
    APP_NAME, SCREEN_FULLSCREEN, HIDE_CURSOR, BACKGROUND_COLOR,
    CLOCK_FONT, DATE_FONT, ALARMS_FONT, EVENTS_FONT, WEATHER_FONT,
    UI_MARGIN, EVENTS_REFRESH_INTERVAL, WEATHER_UPDATE_INTERVAL,
    TTS_DELAY_AFTER_ALARM, DISCORD_UPDATE_INTERVAL, user_config
)
from utils import setup_logging, get_screen_dimensions, create_shadow_text
from calendar_integration import CalendarManager
from audio_manager import AudioManager
from alarm_manager import AlarmManager
from weather_manager import WeatherManager
from background_manager import BackgroundManager
from discord_manager import DiscordManager
from settings_manager import SettingsManager


class KioskClockApp:
    """Main Kiosk Clock application class."""
    
    def __init__(self):
        # Setup logging
        self.logger = setup_logging()
        self.logger.info(f"Starting {APP_NAME}")
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        
        # Get screen dimensions
        self.screen_width, self.screen_height = get_screen_dimensions(self.root)
        self.logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        
        # Create main canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_width, 
            height=self.screen_height,
            highlightthickness=0, 
            bd=0, 
            bg=BACKGROUND_COLOR
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Configure root window
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.update_idletasks()
        
        # Make window fullscreen and on top
        self.root.lift()
        self.root.attributes('-topmost', True)
        if SCREEN_FULLSCREEN:
            self.root.attributes('-fullscreen', True)
        self.root.update()
        
        # Initialize managers
        self.calendar_manager = CalendarManager()
        self.audio_manager = AudioManager()
        self.alarm_manager = AlarmManager()
        self.weather_manager = WeatherManager()
        self.background_manager = BackgroundManager(
            self.canvas, self.screen_width, self.screen_height
        )
        self.discord_manager = DiscordManager()
        self.settings_manager = SettingsManager(self.root)
        
        # UI elements (canvas item IDs)
        self.clock_text: Optional[int] = None
        self.clock_shadow: Optional[int] = None
        self.date_text: Optional[int] = None
        self.date_shadow: Optional[int] = None
        self.alarms_text: Optional[int] = None
        self.alarms_shadow: Optional[int] = None
        self.events_text: Optional[int] = None
        self.events_shadow: Optional[int] = None
        self.weather_text: Optional[int] = None
        self.weather_shadow: Optional[int] = None
        self.weather_icon_item: Optional[int] = None
        self.weather_icon_image: Optional[ImageTk.PhotoImage] = None
        self.discord_text: Optional[int] = None
        self.discord_shadow: Optional[int] = None
        
        # Settings icon
        self.settings_icon_items: Optional[list] = None
        
        # Settings overlay
        self.settings_overlay_frame: Optional[tk.Frame] = None
        self.settings_overlay_window: Optional[int] = None
        self.settings_visible = False
        
        # Visual alarm state
        self.alarm_message_item: Optional[int] = None
        self.alarm_reset_timer: Optional[str] = None
        
        # Display state
        self.display_hidden = False
        
        # Initialize UI
        self._create_ui_elements()
        
        # Start background services
        self._start_services()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        
        self.logger.info("Kiosk Clock application initialized")
    
    def _create_ui_elements(self) -> None:
        """Create all UI text elements."""
        # Clock (top-right)
        self.clock_text, self.clock_shadow = create_shadow_text(
            self.canvas,
            self.screen_width - UI_MARGIN,
            UI_MARGIN / 2,
            font=CLOCK_FONT,
            anchor='ne'
        )
        
        # Date (below clock)
        self.date_text, self.date_shadow = create_shadow_text(
            self.canvas,
            self.screen_width - UI_MARGIN,
            UI_MARGIN + 120,  # Clock height + margin
            font=DATE_FONT,
            anchor='ne'
        )
        
        # Alarms (top-left)
        self.alarms_text, self.alarms_shadow = create_shadow_text(
            self.canvas,
            UI_MARGIN,
            UI_MARGIN,
            font=ALARMS_FONT,
            anchor='nw'
        )
        
        # Discord (middle-left)
        self.discord_text, self.discord_shadow = create_shadow_text(
            self.canvas,
            UI_MARGIN,
            self.screen_height // 2 - 50,  # Middle of screen
            font=EVENTS_FONT,  # Same font as events
            anchor='nw'
        )
        
        # Events (bottom-left)
        self.events_text, self.events_shadow = create_shadow_text(
            self.canvas,
            UI_MARGIN,
            self.screen_height - UI_MARGIN,
            font=EVENTS_FONT,
            anchor='sw'
        )
        
        # Weather (bottom-right)
        self.weather_text, self.weather_shadow = create_shadow_text(
            self.canvas,
            self.screen_width - UI_MARGIN - 64,  # Leave space for icon
            self.screen_height - UI_MARGIN,
            font=WEATHER_FONT,
            anchor='se'
        )
        
        # Settings icon (top-right, well below the date text)
        self._create_settings_icon()
    
    def _create_settings_icon(self):
        """Create a clickable settings gear icon."""
        # Position: top-right, well below the date text
        icon_x = self.screen_width - UI_MARGIN - 30  # 30px from right edge
        icon_y = UI_MARGIN + 240  # Much further below date text to avoid overlap
        
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
    
    def _create_settings_overlay(self):
        """Create an embedded settings overlay on the main canvas."""
        if self.settings_visible:
            return
        
        try:
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
            
            # Update display to ensure it's visible
            self.root.update_idletasks()
            
        except Exception as e:
            self.logger.error(f"Error creating settings overlay: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Reset state on error
            self.settings_visible = False
            raise
    
    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill):
        """Draw a rounded rectangle on canvas."""
        # Draw rectangles and circles to create rounded corners
        canvas.create_rectangle(x1+radius, y1, x2-radius, y2, fill=fill, outline='')
        canvas.create_rectangle(x1, y1+radius, x2, y2-radius, fill=fill, outline='')
        
        # Draw rounded corners
        canvas.create_oval(x1, y1, x1+radius*2, y1+radius*2, fill=fill, outline='')
        canvas.create_oval(x2-radius*2, y1, x2, y1+radius*2, fill=fill, outline='')
        canvas.create_oval(x1, y2-radius*2, x1+radius*2, y2, fill=fill, outline='')
        canvas.create_oval(x2-radius*2, y2-radius*2, x2, y2, fill=fill, outline='')
    
    def _create_embedded_settings_ui(self):
        """Create the settings UI inside the embedded frame with rounded corners."""
        try:
            # Create canvas for rounded corners background
            rounded_canvas = tk.Canvas(
                self.settings_overlay_frame,
                bg='#0a0a0a',
                highlightthickness=0,
                bd=0
            )
            rounded_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Draw rounded rectangle background
            def draw_rounded_bg(event=None):
                w = rounded_canvas.winfo_width()
                h = rounded_canvas.winfo_height()
                if w > 1 and h > 1:
                    rounded_canvas.delete("all")
                    radius = 16  # Rounded corner radius
                    
                    # Draw shadow
                    shadow_offset = 12
                    self._draw_rounded_rect(rounded_canvas, shadow_offset, shadow_offset, 
                                          w-shadow_offset, h-shadow_offset, radius, '#000000')
                    
                    # Draw main background
                    self._draw_rounded_rect(rounded_canvas, 0, 0, w, h, radius, '#1e1e1e')
            
            rounded_canvas.bind('<Configure>', draw_rounded_bg)
            self.settings_overlay_frame.update_idletasks()
            draw_rounded_bg()
            
            # Create main frame on top of canvas
            main_frame = tk.Frame(self.settings_overlay_frame, bg='#1e1e1e', bd=0, relief='flat')
            main_frame.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Polished title bar with gradient-like effect
            title_frame = tk.Frame(main_frame, bg='#0078d4', height=64)
            title_frame.pack(fill='x', side='top')
            title_frame.pack_propagate(False)
            
            # Title section with icon and description
            title_left = tk.Frame(title_frame, bg='#0078d4')
            title_left.pack(side='left', fill='both', expand=True, padx=28, pady=16)
            
            title_label = tk.Label(
                title_left, 
                text="⚙️  Settings",
                font=('Segoe UI', 18, 'bold'),
                fg='white', 
                bg='#0078d4',
                anchor='w'
            )
            title_label.pack(anchor='w')
            
            subtitle_label = tk.Label(
                title_left,
                text="Configure your Kiosk Clock",
                font=('Segoe UI', 10),
                fg='#d4e9ff',
                bg='#0078d4',
                anchor='w'
            )
            subtitle_label.pack(anchor='w', pady=(4, 0))
            
            # Polished close button with rounded look
            close_frame = tk.Frame(title_frame, bg='#0078d4')
            close_frame.pack(side='right', padx=20, pady=16)
            
            close_btn = tk.Button(
                close_frame,
                text="✕",
                font=('Segoe UI', 18, 'bold'),
                fg='white',
                bg='#e63946',
                activebackground='#f1495a',
                activeforeground='white',
                bd=0,
                width=2,
                height=1,
                cursor='hand2',
                command=self._hide_settings_overlay,
                relief='flat',
                padx=14,
                pady=8
            )
            close_btn.pack()
            
            # Add hover effects
            def on_close_enter(e):
                close_btn.config(bg='#f1495a')
            def on_close_leave(e):
                close_btn.config(bg='#e63946')
            close_btn.bind('<Enter>', on_close_enter)
            close_btn.bind('<Leave>', on_close_leave)
            
            # Create scrollable content area with refined styling
            content_frame = tk.Frame(main_frame, bg='#252526')
            content_frame.pack(fill='both', expand=True, padx=24, pady=(0, 0))
            
            # Create modern notebook for tabs with refined styling
            from tkinter import ttk
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure polished tab styling
            style.configure('Modern.TNotebook', 
                           background='#252526',
                           borderwidth=0,
                           tabmargins=[2, 4, 2, 0])
            
            # Well-proportioned tabs with rounded appearance
            style.configure('Modern.TNotebook.Tab', 
                           background='#3c3c3c',
                           foreground='#cccccc',
                           padding=[24, 12],
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=0)
            
            style.map('Modern.TNotebook.Tab', 
                     background=[('selected', '#0078d4'), ('active', '#4a4a4a')],
                     foreground=[('selected', 'white'), ('active', '#ffffff')],
                     padding=[('selected', [26, 14])])
            
            # Notebook container with refined spacing
            notebook_container = tk.Frame(content_frame, bg='#252526')
            notebook_container.pack(fill='both', expand=True, pady=(16, 16))
            
            self.settings_notebook = ttk.Notebook(notebook_container, style='Modern.TNotebook')
            self.settings_notebook.pack(fill='both', expand=True, padx=4, pady=0)
            
            # Load current settings
            current_settings = self.settings_manager._load_current_settings()
            
            # Create styled tabs
            self._create_quick_settings_tab(current_settings)
            self._create_alarms_settings_tab(current_settings)
            self._create_advanced_settings_tab(current_settings)
            
            # Polished button frame with better spacing
            button_frame = tk.Frame(main_frame, bg='#1e1e1e', height=80)
            button_frame.pack(fill='x', side='bottom')
            button_frame.pack_propagate(False)
            
            # Separator line
            separator = tk.Frame(button_frame, bg='#3c3c3c', height=1)
            separator.pack(fill='x', side='top')
            
            # Left side buttons
            left_buttons = tk.Frame(button_frame, bg='#1e1e1e')
            left_buttons.pack(side='left', padx=28, pady=20)
            
            # Polished reset button with rounded appearance
            reset_btn = tk.Button(
                left_buttons,
                text="🔄 Reset",
                font=('Segoe UI', 10, 'bold'),
                fg='white',
                bg='#e63946',
                activebackground='#f1495a',
                activeforeground='white',
                bd=0,
                padx=20,
                pady=9,
                cursor='hand2',
                command=self._reset_settings,
                relief='flat'
            )
            reset_btn.pack(side='left')
            
            # Add hover effect
            def on_reset_enter(e):
                reset_btn.config(bg='#f1495a')
            def on_reset_leave(e):
                reset_btn.config(bg='#e63946')
            reset_btn.bind('<Enter>', on_reset_enter)
            reset_btn.bind('<Leave>', on_reset_leave)
            
            # Right side buttons
            right_buttons = tk.Frame(button_frame, bg='#1e1e1e')
            right_buttons.pack(side='right', padx=28, pady=20)
            
            # Polished cancel button
            cancel_btn = tk.Button(
                right_buttons,
                text="Cancel",
                font=('Segoe UI', 10, 'bold'),
                fg='#e0e0e0',
                bg='#3c3c3c',
                activebackground='#4a4a4a',
                activeforeground='white',
                bd=0,
                padx=22,
                pady=9,
                cursor='hand2',
                command=self._hide_settings_overlay,
                relief='flat'
            )
            cancel_btn.pack(side='right', padx=(0, 10))
            
            # Add hover effect
            def on_cancel_enter(e):
                cancel_btn.config(bg='#4a4a4a')
            def on_cancel_leave(e):
                cancel_btn.config(bg='#3c3c3c')
            cancel_btn.bind('<Enter>', on_cancel_enter)
            cancel_btn.bind('<Leave>', on_cancel_leave)
            
            # Polished save button with emphasis
            save_btn = tk.Button(
                right_buttons,
                text="💾 Save & Apply",
                font=('Segoe UI', 11, 'bold'),
                fg='white',
                bg='#0078d4',
                activebackground='#106ebe',
                activeforeground='white',
                bd=0,
                padx=26,
                pady=9,
                cursor='hand2',
                command=self._save_embedded_settings,
                relief='flat'
            )
            save_btn.pack(side='right')
            
            # Add hover effect
            def on_save_enter(e):
                save_btn.config(bg='#106ebe')
            def on_save_leave(e):
                save_btn.config(bg='#0078d4')
            save_btn.bind('<Enter>', on_save_enter)
            save_btn.bind('<Leave>', on_save_leave)
            
        except Exception as e:
            self.logger.error(f"Error creating embedded settings UI: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def _create_quick_settings_tab(self, settings):
        """Create a quick settings tab with the most common options."""
        frame = tk.Frame(self.settings_notebook, bg='#1e1e1e')
        self.settings_notebook.add(frame, text="⚡ Quick Setup")
        
        # Scrollable frame with improved styling
        canvas = tk.Canvas(frame, bg='#1e1e1e', highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview, 
                               bg='#3c3c3c', troughcolor='#1e1e1e', 
                               activebackground='#505050', width=12)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Calendar Section with help text
        self._create_settings_section(scrollable_frame, "📅 Google Calendar", [
            ("Calendar ID:", "calendar_id", settings['calendar_id'], "entry", 
             "Your Gmail address or calendar ID")
        ])
        
        # Discord Section with help text
        self._create_settings_section(scrollable_frame, "💬 Discord Integration", [
            ("Bot Token:", "discord_token", settings['discord_token'], "password",
             "Get from Discord Developer Portal"),
            ("Channel ID:", "discord_channel_id", settings['discord_channel_id'], "entry",
             "Enable Developer Mode in Discord to copy")
        ])
        
        # Location Section with help text
        self._create_settings_section(scrollable_frame, "🌍 Location & Weather", [
            ("Latitude:", "latitude", settings['latitude'], "entry",
             "Decimal format, e.g., 32.7767"),
            ("Longitude:", "longitude", settings['longitude'], "entry",
             "Decimal format, e.g., -96.7970"),
            ("Temperature Unit:", "temp_unit", settings['temp_unit'], "radio", 
             ["fahrenheit", "celsius"], "Preferred temperature display")
        ])
    
    def _create_alarms_settings_tab(self, settings):
        """Create alarms management tab."""
        frame = tk.Frame(self.settings_notebook, bg='#1e1e1e')
        self.settings_notebook.add(frame, text="⏰ Alarms")
        
        # Header section with improved styling
        header_frame = tk.Frame(frame, bg='#1e1e1e')
        header_frame.pack(fill='x', padx=30, pady=25)
        
        title_label = tk.Label(header_frame, text="⏰ Alarm Times", 
                font=('Segoe UI', 16, 'bold'),  # Reduced from 18
                fg='white', bg='#1e1e1e')
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(header_frame, text="Configure when the kiosk should wake you up", 
                font=('Segoe UI', 10),  # Reduced from 11
                fg='#a0a0a0', bg='#1e1e1e')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Alarms listbox with improved styling
        list_frame = tk.Frame(frame, bg='#1e1e1e')
        list_frame.pack(fill='both', expand=True, padx=30, pady=(0, 25))
        
        # Listbox container with improved border and styling
        listbox_container = tk.Frame(list_frame, bg='#3c3c3c', bd=1, relief='solid')
        listbox_container.pack(fill='both', expand=True)
        
        self.alarms_listbox = tk.Listbox(
            listbox_container, 
            height=10, 
            font=('Segoe UI', 11),  # Reduced from 13
            bg='#2d2d30',
            fg='#e0e0e0',
            selectbackground='#0078d4',
            selectforeground='white',
            bd=0,
            highlightthickness=0,
            activestyle='none',
            relief='flat'
        )
        alarms_scrollbar = tk.Scrollbar(listbox_container, orient="vertical", 
                                      command=self.alarms_listbox.yview,
                                      bg='#3c3c3c', troughcolor='#1e1e1e',
                                      activebackground='#505050', width=12)
        self.alarms_listbox.configure(yscrollcommand=alarms_scrollbar.set)
        
        self.alarms_listbox.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        alarms_scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=15)
        
        # Populate alarms
        for alarm in settings['alarms']:
            self.alarms_listbox.insert(tk.END, alarm)
        
        # Modern control buttons with improved styling
        controls_frame = tk.Frame(frame, bg='#1e1e1e')
        controls_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        # Refined action buttons
        add_btn = tk.Button(controls_frame, text="➕ Add Alarm", command=self._add_alarm_embedded,
                           bg='#107c10', fg='white', font=('Segoe UI', 10, 'bold'),  # Reduced from 12
                           bd=0, padx=20, pady=10, cursor='hand2', relief='flat',
                           activebackground='#0e6e0e', activeforeground='white')
        add_btn.pack(side='left', padx=(0, 10))
        
        edit_btn = tk.Button(controls_frame, text="✏️ Edit Selected", command=self._edit_alarm_embedded,
                            bg='#ff9800', fg='white', font=('Segoe UI', 10, 'bold'),  # Reduced from 12
                            bd=0, padx=20, pady=10, cursor='hand2', relief='flat',
                            activebackground='#fb8c00', activeforeground='white')
        edit_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = tk.Button(controls_frame, text="🗑️ Delete Selected", command=self._delete_alarm_embedded,
                              bg='#d32f2f', fg='white', font=('Segoe UI', 10, 'bold'),  # Reduced from 12
                              bd=0, padx=20, pady=10, cursor='hand2', relief='flat',
                              activebackground='#f44336', activeforeground='white')
        delete_btn.pack(side='left')
        
        # Quick add section with refined styling
        quick_frame = tk.Frame(frame, bg='#2d2d30', bd=1, relief='solid')
        quick_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        quick_label = tk.Label(quick_frame, text="Quick Add Common Times:", 
                font=('Segoe UI', 11, 'bold'),  # Reduced from 13
                fg='white', bg='#2d2d30')
        quick_label.pack(anchor='w', padx=18, pady=(16, 10))
        
        buttons_frame = tk.Frame(quick_frame, bg='#2d2d30')
        buttons_frame.pack(fill='x', padx=18, pady=(0, 16))
        
        for time_str in ["06:30", "07:00", "07:30", "08:00"]:
            quick_btn = tk.Button(buttons_frame, text=time_str, 
                                 command=lambda t=time_str: self._quick_add_alarm(t),
                                 bg='#0078d4', fg='white', font=('Segoe UI', 10, 'bold'),  # Reduced from 12
                                 bd=0, padx=18, pady=8, cursor='hand2', relief='flat',
                                 activebackground='#106ebe', activeforeground='white')
            quick_btn.pack(side='left', padx=(0, 10))
    
    def _create_advanced_settings_tab(self, settings):
        """Create advanced settings tab."""
        frame = tk.Frame(self.settings_notebook, bg='#1e1e1e')
        self.settings_notebook.add(frame, text="🔧 Advanced")
        
        # Scrollable frame with improved styling
        canvas = tk.Canvas(frame, bg='#1e1e1e', highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview,
                               bg='#3c3c3c', troughcolor='#1e1e1e',
                               activebackground='#505050', width=12)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display Schedule Section with help text
        self._create_settings_section(scrollable_frame, "📺 Display Schedule", [
            ("Turn display OFF at:", "display_off_time", settings['display_off_time'], "entry",
             "24-hour format (HH:MM), e.g., 23:00"),
            ("Turn display ON at:", "display_on_time", settings['display_on_time'], "entry",
             "24-hour format (HH:MM), e.g., 07:00")
        ])
        
        # Timezone Section with help text
        self._create_settings_section(scrollable_frame, "🌍 Timezone", [
            ("Timezone:", "timezone", settings['timezone'], "combo", 
             ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
              'America/Toronto', 'Europe/London', 'Europe/Paris', 'Europe/Berlin',
              'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'],
             "Select your timezone")
        ])
    
    def _create_settings_section(self, parent, title, fields):
        """Create a settings section with modern styling."""
        # Section container with polished card design
        section_container = tk.Frame(parent, bg='#1e1e1e')
        section_container.pack(fill='x', padx=20, pady=14)
        
        # Section title with polished styling
        title_frame = tk.Frame(section_container, bg='#0078d4', height=42)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text=title, font=('Segoe UI', 12, 'bold'),
                fg='white', bg='#0078d4').pack(anchor='w', padx=18, pady=11)
        
        # Section content with polished card styling
        content_frame = tk.Frame(section_container, bg='#2d2d30', bd=0, relief='flat')
        content_frame.pack(fill='x')
        
        # Store field variables
        if not hasattr(self, 'settings_vars'):
            self.settings_vars = {}
        
        for field_data in fields:
            # Parse field data (supports both old and new format with help text)
            if len(field_data) >= 4:
                field_label = field_data[0]
                field_key = field_data[1]
                field_value = field_data[2]
                field_type = field_data[3]
                field_options = field_data[4] if len(field_data) > 4 else []
                help_text = field_data[5] if len(field_data) > 5 else None
            else:
                # Legacy format support
                field_label, field_key, field_value, field_type = field_data[:4]
                field_options = field_data[4] if len(field_data) > 4 else []
                help_text = None
            
            field_frame = tk.Frame(content_frame, bg='#2d2d30')
            field_frame.pack(fill='x', padx=18, pady=14)
            
            # Left side: Label and help text
            left_frame = tk.Frame(field_frame, bg='#2d2d30')
            left_frame.pack(side='left', fill='y')
            
            # Label with polished styling
            label = tk.Label(left_frame, text=field_label, font=('Segoe UI', 10, 'bold'),
                           fg='#e8e8e8', bg='#2d2d30', anchor='w', width=20)
            label.pack(anchor='w')
            
            # Help text if provided
            if help_text:
                help_label = tk.Label(left_frame, text=help_text, font=('Segoe UI', 9),
                                    fg='#9a9a9a', bg='#2d2d30', anchor='w', width=20)
                help_label.pack(anchor='w', pady=(3, 0))
            
            # Right side: Input widget
            widget_frame = tk.Frame(field_frame, bg='#2d2d30')
            widget_frame.pack(side='left', fill='x', expand=True, padx=(20, 0))
            
            # Create appropriate widget with polished styling
            if field_type == "entry":
                var = tk.StringVar(value=field_value)
                entry = tk.Entry(widget_frame, textvariable=var, font=('Segoe UI', 10),
                               bg='#3c3c3c', fg='#e8e8e8', insertbackground='#0078d4',
                               bd=0, relief='flat', highlightthickness=2,
                               highlightbackground='#555555', highlightcolor='#0078d4')
                entry.pack(side='left', fill='x', expand=True, ipady=8, ipadx=12)
                self.settings_vars[field_key] = var
                
                # Add polished focus effects
                def on_focus_in(event):
                    entry.config(highlightbackground='#0078d4', bg='#454545')
                def on_focus_out(event):
                    entry.config(highlightbackground='#555555', bg='#3c3c3c')
                entry.bind('<FocusIn>', on_focus_in)
                entry.bind('<FocusOut>', on_focus_out)
                
            elif field_type == "password":
                var = tk.StringVar(value=field_value)
                entry = tk.Entry(widget_frame, textvariable=var, show='*', font=('Segoe UI', 10),
                               bg='#3c3c3c', fg='#e8e8e8', insertbackground='#0078d4',
                               bd=0, relief='flat', highlightthickness=2,
                               highlightbackground='#555555', highlightcolor='#0078d4')
                entry.pack(side='left', fill='x', expand=True, ipady=8, ipadx=12)
                self.settings_vars[field_key] = var
                
                # Add polished focus effects
                def on_focus_in(event):
                    entry.config(highlightbackground='#0078d4', bg='#454545')
                def on_focus_out(event):
                    entry.config(highlightbackground='#555555', bg='#3c3c3c')
                entry.bind('<FocusIn>', on_focus_in)
                entry.bind('<FocusOut>', on_focus_out)
                
            elif field_type == "radio" and field_options:
                var = tk.StringVar(value=field_value)
                radio_frame = tk.Frame(widget_frame, bg='#2d2d30')
                radio_frame.pack(side='left', fill='x', expand=True)
                for option in field_options if isinstance(field_options, list) else [field_options]:
                    radio = tk.Radiobutton(radio_frame, text=option.title(), variable=var, value=option,
                                         fg='#e8e8e8', bg='#2d2d30', selectcolor='#0078d4',
                                         font=('Segoe UI', 10), activebackground='#2d2d30',
                                         activeforeground='#e8e8e8', cursor='hand2',
                                         borderwidth=0, highlightthickness=0)
                    radio.pack(side='left', padx=(0, 18), pady=7)
                self.settings_vars[field_key] = var
                
            elif field_type == "combo" and field_options:
                var = tk.StringVar(value=field_value)
                from tkinter import ttk
                
                # Configure combobox style with polished appearance
                style = ttk.Style()
                style.configure('Modern.TCombobox',
                               fieldbackground='#3c3c3c',
                               background='#3c3c3c',
                               foreground='#e8e8e8',
                               borderwidth=0,
                               relief='flat',
                               padding=8)
                style.map('Modern.TCombobox',
                         fieldbackground=[('readonly', '#3c3c3c'), ('focus', '#454545')],
                         background=[('readonly', '#3c3c3c')])
                
                combo = ttk.Combobox(widget_frame, textvariable=var, values=field_options,
                                   font=('Segoe UI', 10), width=40, style='Modern.TCombobox',
                                   state='readonly')
                combo.pack(side='left', ipady=7)
                self.settings_vars[field_key] = var
    
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
        
        # Unbind escape key
        self.root.unbind('<Escape>')
        
        # Re-bind original escape handler if needed
        self.root.bind('<Escape>', self._on_exit)
        
        # Clear settings variables
        if hasattr(self, 'settings_vars'):
            del self.settings_vars
    
    def _save_embedded_settings(self):
        """Save settings from the embedded overlay."""
        try:
            if not hasattr(self, 'settings_vars'):
                return
            
            # Collect all settings
            new_settings = {}
            for key, var in self.settings_vars.items():
                new_settings[key] = var.get().strip()
            
            # Collect alarms
            alarms = []
            if hasattr(self, 'alarms_listbox'):
                for i in range(self.alarms_listbox.size()):
                    alarms.append(self.alarms_listbox.get(i))
            
            # Save to alarm_config.txt using the settings manager's format
            self._save_config_to_file(new_settings, alarms)
            
            # Update environment and reload config
            self._update_environment(new_settings)
            user_config.reload()
            
            # Show success message briefly
            self._show_success_message("Settings saved successfully!")
            
            # Hide overlay after short delay
            self.root.after(1500, self._hide_settings_overlay)
            
        except Exception as e:
            self.logger.error(f"Error saving embedded settings: {e}")
            self._show_error_message(f"Error saving settings: {str(e)}")
    
    def _save_config_to_file(self, settings, alarms):
        """Save configuration to alarm_config.txt."""
        with open('alarm_config.txt', 'w') as f:
            f.write("# Kiosk Clock Configuration\n")
            f.write("# Generated by Embedded Settings\n\n")
            
            # Write settings
            for key, value in settings.items():
                if value:
                    if key == 'calendar_id':
                        f.write(f"CALENDAR_ID={value}\n")
                    elif key == 'latitude':
                        f.write(f"LATITUDE={value}\n")
                    elif key == 'longitude':
                        f.write(f"LONGITUDE={value}\n")
                    elif key == 'timezone':
                        f.write(f"TIMEZONE={value}\n")
                    elif key == 'temp_unit':
                        f.write(f"TEMP_UNIT={value}\n")
                    elif key == 'discord_token':
                        f.write(f"DISCORD_TOKEN={value}\n")
                    elif key == 'discord_channel_id':
                        f.write(f"DISCORD_CHANNEL_ID={value}\n")
                    elif key == 'display_off_time':
                        f.write(f"DISPLAY_OFF={value}\n")
                    elif key == 'display_on_time':
                        f.write(f"DISPLAY_ON={value}\n")
            
            f.write("\n# Alarms\n")
            for alarm in alarms:
                f.write(f"{alarm}\n")
    
    def _update_environment(self, settings):
        """Update environment variables for immediate effect."""
        env_mapping = {
            'calendar_id': 'KIOSK_CALENDAR_ID',
            'latitude': 'KIOSK_LATITUDE', 
            'longitude': 'KIOSK_LONGITUDE',
            'timezone': 'KIOSK_TIMEZONE',
            'temp_unit': 'KIOSK_TEMP_UNIT',
            'discord_token': 'KIOSK_DISCORD_TOKEN',
            'discord_channel_id': 'KIOSK_DISCORD_CHANNEL_ID'
        }
        
        for key, value in settings.items():
            if key in env_mapping:
                os.environ[env_mapping[key]] = value
    
    def _show_success_message(self, message):
        """Show a temporary success message."""
        self._show_temp_message(message, "#006600")
    
    def _show_error_message(self, message):
        """Show a temporary error message."""
        self._show_temp_message(message, "#cc0000")
    
    def _show_temp_message(self, message, color):
        """Show a temporary message overlay."""
        # Create message overlay
        msg_bg = self.canvas.create_rectangle(
            self.screen_width//2 - 200, self.screen_height//2 - 50,
            self.screen_width//2 + 200, self.screen_height//2 + 50,
            fill=color, outline='white', width=2
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
    
    # Alarm management methods for embedded interface
    def _add_alarm_embedded(self):
        """Add alarm in embedded interface."""
        new_time = self._simple_input_dialog("Add Alarm", "Enter time (HH:MM):", "07:00")
        if new_time:
            try:
                import datetime
                datetime.datetime.strptime(new_time, "%H:%M")
                self.alarms_listbox.insert(tk.END, new_time)
            except ValueError:
                self._show_error_message("Invalid time format. Use HH:MM")
    
    def _edit_alarm_embedded(self):
        """Edit selected alarm in embedded interface."""
        selection = self.alarms_listbox.curselection()
        if not selection:
            self._show_error_message("Please select an alarm to edit")
            return
        
        current_time = self.alarms_listbox.get(selection[0])
        # Create simple input dialog
        new_time = self._simple_input_dialog("Edit Alarm", f"Enter new time:", current_time)
        if new_time:
            try:
                import datetime
                datetime.datetime.strptime(new_time, "%H:%M")
                self.alarms_listbox.delete(selection[0])
                self.alarms_listbox.insert(selection[0], new_time)
            except ValueError:
                self._show_error_message("Invalid time format. Use HH:MM")
    
    def _delete_alarm_embedded(self):
        """Delete selected alarm in embedded interface."""
        selection = self.alarms_listbox.curselection()
        if not selection:
            self._show_error_message("Please select an alarm to delete")
            return
        
        self.alarms_listbox.delete(selection[0])
    
    def _quick_add_alarm(self, time_str):
        """Quick add alarm with predefined time."""
        self.alarms_listbox.insert(tk.END, time_str)
    
    def _simple_input_dialog(self, title, prompt, initial_value=""):
        """Simple input dialog for embedded interface."""
        # This is a simplified version - you might want to enhance this
        from tkinter import simpledialog
        return simpledialog.askstring(title, prompt, initialvalue=initial_value)
    
    def _start_services(self) -> None:
        """Start all background services and update timers."""
        # Start background rotation
        self.background_manager.start_background_rotation()
        
        # Try to download Bing wallpaper
        self.background_manager.download_bing_wallpaper()
        
        # Validate weather icons
        self.weather_manager.validate_weather_icons()
        
        # Start update loops
        self._update_clock()
        self._update_alarms()
        self._update_events()
        self._update_weather()
        self._update_discord()
        self._check_display_times()
    
    def _setup_event_handlers(self) -> None:
        """Setup keyboard event handlers."""
        # ESC to exit (for development)
        self.root.bind('<Escape>', self._on_exit)
        
        # F5 to reload configuration
        self.root.bind('<F5>', self._on_reload_config)
        
        # F6 to open settings
        self.root.bind('<F6>', self._on_open_settings)
    
    def _update_clock(self) -> None:
        """Update clock and date display."""
        try:
            current_time = time.strftime('%H:%M:%S')
            current_date = time.strftime('%A, %B %d, %Y')
            
            self.canvas.itemconfig(self.clock_text, text=current_time)
            self.canvas.itemconfig(self.clock_shadow, text=current_time)
            self.canvas.itemconfig(self.date_text, text=current_date)
            self.canvas.itemconfig(self.date_shadow, text=current_date)
            
            # Check for alarms
            if self.alarm_manager.check_alarm_time():
                self._trigger_alarm()
            
        except Exception as e:
            self.logger.error(f"Error updating clock: {e}")
        
        # Schedule next update
        self.root.after(1000, self._update_clock)
    
    def _update_alarms(self) -> None:
        """Update alarms display."""
        try:
            if not self.display_hidden:
                alarm_summary = self.alarm_manager.get_alarm_summary()
                self.canvas.itemconfig(self.alarms_text, text=alarm_summary)
                self.canvas.itemconfig(self.alarms_shadow, text=alarm_summary)
        except Exception as e:
            self.logger.error(f"Error updating alarms: {e}")
        
        # Schedule next update
        self.root.after(60 * 1000, self._update_alarms)
    
    def _update_events(self) -> None:
        """Update calendar events display."""
        try:
            if not self.display_hidden:
                events = self.calendar_manager.fetch_todays_events()
                events_text = '\n'.join(events)
                self.canvas.itemconfig(self.events_text, text=events_text)
                self.canvas.itemconfig(self.events_shadow, text=events_text)
        except Exception as e:
            self.logger.error(f"Error updating events: {e}")
        
        # Schedule next update
        self.root.after(EVENTS_REFRESH_INTERVAL, self._update_events)
    
    def _update_weather(self) -> None:
        """Update weather display."""
        try:
            weather_text, icon_filename = self.weather_manager.fetch_weather_data()
            
            # Update weather text
            icon_x = self.screen_width - UI_MARGIN
            icon_y = self.screen_height - UI_MARGIN
            text_x = icon_x - 48 - 16  # icon width + gap
            text_y = icon_y
            
            self.canvas.coords(self.weather_text, text_x, text_y)
            self.canvas.coords(self.weather_shadow, text_x + 2, text_y + 2)
            self.canvas.itemconfig(self.weather_text, text=weather_text)
            self.canvas.itemconfig(self.weather_shadow, text=weather_text)
            
            # Update weather icon
            weather_icon = self.weather_manager.load_weather_icon(icon_filename)
            if weather_icon:
                self.weather_icon_image = ImageTk.PhotoImage(weather_icon)
                
                if self.weather_icon_item is None:
                    self.weather_icon_item = self.canvas.create_image(
                        icon_x, icon_y,
                        image=self.weather_icon_image,
                        anchor='se'
                    )
                else:
                    self.canvas.coords(self.weather_icon_item, icon_x, icon_y)
                    self.canvas.itemconfig(self.weather_icon_item, image=self.weather_icon_image)
        
        except Exception as e:
            self.logger.error(f"Error updating weather: {e}")
        
        # Schedule next update
        self.root.after(WEATHER_UPDATE_INTERVAL, self._update_weather)
    
    def _update_discord(self) -> None:
        """Update discord display."""
        try:
            if not self.display_hidden and user_config.discord_token and user_config.discord_channel_id:
                discord_text = self.discord_manager.get_messages_display_text(user_config.discord_channel_id)
                self.canvas.itemconfig(self.discord_text, text=discord_text)
                self.canvas.itemconfig(self.discord_shadow, text=discord_text)
            elif not (user_config.discord_token and user_config.discord_channel_id):
                # Show disabled message if discord not configured
                discord_text = "Discord:\n(not configured)"
                self.canvas.itemconfig(self.discord_text, text=discord_text)
                self.canvas.itemconfig(self.discord_shadow, text=discord_text)
        except Exception as e:
            self.logger.error(f"Error updating discord: {e}")
        
        # Schedule next update
        self.root.after(DISCORD_UPDATE_INTERVAL, self._update_discord)
    
    def _check_display_times(self) -> None:
        """Check if display should be hidden based on configured times."""
        try:
            should_hide = self.alarm_manager.should_display_be_hidden()
            
            if should_hide and not self.display_hidden:
                self._hide_display()
            elif not should_hide and self.display_hidden:
                self._show_display()
        
        except Exception as e:
            self.logger.error(f"Error checking display times: {e}")
        
        # Check again in 60 seconds
        self.root.after(60 * 1000, self._check_display_times)
    
    def _hide_display(self) -> None:
        """Hide all display elements and turn off screen."""
        self.display_hidden = True
        
        # Hide text elements
        for item in [self.clock_text, self.clock_shadow, self.date_text, self.date_shadow,
                    self.alarms_text, self.alarms_shadow, self.events_text, self.events_shadow,
                    self.weather_text, self.weather_shadow, self.weather_icon_item,
                    self.discord_text, self.discord_shadow]:
            if item:
                self.canvas.itemconfig(item, state='hidden')
        
        # Hide settings icon
        if self.settings_icon_items:
            for item in self.settings_icon_items:
                self.canvas.itemconfig(item, state='hidden')
        
        # Turn off screen
        self.alarm_manager.turn_screen_off()
        self.logger.info("Display hidden")
    
    def _show_display(self) -> None:
        """Show all display elements and turn on screen."""
        self.display_hidden = False
        
        # Show text elements
        for item in [self.clock_text, self.clock_shadow, self.date_text, self.date_shadow,
                    self.alarms_text, self.alarms_shadow, self.events_text, self.events_shadow,
                    self.weather_text, self.weather_shadow, self.weather_icon_item,
                    self.discord_text, self.discord_shadow]:
            if item:
                self.canvas.itemconfig(item, state='normal')
        
        # Show settings icon
        if self.settings_icon_items:
            for item in self.settings_icon_items:
                self.canvas.itemconfig(item, state='normal')
        
        # Turn on screen
        self.alarm_manager.turn_screen_on()
        self.logger.info("Display shown")
    
    def _trigger_alarm(self) -> None:
        """Trigger alarm with sound and visual notification."""
        try:
            self.logger.info("In _trigger_alarm")

            # Play alarm sound
            self.audio_manager.play_alarm_sound()
            self.logger.info("In _trigger_alarm after play_alarm_sound")
            
            # Show visual alarm
            self._show_alarm_visual()
            self.logger.info("In _trigger_alarm after show_alarm_visual")

            # Schedule TTS announcement
            self.root.after(TTS_DELAY_AFTER_ALARM, self._announce_events)
            self.logger.info("In _trigger_alarm after schedule TTS announcement")

        except Exception as e:
            self.logger.error(f"Error triggering alarm: {e}")
    
    def _show_alarm_visual(self) -> None:
        """Show visual alarm notification."""
        try:
            # Remove any existing alarm message
            if self.alarm_message_item:
                self.canvas.delete(self.alarm_message_item)
            
            # Create alarm message
            alarm_text = "⏰ ALARM ⏰"
            self.alarm_message_item = self.canvas.create_text(
                self.screen_width // 2,
                self.screen_height // 2,
                text=alarm_text,
                font=('Arial', 72, 'bold'),
                fill='red',
                anchor='center'
            )
            
            # Schedule removal
            if self.alarm_reset_timer:
                self.root.after_cancel(self.alarm_reset_timer)
            self.alarm_reset_timer = self.root.after(10000, self._hide_alarm_visual)
            
        except Exception as e:
            self.logger.error(f"Error showing alarm visual: {e}")
    
    def _hide_alarm_visual(self) -> None:
        """Hide visual alarm notification."""
        if self.alarm_message_item:
            self.canvas.delete(self.alarm_message_item)
            self.alarm_message_item = None
        
        if self.alarm_reset_timer:
            self.root.after_cancel(self.alarm_reset_timer)
            self.alarm_reset_timer = None
    
    def _announce_events(self) -> None:
        """Announce upcoming events via TTS."""
        try:
            speech_text = self.calendar_manager.get_upcoming_events_for_speech()
            self.audio_manager.speak_text(speech_text)
        except Exception as e:
            self.logger.error(f"Error announcing events: {e}")
    
    def _on_exit(self, event=None) -> None:
        """Handle exit request."""
        self.logger.info("Exit requested")
        self.cleanup()
        self.root.destroy()
    
    def _on_reload_config(self, event=None) -> None:
        """Handle configuration reload request."""
        try:
            self.alarm_manager.reload_config()
            self.logger.info("Configuration reloaded")
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
    
    def _on_open_settings(self, event=None) -> None:
        """Handle settings open request."""
        try:
            # Show embedded settings overlay instead of separate window
            self._create_settings_overlay()
            
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Try to show error to user
            try:
                from tkinter import messagebox
                messagebox.showerror("Settings Error", f"Failed to open settings: {str(e)}")
            except:
                pass
    
    def _reset_settings(self):
        """Reset all settings to defaults."""
        if not hasattr(self, 'settings_vars'):
            return
            
        # Show confirmation dialog
        from tkinter import messagebox
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?\n\n"
                              "This will clear all current configuration.",
                              parent=self.settings_overlay_frame):
            
            # Reset all field variables to defaults
            if 'calendar_id' in self.settings_vars:
                self.settings_vars['calendar_id'].set('')
            if 'latitude' in self.settings_vars:
                self.settings_vars['latitude'].set('32.7767')
            if 'longitude' in self.settings_vars:
                self.settings_vars['longitude'].set('-96.7970')
            if 'timezone' in self.settings_vars:
                self.settings_vars['timezone'].set('America/Chicago')
            if 'temp_unit' in self.settings_vars:
                self.settings_vars['temp_unit'].set('fahrenheit')
            if 'discord_token' in self.settings_vars:
                self.settings_vars['discord_token'].set('')
            if 'discord_channel_id' in self.settings_vars:
                self.settings_vars['discord_channel_id'].set('')
            if 'display_off_time' in self.settings_vars:
                self.settings_vars['display_off_time'].set('')
            if 'display_on_time' in self.settings_vars:
                self.settings_vars['display_on_time'].set('')
            
            # Clear alarms list
            if hasattr(self, 'alarms_listbox'):
                self.alarms_listbox.delete(0, tk.END)
            
            self._show_success_message("Settings reset to defaults!")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.logger.info("Cleaning up resources")
            
            # Stop background rotation
            self.background_manager.stop_background_rotation()
            
            # Clean up audio
            self.audio_manager.cleanup()
            
            # Clean up Discord connection
            self.discord_manager.cleanup()
            
            # Hide alarm visual
            self._hide_alarm_visual()
            
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.logger.info("Starting main application loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    try:
        app = KioskClockApp()
        app.run()
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        return 1
    return 0


if __name__ == '__main__':
    exit(main()) 