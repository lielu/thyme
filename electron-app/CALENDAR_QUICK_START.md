# Google Calendar - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Get Credentials (2 minutes)
1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials → **Desktop app**
5. Download as `credentials.json`

### Step 2: Add to App (30 seconds)
```bash
# Copy to config directory
cp ~/Downloads/credentials.json electron-app/config/
```

### Step 3: Authenticate (1 minute)
1. Launch the app
2. Press **F6** to open Settings
3. Scroll to "📅 Google Calendar"
4. Click **🔐 Authenticate with Google Calendar**
5. Sign in with Google
6. Click **Allow**

### Step 4: Enjoy! ✅
Your calendar events now appear on the display!

## 🎯 Status Check

After authentication, you should see:
- Status: **✓ Authenticated and ready** (green)
- Events visible on main display
- Events update every 10 seconds

## ❓ Troubleshooting

### "Missing credentials.json"
- Make sure file is in `config/` directory
- Restart the app

### "Authentication failed"
- Check internet connection
- Try clicking "Allow" again
- Verify credentials.json is valid

### Events not showing
- Check Calendar ID in settings (default: "primary")
- Verify you have events today in Google Calendar
- Check timezone settings match your location

## 📚 Full Documentation

For detailed instructions, troubleshooting, and advanced configuration:
- **Setup Guide:** [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)
- **Technical Details:** [CALENDAR_OAUTH_FEATURE.md](CALENDAR_OAUTH_FEATURE.md)

## 🔐 Security

- ✅ Official Google OAuth 2.0
- ✅ Read-only access to calendar
- ✅ Tokens stored locally only
- ✅ Open source - review the code!

---

**Need help?** Check the full [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) guide.

