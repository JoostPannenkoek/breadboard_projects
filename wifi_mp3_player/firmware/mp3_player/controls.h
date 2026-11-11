// ============================================================
//  controls.h - the buttons and the volume knob.
// ============================================================
#pragma once
#include <Arduino.h>

enum ButtonEvent { NO_BUTTON, BUTTON_PREV, BUTTON_PLAY, BUTTON_NEXT };

void controlsBegin();

// Returns which button was just pressed (or NO_BUTTON).
ButtonEvent controlsCheckButtons();

// Returns true if the knob was turned. The new position (0..100) is put in "percent".
bool controlsCheckKnob(int &percent);
