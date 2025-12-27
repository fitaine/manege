#!/bin/bash

# Start libcamera-vid in background, listening on TCP port
libcamera-vid -t 0 --width 1280 --height 720 --framerate 25 \
    --codec mjpeg --nopreview --listen -o tcp://127.0.0.1:8888 &

# Save the PID so we can stop it later if needed
echo $! > /tmp/libcamera_stream.pid
