// ============================================================
//  audio.cpp - how the sound gets from the buffer to the speaker.
// ============================================================
#include "audio.h"
#include "config.h"
#include <ESP_I2S.h>
#include <freertos/stream_buffer.h>
#include <atomic>

static I2SClass i2s;
static StreamBufferHandle_t buffer;          // the "waiting room" for samples

static volatile int volume = START_VOLUME;   // 0 .. 100
static volatile bool streaming = false;      // a song is playing (or paused)
static volatile bool paused = false;
static volatile unsigned long lastSoundMs = 0;

static std::atomic<int> credits(0);          // chunks played, not yet reported to the web app
static std::atomic<bool> underrun(false);

// The network code asks the audio task to start/stop. The audio task does the
// actual work, so that two tasks never touch the buffer at the same time.
enum Request { REQ_NONE, REQ_START, REQ_STOP };
static volatile Request request = REQ_NONE;
static volatile int requestedRate = SAMPLE_RATE;
static int currentRate = SAMPLE_RATE;

// How many samples the audio task handles in one go.
const int FRAMES = 256;

// ------------------------------------------------------------
// The audio task runs all the time, next to the normal loop().
// ------------------------------------------------------------
static void handleRequest() {
  xStreamBufferReset(buffer);                // throw away everything in the waiting room
  credits = 0;
  underrun = false;
  if (request == REQ_START) {
    if (requestedRate != currentRate) {
      i2s.configureTX(requestedRate, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO);
      currentRate = requestedRate;
    }
    streaming = true;
  } else {
    streaming = false;
  }
  paused = false;
  request = REQ_NONE;                        // tell the network code we are done
}

static void audioTask(void *) {
  int16_t mono[FRAMES];                      // samples from the web app (one channel)
  int16_t stereo[FRAMES * 2];                // what we send to the amplifier (left + right)
  int bytesSinceCredit = 0;
  bool hadSound = false;

  while (true) {
    if (request != REQ_NONE) {
      handleRequest();
      bytesSinceCredit = 0;
      hadSound = false;
    }

    // 1. Take samples out of the waiting room (wait at most 5 ms for them).
    size_t bytes = 0;
    if (!paused) {
      bytes = xStreamBufferReceive(buffer, mono, sizeof(mono), pdMS_TO_TICKS(5));
    }
    int frames = bytes / 2;                  // 2 bytes per sample

    if (frames > 0) {
      // 2. Make it louder or softer, and copy it to both left and right.
      int vol = volume;
      for (int i = 0; i < frames; i++) {
        int16_t sample = (int32_t)mono[i] * vol / 100;
        stereo[i * 2] = sample;
        stereo[i * 2 + 1] = sample;
      }
      lastSoundMs = millis();
      hadSound = true;

      // 3. Every time a whole chunk has been played, the web app may send a new one.
      if (streaming) {
        bytesSinceCredit += bytes;
        while (bytesSinceCredit >= CHUNK_BYTES) {
          bytesSinceCredit -= CHUNK_BYTES;
          credits++;
        }
      }
    } else {
      // Nothing to play: send silence, so the speaker stays quiet and doesn't "pop".
      frames = paused ? FRAMES : 64;
      memset(stereo, 0, frames * 2 * sizeof(int16_t));
      if (streaming && !paused && hadSound) {
        underrun = true;                     // the waiting room ran empty!
        hadSound = false;
      }
    }

    // 4. Send to the amplifier. This waits until the amplifier is ready for more,
    //    which automatically makes us go at exactly the right speed.
    i2s.write((uint8_t *)stereo, frames * 2 * sizeof(int16_t));
  }
}

// ------------------------------------------------------------
// Functions used by the rest of the program
// ------------------------------------------------------------
void audioBegin() {
  buffer = xStreamBufferCreate(BUFFER_BYTES, 1);
  i2s.setPins(PIN_I2S_BCLK, PIN_I2S_LRC, PIN_I2S_DIN);
  if (!i2s.begin(I2S_MODE_STD, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO)) {
    Serial.println("ERROR: could not start I2S. Check the pin numbers in config.h.");
  }
  // Run the audio task on core 1 with a high priority, so music never waits.
  xTaskCreatePinnedToCore(audioTask, "audio", 4096, NULL, 5, NULL, 1);
}

static void sendRequest(Request r) {
  request = r;
  unsigned long start = millis();
  while (request != REQ_NONE && millis() - start < 500) {
    delay(1);                                // wait until the audio task has done it
  }
}

void audioStart(int sampleRate) {
  if (sampleRate < 8000 || sampleRate > 48000) sampleRate = SAMPLE_RATE;
  requestedRate = sampleRate;
  sendRequest(REQ_START);
}

void audioStop()   { sendRequest(REQ_STOP); }
void audioPause()  { paused = true; }
void audioResume() { paused = false; }

size_t audioAddSamples(const uint8_t *data, size_t bytes) {
  bytes -= bytes % 2;                        // samples are 2 bytes; never send half a sample
  return xStreamBufferSend(buffer, data, bytes, 0);
}

void audioSetVolume(int percent) { volume = constrain(percent, 0, 100); }
int  audioGetVolume()            { return volume; }

bool audioIsStreaming()   { return streaming; }
bool audioIsPaused()      { return paused; }
bool audioIsMakingSound() { return millis() - lastSoundMs < 200; }

int  audioTakeCredits()  { return credits.exchange(0); }
bool audioTakeUnderrun() { return underrun.exchange(false); }

void audioBeep(int frequency, int lengthMs) {
  if (streaming) return;                     // don't mix beeps into a song
  const int BLOCK = 256;
  int16_t block[BLOCK];
  int total = currentRate * lengthMs / 1000;
  int fade = currentRate / 200;              // 5 ms fade in/out against clicks
  float phase = 0, step = 2 * PI * frequency / currentRate;
  for (int done = 0; done < total; done += BLOCK) {
    int count = min(BLOCK, total - done);
    for (int i = 0; i < count; i++) {
      int n = done + i;
      float env = 1.0;
      if (n < fade) env = (float)n / fade;
      if (total - n < fade) env = (float)(total - n) / fade;
      block[i] = (int16_t)(sin(phase) * 12000 * env);
      phase += step;
      if (phase > 2 * PI) phase -= 2 * PI;
    }
    xStreamBufferSend(buffer, block, count * 2, pdMS_TO_TICKS(1000));
  }
}
