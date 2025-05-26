# Discord Setup Guide for Kiosk Clock

This guide will help you set up Discord integration for your Kiosk Clock. The kiosk will display recent messages from a Discord channel, making it perfect for family updates, group announcements, or team communications.

## 🤖 Part 1: Create a Discord Bot

1. **Go to Discord Developer Portal:**
   - Visit: https://discord.com/developers/applications

2. **Create New Application:**
   - Click "New Application"
   - Name it something like "Family Kiosk Bot" or "Kiosk Clock"
   - Click "Create"

3. **Configure Bot Settings:**
   - Go to the "Bot" section in the left sidebar
   - Click "Add Bot" (if not already created)
   - Under "Privileged Gateway Intents", enable:
     - ✅ **Message Content Intent** (required to read message content)

4. **Copy the Bot Token:**
   - Under "Token" section, click "Copy"
   - Save this token - you'll need it for configuration
   - ⚠️ **KEEP THIS SECRET!** Never share your bot token

## 🏠 Part 2: Add Bot to Your Discord Server

1. **Generate Invite URL:**
   - In Discord Developer Portal, go to "OAuth2" > "URL Generator"

2. **Select Scopes:**
   - ✅ `bot`

3. **Select Bot Permissions:**
   - ✅ Manage Messages
   - ✅ Read Message History
   - ✅ View Channels

4. **Invite Bot:**
   - Copy the generated URL and open it in your browser
   - Select your Discord server and authorize the bot
   - The bot should now appear in your server's member list

## 🔍 Part 3: Get Channel ID

1. **Enable Developer Mode:**
   - In Discord, go to User Settings (gear icon)
   - Navigate to Advanced > Developer Mode (toggle ON)

2. **Copy Channel ID:**
   - Right-click on the channel you want to monitor
   - Select "Copy ID"
   - This is your Channel ID (a long number like `1234567890123456789`)

## ⚙️ Part 4: Configure Kiosk Clock

Set environment variables for your system, or you can update them in `config.py`:

### Linux/macOS
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export KIOSK_DISCORD_TOKEN="your_bot_token_here"
export KIOSK_DISCORD_CHANNEL_ID="your_channel_id_here"
```

### Windows
In Command Prompt:
```cmd
set KIOSK_DISCORD_TOKEN=your_bot_token_here
set KIOSK_DISCORD_CHANNEL_ID=your_channel_id_here
```

### Temporary Testing
```bash
KIOSK_DISCORD_TOKEN="your_bot_token_here" KIOSK_DISCORD_CHANNEL_ID="your_channel_id_here" python kiosk_clock_app.py
```

## 🧪 Part 5: Test the Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Discord Test Script:**
   ```bash
   python test_discord.py
   ```
   This script will:
   - ✅ Check environment variables
   - ✅ Test Discord bot connection
   - ✅ Verify message fetching
   - 📱 Show current messages from your channel

3. **Manual Test (Alternative):**
   ```bash
   python -c "from discord_manager import DiscordManager; dm = DiscordManager(); print('Discord authenticated:', dm.is_authenticated())"
   ```

4. **Start Kiosk Application:**
   ```bash
   python kiosk_clock_app.py
   ```

5. **Test Messaging:**
   - Send a test message in your Discord channel
   - It should appear on the kiosk display within 10 seconds

## 💡 Usage Tips

- 📱 The kiosk displays the **3 most recent messages** from the configured channel
- ✂️ Messages are automatically **truncated** if they're too long (100 characters max)
- 🤖 **Bot commands** (messages starting with `!`) are ignored
- 📝 Only **text messages** are supported (no images/embeds)
- 🔄 Messages **update every 10 seconds**

### Family/Group Usage Examples:
- "Dinner will be ready at 6:30 PM"
- "Running 15 minutes late from work"
- "Meeting moved to conference room B"
- "Don't forget soccer practice at 4 PM"
- "Pizza delivery arriving in 20 minutes"

## 🔒 Security Considerations

- 🔐 **Keep your bot token secure** and never share it
- 👁️ Only give the bot **minimal permissions** (read-only)
- 🔒 Consider creating a **private channel** for kiosk messages
- 📋 The bot can only read messages from **channels it has access to**
- 🚪 You can **remove the bot anytime** by kicking it from the server

## 🐛 Troubleshooting

### SSL Certificate Errors (macOS):
If you see `SSL: CERTIFICATE_VERIFY_FAILED` errors:
```bash
# Update certificates
pip install --upgrade certifi

# If still having issues, update all SSL-related packages
pip install --upgrade certifi urllib3 requests aiohttp
```

The Discord manager includes built-in SSL certificate handling for macOS systems.

### Bot not connecting:
- ✅ Check that the bot token is correct
- ✅ Verify Message Content Intent is enabled
- ✅ Make sure the bot is added to your server
- ✅ Check your internet connection

### No messages showing:
- ✅ Verify the channel ID is correct (remember to enable Developer Mode)
- ✅ Check that the bot has "View Channel" and "Read Message History" permissions
- ✅ Send a new message to test - the bot only shows messages it can see

### Authentication errors:
- ✅ Double-check your environment variables are set correctly
- ✅ Restart your terminal/shell after setting environment variables
- ✅ Try running with explicit variables: `KIOSK_DISCORD_TOKEN="..." python kiosk_clock_app.py`

### Permission denied:
- ✅ Make sure the bot has the right permissions in the channel
- ✅ Check if the channel is restricted to certain roles
- ✅ Verify the bot role has sufficient privileges

## 🔧 Advanced Configuration

You can also configure Discord settings in Python code by modifying `config.py`:

```python
user_config.discord_token = "your_bot_token_here"
user_config.discord_channel_id = "your_channel_id_here"
```

## 🆘 Support

If you encounter issues:

1. 📚 Check the [Discord Developer Documentation](https://discord.com/developers/docs)
2. 🔍 Verify your setup step by step
3. 📋 Check the kiosk application logs for detailed error messages
4. 🧪 Test the bot connection independently before running the full kiosk

---

**Happy messaging!** 🎉 