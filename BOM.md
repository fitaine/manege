# Bill of Materials (BOM)

Complete parts list for building Manège automated photobox.

**Source:** All parts available on AliExpress

---

## Core Electronics

| Component | Specs | Qty | Notes |
|-----------|-------|-----|-------|
| **Raspberry Pi 5** | 4GB+ RAM | 1 | Supports 2 cameras simultaneously |
| **Pi Camera HQ** | 12.3MP, C/CS mount | 1 | Main capture camera (high quality) |
| **Pi Camera Module V3** | 11.9MP, autofocus | 1 | Live preview stream |
| **Camera Cables** | 15-pin ribbon cables | 2 | One for each camera |
| **ESP32 DevKit** | WiFi enabled | 1 | Turntable controller |
| **NEMA 17 Stepper** | 200 steps/rev, 1.8° | 1 | Turntable motor |
| **DRV8825 Driver** | With heatsink | 1 | Stepper driver (1/32 microstepping) |

---

## Power System

| Component | Specs | Qty | Notes |
|-----------|-------|-----|-------|
| **XH-M291** | 12V Buck converter | 1 | 12V power distribution |
| **LM2596** | 5V Buck converter | 1 | 5V for Raspberry Pi |
| **12V Power Supply** | 2-3A minimum | 1 | Main power input |

---

## Mechanical

| Component | Specs | Qty | Notes |
|-----------|-------|-----|-------|
| **Lazy Susan** | 8 inch (200mm) | 1 | Rotating bearing platform |
| **Timing Belt & Pulleys** | 10:1 ratio (160T/16T) | 1 set | Gear reduction |
| **Mounting Hardware** | M3/M4 screws, brackets | 1 set | Assembly hardware |

---

## Wiring & Connectors

| Component | Qty | Notes |
|-----------|-----|-------|
| **Jumper Wires** | 20-30 | Male-to-female, various colors |
| **Heat Shrink Tubing** | Assortment | Cable management |
| **Breadboard** (optional) | 1 | For prototyping/testing |

---

## Optional Upgrades

| Component | Purpose | Notes |
|-----------|---------|-------|
| **LED Strips** (8x) | Product lighting | 12V COB strips |
| **IRLZ44N MOSFET** | LED PWM control | Logic-level N-channel |
| **Resistors** | 1kΩ, 10kΩ | For MOSFET circuit |
| **Enclosure Materials** | Protective housing | 3D printed or fabricated |

---

## Camera Setup - Two Camera System

### Why Two Cameras?

**Camera HQ (Main Capture):**
- High quality photos (12.3MP)
- Interchangeable C/CS lenses
- Manual focus control
- RAW capture support
- Used for: Final 360° photos, product shots

**Camera Module V3 (Live Preview):**
- Fast autofocus
- Good for live streaming
- Lower latency
- Used for: Real-time preview, composition, framing

### Raspberry Pi 5 Requirement

Pi 5 has **dual camera connectors** - allows both cameras simultaneously:
- Camera HQ on CSI-0 (main photos)
- Module V3 on CSI-1 (live preview)

Earlier Pi models (4, 3, etc.) require camera multiplexer for dual cameras.

---

## Power Distribution

```
12V Power Supply
    │
    ├──> XH-M291 (12V distribution)
    │       ├──> NEMA 17 Stepper Motor
    │       ├──> LED Strips (optional)
    │       └──> LM2596 (12V → 5V)
    │               └──> Raspberry Pi 5
    │
    └──> ESP32 (via LM2596 or dedicated 5V)
```

---

## Critical Notes

⚠️ **Raspberry Pi 5 required** for dual camera setup (or use multiplexer with Pi 4)  
⚠️ **Camera HQ needs lens** - C or CS mount (6mm or 16mm recommended)  
⚠️ **DRV8825 needs heatsink** - Gets hot during operation  
⚠️ **Power calculations** - Ensure 12V supply can handle motor + LEDs  
⚠️ **Camera cables** - Check length needed for your enclosure

---

## Assembly Order

**Recommended build sequence:**

1. **Electronics breadboard test**
   - Wire ESP32 + DRV8825 + motor
   - Test basic rotation
   - Verify power supply voltages

2. **Raspberry Pi setup**
   - Install Pi OS
   - Connect both cameras
   - Test camera detection
   - Install libcamera-apps

3. **Mechanical assembly**
   - Mount motor to base
   - Install lazy susan bearing
   - Add timing belt/pulleys
   - Test rotation smoothness

4. **Software setup**
   - Clone Manège repository
   - Configure network settings
   - Upload ESP32 firmware
   - Test web interface

5. **Final integration**
   - Mount cameras
   - Wire everything neatly
   - Add enclosure (optional)
   - Calibrate and test

---

## Where to Buy

**Primary Source:** AliExpress
- Search terms: "Raspberry Pi 5", "NEMA 17", "DRV8825", "8 inch lazy susan"
- Typical shipping: 2-4 weeks
- Buy extras: jumper wires, heat shrink, screws

**Camera-Specific:**
- Pi Camera HQ + lens: Official distributors or AliExpress
- Ensure genuine Camera Module V3 (many clones exist)

**Power Components:**
- XH-M291: Search "XH-M291 buck converter"
- LM2596: Search "LM2596 DC-DC buck"
- 12V adapter: "12V 3A power supply"

---

## What You Might Already Have

Check your parts bin for:
- Jumper wires (Arduino kits)
- Breadboard
- USB cables
- Heat shrink tubing
- Basic hand tools
- Multimeter (for testing voltages)

---

**Last Updated:** December 2025
