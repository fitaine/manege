# Bill of Materials (BOM)

Complete parts list for building Manège automated photobox.

---

## Electronics

| Component | Specs | Qty | Est. Price | Notes |
|-----------|-------|-----|------------|-------|
| **Raspberry Pi 4/5** | 4GB+ RAM recommended | 1 | €60-80 | Main controller |
| **Pi Camera Module V3** | 11.9MP, autofocus | 1 | €25-30 | Critical: V3 required |
| **Camera Cable** | 15-pin ribbon cable | 1 | €3-5 | Usually included with camera |
| **ESP32 DevKit** | WiFi enabled | 1 | €8-12 | Turntable controller |
| **NEMA 17 Stepper** | 200 steps/rev, 1.8° | 1 | €15-20 | Turntable motor |
| **DRV8825 Driver** | With heatsink | 1 | €3-5 | Stepper driver (1/32 microstepping) |
| **12V Power Supply** | 2-3A minimum | 1 | €10-15 | For motor + ESP32 |
| **5V Power Supply** | 3A (USB-C) | 1 | €10-15 | For Raspberry Pi |

**Electronics Subtotal:** ~€134-182

---

## Mechanical

| Component | Specs | Qty | Est. Price | Notes |
|-----------|-------|-----|------------|-------|
| **Turntable Platform** | Ø300mm rotating base | 1 | €20-40 | DIY or purchased |
| **Timing Belt & Pulleys** | 10:1 ratio (160T/16T) | 1 set | €15-25 | For gear reduction |
| **Bearings** | For turntable rotation | 2-4 | €5-10 | Depends on design |
| **Mounting Hardware** | Screws, brackets | 1 set | €5-10 | M3/M4 hardware |

**Mechanical Subtotal:** ~€45-85

---

## Wiring & Connectors

| Component | Qty | Est. Price | Notes |
|-----------|-----|------------|-------|
| **Jumper Wires** | 20-30 | €5-8 | Male-to-female, various colors |
| **Breadboard** (optional) | 1 | €3-5 | For prototyping |
| **Heat Shrink Tubing** | Assortment | €3-5 | Cable management |

**Wiring Subtotal:** ~€11-18

---

## Optional/Future

| Component | Purpose | Est. Price |
|-----------|---------|------------|
| **LED Strips** (8x) | Product lighting | €24-40 |
| **MOSFET (IRLZ44N)** | LED control | €0.50 |
| **Buck Converter** | 12V → 5V for ESP32 | €3-5 |
| **Enclosure** | Protective housing | €20-50 |
| **3D Printed Parts** | Custom mounts, case | €10-20 (filament) |

**Optional Subtotal:** ~€58-115

---

## Total Project Cost

| Category | Cost Range |
|----------|------------|
| **Core Electronics** | €134-182 |
| **Mechanical** | €45-85 |
| **Wiring** | €11-18 |
| **Subtotal (Minimum Working System)** | **€190-285** |
| **+ Optional (Full Featured)** | €248-400 |

---

## Where to Buy

**Electronics:**
- AliExpress (cheapest, 2-4 weeks shipping)
- Amazon (faster, slightly more expensive)
- Local electronics shops (immediate, higher prices)

**Raspberry Pi & Camera:**
- Official distributors (Farnell, RS Components, Adafruit)
- Ensure Camera Module V3 (not V1 or V2\!)

**Mechanical:**
- Timing belts: AliExpress, robotics suppliers
- Bearings: Local hardware stores, Amazon
- Turntable: DIY from wood/acrylic or purchase lazy susan bearing

---

## Critical Notes

⚠️ **Camera Module V3 is required** - V1/V2 will NOT work (different software)  
⚠️ **DRV8825 needs heatsink** - Gets hot during operation  
⚠️ **12V power must be adequate** - Minimum 2A for motor under load  
⚠️ **ESP32 needs WiFi** - Generic ESP32 DevKit works fine

---

## What You Already Have

If you have these, you can save money:
- Old 12V laptop power supply
- USB-C phone charger (5V 3A)
- Jumper wires from Arduino kits
- Breadboard for testing

---

## Recommended First Purchase

Start with essentials:
1. Raspberry Pi 4 (4GB)
2. Pi Camera Module V3
3. ESP32 DevKit
4. NEMA 17 stepper
5. DRV8825 driver

**Minimum to test:** ~€120-140

Add mechanical parts once electronics are working.

---

**Last Updated:** December 2025  
**Currency:** EUR (adjust for your region)
