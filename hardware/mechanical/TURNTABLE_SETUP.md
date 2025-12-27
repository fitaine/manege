# Manège Turntable Setup Guide

## Hardware Components
- ESP32 development board
- DRV8825 stepper motor driver
- NEMA 17 stepper motor (200 steps/rev recommended)
- Step-down converter (to match your motor's voltage)
- 2x Capacitors (100µF and 10µF)
- Jumper wires
- Power supply

## Wiring Diagram

### ESP32 to DRV8825 Connections
```
ESP32 Pin    →    DRV8825 Pin    Purpose
──────────────────────────────────────────
GPIO 5       →    STEP           Step signal
GPIO 2       →    DIR            Direction control
GPIO 18      →    SLP            Sleep mode control
GPIO 23      →    RST            Reset
GPIO 4       →    M0             Microstepping (set to GND for full step)
GPIO 22      →    M1             Microstepping (set to GND for full step)
GPIO 19      →    M2             Microstepping (set to GND for full step)
GPIO 15      →    EN             Enable (active LOW)
GND          →    GND            Common ground
```

### DRV8825 to Motor & Power
```
DRV8825 Pin       Connection
──────────────────────────────────────────
VMOT             → Step-down converter (+) output
GND              → Step-down converter (-) output & ESP32 GND
A1, A2           → Motor coil A
B1, B2           → Motor coil B
M0, M1, M2       → GND (for full step mode)
```

### Power Supply
```
Power Supply (+) → Step-down converter input (+)
Power Supply (-) → Step-down converter input (-) & Common GND

Step-down output: Adjust to match your motor voltage
  - NEMA 17 typical: 12V
  - Check your motor datasheet
```

### Capacitor Placement
```
100µF capacitor: Between VMOT and GND (close to DRV8825)
10µF capacitor:  Between VMOT and GND (additional filtering)
```

## Software Setup

### 1. Install Arduino IDE Libraries
Open Arduino IDE and install these libraries via Library Manager:
- WiFi (built-in)
- WebServer (built-in)
- AccelStepper (by Mike McCauley)
- ArduinoJson (by Benoit Blanchon)

### 2. Configure WiFi
Edit the ESP32 firmware (`esp32_turntable.ino`):
```cpp
const char* ssid = "YOUR_WIFI_SSID";        // Change to your WiFi name
const char* password = "YOUR_WIFI_PASSWORD"; // Change to your WiFi password
```

The ESP32 will use static IP: **192.168.1.42**

If you need to change the IP, edit these lines:
```cpp
IPAddress local_IP(192, 168, 1, 42);    // Change last number
IPAddress gateway(192, 168, 1, 1);      // Your router IP
IPAddress subnet(255, 255, 255, 0);
```

### 3. Upload Firmware
1. Connect ESP32 to your computer via USB
2. Open `esp32_turntable.ino` in Arduino IDE
3. Select board: **ESP32 Dev Module** (Tools → Board)
4. Select correct COM port (Tools → Port)
5. Click Upload

### 4. Verify Connection
After upload, open Serial Monitor (115200 baud):
```
Connecting to WiFi...
WiFi connected!
IP: 192.168.1.42
HTTP server started
Manège Turntable Ready!
```

### 5. Test ESP32 API
Open browser and visit: `http://192.168.1.42`

You should see the API documentation page.

Test rotation:
```
http://192.168.1.42/preset/45   (rotate 45°)
http://192.168.1.42/status      (check position)
```

### 6. Install Python Dependencies
On your Raspberry Pi:
```bash
pip3 install requests
```

### 7. Update Flask App
The turntable features are already integrated in `/home/yourusername/Documents/app.py`

Verify the ESP32 IP address matches:
```python
TURNTABLE_IP = "192.168.1.42"
TURNTABLE_ENABLED = True
```

### 8. Add UI to Web Interface
The turntable UI snippet is in `/home/yourusername/Documents/turntable_ui_snippet.html`

To add it to your Manège interface:
1. Open `/home/yourusername/Documents/templates/index.html`
2. Find a suitable location (e.g., after the camera settings section)
3. Copy the HTML section from `turntable_ui_snippet.html`
4. Copy the JavaScript section into your existing `<script>` block

## Features

### Manual Control
- **Left/Right buttons**: Rotate by 10°, 45°, or 90°
- **Home button**: Return to home position (0°)
- **Set as Home**: Define current position as 0°

### 360° Photo Sequence
Automatically captures multiple photos while rotating:
- Choose 12, 18, 24, 36, or 72 photos
- Photos saved in timestamped subfolder
- Returns to home position after completion

### 360° Video Recording
Records video while rotating smoothly:
- Choose duration: 10-60 seconds
- Camera and turntable synchronized
- Smooth rotation for professional results

### Emergency Stop
Immediately stops all turntable movement.

## API Endpoints

### Turntable Control (Flask → ESP32)
```
GET  /turntable/status              - Get position and state
POST /turntable/left?degrees=N      - Rotate left (CCW)
POST /turntable/right?degrees=N     - Rotate right (CW)
POST /turntable/goto?position=N     - Go to absolute position
POST /turntable/home                - Return to home (0°)
POST /turntable/set_home            - Set current as home
POST /turntable/stop                - Emergency stop
```

### Advanced Features
```
POST /capture_360_sequence
     Parameters: photo_count, format

POST /record_360_video
     Parameters: duration
```

## Troubleshooting

### ESP32 not connecting to WiFi
1. Check WiFi credentials in firmware
2. Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check Serial Monitor for error messages

### Motor not moving
1. Verify all wiring connections
2. Check if EN pin is LOW (motor enabled)
3. Measure voltage at VMOT (should match motor voltage)
4. Test with `/preset/45` endpoint

### Motor moving erratically
1. Check capacitor placement (close to DRV8825)
2. Verify power supply current rating (≥1A recommended)
3. Adjust AccelStepper speed/acceleration values

### Motor too slow/fast
Edit firmware speed settings:
```cpp
const int SPEED_SLOW = 300;      // Lower = slower
const int SPEED_MEDIUM = 600;
const int SPEED_FAST = 1000;
```

### Turntable offline in web interface
1. Verify ESP32 is powered and connected to WiFi
2. Check IP address: `http://192.168.1.42`
3. Verify TURNTABLE_IP in Flask app matches ESP32 IP
4. Check both devices are on same network

### Photos not synchronized with rotation
1. Increase settle time in `capture_360_sequence` function
2. Reduce rotation speed (SPEED_SLOW constant)
3. Check for vibrations in mechanical setup

## Mechanical Assembly Tips

### Turntable Platform
- Use a lazy susan bearing for smooth rotation
- Mount motor underneath platform
- Use timing belt or direct coupling to stepper shaft

### Camera Positioning
- Keep camera stationary, rotate object
- Ensure camera is centered and perpendicular to turntable
- Use diffused lighting to minimize shadows

### Object Placement
- Center object on turntable
- Mark home position on platform for repeatability
- Keep objects within weight limit of motor/platform

## Calibration

### Find Home Position
1. Manually rotate turntable to desired starting position
2. Click "Set as Home" button in UI
3. ESP32 will remember this as 0°

### Test Accuracy
1. Click "Home" button
2. Click "Preset/360" to do full rotation
3. Should return to exact same position
4. If not, check:
   - STEPS_PER_REV setting (200 for most NEMA 17)
   - Mechanical slippage (belt tension, coupling)

## Safety Notes

- **Emergency Stop**: Always accessible in UI
- **Power**: Never connect/disconnect motor while powered
- **Voltage**: Double-check motor voltage before powering
- **Current**: DRV8825 current limit should be set for your motor
- **Heat**: DRV8825 may need heatsink for continuous operation

## Next Steps / Enhancements

- Add position encoder for closed-loop control
- Add limit switches for homing
- Implement variable speed control in UI
- Add timelapse mode (photo + rotation over hours)
- Support for photogrammetry exports

## Support Files

- Firmware: `/home/yourusername/Documents/scripts/esp32_turntable.ino`
- Flask API: `/home/yourusername/Documents/app.py`
- UI Snippet: `/home/yourusername/Documents/turntable_ui_snippet.html`
- This guide: `/home/yourusername/Documents/TURNTABLE_SETUP.md`

Happy shooting! 📷🔄
