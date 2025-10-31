# Google Calendar Direct Setup Guide

The Electron app now supports **direct Google Calendar authentication** without requiring the Python version! 🎉

## ✨ What's New

- **Built-in OAuth flow** - Authenticate directly from the app
- **Visual status indicator** - See your authentication status at a glance
- **One-click setup** - No command-line tools needed
- **Automatic token refresh** - Stays authenticated
- **User-friendly errors** - Clear guidance if something goes wrong

## 🚀 Quick Setup (5 Steps)

### Step 1: Get Google Calendar Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Desktop application** as the application type
6. Download the credentials as **`credentials.json`**

### Step 2: Add Credentials to App

Place the downloaded `credentials.json` file in the app's config directory:

```bash
# Copy to config directory
cp ~/Downloads/credentials.json ~/path/to/electron-app/config/
```

Or if using the installed app:
- **macOS**: `~/Library/Application Support/thyme-kiosk-clock/config/`
- **Linux**: `~/.config/thyme-kiosk-clock/config/`

### Step 3: Open Settings

1. Launch Thyme Kiosk Clock
2. Press **F6** or click the **⚙️ icon** (top-right)
3. Scroll to the **📅 Google Calendar** section

### Step 4: Authenticate

1. Check the **Authentication Status** - should say "Not authenticated yet"
2. Click **🔐 Authenticate with Google Calendar**
3. A Google sign-in window will open
4. Sign in with your Google account
5. Click **Allow** to grant calendar access
6. Window will close automatically

### Step 5: Verify

- Status should show: **✓ Authenticated and ready**
- Your calendar events will now appear on the main display!

## 📋 Detailed Instructions

### Getting Google Cloud Credentials

#### A. Create a Google Cloud Project

1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Enter project name: "Thyme Kiosk Clock"
4. Click **Create**

#### B. Enable Calendar API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click on it and click **Enable**

#### C. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: "Thyme Kiosk Clock"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add **Google Calendar API** → **calendar.readonly**
   - Test users: Add your Gmail address
   - Save and continue
4. Back to **Create OAuth client ID**:
   - Application type: **Desktop app**
   - Name: "Thyme Kiosk Clock"
5. Click **Create**
6. Click **Download JSON**
7. Rename to `credentials.json`

### Using the Authentication UI

#### Authentication Status Indicators

| Status | Meaning |
|--------|---------|
| **✓ Authenticated and ready** | Working perfectly |
| **⏳ Not authenticated yet** | credentials.json found, click to authenticate |
| **⚠ Token found but not connected** | Try re-authenticating |
| **✕ Missing credentials.json** | Add credentials.json first |

#### Troubleshooting Authentication

**Issue: "Missing credentials.json"**
- Make sure `credentials.json` is in the `config/` directory
- Restart the app after adding the file

**Issue: "Authentication failed"**
- Check your internet connection
- Make sure you clicked "Allow" in the Google sign-in
- Verify the credentials.json file is valid (not corrupted)

**Issue: "Token found but not connected"**
- Click "Re-authenticate" to get a fresh token
- Check console logs: run app with `npm run dev`

**Issue: Authentication window doesn't close**
- Close it manually
- The authentication might have succeeded anyway
- Check the status indicator

## 🔄 Re-authenticating

If you need to re-authenticate (e.g., changed Google account):

1. Open Settings (F6)
2. Go to Google Calendar section
3. Click **🔄 Re-authenticate**
4. Sign in again

## 📁 File Locations

### Development (from source)

```
electron-app/
└── config/
    ├── credentials.json    # Your credentials (add this)
    └── token.json          # Created automatically
```

### Installed App

**macOS:**
```
~/Library/Application Support/thyme-kiosk-clock/
└── config/
    ├── credentials.json
    └── token.json
```

**Linux:**
```
~/.config/thyme-kiosk-clock/
└── config/
    ├── credentials.json
    └── token.json
```

## 🔒 Security & Privacy

### What Access Does the App Need?

The app requests **read-only access** to your calendar:
- Scope: `calendar.readonly`
- Can view events
- **Cannot** create, modify, or delete events
- **Cannot** access other Google services

### Is It Safe?

✅ **Yes!** The authentication is:
- Official Google OAuth 2.0
- Tokens stored locally on your device
- No third-party servers involved
- Open source - you can review the code

### Where Are Tokens Stored?

- Tokens are stored in `config/token.json`
- Only accessible by the app on your device
- Never sent to any external server (except Google for refresh)

## 🎓 Advanced Configuration

### Custom Calendar ID

By default, the app uses your primary calendar (`primary`). To use a different calendar:

1. Find your calendar ID:
   - Go to [Google Calendar](https://calendar.google.com)
   - Click the 3 dots next to the calendar
   - Settings and sharing
   - Scroll to "Integrate calendar"
   - Copy the "Calendar ID"

2. In Settings:
   - Paste the calendar ID in the "Calendar ID" field
   - Click "Save & Apply"

### Multiple Calendars

Currently, the app displays events from one calendar at a time. To see multiple calendars:
- Use your primary calendar (which can show events from other calendars if they're overlaid)
- Or manually switch the calendar ID in settings

### Redirect URI

The app uses `http://localhost:3000/oauth2callback` as the redirect URI. This is automatically configured when you create OAuth credentials for a "Desktop app".

If you need to use a different redirect URI:
1. Update it in Google Cloud Console
2. Update `credentials.json` with the new redirect URI

## 🆘 Troubleshooting

### Common Issues

#### "credentials.json not found"

**Solution:**
```bash
# Check if file exists
ls config/credentials.json

# If not, add it
cp ~/Downloads/credentials.json config/
```

#### "Invalid client"

**Cause:** credentials.json is not valid or from wrong project type

**Solution:**
- Make sure you selected "Desktop app" when creating credentials
- Download fresh credentials from Google Cloud Console

#### "Access denied"

**Cause:** App is not approved for your Google Workspace

**Solution:**
- If using Google Workspace, admin needs to approve the app
- Or use a personal Gmail account

#### Events not showing

**Possible causes:**
1. Calendar ID is wrong → Check and update in settings
2. No events today → Check Google Calendar web
3. Not authenticated → Re-authenticate

**Debug:**
```bash
# Run in development mode to see logs
npm run dev

# Check for calendar errors in console
```

## 📚 API Limits

Google Calendar API has these limits (free tier):
- **10,000 requests per day**
- **100 requests per 100 seconds**

The app fetches events every 10 seconds, using ~8,640 requests per day, which is well within limits.

## 🔄 Migrating from Python Version

If you previously used the Python version:

1. **Copy credentials:**
   ```bash
   cp ../src/credentials.json config/
   ```

2. **Convert token (optional):**
   - If you have `token.pickle` from Python, it needs conversion
   - Or just re-authenticate using the button (easier!)

3. **That's it!**
   - The Electron app now handles everything

## ✅ Verification Checklist

After setup, verify:
- [ ] `credentials.json` exists in `config/` directory
- [ ] Settings shows "✓ Authenticated and ready"
- [ ] Today's events appear on main display
- [ ] Events update every 10 seconds
- [ ] Alarm announcements include events

## 💡 Tips

1. **Test with a test calendar first** - Create a test calendar with a few events to verify it works

2. **Keep credentials.json safe** - It contains your OAuth client secret (though it's not highly sensitive)

3. **Backup token.json** - If you don't want to re-authenticate after reinstalling

4. **Check event privacy** - Only events you can see will appear

5. **Time zones matter** - Make sure app timezone matches your calendar timezone in settings

## 🎉 Success!

If you see your events on the display, you're all set! The app will:
- ✅ Auto-refresh events every 10 seconds
- ✅ Show today's events (up to 3 by default)
- ✅ Announce events when alarm goes off
- ✅ Refresh authentication token automatically

Enjoy your calendar-integrated kiosk clock! 🎊

---

**Need more help?** 
- Check console logs: `npm run dev`
- Review `CalendarManager.js` for implementation details
- Open an issue on GitHub

