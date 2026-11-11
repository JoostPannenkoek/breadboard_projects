// ============================================================
//  Test 3: Buttons and Knob
//  Open the Serial Monitor (115200 baud), then press the buttons and
//  turn the knob. You should see messages appear.
//
//  Buttons are DIGITAL: they are either pressed or not (1 or 0).
//  The knob is ANALOG: it can be anywhere in between. The ESP32 measures
//  its voltage and turns it into a number from 0 to 4095.
// ============================================================

// ----- Wiring (must match your breadboard!) -----
const int PIN_BUTTON_PREV = 32;
const int PIN_BUTTON_PLAY = 33;
const int PIN_BUTTON_NEXT = 14;
const int PIN_KNOB        = 34;   // the middle leg of the knob
const int PIN_KNOB_POWER  = 13;   // gives 3.3 V to one outer leg of the knob
const int LED_PIN         = 2;

int lastPrev = HIGH, lastPlay = HIGH, lastNext = HIGH;
int lastKnobPercent = -1;

void setup() {
  Serial.begin(115200);

  // INPUT_PULLUP: a resistor inside the ESP32 pulls the pin up to 3.3 V (HIGH).
  // When you press the button, it connects the pin to GND, so it reads LOW.
  pinMode(PIN_BUTTON_PREV, INPUT_PULLUP);
  pinMode(PIN_BUTTON_PLAY, INPUT_PULLUP);
  pinMode(PIN_BUTTON_NEXT, INPUT_PULLUP);

  // Use a pin as a tiny 3.3 V power supply for the knob.
  pinMode(PIN_KNOB_POWER, OUTPUT);
  digitalWrite(PIN_KNOB_POWER, HIGH);

  pinMode(LED_PIN, OUTPUT);
  Serial.println("Press a button or turn the knob!");
}

// Checks one button and prints a message when it gets pressed.
// "lastState" remembers what the button was the previous time.
void checkButton(int pin, const char *name, int &lastState) {
  int state = digitalRead(pin);
  if (state == LOW && lastState == HIGH) {   // it was up, now it's down
    Serial.printf("Button %s pressed!\n", name);
  }
  lastState = state;
}

void loop() {
  checkButton(PIN_BUTTON_PREV, "PREV", lastPrev);
  checkButton(PIN_BUTTON_PLAY, "PLAY", lastPlay);
  checkButton(PIN_BUTTON_NEXT, "NEXT", lastNext);

  // LED is on while any button is held down
  bool anyPressed = (lastPrev == LOW || lastPlay == LOW || lastNext == LOW);
  digitalWrite(LED_PIN, anyPressed ? HIGH : LOW);

  int raw = analogRead(PIN_KNOB);              // 0 .. 4095
  int percent = map(raw, 0, 4095, 0, 100);     // 0 .. 100
  if (abs(percent - lastKnobPercent) >= 2) {   // only print when it really changed
    Serial.printf("Knob: raw=%4d  ->  %3d%%\n", raw, percent);
    lastKnobPercent = percent;
  }

  delay(20);   // check 50 times per second; this also ignores button "bounce"
}
