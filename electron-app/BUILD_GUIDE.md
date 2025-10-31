# Build & Package Guide

Complete guide for building and packaging Thyme Kiosk Clock for distribution.

## 🎯 Quick Start

### Build Everything

```bash
./build.sh --all
```

### Build for Specific Platform

```bash
# Linux
./build.sh --linux

# macOS
./build.sh --mac
```

### Install Built Package

```bash
# Linux
./install-linux.sh

# macOS
./install-mac.sh
```

---

## 📦 Build Scripts Reference

### Main Build Script: `build.sh`

Comprehensive build script with multiple options:

```bash
./build.sh [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--linux` | Build all Linux formats (AppImage, Deb, RPM) |
| `--linux-appimage` | Build Linux AppImage only |
| `--linux-deb` | Build Debian package only |
| `--linux-rpm` | Build RPM package only |
| `--mac` | Build all macOS formats (DMG, ZIP) |
| `--mac-dmg` | Build macOS DMG only |
| `--mac-zip` | Build macOS ZIP only |
| `--all` | Build for all platforms |
| `--clean` | Clean build artifacts |
| `-h, --help` | Show help message |

**Examples:**

```bash
# Build AppImage for Linux
./build.sh --linux-appimage

# Build DMG for macOS
./build.sh --mac-dmg

# Build everything
./build.sh --all

# Clean build files
./build.sh --clean
```

---

## 🐧 Linux Build Options

### AppImage

**What it is:** Self-contained executable that runs on any Linux distribution

```bash
# Build
./build.sh --linux-appimage

# Or using npm
npm run build:linux:appimage
```

**Output:** `dist/Thyme-Kiosk-Clock-2.0.0.AppImage`

**Architectures:** x64, arm64, armv7l (Raspberry Pi)

**Installation:**
```bash
chmod +x Thyme-Kiosk-Clock-2.0.0.AppImage
./Thyme-Kiosk-Clock-2.0.0.AppImage
```

### Debian Package (.deb)

**What it is:** Package for Debian/Ubuntu-based systems

```bash
# Build
./build.sh --linux-deb

# Or using npm
npm run build:linux:deb
```

**Output:** `dist/thyme-kiosk-clock_2.0.0_amd64.deb`

**Architectures:** x64, arm64, armv7l

**Installation:**
```bash
sudo dpkg -i thyme-kiosk-clock_2.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

**Includes:**
- Desktop entry
- Application menu integration
- System dependencies (alsa-utils, etc.)

### RPM Package (.rpm)

**What it is:** Package for RedHat/Fedora-based systems

```bash
# Build
./build.sh --linux-rpm

# Or using npm
npm run build:linux:rpm
```

**Output:** `dist/thyme-kiosk-clock-2.0.0.x86_64.rpm`

**Architectures:** x64, arm64

**Installation:**
```bash
sudo rpm -i thyme-kiosk-clock-2.0.0.x86_64.rpm
```

---

## 🍎 macOS Build Options

### DMG Installer

**What it is:** Drag-and-drop installer with Applications shortcut

```bash
# Build
./build.sh --mac-dmg

# Or using npm
npm run build:mac:dmg
```

**Output:** `dist/Thyme-Kiosk-Clock-2.0.0.dmg`

**Architectures:** x64 (Intel), arm64 (Apple Silicon)

**Installation:**
1. Open the DMG
2. Drag app to Applications folder
3. Eject DMG

### ZIP Archive

**What it is:** Compressed .app bundle

```bash
# Build
./build.sh --mac-zip

# Or using npm
npm run build:mac:zip
```

**Output:** `dist/Thyme-Kiosk-Clock-2.0.0-mac.zip`

**Architectures:** x64, arm64

**Installation:**
1. Extract ZIP
2. Move .app to Applications folder

---

## 🛠️ NPM Scripts Reference

All available npm scripts for building:

```json
{
  "start": "electron .",                    // Run app
  "dev": "electron . --dev",                // Run with DevTools
  "build": "electron-builder",              // Build current platform
  "build:linux": "...",                     // Build all Linux
  "build:linux:appimage": "...",           // Build AppImage
  "build:linux:deb": "...",                // Build Deb
  "build:linux:rpm": "...",                // Build RPM
  "build:mac": "...",                      // Build all macOS
  "build:mac:dmg": "...",                  // Build DMG
  "build:mac:zip": "...",                  // Build ZIP
  "build:all": "...",                      // Build all platforms
  "build:dir": "...",                      // Build unpacked
  "pack": "...",                           // Pack without building
  "dist": "...",                           // Build all for distribution
  "clean": "..."                           // Clean build artifacts
}
```

---

## 📁 Output Structure

After building, the `dist/` directory contains:

```
dist/
├── Thyme-Kiosk-Clock-2.0.0.AppImage           # Linux AppImage
├── thyme-kiosk-clock_2.0.0_amd64.deb          # Linux Deb
├── thyme-kiosk-clock-2.0.0.x86_64.rpm         # Linux RPM
├── Thyme-Kiosk-Clock-2.0.0.dmg                # macOS DMG
├── Thyme-Kiosk-Clock-2.0.0-mac.zip            # macOS ZIP
├── linux-unpacked/                             # Unpacked Linux
├── mac/                                        # Unpacked macOS
│   └── Thyme Kiosk Clock.app
└── builder-effective-config.yaml               # Build config used
```

---

## 🔧 Build Configuration

### package.json Build Section

The build configuration is in `package.json` under the `"build"` key:

```json
{
  "build": {
    "appId": "com.lielu.thyme",
    "productName": "Thyme Kiosk Clock",
    "files": [...],
    "linux": {...},
    "mac": {...}
  }
}
```

### Customization

Edit `package.json` to customize:

- **App name:** `productName`
- **Bundle ID:** `appId`
- **Included files:** `files` array
- **Dependencies:** `linux.deb.depends`, etc.
- **Desktop entry:** `linux.desktop`

---

## 🎨 Icons & Assets

### Required Icons

**Linux:**
- `assets/icons/icon.png` (512x512 recommended)

**macOS:**
- `assets/icons/icon.icns` (Mac icon bundle)

### Creating Icons

**From PNG to ICNS (macOS):**
```bash
# Install iconutil (comes with Xcode)
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
# Need to copy PNG files with resolutions to the icons folder as per https://github.com/nklayman/vue-cli-plugin-electron-builder/issues/1243
cp icon.iconset/* .
```

---

## 🚀 Distribution Workflow

### 1. Prepare for Build

```bash
# Ensure dependencies are installed
npm install --cache /tmp/npm-cache

# Clean previous builds
./build.sh --clean
```

### 2. Build Packages

```bash
# Build for all platforms
./build.sh --all

# Or build individually
./build.sh --linux
./build.sh --mac
```

### 3. Test Built Packages

**Linux:**
```bash
# Test AppImage
chmod +x dist/Thyme-Kiosk-Clock-*.AppImage
./dist/Thyme-Kiosk-Clock-*.AppImage

# Test Deb
sudo dpkg -i dist/thyme-kiosk-clock_*.deb
```

**macOS:**
```bash
# Test DMG
open dist/Thyme-Kiosk-Clock-*.dmg

# Test app directly
open "dist/mac/Thyme Kiosk Clock.app"
```

### 4. Distribute

Upload packages to:
- GitHub Releases
- Website download page
- Package managers (optional)

---

## 🍓 Raspberry Pi Specific

### Building for ARM

The build system automatically creates ARM builds:

- **armv7l:** Raspberry Pi 2, 3, 4 (32-bit)
- **arm64:** Raspberry Pi 3, 4, 5 (64-bit)

### Cross-Platform Building

**Build ARM packages on x64:**

Install dependencies:
```bash
# On Ubuntu/Debian
sudo apt-get install -y qemu-user-static
```

Then build normally:
```bash
./build.sh --linux
```

### Installing on Raspberry Pi

**Method 1: AppImage (easiest)**
```bash
chmod +x Thyme-Kiosk-Clock-*-armv7l.AppImage
./Thyme-Kiosk-Clock-*-armv7l.AppImage
```

**Method 2: Deb Package**
```bash
sudo dpkg -i thyme-kiosk-clock_*_armhf.deb
```

---

## 🔍 Troubleshooting

### Build Fails

**Issue:** npm permission errors

**Fix:**
```bash
npm install --cache /tmp/npm-cache
```

**Issue:** Missing dependencies

**Fix:**
```bash
# Linux
sudo apt-get install -y rpm

# macOS
# DMG building requires macOS

# Building Linux on macOS
brew install rpm
```

### Package Won't Install

**Linux - Missing dependencies:**
```bash
# After installing .deb
sudo apt-get install -f
```

**macOS - Security warning:**
```bash
# Remove quarantine attribute
xattr -cr "/Applications/Thyme Kiosk Clock.app"
```

### Build is Slow

**Optimize:**
```bash
# Build only what you need
./build.sh --linux-appimage  # Fastest
./build.sh --linux-deb       # Fast

# Avoid building everything
# Don't use --all unless needed
```

---

## 📊 Build Size Comparison

| Package Type | Size | Notes |
|-------------|------|-------|
| AppImage | ~150MB | Self-contained |
| Deb | ~100MB | Uses system libs |
| RPM | ~100MB | Uses system libs |
| DMG | ~140MB | macOS only |
| ZIP | ~130MB | Compressed |

---

## 🎯 Best Practices

### Version Management

1. Update version in `package.json`
2. Build all packages
3. Test on each platform
4. Tag release in git
5. Upload to releases

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build
on: [push, pull_request]
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run build
```

---

## 📝 Checklist

Before releasing:

- [ ] Update version in `package.json`
- [ ] Test app works (`npm start`)
- [ ] Build all packages
- [ ] Test each package format
- [ ] Verify icons appear correctly
- [ ] Check file sizes are reasonable
- [ ] Test on clean systems
- [ ] Update CHANGELOG.md
- [ ] Create git tag
- [ ] Upload to releases

---

## 🆘 Getting Help

- Check `npm run` output for errors
- Review `dist/builder-debug.yml` for config issues
- See [Electron Builder docs](https://www.electron.build/)
- Check system requirements for building

---

**Happy Building! 🚀**

