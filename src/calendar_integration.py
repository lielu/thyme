# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Google Calendar integration module for Kiosk Clock application.

This module handles authentication, event fetching, and calendar
operations using the Google Calendar API.
"""

import os
import pickle
import datetime
from typing import List, Optional
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import CALENDAR_SCOPES, CREDENTIALS_FILE, TOKEN_FILE, user_config
from utils import safe_file_operation


class CalendarManager:
    """Manages Google Calendar authentication and event retrieval."""
    
    def __init__(self):
        self.logger = logging.getLogger('kiosk_clock.calendar')
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Calendar API."""
        creds = None
        
        # Load existing credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Refreshed Google Calendar credentials")
                except Exception as e:
                    self.logger.error(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    self.logger.error(f"Credentials file {CREDENTIALS_FILE} not found")
                    return
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, CALENDAR_SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    self.logger.info("Obtained new Google Calendar credentials")
                except Exception as e:
                    self.logger.error(f"Failed to obtain credentials: {e}")
                    return
            
            # Save credentials
            try:
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                self.logger.info("Saved Google Calendar credentials")
            except Exception as e:
                self.logger.error(f"Failed to save credentials: {e}")
        
        # Build the service
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            self.logger.info("Google Calendar service initialized")
        except Exception as e:
            self.logger.error(f"Failed to build calendar service: {e}")
    
    def fetch_todays_events(self, max_events: int = 3) -> List[str]:
        """
        Fetch today's calendar events.
        
        Args:
            max_events: Maximum number of events to return
            
        Returns:
            List of formatted event strings
        """
        if not self.service:
            return ["Error: Calendar service not available"]
        
        try:
            # Get current time boundaries
            now = datetime.datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + datetime.timedelta(days=1)
            
            # Convert to RFC3339 format
            time_min = today_start.isoformat() + 'Z'
            time_max = today_end.isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=user_config.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_events,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return ["No upcoming events today"]
            
            formatted_events = []
            for event in events:
                formatted_event = self._format_event(event)
                if formatted_event:
                    formatted_events.append(formatted_event)
            
            return formatted_events if formatted_events else ["No upcoming events today"]
            
        except Exception as e:
            self.logger.error(f"Failed to fetch calendar events: {e}")
            return [f"Error: {str(e)}"]
    
    def _format_event(self, event: dict) -> Optional[str]:
        """
        Format a single calendar event for display.
        
        Args:
            event: Event dictionary from Google Calendar API
            
        Returns:
            Formatted event string or None if event should be skipped
        """
        try:
            title = event.get('summary', 'Untitled Event')
            
            # Handle different event time formats
            start = event['start']
            if 'dateTime' in start:
                # Timed event
                start_time = datetime.datetime.fromisoformat(
                    start['dateTime'].replace('Z', '+00:00')
                )
                time_str = start_time.strftime('%-I:%M %p')
            else:
                # All-day event
                time_str = "All day"
            
            # Add location if available
            location = event.get('location', '')
            if location:
                # Simplify location (remove detailed address, keep main part)
                location_parts = location.split(',')
                simplified_location = location_parts[0].strip()
                if len(simplified_location) > 30:
                    simplified_location = simplified_location[:30] + "..."
                return f"{time_str} - {title} @ {simplified_location}"
            else:
                return f"{time_str} - {title}"
                
        except Exception as e:
            self.logger.error(f"Failed to format event: {e}")
            return None
    
    def get_upcoming_events_for_speech(self) -> str:
        """
        Get upcoming events formatted for text-to-speech.
        
        Returns:
            String suitable for TTS announcement
        """
        events = self.fetch_todays_events(max_events=3)
        
        if not events or events[0].startswith('No upcoming') or events[0].startswith('Error:'):
            return "There are no upcoming events today."
        
        speech_text = "Here are your upcoming events: "
        for event in events:
            if event.strip():  # Only include non-empty events
                # Remove location for speech (too verbose)
                event_parts = event.split(' @ ')
                speech_text += event_parts[0] + ". "
        
        return speech_text
    
    def is_authenticated(self) -> bool:
        """Check if the calendar service is authenticated and ready."""
        return self.service is not None 