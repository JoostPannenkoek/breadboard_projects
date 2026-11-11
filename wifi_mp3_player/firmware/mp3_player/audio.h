// ============================================================
//  audio.h - everything that has to do with making sound.
//
//  Sound arrives from the web app as numbers (samples). They wait in a
//  "buffer" (a waiting room). A separate task takes them out of the
//  buffer at exactly the right speed and sends them to the amplifier.
// ============================================================
#pragma once
#include <Arduino.h>

void audioBegin();                       // start the amplifier and the audio task

void audioStart(int sampleRate);         // a new song begins: empty the buffer, set the speed
void audioStop();                        // stop playing and empty the buffer
void audioPause();                       // stop taking samples out of the buffer (keep them)
void audioResume();                      // continue

size_t audioAddSamples(const uint8_t *data, size_t bytes);  // put samples into the buffer

void audioSetVolume(int percent);        // 0 .. 100
int  audioGetVolume();

bool audioIsStreaming();                 // true between "start" and "stop"
bool audioIsPaused();
bool audioIsMakingSound();               // true when music is actually coming out

int  audioTakeCredits();                 // how many chunks were played since the last call
bool audioTakeUnderrun();                // true (once) if the buffer ran empty while playing

void audioBeep(int frequency, int lengthMs);  // play a short tone (only when not streaming)
