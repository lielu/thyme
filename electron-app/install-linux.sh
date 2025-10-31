#!/bin/bash
# Thyme Kiosk Clock - Linux Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Thyme Kiosk Clock - Linux Installer        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Detect package type
PACKAGE_FILE=""

if [ -f dist/*.AppImage ]; then
    PACKAGE_FILE=$(ls dist/*.AppImage | head -1)
    PACKAGE_TYPE="AppImage"
elif [ -f dist/*.deb ]; then
    PACKAGE_FILE=$(ls dist/*.deb | head -1)
    PACKAGE_TYPE="deb"
elif [ -f dist/*.rpm ]; then
    PACKAGE_FILE=$(ls dist/*.rpm | head -1)
    PACKAGE_TYPE="rpm"
else
    echo -e "${RED}Error: No package found in dist/ directory${NC}"
    echo "Please build the package first:"
    echo "  ./build.sh --linux"
    exit 1
fi

echo -e "${BLUE}Found package:${NC} $PACKAGE_FILE"
echo -e "${BLUE}Package type:${NC} $PACKAGE_TYPE"
echo ""

# Install based on package type
case "$PACKAGE_TYPE" in
    AppImage)
        echo -e "${YELLOW}Installing AppImage...${NC}"
        
        # Make executable
        chmod +x "$PACKAGE_FILE"
        
        # Create desktop entry
        DESKTOP_FILE="$HOME/.local/share/applications/thyme-kiosk-clock.desktop"
        mkdir -p "$HOME/.local/share/applications"
        
        APPIMAGE_PATH="$(realpath "$PACKAGE_FILE")"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Thyme Kiosk Clock
GenericName=Kiosk Clock
Comment=Digital clock with calendar and weather
Exec=$APPIMAGE_PATH
Icon=clock
Terminal=false
Type=Application
Categories=Utility;Clock;Calendar;
Keywords=clock;calendar;weather;alarm;
EOF
        
        echo -e "${GREEN}✓ AppImage installed successfully${NC}"
        echo ""
        echo "To run:"
        echo "  $APPIMAGE_PATH"
        echo ""
        echo "Or search for 'Thyme Kiosk Clock' in your application menu"
        ;;
        
    deb)
        echo -e "${YELLOW}Installing Deb package...${NC}"
        
        if ! command -v dpkg &> /dev/null; then
            echo -e "${RED}Error: dpkg not found. Are you on a Debian-based system?${NC}"
            exit 1
        fi
        
        echo "This requires sudo privileges..."
        sudo dpkg -i "$PACKAGE_FILE" || {
            echo -e "${YELLOW}Installing missing dependencies...${NC}"
            sudo apt-get install -f -y
        }
        
        echo -e "${GREEN}✓ Deb package installed successfully${NC}"
        echo ""
        echo "To run:"
        echo "  thyme-kiosk-clock"
        echo ""
        echo "Or search for 'Thyme Kiosk Clock' in your application menu"
        ;;
        
    rpm)
        echo -e "${YELLOW}Installing RPM package...${NC}"
        
        if ! command -v rpm &> /dev/null; then
            echo -e "${RED}Error: rpm not found. Are you on a RedHat-based system?${NC}"
            exit 1
        fi
        
        echo "This requires sudo privileges..."
        sudo rpm -i "$PACKAGE_FILE"
        
        echo -e "${GREEN}✓ RPM package installed successfully${NC}"
        echo ""
        echo "To run:"
        echo "  thyme-kiosk-clock"
        echo ""
        echo "Or search for 'Thyme Kiosk Clock' in your application menu"
        ;;
esac

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Config file: ~/.config/thyme-kiosk-clock/alarm_config.json"
echo "  Or use the Settings UI (press F6)"
echo ""
echo -e "${BLUE}Auto-start on boot:${NC}"
echo "  See MIGRATION_GUIDE.md for systemd service setup"
echo ""

