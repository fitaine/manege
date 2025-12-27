# Credits & Attribution

## Original Inspiration

**Manège** began as a development of the [twirly](https://github.com/veebch/twirly) project by [veebch](https://github.com/veebch).

### twirly - Original Project
- **Repository:** https://github.com/veebch/twirly
- **Author:** veebch
- **Concept:** ESP32-controlled turntable for product photography
- **License:** MIT License

### What We Borrowed from twirly
- ESP32 + stepper motor architecture
- Basic HTTP API concept for turntable control
- Inspiration for 360° rotation automation
- DRV8825 stepper driver approach

### What Manège Adds
Manège evolved twirly into a **complete photography solution** for artisans and craftspeople:

**Camera System:**
- Raspberry Pi Camera Module V3 integration
- Live MJPEG preview stream
- Manual focus control with preset positions
- Manual exposure (ISO + shutter speed)
- White balance sampling and adjustment
- HDR capture mode (3-exposure bracketing)
- RAW + JPEG capture options

**Software:**
- Flask-based web interface
- 360° photo sequencing automation
- 360° video recording with loop mode
- Photo management and storage
- Real-time camera preview with controls

**Hardware Enhancements:**
- Higher precision: 64,000 steps/360° (vs standard resolution)
- 1/32 microstepping for smooth motion
- Multiple speed profiles (photo, video, positioning)
- Network configuration system
- Professional wiring and power design

**Target Audience:**
- Professional and semi-professional photographers
- Artisans creating product catalogs
- Small businesses needing product photography
- Craftspeople (basketry, pottery, etc.)

## Development Philosophy

While inspired by twirly's elegant simplicity, Manège is a **separate development** aimed at a different use case:

- **twirly:** Minimalist turntable for basic 360° capture
- **Manège:** Complete photography system with professional features

This is not a fork in the technical sense, but rather a parallel development that took the core turntable concept and built a comprehensive solution around it.

## License Compatibility

Both projects use permissive open-source licenses:
- **twirly:** MIT License
- **Manège:** MIT License (software) + CERN-OHL-P-2.0 (hardware)

## Thank You

Special thanks to **veebch** for creating twirly and sharing it with the open-source community. Your project provided the perfect starting point for this development! 🙏

If you're looking for a **simple, minimalist turntable**, check out the original [twirly](https://github.com/veebch/twirly).

If you need a **complete photography system** with camera integration and advanced features, that's what Manège offers.

---

## Other Acknowledgments

### Software & Libraries
- **Flask** - Web framework (BSD License)
- **Pillow** - Image processing (HPND License)
- **libcamera** - Raspberry Pi camera interface
- **ArduinoJson** - JSON parsing for ESP32
- **AccelStepper** - Stepper motor control library

### Hardware
- **Raspberry Pi Foundation** - Pi and Camera Module
- **Espressif** - ESP32 platform
- **Community designs** - DRV8825 driver circuits

### Inspiration
- Artisan basketry photography workflows
- Professional product photography techniques
- Open-source hardware movement

---

**Manège** stands on the shoulders of giants. Thank you to everyone who contributes to open-source! 🎉
