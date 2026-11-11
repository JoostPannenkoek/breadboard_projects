// ============================================================
//  Test 4: WiFi
//  Connects to your home WiFi and tells you its address.
//
//  BEFORE YOU UPLOAD:
//    1. Close the Arduino IDE. In your file explorer, open this sketch's
//       folder, copy "secrets.example.h" and name the copy "secrets.h".
//    2. Open the sketch again. Click the "secrets.h" tab and type your
//       WiFi name and password between the quotes.
//    secrets.h is never shared or uploaded to GitHub.
// ============================================================

#include <WiFi.h>
#include <ESPmDNS.h>
#include "secrets.h"

const char *DEVICE_NAME = "mp3player-1";   // give your player its own name!

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.printf("Connecting to WiFi network \"%s\"", WIFI_SSID);

  WiFi.mode(WIFI_STA);              // STA = "station": we join an existing network
  WiFi.setHostname(DEVICE_NAME);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int seconds = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    seconds++;
    if (seconds == 20) {
      Serial.println();
      Serial.println("Still not connected... Check the name and password in secrets.h.");
      Serial.println("Note: the ESP32 only works with 2.4 GHz WiFi, not 5 GHz.");
    }
  }

  Serial.println();
  Serial.println("Connected!");
  Serial.print("My IP address is: ");
  Serial.println(WiFi.localIP());

  // mDNS lets computers find us by name instead of by number.
  if (MDNS.begin(DEVICE_NAME)) {
    Serial.printf("You can also find me as: %s.local\n", DEVICE_NAME);
  }
}

void loop() {
  // RSSI = signal strength. Closer to 0 is better.
  //   -30 to -60: great    -60 to -70: OK    below -75: weak (music may stutter)
  int rssi = WiFi.RSSI();
  Serial.printf("Signal strength: %d dBm  %s\n", rssi,
                rssi > -60 ? "(great)" : rssi > -70 ? "(OK)" : "(weak - move closer to the router)");
  delay(3000);
}
