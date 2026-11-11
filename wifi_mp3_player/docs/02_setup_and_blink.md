# Lesson 2: Setup and Blink

**Goal:** upload your first program to the ESP32.
**Time:** about 45 minutes. **You need:** laptop with the Arduino IDE (your parent installed it), the ESP32, a USB cable.

---

## The Arduino IDE

The **Arduino IDE** is the program where you write code and send it to the ESP32. (IDE = Integrated Development Environment, a fancy word for "code editor with extra buttons".)

The most important buttons are at the top left:

| Button | Name | What it does |
|---|---|---|
| ✔ | **Verify** | Checks your code for mistakes (this is called *compiling*) |
| ➜ | **Upload** | Compiles, then sends the program to the ESP32 |
| 🔍 (top right) | **Serial Monitor** | Shows messages the ESP32 sends back to the computer |

## Step 1: Connect the ESP32
1. Plug the USB cable into the ESP32 and into the laptop. A red LED on the board should light up: it has power.
2. In the Arduino IDE, click **Tools → Board → esp32 → ESP32 Dev Module**.
3. Click **Tools → Port** and choose the new port. It's called something like `COM3` (Windows), `/dev/ttyUSB0` (Linux) or `/dev/cu.usbserial-…` (Mac).
   - Not sure which one? Unplug the ESP32, look at the list, plug it back in, and look again. The new one is yours!

## Step 2: Open the Blink program
**File → Open…** and choose `firmware/tests/01_blink/01_blink.ino`.

Read the code. Lines starting with `//` are **comments**: notes for humans that the computer ignores.

```cpp
const int LED_PIN = 2;          // the onboard LED is connected to GPIO2
const int BLINK_TIME_MS = 500;  // try changing this number!

void setup() {
  pinMode(LED_PIN, OUTPUT);     // we want to SEND voltage out of this pin
  ...
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // HIGH = 3.3 volts -> LED on
  delay(BLINK_TIME_MS);
  digitalWrite(LED_PIN, LOW);   // LOW = 0 volts -> LED off
  delay(BLINK_TIME_MS);
}
```

Every Arduino program has two parts:
- **`setup()`** runs **once**, when the ESP32 starts.
- **`loop()`** runs **again and again, forever**.

## Step 3: Upload
Click **Upload** (➜). At the bottom you'll see lots of text scrolling by. It takes a while the first time. When it says **"Hard resetting via RTS pin..."**, it's done.

✅ **Checkpoint:** the **blue LED** on the ESP32 blinks: half a second on, half a second off.

> 😕 Upload failed? See [troubleshooting](troubleshooting.md#uploading). The most common fix: when the text says `Connecting.....`, press and hold the **BOOT** button on the ESP32 until the upload starts.

## Step 4: The Serial Monitor
Click the **Serial Monitor** button (🔍, top right). At the bottom, set the speed to **115200 baud**. Press the **EN** button on the ESP32 to restart it. You should see:

```
Hello from the ESP32! The LED should blink now.
```

The Serial Monitor is how the ESP32 "talks" to you. You'll use it a lot to find out what's going on inside.

## Step 5: Change it!
1. Change `BLINK_TIME_MS` to `100`. Upload. What happens?
2. Make the LED stay on for 1 second and off for 0.2 seconds. (Hint: you need two different `delay()` numbers.)
3. Add `Serial.println("on");` and `Serial.println("off");` in the right places and watch the Serial Monitor.
4. **Bonus:** make the LED blink an SOS in Morse code: `··· ——— ···`

---

## ✅ What did you learn?
- [ ] How to choose the board and port, and upload.
- [ ] `setup()` runs once, `loop()` runs forever.
- [ ] `digitalWrite(pin, HIGH)` puts 3.3 V on a pin, `LOW` puts 0 V.
- [ ] The Serial Monitor shows messages from the ESP32.

## 🤔 Quiz
1. What does `delay(2000)` do?
2. What's the difference between `setup()` and `loop()`?
3. What happens if you delete the `delay()` lines? Why can't you see it blink anymore?

<details><summary>Answers</summary>

1. Waits 2000 milliseconds = 2 seconds.
2. `setup()` runs once at the start; `loop()` repeats forever.
3. It still blinks, but millions of times per second: way too fast for your eyes. It looks like it's half-bright.
</details>

**Next:** [Lesson 3: Build part 1, sound](03_build_part1_sound.md)
