#!/bin/bash
# Thyme Kiosk Clock Startup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Thyme Kiosk Clock - Electron      ║${NC}"
echo -e "${BLUE}║           Starting...                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}Dependencies not installed!${NC}"
    echo -e "${GREEN}Running npm install...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Check if config file exists
if [ ! -f "config/alarm_config.json" ]; then
    echo -e "${BLUE}Creating default configuration...${NC}"
    mkdir -p config
    cat > config/alarm_config.json << 'EOF'
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
  "displayOffTime": "",
  "displayOnTime": "",
  "alarms": [],
  "clockFontSize": 120,
  "dateFontSize": 36,
  "alarmsFontSize": 24,
  "eventsFontSize": 32,
  "weatherFontSize": 28,
  "eventsRefreshInterval": 10000,
  "weatherUpdateInterval": 3600000,
  "discordUpdateInterval": 10000,
  "backgroundChangeInterval": 30000
}
EOF
fi

# Start the application
echo -e "${GREEN}Starting Thyme Kiosk Clock...${NC}"
echo ""

# Check if --dev flag is passed
if [ "$1" == "--dev" ]; then
    npm run dev
else
    npm start
fi

