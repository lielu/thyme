# Quick Start Guide

Get Thyme Kiosk Clock running in 5 minutes!

## 🚀 Installation

```bash
cd electron-app
npm install
```

## ⚡ Run

```bash
# Easy start
./start.sh

# Or manually
npm start

# Development mode (with DevTools)
npm run dev
```

## ⚙️ Basic Configuration

### Option 1: Using Settings UI (Recommended)

1. Start the app
2. Click the ⚙️ icon (top right)
3. Configure your settings
4. Click "Save & Apply"

### Option 2: Edit Config File

Edit `config/alarm_config.json`:

```json
{
  "latitude": 32.7767,
  "longitude": -96.7970,
  "timezone": "America/Chicago",
  "temperatureUnit": "fahrenheit",
  "alarms": ["07:00", "08:00"]
}
```

## 📅 Google Calendar Setup

1. Get credentials from [Google Cloud Console](https://console.cloud.google.com)
2. Enable Google Calendar API
3. Download `credentials.json`
4. Place in `config/` directory
5. Run Python version once for OAuth
6. Token will be automatically converted

## 💬 Discord Setup (Optional)

1. Create bot at [Discord Developer Portal](https://discord.com/developers)
2. Enable "Message Content Intent"
3. Get bot token and channel ID
4. Add to Settings UI or config file

## 🎹 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F6** | Open Settings |
| **F5** | Reload Config |
| **Esc** | Close Settings/Exit |

## 🐛 Quick Troubleshooting

### App won't start
```bash
npm install
npm start
```

### No weather data
- Check latitude/longitude in settings
- Verify internet connection

### Calendar not working
- Ensure `credentials.json` exists
- Complete OAuth flow (run Python version once)

### Audio not working
**Linux:**
```bash
sudo apt-get install alsa-utils
```

**macOS:** Should work automatically

## 📦 Building

```bash
# Current platform
npm run build

# Linux
npm run build:linux

# macOS  
npm run build:mac
```

Output in `dist/` directory.

## 🍓 Raspberry Pi

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Run
cd electron-app
npm install
npm start
```

## 📖 Full Documentation

- **README.md** - Complete documentation
- **MIGRATION_GUIDE.md** - Migrate from Python version
- **package.json** - All available commands

## 🆘 Need Help?

1. Check console logs: `npm run dev`
2. Review README.md
3. Check MIGRATION_GUIDE.md if migrating

---

**That's it! Enjoy your beautiful kiosk clock! ✨**

