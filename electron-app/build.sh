#!/bin/bash
# Thyme Kiosk Clock - Build Script
# Builds distributable packages for Linux and macOS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Thyme Kiosk Clock - Build Script           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install --cache /tmp/npm-cache
    echo ""
fi

# Parse command line arguments
PLATFORM=""
FORMAT=""

show_help() {
    echo "Usage: ./build.sh [options]"
    echo ""
    echo "Options:"
    echo "  --linux              Build for Linux (all formats)"
    echo "  --linux-appimage     Build Linux AppImage only"
    echo "  --linux-deb          Build Linux Deb package only"
    echo "  --linux-rpm          Build Linux RPM package only"
    echo "  --mac                Build for macOS (all formats)"
    echo "  --mac-dmg            Build macOS DMG only"
    echo "  --mac-zip            Build macOS ZIP only"
    echo "  --all                Build for all platforms"
    echo "  --clean              Clean build artifacts"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./build.sh --linux             # Build all Linux formats"
    echo "  ./build.sh --linux-appimage    # Build AppImage only"
    echo "  ./build.sh --mac               # Build all macOS formats"
    echo "  ./build.sh --all               # Build everything"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --linux)
            PLATFORM="linux"
            shift
            ;;
        --linux-appimage)
            PLATFORM="linux"
            FORMAT="appimage"
            shift
            ;;
        --linux-deb)
            PLATFORM="linux"
            FORMAT="deb"
            shift
            ;;
        --linux-rpm)
            PLATFORM="linux"
            FORMAT="rpm"
            shift
            ;;
        --mac)
            PLATFORM="mac"
            shift
            ;;
        --mac-dmg)
            PLATFORM="mac"
            FORMAT="dmg"
            shift
            ;;
        --mac-zip)
            PLATFORM="mac"
            FORMAT="zip"
            shift
            ;;
        --all)
            PLATFORM="all"
            shift
            ;;
        --clean)
            echo -e "${YELLOW}Cleaning build artifacts...${NC}"
            npm run clean
            echo -e "${GREEN}✓ Clean complete${NC}"
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# If no arguments, show help
if [ -z "$PLATFORM" ]; then
    show_help
    exit 0
fi

echo -e "${BLUE}Building Thyme Kiosk Clock...${NC}"
echo ""

# Function to build
build() {
    local cmd=$1
    local name=$2
    
    echo -e "${YELLOW}Building $name...${NC}"
    if npm run $cmd; then
        echo -e "${GREEN}✓ $name built successfully${NC}"
        echo ""
    else
        echo -e "${RED}✗ $name build failed${NC}"
        exit 1
    fi
}

# Build based on platform
case "$PLATFORM" in
    linux)
        if [ -n "$FORMAT" ]; then
            case "$FORMAT" in
                appimage)
                    build "build:linux:appimage" "Linux AppImage"
                    ;;
                deb)
                    build "build:linux:deb" "Linux Deb Package"
                    ;;
                rpm)
                    build "build:linux:rpm" "Linux RPM Package"
                    ;;
            esac
        else
            build "build:linux" "All Linux Packages"
        fi
        ;;
    mac)
        if [ -n "$FORMAT" ]; then
            case "$FORMAT" in
                dmg)
                    build "build:mac:dmg" "macOS DMG"
                    ;;
                zip)
                    build "build:mac:zip" "macOS ZIP"
                    ;;
            esac
        else
            build "build:mac" "All macOS Packages"
        fi
        ;;
    all)
        build "build:all" "All Platforms"
        ;;
esac

echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Build Complete!                             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Output directory:${NC} dist/"
echo ""
echo "Built files:"
ls -lh dist/ | grep -E "\.(AppImage|deb|rpm|dmg|zip)$" || echo "  (checking dist/ directory...)"
echo ""
echo -e "${YELLOW}Installation instructions:${NC}"
echo "  Linux AppImage: chmod +x *.AppImage && ./Thyme-Kiosk-Clock-*.AppImage"
echo "  Linux Deb:      sudo dpkg -i thyme-kiosk-clock_*.deb"
echo "  Linux RPM:      sudo rpm -i thyme-kiosk-clock-*.rpm"
echo "  macOS DMG:      Open the DMG and drag to Applications"
echo "  macOS ZIP:      Extract and move .app to Applications"
echo ""

