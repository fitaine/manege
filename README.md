# Manège 🎠
## Professional 360° Photography for Makers & Artisans

> **Transform your workshop into a professional product photography studio with a single cable.**

Manège is the complete open-source photography system that serious makers and artisans have been waiting for. Capture stunning 360° views of your work, stream live to clients, and automatically publish to your online gallery - all controlled from your phone or computer.

---

## ✨ Why Manège?

**You're a craftsperson, not a photographer.** Your time should be spent creating, not fighting with complicated photography setups. Manège gives you professional-quality product photos with zero hassle.

### The Complete Package

- 🎥 **Dual Camera System** - Raspberry Pi 5 with dual camera support for simultaneous HQ capture + continuous live streaming
- 🔌 **True One-Cable Solution** - PoE HAT powers everything: Pi, cameras, LED lighting, and turntable from a single Ethernet cable
- 💡 **Integrated LED Control** - Built-in power management for your LED light strips - one power source for the entire system
- 🌀 **Professional Turntable** - 8-inch lazy susan supports large objects with precision rotation (64,000 steps per revolution!)
- 🌬️ **Honeygrid Ventilation** - Smart thermal design keeps your Pi cool during long shooting sessions
- 🌐 **WordPress Auto-Upload** - Your photos automatically appear in your online gallery as you shoot
- 📱 **Lightweight Web App** - Control everything from any device - fast, responsive, and functional

---

## 🎯 What Can You Do?

### For Product Catalogues
Photograph your entire inventory systematically. The WordPress integration creates a beautiful grid wall gallery where customers can browse your complete catalogue instantly.

### For Client Presentations
Live stream your work-in-progress directly to clients. Get real-time feedback before shipping.

### For Online Sales
Generate professional 360° product views and interactive spins that boost conversion rates.

### For Documentation
Build a visual archive of everything you create with automatic organization and tagging.

---

## 🚀 Key Features

### Camera & Capture
- **Dual Camera Architecture** - Stream live while capturing high-resolution stills
- **Manual Controls** - Precise focus, exposure, and white balance adjustment
- **HDR Mode** - Perfect for challenging lighting conditions
- **360° Sequences** - Automated multi-angle capture with configurable step count
- **Video Recording** - Create smooth rotating product videos

### Hardware Excellence
- **8-inch Turntable** - Handles everything from jewelry to furniture
- **Ultra-Precise Motion** - 0.005625° per step for silky-smooth rotation
- **PoE Powered** - Just plug in one Ethernet cable - power + network in one
- **Integrated LED Power** - Dedicated power rail for your lighting setup
- **Passive Cooling** - Honeygrid vents keep the system running cool and silent

### Software & Workflow
- **WordPress Integration** - Auto-upload to your website gallery as you shoot
- **Grid Wall View** - Customers see your entire catalogue at a glance
- **Web-Based Control** - Access from any device on your network
- **Fast & Responsive** - Lightweight interface that works on phones, tablets, and computers
- **Open Source** - Customize everything to match your workflow

---

## 🛠️ Perfect For

- **Woodworkers** - Showcase custom furniture and turning projects
- **Ceramicists** - Capture the full beauty of your pottery
- **Jewelers** - Professional shots that highlight intricate details
- **Leatherworkers** - Show every angle of bags, wallets, and accessories
- **Sculptors** - Document your work from every perspective
- **Vintage Dealers** - Photograph inventory fast with consistent quality
- **Any Maker** - If you create physical products, Manège is for you

---

## 📦 What You Need

### Essential Hardware
- Raspberry Pi 5 (4GB+ recommended)
- 2x Camera Module 3 (or Camera Module 3 Wide)
- PoE+ HAT for Raspberry Pi 5
- ESP32 development board
- NEMA 17 stepper motor + A4988 driver
- 8-inch lazy susan bearing
- Power supply for LED strip (if using integrated lighting)

### Optional But Recommended
- LED light strips for consistent product lighting
- Enclosure with honeygrid ventilation (STL files included)
- Ethernet switch with PoE+ support

**Full BOM with suppliers: [BOM.md](BOM.md)**

---

## 🎬 Quick Start

### 1. Get Your Hardware Ready
Follow the [Assembly Guide](ASSEMBLY_ORDER.md) to build your Manège. The PoE HAT simplifies everything - just connect Ethernet and you're powered up.

### 2. Configure Software
```bash
cd manege
cp config.example.py config.py
nano config.py  # Set your WordPress credentials and preferences
pip3 install -r requirements.txt
```

### 3. Flash ESP32 Firmware
Upload the turntable controller firmware from `firmware/esp32_turntable/`

### 4. Launch the Web App
```bash
./scripts/start_webapp.sh
```

Access from any device: `http://<your-pi-ip>:5000`

### 5. Start Shooting!
Take a test shot, verify the WordPress upload, and start building your catalogue.

**Detailed setup: [Full Documentation](hardware/README.md)**

---

## 🌐 WordPress Integration

Manège automatically uploads your photos as you shoot them, building a beautiful online gallery:

- **Automatic Upload** - Every capture instantly appears in your WordPress media library
- **Gallery Grid View** - Your catalogue displays as an organized image wall
- **No Manual Transfers** - Set it up once, never touch it again
- **Custom Organization** - Tag and categorize as you shoot

Perfect for artisans who want to keep their online store updated without the hassle.

---

## 💪 Built for Real Work

This isn't a hobbyist toy - Manège is designed for daily professional use:

- **Reliable PoE Power** - No battery anxiety, no power adapter tangles
- **Thermal Management** - Honeygrid vents prevent overheating during marathon photo sessions
- **Large Capacity** - 8-inch turntable handles serious work, not just trinkets
- **Fast Operation** - Lightweight web interface responds instantly
- **Production Ready** - Shoot dozens or hundreds of products without slowing down

---

## 🏗️ Build or Buy?

**Want to Build It Yourself?**
Everything you need is here:
- Complete bill of materials with part numbers
- Step-by-step assembly guide
- 3D printable files for custom enclosure
- Full source code and schematics

**Want a Ready-Made Solution?**
*Coming Soon* - Pre-assembled kits and fully assembled units for makers who want to skip straight to shooting.

---

## 📚 Documentation

- [Bill of Materials](BOM.md) - Complete parts list with links
- [Assembly Guide](ASSEMBLY_ORDER.md) - Step-by-step build instructions
- [Camera Setup](app/CAMERA_SETUP.md) - Raspberry Pi camera configuration
- [Git Quick Guide](GIT_QUICK_GUIDE.md) - Contribute to the project
- [Credits](CREDITS.md) - Standing on the shoulders of giants

---

## 🤝 Community & Support

Built by makers, for makers in the Jura mountains of France.

- **Website**: [tiphainebuccino.com](https://tiphainebuccino.com)
- **Issues & Features**: [GitHub Issues](https://github.com/yourusername/manege/issues)
- **Contributions Welcome**: See [Contributing Guidelines](CONTRIBUTING.md)

---

## 📜 License

- **Software**: MIT License - Use it, modify it, sell products photographed with it
- **Hardware**: CERN-OHL-P-2.0 - Open source hardware for everyone

---

## 🙏 Credits

Manège began as an evolution of [twirly](https://github.com/veebch/twirly) by veebch. We took their elegant ESP32 turntable concept and built a complete photography system around it.

**Original concept**: ESP32-based turntable by veebch
**Manège additions**: Raspberry Pi camera integration, dual camera support, PoE power, LED integration, WordPress auto-upload, web interface, and production-ready hardware design.

Huge thanks to veebch for the inspiration! 🎉

---

## 🎨 Start Creating

Your craftsmanship deserves professional presentation. Whether you're selling on Etsy, building a portfolio, or documenting your workshop's output - Manège gives you studio-quality results without the studio.

**One cable. Professional results. Open source freedom.**

Ready to showcase your work the way it deserves? Start building your Manège today.

---

*Made with ❤️ in Jura, France*
