#!/bin/bash

cd /home/florine/Documents

# Kill old Flask server if still running
pkill -f app.py

# Start Flask app in background
nohup python3 app.py > flask.log 2>&1 &

# Wait briefly then open Chromium
sleep 1
chromium-browser --app=http://127.0.0.1:5000 &
