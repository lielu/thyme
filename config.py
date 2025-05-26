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

# User Customizable Settings (can be overridden)
class UserConfig:
    """User customizable configuration settings."""
    
    def __init__(self):
        self.calendar_id = os.getenv('KIOSK_CALENDAR_ID', DEFAULT_CALENDAR_ID)
        self.latitude = float(os.getenv('KIOSK_LATITUDE', DEFAULT_LATITUDE))
        self.longitude = float(os.getenv('KIOSK_LONGITUDE', DEFAULT_LONGITUDE))
        self.timezone = os.getenv('KIOSK_TIMEZONE', 'America/Chicago')
        self.temperature_unit = os.getenv('KIOSK_TEMP_UNIT', 'fahrenheit')
        self.discord_token = os.getenv('KIOSK_DISCORD_TOKEN', KIOSK_DISCORD_TOKEN)  # Discord bot token
        self.discord_channel_id = os.getenv('KIOSK_DISCORD_CHANNEL_ID', KIOSK_DISCORD_CHANNEL_ID)  # Discord channel ID
        
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

# Global configuration instance
user_config = UserConfig() 