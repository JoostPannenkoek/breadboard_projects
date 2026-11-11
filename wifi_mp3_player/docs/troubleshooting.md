# Troubleshooting 🔍

Something doesn't work? That's normal, and engineers spend most of their time finding problems! Go through the checklist for your problem **one item at a time**.

**Golden rules:**
1. **Unplug USB** before you change any wire.
2. **Compare with the picture**, hole by hole. Count the rows out loud.
3. **Ask a buddy** to check your board. Fresh eyes spot mistakes faster.
4. **Change one thing at a time**, then test again.

---

## Uploading

**There's no port in Tools → Port**
- [ ] Is the USB cable a **data** cable? Many cables can only charge. Try another cable.
- [ ] Is the driver installed? (See the [parent guide](00_parent_guide.md#1-check-the-parts).)
- [ ] Linux: is your user in the `dialout` group? On Ubuntu, remove `brltty`.
- [ ] Try another USB port on the laptop.

**Upload fails with `Failed to connect to ESP32` or `Timed out waiting for packet header`**
- [ ] When the text says `Connecting.....`, **press and hold the BOOT button** on the ESP32 until you see percentages appear.
- [ ] Is the right board selected? **Tools → Board → ESP32 Dev Module**.
- [ ] Is the Serial Monitor of *another* program using the port? Close it.
- [ ] Unplug the amplifier's VIN wire (wire 8) and try again.

**Compile error: `secrets.h: No such file or directory`**
- [ ] You forgot to copy `secrets.example.h` to `secrets.h` in the sketch folder. See lesson 5.

**Compile error: `WebSocketsServer.h: No such file or directory`**
- [ ] Install the library: **Tools → Manage Libraries**, search `WebSockets`, and install the one **by Markus Sattler**.

**Compile error about `ESP_I2S.h`**
- [ ] Your ESP32 board package is too old. Update **esp32 by Espressif Systems** to version 3.x in the Boards Manager.

---

## No sound

Run `02_first_sound` while you check this.

- [ ] Is the **red power LED** on the ESP32 on?
- [ ] Amplifier pins in **`g20` to `g26`**? Labels: `g20` = LRC, `g21` = BCLK, `g22` = DIN.
- [ ] **Wire 4** (yellow) from `j6` to `j20`, **wire 5** (green) from `j7` to `j21`, **wire 6** (blue) from `j8` to `j22`? Count again!
- [ ] **Wire 8** (red) from `j26` to the **+** rail, **wire 7** (black) from `j25` to the **−** rail?
- [ ] **Wire 1** (red) from `j1` (VIN) to the + rail, **wire 2** (black) from `j2` (GND) to the − rail?
- [ ] Does your breadboard have a **break in the rails** halfway? Look at the red and blue lines.
- [ ] Are the speaker wires screwed in tight? Pull gently.
- [ ] Is the speaker cable's metal touching the screw terminal, not the plastic insulation?
- [ ] In the MP3 player: is the volume (knob/slider) above 0?
- [ ] **Swap test:** swap your amplifier with your brother's or sister's. Does the problem move with it?

**It crackles or hums**
- [ ] Loose wire somewhere? Press all wires in firmly.
- [ ] Is the volume very high? Turn it down a bit.

---

## Buttons and knob

Run `03_buttons_knob` and open the Serial Monitor while you check this.

**A button does nothing**
- [ ] Is the button pushed in all the way, across the middle gap (legs in `e` and `f`)?
- [ ] Are your wires on **diagonal** legs: one wire in column `j` of the **top** row, one in column `a` of the **bottom** row?
- [ ] Is the left − rail connected to GND? That's **wire 3**, the long wire across the board at row 50.
- [ ] Is the white wire in the right ESP32 row? PREV = `j10`, PLAY = `j9`, NEXT = `j5`.

**A button says "pressed" all the time**
- [ ] The wires are probably on two legs that are always connected. Use the diagonal rule!

**The knob always shows 0% or 100%, or jumps around**
- [ ] Are the knob legs in `f29`, `f30`, `f31`?
- [ ] **Wire 16** (purple, middle leg) to `j12` (D34)? **Wire 17** (orange) to `j3` (D13)? **Wire 15** (black) to the − rail?
- [ ] The volume goes *down* when you turn right? That's not a mistake! Swap wires 15 and 17 at the knob end if you prefer the other direction.

---

## WiFi

**The Serial Monitor only shows dots, never "Connected"**
- [ ] WiFi name and password in `secrets.h` exactly right? **Capital letters matter.** Spaces too.
- [ ] Is it a **2.4 GHz** network? The ESP32 can't see 5 GHz-only networks.
- [ ] School/work networks with a username and password don't work. Try a phone hotspot.
- [ ] Too far from the router? Move closer.

**The music stutters**
- [ ] Check the signal strength in the Serial Monitor at startup. Below −75 dBm is too weak. Move closer to the router.
- [ ] Is someone in the house streaming 4K video or downloading a big game? 😄
- [ ] Try a bigger buffer: `BUFFER_BYTES` in `config.h` (for example 65536).

---

## Web app

**"Could not connect"**
- [ ] Is the ESP32 on, and did it say "connected to WiFi" (two beeps going up)?
- [ ] Is the laptop on the **same WiFi network** as the ESP32?
- [ ] Try the **IP address** from the Serial Monitor instead of the `.local` name. Windows doesn't always understand `.local`.
- [ ] Did you type the same name as `DEVICE_NAME` in `config.h`?
- [ ] Chrome asked to *"access devices on your local network"*? Click **Allow**. Did you click Block by accident? Click the icon left of the address bar → **Site settings** → allow **Local network access**.
- [ ] Still nothing? Run a tiny web server instead of double-clicking. Open a terminal in the `webapp` folder and type `python3 -m http.server 8000`. Then open <http://localhost:8000> in the browser.

**It connects, but disconnects again and again**
- [ ] Is a second browser tab connected to the same player? Only one can be connected at a time: the newest one wins.
- [ ] Weak WiFi? See above.

**"Could not read this file as audio"**
- [ ] Is it really an MP3? Some files are protected (DRM) or broken. Try another file.

**The slider and the knob fight each other**
- [ ] Whatever you touched last wins. If the knob's reading jumps around a lot, check its wiring.

---

## Headphones

Run `02_first_sound` while you check this. Hold the headphones a little away from your ear.

**The speaker plays, but the headphones are silent**
- [ ] Is the plug pushed in **all the way**? It clicks.
- [ ] DAC pins in **`h55` to `h63`**, with VIN in row 55?
- [ ] **Wire 18** (red) from the **+** rail to `f55`, **wire 19** (black) from the **−** rail to `f57`? Is the red wire in the rail next to the red line?
- [ ] **Wire 20** (yellow) `i20` → `f58`, **wire 21** (blue) `i22` → `f59`, **wire 22** (green) `i21` → `f60`? Wires 21 and 22 should cross.
- [ ] Look at the solder joints with a magnifying glass, or your phone camera zoomed in. Shiny little volcanoes? Or balls, or solder between two pins? Ask a grown-up to fix them.
- [ ] Nothing in the 6 holes on the other side of the DAC (MUTE, PLL, …)? A wire in MUTE can switch the DAC off.
- [ ] Try other headphones.

**Sound in one ear only**
- [ ] Push the plug in all the way.
- [ ] Headsets with a microphone (a plug with **3** black rings) sometimes don't fit well. Try headphones whose plug has 2 rings.

**It hisses or hums a bit**
- [ ] A soft hiss with the volume up is normal. A loud hum? Check wire 19 (GND).

**The speaker won't switch off**
- [ ] Is wire 23 from `j24` (amp SD) to the **−** rail? See [Speaker off](09_extra_headphones.md#speaker-off-one-extra-wire).

---

## Still stuck?
Write down:
1. What you expected to happen
2. What happened instead (exact error message, or a photo of the screen)
3. What you already tried

Then ask for help. Often, writing it down helps you find it yourself! 🦆 (Programmers call this *rubber duck debugging*: explain your problem to a rubber duck, and the answer often pops up.)
