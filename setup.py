#!/usr/bin/env python3
# Copyright (c) 2025 Lie Lu
# Licensed under the MIT License - see LICENSE file for details

"""
Setup script for Kiosk Clock application.

This script handles the package installation, dependencies,
and creates the command-line entry point for the application.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="kiosk-clock",
    version="2.0.0",
    author="Kiosk Clock Contributors",
    author_email="your-email@example.com",
    description="A beautiful, full-screen digital clock with Google Calendar integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/kiosk-clock",
    project_urls={
        "Bug Reports": "https://github.com/your-username/kiosk-clock/issues",
        "Source": "https://github.com/your-username/kiosk-clock",
        "Documentation": "https://github.com/your-username/kiosk-clock#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Gnome",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords="clock, calendar, kiosk, display, raspberry-pi, weather, alarm",
    py_modules=[
        "kiosk_clock_app",
        "config",
        "utils",
        "calendar_integration", 
        "audio_manager",
        "alarm_manager",
        "weather_manager",
        "background_manager",
        "kiosk_clock"  # Backward compatibility
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "pre-commit>=2.15",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "pytest-mock>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kiosk-clock=kiosk_clock_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "weather_icons/*.png",
            "*.txt",
            "*.sh",
            "*.md",
            "LICENSE",
        ],
    },
    zip_safe=False,
) 