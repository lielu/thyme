# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Weather management module for Kiosk Clock application.

This module handles weather data fetching from Open-Meteo API,
weather icon management, and temperature display formatting.
"""

import os
import logging
from typing import Tuple, Optional
import requests

from config import (
    WEATHER_CODE_MAP, WEATHER_ICONS_DIR, WEATHER_ICON_SIZE,
    user_config
)
from utils import load_and_resize_image


class WeatherManager:
    """Manages weather data fetching and display."""
    
    def __init__(self):
        self.logger = logging.getLogger('kiosk_clock.weather')
        self.last_weather_data: Optional[Tuple[str, str]] = None
    
    def fetch_weather_data(self) -> Tuple[str, str]:
        """
        Fetch current weather data from Open-Meteo API.
        
        Returns:
            Tuple of (temperature_text, icon_filename)
        """
        try:
            # Build API URL with user configuration
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={user_config.latitude}&longitude={user_config.longitude}"
                f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
                f"&current_weather=true"
                f"&temperature_unit={user_config.temperature_unit}"
                f"&timezone={user_config.timezone.replace('/', '%2F')}"
            )
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract temperature data
            max_temp = data['daily']['temperature_2m_max'][0]
            min_temp = data['daily']['temperature_2m_min'][0]
            weather_code = data['daily']['weathercode'][0]
            
            # Format temperature text
            temp_text = f"{int(round(max_temp))}° / {int(round(min_temp))}°"
            
            # Get weather icon
            icon_filename = WEATHER_CODE_MAP.get(weather_code, 'clear.png')
            
            self.last_weather_data = (temp_text, icon_filename)
            self.logger.debug(f"Weather updated: {temp_text}, icon: {icon_filename}")
            
            return temp_text, icon_filename
            
        except requests.RequestException as e:
            self.logger.error(f"Network error fetching weather: {e}")
            return self._get_fallback_weather()
            
        except (KeyError, ValueError, TypeError) as e:
            self.logger.error(f"Error parsing weather data: {e}")
            return self._get_fallback_weather()
            
        except Exception as e:
            self.logger.error(f"Unexpected error fetching weather: {e}")
            return self._get_fallback_weather()
    
    def _get_fallback_weather(self) -> Tuple[str, str]:
        """
        Get fallback weather data when API fails.
        
        Returns:
            Tuple of (fallback_text, default_icon)
        """
        if self.last_weather_data:
            self.logger.info("Using cached weather data")
            return self.last_weather_data
        
        return "--° / --°", 'clear.png'
    
    def get_weather_icon_path(self, icon_filename: str) -> str:
        """
        Get full path to weather icon file.
        
        Args:
            icon_filename: Icon filename (e.g., 'clear.png')
            
        Returns:
            Full path to icon file
        """
        return os.path.join(WEATHER_ICONS_DIR, icon_filename)
    
    def load_weather_icon(self, icon_filename: str):
        """
        Load and resize weather icon for display.
        
        Args:
            icon_filename: Icon filename to load
            
        Returns:
            PIL Image object or None if failed
        """
        icon_path = self.get_weather_icon_path(icon_filename)
        
        if not os.path.exists(icon_path):
            self.logger.warning(f"Weather icon not found: {icon_path}")
            # Try to use default clear icon
            default_path = self.get_weather_icon_path('clear.png')
            if os.path.exists(default_path):
                icon_path = default_path
            else:
                self.logger.error("No weather icons found")
                return None
        
        return load_and_resize_image(icon_path, WEATHER_ICON_SIZE)
    
    def get_weather_description(self, weather_code: int) -> str:
        """
        Get human-readable weather description from weather code.
        
        Args:
            weather_code: Weather code from Open-Meteo API
            
        Returns:
            Human-readable weather description
        """
        # Weather code to description mapping
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        return descriptions.get(weather_code, "Unknown weather")
    
    def validate_weather_icons(self) -> bool:
        """
        Validate that all required weather icons exist.
        
        Returns:
            True if all icons are present, False otherwise
        """
        if not os.path.exists(WEATHER_ICONS_DIR):
            self.logger.error(f"Weather icons directory not found: {WEATHER_ICONS_DIR}")
            return False
        
        missing_icons = []
        for icon_filename in set(WEATHER_CODE_MAP.values()):
            icon_path = self.get_weather_icon_path(icon_filename)
            if not os.path.exists(icon_path):
                missing_icons.append(icon_filename)
        
        if missing_icons:
            self.logger.warning(f"Missing weather icons: {missing_icons}")
            return False
        
        self.logger.info("All weather icons validated successfully")
        return True
    
    def get_location_info(self) -> str:
        """
        Get formatted location information.
        
        Returns:
            Location string for display
        """
        # This could be enhanced to do reverse geocoding
        return f"Lat: {user_config.latitude:.2f}, Lon: {user_config.longitude:.2f}" 