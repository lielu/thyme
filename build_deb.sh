#!/bin/bash
# Build script for creating Debian packages

set -e

echo "Building Thyme Debian package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf debian/thyme
rm -f ../thyme_*.deb ../thyme_*.dsc ../thyme_*.tar.xz ../thyme_*.changes ../thyme_*.buildinfo

# Install build dependencies
echo "Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y devscripts build-essential debhelper dh-python python3-all python3-setuptools

# Build the package
echo "Building package..."
debuild -us -uc -b

echo "Build completed!"
echo "Package files created in parent directory:"
ls -la ../thyme_*.deb

echo ""
echo "To install the package:"
echo "  sudo dpkg -i ../thyme_*.deb"
echo "  sudo apt-get install -f  # Fix any dependency issues"
echo ""
echo "To test the package:"
echo "  sudo dpkg -i ../thyme_*.deb"
echo "  thyme --help" 