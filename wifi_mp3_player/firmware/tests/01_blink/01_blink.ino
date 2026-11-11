// ============================================================
//  Test 1: Blink
//  Makes the little blue LED on the ESP32 board blink.
//
//  If this works, you know that:
//    - the USB cable carries data (not just power)
//    - the driver is installed
//    - the Arduino IDE can upload code to your ESP32
//
//  No wiring needed! The LED is already on the board.
// ============================================================

const int LED_PIN = 2;          // the onboard LED is connected to GPIO2
const int BLINK_TIME_MS = 500;  // try changing this number!

// setup() runs ONE time, when the ESP32 starts.
void setup() {
  pinMode(LED_PIN, OUTPUT);     // we want to SEND voltage out of this pin
  Serial.begin(115200);         // open the Serial Monitor at 115200 baud
  Serial.println("Hello from the ESP32! The LED should blink now.");
}

// loop() runs AGAIN and AGAIN, forever.
void loop() {
  digitalWrite(LED_PIN, HIGH);  // HIGH = 3.3 volts -> LED on
  delay(BLINK_TIME_MS);         // wait (in milliseconds, 1000 ms = 1 second)
  digitalWrite(LED_PIN, LOW);   // LOW = 0 volts -> LED off
  delay(BLINK_TIME_MS);
}
