# ESP32 Turntable Firmware

ESP32-based stepper motor controller for precision turntable rotation.

## Origins

The turntable control concept is inspired by [twirly](https://github.com/veebch/twirly) by veebch.

Manège extends this with:
- Enhanced precision (1/32 microstepping, 64,000 steps/360°)
- Multiple speed profiles for photography modes
- Loop-ready video mode
- Integration with Raspberry Pi camera

## Features

- Precision: 0.005625° per step (64,000 steps/360°)
- Microstepping: 1/32 for smooth motion
- HTTP API for WiFi control
- Multiple speed profiles (SLOW, MEDIUM, FAST, VIDEO)

## Configuration

1. Copy config.example.h to config.h
2. Edit with your WiFi credentials
3. Upload to ESP32 via Arduino IDE

## HTTP API Endpoints

- GET /status - Current position and state
- POST /left?degrees=N - Rotate left
- POST /right?degrees=N - Rotate right
- POST /home - Return to home position
- POST /photo360?count=N - Photo sequence mode
- POST /video360?duration=N - Video recording mode

## Hardware

- ESP32 DevKit
- NEMA 17 stepper motor
- DRV8825 driver
- 10:1 gear ratio

See hardware/ directory for complete documentation.

## Acknowledgments

Inspired by [twirly](https://github.com/veebch/twirly) by veebch.
