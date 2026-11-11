# Lesson 8: Challenges 🏆

Your MP3 player works. Now make it **yours**! Pick any challenge you like. They go from ⭐ (easy) to ⭐⭐⭐ (hard). Each one has hints, but try first without them.

**Before you start:**
- Make a copy of the file you're changing first (or use git). Then you can always go back.
- Change one small thing at a time, then test it.
- Read the error messages. They usually say which line is wrong.

---

## 🔧 Firmware challenges (ESP32, C++)

### ⭐ Your own name
Give your player a cool name in `config.h`, and connect to it in the web app.

### ⭐ Your own startup sound
When the ESP32 connects to WiFi, it plays beep-BEEP. Change it into your own little tune.
<details><summary>Hint</summary>

Look in `setup()` in `mp3_player.ino`: `audioBeep(660, 120);` plays 660 Hz for 120 ms. Add more `audioBeep` lines. You can find the note frequencies in lesson 3.
</details>

### ⭐ Start volume
Make the player start at volume 20 when no knob is connected.
<details><summary>Hint</summary>

`config.h` has `START_VOLUME` and `USE_KNOB`.
</details>

### ⭐⭐ Long press = stop
Holding PLAY down for 1 second should stop the music completely, instead of pausing.
<details><summary>Hint</summary>

In `controls.cpp`, remember *when* the button was pressed (`millis()`). When it is released, check how long it was held. Return a new event `BUTTON_STOP` (add it to the `enum` in `controls.h`), send `"button stop"` in `loop()`, and handle `stop` in `app.js` (`player.stop()`).
</details>

### ⭐⭐ Volume that feels right
Our ears are strange: going from volume 10 to 20 sounds like a big jump, but 80 to 90 hardly sounds different. Make the knob feel more natural.
<details><summary>Hint</summary>

In `audio.cpp`, the line `int16_t sample = (int32_t)mono[i] * vol / 100;` is a straight line. Try a curve: use `vol * vol / 100` instead of `vol`. (Still 0 at 0 and 100 at 100, but much softer in the middle.) Watch out for numbers getting too big!
</details>

### ⭐⭐ Dancing LED
Make the blue LED glow brighter when the music is louder.
<details><summary>Hint</summary>

`analogWrite(PIN_LED, brightness)` with brightness 0–255 makes the LED dim (this is called PWM). In the audio task, find the biggest sample (use `abs()`) in each block of 256 and save it in a variable. In `updateLed()`, turn that into a brightness.
</details>

### ⭐⭐⭐ A 4th button: shuffle
Add a fourth button that sends `button shuffle`. The web app then plays a random song.
<details><summary>Hint</summary>

You have 2 spare buttons! Free pins on the VIN side of the ESP32: **D35** is input-only and has no pull-up resistor, so that one is harder. Look on the other side of the board, or use D12 carefully (it's a "strapping pin" that affects booting). Read about strapping pins first! You need to change `config.h`, `controls.cpp`, `controls.h`, `mp3_player.ino` and `app.js`.
</details>

### ⭐⭐⭐ CD quality: 44100 Hz
Make the web app send 44100 samples per second instead of 22050. Can you hear the difference? What happens to the speed in the message log?
<details><summary>Hint</summary>

Change `SAMPLE_RATE` in `webapp/player.js`. The ESP32 automatically follows the rate in the `start` command. With twice as much data per second, the 0.75 s buffer only lasts 0.37 s, so maybe make `BUFFER_BYTES` bigger.
</details>

### ⭐⭐⭐ Sound effects button
When no song is playing, the PREV button plays a funny sound effect, made by the ESP32 itself.
<details><summary>Hint</summary>

`audioBeep()` can make tones. A "siren" is many short beeps going up and down in frequency. Use `audioIsStreaming()` to check whether a song is playing.
</details>

### ⭐⭐⭐ Real stereo (for headphones)
Only if you built the [headphone step](09_extra_headphones.md). Send the left and right channels separately, so the headphones play in real stereo. Find a song where the instruments are spread out, or a stereo test file, and hear the difference!
<details><summary>Hint</summary>

You need to change both sides:
- **Web app**, in `Player.decode()` in `player.js`: make the recorder `OfflineAudioContext` record **2** channels instead of 1. Get both with `getChannelData(0)` and `getChannelData(1)`, and put them *interleaved* in one `Int16Array` that is twice as long: left, right, left, right…
- **ESP32**, in the audio task in `audio.cpp`: the samples arrive as left/right pairs already, so don't copy each sample twice. Make it switchable: send `start 22050 stereo` from the web app, and look at how `network.cpp` reads the `start` command.
- **Watch out:** a chunk of 1024 numbers now holds only 512 moments in time, so the song position and length in `player.js` are off by a factor 2, and the buffer lasts half as long.

The speaker still sounds fine: the amplifier mixes left and right together.
</details>

---

## 🌐 Web app challenges (HTML, CSS, JavaScript)

You can test web app changes without hardware, using the fake player: see the [parent guide](00_parent_guide.md#testing-the-web-app-without-hardware).

### ⭐ Your own colours
Change the colours in `webapp/style.css`. They are all at the top, in `:root`.

### ⭐ Total playlist time
Show the total time of all songs below the playlist, for example *"5 songs · 17:32"*.
<details><summary>Hint</summary>

In `renderPlaylist()` in `app.js`, add up all the `song.duration` values and use `formatTime()`.
</details>

### ⭐⭐ Keyboard shortcuts
Space = play/pause, → = next, ← = previous.
<details><summary>Hint</summary>

```js
document.addEventListener('keydown', (event) => {
  if (event.target.tagName === 'INPUT') return;   // not while typing a command
  if (event.code === 'Space') { event.preventDefault(); togglePlay(); }
});
```
</details>

### ⭐⭐ Shuffle and repeat
Add buttons for shuffle (random order) and repeat (start again after the last song).
<details><summary>Hint</summary>

Look at `player.on('ended', ...)` in `app.js`: that's where the next song is chosen. `Math.floor(Math.random() * playlist.length)` gives a random song number.
</details>

### ⭐⭐ Draw the sound wave
Draw the current song's sound wave on a `<canvas>`, and show where you are in the song.
<details><summary>Hint</summary>

`player.samples` holds all the numbers. The canvas is maybe 600 pixels wide, so for each pixel, take a group of samples (`samples.length / 600`), find the biggest one, and draw a vertical line that tall.
</details>

### ⭐⭐⭐ Bass boost
Add a "Bass boost" checkbox that makes the low sounds louder.
<details><summary>Hint</summary>

In `Player.decode()`, put a filter between `source` and `recorder.destination`:
```js
const bass = recorder.createBiquadFilter();
bass.type = 'lowshelf';
bass.frequency.value = 200;   // everything below 200 Hz...
bass.gain.value = 10;         // ...gets 10 dB louder
source.connect(bass);
bass.connect(recorder.destination);
```
</details>

---

## 👫 Sibling challenges: both players together

### ⭐⭐⭐ Party mode
One web app connects to **both** players and plays the same song on both at the same time.
<details><summary>Hint</summary>

Make two `Device` objects and two `Player` objects in `app.js`, one for each address. Start both at the same time. Do they stay in sync? Why (not)? What could you do about it?
</details>

### ⭐⭐⭐ Walkie-talkie
Talk into the laptop's microphone, and your voice comes out of your brother's or sister's player!
<details><summary>Hint</summary>

`navigator.mediaDevices.getUserMedia({ audio: true })` gives you the microphone. An `AudioWorklet` can collect its samples. Resample them to 22050 (or simply take every 2nd sample from 44100), convert to `Int16Array`, and send them in chunks of 1024, using the credits just like `player.js` does. Send `start 22050` first!
</details>

### ⭐⭐⭐ Your own idea
Something else you'd like your player to do? Write down how you think it could work, which files you need to change, and give it a try! 🚀
