// ============================================================
//  controls.cpp - reading buttons and the knob.
// ============================================================
#include "controls.h"
#include "config.h"

// Everything we need to remember about one button.
struct Button {
  int pin;
  ButtonEvent event;          // what to report when it is pressed
  int stableState;            // the state we trust (HIGH = not pressed)
  int lastReading;            // what we read last time
  unsigned long changedAt;    // when the reading last changed
};

static Button buttons[] = {
  {PIN_BUTTON_PREV, BUTTON_PREV, HIGH, HIGH, 0},
  {PIN_BUTTON_PLAY, BUTTON_PLAY, HIGH, HIGH, 0},
  {PIN_BUTTON_NEXT, BUTTON_NEXT, HIGH, HIGH, 0},
};
const int NUMBER_OF_BUTTONS = sizeof(buttons) / sizeof(buttons[0]);

// When you press a button, the metal inside "bounces" and the pin flips between
// HIGH and LOW for a few milliseconds. We only believe a new state after it has
// stayed the same for this long:
const unsigned long DEBOUNCE_MS = 30;

static float smoothKnob = -1;   // the knob value, smoothed out
static int lastKnobPercent = -1;
static unsigned long lastKnobRead = 0;

void controlsBegin() {
  for (int i = 0; i < NUMBER_OF_BUTTONS; i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);   // HIGH when not pressed, LOW when pressed
  }
  pinMode(PIN_KNOB_POWER, OUTPUT);
  digitalWrite(PIN_KNOB_POWER, HIGH);        // 3.3 V for the knob
}

ButtonEvent controlsCheckButtons() {
  unsigned long now = millis();
  for (int i = 0; i < NUMBER_OF_BUTTONS; i++) {
    Button &b = buttons[i];
    int reading = digitalRead(b.pin);
    if (reading != b.lastReading) {          // it changed: start the timer again
      b.lastReading = reading;
      b.changedAt = now;
    }
    if (now - b.changedAt > DEBOUNCE_MS && reading != b.stableState) {
      b.stableState = reading;
      if (reading == LOW) return b.event;    // pressed!
    }
  }
  return NO_BUTTON;
}

bool controlsCheckKnob(int &percent) {
  if (!USE_KNOB) return false;
  if (millis() - lastKnobRead < 50) return false;   // read 20 times per second
  lastKnobRead = millis();

  int raw = analogRead(PIN_KNOB);                   // 0 .. 4095
  // Smoothing: take 80% of the old value and 20% of the new one.
  // This removes the little jitter that every analog reading has.
  if (smoothKnob < 0) smoothKnob = raw;
  smoothKnob = smoothKnob * 0.8 + raw * 0.2;

  // The ESP32 can't measure very close to 0 V or 3.3 V, so we use 100..4000.
  int p = map((int)smoothKnob, 100, 4000, 0, 100);
  p = constrain(p, 0, 100);

  bool changedEnough = abs(p - lastKnobPercent) >= 2;
  bool reachedEnd = (p == 0 || p == 100) && p != lastKnobPercent;
  if (changedEnough || reachedEnd) {
    lastKnobPercent = p;
    percent = p;
    return true;
  }
  return false;
}
