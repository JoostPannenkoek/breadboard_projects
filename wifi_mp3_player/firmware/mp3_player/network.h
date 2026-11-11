// ============================================================
//  network.h - WiFi and talking to the web app.
// ============================================================
#pragma once
#include <Arduino.h>

bool networkBegin();                 // connect to WiFi, start the WebSocket server
void networkLoop();                  // call this in loop(): handles messages
bool networkHasClient();             // is a web app connected?
void networkSend(const char *text);  // send a text message to the web app
