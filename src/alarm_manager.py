# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Alarm management module for Kiosk Clock application.

This module handles alarm scheduling, display control, and
screen power management across different platforms.
"""

import os
import datetime
import logging
from typing import List, Set, Optional, Tuple
import subprocess

from config import ALARM_CONFIG_FILE
from utils import parse_time_string, time_to_minutes


class AlarmManager:
    """Manages alarm scheduling and display control."""
    
    def __init__(self):
        self.logger = logging.getLogger('kiosk_clock.alarm')
        self.fired_alarms_today: Set[str] = set()
        self.display_off_time: Optional[str] = None
        self.display_on_time: Optional[str] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load alarm and display configuration from file."""
        self.display_off_time = None
        self.display_on_time = None
        
        if not os.path.exists(ALARM_CONFIG_FILE):
            self.logger.warning(f"Alarm config file {ALARM_CONFIG_FILE} not found")
            return
        
        try:
            with open(ALARM_CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('DISPLAY_OFF='):
                        self.display_off_time = line.split('=', 1)[1].strip()
                        self.logger.info(f"Display off time set to: {self.display_off_time}")
                    elif line.startswith('DISPLAY_ON='):
                        self.display_on_time = line.split('=', 1)[1].strip()
                        self.logger.info(f"Display on time set to: {self.display_on_time}")
        except Exception as e:
            self.logger.error(f"Failed to load alarm config: {e}")
    
    def get_alarm_times(self) -> List[str]:
        """
        Get list of configured alarm times.
        
        Returns:
            List of alarm times in HH:MM format
        """
        if not os.path.exists(ALARM_CONFIG_FILE):
            return []
        
        alarm_times = []
        try:
            with open(ALARM_CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and configuration lines
                    if line and not line.startswith('#') and not line.startswith('DISPLAY_'):
                        # Validate time format
                        if parse_time_string(line):
                            alarm_times.append(line)
        except Exception as e:
            self.logger.error(f"Failed to read alarm times: {e}")
        
        return alarm_times
    
    def check_alarm_time(self) -> bool:
        """
        Check if current time matches any alarm time.
        
        Returns:
            True if alarm should fire now, False otherwise
        """
        now = datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hm = now.strftime('%H:%M')
        
        alarm_times = self.get_alarm_times()
        alarm_id = f'{today}-{current_hm}'
        
        # Check if it's time for an alarm and not already fired today
        if current_hm in alarm_times and alarm_id not in self.fired_alarms_today:
            self.fired_alarms_today.add(alarm_id)
            self.logger.info(f"Alarm fired at {current_hm}")
            return True
        
        # Reset fired alarms at midnight
        if current_hm == '00:00':
            self.fired_alarms_today.clear()
            self.logger.info("Reset fired alarms for new day")
        
        return False
    
    def should_display_be_hidden(self) -> bool:
        """
        Check if display should be hidden based on configured times.
        
        Returns:
            True if display should be hidden, False otherwise
        """
        if not self.display_off_time or not self.display_on_time:
            return False
        
        now = datetime.datetime.now()
        current_minutes = now.hour * 60 + now.minute
        
        off_minutes = time_to_minutes(self.display_off_time)
        on_minutes = time_to_minutes(self.display_on_time)
        
        if off_minutes is None or on_minutes is None:
            return False
        
        # Handle overnight periods (e.g., 23:00 to 07:00)
        if off_minutes > on_minutes:
            # Display is off from off_time to midnight and from midnight to on_time
            return current_minutes >= off_minutes or current_minutes < on_minutes
        else:
            # Display is off from off_time to on_time (same day)
            return off_minutes <= current_minutes < on_minutes
    
    def turn_screen_off(self) -> bool:
        """
        Turn screen off using platform-specific methods.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try Raspberry Pi specific method first
            try:
                subprocess.run(['vcgencmd', 'display_power', '0'], 
                             check=True, capture_output=True)
                self.logger.info("Screen turned off (Raspberry Pi)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            # Try generic Linux method
            try:
                subprocess.run(['xset', 'dpms', 'force', 'off'], 
                             check=True, capture_output=True)
                self.logger.info("Screen turned off (xset)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            self.logger.warning("Could not turn screen off - no supported method found")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to turn screen off: {e}")
            return False
    
    def turn_screen_on(self) -> bool:
        """
        Turn screen on using platform-specific methods.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try Raspberry Pi specific method first
            try:
                subprocess.run(['vcgencmd', 'display_power', '1'], 
                             check=True, capture_output=True)
                self.logger.info("Screen turned on (Raspberry Pi)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            # Try generic Linux method
            try:
                subprocess.run(['xset', 'dpms', 'force', 'on'], 
                             check=True, capture_output=True)
                self.logger.info("Screen turned on (xset)")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            self.logger.warning("Could not turn screen on - no supported method found")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to turn screen on: {e}")
            return False
    
    def get_alarm_summary(self, max_alarms: int = 3) -> str:
        """
        Get formatted summary of configured alarms.
        
        Args:
            max_alarms: Maximum number of alarms to include
            
        Returns:
            Formatted alarm summary string
        """
        alarm_times = self.get_alarm_times()
        
        if not alarm_times:
            return 'Alarms:\n(no alarms)\n \n '
        
        # Show up to max_alarms
        display_alarms = alarm_times[:max_alarms]
        summary = 'Alarms:\n' + '\n'.join(display_alarms)
        
        # Ensure we always have the same number of lines for consistent layout
        lines_count = summary.count('\n')
        while lines_count < max_alarms:
            summary += '\n '
            lines_count += 1
        
        return summary
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        self.logger.info("Alarm configuration reloaded") 