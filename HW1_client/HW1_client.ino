/*
 * HW1-1 Client Side — ESP32
 * Features:
 *   1. LED flash  (GPIO 2 built-in LED blinks every 500ms)
 *   2. DHT11 temperature & humidity printed to Serial port  (GPIO 15)
 *   3. Send data via WiFi HTTP POST to PC server  (172.20.10.2:5000)
 *
 * WiFi:  Kaiting's iPhone  /  z0968343949
 * Server IP (PC on iPhone hotspot): 172.20.10.2
 *
 * TIP: If DHT11 errors occur, upgrade SimpleDHT library to the latest version.
 *
 * Wiring:
 *   DHT11 VCC  -> 3.3V
 *   DHT11 GND  -> GND
 *   DHT11 DATA -> GPIO 15  (with 10kOhm pull-up resistor recommended)
 *   LED         -> GPIO 2   (built-in LED on most ESP32 dev boards)
 */

#include <SimpleDHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ─── Pin Definitions ─────────────────────────────────────────────────────────
#define DHT11_PIN   15   // DHT11 DATA pin -> GPIO 15 (matches sketch_mar24b)
#define LED_PIN      2   // Built-in LED

// ─── WiFi & Server Settings ───────────────────────────────────────────────────
const char* WIFI_SSID     = "alvin";
const char* WIFI_PASSWORD = "20050423";
const char* SERVER_URL    = "http://192.168.137.254:5000/sensor";
// NOTE: 172.20.10.2 is your PC's IP on the iPhone hotspot network.
//       Run `ipconfig` on your PC to confirm if upload fails.

// ─── Global Objects ───────────────────────────────────────────────────────────
SimpleDHT11 dht11;

// ─── Timing ───────────────────────────────────────────────────────────────────
unsigned long lastReadTime  = 0;
const unsigned long READ_INTERVAL = 3000;   // Read DHT11 every 3 seconds

unsigned long lastLedToggle = 0;
const unsigned long LED_INTERVAL  = 500;    // Toggle LED every 500ms

bool ledState = false;

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("==============================");
  Serial.println("  HW1-1 Client Side -- ESP32 ");
  Serial.println("==============================");

  // ── Connect to WiFi ─────────────────────────────────────────────────────────
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 30) {               // 15 seconds timeout
      Serial.println();
      Serial.println("[WiFi] Connection FAILED. Running without WiFi.");
      break;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("[WiFi] Connected! ESP32 IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WiFi] Server URL: ");
    Serial.println(SERVER_URL);
  }

  Serial.println("------------------------------");
  Serial.println("[LED]   Blinking every 500ms");
  Serial.println("[DHT11] Reading every 3 seconds");
  Serial.println("------------------------------");
}

// ─── Main Loop ────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // ── 1. LED Flash ────────────────────────────────────────────────────────────
  if (now - lastLedToggle >= LED_INTERVAL) {
    lastLedToggle = now;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  }

  // ── 2. DHT11 Read & Serial Print ────────────────────────────────────────────
  if (now - lastReadTime >= READ_INTERVAL) {
    lastReadTime = now;

    byte temperature = 0;
    byte humidity    = 0;

    int err = SimpleDHTErrSuccess;
    if ((err = dht11.read(DHT11_PIN, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
      Serial.print("Read DHT11 failed, err="); Serial.println(err); delay(1000);
    } else {
      Serial.println("=================================");
      Serial.print("Humidity = ");
      Serial.print((int)humidity);
      Serial.print("% , ");
      Serial.print("Temperature = ");
      Serial.print((int)temperature);
      Serial.println("C ");

      // ── 3. Send via WiFi ──────────────────────────────────────────────────
      if (WiFi.status() == WL_CONNECTED) {
        sendDataToServer((int)temperature, (int)humidity);
      } else {
        Serial.println("[WiFi] Not connected, skipping upload.");
      }
    }
  }
}

// ─── WiFi Upload Function ─────────────────────────────────────────────────────
void sendDataToServer(int temp, int hum) {
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Build JSON payload
  String payload = "{";
  payload += "\"temperature\":" + String(temp) + ",";
  payload += "\"humidity\":"    + String(hum)  + ",";
  payload += "\"device_id\":\"ESP32_DHT11_HW1\"";
  payload += "}";

  Serial.print("[WiFi] POST -> ");
  Serial.println(payload);

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("[WiFi] Response (");
    Serial.print(httpCode);
    Serial.print("): ");
    Serial.println(response);
  } else {
    Serial.print("[WiFi] POST failed: ");
    Serial.println(http.errorToString(httpCode).c_str());
  }

  http.end();
}
