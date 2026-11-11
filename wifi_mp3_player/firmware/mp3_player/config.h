// ============================================================
//  config.h - all the settings of your MP3 player in one place.
//  This is the file you change most often!
// ============================================================
#pragma once

// ----- Your player's name -----
// The web app finds your player at  <name>.local  (for example mp3player-1.local).
// Give each player a different name! Use only letters, numbers and "-".
const char *const DEVICE_NAME = "mp3player-1";

// ----- Wiring: which GPIO pin goes where -----
// If you change a wire on the breadboard, change the number here too.
const int PIN_I2S_BCLK    = 26;  // amplifier BCLK (bit clock)
const int PIN_I2S_LRC     = 27;  // amplifier LRC  (left/right clock)
const int PIN_I2S_DIN     = 25;  // amplifier DIN  (the sound data)

const int PIN_BUTTON_PREV = 32;  // previous song
const int PIN_BUTTON_PLAY = 33;  // play / pause
const int PIN_BUTTON_NEXT = 14;  // next song

const int PIN_KNOB        = 34;  // middle leg of the volume knob
const int PIN_KNOB_POWER  = 13;  // outer leg of the knob (we switch this pin to 3.3 V)
const bool USE_KNOB       = true; // set to false if you have no knob connected

const int PIN_LED         = 2;   // the blue LED on the ESP32 board

// ----- Sound settings -----
const int SAMPLE_RATE  = 22050;  // samples per second (the web app can ask for another rate)
const int START_VOLUME = 40;     // volume when the player starts (0..100)

// ----- Network settings -----
const int WEBSOCKET_PORT = 81;   // the web app connects to ws://<name>.local:81

// ----- Buffer settings (advanced) -----
// The buffer is a "waiting room" for sound. A bigger buffer means fewer
// hiccups when the WiFi is slow, but a longer delay when you press pause.
// 32768 bytes = 16384 samples = about 0.75 seconds at 22050 Hz.
const int BUFFER_BYTES = 32768;
// The web app sends sound in chunks of this many bytes (1024 samples).
const int CHUNK_BYTES  = 2048;
