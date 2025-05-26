# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Discord integration module for Kiosk Clock application.

This module handles Discord API integration to display messages
from specified Discord channels on the kiosk display.
"""

import logging
import asyncio
import threading
from typing import List, Dict, Optional
import datetime
import ssl
import certifi
import discord
from discord.ext import commands
import aiohttp

from config import user_config


# Configure SSL for macOS certificate issues
ssl_context = ssl.create_default_context(cafile=certifi.where())


class DiscordManager:
    """Manages Discord integration and message retrieval."""
    
    def __init__(self):
        self.logger = logging.getLogger('kiosk_clock.discord')
        self.bot = None
        self.last_message_time: Optional[datetime.datetime] = None
        self.recent_messages: List[Dict] = []
        self.is_ready = False
        self.loop = None
        self.thread = None
        
        # Discord configuration
        self.token = getattr(user_config, 'discord_token', None)
        self.channel_id = getattr(user_config, 'discord_channel_id', None)
        
        if self.token and self.channel_id:
            self._start_bot()
        else:
            self.logger.warning("Discord token or channel ID not configured")
    
    def _start_bot(self) -> None:
        """Start the Discord bot in a separate thread."""
        def run_bot():
            try:
                # Create new event loop for this thread
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                
                # Set up Discord intents
                intents = discord.Intents.default()
                intents.message_content = True
                
                # Create custom session with SSL context for macOS certificate issues
                async def create_session():
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    return aiohttp.ClientSession(connector=connector)
                
                # Create bot instance with custom session
                self.bot = commands.Bot(
                    command_prefix='!', 
                    intents=intents
                )
                
                # Override the bot's session creation
                async def setup_session():
                    if self.bot.http.connector:
                        await self.bot.http.connector.close()
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    self.bot.http.connector = connector
                    self.bot.http._session = aiohttp.ClientSession(connector=connector)
                
                @self.bot.event
                async def on_ready():
                    self.logger.info(f'Discord bot logged in as {self.bot.user}')
                    self.is_ready = True
                
                @self.bot.event
                async def on_message(message):
                    self.logger.info(f"Received message: {message}")

                    # Don't process bot's own messages
                    if message.author == self.bot.user:
                        return
                    
                    # Only process messages from the configured channel
                    if str(message.channel.id) == str(self.channel_id):
                        await self._process_message(message)
                
                # Start the bot as a task in the event loop
                async def start_bot():
                    try:
                        # Setup custom session with SSL context
                        await setup_session()
                        await self.bot.start(self.token)
                    except Exception as e:
                        self.logger.error(f"Error in bot.start: {e}")

                # Create the task and run the event loop
                self.loop.create_task(start_bot())
                self.loop.run_forever()

            except Exception as e:
                self.logger.error(f"Failed to start Discord bot: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Start bot in separate thread
        self.logger.info(f'In _start_bot with token: {self.token} and channel_id: {self.channel_id}')
        self.thread = threading.Thread(target=run_bot, daemon=True)
        self.thread.start()
        self.logger.info("Discord bot thread started")
    
    async def _process_message(self, message: discord.Message) -> None:
        """Process a new Discord message."""
        try:
            formatted_msg = self._format_message(message)
            if formatted_msg:
                # Add to recent messages (keep only last 10)
                self.recent_messages.insert(0, formatted_msg)
                if len(self.recent_messages) > 10:
                    self.recent_messages = self.recent_messages[:10]
                
                # Update last message time
                self.last_message_time = formatted_msg['timestamp']
                
                self.logger.debug(f"Processed message from {formatted_msg['sender']}")
        
        except Exception as e:
            self.logger.error(f"Error processing Discord message: {e}")
    
    def _format_message(self, message: discord.Message) -> Optional[Dict]:
        """
        Format a Discord message for display.
        
        Args:
            message: Discord message object
            
        Returns:
            Formatted message dict or None
        """
        try:
            # Extract message data
            text = message.content
            sender = message.author.display_name or message.author.name
            timestamp = message.created_at
            time_str = timestamp.strftime('%H:%M')
            
            # Skip empty messages
            if not text.strip():
                return None
            
            # Skip messages starting with bot command prefix
            if text.startswith('!'):
                return None
            
            # Limit message length for display
            if len(text) > 100:
                text = text[:97] + "..."
            
            return {
                'text': text,
                'sender': sender,
                'time': time_str,
                'timestamp': timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting Discord message: {e}")
            return None
    
    def fetch_recent_messages(self, channel_id: str = None, max_messages: int = 5) -> List[Dict]:
        """
        Fetch recent messages from Discord channel.
        
        Args:
            channel_id: Discord channel ID (uses configured channel if None)
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of message dictionaries
        """
        if not self.is_ready or not self.bot:
            return []
        
        # Use recent messages from memory (updated in real-time)
        return self.recent_messages[:max_messages]
    
    async def _fetch_message_history(self, channel_id: str, max_messages: int = 5) -> List[Dict]:
        """
        Fetch message history from Discord API.
        
        Args:
            channel_id: Discord channel ID
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of message dictionaries
        """
        try:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                self.logger.error(f"Discord channel {channel_id} not found")
                return []
            
            messages = []
            async for message in channel.history(limit=max_messages):
                if message.author != self.bot.user:  # Skip bot messages
                    formatted_msg = self._format_message(message)
                    if formatted_msg:
                        messages.append(formatted_msg)
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Discord message history: {e}")
            return []
    
    def get_messages_display_text(self, channel_id: str = None) -> str:
        """
        Get formatted text for displaying recent messages.
        
        Args:
            channel_id: Discord channel ID (uses configured channel if None)
            
        Returns:
            Formatted string for display
        """
        if not self.is_ready:
            return "Discord:\n(connecting...)"
        
        messages = self.fetch_recent_messages(channel_id, max_messages=3)
        
        if not messages:
            return "Discord:\n(no recent messages)"
        
        lines = ["Discord:"]
        for msg in messages:
            sender_short = msg['sender'].split()[0]  # First name only
            line = f"{msg['time']} {sender_short}: {msg['text']}"
            lines.append(line)
        
        # Ensure consistent number of lines
        while len(lines) < 4:  # Title + 3 messages
            lines.append(" ")
        
        return '\n'.join(lines)
    
    def has_new_messages(self, channel_id: str = None) -> bool:
        """
        Check if there are new messages since last check.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            True if new messages exist
        """
        messages = self.fetch_recent_messages(channel_id, max_messages=1)
        
        if not messages:
            return False
        
        latest_message = messages[0]
        latest_time = latest_message.get('timestamp')
        
        if not latest_time:
            return False
        
        if self.last_message_time is None or latest_time > self.last_message_time:
            return True
        
        return False
    
    def is_authenticated(self) -> bool:
        """Check if Discord bot is authenticated and ready."""
        return self.is_ready and self.bot is not None
    
    def cleanup(self) -> None:
        """Clean up Discord connection."""
        try:
            if self.bot and self.loop and self.loop.is_running():
                # Schedule bot close in the event loop
                future = asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
                future.result(timeout=5)  # Wait up to 5 seconds
                
                # Stop the event loop
                if self.loop.is_running():
                    self.loop.call_soon_threadsafe(self.loop.stop)
                
                self.logger.info("Discord bot connection closed")
            
            # Wait for thread to finish
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
                
        except Exception as e:
            self.logger.error(f"Error during Discord cleanup: {e}")
        finally:
            self.bot = None
            self.loop = None
            self.is_ready = False 