# Migration Guide: Python/Tkinter → Electron

This guide helps you migrate from the Python/Tkinter version to the Electron version of Thyme Kiosk Clock.

## Why Migrate to Electron?

### Advantages

✅ **Better Cross-Platform Support**
- Consistent behavior on macOS, Linux, and Windows
- Native installers (DMG, AppImage, Deb)
- Easier deployment

✅ **Modern UI**
- Better styling with CSS
- Smoother animations
- Responsive design

✅ **Better Package Management**
- npm ecosystem
- Easier dependency management
- Auto-updates capability

✅ **Development Experience**
- Hot reload during development
- Better debugging tools
- Modern JavaScript features

### Trade-offs

⚠️ **Resource Usage**
- Higher memory footprint (~200MB vs ~50MB)
- Chromium engine overhead
- Still acceptable for Raspberry Pi 4+

⚠️ **Initial Setup**
- Requires Node.js installation
- Different configuration format
- OAuth token conversion needed

## Step-by-Step Migration

### 1. Prerequisites

Install Node.js:

```bash
# macOS (using Homebrew)
brew install node

# Linux
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be v18.x or higher
npm --version
```

### 2. Install Electron App

```bash
cd electron-app
npm install
```

### 3. Migrate Configuration

The Python version uses `alarm_config.txt`, while Electron uses `alarm_config.json`.

#### Automatic Migration Script

Create this script to convert your settings:

```bash
#!/bin/bash
# migrate_config.sh

PYTHON_CONFIG="../src/alarm_config.txt"
ELECTRON_CONFIG="./config/alarm_config.json"

if [ ! -f "$PYTHON_CONFIG" ]; then
    echo "Python config not found"
    exit 1
fi

# Extract settings from Python config
CALENDAR_ID=$(grep "^CALENDAR_ID=" "$PYTHON_CONFIG" | cut -d'=' -f2)
LATITUDE=$(grep "^LATITUDE=" "$PYTHON_CONFIG" | cut -d'=' -f2)
LONGITUDE=$(grep "^LONGITUDE=" "$PYTHON_CONFIG" | cut -d'=' -f2)
TIMEZONE=$(grep "^TIMEZONE=" "$PYTHON_CONFIG" | cut -d'=' -f2)
TEMP_UNIT=$(grep "^TEMP_UNIT=" "$PYTHON_CONFIG" | cut -d'=' -f2)
DISCORD_TOKEN=$(grep "^DISCORD_TOKEN=" "$PYTHON_CONFIG" | cut -d'=' -f2)
DISCORD_CHANNEL=$(grep "^DISCORD_CHANNEL_ID=" "$PYTHON_CONFIG" | cut -d'=' -f2)

# Extract alarms (lines that are HH:MM format)
ALARMS=$(grep -E "^[0-9]{2}:[0-9]{2}$" "$PYTHON_CONFIG" | jq -R . | jq -s .)

# Create JSON config
cat > "$ELECTRON_CONFIG" <<EOF
{
  "hideCursor": true,
  "fullscreen": true,
  "calendarId": "${CALENDAR_ID:-primary}",
  "latitude": ${LATITUDE:-32.7767},
  "longitude": ${LONGITUDE:--96.7970},
  "timezone": "${TIMEZONE:-America/Chicago}",
  "temperatureUnit": "${TEMP_UNIT:-fahrenheit}",
  "discordToken": "${DISCORD_TOKEN:-}",
  "discordChannelId": "${DISCORD_CHANNEL:-}",
  "alarms": ${ALARMS:-[]},
  "eventsRefreshInterval": 10000,
  "weatherUpdateInterval": 3600000,
  "discordUpdateInterval": 10000,
  "backgroundChangeInterval": 30000
}
EOF

echo "Configuration migrated successfully!"
```

Run it:

```bash
chmod +x migrate_config.sh
./migrate_config.sh
```

#### Manual Migration

Edit `config/alarm_config.json` and copy values from your Python `alarm_config.txt`:

**Python format:**
```
CALENDAR_ID=your.email@gmail.com
LATITUDE=32.7767
LONGITUDE=-96.7970
07:00
08:30
```

**Electron format:**
```json
{
  "calendarId": "your.email@gmail.com",
  "latitude": 32.7767,
  "longitude": -96.7970,
  "alarms": ["07:00", "08:30"]
}
```

### 4. Migrate Google Calendar Credentials

Copy your existing credentials:

```bash
# Copy credentials
cp ../src/credentials.json ./config/

# Convert token from pickle to JSON (requires Python)
cd ../src
python3 << 'EOF'
import pickle
import json

try:
    with open('token.pickle', 'rb') as f:
        creds = pickle.load(f)
    
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    
    with open('../electron-app/config/token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("Token converted successfully!")
except Exception as e:
    print(f"Error: {e}")
    print("You may need to re-authenticate with Google Calendar")
EOF
```

### 5. Copy Assets

```bash
# From electron-app directory
cp -r ../src/backgrounds/* ./assets/backgrounds/
cp -r ../src/sounds/* ./assets/sounds/
cp -r ../src/weather_icons/* ./assets/weather_icons/
```

### 6. Test the Electron App

```bash
# Development mode (with debugging)
npm run dev

# Or use the startup script
./start.sh --dev
```

### 7. Deploy

Once everything works:

```bash
# Production mode
npm start

# Or build installer
npm run build
```

## Feature Parity Check

| Feature | Python | Electron | Notes |
|---------|--------|----------|-------|
| Clock Display | ✅ | ✅ | |
| Date Display | ✅ | ✅ | |
| Google Calendar | ✅ | ✅ | Requires token migration |
| Alarms | ✅ | ✅ | |
| Weather | ✅ | ✅ | |
| Discord | ✅ | ✅ | |
| Background Rotation | ✅ | ✅ | |
| Bing Wallpaper | ✅ | ✅ | |
| TTS Announcements | ✅ | ✅ | Uses `say` library |
| Settings UI | ✅ | ✅ | More modern in Electron |
| Display Schedule | ✅ | 🚧 | Not yet implemented |
| Keyboard Shortcuts | ✅ | ✅ | |

## Raspberry Pi Considerations

### Performance

- **Raspberry Pi 4 (4GB+)**: Excellent performance
- **Raspberry Pi 4 (2GB)**: Good performance
- **Raspberry Pi 3**: May be slower, not recommended
- **Raspberry Pi 5**: Best performance

### Memory Usage

- Python version: ~50-80 MB
- Electron version: ~150-250 MB
- Recommendation: Minimum 2GB RAM

### Auto-Start Setup

The process is similar but uses different commands:

**Python systemd service:**
```ini
ExecStart=/usr/bin/python3 /home/pi/src/kiosk_clock_app.py
```

**Electron systemd service:**
```ini
ExecStart=/usr/bin/npm start
WorkingDirectory=/home/pi/electron-app
```

## Troubleshooting Migration

### Calendar Not Working

If calendar doesn't work after migration:

1. Check that `credentials.json` exists in `config/`
2. Verify `token.json` was created correctly
3. If conversion failed, re-run OAuth flow:
   - Run Python version once
   - Follow OAuth prompts
   - Re-run token conversion script

### Alarms Not Triggering

1. Check alarm format in `config/alarm_config.json`
2. Verify times are in "HH:MM" format (24-hour)
3. Check console for cron errors: `npm run dev`

### Discord Not Connecting

1. Verify token and channel ID are correct
2. Check bot permissions
3. Ensure "Message Content Intent" is enabled

### Audio Issues

**Linux:**
```bash
# Install ALSA utilities
sudo apt-get install alsa-utils

# Test audio
aplay assets/sounds/alarm.wav
```

**macOS:**
```bash
# Should work out of the box
afplay assets/sounds/alarm.wav
```

### Build Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

## Reverting to Python Version

If you need to revert:

1. Keep both versions installed
2. They use separate config files
3. Can run both (but not simultaneously)

```bash
# Run Python version
cd src
python3 kiosk_clock_app.py

# Run Electron version
cd electron-app
npm start
```

## Getting Help

- Check logs: `npm run dev` shows console output
- Review `README.md` for detailed documentation
- Check GitHub issues for common problems

## Next Steps

Once migrated successfully:

1. Set up auto-start (systemd)
2. Build installer for your platform
3. Configure all settings via Settings UI
4. Test all features thoroughly
5. Consider removing Python version

---

**Happy migrating! 🚀**

