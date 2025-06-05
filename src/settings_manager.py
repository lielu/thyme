import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from typing import List, Dict, Any
import json
from config import user_config
import datetime


class SettingsManager:
    """Manages application settings through a GUI interface."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.settings_window = None
        self.settings = self._load_current_settings()
        
    def _load_current_settings(self) -> Dict[str, Any]:
        """Load current settings from alarm_config.txt and environment variables."""
        # Default settings
        settings = {
            # Calendar settings
            'calendar_id': '',
            
            # Weather settings
            'latitude': '32.7767',
            'longitude': '-96.7970',
            'timezone': 'America/Chicago',
            'temp_unit': 'fahrenheit',
            
            # Discord settings
            'discord_token': '',
            'discord_channel_id': '',
            
            # Display settings
            'display_off_time': '',
            'display_on_time': '',
            
            # Alarms
            'alarms': []
        }
        
        # Load from alarm_config.txt first
        try:
            if os.path.exists('alarm_config.txt'):
                with open('alarm_config.txt', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        
                        # Handle key=value settings
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key == 'CALENDAR_ID':
                                settings['calendar_id'] = value
                            elif key == 'LATITUDE':
                                settings['latitude'] = value
                            elif key == 'LONGITUDE':
                                settings['longitude'] = value
                            elif key == 'TIMEZONE':
                                settings['timezone'] = value
                            elif key == 'TEMP_UNIT':
                                settings['temp_unit'] = value
                            elif key == 'DISCORD_TOKEN':
                                settings['discord_token'] = value
                            elif key == 'DISCORD_CHANNEL_ID':
                                settings['discord_channel_id'] = value
                            elif key == 'DISPLAY_OFF':
                                settings['display_off_time'] = value
                            elif key == 'DISPLAY_ON':
                                settings['display_on_time'] = value
                        
                        # Handle alarm times (HH:MM format)
                        elif ':' in line and len(line.split(':')) == 2:
                            try:
                                # Validate it's a time format
                                datetime.datetime.strptime(line, "%H:%M")
                                settings['alarms'].append(line)
                            except ValueError:
                                continue
        except Exception as e:
            print(f"Error loading alarm config: {e}")
        
        # Fall back to environment variables if not found in config file
        if not settings['calendar_id']:
            settings['calendar_id'] = os.getenv('KIOSK_CALENDAR_ID', '')
        if not settings['discord_token']:
            settings['discord_token'] = os.getenv('KIOSK_DISCORD_TOKEN', '')
        if not settings['discord_channel_id']:
            settings['discord_channel_id'] = os.getenv('KIOSK_DISCORD_CHANNEL_ID', '')
        
        # Override with environment variables for weather if they exist
        settings['latitude'] = os.getenv('KIOSK_LATITUDE', settings['latitude'])
        settings['longitude'] = os.getenv('KIOSK_LONGITUDE', settings['longitude'])
        settings['timezone'] = os.getenv('KIOSK_TIMEZONE', settings['timezone'])
        settings['temp_unit'] = os.getenv('KIOSK_TEMP_UNIT', settings['temp_unit'])
            
        return settings
    
    def show_settings(self):
        """Show the settings window."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
            
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title("Kiosk Clock Settings")
        self.settings_window.geometry("600x700")
        self.settings_window.resizable(True, True)
        
        # Make it modal and always on top
        self.settings_window.transient(self.parent)
        
        # Ensure settings window stays on top of the main application
        self.settings_window.attributes('-topmost', True)
        
        # Force focus to the settings window
        self.settings_window.focus_force()
        
        self._create_settings_ui()
        
        # Center the window
        self.settings_window.update_idletasks()
        x = (self.settings_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (700 // 2)
        self.settings_window.geometry(f"600x700+{x}+{y}")
        
        # Final lift and focus to ensure visibility
        self.settings_window.lift()
        self.settings_window.focus_set()
        
        # Immediately try to set focus to first entry widget
        self.settings_window.after_idle(self._set_initial_focus)
        
        # Handle window focus events
        self.settings_window.bind('<FocusIn>', self._on_settings_focus)
        self.settings_window.protocol("WM_DELETE_WINDOW", self._on_settings_close)
        
        # Delay grab_set() to ensure window is fully visible (fixes Raspberry Pi issue)
        self.settings_window.after(100, self._setup_modal_grab)
    
    def _create_settings_ui(self):
        """Create the settings user interface."""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.settings_window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_general_tab(self.notebook)
        self._create_discord_tab(self.notebook)
        self._create_weather_tab(self.notebook)
        self._create_alarms_tab(self.notebook)
        self._create_display_tab(self.notebook)
        
        # Bind tab change event to ensure proper focus
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self.settings_window)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Save & Apply", 
                  command=self._save_settings).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", 
                  command=self._on_settings_close).pack(side="right")
        ttk.Button(buttons_frame, text="Reset to Defaults", 
                  command=self._reset_defaults).pack(side="left")
    
    def _create_general_tab(self, notebook):
        """Create the general settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="General")
        
        # Calendar settings
        ttk.Label(frame, text="Google Calendar Settings", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        ttk.Label(frame, text="Calendar ID (usually your email):").pack(anchor="w")
        self.calendar_id_var = tk.StringVar(value=self.settings['calendar_id'])
        self.calendar_id_entry = ttk.Entry(frame, textvariable=self.calendar_id_var, width=50)
        self.calendar_id_entry.pack(fill="x", pady=(0, 10))
        
        # Info text
        info_text = tk.Text(frame, height=4, wrap=tk.WORD, 
                           font=("Arial", 9), background="#e8e8e8")
        info_text.pack(fill="x", pady=(0, 10))
        info_text.insert("1.0", 
                        "Calendar ID is usually your Gmail address. Make sure you have:\n"
                        "• Google Calendar API enabled in Google Cloud Console\n"
                        "• OAuth 2.0 credentials downloaded as 'credentials.json'\n"
                        "• Authorized the application to access your calendar")
        info_text.config(state="disabled")
    
    def _create_discord_tab(self, notebook):
        """Create the Discord settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Discord")
        
        ttk.Label(frame, text="Discord Integration Settings", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Discord token
        ttk.Label(frame, text="Bot Token:").pack(anchor="w")
        self.discord_token_var = tk.StringVar(value=self.settings['discord_token'])
        self.discord_token_entry = ttk.Entry(frame, textvariable=self.discord_token_var, 
                               width=50, show="*")
        self.discord_token_entry.pack(fill="x", pady=(0, 5))
        
        # Show/hide token button
        def toggle_token_visibility():
            if self.discord_token_entry.cget("show") == "*":
                self.discord_token_entry.config(show="")
                toggle_btn.config(text="Hide Token")
            else:
                self.discord_token_entry.config(show="*")
                toggle_btn.config(text="Show Token")
        
        toggle_btn = ttk.Button(frame, text="Show Token", command=toggle_token_visibility)
        toggle_btn.pack(anchor="w", pady=(0, 10))
        
        # Channel ID
        ttk.Label(frame, text="Channel ID:").pack(anchor="w")
        self.discord_channel_var = tk.StringVar(value=self.settings['discord_channel_id'])
        self.discord_channel_entry = ttk.Entry(frame, textvariable=self.discord_channel_var, width=50)
        self.discord_channel_entry.pack(fill="x", pady=(0, 10))
        
        # Info text
        info_text = tk.Text(frame, height=6, wrap=tk.WORD, 
                           font=("Arial", 9))
        info_text.pack(fill="x", pady=(0, 10))
        info_text.insert("1.0", 
                        "To set up Discord integration:\n"
                        "1. Go to Discord Developer Portal (discord.com/developers/applications)\n"
                        "2. Create a new application and bot\n"
                        "3. Enable 'Message Content Intent' in Bot settings\n"
                        "4. Copy the bot token and paste above\n"
                        "5. Invite bot to your server with 'Read Messages' permission\n"
                        "6. Enable Developer Mode in Discord and copy channel ID")
        info_text.config(state="disabled")
        
        # Test connection button
        ttk.Button(frame, text="Test Discord Connection", 
                  command=self._test_discord_connection).pack(anchor="w")
    
    def _create_weather_tab(self, notebook):
        """Create the weather settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Weather")
        
        ttk.Label(frame, text="Weather Settings", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Location settings
        location_frame = ttk.LabelFrame(frame, text="Location")
        location_frame.pack(fill="x", pady=(0, 10))
        
        # Latitude
        ttk.Label(location_frame, text="Latitude:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.latitude_var = tk.StringVar(value=self.settings['latitude'])
        self.latitude_entry = ttk.Entry(location_frame, textvariable=self.latitude_var, width=15)
        self.latitude_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Longitude
        ttk.Label(location_frame, text="Longitude:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.longitude_var = tk.StringVar(value=self.settings['longitude'])
        self.longitude_entry = ttk.Entry(location_frame, textvariable=self.longitude_var, width=15)
        self.longitude_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Get location button
        ttk.Button(location_frame, text="Get Current Location", 
                  command=self._get_current_location).grid(row=1, column=0, columnspan=4, pady=5)
        
        # Timezone
        ttk.Label(frame, text="Timezone:").pack(anchor="w")
        self.timezone_var = tk.StringVar(value=self.settings['timezone'])
        timezone_combo = ttk.Combobox(frame, textvariable=self.timezone_var, width=30)
        timezone_combo['values'] = [
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'America/Toronto', 'Europe/London', 'Europe/Paris', 'Europe/Berlin',
            'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'
        ]
        timezone_combo.pack(fill="x", pady=(0, 10))
        
        # Temperature unit
        ttk.Label(frame, text="Temperature Unit:").pack(anchor="w")
        self.temp_unit_var = tk.StringVar(value=self.settings['temp_unit'])
        temp_frame = ttk.Frame(frame)
        temp_frame.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(temp_frame, text="Fahrenheit", variable=self.temp_unit_var, 
                       value="fahrenheit").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(temp_frame, text="Celsius", variable=self.temp_unit_var, 
                       value="celsius").pack(side="left")
    
    def _create_alarms_tab(self, notebook):
        """Create the alarms settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Alarms")
        
        ttk.Label(frame, text="Alarm Settings", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Alarms list
        alarms_frame = ttk.LabelFrame(frame, text="Configured Alarms")
        alarms_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(alarms_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.alarms_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.alarms_listbox.yview)
        self.alarms_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.alarms_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate alarms list
        for alarm in self.settings['alarms']:
            self.alarms_listbox.insert(tk.END, alarm)
        
        # Alarm controls
        controls_frame = ttk.Frame(alarms_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Alarm", 
                  command=self._add_alarm).pack(side="left", padx=(0, 5))
        ttk.Button(controls_frame, text="Edit Selected", 
                  command=self._edit_alarm).pack(side="left", padx=(0, 5))
        ttk.Button(controls_frame, text="Delete Selected", 
                  command=self._delete_alarm).pack(side="left")
    
    def _create_display_tab(self, notebook):
        """Create the display settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Display")
        
        ttk.Label(frame, text="Display Power Management", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Display schedule
        schedule_frame = ttk.LabelFrame(frame, text="Automatic Display On/Off")
        schedule_frame.pack(fill="x", pady=(0, 10))
        
        # Display off time
        ttk.Label(schedule_frame, text="Turn display OFF at:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.display_off_var = tk.StringVar(value=self.settings['display_off_time'])
        self.display_off_entry = ttk.Entry(schedule_frame, textvariable=self.display_off_var, width=10)
        self.display_off_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(schedule_frame, text="(24-hour format, e.g., 23:00)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Display on time
        ttk.Label(schedule_frame, text="Turn display ON at:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.display_on_var = tk.StringVar(value=self.settings['display_on_time'])
        self.display_on_entry = ttk.Entry(schedule_frame, textvariable=self.display_on_var, width=10)
        self.display_on_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(schedule_frame, text="(24-hour format, e.g., 07:00)").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Note
        note_text = tk.Text(frame, height=3, wrap=tk.WORD,
                           font=("Arial", 9))
        note_text.pack(fill="x", pady=(0, 10))
        note_text.insert("1.0", 
                        "Note: Display power management is platform-dependent. "
                        "This feature works best on Raspberry Pi with proper display drivers. "
                        "Leave times empty to disable automatic display control.")
        note_text.config(state="disabled")
    
    def _add_alarm(self):
        """Add a new alarm."""
        time_str = simpledialog.askstring("Add Alarm", 
                                         "Enter alarm time (HH:MM, 24-hour format):")
        if time_str:
            try:
                # Validate time format
                datetime.datetime.strptime(time_str, "%H:%M")
                self.alarms_listbox.insert(tk.END, time_str)
            except ValueError:
                messagebox.showerror("Invalid Time", 
                                   "Please enter time in HH:MM format (e.g., 07:30)")
    
    def _edit_alarm(self):
        """Edit the selected alarm."""
        selection = self.alarms_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an alarm to edit.")
            return
        
        current_time = self.alarms_listbox.get(selection[0])
        new_time = simpledialog.askstring("Edit Alarm", 
                                         "Enter new alarm time (HH:MM, 24-hour format):",
                                         initialvalue=current_time)
        if new_time:
            try:
                # Validate time format
                datetime.datetime.strptime(new_time, "%H:%M")
                self.alarms_listbox.delete(selection[0])
                self.alarms_listbox.insert(selection[0], new_time)
            except ValueError:
                messagebox.showerror("Invalid Time", 
                                   "Please enter time in HH:MM format (e.g., 07:30)")
    
    def _delete_alarm(self):
        """Delete the selected alarm."""
        selection = self.alarms_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an alarm to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this alarm?"):
            self.alarms_listbox.delete(selection[0])
    
    def _get_current_location(self):
        """Get current location using IP geolocation."""
        try:
            import requests
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            if data['status'] == 'success':
                self.latitude_var.set(str(data['lat']))
                self.longitude_var.set(str(data['lon']))
                self.timezone_var.set(data['timezone'])
                messagebox.showinfo("Location Updated", 
                                   f"Location set to: {data['city']}, {data['country']}")
            else:
                messagebox.showerror("Error", "Could not determine location")
        except Exception as e:
            messagebox.showerror("Error", f"Could not get location: {str(e)}")
    
    def _test_discord_connection(self):
        """Test Discord bot connection."""
        token = self.discord_token_var.get().strip()
        channel_id = self.discord_channel_var.get().strip()
        
        if not token or not channel_id:
            messagebox.showwarning("Missing Information", 
                                 "Please enter both bot token and channel ID")
            return
        
        # This would need to be implemented with actual Discord API testing
        messagebox.showinfo("Test Connection", 
                           "Discord connection test would be performed here.\n"
                           "Implementation requires async Discord client setup.")
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?"):
            # Reset all variables to defaults
            self.calendar_id_var.set('')
            self.latitude_var.set('32.7767')
            self.longitude_var.set('-96.7970')
            self.timezone_var.set('America/Chicago')
            self.temp_unit_var.set('fahrenheit')
            self.discord_token_var.set('')
            self.discord_channel_var.set('')
            self.display_off_var.set('')
            self.display_on_var.set('')
            
            # Clear alarms list
            self.alarms_listbox.delete(0, tk.END)
    
    def _save_settings(self):
        """Save all settings to alarm_config.txt and update environment variables."""
        try:
            # Validate settings first
            if not self._validate_settings():
                return
            
            # Save all configuration to alarm_config.txt
            self._save_alarm_config()
            
            # Update current environment variables for immediate effect
            os.environ['KIOSK_CALENDAR_ID'] = self.calendar_id_var.get().strip()
            os.environ['KIOSK_LATITUDE'] = self.latitude_var.get().strip()
            os.environ['KIOSK_LONGITUDE'] = self.longitude_var.get().strip()
            os.environ['KIOSK_TIMEZONE'] = self.timezone_var.get().strip()
            os.environ['KIOSK_TEMP_UNIT'] = self.temp_unit_var.get().strip()
            os.environ['KIOSK_DISCORD_TOKEN'] = self.discord_token_var.get().strip()
            os.environ['KIOSK_DISCORD_CHANNEL_ID'] = self.discord_channel_var.get().strip()
            
            messagebox.showinfo("Settings Saved", 
                               "Settings have been saved to alarm_config.txt successfully!\n"
                               "Changes will take effect immediately for most settings.\n"
                               "Some changes may require restarting the application.")
            
            # Reload user_config to pick up changes immediately
            user_config.reload()
            
            self._on_settings_close()
            
        except Exception as e:
            messagebox.showerror("Error Saving Settings", f"Failed to save settings: {str(e)}")
    
    def _validate_settings(self) -> bool:
        """Validate all settings before saving."""
        # Validate latitude/longitude
        try:
            lat = float(self.latitude_var.get())
            lon = float(self.longitude_var.get())
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Location", 
                                "Please enter valid latitude (-90 to 90) and longitude (-180 to 180)")
            return False
        
        # Validate display times if provided
        for time_var, label in [(self.display_off_var, "Display OFF"), 
                               (self.display_on_var, "Display ON")]:
            time_str = time_var.get().strip()
            if time_str:
                try:
                    datetime.datetime.strptime(time_str, "%H:%M")
                except ValueError:
                    messagebox.showerror("Invalid Time", 
                                       f"{label} time must be in HH:MM format")
                    return False
        
        return True
    
    def _save_alarm_config(self):
        """Save all configuration to alarm_config.txt."""
        with open('alarm_config.txt', 'w') as f:
            f.write("# Kiosk Clock Configuration\n")
            f.write("# This file contains all settings for the Kiosk Clock application\n")
            f.write("# Generated by Settings Manager\n\n")
            
            # Calendar settings
            f.write("# Google Calendar Settings\n")
            calendar_id = self.calendar_id_var.get().strip()
            if calendar_id:
                f.write(f"CALENDAR_ID={calendar_id}\n")
            else:
                f.write("# CALENDAR_ID=your-email@gmail.com\n")
            f.write("\n")
            
            # Weather settings
            f.write("# Weather Settings\n")
            f.write(f"LATITUDE={self.latitude_var.get().strip()}\n")
            f.write(f"LONGITUDE={self.longitude_var.get().strip()}\n")
            f.write(f"TIMEZONE={self.timezone_var.get().strip()}\n")
            f.write(f"TEMP_UNIT={self.temp_unit_var.get().strip()}\n")
            f.write("\n")
            
            # Discord settings
            f.write("# Discord Integration Settings\n")
            discord_token = self.discord_token_var.get().strip()
            discord_channel = self.discord_channel_var.get().strip()
            if discord_token:
                f.write(f"DISCORD_TOKEN={discord_token}\n")
            else:
                f.write("# DISCORD_TOKEN=your_bot_token_here\n")
            if discord_channel:
                f.write(f"DISCORD_CHANNEL_ID={discord_channel}\n")
            else:
                f.write("# DISCORD_CHANNEL_ID=your_channel_id_here\n")
            f.write("\n")
            
            # Display power management
            f.write("# Display Power Management\n")
            display_off = self.display_off_var.get().strip()
            display_on = self.display_on_var.get().strip()
            if display_off:
                f.write(f"DISPLAY_OFF={display_off}\n")
            else:
                f.write("# DISPLAY_OFF=23:00\n")
            if display_on:
                f.write(f"DISPLAY_ON={display_on}\n")
            else:
                f.write("# DISPLAY_ON=07:00\n")
            f.write("\n")
            
            # Alarms
            f.write("# Alarm Times (HH:MM format, 24-hour)\n")
            if self.alarms_listbox.size() > 0:
                for i in range(self.alarms_listbox.size()):
                    alarm_time = self.alarms_listbox.get(i)
                    f.write(f"{alarm_time}\n")
            else:
                f.write("# 07:00\n")
                f.write("# 12:00\n")
                f.write("# 18:00\n")
    
    def _on_settings_focus(self, event=None):
        """Handle settings window gaining focus."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.attributes('-topmost', True)
            self.settings_window.lift()
    
    def _on_settings_close(self):
        """Handle settings window close event."""
        if self.settings_window:
            try:
                self.settings_window.grab_release()
            except tk.TclError:
                # Ignore errors if grab was never set
                pass
            self.settings_window.destroy()
            self.settings_window = None
    
    def _setup_modal_grab(self):
        """Setup modal grab after window is fully visible."""
        try:
            if self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.grab_set()
                # Ensure proper focus for input widgets
                self.settings_window.focus_force()
                self.settings_window.lift()
                # Set focus to the first input field to ensure editing works
                if hasattr(self, 'calendar_id_entry'):
                    self.calendar_id_entry.focus_set()
        except tk.TclError as e:
            # Handle cases where grab_set() might still fail (e.g., on some Linux systems)
            print(f"Warning: Could not set modal grab: {e}")
            # Window will still work, just won't be modal
            # But still ensure focus is set
            try:
                if self.settings_window and self.settings_window.winfo_exists():
                    self.settings_window.focus_force()
                    self.settings_window.lift()
                    # Set focus to the first input field to ensure editing works
                    if hasattr(self, 'calendar_id_entry'):
                        self.calendar_id_entry.focus_set()
            except tk.TclError:
                pass 

    def _on_tab_changed(self, event):
        """Handle tab change event."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.attributes('-topmost', True)
            self.settings_window.lift()
            
            # Set focus to appropriate entry widget based on selected tab
            try:
                selected_tab = self.notebook.index("current")
                if selected_tab == 0 and hasattr(self, 'calendar_id_entry'):  # General tab
                    self.calendar_id_entry.focus_set()
                elif selected_tab == 1 and hasattr(self, 'discord_token_entry'):  # Discord tab
                    self.discord_token_entry.focus_set()
                elif selected_tab == 2 and hasattr(self, 'latitude_entry'):  # Weather tab
                    self.latitude_entry.focus_set()
                elif selected_tab == 4 and hasattr(self, 'display_off_entry'):  # Display tab
                    self.display_off_entry.focus_set()
            except (tk.TclError, AttributeError):
                pass 

    def _set_initial_focus(self):
        """Set focus to the first entry widget when the window is created."""
        if hasattr(self, 'calendar_id_entry'):
            self.calendar_id_entry.focus_set()
        elif hasattr(self, 'discord_token_entry'):
            self.discord_token_entry.focus_set()
        elif hasattr(self, 'latitude_entry'):
            self.latitude_entry.focus_set()
        elif hasattr(self, 'display_off_entry'):
            self.display_off_entry.focus_set()