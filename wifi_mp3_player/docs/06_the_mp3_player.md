# Lesson 6: The MP3 player 🎶

**Goal:** upload the real MP3 player program, open the web app, and play music!
**Time:** about 45 minutes. **You need:** your finished breadboard, the laptop, some MP3 files.

---

## Step 1: Prepare the program

The MP3 player program is in `firmware/mp3_player/`. It has several **tabs** (files):

| Tab | What's in it |
|---|---|
| `mp3_player.ino` | the main program: `setup()` and `loop()` |
| `config.h` | **all the settings**: your player's name, pins, volume. Start here! |
| `secrets.h` | your WiFi name and password (you make this one yourself) |
| `audio.cpp` | how sound goes from the buffer to the speaker |
| `controls.cpp` | reading the buttons and knob |
| `network.cpp` | WiFi, and messages to and from the web app |

1. **Close the Arduino IDE.** In your file explorer, go to `firmware/mp3_player/`. Copy `secrets.example.h` to **`secrets.h`**. (Or copy the `secrets.h` you made in lesson 5.)
2. Open `firmware/mp3_player/mp3_player.ino` in the Arduino IDE.
3. In the **`secrets.h`** tab: fill in the WiFi name and password.
4. In the **`config.h`** tab: set `DEVICE_NAME` to your player's name, the same one as in lesson 5.
   ```cpp
   const char *const DEVICE_NAME = "mp3player-1";
   ```
5. Turn the knob about halfway. **Upload**, and open the Serial Monitor.

✅ **Checkpoint:**
- You hear **two short beeps going up** (beep-BEEP) = connected to WiFi. One low beep means: no WiFi, so check `secrets.h`.
- The Serial Monitor shows:
  ```
  ==============================================
   mp3player-1 is connected to WiFi!
   In the web app, connect to:
      mp3player-1.local
      or 192.168.1.42
  ==============================================
  ```

## Step 2: Open the web app

1. In your file explorer, open the folder `webapp/` and **double-click `index.html`**. It opens in your browser. Use **Chrome** or **Edge**.
2. In box **1. Connect to your player**, type your player's name (for example `mp3player-1.local`) or its IP address, and click **Connect**.

✅ **Checkpoint:** the dot turns **green** and says *Connected to mp3player-1*. The **blue LED** on the ESP32 is on.

> 😕 It says "Could not connect"? Try the IP address instead of the `.local` name. If Chrome asks *"Allow this site to access devices on your local network?"*, click **Allow**. More help: [troubleshooting](troubleshooting.md#web-app).

## Step 3: Play music!

1. In box **3. Playlist**, click **Add MP3 files** and choose a few songs. You can also drag them onto the page.
2. Click a song, or press **▶**.

✅ **Checkpoint:** 🎉 **Music comes out of your speaker!** The blue LED blinks while music plays.

## Step 4: Try everything

| Try this | What should happen |
|---|---|
| Press **⏸ / ▶** in the web app | music pauses and continues |
| Press the **PLAY** button on the breadboard | same thing! |
| Press **NEXT** on the breadboard | next song |
| Press **PREV** on the breadboard | back to the start of the song; press again quickly for the previous song |
| Turn the **knob** | the volume changes, **and the slider in the web app moves along!** |
| Move the **volume slider** in the web app | the volume changes |
| Let a song finish | the next song starts by itself |

## Two players at the same time

Each player has its own name. Open the web app **in two browser tabs** (or on two laptops). Connect one tab to `mp3player-1.local` and the other to `mp3player-2.local`. Now you can each play your own music. Or play the same song on both at once: that's one of the [challenges](08_challenges.md)!

> Only one web app can be connected to a player at a time. If a second one connects, the first one is disconnected (the newest one wins).

## What do the lights and sounds mean?

| Signal | Meaning |
|---|---|
| beep-BEEP (going up) at startup | connected to WiFi |
| one low beep at startup | WiFi connection failed (it keeps trying) |
| blue LED off | no web app connected |
| blue LED on | web app connected |
| blue LED blinking | playing music |

---

## ✅ What did you learn?
- [ ] A program can be split into several files (tabs).
- [ ] The web app and the player talk to each other over WiFi.
- [ ] The buttons on the breadboard work like a remote control for the web app.

## 🤔 Think about it
1. The MP3 file is on the laptop, not on the ESP32. So how does the ESP32 get the music?
2. When you turn the knob, the slider in the web app moves. Which way does that message travel?
3. What do you think happens if you close the web app while music is playing? Try it!

<details><summary>Answers</summary>

1. The web app reads the MP3, turns it into numbers (samples), and sends those over WiFi to the ESP32. In the next lesson you'll find out exactly how.
2. From the ESP32 to the web app: the ESP32 sends the message `volume 57` (for example).
3. The music stops after a moment. The ESP32 notices that the web app is gone and stops playing.
</details>

> 🎧 Want to listen with headphones? There's an extra step for that: [Extra: Headphones](09_extra_headphones.md).

**Next:** [Lesson 7: How it works](07_how_it_works.md)
