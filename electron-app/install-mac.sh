#!/bin/bash
# Thyme Kiosk Clock - macOS Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Thyme Kiosk Clock - macOS Installer        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Detect package type
DMG_FILE=""
ZIP_FILE=""
APP_FILE=""

if [ -f dist/*.dmg ]; then
    DMG_FILE=$(ls dist/*.dmg | head -1)
    PACKAGE_TYPE="dmg"
elif [ -f dist/mac/*.app ]; then
    APP_FILE=$(ls -d dist/mac/*.app | head -1)
    PACKAGE_TYPE="app"
elif [ -f dist/*.zip ]; then
    ZIP_FILE=$(ls dist/*.zip | head -1)
    PACKAGE_TYPE="zip"
else
    echo -e "${RED}Error: No package found in dist/ directory${NC}"
    echo "Please build the package first:"
    echo "  ./build.sh --mac"
    exit 1
fi

echo -e "${BLUE}Package type:${NC} $PACKAGE_TYPE"
echo ""

# Install based on package type
case "$PACKAGE_TYPE" in
    dmg)
        echo -e "${YELLOW}Installing from DMG...${NC}"
        echo ""
        echo "Opening DMG file..."
        open "$DMG_FILE"
        echo ""
        echo -e "${GREEN}✓ DMG opened${NC}"
        echo ""
        echo -e "${YELLOW}Please drag 'Thyme Kiosk Clock' to the Applications folder${NC}"
        echo ""
        echo "After installation, you can:"
        echo "  • Open from Applications folder"
        echo "  • Add to Dock"
        echo "  • Search in Spotlight"
        ;;
        
    app)
        echo -e "${YELLOW}Installing .app bundle...${NC}"
        
        if [ -d "/Applications/Thyme Kiosk Clock.app" ]; then
            echo -e "${YELLOW}Removing existing installation...${NC}"
            rm -rf "/Applications/Thyme Kiosk Clock.app"
        fi
        
        echo "Copying to Applications folder..."
        cp -R "$APP_FILE" "/Applications/"
        
        echo -e "${GREEN}✓ Application installed successfully${NC}"
        echo ""
        echo "To run:"
        echo "  open '/Applications/Thyme Kiosk Clock.app'"
        echo ""
        echo "Or search for 'Thyme Kiosk Clock' in Spotlight"
        ;;
        
    zip)
        echo -e "${YELLOW}Installing from ZIP...${NC}"
        
        # Create temp directory
        TEMP_DIR=$(mktemp -d)
        
        echo "Extracting ZIP file..."
        unzip -q "$ZIP_FILE" -d "$TEMP_DIR"
        
        # Find .app bundle
        APP_BUNDLE=$(find "$TEMP_DIR" -name "*.app" -type d | head -1)
        
        if [ -z "$APP_BUNDLE" ]; then
            echo -e "${RED}Error: No .app bundle found in ZIP${NC}"
            rm -rf "$TEMP_DIR"
            exit 1
        fi
        
        if [ -d "/Applications/Thyme Kiosk Clock.app" ]; then
            echo -e "${YELLOW}Removing existing installation...${NC}"
            rm -rf "/Applications/Thyme Kiosk Clock.app"
        fi
        
        echo "Copying to Applications folder..."
        cp -R "$APP_BUNDLE" "/Applications/"
        
        # Cleanup
        rm -rf "$TEMP_DIR"
        
        echo -e "${GREEN}✓ Application installed successfully${NC}"
        echo ""
        echo "To run:"
        echo "  open '/Applications/Thyme Kiosk Clock.app'"
        echo ""
        echo "Or search for 'Thyme Kiosk Clock' in Spotlight"
        ;;
esac

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Config file: ~/Library/Application Support/thyme-kiosk-clock/alarm_config.json"
echo "  Or use the Settings UI (press F6)"
echo ""
echo -e "${BLUE}First Run:${NC}"
echo "  If macOS shows a security warning:"
echo "  1. Go to System Preferences > Security & Privacy"
echo "  2. Click 'Open Anyway' for Thyme Kiosk Clock"
echo ""
echo -e "${BLUE}Auto-start on login:${NC}"
echo "  1. System Preferences > Users & Groups > Login Items"
echo "  2. Click '+' and add Thyme Kiosk Clock"
echo ""

