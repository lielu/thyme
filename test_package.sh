#!/bin/bash
# Test script for the Debian package

set -e

PACKAGE_FILE="../thyme_*.deb"

echo "Testing Thyme Debian package installation..."

# Check if package file exists
if ! ls $PACKAGE_FILE 1> /dev/null 2>&1; then
    echo "Error: No package file found. Run ./build_deb.sh first."
    exit 1
fi

# Create test environment
echo "Setting up test environment..."
TEST_DIR="/tmp/thyme_test"
rm -rf $TEST_DIR
mkdir -p $TEST_DIR

# Install package
echo "Installing package..."
sudo dpkg -i $PACKAGE_FILE || true
sudo apt-get install -f -y

# Test installation
echo "Testing installation..."
if command -v thyme >/dev/null 2>&1; then
    echo "✓ thyme command is available"
else
    echo "✗ thyme command not found"
    exit 1
fi

# Test service file
if [ -f /lib/systemd/system/thyme.service ]; then
    echo "✓ systemd service file installed"
else
    echo "✗ systemd service file missing"
    exit 1
fi

# Test desktop file
if [ -f /usr/share/applications/thyme.desktop ]; then
    echo "✓ desktop file installed"
else
    echo "✗ desktop file missing"
    exit 1
fi

# Test user creation
if getent passwd thyme >/dev/null; then
    echo "✓ thyme user created"
else
    echo "✗ thyme user not created"
    exit 1
fi

echo ""
echo "Package installation test completed successfully!"
echo ""
echo "To start the service:"
echo "  sudo systemctl enable thyme"
echo "  sudo systemctl start thyme"
echo ""
echo "To remove the package:"
echo "  sudo apt-get remove thyme"
echo "  sudo apt-get purge thyme  # Remove all config files" 