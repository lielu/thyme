# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Utility functions and common helpers for Kiosk Clock application.

This module contains logging setup, file operations, and other
utility functions used throughout the application.
"""

import os
import sys
import logging
import glob
from typing import List, Optional, Tuple
from datetime import datetime
import tkinter as tk
from PIL import Image


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('kiosk_clock')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_file = os.path.join('logs', f'kiosk_clock_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_screen_dimensions(root: tk.Tk) -> Tuple[int, int]:
    """
    Get screen dimensions.
    
    Args:
        root: Tkinter root window
        
    Returns:
        Tuple of (width, height)
    """
    return root.winfo_screenwidth(), root.winfo_screenheight()


def create_shadow_text(canvas: tk.Canvas, x: int, y: int, text: str = '', 
                      font: Optional[Tuple] = None, anchor: str = 'nw', 
                      justify: str = 'left', shadow_offset: int = 2) -> Tuple[int, int]:
    """
    Create text with shadow effect on canvas.
    
    Args:
        canvas: Tkinter canvas
        x, y: Position coordinates
        text: Text to display
        font: Font tuple (family, size, style)
        anchor: Text anchor point
        justify: Text justification
        shadow_offset: Pixel offset for shadow
        
    Returns:
        Tuple of (main_text_id, shadow_text_id)
    """
    # Create shadow text (darker)
    shadow = canvas.create_text(
        x + shadow_offset, y + shadow_offset,
        text=text,
        font=font,
        fill='#333333',
        anchor=anchor,
        justify=justify
    )
    
    # Create main text (white)
    main = canvas.create_text(
        x, y,
        text=text,
        font=font,
        fill='white',
        anchor=anchor,
        justify=justify
    )
    
    return main, shadow


def get_image_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Get list of image files from directory.
    
    Args:
        directory: Directory path to search
        extensions: List of file extensions to include
        
    Returns:
        List of image file paths
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    
    if not os.path.exists(directory):
        return []
    
    image_files = []
    for ext in extensions:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern, recursive=False))
        # Also check uppercase
        pattern = os.path.join(directory, ext.upper())
        image_files.extend(glob.glob(pattern, recursive=False))
    
    return sorted(list(set(image_files)))  # Remove duplicates and sort


def load_and_resize_image(image_path: str, target_size: Tuple[int, int]) -> Optional[Image.Image]:
    """
    Load and resize image to target size.
    
    Args:
        image_path: Path to image file
        target_size: Target size as (width, height)
        
    Returns:
        PIL Image object or None if failed
    """
    try:
        img = Image.open(image_path)
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        logging.getLogger('kiosk_clock').error(f"Failed to load image {image_path}: {e}")
        return None


def parse_time_string(time_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse time string in HH:MM format.
    
    Args:
        time_str: Time string in format "HH:MM"
        
    Returns:
        Tuple of (hours, minutes) or None if invalid
    """
    try:
        parts = time_str.strip().split(':')
        if len(parts) != 2:
            return None
        
        hours = int(parts[0])
        minutes = int(parts[1])
        
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return hours, minutes
        else:
            return None
    except (ValueError, AttributeError):
        return None


def time_to_minutes(time_str: str) -> Optional[int]:
    """
    Convert time string to minutes since midnight.
    
    Args:
        time_str: Time string in format "HH:MM"
        
    Returns:
        Minutes since midnight or None if invalid
    """
    parsed = parse_time_string(time_str)
    if parsed is None:
        return None
    
    hours, minutes = parsed
    return hours * 60 + minutes


def safe_file_operation(operation, *args, **kwargs):
    """
    Safely perform file operation with error handling.
    
    Args:
        operation: Function to call
        *args, **kwargs: Arguments to pass to operation
        
    Returns:
        Result of operation or None if failed
    """
    logger = logging.getLogger('kiosk_clock')
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"File operation failed: {e}")
        return None


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logging.getLogger('kiosk_clock').error(f"Failed to create directory {directory}: {e}")
        return False


def get_platform_command(windows_cmd: str, macos_cmd: str, linux_cmd: str) -> str:
    """
    Get platform-specific command.
    
    Args:
        windows_cmd: Command for Windows
        macos_cmd: Command for macOS
        linux_cmd: Command for Linux
        
    Returns:
        Appropriate command for current platform
    """
    if sys.platform.startswith('win'):
        return windows_cmd
    elif sys.platform == 'darwin':
        return macos_cmd
    else:
        return linux_cmd 