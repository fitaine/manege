# Camera Setup Guide - Raspberry Pi Camera V3

IMPORTANT: This project uses libcamera, not the old picamera library\!

---

## Why libcamera?

### The Raspberry Pi Camera Mess (Short History)

**The Old Way (DEPRECATED):**
- Raspberry Pi Camera Module 1 & 2
- Python library: picamera
- Commands: raspistill, raspivid
- Problem: Does NOT work with Camera V3 or modern Raspberry Pi OS\!

**The New Way (CURRENT):**
- Raspberry Pi Camera Module 3
- Commands: libcamera-still, libcamera-vid, libcamera-hello
- Python: Use subprocess to call libcamera commands
- This is what Manège uses\!

### Why We Chose libcamera

✅ Works with Camera Module V3 (what we have)
✅ Supported by Raspberry Pi (actively maintained)
✅ Better manual controls (focus, exposure, white balance)
✅ RAW capture support
✅ Modern and future-proof

❌ Old picamera does NOT work with Camera V3
❌ Old raspistill/raspivid are deprecated

---

## What You Need

### Hardware
- Raspberry Pi 4 or 5
- Pi Camera Module V3 (critical\!)
- Camera cable (comes with camera)

### Software
- Raspberry Pi OS Bullseye or newer (64-bit recommended)
- libcamera-apps (usually pre-installed)

---

## Installation & Setup

### 1. Enable Camera Interface

sudo raspi-config

Navigate to: Interface Options → Camera → Enable
Reboot: sudo reboot

### 2. Check Camera Detection

After reboot:

libcamera-hello --list-cameras

Expected output:
Available cameras
0 : imx708 [4608x2592]

If you see this, camera is detected\! ✅

If you see "No cameras available":
- Check camera cable connection (blue side toward camera)
- Make sure camera interface is enabled in raspi-config
- Try: sudo reboot

### 3. Install libcamera-apps (if needed)

Usually pre-installed, but if not:

sudo apt update
sudo apt install libcamera-apps

### 4. Test Camera

Quick test (shows preview for 5 seconds):
libcamera-hello --timeout 5000

Take a test photo:
libcamera-still -o test.jpg

Record test video:
libcamera-vid -t 10000 -o test.h264

If these work, you are all set\! ✅

---

## How Manège Uses libcamera

### We DO NOT use picamera

This will NOT work:
from picamera import PiCamera  # Old library - does not work\!

### We DO use subprocess + libcamera commands

This is what we do in app.py:

import subprocess

# Start video stream
subprocess.Popen([
    "libcamera-vid",
    "--width", "1280",
    "--height", "720",
    "--codec", "mjpeg",
    "--listen",
    "-o", "tcp://0.0.0.0:8888"
])

# Capture photo
subprocess.run([
    "libcamera-still",
    "-o", "photo.jpg",
    "--width", "4608",
    "--height", "2592"
])

This is exactly how app/app.py works\!

---

## Common Issues & Solutions

### "No cameras available"

Check:
1. Camera cable connected properly (blue side to camera)
2. Camera interface enabled: sudo raspi-config
3. Camera detected: libcamera-hello --list-cameras
4. Try different camera port (Pi 5 has two ports)

### "Command not found: libcamera-still"

Fix:
sudo apt update
sudo apt install libcamera-apps

### "Timeout waiting for camera"

Causes:
- Camera already in use by another process
- Camera not connected
- Cable damaged

Fix:
sudo pkill libcamera
libcamera-hello

### "I want to use the old picamera library"

You cannot\! Camera Module V3 requires libcamera. Options:
1. Use libcamera (recommended - what Manège does)
2. Downgrade to Camera Module V2 + old OS (not recommended)

### "Stream not working in browser"

Check:
1. Camera stream is running: ps aux | grep libcamera
2. Port 8888 is accessible: curl http://localhost:8888
3. Firewall not blocking port

Restart stream:
cd /home/yourusername/manege
./scripts/stop_cam.sh
./scripts/start_cam.sh

---

## Camera Module V3 Specs

Our camera:
- Model: Raspberry Pi Camera Module V3
- Sensor: Sony IMX708
- Resolution: 11.9 megapixels (4608 x 2592)
- Focus: Autofocus + manual control (this is why we use it\!)
- Field of View: 66° diagonal

Special features we use:
- Manual focus control (for product photography)
- Manual exposure (ISO + shutter speed)
- RAW capture (DNG format)
- HDR mode

Note: We removed the NoIR filter for better color accuracy.

---

## Why This Matters for Manège

Product Photography Needs:
- Manual focus: Critical for consistent focus across 360° sequence
- Manual exposure: Prevents brightness changes between photos
- High resolution: 4608x2592 = high-quality product images
- RAW capture: Professional post-processing flexibility

libcamera gives us all of this\!

---

## Important Notes

1. Do NOT mix old and new:
   - Do NOT install picamera if using libcamera
   - Do NOT try to use raspistill/raspivid commands
   - Use ONLY libcamera commands

2. Python integration:
   - We use subprocess to call libcamera commands
   - This is the recommended way
   - No Python picamera library needed

3. Camera Module versions:
   - V1 & V2: Use old picamera library (deprecated)
   - V3: MUST use libcamera (that is us\!)

---

## The Camera Learning Curve

The camera situation was painful to figure out, but now it works reliably\!

Key lessons learned:
- Raspberry Pi changed camera systems (picamera → libcamera)
- Camera V3 ONLY works with libcamera
- Using subprocess is the right approach for Python
- Manual controls require specific libcamera flags

---

Official Documentation:
- libcamera: https://libcamera.org/
- Raspberry Pi Camera: https://www.raspberrypi.com/documentation/accessories/camera.html
- libcamera-apps: https://github.com/raspberrypi/libcamera-apps

---

Questions? Check the Raspberry Pi forums or open an issue on GitHub.
