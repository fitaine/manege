# Manège - Automated 360° Photography System

Open-source automated photography system combining Raspberry Pi camera with ESP32-controlled turntable.

## Quick Start

1. Configure: `cp config.example.py config.py && nano config.py`
2. Install: `pip3 install -r requirements.txt`
3. Upload ESP32 firmware (see firmware/esp32_turntable/)
4. Run: `./scripts/start_webapp.sh`
5. Access: http://<pi-ip>:5000

## Features

- 360° photo sequences & videos
- Manual focus/exposure/white balance
- HDR capture mode
- Precision turntable (0.005625°/step)

## Structure

- app/ - Flask web application
- firmware/ - ESP32 code
- hardware/ - Wiring, docs, 3D files
- scripts/ - Startup scripts

## Configuration

Edit `config.py`:
- TURNTABLE_IP - ESP32 address
- FLASK_HOST - Pi address  
- PHOTOS_BASE_DIR - Photo location

**Never commit config.py or firmware/config.h\!**

## License

Software: MIT | Hardware: CERN-OHL-P-2.0

Built in Jura, France | https://tiphainebuccino.com

---

## 🙏 Acknowledgments

This project began as an evolution of [twirly](https://github.com/veebch/twirly) by veebch - a minimalist ESP32-based turntable. Manège extends the concept into a complete photography solution for artisans and craftspeople, adding:

- Raspberry Pi camera integration with manual controls
- Web-based interface for remote operation
- 360° photo sequencing and video recording
- HDR capture and advanced camera features
- Professional-grade precision (64,000 steps/360°)

Thank you to veebch for the original inspiration and ESP32 turntable foundation! 🎉

---


## 📷 Camera Setup

**IMPORTANT:** This project uses **libcamera** (not the old picamera library!).

Camera Module V3 requires libcamera commands. The old picamera/raspistill/raspivid will NOT work.

See [app/CAMERA_SETUP.md](app/CAMERA_SETUP.md) for:
- Why we use libcamera
- Installation and testing
- Common issues and solutions
- How Manège uses the camera

