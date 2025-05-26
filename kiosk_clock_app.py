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
from typing import Optional
from PIL import ImageTk

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


class KioskClockApp:
    """Main Kiosk Clock application class."""
    
    def __init__(self):
        # Setup logging
        self.logger = setup_logging()
        self.logger.info(f"Starting {APP_NAME}")
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        
        # Configure window
        if HIDE_CURSOR:
            self.root.config(cursor="none")
        
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