# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Audio management module for Kiosk Clock application.

This module handles text-to-speech generation, audio playback,
and alarm sound management across different platforms.
"""

import os
import sys
import subprocess
import threading
import time
import logging
from typing import Optional

from gtts import gTTS

from config import (
    TTS_OUTPUT_FILE, ALARM_WAV_FILE, AUDIO_PLAYER_LINUX, 
    TTS_PLAYER_LINUX, TTS_LANGUAGE
)
from utils import get_platform_command


class AudioManager:
    """Manages audio playback for TTS and alarm sounds."""
    
    def __init__(self):
        self.logger = logging.getLogger('kiosk_clock.audio')
        self.tts_process: Optional[subprocess.Popen] = None
        self.alarm_process: Optional[subprocess.Popen] = None
        self._lock = threading.RLock()
    
    def play_alarm_sound(self) -> bool:
        """
        Play the alarm sound file.
        
        Returns:
            True if alarm started successfully, False otherwise
        """
        if not os.path.exists(ALARM_WAV_FILE):
            self.logger.warning(f"Alarm file {ALARM_WAV_FILE} not found")
            return False
        
        try:
            self.logger.info(f"In play_alarm_sound")
            with self._lock:
                # Stop any existing alarm
                self.stop_alarm_sound()
                
                if sys.platform.startswith('win'):
                    import winsound
                    # Play sound in a separate thread for Windows
                    def play_windows_sound():
                        winsound.PlaySound(ALARM_WAV_FILE, winsound.SND_FILENAME)
                    
                    thread = threading.Thread(target=play_windows_sound, daemon=True)
                    thread.start()
                    
                else:
                    # Linux/macOS using aplay or afplay
                    command = get_platform_command(
                        windows_cmd='',  # Handled above
                        macos_cmd='afplay',
                        linux_cmd=AUDIO_PLAYER_LINUX
                    )
                    
                    self.alarm_process = subprocess.Popen(
                        [command, ALARM_WAV_FILE],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                self.logger.info("Alarm sound started")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to play alarm sound: {e}")
            return False
    
    def stop_alarm_sound(self) -> None:
        """Stop the currently playing alarm sound."""
        try:
            with self._lock:
                if sys.platform.startswith('win'):
                    try:
                        import winsound
                        winsound.PlaySound(None, winsound.SND_PURGE)
                    except Exception as e:
                        self.logger.debug(f"Could not stop Windows sound: {e}")
                
                elif self.alarm_process and self.alarm_process.poll() is None:
                    try:
                        self.alarm_process.terminate()
                        # Wait a bit for graceful termination
                        time.sleep(0.1)
                        if self.alarm_process.poll() is None:
                            self.alarm_process.kill()
                    except Exception as e:
                        self.logger.debug(f"Could not stop alarm process: {e}")
                
                self.alarm_process = None
                self.logger.debug("Alarm sound stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping alarm sound: {e}")
    
    def speak_text(self, text: str) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
        """
        def speak_thread():
            try:
                # Stop any existing TTS
                self.stop_tts()
                
                self.logger.info("TTS playback started")

                # Clean up any existing temporary file
                if os.path.exists(TTS_OUTPUT_FILE):
                    try:
                        os.remove(TTS_OUTPUT_FILE)
                    except Exception as e:
                        self.logger.debug(f"Could not remove TTS file: {e}")
                
                # Generate speech
                tts = gTTS(text=text, lang=TTS_LANGUAGE)
                tts.save(TTS_OUTPUT_FILE)
                self.logger.info("TTS file saved")
                
                # Play the generated audio
                self._play_audio_file(TTS_OUTPUT_FILE)
                
                self.logger.info("TTS playback completed")
                
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
            finally:
                self.stop_tts()  # Ensure cleanup
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def _play_audio_file(self, file_path: str) -> None:
        """
        Play an audio file using platform-appropriate player.
        
        Args:
            file_path: Path to audio file to play
        """
        try:
            with self._lock:
                command = get_platform_command(
                    windows_cmd='start',
                    macos_cmd='afplay',
                    linux_cmd=TTS_PLAYER_LINUX
                )
                
                if sys.platform.startswith('win'):
                    # Windows: use start command
                    self.tts_process = subprocess.Popen(
                        ['start', '/wait', file_path],
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Linux/macOS
                    self.tts_process = subprocess.Popen(
                        [command, file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                # Wait for playback to complete
                if self.tts_process:
                    self.tts_process.wait()
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Error playing audio file {file_path}: {e}")
            if command == TTS_PLAYER_LINUX:
                self.logger.error(f"Please ensure {TTS_PLAYER_LINUX} is installed")
    
    def stop_tts(self) -> None:
        """Stop any running TTS playback."""
        try:
            with self._lock:
                if self.tts_process and self.tts_process.poll() is None:
                    try:
                        # Try graceful termination first
                        self.tts_process.terminate()
                        time.sleep(0.1)
                        
                        # If still running, force kill
                        if self.tts_process.poll() is None:
                            self.tts_process.kill()
                            
                    except Exception as e:
                        self.logger.debug(f"Error stopping TTS process: {e}")
                        
                        # Last resort: use pkill on Linux
                        if not sys.platform.startswith('win'):
                            try:
                                subprocess.run(['pkill', '-9', TTS_PLAYER_LINUX])
                            except Exception as e:
                                self.logger.debug(f"Failed to force kill {TTS_PLAYER_LINUX}: {e}")
                
                self.tts_process = None
                
                # Clean up temporary file
                if os.path.exists(TTS_OUTPUT_FILE):
                    try:
                        os.remove(TTS_OUTPUT_FILE)
                    except Exception as e:
                        self.logger.debug(f"Could not remove TTS file: {e}")
                
        except Exception as e:
            self.logger.error(f"Error stopping TTS: {e}")
    
    def cleanup(self) -> None:
        """Clean up all audio resources."""
        self.stop_alarm_sound()
        self.stop_tts()
        self.logger.info("Audio manager cleaned up")
    
    def is_tts_playing(self) -> bool:
        """Check if TTS is currently playing."""
        return self.tts_process is not None and self.tts_process.poll() is None
    
    def is_alarm_playing(self) -> bool:
        """Check if alarm is currently playing."""
        return self.alarm_process is not None and self.alarm_process.poll() is None 