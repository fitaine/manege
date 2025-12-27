#!/bin/bash

# Start camera stream in background
libcamera-vid -t 0 --width 1280 --height 720 --framerate 25 --codec mjpeg --nopreview --listen -o tcp://0.0.0.0:8888 &

# Save PID if you want to stop it later
echo $! > /tmp/libcamera_vid.pid

# Start Flask app (foreground)
python3 /home/florine/manege/app/app.py
