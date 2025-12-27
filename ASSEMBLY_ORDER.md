# Assembly Order

Step-by-step build sequence for Manège automated photobox.

**Estimated time:** 4-6 hours (spread over multiple sessions recommended)

---

## Prerequisites

Before starting, ensure you have:
- All parts from BOM.md
- Basic tools (screwdriver, wire strippers, multimeter)
- Soldering iron (optional, for permanent connections)
- Computer with SD card reader
- WiFi network for testing

---

## 1. Electronics Breadboard Test

**Goal:** Verify motor control works before permanent assembly

**Steps:**

- Connect DRV8825 to ESP32 (STEP→GPIO5, DIR→GPIO2, SLP→GPIO18)
- Connect DRV8825 to motor
- Add heatsink to DRV8825 (critical!)
- Upload basic ESP32 test code
- Verify motor rotates smoothly in both directions

**Success criteria:**
- Motor rotates in both directions
- DRV8825 warm but not burning hot
- No burning smell or sparks

---

## 2. Raspberry Pi Setup

**Goal:** Get both cameras working with Pi 5

**Steps:**

- Flash Raspberry Pi OS (64-bit, Bookworm or newer)
- Enable camera interface (sudo raspi-config)
- Connect Camera HQ to CSI-0, Module V3 to CSI-1
- Test camera detection (libcamera-hello --list-cameras)
- Install dependencies (libcamera-apps, Python packages)

**Success criteria:**
- Both cameras detected
- Can capture test photos from each camera
- SSH access working
- Python dependencies installed

---

## 3. 3D Printing

**Goal:** Protect the hardware from outside

**Print Steps:**
- Manège's base
- Top with honeycomb grid
- Gear
- Ring gear
- Raspi bottom case
- Raspi top case

## 4. Mechanical Assembly

**Goal:** Build stable rotating platform

**Steps:**

- Install NEMA 17 motor mount
- Install boards and converters
- Wire and Solder (Tricky part)
- Screw the ring gear and place the gear on the NEAM's shaft.

**Success criteria:**
- Turntable rotates smoothly by hand
- No mechanical binding or wobble
- Motor securely mounted
- Belt properly tensioned

---

## 5. Software Setup

**Goal:** Get Manège code running

**Steps:**

- Clone repository: git clone https://github.com/fitaine/manege.git
- Configure config.py (TURNTABLE_IP, FLASK_HOST, paths)
- Configure ESP32 config.h (WiFi credentials, static IP)
- Upload ESP32 firmware via Arduino IDE
- Start Flask app and test web interface

**Success criteria:**
- ESP32 connects to WiFi
- Flask web interface loads
- Can see camera preview
- Turntable controls respond

---

## 6. Final Integration

**Goal:** Complete system assembly and calibration

**Steps:**

- Mount both cameras at optimal positions
- Wire power system (12V → XH-M291 → motor/LM2596 → Pi)
- Organize wiring with cable ties and heat shrink
- Calibrate turntable home position
- Test full 360° photo sequence

**Success criteria:**
- All components powered correctly
- Cameras properly focused
- Full 360° sequence works
- Photos saved correctly
- System stable during operation

---

## Troubleshooting

**Motor doesn't move:**
- Check DRV8825 connections
- Verify 12V power supply
- Check ESP32 serial output
- Ensure SLP pin is HIGH

**Camera not detected:**
- Check cable connections (blue side to camera)
- Verify camera enabled in raspi-config
- Try different CSI port

**Web interface not loading:**
- Verify Pi IP address
- Check Flask is running
- Try accessing from Pi itself

**Turntable position drift:**
- Check belt tension
- Verify microstepping settings (1/32)
- Ensure motor not skipping steps

---

## Safety Notes

**Before each session:**
- Check 12V power supply polarity
- Verify all connections secure
- Ensure workspace is clear

**During operation:**
- Don't touch rotating parts
- Monitor for overheating
- Keep liquids away from electronics

---

## Next Steps

After successful assembly:

1. Calibration: Fine-tune camera focus and rotation speed
2. Documentation: Take photos of your build, share improvements
3. Start shooting: Test with real products!

---

**Enjoy your Manège photobox!**

For issues or questions, open an issue on GitHub: https://github.com/fitaine/manege
