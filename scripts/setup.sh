#!/bin/bash
# Manège - First-Time Setup Script

set -e  # Exit on error

echo ""
echo "🎠 Manège - Automated Photography System Setup"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -d "/boot" ]; then
    echo "⚠️  Warning: This doesn't look like a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for config.py
if [ ! -f "config.py" ]; then
    echo "📝 Creating config.py from template..."
    cp config.example.py config.py
    echo ""
    echo "⚠️  IMPORTANT: You must edit config.py with your settings!"
    echo ""
    echo "Required settings:"
    echo "  - TURNTABLE_IP: Your ESP32 IP address"
    echo "  - FLASK_HOST: This Raspberry Pi's IP address"
    echo "  - PHOTOS_BASE_DIR: Where to save photos"
    echo ""
    echo "Run: nano config.py"
    echo ""
    read -p "Press Enter to open config.py in nano now, or Ctrl+C to exit..."
    nano config.py
fi

echo ""
echo "✅ config.py exists"

# Create required directories
echo "📁 Creating photo directories..."
mkdir -p ~/Pictures
mkdir -p app/static/photos

# Check for system dependencies
echo ""
echo "🔍 Checking system dependencies..."

if ! command -v libcamera-hello &> /dev/null; then
    echo "❌ libcamera-apps not found"
    echo ""
    echo "Install with:"
    echo "  sudo apt update"
    echo "  sudo apt install libcamera-apps"
    echo ""
    exit 1
fi
echo "✅ libcamera-apps installed"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 installed"

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found"
    echo ""
    echo "Install with:"
    echo "  sudo apt install python3-pip"
    echo ""
    exit 1
fi
echo "✅ pip3 installed"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Test camera
echo ""
echo "📷 Testing camera..."
if libcamera-hello --list-cameras &> /dev/null; then
    echo "✅ Camera detected"
else
    echo "⚠️  Camera not detected"
    echo "Make sure:"
    echo "  1. Camera is connected"
    echo "  2. Camera interface is enabled (raspi-config)"
    echo "  3. Raspberry Pi is rebooted after enabling camera"
fi

# Test ESP32 connection
echo ""
echo "🔌 Testing ESP32 turntable connection..."
source config.py 2>/dev/null || true
TURNTABLE_IP=$(python3 -c "from config import TURNTABLE_IP; print(TURNTABLE_IP)" 2>/dev/null || echo "192.168.1.42")

if curl -s --max-time 3 "http://${TURNTABLE_IP}/status" > /dev/null 2>&1; then
    echo "✅ ESP32 turntable responding at ${TURNTABLE_IP}"
else
    echo "⚠️  Cannot reach ESP32 at ${TURNTABLE_IP}"
    echo "Make sure:"
    echo "  1. ESP32 is powered on"
    echo "  2. ESP32 firmware is uploaded with correct WiFi credentials"
    echo "  3. ESP32 IP address in config.py matches your setup"
fi

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Review your config.py settings"
echo "2. Upload ESP32 firmware (firmware/esp32_turntable/)"
echo "3. Start the application:"
echo "     ./scripts/start_webapp.sh"
echo ""
echo "4. Access the web interface:"
echo "     http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "For help, see: README.md"
echo ""
