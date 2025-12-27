#!/bin/bash

# Settings
PI_USER="youruser"
PI_HOST="<PI_IP_ADDRESS>"
MAC_FOLDER="/path/to/your/photos"  # Adjust as needed

# Create a timestamp string, e.g. 20250628_162435
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Define remote file with timestamp
PI_FILE="/home/yourusername/Pictures/photo_${TIMESTAMP}.jpg"

# Take photo on Pi with timestamped filename
ssh "$PI_USER@$PI_HOST" "libcamera-still -o $PI_FILE --nopreview -t 1000"

# Copy photo back to Mac with same timestamped name
scp "$PI_USER@$PI_HOST:$PI_FILE" "$MAC_FOLDER"

# Optional: delete photo on Pi after copying
# ssh "$PI_USER@$PI_HOST" "rm $PI_FILE"
