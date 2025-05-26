# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Configuration module for Kiosk Clock application.

This module contains all configuration settings, constants,
and user preferences for the application.
"""

import os
from typing import Dict, Any

# Application Information
APP_NAME = "Kiosk Clock"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "A full-screen digital clock with calendar integration, alarms, and weather display"

# File Paths
ALARM_CONFIG_FILE = 'alarm_config.txt'
ALARM_WAV_FILE = 'alarm.wav'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
TTS_OUTPUT_FILE = 'tts_output.mp3'
BACKGROUNDS_DIR = 'backgrounds'
WEATHER_ICONS_DIR = 'weather_icons'

# Google Calendar Configuration
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DEFAULT_CALENDAR_ID = 'primary'  # Use 'primary' for main calendar
EVENTS_REFRESH_INTERVAL = 10 * 1000  # 10 seconds in milliseconds

# Discord Configuration
DISCORD_UPDATE_INTERVAL = 10 * 1000  # 10 seconds in milliseconds
KIOSK_DISCORD_TOKEN = '<discord_token>'
KIOSK_DISCORD_CHANNEL_ID = '<discord_channel_id>'

# UI Configuration
SCREEN_FULLSCREEN = True
HIDE_CURSOR = True
BACKGROUND_COLOR = 'black'

# Font Settings
CLOCK_FONT = ('Arial', 120, 'bold')
DATE_FONT = ('Arial', 36)
ALARMS_FONT = ('Arial', 24)
EVENTS_FONT = ('Arial', 32)
WEATHER_FONT = ('Arial', 28)

# Positioning (pixels from edges)
UI_MARGIN = 40

# Background Image Settings
BACKGROUND_CHANGE_INTERVAL = 30 * 1000  # 30 seconds in milliseconds
FADE_STEPS = 20
FADE_DURATION = 1000  # milliseconds for fade in/out

# Weather Configuration
WEATHER_UPDATE_INTERVAL = 60 * 60 * 1000  # 1 hour in milliseconds
DEFAULT_LATITUDE = 32.7767  # Dallas, TX
DEFAULT_LONGITUDE = -96.7970  # Dallas, TX
WEATHER_ICON_SIZE = (48, 48)

# Weather Code Mapping (Open-Meteo API)
WEATHER_CODE_MAP = {
    0: 'clear.png', 1: 'clear.png', 2: 'partly_cloudy.png', 3: 'cloudy.png',
    45: 'fog.png', 48: 'fog.png',
    51: 'rain.png', 53: 'rain.png', 55: 'rain.png',
    56: 'rain.png', 57: 'rain.png',
    61: 'rain.png', 63: 'rain.png', 65: 'rain.png',
    66: 'rain.png', 67: 'rain.png',
    71: 'snow.png', 73: 'snow.png', 75: 'snow.png',
    77: 'snow.png',
    80: 'rain.png', 81: 'rain.png', 82: 'rain.png',
    85: 'snow.png', 86: 'snow.png',
    95: 'thunderstorm.png', 96: 'thunderstorm.png', 99: 'thunderstorm.png'
}

# Audio Configuration
AUDIO_PLAYER_LINUX = 'aplay'  # For alarm sound
TTS_PLAYER_LINUX = 'mpg123'  # For text-to-speech
TTS_LANGUAGE = 'en'
TTS_DELAY_AFTER_ALARM = 2000  # milliseconds

# Browser Configuration (for Google OAuth)
os.environ['BROWSER'] = '/usr/bin/chromium'

def _load_config_from_file() -> Dict[str, str]:
    """Load configuration from alarm_config.txt file."""
    config = {}
    
    try:
        if os.path.exists(ALARM_CONFIG_FILE):
            with open(ALARM_CONFIG_FILE, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('#') or not line or '=' not in line:
                        continue
                    
                    # Handle key=value settings
                    key, value = line.split('=', 1)
                    if key == 'CALENDAR_ID':
                        config['calendar_id'] = value
                    elif key == 'LATITUDE':
                        config['latitude'] = value
                    elif key == 'LONGITUDE':
                        config['longitude'] = value
                    elif key == 'TIMEZONE':
                        config['timezone'] = value
                    elif key == 'TEMP_UNIT':
                        config['temp_unit'] = value
                    elif key == 'DISCORD_TOKEN':
                        config['discord_token'] = value
                    elif key == 'DISCORD_CHANNEL_ID':
                        config['discord_channel_id'] = value
    except Exception as e:
        print(f"Warning: Error loading config from {ALARM_CONFIG_FILE}: {e}")
    
    return config

# User Customizable Settings (can be overridden)
class UserConfig:
    """User customizable configuration settings."""
    
    def __init__(self):
        # Load from alarm_config.txt first
        file_config = _load_config_from_file()
        
        # Use config file values if available, otherwise fall back to environment variables, then defaults
        self.calendar_id = file_config.get('calendar_id') or os.getenv('KIOSK_CALENDAR_ID', DEFAULT_CALENDAR_ID)
        
        latitude_str = file_config.get('latitude') or os.getenv('KIOSK_LATITUDE', str(DEFAULT_LATITUDE))
        longitude_str = file_config.get('longitude') or os.getenv('KIOSK_LONGITUDE', str(DEFAULT_LONGITUDE))
        
        try:
            self.latitude = float(latitude_str)
            self.longitude = float(longitude_str)
        except (ValueError, TypeError):
            self.latitude = DEFAULT_LATITUDE
            self.longitude = DEFAULT_LONGITUDE
            
        self.timezone = file_config.get('timezone') or os.getenv('KIOSK_TIMEZONE', 'America/Chicago')
        self.temperature_unit = file_config.get('temp_unit') or os.getenv('KIOSK_TEMP_UNIT', 'fahrenheit')
        
        # Discord settings from config file first, then environment variables
        self.discord_token = file_config.get('discord_token') or os.getenv('KIOSK_DISCORD_TOKEN', KIOSK_DISCORD_TOKEN)
        self.discord_channel_id = file_config.get('discord_channel_id') or os.getenv('KIOSK_DISCORD_CHANNEL_ID', KIOSK_DISCORD_CHANNEL_ID)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'calendar_id': self.calendar_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone,
            'temperature_unit': self.temperature_unit,
            'discord_token': self.discord_token,
            'discord_channel_id': self.discord_channel_id
        }
    
    def reload(self):
        """Reload configuration from alarm_config.txt and environment variables."""
        self.__init__()

# Global configuration instance
user_config = UserConfig() 