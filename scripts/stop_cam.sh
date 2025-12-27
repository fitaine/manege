#!/bin/bash

PID_FILE="/tmp/libcamera_stream.pid"

echo "[INFO] Stopping Flask app..."
pkill -f "python3 app.py"

if [ -f "$PID_FILE" ]; then
    echo "[INFO] Stopping camera stream..."
    kill "$(cat $PID_FILE)" && rm "$PID_FILE"
else
    echo "[WARN] No PID file found for camera stream."
fi
