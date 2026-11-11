// ============================================================
//  Test 2: First Sound
//  Plays a little melody through the amplifier and speaker.
//
//  If this works, your ESP32 -> amplifier -> speaker wiring is correct.
//
//  How it works:
//    Sound is air that wiggles back and forth. A speaker makes the air
//    wiggle by moving its cone. We tell the speaker where its cone should
//    be with NUMBERS, called "samples". We send 22050 numbers every second!
//    The numbers go from -32768 (cone all the way in) to 32767 (all the way out).
//
//    To make a tone, we calculate a smooth wave (a "sine wave").
//    A wave that wiggles 440 times per second sounds like the note A.
// ============================================================

#include <ESP_I2S.h>   // I2S = the digital "sound cable" between ESP32 and amplifier

// ----- Wiring (must match your breadboard!) -----
const int PIN_I2S_BCLK = 26;   // bit clock  -> amp BCLK
const int PIN_I2S_LRC  = 27;   // left/right -> amp LRC
const int PIN_I2S_DIN  = 25;   // data       -> amp DIN

const int SAMPLE_RATE = 22050; // samples per second
const int LOUDNESS = 6000;     // how big the wave is (max 32767). Careful, loud!

// ----- Notes: how many wiggles per second (Hz) -----
const int REST = 0;
const int NOTE_C4 = 262, NOTE_D4 = 294, NOTE_E4 = 330, NOTE_F4 = 349, NOTE_G4 = 392, NOTE_A4 = 440, NOTE_B4 = 494, NOTE_C5 = 523;

// ----- The melody: pairs of {note, length in milliseconds} -----
// Change these to write your own song!
const int melody[][2] = {
  {NOTE_C4, 300}, {NOTE_D4, 300}, {NOTE_E4, 300}, {NOTE_F4, 300},
  {NOTE_G4, 300}, {NOTE_A4, 300}, {NOTE_B4, 300}, {NOTE_C5, 600},
  {REST, 300},
  {NOTE_C5, 200}, {NOTE_G4, 200}, {NOTE_E4, 200}, {NOTE_C4, 600},
};
const int NUMBER_OF_NOTES = sizeof(melody) / sizeof(melody[0]);

I2SClass i2s;

// Plays one note. frequency = 0 means silence.
void playNote(int frequency, int lengthMs) {
  const int BLOCK = 256;            // we calculate 256 samples at a time
  int16_t block[BLOCK * 2];         // *2 because we send left AND right
  int totalSamples = SAMPLE_RATE * lengthMs / 1000;
  int fadeSamples = SAMPLE_RATE / 200;  // 5 ms fade in/out so it doesn't "click"
  float phase = 0;                  // where we are in the wave (0..2*PI)
  float step = 2 * PI * frequency / SAMPLE_RATE;

  for (int done = 0; done < totalSamples; done += BLOCK) {
    int count = min(BLOCK, totalSamples - done);
    for (int i = 0; i < count; i++) {
      int n = done + i;
      // volume envelope: fade in at the start, fade out at the end
      float envelope = 1.0;
      if (n < fadeSamples) envelope = (float)n / fadeSamples;
      if (totalSamples - n < fadeSamples) envelope = (float)(totalSamples - n) / fadeSamples;

      int16_t sample = 0;
      if (frequency > 0) sample = (int16_t)(sin(phase) * LOUDNESS * envelope);
      phase += step;
      if (phase > 2 * PI) phase -= 2 * PI;

      block[i * 2] = sample;        // left
      block[i * 2 + 1] = sample;    // right
    }
    i2s.write((uint8_t *)block, count * 2 * sizeof(int16_t));
  }
}

void setup() {
  Serial.begin(115200);
  i2s.setPins(PIN_I2S_BCLK, PIN_I2S_LRC, PIN_I2S_DIN);
  if (!i2s.begin(I2S_MODE_STD, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO)) {
    Serial.println("Oops: could not start I2S. Check the pin numbers.");
    while (true) delay(1000);
  }
  Serial.println("Playing the melody. Do you hear it?");
}

void loop() {
  for (int i = 0; i < NUMBER_OF_NOTES; i++) {
    Serial.printf("Note %d: %d Hz for %d ms\n", i + 1, melody[i][0], melody[i][1]);
    playNote(melody[i][0], melody[i][1]);
    playNote(REST, 30);             // tiny gap between notes
  }
  playNote(REST, 2000);             // wait 2 seconds, then play again
}
