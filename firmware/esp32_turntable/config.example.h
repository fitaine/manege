// Manège - ESP32 Turntable Firmware
// WiFi Configuration Template
// Copy this file to config.h and customize for your network
// DO NOT commit config.h to git (it contains your WiFi password)

#ifndef CONFIG_H
#define CONFIG_H

// WiFi Settings
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"

// Static IP Configuration
#define STATIC_IP 192,168,1,42      // ESP32 IP address (comma-separated)
#define GATEWAY 192,168,1,1         // Your router/gateway IP
#define SUBNET 255,255,255,0        // Subnet mask
#define DNS 8,8,8,8                 // DNS server (Google DNS)

// HTTP Server Settings
#define HTTP_PORT 80

#endif // CONFIG_H
