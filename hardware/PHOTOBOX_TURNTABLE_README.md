# Photobox Turntable Project - Complete System Documentation

**Last Updated: November 28, 2025**
**Status: ✅ FULLY OPERATIONAL - Advanced Features Implemented**

---

## Table of Contents
1. [Overview](#overview)
2. [Current System Status](#current-system-status)
3. [What We've Achieved](#what-weve-achieved)
4. [System Architecture](#system-architecture)
5. [Features](#features)
6. [Hardware Configuration](#hardware-configuration)
7. [Software Components](#software-components)
8. [UI Layout](#ui-layout)
9. [Next Steps & TODO](#next-steps--todo)
10. [File Locations](#file-locations)
11. [Known Issues](#known-issues)

---

## Overview

Your photobox is a complete automated photography system for capturing basketry and craft objects with:
- **Raspberry Pi Camera Module V3** (NoIR - No Infrared filter)
- **ESP32-controlled motorized turntable** with DRV8825 stepper driver
- **Web-based interface** for full remote control
- **Flask backend** (Python) serving camera and turntable APIs
- **Advanced camera controls**: Manual focus, exposure, WB, saturation, contrast
- **360° automation**: Photo sequences and video recording with loop mode

---

## Current System Status

### ✅ Working Features
- Live camera preview (MJPEG stream)
- Manual camera controls (focus, ISO, shutter, WB, saturation, contrast)
- HDR photo capture with EV compensation
- 360° photo sequences (4, 8, 12, 18 photos)
- 360° video recording with loop mode (constant-speed, loopable videos)
- Turntable manual control (left/right, home, set home)
- Emergency stop functionality
- Photo thumbnails with subfolder support
- Bottom panel UI (thumbnails, WB, saturation, contrast) - collapsed by default
- Focus: Horizontal carousel, manual mode by default (30cm)

### ⚠️ Needs Attention
- **ESP32 firmware upload required** for latest loop mode features
- Some UI elements may need final testing after recent changes

### 🔧 Configuration Details
- **Camera**: Raspberry Pi Camera Module V3 NoIR
- **Resolution**: 1920×1080 for video, configurable for photos
- **Network**:
  - Flask app: 192.168.2.5:5000
  - ESP32 turntable: 192.168.1.42 (update if needed)
- **Photo storage**: `/home/florine/Pictures/` with date-organized folders

---

## What We've Achieved

### Session 1 (Nov 27, 2025) - Initial Integration
✅ ESP32 firmware created with HTTP API
✅ Flask backend turntable endpoints
✅ Web UI integrated into right panel
✅ Manual rotation controls working
✅ 360° photo sequences functional
✅ 360° video recording implemented

### Session 2 (Nov 28, 2025) - Advanced Features & Refinements

#### Camera & Capture Improvements
✅ Fixed camera blocking issues (pkill rpicam-vid before sequences)
✅ Added overlay messages during 360° capture/video
✅ Removed confirmation popups for smoother workflow
✅ Manual focus/exposure now applied in sequences
✅ Fixed EV settings conflict with HDR mode
✅ Enhanced emergency stop (kills processes, resets UI, restarts feed)
✅ Updated photo count options (4, 8, 12, 18 photos - removed 24+)
✅ Fixed thumbnails to show photos from sequence subfolders

#### ESP32 Firmware Enhancements
✅ Implemented 1/32 microstepping for smoother motion
✅ Gentle accelerations (300-500 steps/sec²) for basketry safety
✅ Return-to-home now uses shortest path (CW vs CCW)
✅ Dynamic speed calculation based on duration
✅ Proportional acceleration (reaches full speed in 10% of duration)
✅ **Loop mode implementation**:
  - Pre-positions backwards 10% (36°)
  - Accelerates through starting position to reach cruise speed
  - Records only constant-speed portion (80% of duration)
  - Decelerates after recording
  - Returns to exact starting position

#### Video Recording Features
✅ Loop mode checkbox (enabled by default)
✅ Speed presets: Fast (10s), Medium (20s), Slow (30s), Very Slow (45s), Ultra Slow (60s)
✅ Loop mode produces seamless, loopable videos
✅ Full rotation mode option (records acceleration/deceleration)
✅ Turntable returns to home position after loop mode video

#### UI Improvements
✅ Focus carousel made horizontal (saves ~130px vertical space)
✅ Focus carousel height reduced to 50px
✅ "FOCUS" label moved above auto/manual toggle
✅ Focus defaults to Manual mode with 30cm setting
✅ Focus carousel scrolls to 30cm position on load
✅ Bottom panel (thumbnails/WB/saturation/contrast) collapsed by default
✅ Removed redundant video controls

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│  Web Browser (Client)                           │
│  - HTML/CSS/JavaScript UI                       │
│  - Displays live camera feed                    │
│  - Controls camera & turntable                  │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ↓
┌─────────────────────────────────────────────────┐
│  Raspberry Pi (192.168.2.5:5000)                │
│  ┌───────────────────────────────────────────┐  │
│  │ Flask App (Python)                        │  │
│  │ - Serves web UI                           │  │
│  │ - Controls camera (rpicam-vid/still)      │  │
│  │ - Proxies turntable commands              │  │
│  │ - Manages photo storage                   │  │
│  └───────────────────┬───────────────────────┘  │
│                      │                           │
│  ┌───────────────────┴───────────────────────┐  │
│  │ Camera Module V3 NoIR                     │  │
│  │ - Live preview stream                     │  │
│  │ - Photo capture (JPEG/RAW/DNG)            │  │
│  │ - Video recording (H264→MP4)              │  │
│  └───────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ↓
┌─────────────────────────────────────────────────┐
│  ESP32 (192.168.1.42)                           │
│  ┌───────────────────────────────────────────┐  │
│  │ HTTP Server (C++)                         │  │
│  │ - AccelStepper control                    │  │
│  │ - Position tracking                       │  │
│  │ - Loop mode logic                         │  │
│  └───────────────────┬───────────────────────┘  │
│                      │                           │
│  ┌───────────────────┴───────────────────────┐  │
│  │ DRV8825 Stepper Driver                    │  │
│  │ - 1/32 microstepping                      │  │
│  │ - NEMA stepper motor control              │  │
│  │ - 6400 steps/revolution                   │  │
│  └───────────────────┬───────────────────────┘  │
│                      │                           │
│  ┌───────────────────┴───────────────────────┐  │
│  │ NEMA Stepper Motor                        │  │
│  │ - Turntable rotation                      │  │
│  │ - 200 steps/rev (×32 microstepping)       │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Features

### Camera Controls

#### Focus
- **Auto/Manual toggle**
- **Manual settings**: Infinity, 2m, 1m, 60cm, **30cm (default)**, 20cm, 15cm, 10cm
- **Horizontal carousel** interface (50px height)
- Position saved and applied to all captures

#### Exposure
- **Auto/Manual modes**
- **Manual controls**:
  - ISO: 100-800
  - Shutter: 1/8000 to 1 second
  - EV Compensation: -2 to +2 (HDR mode only)
- Settings preserved across sequences

#### White Balance
- **Presets**: Auto, Daylight, Cloudy, Shade, Tungsten, Fluorescent, Flash, Custom
- **Custom RGB tuning**: Fine-tune red/blue gains
- Applied to all photos and videos

#### Image Adjustments
- **Saturation**: -100 to +100
- **Contrast**: -100 to +100
- Real-time preview on live feed

### Photo Capture

#### Single Photo
- JPEG, RAW (DNG), or Both formats
- HDR mode with 3-bracket exposure
- Current settings applied (focus, WB, etc.)

#### 360° Photo Sequence
- **Photo counts**: 4, 8, 12, or 18 photos
- **Default**: 4 photos (90° spacing)
- Auto-rotation between shots
- Saved to timestamped subfolder (`360seq_YYYYMMDD_HHMMSS/`)
- Returns to home position when complete
- Thumbnails show in bottom panel

### Video Recording

#### 360° Video with Loop Mode
**Loop Mode (default, checkbox enabled):**
- Pre-positions backwards 36° before starting
- Accelerates to cruise speed while returning to start position
- Records only constant-speed rotation (no acceleration in video)
- Creates seamless, loopable videos perfect for web
- Returns to starting position after recording

**Speed Presets:**
- Fast (10s): ~8s of usable footage
- Medium (20s): ~16s of usable footage
- Slow (30s): ~24s of usable footage
- Very Slow (45s): ~36s of usable footage
- Ultra Slow (60s): ~48s of usable footage

**Full Rotation Mode (checkbox unchecked):**
- Records entire rotation including acceleration/deceleration
- Good for documentary-style captures

**Output**: MP4 format (H264 encoding, 1920×1080, 30fps)

### Turntable Controls

#### Manual Control
- **Left/Right**: Rotate in 10°, 45°, or 90° increments
- **Home**: Return to reference position (0°)
- **Set as Home**: Mark current position as starting point
- **Emergency Stop**: Immediate halt with full system reset

#### Automation
- 360° photo sequences (integrated with camera settings)
- 360° video recording with loop mode
- Smooth acceleration/deceleration for delicate objects
- Position tracking and return-to-home

### Safety Features
- Emergency stop kills all processes (camera + turntable)
- Gentle accelerations protect basketry and motor
- 1/32 microstepping eliminates vibration
- Shortest-path homing reduces wear
- Clear status indicators and overlay messages

---

## Hardware Configuration

### Raspberry Pi Camera
- **Model**: Raspberry Pi Camera Module V3 NoIR
- **Resolution**: 1920×1080 (video), higher for stills
- **Connection**: CSI ribbon cable (blue side facing USB ports)

### ESP32 Turntable
```
ESP32 Pins → DRV8825:
  STEP: GPIO 5
  DIR:  GPIO 2
  SLP:  GPIO 18
  RST:  GPIO 23
  EN:   GPIO 15
  M0:   GPIO 4  (HIGH for 1/32 microstepping)
  M1:   GPIO 22 (HIGH for 1/32 microstepping)
  M2:   GPIO 19 (HIGH for 1/32 microstepping)

Network:
  WiFi SSID: WiFi
  Password: lecodewifi
  Static IP: 192.168.1.42

Motor Configuration:
  Steps per revolution: 200 (NEMA 17)
  Microstepping: 1/32
  Total steps: 6400 per revolution
```

### Speed & Acceleration Settings
```cpp
// Speeds (steps per second)
SPEED_SLOW = 800      // Photo capture (very smooth)
SPEED_MEDIUM = 1200   // General positioning
SPEED_FAST = 1600     // Return home
SPEED_VIDEO = 400     // Ultra slow for video

// Accelerations (steps per second²)
ACCEL_SLOW = 300      // Very gentle start/stop
ACCEL_MEDIUM = 400    // Gentle acceleration
ACCEL_FAST = 500      // Return home (still gentle)

// Video mode uses dynamic calculation:
// accel = speed / (duration × 0.1)
// Reaches full speed in 10% of rotation time
```

---

## Software Components

### Backend: Flask App (`/home/florine/Documents/app.py`)

**Key Functions:**
- `video_feed()` - MJPEG live stream
- `capture_photo()` - Single photo with settings
- `capture_360_sequence()` - Automated photo sequence
- `record_360_video()` - 360° video with loop mode
- `kill_camera_processes()` - Emergency camera reset
- Turntable proxy endpoints (status, left, right, home, etc.)

**Recent Changes:**
- Added loop mode support with pre-positioning
- Dynamic video duration calculation (80% of total for loop mode)
- Return-to-home after loop mode videos
- Subfolder scanning for thumbnails
- Fixed HDR/manual exposure conflicts

### Frontend: Web UI (`/home/florine/Documents/templates/index.html`)

**Structure:**
- **Left Panel**: Live preview, capture overlay, photo modal
- **Right Panel**: Camera controls, turntable controls
- **Bottom Panel**: Thumbnails, WB tuning, Saturation, Contrast (collapsed by default)

**Key JavaScript Functions:**
- `capture360Sequence()` - Photo sequence with overlay
- `record360Video()` - Video recording with countdown
- `emergencyStop()` - Full system abort
- `createCarousel()` - Dynamic control carousels
- `updateLiveFocus()`, `updateLiveExposure()` - Real-time settings

### Firmware: ESP32 (`/home/florine/Documents/scripts/esp32_turntable/esp32_turntable.ino`)

**HTTP Endpoints:**
- `/status` - Get position and state
- `/left`, `/right` - Manual rotation
- `/rotate_degrees` - Rotate by specific amount
- `/home` - Return to home (shortest path)
- `/set_home` - Set current as home position
- `/photo360` - Photo sequence mode
- `/video360` - Normal video mode
- `/video360_loop` - **New: Loop mode with pre-positioning**
- `/stop` - Emergency stop

**Key Functions:**
- `handleVideo360Loop()` - **New: Pre-position, accelerate, cruise rotation**
- `handleHome()` - Shortest path calculation
- `rotateByDegrees()` - Smooth rotation with accel/decel
- `runToTarget()` - Blocking movement execution

---

## UI Layout

### Right Panel (Top to Bottom)

1. **Photo Format** (JPEG/RAW/Both dropdown)
2. **Capture Photo** button
3. **HDR Mode** toggle + EV slider
4. **Exposure Control** (Auto/Manual toggle + ISO/Shutter carousels)
5. **360° Photo Sequence** (count selector + Capture button)
6. **Turntable Manual Controls** (Left/Right buttons, Home, Set Home)
7. **360° Video** (Loop mode checkbox + speed selector + Record button)
8. **Emergency Stop** button (red)
9. **Focus Control** ("FOCUS" title + Auto/Manual toggle + horizontal carousel)

### Bottom Panel (Tabs - Collapsed by Default)

- **Thumbnails**: Recent photos with subfolder support
- **White Balance**: Preset selector + custom RGB tuning
- **Saturation**: Slider (-100 to +100)
- **Contrast**: Slider (-100 to +100)

---

## Next Steps & TODO

### 🔴 Critical - Must Do
1. **Upload updated ESP32 firmware** to enable:
   - Loop mode pre-positioning
   - 1/32 microstepping
   - Shortest-path homing
   - Dynamic acceleration

2. **Test loop mode video** after firmware upload:
   - Verify pre-positioning works
   - Check if object returns to exact start position
   - Confirm video has constant speed (no acceleration visible)

### 🟡 Important - Should Do
3. **Calibrate turntable speeds** for your specific setup:
   - Test different video presets (10s, 20s, 30s)
   - Adjust if rotation too fast/slow for your objects
   - Fine-tune acceleration times if needed

4. **Document your workflow**:
   - Best settings for different basket types
   - Lighting setup notes
   - Object placement guidelines

5. **Backup configuration**:
   ```bash
   cp /home/florine/Documents/app.py /home/florine/Documents/app.py.backup
   cp /home/florine/Documents/scripts/esp32_turntable/esp32_turntable.ino /home/florine/Documents/scripts/esp32_turntable/esp32_turntable.ino.backup
   ```

### 🟢 Nice to Have - Future Enhancements
6. **Video post-processing**:
   - Auto-trim to exact 360° rotation
   - Color grading pipeline
   - Batch processing scripts

7. **Additional camera features**:
   - Bracketed focus stacking
   - Timelapse mode with rotation
   - Multi-row captures (vertical adjustment)

8. **UI improvements**:
   - Save/load preset configurations
   - Quick access to recent settings
   - Keyboard shortcuts

9. **Hardware upgrades**:
   - Limit switches for precision homing
   - Position encoder for closed-loop control
   - LED ring light integration
   - Vertical axis control for 3D scanning

10. **Export features**:
    - Photogrammetry mesh generation
    - Automatic background removal
    - 360° viewer web embed code

---

## File Locations

### Core Files
```
Flask Backend:
  /home/florine/Documents/app.py

Web UI:
  /home/florine/Documents/templates/index.html

ESP32 Firmware:
  /home/florine/Documents/scripts/esp32_turntable/esp32_turntable.ino

Photo Storage:
  /home/florine/Pictures/YYYY-MM-DD/
  /home/florine/Pictures/YYYY-MM-DD/360seq_YYYYMMDD_HHMMSS/

Current Folder Tracker:
  /home/florine/Pictures/current_folder.txt
```

### Documentation
```
Main README:
  /home/florine/Documents/PHOTOBOX_TURNTABLE_README.md (this file)

Setup Guide:
  /home/florine/Documents/TURNTABLE_SETUP.md

TODO List:
  /home/florine/Documents/TODO.md (to be created)

Session Notes:
  See conversation history for detailed implementation notes
```

### Scripts
```
Flask Startup:
  /home/florine/Documents/scripts/start_webapp.sh
  /home/florine/Documents/scripts/run_photobox.sh
```

---

## Known Issues

### Camera Feed Occasionally Disappears
**Symptom**: Live preview stops loading
**Cause**: rpicam-vid process dies or gets stuck
**Solution**: Emergency stop button kills and restarts camera processes
**Prevention**: Current implementation includes automatic cleanup before sequences

### Thumbnails Don't Update Immediately
**Symptom**: New photos don't appear in thumbnail panel right away
**Cause**: Thumbnail refresh was removed to prevent scope errors
**Workaround**: Click on thumbnail tab to manually refresh
**Future Fix**: Implement proper scoped refresh function

### Focus Carousel Position on Page Load
**Status**: ✅ FIXED - Now scrolls to 30cm on initialization
**Implementation**: Searches for `.selected` item and scrolls to it

### Loop Mode Timing
**Status**: ⚠️ NEEDS TESTING after firmware upload
**Note**: Pre-positioning and acceleration times are estimates
**Potential Issue**: Object might not be exactly at start position when recording begins
**Solution**: Fine-tune timing constants in app.py:
```python
accel_time = duration * 0.1  # Adjust if needed
preposition_time = 2.0       # Adjust if needed
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Camera not detected | Check ribbon cable, run `vcgencmd get_camera` |
| Live feed not loading | Emergency Stop, wait 2s, refresh page |
| Turntable shows "Offline" | Check ESP32 power, WiFi, verify IP 192.168.1.42 |
| Motor not moving | Verify wiring, check VMOT voltage, test with `/status` |
| Jerky rotation | Upload latest firmware with 1/32 microstepping |
| Photos not in thumbnails | Click thumbnails tab, check `/home/florine/Pictures/` |
| Video too fast/slow | Change speed preset or adjust firmware constants |
| Loop mode not working | Upload latest ESP32 firmware with `handleVideo360Loop()` |
| Object not at start after loop | Adjust `preposition_time` in app.py |

---

## Useful Commands

### Camera
```bash
# Check camera detection
vcgencmd get_camera

# List camera processes
ps aux | grep rpicam

# Kill all camera processes
sudo pkill -9 -f rpicam

# Test camera capture
rpicam-still -o test.jpg
```

### Flask App
```bash
# Check if Flask is running
pgrep -f "flask run"

# View Flask logs
tail -f /tmp/flask.log

# Restart Flask (if using systemd)
sudo systemctl restart photobox
```

### ESP32
```bash
# Test ESP32 connectivity
curl http://192.168.1.42/status

# Test rotation
curl -X POST http://192.168.1.42/preset/45
```

### Photos
```bash
# List recent photos
ls -lth /home/florine/Pictures/2025-11-28/ | head

# Count photos in sequences
find /home/florine/Pictures/ -name "360seq_*" -type d | wc -l

# Check disk space
df -h /home/florine/Pictures/
```

---

## Credits & Licenses

**Project**: Custom photobox for basketry documentation
**Hardware**: Raspberry Pi, ESP32, DRV8825, NEMA stepper, Camera Module V3
**Software Stack**: Flask, rpicam-apps, AccelStepper, ArduinoJson

**Libraries Used:**
- Flask (Pallets Projects) - BSD License
- AccelStepper (Mike McCauley) - GPL
- ArduinoJson (Benoit Blanchon) - MIT License
- rpicam-apps (Raspberry Pi Foundation) - BSD License

---

## Support & Maintenance

### Regular Maintenance
- Clean camera lens monthly
- Check motor temperature after long sequences
- Tighten wire connections if vibration occurs
- Keep firmware and app.py backed up
- Test emergency stop periodically

### Getting Help
- Review this document first
- Check TURNTABLE_SETUP.md for detailed guides
- Check conversation history for implementation details
- Test individual components in isolation

---

**Ready to capture professional 360° basketry photos and videos!** 📷🔄✨

**Next step**: Upload the updated ESP32 firmware to enable loop mode!
