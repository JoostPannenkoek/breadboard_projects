// ============================================================
//  WiFi MP3 Player
//
//  The web app in your browser turns MP3 files into sound samples and
//  sends them over WiFi. This ESP32 receives them and plays them through
//  the amplifier and speaker. The buttons and knob work like a remote
//  control for the web app.
//
//  Files (tabs) in this sketch:
//    config.h      - settings: name, pins, volume   <- start here!
//    secrets.h     - your WiFi name and password (copy secrets.example.h)
//    audio.cpp     - buffer -> amplifier -> speaker
//    controls.cpp  - buttons and knob
//    network.cpp   - WiFi and WebSocket messages
// ============================================================
#include "config.h"
#include "audio.h"
#include "controls.h"
#include "network.h"

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.printf("Hi! I am %s.\n", DEVICE_NAME);

  pinMode(PIN_LED, OUTPUT);
  audioBegin();
  controlsBegin();

  // Give the knob a moment, then use its position as the starting volume.
  int knob;
  audioSetVolume(START_VOLUME);
  delay(100);
  for (int i = 0; i < 10; i++) {
    if (controlsCheckKnob(knob)) audioSetVolume(knob);
    delay(55);
  }

  if (networkBegin()) {
    // Happy sound: WiFi works!
    audioBeep(660, 120);
    audioBeep(880, 180);
  } else {
    // Sad sound: no WiFi yet.
    audioBeep(330, 400);
  }
}

// The LED tells you what is going on:
//   off      = no web app connected
//   on       = web app connected
//   blinking = playing music
void updateLed() {
  bool on;
  if (!networkHasClient())        on = false;
  else if (audioIsMakingSound())  on = (millis() / 250) % 2;   // blink
  else                            on = true;
  digitalWrite(PIN_LED, on ? HIGH : LOW);
}

void loop() {
  networkLoop();

  // A button was pressed: tell the web app. The web app decides what to do
  // (it knows the playlist).
  ButtonEvent button = controlsCheckButtons();
  if (button == BUTTON_PREV) { Serial.println("Button: prev"); networkSend("button prev"); }
  if (button == BUTTON_PLAY) { Serial.println("Button: play"); networkSend("button play"); }
  if (button == BUTTON_NEXT) { Serial.println("Button: next"); networkSend("button next"); }

  // The knob was turned: change the volume, and tell the web app so its slider moves too.
  int knob;
  if (controlsCheckKnob(knob)) {
    audioSetVolume(knob);
    char msg[16];
    snprintf(msg, sizeof(msg), "volume %d", knob);
    networkSend(msg);
  }

  updateLed();
  delay(1);
}
