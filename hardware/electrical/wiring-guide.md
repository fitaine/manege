╔═══════════════════════════════════════════════════════════════════════╗
║           MANÈGE - QUICK WIRING REFERENCE                 ║
╚═══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│  ESP32 → DRV8825 CONNECTIONS                                        │
└─────────────────────────────────────────────────────────────────────┘

    ESP32          Wire Color         DRV8825
  ─────────       (suggestion)       ─────────
   GPIO 5    ───────[ORANGE]───────→   STEP
   GPIO 2    ───────[YELLOW]───────→   DIR
   GPIO 18   ───────[GREEN]────────→   SLP
   GPIO 23   ───────[BLUE]─────────→   RST
   GPIO 15   ───────[PURPLE]───────→   EN
   GPIO 4    ───────[BROWN]────────→   M0  ───┐
   GPIO 22   ───────[GRAY]─────────→   M1  ───┼──→ GND (full step)
   GPIO 19   ───────[WHITE]────────→   M2  ───┘
   GND       ───────[BLACK]────────→   GND

┌─────────────────────────────────────────────────────────────────────┐
│  POWER SUPPLY CONNECTIONS                                           │
└─────────────────────────────────────────────────────────────────────┘

  Power Supply              Step-down            DRV8825
  ────────────             Converter            ─────────
      (+)  ─────────────→  VIN (+)
                              │
                              ↓
                           [Adjust to
                           motor voltage]
                              │
                              ↓
                           VOUT (+) ─────────→  VMOT

      (-)  ─────────────→  GND (-) ──────────→  GND ←─── ESP32 GND
                                                  │
                                               [100µF]
                                                  │
                                               [10µF]

┌─────────────────────────────────────────────────────────────────────┐
│  STEPPER MOTOR CONNECTIONS                                          │
└─────────────────────────────────────────────────────────────────────┘

  Stepper Motor (NEMA 17)            DRV8825
  ───────────────────────            ─────────
   Coil A - Wire 1 (Red)    ───────→   A1
   Coil A - Wire 2 (Green)  ───────→   A2

   Coil B - Wire 1 (Blue)   ───────→   B1
   Coil B - Wire 2 (Yellow) ───────→   B2

  Note: Wire colors may vary by manufacturer.
        Use multimeter to identify coil pairs (continuity test).

┌─────────────────────────────────────────────────────────────────────┐
│  CAPACITOR PLACEMENT (IMPORTANT!)                                   │
└─────────────────────────────────────────────────────────────────────┘

     DRV8825
  ┌───────────┐
  │   VMOT    │────┬────[100µF]────┬──→ GND
  │           │    │                │
  │           │    └────[10µF]─────┘
  │    GND    │────────────────────────→ GND
  └───────────┘

  Position capacitors as CLOSE as possible to DRV8825 board.
  Polarity: Negative leg to GND, Positive leg to VMOT

┌─────────────────────────────────────────────────────────────────────┐
│  VOLTAGE SETTINGS                                                   │
└─────────────────────────────────────────────────────────────────────┘

  Component              Voltage       Notes
  ─────────────────────────────────────────────────────────────
  ESP32                  3.3V / 5V     USB or external 5V
  DRV8825 Logic          3.3V          Powered by ESP32
  DRV8825 Motor (VMOT)   8-35V         Set via step-down
  NEMA 17 (typical)      12V           Check motor datasheet
  Step-down output       12V           Adjust pot for motor

┌─────────────────────────────────────────────────────────────────────┐
│  NETWORK CONFIGURATION                                              │
└─────────────────────────────────────────────────────────────────────┘

  Device              IP Address         Port    Protocol
  ───────────────────────────────────────────────────────────
  Raspberry Pi        <PI_IP_ADDRESS>        5000    HTTP (Flask)
  ESP32 Turntable     <ESP32_IP_ADDRESS>       80      HTTP (WebServer)

  WiFi SSID:     YourWiFiName
  WiFi Password: YourWiFiPassword

┌─────────────────────────────────────────────────────────────────────┐
│  TESTING CHECKLIST                                                  │
└─────────────────────────────────────────────────────────────────────┘

  □ 1. Power off everything
  □ 2. Connect ESP32 to DRV8825 (control signals)
  □ 3. Connect step-down converter to power supply
  □ 4. Adjust step-down output voltage (use multimeter)
  □ 5. Connect step-down output to DRV8825 VMOT
  □ 6. Add capacitors between VMOT and GND
  □ 7. Connect common ground (ESP32, DRV8825, step-down)
  □ 8. Connect stepper motor to DRV8825 (A1, A2, B1, B2)
  □ 9. Set M0, M1, M2 to GND (full step mode)
  □ 10. Upload firmware to ESP32 (via USB)
  □ 11. Open Serial Monitor, verify WiFi connection
  □ 12. Test via browser: http://<ESP32_IP_ADDRESS>
  □ 13. Test rotation: /preset/45
  □ 14. Test Flask integration from photobox UI

┌─────────────────────────────────────────────────────────────────────┐
│  TROUBLESHOOTING - NO MOVEMENT                                      │
└─────────────────────────────────────────────────────────────────────┘

  Check:
  ✓ VMOT voltage present (use multimeter)
  ✓ EN pin is LOW (motor enabled)
  ✓ Common ground connected
  ✓ Motor coils connected correctly
  ✓ ESP32 sending signals (check Serial Monitor)
  ✓ WiFi connected (ESP32 shows IP address)

┌─────────────────────────────────────────────────────────────────────┐
│  TROUBLESHOOTING - ERRATIC MOVEMENT                                 │
└─────────────────────────────────────────────────────────────────────┘

  Fix:
  ✓ Add/reposition capacitors (close to DRV8825)
  ✓ Check wire connections (loose wires)
  ✓ Verify power supply current rating (≥1A)
  ✓ Reduce speed in firmware (SPEED_FAST = 500)
  ✓ Check motor current limit pot on DRV8825

┌─────────────────────────────────────────────────────────────────────┐
│  CURRENT LIMIT ADJUSTMENT (DRV8825)                                 │
└─────────────────────────────────────────────────────────────────────┘

  Most NEMA 17: ~1.2A per phase

  Formula: Vref = Current × 2
  Example: 1.2A → Vref = 2.4V (but DRV8825 uses different formula)

  DRV8825 formula: Vref = Current × 8 × Rsense
  Rsense (typical) = 0.1Ω

  For 1.2A: Vref = 1.2 × 8 × 0.1 = 0.96V

  Use multimeter on pot (center) to GND while adjusting.

═══════════════════════════════════════════════════════════════════════

  For detailed instructions, see:
  /home/yourusername/Documents/TURNTABLE_SETUP.md

═══════════════════════════════════════════════════════════════════════
