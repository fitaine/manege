╔═══════════════════════════════════════════════════════════════════════╗
║           MANÈGE - QUICK WIRING REFERENCE                 ║
╚═══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│  ESP32 → DRV8825 CONNECTIONS (STEPPER CONTROL)                      │
└─────────────────────────────────────────────────────────────────────┘

    ESP32          Wire Color         DRV8825
  ─────────       (suggestion)       ─────────
   GPIO 5    ───────[ORANGE]───────→   STEP
   GPIO 2    ───────[YELLOW]───────→   DIR
   GPIO 18   ───────[GREEN]────────→   SLP
   GPIO 23   ───────[BLUE]─────────→   RST
   GPIO 15   ───────[PURPLE]───────→   EN (LOW = motor energized)
   GPIO 4    ───────[BROWN]────────→   M0  ───┐
   GPIO 22   ───────[GRAY]─────────→   M1  ───┼──→ HIGH (1/32 step)
   GPIO 19   ───────[WHITE]────────→   M2  ───┘
   GND       ───────[BLACK]────────→   GND

┌─────────────────────────────────────────────────────────────────────┐
│  ESP32 → LED CONTROL (PHOTOBOX)                                     │
└─────────────────────────────────────────────────────────────────────┘

    ESP32          Wire Color         MOSFET (IRLZ44N)
  ─────────       (suggestion)       ─────────────────
   GPIO 25   ───────[CYAN]──────────→   Gate (G)

   GND       ───────[BLACK]────────→   Source (S) ──→ Common GND

  LED POWER PATH (Low-Side Switching):
  ─────────────────────────────────────────────────────────
   XH-M291 12V OUT+ ──→ LED Strip (+)
                           ↓
                      LED Strip (-)
                           ↓
                    MOSFET Drain (D)
                           ↓
                    MOSFET Source (S) ──→ Common GND
                           ↑
                      Gate (G) ←── GPIO 25 (PWM signal)

  Note: GPIO 25 provides PWM (0-100% duty cycle) for brightness control
        MOSFET is placed AFTER the LED strip (low-side switching)

┌─────────────────────────────────────────────────────────────────────┐
│  PHOTOBOX POWER DISTRIBUTION (USB-C PD)                             │
└─────────────────────────────────────────────────────────────────────┘

  AC Outlet → USB-C PD Charger (100W, 20V@5A)
            → 5A E-Marked USB-C Cable
            → PD Trigger (20V output)
            → 20V Main Bus (distributes to 3 paths):

  Path 1: Buck 20V→5V → Diode → ESP32 VIN (~2W)
  Path 2: Stepper Driver (20V VMOT) → NEMA 17 (~20W)
  Path 3: XH-M291 Buck 20V→12V → LED Strips via MOSFET (~50W)

  Total Power Budget: ~72W / 100W available

  CRITICAL: All grounds must be common (use ground bus bar)!
  Wire Specs: 18 AWG for power, 22 AWG for signals

┌─────────────────────────────────────────────────────────────────────┐
│  DIODE PROTECTION (USB PROGRAMMING)                                 │
└─────────────────────────────────────────────────────────────────────┘

  Purpose: Allow ESP32 programming via USB while system runs

  Configuration:
  ┌──────────────────────────────────────────┐
  │  Buck 5V ──→|── Diode ──┬──→ ESP32 VIN  │
  │           (1N5819)      │                │
  │                         │                │
  │  USB 5V (internal) ─────┘                │
  │  (already connected                      │
  │   on ESP32 dev board)                    │
  └──────────────────────────────────────────┘

  Component: 1× 1N5819 Schottky Diode (1A rated)

  Installation:
  - Diode ANODE (stripe end = cathode) → Buck 5V output
  - Diode CATHODE → ESP32 VIN pin
  - Voltage drop: ~0.3V (ESP32 receives ~4.7V, which is fine)

  How it works:
  - When USB unplugged: Buck powers ESP32 through diode
  - When USB plugged in: USB powers ESP32, diode blocks backfeed to Buck
  - No board modification needed (simple one-diode solution)

┌─────────────────────────────────────────────────────────────────────┐
│  COMMON GROUND IMPLEMENTATION                                       │
└─────────────────────────────────────────────────────────────────────┘

  Use a ground rail/bus bar for clean wiring:

  USB-C PD Charger (-)
          │
          │ (one 18 AWG wire)
          ↓
     [GROUND RAIL/BUS BAR]
     ═════════════════════
      │  │  │  │  │  │  │
      │  │  │  │  │  │  └─→ LED Strip (-)
      │  │  │  │  │  └────→ MOSFET Source
      │  │  │  │  └───────→ XH-M291 IN(-) and OUT(-)
      │  │  │  └──────────→ DRV8825 GND
      │  │  └─────────────→ ESP32 GND
      │  └────────────────→ Buck 5V OUT(-)
      └───────────────────→ PD Trigger (-)

  Implementation Options:
  - Screw terminal block (recommended)
  - Ground bus bar
  - High-quality wire nuts

  Why: Cleaner wiring, easier troubleshooting, standard practice

┌─────────────────────────────────────────────────────────────────────┐
│  CAPACITOR PLACEMENT (CRITICAL!)                                    │
└─────────────────────────────────────────────────────────────────────┘

  Simple Rule: Connect capacitor (+) to device (+), and (-) to device (-)
               Place as CLOSE as possible to each device!

  TOTAL: 4 Capacitors (not 5!)

  Capacitor 1: Motor Power (20V VMOT) - 100µF @ 50V
  ┌──────────────────────────────────────────┐
  │  20V ──┬─→ DRV8825 VMOT pin              │
  │        │                                  │
  │     [100µF]  ← Place within 1-2cm        │
  │     +    -     of DRV8825 board          │
  │        │                                  │
  │  GND ──┴─→ DRV8825 GND pin               │
  │                                           │
  │  Connect capacitor (-) to DRV8825 GND    │
  │  pin directly, NOT to ground bus!        │
  └──────────────────────────────────────────┘

  Capacitor 2: Logic Power (5V) - 100µF @ 25V
  ┌──────────────────────────────────────────┐
  │  5V  ──┬─→ Buck OUT(+)                   │
  │        │                                  │
  │     [100µF]  ← Place at Buck             │
  │     +    -     converter output          │
  │        │                                  │
  │  GND ──┴─→ Buck OUT(-)                   │
  └──────────────────────────────────────────┘

  Capacitor 3: XH-M291 Input (20V) - 100µF @ 50V [OPTIONAL]
  ┌──────────────────────────────────────────┐
  │  20V ──┬─→ XH-M291 IN(+)                 │
  │        │                                  │
  │     [100µF]  50V rated                   │
  │     +    -   (OPTIONAL but recommended)  │
  │        │                                  │
  │  GND ──┴─→ XH-M291 IN(-)                 │
  └──────────────────────────────────────────┘

  Capacitor 4: XH-M291 Output (12V) - 220µF @ 25V [CRITICAL!]
  ┌──────────────────────────────────────────┐
  │  12V ──┬─→ XH-M291 OUT(+)                │
  │        │   (before LED strip)            │
  │     [220µF]  25V rated                   │
  │     +    -   PREVENTS LED FLICKER!       │
  │        │                                  │
  │  GND ──┴─→ XH-M291 OUT(-)                │
  └──────────────────────────────────────────┘

  BILL OF MATERIALS - Capacitors:
  ─────────────────────────────────────────────────────────
  □ 2× 100µF electrolytic @ 50V (for 20V circuits)
  □ 1× 100µF electrolytic @ 25V (for 5V circuit)
  □ 1× 220µF electrolytic @ 25V (for 12V LED output)

  Voltage Rating Guide:
  - 20V circuits → use 50V rated (1.5× safety margin minimum)
  - 12V circuits → use 25V rated
  - 5V circuits  → use 25V rated (overkill but fine)

  Polarity: Longer leg = (+), Stripe/shorter leg = (-)

  IMPORTANT:
  - Place capacitors as close as possible to each device!
  - Connect capacitor legs to device pins, NOT directly to bus bar
  - This minimizes loop area for best noise filtering

┌─────────────────────────────────────────────────────────────────────┐
│  STEPPER MOTOR CONNECTIONS                                          │
└─────────────────────────────────────────────────────────────────────┘

  Stepper Motor (NEMA 17)            DRV8825
  ───────────────────────            ─────────
   Coil A - Wire 1 (Red)    ───────→   A1
   Coil A - Wire 2 (Green)  ───────→   A2

   Coil B - Wire 1 (Blue)   ───────→   B1
   Coil B - Wire 2 (Yellow) ───────→   B2

  IMPORTANT: NEMA 17 has NO separate ground wire!

  - Motor has only 4 coil wires
  - Motor ground reference comes through DRV8825 GND pin
  - Motor coils are isolated windings (no direct ground connection)
  - Optional: Ground metal motor case for EMI shielding (not required)

  Note: Wire colors may vary by manufacturer.
        Use multimeter to identify coil pairs (continuity test).

┌─────────────────────────────────────────────────────────────────────┐
│  VOLTAGE SETTINGS                                                   │
└─────────────────────────────────────────────────────────────────────┘

  Component              Voltage       Notes
  ─────────────────────────────────────────────────────────────
  ESP32                  5V            From Buck via diode (~4.7V at VIN)
  DRV8825 Logic (VDD)    5V            From Buck converter
  DRV8825 Motor (VMOT)   20V           Direct from PD Trigger
  NEMA 17 (typical)      12-20V        Check motor datasheet
  XH-M291 Input          20V           From PD Trigger
  XH-M291 Output         12V           Adjust to exactly 12.0V
  LED Strips             12V           COB strips, ~50W total

┌─────────────────────────────────────────────────────────────────────┐
│  NETWORK CONFIGURATION                                              │
└─────────────────────────────────────────────────────────────────────┘

  Device              IP Address         Port    Protocol
  ───────────────────────────────────────────────────────────
  Raspberry Pi        192.168.1.100      5000    HTTP (Flask)
  ESP32 Turntable     192.168.1.42       80      HTTP (WebServer)

  WiFi SSID:     YourWiFiName
  WiFi Password: YourWiFiPassword

┌─────────────────────────────────────────────────────────────────────┐
│  GPIO PIN SUMMARY                                                   │
└─────────────────────────────────────────────────────────────────────┘

  Stepper Control:
  ────────────────────────────────────────────────────────────
   GPIO 5   → STEP     GPIO 15  → EN (LOW = motor energized)
   GPIO 2   → DIR      GPIO 4   → M0
   GPIO 18  → SLP      GPIO 22  → M1
   GPIO 23  → RST      GPIO 19  → M2

  LED Control:
  ────────────────────────────────────────────────────────────
   GPIO 25  → MOSFET Gate (PWM for brightness, low-side switch)

  Available GPIOs for future use:
  ────────────────────────────────────────────────────────────
   GPIO 12, 13, 14, 16, 17, 21, 26, 27, 32, 33

┌─────────────────────────────────────────────────────────────────────┐
│  TESTING CHECKLIST                                                  │
└─────────────────────────────────────────────────────────────────────┘

  Turntable System:
  ─────────────────────────────────────────────────────────────
  □ 1. Power off everything
  □ 2. Install 1N5819 diode between Buck 5V and ESP32 VIN
  □ 3. Install 100µF@50V cap on 20V VMOT (at DRV8825 pins)
  □ 4. Install 100µF@25V cap on 5V Buck output
  □ 5. Set up ground bus bar (screw terminal block)
  □ 6. Connect all grounds to ground bus bar
  □ 7. Connect ESP32 to DRV8825 (8 control signals)
  □ 8. Connect 20V power to DRV8825 VMOT
  □ 9. Connect 5V power to DRV8825 VDD
  □ 10. Connect stepper motor 4 wires to DRV8825 (A1, A2, B1, B2)
  □ 11. Set M0, M1, M2 to HIGH (1/32 microstepping)
  □ 12. Upload firmware to ESP32 (via USB)
  □ 13. Open Serial Monitor, verify WiFi connection
  □ 14. Test via browser: http://192.168.1.42/status
  □ 15. Test rotation: /rotate_degrees?degrees=45
  □ 16. Test Flask integration from Manège UI

  LED System:
  ─────────────────────────────────────────────────────────────
  □ 1. Install 100µF@50V cap on XH-M291 input (20V) [OPTIONAL]
  □ 2. Install 220µF@25V cap on XH-M291 output (12V) [CRITICAL]
  □ 3. Connect XH-M291 input to 20V main bus
  □ 4. Adjust XH-M291 output to exactly 12.0V (use multimeter)
  □ 5. Connect GPIO 25 to MOSFET Gate
  □ 6. Connect 12V from XH-M291 to LED Strip (+)
  □ 7. Connect LED Strip (-) to MOSFET Drain
  □ 8. Connect MOSFET Source to ground bus bar
  □ 9. Test with 1 LED strip first
  □ 10. Test PWM control: /led?brightness=50
  □ 11. Add remaining LED strips gradually
  □ 12. Verify total current < 3A
  □ 13. Check for LED flicker (if present, check cap #4)

┌─────────────────────────────────────────────────────────────────────┐
│  TROUBLESHOOTING - NO MOVEMENT                                      │
└─────────────────────────────────────────────────────────────────────┘

  Check:
  ✓ VMOT voltage present (use multimeter, should be 20V)
  ✓ VDD voltage present (should be 5V)
  ✓ EN pin is LOW (motor enabled, GPIO 15 = LOW)
  ✓ Ground bus bar properly connected
  ✓ Motor coils connected correctly (all 4 wires, no 5th ground wire)
  ✓ ESP32 sending signals (check Serial Monitor)
  ✓ WiFi connected (ESP32 shows IP address)
  ✓ Capacitors installed correctly (polarity!)

┌─────────────────────────────────────────────────────────────────────┐
│  TROUBLESHOOTING - ERRATIC MOVEMENT                                 │
└─────────────────────────────────────────────────────────────────────┘

  Fix:
  ✓ Check capacitor placement (within 1-2cm of DRV8825)
  ✓ Verify capacitor polarity (+ to +, - to -)
  ✓ Check capacitor connections (to device pins, not bus)
  ✓ Check wire connections (loose wires)
  ✓ Verify power supply current rating (≥2A)
  ✓ Reduce speed in firmware (SPEED_FAST = 500)
  ✓ Check motor current limit pot on DRV8825

┌─────────────────────────────────────────────────────────────────────┐
│  TROUBLESHOOTING - LEDs NOT WORKING / FLICKERING                    │
└─────────────────────────────────────────────────────────────────────┘

  Check:
  ✓ XH-M291 output is 12.0V (measure with multimeter)
  ✓ 220µF capacitor installed on 12V output (CRITICAL!)
  ✓ Capacitor polarity correct (+ to 12V, - to GND)
  ✓ MOSFET is logic-level (IRLZ44N works with 3.3V)
  ✓ GPIO 25 PWM signal present (use /led?brightness=255)
  ✓ LED wiring: 12V → LED(+), LED(-) → MOSFET Drain
  ✓ MOSFET Source connected to ground bus bar
  ✓ Total current < 3A (XH-M291 max)
  ✓ All grounds are common (check ground bus)
  ✓ Check LED strip connections (loose wires)

  LED Flicker Causes:
  ✓ Missing 220µF output capacitor (most common!)
  ✓ Capacitor too far from XH-M291 (place within 2cm)
  ✓ Insufficient capacitance (use 220µF minimum)
  ✓ Wrong MOSFET wiring (LED strip must come BEFORE MOSFET)
  ✓ PWM frequency too low (firmware uses 5kHz, should be OK)

┌─────────────────────────────────────────────────────────────────────┐
│  CURRENT LIMIT ADJUSTMENT (DRV8825)                                 │
└─────────────────────────────────────────────────────────────────────┘

  Most NEMA 17: ~1.2A per phase

  DRV8825 formula: VREF = Current_Limit × 0.8

  For 1.2A motor: VREF = 1.2 × 0.8 = 0.96V

  Steps:
  1. Power off system
  2. Set multimeter to DC voltage
  3. Connect black probe to GND
  4. Connect red probe to potentiometer center (metal part)
  5. Power on (without motor connected)
  6. Measure voltage (should read ~0.96V for 1.2A)
  7. Adjust potentiometer with small screwdriver
     - Clockwise = increase current
     - Counter-clockwise = decrease current
  8. Power off, connect motor, test

  Safety: Start with lower current (0.8A = 0.64V) and increase if needed

═══════════════════════════════════════════════════════════════════════

  References:
  - Twirly project: github.com/veebch/twirly
  - MANÈGE project: github.com/fitaine/manege

  For detailed instructions, see:
  /home/florine/manege/hardware/MANEGE_TURNTABLE_README.md

═══════════════════════════════════════════════════════════════════════
