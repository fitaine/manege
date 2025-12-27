#!/bin/bash

# Settings
PI_USER="florine"
PI_HOST="192.168.2.5"
MAC_FOLDER="/Users/Tiphaine/Documents/3D/2025-06-22_PHOTOBOX/PHOTOS"  # Adjust as needed

# Create a timestamp string, e.g. 20250628_162435
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Define remote file with timestamp
PI_FILE="/home/florine/Pictures/photo_${TIMESTAMP}.jpg"

# Take photo on Pi with timestamped filename
ssh "$PI_USER@$PI_HOST" "libcamera-still -o $PI_FILE --nopreview -t 1000"

# Copy photo back to Mac with same timestamped name
scp "$PI_USER@$PI_HOST:$PI_FILE" "$MAC_FOLDER"

# Optional: delete photo on Pi after copying
# ssh "$PI_USER@$PI_HOST" "rm $PI_FILE"
