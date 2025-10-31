# Thyme Kiosk Clock - Electron Edition

A beautiful, full-screen kiosk clock application with Google Calendar integration, weather display, Discord messages, and customizable alarms. Built with Electron for cross-platform compatibility.

![Thyme Kiosk Clock](https://img.shields.io/badge/version-2.0.0-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🕐 **Large Digital Clock** - Easy-to-read time display
- 📅 **Google Calendar Integration** - View today's events with **built-in OAuth authentication**
- 🌤️ **Weather Display** - Current weather with Open-Meteo API
- ⏰ **Customizable Alarms** - Set multiple daily alarms with TTS announcements
- 💬 **Discord Integration** - Display recent messages from a Discord channel
- 🖼️ **Dynamic Backgrounds** - Automatic Bing wallpaper downloads and rotation
- ⚙️ **Settings Panel** - Easy-to-use configuration interface
- 🔒 **Secure** - Context isolation and secure IPC communication

## 📋 Requirements

- **Node.js** 18.x or higher
- **npm** or **yarn**
- **Operating System**: macOS 10.13+, Linux (Ubuntu 18.04+, Raspberry Pi OS)

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the electron-app directory
cd electron-app

# Install dependencies
npm install
```

### 2. Configuration

#### Google Calendar (Optional)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download the credentials as `credentials.json`
5. Place `credentials.json` in the `config/` directory
6. **NEW!** Use the built-in authentication button in Settings to authenticate directly (no Python required!)

📖 **Detailed guide:** See [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) for complete setup instructions

#### Weather Settings

Edit `config/alarm_config.json` or use the Settings UI:
- Set your `latitude` and `longitude`
- Choose your `timezone`
- Select temperature unit (`fahrenheit` or `celsius`)

#### Discord Integration (Optional)

1. Create a Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable "Message Content Intent"
3. Copy the bot token
4. Add the bot to your server
5. Copy the channel ID (enable Developer Mode in Discord)
6. Add to `config/alarm_config.json` or use Settings UI

### 3. Running the Application

```bash
# Development mode (with DevTools)
npm run dev

# Production mode
npm start
```

## 🎨 Usage

### Keyboard Shortcuts

- **F6** - Open Settings
- **F5** - Reload Configuration
- **Escape** - Close Settings or Exit App

### Settings Panel

Click the ⚙️ icon in the top-right to access settings:

1. **Display Settings**
   - Fullscreen mode
   - Hide cursor

2. **Google Calendar**
   - Calendar ID configuration
   - **One-click OAuth authentication** 🔐
   - Real-time authentication status

3. **Weather & Location**
   - Latitude/Longitude
   - Timezone
   - Temperature unit

4. **Discord Integration**
   - Bot token
   - Channel ID

5. **Alarms**
   - Add/remove daily alarms
   - Quick time entry

## 📦 Building for Distribution

### Build for Current Platform

```bash
npm run build
```

### Build for Specific Platforms

```bash
# Linux only
npm run build:linux

# macOS only
npm run build:mac

# Both platforms
npm run build:all
```

Built applications will be in the `dist/` directory.

### Supported Formats

- **Linux**: AppImage, Deb
- **macOS**: DMG, ZIP
- **Architectures**: x64, arm64 (including Raspberry Pi)

## 🔧 Configuration File

The `config/alarm_config.json` file contains all settings:

```json
{
  "hideCursor": true,
  "fullscreen": true,
  "calendarId": "primary",
  "latitude": 32.7767,
  "longitude": -96.7970,
  "timezone": "America/Chicago",
  "temperatureUnit": "fahrenheit",
  "discordToken": "",
  "discordChannelId": "",
  "alarms": ["07:00", "08:00"],
  "eventsRefreshInterval": 10000,
  "weatherUpdateInterval": 3600000,
  "discordUpdateInterval": 10000,
  "backgroundChangeInterval": 30000
}
```

## 🍓 Raspberry Pi Deployment

### System Requirements

- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit recommended)
- Node.js 18.x or higher

### Installation on Raspberry Pi

```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Clone/copy the electron-app directory
cd electron-app

# Install dependencies
npm install

# Run the app
npm start
```

### Auto-start on Boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/thyme-kiosk.service
```

Add:

```ini
[Unit]
Description=Thyme Kiosk Clock
After=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
WorkingDirectory=/home/pi/electron-app
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=graphical.target
```

Enable and start:

```bash
sudo systemctl enable thyme-kiosk
sudo systemctl start thyme-kiosk
```

## 📁 Project Structure

```
electron-app/
├── main/                   # Main process (Node.js)
│   ├── index.js           # Entry point
│   ├── config.js          # Configuration manager
│   ├── utils.js           # Utility functions
│   └── managers/          # Feature managers
│       ├── AlarmManager.js
│       ├── AudioManager.js
│       ├── BackgroundManager.js
│       ├── CalendarManager.js
│       ├── DiscordManager.js
│       └── WeatherManager.js
├── renderer/              # Renderer process (UI)
│   ├── index.html
│   ├── styles/
│   │   └── main.css
│   └── scripts/
│       ├── main.js
│       └── settings.js
├── preload.js            # Security bridge
├── assets/               # Static assets
│   ├── backgrounds/
│   ├── sounds/
│   └── weather_icons/
├── config/               # Configuration
│   ├── alarm_config.json
│   ├── credentials.json  # Google OAuth (not included)
│   └── token.json        # Google token (generated)
└── package.json
```

## 🛠️ Development

### Code Structure

- **Main Process** (`main/`): Handles system operations, API calls, and manages application state
- **Renderer Process** (`renderer/`): Handles UI rendering and user interactions
- **Preload Script** (`preload.js`): Provides secure bridge between main and renderer
- **Managers**: Modular components for specific features

### Adding Features

1. Create a new manager in `main/managers/`
2. Initialize in `main/index.js`
3. Add IPC handlers for communication
4. Update UI in `renderer/scripts/`

### Debugging

```bash
# Run with DevTools open
npm run dev

# View console logs
# Main process: Terminal output
# Renderer process: DevTools console
```

## 🐛 Troubleshooting

### Google Calendar Not Working

- Ensure `credentials.json` is in `config/` directory
- Complete OAuth flow using Python version first
- Check that `token.json` was created successfully

### Discord Not Connecting

- Verify bot token is correct
- Ensure bot has "Message Content Intent" enabled
- Check that bot is in the server
- Verify channel ID is correct

### Audio Not Playing

- **macOS**: Should work out of the box with `afplay`
- **Linux**: Requires `aplay` (ALSA) - `sudo apt-get install alsa-utils`
- Check that `alarm.wav` exists in `assets/sounds/`

### Background Images Not Loading

- Check that images exist in `assets/backgrounds/`
- Verify file permissions
- Check console for error messages

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- Weather data from [Open-Meteo API](https://open-meteo.com/)
- Background images from [Bing Image of the Day](https://www.bing.com/)
- Built with [Electron](https://www.electronjs.org/)

## 📞 Support

For issues, questions, or contributions, please visit the project repository.

---

**Thyme Kiosk Clock** - Wake up to beauty and information ✨

