// Manège Turntable Control - ESP32 + DRV8825 + AccelStepper
// Enhanced version with 360° photo sequence and video support
// Based on working test code with improvements

#include <WiFi.h>
#include <WebServer.h>
#include <AccelStepper.h>
#include <ArduinoJson.h>
n// Configuration (WiFi credentials, network settings)
#include "config.h"

// === Wi-Fi Configuration ===
// WiFi credentials moved to config.h
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// === Stepper Pin Assignments ===
#define STEP_PIN 5
#define DIR_PIN 2
#define SLP_PIN 18
#define RST_PIN 23
#define M0_PIN 4
#define M1_PIN 22
#define M2_PIN 19
#define EN_PIN 15

// === Motor Configuration ===
const int STEPS_PER_REV = 200;       // 200 steps for full step mode (motor shaft)
const int MICROSTEPS = 32;           // 1/32 microstepping (M0=M1=M2=HIGH) for smooth motion
const int GEAR_RATIO = 10;           // 160 teeth ring gear / 16 teeth pinion = 10:1 reduction
const long TOTAL_STEPS = (long)STEPS_PER_REV * MICROSTEPS * GEAR_RATIO;  // 64000 steps per lazy susan revolution

// === Speed Profiles (adjusted for 1/32 microstepping + 10:1 gear ratio) ===
// Note: With 32x microstepping and 10x gear ratio, we have 320x more steps than direct full-step drive
// Speeds are in steps/second for the motor (not lazy susan rotation speed)
const int SPEED_SLOW = 800;          // For photo capture (very smooth, no vibration)
const int SPEED_MEDIUM = 1200;       // General positioning (gentle)
const int SPEED_FAST = 1600;         // Return home (smooth but faster)
const int SPEED_VIDEO = 400;         // Slow for 360° video (ultra smooth)

// === Gentle Accelerations (safe for delicate objects like basketery) ===
const int ACCEL_SLOW = 300;          // Very gentle start/stop
const int ACCEL_MEDIUM = 400;        // Gentle acceleration
const int ACCEL_FAST = 500;          // Return home acceleration (still gentle)

// === State Variables ===
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);
WebServer server(80);

volatile bool isMoving = false;
volatile bool stopRequested = false;
long homePosition = 0;               // Reference home position

// === Driver Control Functions ===
void wakeDriver() {
  digitalWrite(RST_PIN, HIGH);
  digitalWrite(SLP_PIN, HIGH);
  digitalWrite(EN_PIN, LOW);  // ENABLE LOW = enabled
}

void sleepDriver() {
  digitalWrite(SLP_PIN, LOW);
  digitalWrite(EN_PIN, HIGH); // ENABLE HIGH = disabled
}

// === Setup ===
void setup() {
  Serial.begin(115200);
  delay(1000);

  // Set motor control pins
  pinMode(SLP_PIN, OUTPUT);
  pinMode(RST_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  pinMode(M0_PIN, OUTPUT);
  pinMode(M1_PIN, OUTPUT);
  pinMode(M2_PIN, OUTPUT);

  // Set microstepping to 1/32 (M0=M1=M2=HIGH for DRV8825)
  digitalWrite(M0_PIN, HIGH);
  digitalWrite(M1_PIN, HIGH);
  digitalWrite(M2_PIN, HIGH);

  wakeDriver();
  delay(10);

  // Setup stepper motion parameters
  stepper.setMaxSpeed(SPEED_MEDIUM);
  stepper.setAcceleration(ACCEL_MEDIUM);

  // Connect to Wi-Fi with static IP
  IPAddress local_IP(192, 168, 1, 42);
  IPAddress gateway(192, 168, 1, 1);
  IPAddress subnet(255, 255, 255, 0);

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // === HTTP API Routes ===
  setupRoutes();

  server.begin();
  Serial.println("HTTP server started");
  Serial.println("Manège Turntable Ready!");
}

void setupRoutes() {
  // Root endpoint - API documentation
  server.on("/", HTTP_GET, []() {
    String html = "<html><head><title>Manège Turntable</title></head><body>";
    html += "<h1>Manège Turntable Control</h1>";
    html += "<h2>Available Endpoints:</h2>";
    html += "<ul>";
    html += "<li><b>GET /status</b> - Get current position and state</li>";
    html += "<li><b>POST /rotate?steps=N</b> - Rotate by N steps (+ = CW, - = CCW)</li>";
    html += "<li><b>POST /rotate_degrees?degrees=N</b> - Rotate by N degrees</li>";
    html += "<li><b>POST /goto?position=N</b> - Go to absolute position (0-360°)</li>";
    html += "<li><b>POST /home</b> - Return to home position (0°)</li>";
    html += "<li><b>POST /set_home</b> - Set current position as home</li>";
    html += "<li><b>POST /left?degrees=N</b> - Rotate left (CCW)</li>";
    html += "<li><b>POST /right?degrees=N</b> - Rotate right (CW)</li>";
    html += "<li><b>POST /photo360?count=N</b> - Prepare for N-photo 360° sequence</li>";
    html += "<li><b>POST /video360?duration=N</b> - Rotate 360° over N seconds</li>";
    html += "<li><b>POST /stop</b> - Emergency stop</li>";
    html += "<li><b>POST /sleep</b> - Disable motor (save power)</li>";
    html += "<li><b>POST /wake</b> - Enable motor</li>";
    html += "</ul></body></html>";
    server.send(200, "text/html", html);
  });

  // Status endpoint - returns JSON
  server.on("/status", HTTP_GET, handleStatus);

  // Basic rotation
  server.on("/rotate", HTTP_POST, handleRotate);
  server.on("/rotate_degrees", HTTP_POST, handleRotateDegrees);

  // Absolute positioning
  server.on("/goto", HTTP_POST, handleGoto);
  server.on("/home", HTTP_POST, handleHome);
  server.on("/set_home", HTTP_POST, handleSetHome);

  // Simple left/right
  server.on("/left", HTTP_POST, handleLeft);
  server.on("/right", HTTP_POST, handleRight);

  // 360° capture modes
  server.on("/photo360", HTTP_POST, handlePhoto360);
  server.on("/video360", HTTP_POST, handleVideo360);
  server.on("/video360_loop", HTTP_POST, handleVideo360Loop);

  // Motor control
  server.on("/stop", HTTP_POST, handleStop);
  server.on("/sleep", HTTP_POST, handleSleep);
  server.on("/wake", HTTP_POST, handleWake);

  // Legacy presets (keep for compatibility)
  server.on("/preset/45", HTTP_ANY, []() {
    rotateByDegrees(45, SPEED_MEDIUM, ACCEL_MEDIUM);
    sendJSON(200, "success", "Rotated 45 degrees");
  });

  server.on("/preset/360", HTTP_ANY, []() {
    rotateByDegrees(360, SPEED_MEDIUM, ACCEL_MEDIUM);
    sendJSON(200, "success", "Rotated 360 degrees");
  });
}

// === API Handlers ===

void handleStatus() {
  StaticJsonDocument<256> doc;
  doc["position_steps"] = stepper.currentPosition();
  doc["position_degrees"] = stepsToDegrees(stepper.currentPosition());
  doc["is_moving"] = isMoving;
  doc["distance_to_go"] = stepper.distanceToGo();
  doc["speed"] = stepper.speed();
  doc["max_speed"] = stepper.maxSpeed();
  doc["wifi_rssi"] = WiFi.RSSI();

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleRotate() {
  if (!server.hasArg("steps")) {
    sendJSON(400, "error", "Missing 'steps' parameter");
    return;
  }

  int steps = server.arg("steps").toInt();
  Serial.print("Rotate: ");
  Serial.print(steps);
  Serial.println(" steps");

  rotateBySteps(steps, SPEED_MEDIUM, ACCEL_MEDIUM);
  sendJSON(200, "success", "Moved " + String(steps) + " steps");
}

void handleRotateDegrees() {
  if (!server.hasArg("degrees")) {
    sendJSON(400, "error", "Missing 'degrees' parameter");
    return;
  }

  float degrees = server.arg("degrees").toFloat();
  Serial.print("Rotate: ");
  Serial.print(degrees);
  Serial.println(" degrees");

  rotateByDegrees(degrees, SPEED_MEDIUM, ACCEL_MEDIUM);
  sendJSON(200, "success", "Rotated " + String(degrees) + " degrees");
}

void handleGoto() {
  if (!server.hasArg("position")) {
    sendJSON(400, "error", "Missing 'position' parameter");
    return;
  }

  float targetDegrees = server.arg("position").toFloat();
  gotoAbsolutePosition(targetDegrees);
  sendJSON(200, "success", "Moved to " + String(targetDegrees) + " degrees");
}

void handleHome() {
  Serial.println("Returning to home position");

  // Calculate shortest path to home
  long currentPos = stepper.currentPosition();
  long delta = homePosition - currentPos;

  // Normalize delta to find shortest rotation
  // If delta > half revolution, go the other way
  if (delta > TOTAL_STEPS / 2) {
    delta -= TOTAL_STEPS;
  } else if (delta < -TOTAL_STEPS / 2) {
    delta += TOTAL_STEPS;
  }

  // Move by the shortest delta
  long targetPos = currentPos + delta;

  Serial.print("Current: ");
  Serial.print(currentPos);
  Serial.print(", Home: ");
  Serial.print(homePosition);
  Serial.print(", Shortest delta: ");
  Serial.println(delta);

  stepper.moveTo(targetPos);
  stepper.setMaxSpeed(SPEED_MEDIUM);    // Slower, safer return home
  stepper.setAcceleration(ACCEL_MEDIUM); // Gentle acceleration
  runToTarget();

  // Sync position to home after arrival
  stepper.setCurrentPosition(homePosition);

  sendJSON(200, "success", "Returned to home");
}

void handleSetHome() {
  homePosition = stepper.currentPosition();
  Serial.print("Home position set to: ");
  Serial.println(homePosition);
  sendJSON(200, "success", "Home position set");
}

void handleLeft() {
  float degrees = server.hasArg("degrees") ? server.arg("degrees").toFloat() : 90;
  rotateByDegrees(-degrees, SPEED_MEDIUM, ACCEL_MEDIUM);
  sendJSON(200, "success", "Rotated left " + String(degrees) + " degrees");
}

void handleRight() {
  float degrees = server.hasArg("degrees") ? server.arg("degrees").toFloat() : 90;
  rotateByDegrees(degrees, SPEED_MEDIUM, ACCEL_MEDIUM);
  sendJSON(200, "success", "Rotated right " + String(degrees) + " degrees");
}

void handlePhoto360() {
  if (!server.hasArg("count")) {
    sendJSON(400, "error", "Missing 'count' parameter");
    return;
  }

  int photoCount = server.arg("count").toInt();

  if (photoCount < 1 || photoCount > 360) {
    sendJSON(400, "error", "Invalid count (1-360)");
    return;
  }

  Serial.print("Photo360 sequence: ");
  Serial.print(photoCount);
  Serial.println(" photos");

  float degreesPerPhoto = 360.0 / photoCount;

  // Return immediately - Pi will call /rotate_degrees for each step
  StaticJsonDocument<128> doc;
  doc["status"] = "ready";
  doc["photo_count"] = photoCount;
  doc["degrees_per_photo"] = degreesPerPhoto;
  doc["total_steps"] = photoCount;

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleVideo360() {
  if (!server.hasArg("duration")) {
    sendJSON(400, "error", "Missing 'duration' parameter");
    return;
  }

  int duration = server.arg("duration").toInt();  // Duration in seconds

  if (duration < 5 || duration > 300) {
    sendJSON(400, "error", "Invalid duration (5-300 seconds)");
    return;
  }

  Serial.print("Video360: ");
  Serial.print(duration);
  Serial.println(" seconds");

  // Calculate speed for smooth rotation over duration
  // speed = steps / time = TOTAL_STEPS / duration (steps per second)
  float speed = (float)TOTAL_STEPS / (float)duration;

  // Calculate acceleration proportional to speed for smooth ramp-up
  // Use 10% of duration for acceleration (reaches full speed quickly but smoothly)
  // accel = speed / (duration * 0.1)
  float accel = speed / (duration * 0.1);

  // Ensure minimum acceleration for very long videos
  if (accel < 50) accel = 50;

  stepper.setMaxSpeed(speed);
  stepper.setAcceleration(accel);

  long startPosition = stepper.currentPosition();
  stepper.moveTo(startPosition + TOTAL_STEPS);

  // Non-blocking - return immediately
  isMoving = true;

  StaticJsonDocument<128> doc;
  doc["status"] = "rotating";
  doc["duration"] = duration;
  doc["speed"] = speed;
  doc["total_steps"] = TOTAL_STEPS;

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleVideo360Loop() {
  if (!server.hasArg("duration")) {
    sendJSON(400, "error", "Missing 'duration' parameter");
    return;
  }

  int duration = server.arg("duration").toInt();  // Duration in seconds

  if (duration < 5 || duration > 300) {
    sendJSON(400, "error", "Invalid duration (5-300 seconds)");
    return;
  }

  Serial.print("Video360 Loop mode: ");
  Serial.print(duration);
  Serial.println(" seconds");

  // Calculate speed and acceleration for the specified duration
  float speed = (float)TOTAL_STEPS / (float)duration;
  float accel = speed / (duration * 0.1);
  if (accel < 50) accel = 50;

  // Calculate steps during acceleration phase (10% of total rotation)
  long accelSteps = TOTAL_STEPS / 10;  // 10% of 360° = 36°

  stepper.setMaxSpeed(speed);
  stepper.setAcceleration(accel);

  long startPos = stepper.currentPosition();

  // Phase 1: Pre-position backwards by 10% (move to -36° from start)
  // This is done at medium speed with normal acceleration
  stepper.setMaxSpeed(SPEED_MEDIUM);
  stepper.setAcceleration(ACCEL_MEDIUM);
  stepper.moveTo(startPos - accelSteps);
  isMoving = true;
  runToTarget();

  // Phase 2: Accelerate forward through the 36° back to start position
  // By the time we reach startPos, we'll be at full cruise speed
  // Then continue for full 360° rotation plus deceleration distance
  stepper.setMaxSpeed(speed);
  stepper.setAcceleration(accel);
  stepper.moveTo(startPos + TOTAL_STEPS + accelSteps);  // 360° + 36° for deceleration
  isMoving = true;

  // Note: This is non-blocking. The sequence will be:
  // 1. Currently at: startPos - 36° (pre-positioned)
  // 2. Accelerate to startPos (cruise speed reached) <- Recording starts here
  // 3. Cruise for 360° at constant speed <- Recording happens during this
  // 4. Decelerate for final 36° <- Recording stops before this
  // 5. (Phase 3 below) Return to startPos

  // Return immediately - rotation is non-blocking
  StaticJsonDocument<128> doc;
  doc["status"] = "rotating_loop";
  doc["duration"] = duration;
  doc["speed"] = speed;
  doc["accel_steps"] = accelSteps;
  doc["start_position"] = startPos;

  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleStop() {
  Serial.println("Emergency stop!");
  stepper.stop();
  stopRequested = true;
  isMoving = false;
  sendJSON(200, "success", "Motor stopped");
}

void handleSleep() {
  sleepDriver();
  sendJSON(200, "success", "Motor disabled (sleeping)");
}

void handleWake() {
  wakeDriver();
  sendJSON(200, "success", "Motor enabled");
}

// === Helper Functions ===

void rotateBySteps(int steps, int speed, int accel) {
  stepper.setMaxSpeed(speed);
  stepper.setAcceleration(accel);
  stepper.moveTo(stepper.currentPosition() + steps);
  runToTarget();
}

void rotateByDegrees(float degrees, int speed, int accel) {
  int steps = degreesToSteps(degrees);
  rotateBySteps(steps, speed, accel);
}

void gotoAbsolutePosition(float targetDegrees) {
  // Normalize to 0-360
  while (targetDegrees < 0) targetDegrees += 360;
  while (targetDegrees >= 360) targetDegrees -= 360;

  long targetSteps = homePosition + degreesToSteps(targetDegrees);
  long currentSteps = stepper.currentPosition();

  // Calculate shortest path
  long delta = targetSteps - currentSteps;
  long altDelta = delta > 0 ? delta - TOTAL_STEPS : delta + TOTAL_STEPS;

  if (abs(altDelta) < abs(delta)) {
    delta = altDelta;
  }

  rotateBySteps(delta, SPEED_FAST, ACCEL_FAST);
}

void runToTarget() {
  isMoving = true;
  stopRequested = false;

  Serial.println("Starting movement...");
  Serial.print("Target: ");
  Serial.println(stepper.targetPosition());

  while (stepper.distanceToGo() != 0 && !stopRequested) {
    stepper.run();
    server.handleClient();  // Keep server responsive during movement
  }

  isMoving = false;
  Serial.println("Movement complete");
}

int degreesToSteps(float degrees) {
  return (int)((degrees / 360.0) * TOTAL_STEPS);
}

float stepsToDegrees(long steps) {
  return (steps % TOTAL_STEPS) * (360.0 / TOTAL_STEPS);
}

void sendJSON(int code, String status, String message) {
  StaticJsonDocument<128> doc;
  doc["status"] = status;
  doc["message"] = message;

  String json;
  serializeJson(doc, json);
  server.send(code, "application/json", json);
}

// === Main Loop ===
void loop() {
  server.handleClient();

  // Continue running stepper if in non-blocking mode (e.g., video360)
  if (isMoving && stepper.distanceToGo() != 0) {
    stepper.run();
  } else if (isMoving && stepper.distanceToGo() == 0) {
    isMoving = false;
    Serial.println("Non-blocking movement complete");
  }

  // Optional: Auto-sleep after 60 seconds of inactivity
  static unsigned long lastMoveTime = 0;
  if (stepper.distanceToGo() != 0) {
    lastMoveTime = millis();
  }

  // Uncomment to enable auto-sleep:
  // if (millis() - lastMoveTime > 60000) {
  //   sleepDriver();
  //   lastMoveTime = millis();  // Reset timer
  // }
}
