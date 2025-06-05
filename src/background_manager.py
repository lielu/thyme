# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Background management module for Kiosk Clock application.

This module handles dynamic background image rotation with
smooth fade transitions and background downloading.
"""

import os
import random
import logging
import subprocess
from typing import List, Optional, Tuple
import tkinter as tk
from PIL import Image, ImageTk

from config import (
    BACKGROUNDS_DIR, BACKGROUND_CHANGE_INTERVAL, FADE_STEPS, 
    FADE_DURATION
)
from utils import get_image_files, load_and_resize_image, ensure_directory_exists


class BackgroundManager:
    """Manages dynamic background images with fade effects."""
    
    def __init__(self, canvas: tk.Canvas, screen_width: int, screen_height: int):
        self.logger = logging.getLogger('kiosk_clock.background')
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Background state
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.background_item: Optional[int] = None
        self.fade_job: Optional[str] = None
        self.next_bg_path: Optional[str] = None
        
        # Ensure backgrounds directory exists
        ensure_directory_exists(BACKGROUNDS_DIR)
        
        self.logger.info("Background manager initialized")
    
    def get_background_images(self) -> List[str]:
        """
        Get list of available background images.
        
        Returns:
            List of background image file paths
        """
        images = get_image_files(BACKGROUNDS_DIR)
        if not images:
            self.logger.warning(f"No background images found in {BACKGROUNDS_DIR}")
        else:
            self.logger.debug(f"Found {len(images)} background images")
        return images
    
    def load_random_background(self) -> Optional[ImageTk.PhotoImage]:
        """
        Load a random background image.
        
        Returns:
            PIL ImageTk.PhotoImage object or None if no images available
        """
        images = self.get_background_images()
        if not images:
            return None
        
        # Choose a random image
        image_path = random.choice(images)
        return self.load_background_image(image_path)
    
    def load_background_image(self, image_path: str) -> Optional[ImageTk.PhotoImage]:
        """
        Load and prepare background image for display.
        
        Args:
            image_path: Path to background image file
            
        Returns:
            PIL ImageTk.PhotoImage object or None if failed
        """
        try:
            img = load_and_resize_image(image_path, (self.screen_width, self.screen_height))
            if img:
                photo = ImageTk.PhotoImage(img)
                self.logger.debug(f"Loaded background image: {os.path.basename(image_path)}")
                return photo
            else:
                self.logger.error(f"Failed to load background image: {image_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading background image {image_path}: {e}")
            return None
    
    def set_background(self, image: ImageTk.PhotoImage) -> None:
        """
        Set background image on canvas immediately (no fade).
        
        Args:
            image: PIL ImageTk.PhotoImage to set as background
        """
        try:
            if self.background_item:
                self.canvas.delete(self.background_item)
            
            self.background_item = self.canvas.create_image(
                0, 0, image=image, anchor='nw'
            )
            self.canvas.tag_lower(self.background_item)  # Keep background behind other elements
            self.current_image = image
            
        except Exception as e:
            self.logger.error(f"Error setting background: {e}")
    
    def fade_to_new_background(self, new_image: ImageTk.PhotoImage) -> None:
        """
        Fade from current background to new background.
        
        Args:
            new_image: New background image to fade to
        """
        if not self.current_image:
            # No current background, just set the new one
            self.set_background(new_image)
            return
        
        # Cancel any existing fade operation
        if self.fade_job:
            self.canvas.after_cancel(self.fade_job)
            self.fade_job = None
        
        # Create new background item (initially transparent)
        try:
            new_bg_item = self.canvas.create_image(
                0, 0, image=new_image, anchor='nw'
            )
            self.canvas.tag_lower(new_bg_item)
            
            # Start fade animation
            self._perform_fade(new_bg_item, new_image, 0)
            
        except Exception as e:
            self.logger.error(f"Error starting background fade: {e}")
            # Fallback to immediate change
            self.set_background(new_image)
    
    def _perform_fade(self, new_bg_item: int, new_image: ImageTk.PhotoImage, step: int) -> None:
        """
        Perform one step of the fade animation.
        
        Args:
            new_bg_item: Canvas item ID of new background
            new_image: New background image
            step: Current fade step (0 to FADE_STEPS)
        """
        try:
            if step <= FADE_STEPS:
                # Calculate alpha (opacity) for this step
                alpha = int(255 * (step / FADE_STEPS))
                
                # Note: Tkinter doesn't support true alpha blending
                # This is a simplified approach - actual implementation
                # might need more sophisticated blending
                
                # Continue to next step
                step_duration = FADE_DURATION // FADE_STEPS
                self.fade_job = self.canvas.after(
                    step_duration,
                    lambda: self._perform_fade(new_bg_item, new_image, step + 1)
                )
            else:
                # Fade complete
                if self.background_item and self.background_item != new_bg_item:
                    self.canvas.delete(self.background_item)
                
                self.background_item = new_bg_item
                self.current_image = new_image
                self.fade_job = None
                self.logger.debug("Background fade completed")
                
        except Exception as e:
            self.logger.error(f"Error during fade animation: {e}")
            # Cleanup on error
            if self.background_item:
                self.canvas.delete(self.background_item)
            self.background_item = new_bg_item
            self.current_image = new_image
            self.fade_job = None
    
    def update_background(self) -> None:
        """Update background image with fade effect."""
        try:
            new_image = self.load_random_background()
            if new_image:
                if self.current_image:
                    self.fade_to_new_background(new_image)
                else:
                    self.set_background(new_image)
            
            # Schedule next update
            self.canvas.after(BACKGROUND_CHANGE_INTERVAL, self.update_background)
            
        except Exception as e:
            self.logger.error(f"Error updating background: {e}")
            # Schedule retry
            self.canvas.after(BACKGROUND_CHANGE_INTERVAL, self.update_background)
    
    def start_background_rotation(self) -> None:
        """Start automatic background rotation."""
        self.logger.info("Starting background rotation")
        # Load initial background
        initial_image = self.load_random_background()
        if initial_image:
            self.set_background(initial_image)
        
        # Start rotation timer
        self.update_background()
    
    def stop_background_rotation(self) -> None:
        """Stop automatic background rotation."""
        if self.fade_job:
            self.canvas.after_cancel(self.fade_job)
            self.fade_job = None
        self.logger.info("Background rotation stopped")
    
    def download_bing_wallpaper(self) -> bool:
        """
        Download Bing daily wallpaper to backgrounds directory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            script_path = os.path.join(os.getcwd(), 'download_bing_wallpaper.sh')
            if os.path.exists(script_path):
                result = subprocess.run(
                    ['bash', script_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info("Successfully downloaded Bing wallpaper")
                    return True
                else:
                    self.logger.warning(f"Bing wallpaper download failed: {result.stderr}")
                    return False
            else:
                self.logger.debug("Bing wallpaper download script not found")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Bing wallpaper download timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading Bing wallpaper: {e}")
            return False
    
    def get_background_info(self) -> str:
        """
        Get information about current background setup.
        
        Returns:
            Background information string
        """
        images = self.get_background_images()
        return f"Background images: {len(images)} available in {BACKGROUNDS_DIR}" 