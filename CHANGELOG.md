# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-05-23

### Major Refactoring 🎉

This release represents a complete rewrite of the Kiosk Clock application with a focus on modularity, maintainability, and open source best practices.

### Added
- **Modular Architecture**: Split monolithic code into specialized managers
  - `CalendarManager` for Google Calendar integration
  - `AudioManager` for TTS and alarm sounds
  - `AlarmManager` for alarm scheduling and display control
  - `WeatherManager` for weather data and icons
  - `BackgroundManager` for dynamic backgrounds
- **Configuration Management**: Centralized configuration in `config.py`
- **Environment Variable Support**: Configure via environment variables
- **Comprehensive Logging**: Structured logging with rotation
- **Type Hints**: Full type annotations throughout codebase
- **Error Handling**: Graceful error recovery and fallbacks
- **Cross-Platform Audio**: Improved audio handling for Windows/macOS/Linux
- **Installation Script**: `setup.py` for easy installation
- **Development Tools**: Pre-commit hooks, linting, testing framework
- **Documentation**: Complete README, contributing guide, and code docs

### Improved
- **Code Quality**: Following PEP 8 and best practices
- **Performance**: More efficient background image handling
- **Reliability**: Better error handling and recovery
- **User Experience**: Clearer configuration and setup process
- **Developer Experience**: Modular code easier to extend and maintain

### Changed
- **Entry Point**: Main application now in `kiosk_clock_app.py`
- **Configuration**: Uses environment variables and improved config file format
- **File Structure**: Organized into logical modules
- **Dependencies**: Updated to latest stable versions with proper constraints

### Backward Compatibility
- **Legacy Support**: Original `kiosk_clock.py` provides compatibility wrapper
- **Configuration**: Existing `alarm_config.txt` files still work
- **Asset Files**: Weather icons and backgrounds use same format

### Open Source Ready
- **MIT License**: Added open source license
- **Contributing Guide**: Detailed contribution guidelines
- **Issue Templates**: GitHub issue and PR templates
- **CI/CD Ready**: Prepared for continuous integration
- **Package Distribution**: Ready for PyPI publication

### Technical Improvements
- **Memory Management**: Better resource cleanup and garbage collection
- **Thread Safety**: Improved thread management for audio and background tasks
- **API Integration**: More robust weather and calendar API handling
- **Display Management**: Enhanced screen power control for various platforms

## [1.0.0] - 2025-05-09

### Initial Release
- Basic fullscreen clock display
- Google Calendar integration
- Simple alarm system
- Weather display
- Background image rotation
- Text-to-speech announcements
- Raspberry Pi support

---

### Migration Guide (1.0 → 2.0)

#### For Users
1. **Update your startup script** to use `python kiosk_clock_app.py`
2. **Set environment variables** for location and calendar settings:
   ```bash
   export KIOSK_CALENDAR_ID="your-email@gmail.com"
   export KIOSK_LATITUDE="32.7767"
   export KIOSK_LONGITUDE="-96.7970"
   ```
3. **Install new dependencies**: `pip install -r requirements.txt`
4. **Existing files**: Your `alarm_config.txt`, weather icons, and backgrounds will continue to work

#### For Developers
1. **New module structure**: Import from specific managers instead of main file
2. **Configuration**: Use `config.py` for all constants and settings
3. **Logging**: Use the structured logging system
4. **Error handling**: Follow the new error handling patterns
5. **Type hints**: Add type annotations to new code

### Breaking Changes
- Main entry point moved from `kiosk_clock.py` to `kiosk_clock_app.py`
- Some internal APIs have changed (affects only developers extending the code)
- Configuration through environment variables (old hardcoded values may need updating)

### Deprecations
- Direct execution of `kiosk_clock.py` is deprecated (compatibility wrapper provided)
- Hardcoded configuration values should be moved to environment variables 