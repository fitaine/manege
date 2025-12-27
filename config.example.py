# Manège Configuration Template
# Copy this file to config.py and customize for your setup
# DO NOT commit config.py to git (it contains your network settings)

# Network Configuration
TURNTABLE_IP = "192.168.1.42"     # ESP32 turntable IP address
FLASK_HOST = "0.0.0.0"            # Flask server host (0.0.0.0 = all interfaces)
FLASK_PORT = 5000                  # Flask server port

# Storage Paths
PHOTOS_BASE_DIR = "/home/yourusername/Pictures"
STATIC_PHOTOS_DIR = "/home/yourusername/manege/app/static/photos"

# Camera Settings (defaults)
DEFAULT_FOCUS_POSITION = 5.0
DEFAULT_ISO = 100
DEFAULT_SHUTTER_SPEED = 10000

# Camera Modes
ENABLE_TURNTABLE = True            # Enable ESP32 turntable integration
