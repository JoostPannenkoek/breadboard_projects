// ============================================================
//  network.cpp - WiFi, and the WebSocket "phone line" to the web app.
//
//  A WebSocket is a connection that stays open, so both sides can send
//  messages whenever they want. We use two kinds of messages:
//    - TEXT messages are commands, like "volume 50" or "button next"
//    - BINARY messages are sound: 1024 samples per message
// ============================================================
#include "network.h"
#include "config.h"
#include "secrets.h"
#include "audio.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WebSocketsServer.h>

static WebSocketsServer webSocket(WEBSOCKET_PORT);
static int client = -1;            // number of the connected web app (-1 = nobody)
static bool mdnsStarted = false;
static unsigned long droppedBytes = 0;

void networkSend(const char *text) {
  if (client >= 0) webSocket.sendTXT(client, text);
}

bool networkHasClient() { return client >= 0; }

static void sendHello() {
  char msg[80];
  snprintf(msg, sizeof(msg), "hello %s %d %d", DEVICE_NAME, BUFFER_BYTES, CHUNK_BYTES);
  networkSend(msg);
  snprintf(msg, sizeof(msg), "volume %d", audioGetVolume());
  networkSend(msg);
}

// ------------------------------------------------------------
// Commands from the web app. Every command is a word, sometimes
// followed by numbers. For example: "volume 50" or "beep 440 200".
// ------------------------------------------------------------
static void handleCommand(const char *text) {
  Serial.printf("<- %s\n", text);

  char word[16] = "";
  int number = 0, number2 = 0;
  sscanf(text, "%15s %d %d", word, &number, &number2);

  if (strcmp(word, "start") == 0) {
    audioStart(number > 0 ? number : SAMPLE_RATE);
    droppedBytes = 0;
  } else if (strcmp(word, "stop") == 0) {
    audioStop();
    networkSend("stopped");
  } else if (strcmp(word, "pause") == 0) {
    audioPause();
  } else if (strcmp(word, "resume") == 0) {
    audioResume();
  } else if (strcmp(word, "volume") == 0) {
    audioSetVolume(number);
  } else if (strcmp(word, "ping") == 0) {
    networkSend("pong");
  } else if (strcmp(word, "hello") == 0) {
    sendHello();
  } else if (strcmp(word, "beep") == 0) {
    audioBeep(number > 0 ? number : 880, number2 > 0 ? min(number2, 3000) : 200);
  } else {
    char msg[64];
    snprintf(msg, sizeof(msg), "error unknown command: %s", word);
    networkSend(msg);
  }
}

// ------------------------------------------------------------
// This function is called by the WebSocket library whenever
// something happens: someone connects, leaves, or sends a message.
// ------------------------------------------------------------
static void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t *payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED: {
      Serial.printf("Web app #%d connected from %s\n", num, webSocket.remoteIP(num).toString().c_str());
      int oldClient = client;
      client = num;
      if (oldClient >= 0 && oldClient != num) {
        webSocket.disconnect(oldClient);   // only one web app at a time: the newest wins
      }
      audioStop();
      sendHello();
      break;
    }
    case WStype_DISCONNECTED:
      Serial.printf("Web app #%d disconnected\n", num);
      if (num == client) {
        client = -1;
        audioStop();                      // nobody is listening: stop the music
      }
      break;
    case WStype_TEXT: {
      if (num != client) break;
      char text[64];
      size_t n = min(length, sizeof(text) - 1);
      memcpy(text, payload, n);
      text[n] = '\0';
      handleCommand(text);
      break;
    }
    case WStype_BIN:
      if (num != client || !audioIsStreaming()) break;
      // Sound! Put it in the waiting room.
      droppedBytes += length - audioAddSamples(payload, length);
      break;
    default:
      break;
  }
}

// ------------------------------------------------------------
static void printWelcome() {
  Serial.println();
  Serial.println("==============================================");
  Serial.printf(" %s is connected to WiFi!\n", DEVICE_NAME);
  Serial.println(" In the web app, connect to:");
  Serial.printf("    %s.local\n", DEVICE_NAME);
  Serial.print("    or ");
  Serial.println(WiFi.localIP());
  Serial.printf(" Signal strength: %d dBm\n", WiFi.RSSI());
  Serial.println("==============================================");
}

bool networkBegin() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(DEVICE_NAME);
  WiFi.setSleep(false);      // no power saving: music needs the WiFi awake all the time
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.printf("Connecting to WiFi \"%s\"", WIFI_SSID);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  webSocket.begin();
  webSocket.onEvent(onWebSocketEvent);
  webSocket.enableHeartbeat(15000, 3000, 2);   // notice when a browser silently disappears

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Could not connect to WiFi (yet). I'll keep trying...");
    Serial.println("Check WIFI_SSID and WIFI_PASSWORD in secrets.h (2.4 GHz only!).");
    return false;
  }
  return true;
}

void networkLoop() {
  webSocket.loop();

  // Start mDNS (the ".local" name) as soon as we have WiFi.
  if (WiFi.status() == WL_CONNECTED && !mdnsStarted) {
    if (MDNS.begin(DEVICE_NAME)) {
      MDNS.addService("ws", "tcp", WEBSOCKET_PORT);
      mdnsStarted = true;
    }
    printWelcome();
  }

  // Tell the web app how many chunks were played, so it can send new ones.
  int credits = audioTakeCredits();
  if (credits > 0 && audioIsStreaming()) {
    char msg[24];
    snprintf(msg, sizeof(msg), "credit %d", credits);
    networkSend(msg);
  }

  if (audioTakeUnderrun()) {
    networkSend("underrun");
    Serial.println("Underrun: the buffer ran empty (slow WiFi, or the song ended)");
  }

  if (droppedBytes > 0) {
    Serial.printf("Warning: buffer full, %lu bytes of sound were dropped\n", droppedBytes);
    droppedBytes = 0;
  }
}
