# Lesson 5: WiFi

**Goal:** connect the ESP32 to your home WiFi and find its address.
**Time:** about 30 minutes. **You need:** your breadboard, the laptop, the WiFi name and password.

---

## Step 1: Your secret file
Your WiFi password should never be shared, not even in code you put online. So we keep it in a separate file called **`secrets.h`**. That file is on the "ignore list" (`.gitignore`), so it never gets uploaded to GitHub.

1. **Close the Arduino IDE.**
2. In your file explorer, open the folder `firmware/tests/04_wifi/`.
3. Copy the file **`secrets.example.h`** and name the copy **`secrets.h`**.
4. Open `04_wifi.ino` in the Arduino IDE. You now see a tab called `secrets.h`. Click it and fill in your WiFi name and password:
   ```cpp
   const char *WIFI_SSID = "OurHomeWiFi";
   const char *WIFI_PASSWORD = "the-password";
   ```
5. In the `04_wifi.ino` tab, change `DEVICE_NAME` to your player's name: `mp3player-1` or `mp3player-2`, or your own name like `sam-speaker`. Only use letters, numbers and `-`. **The two players must have different names!**

## Step 2: Upload and watch
Upload the sketch and open the Serial Monitor (115200 baud).

✅ **Checkpoint:**
```
Connecting to WiFi network "OurHomeWiFi".....
Connected!
My IP address is: 192.168.1.42
You can also find me as: mp3player-1.local
Signal strength: -52 dBm  (great)
```

**Write down your IP address:** `___.___.___.___`

> 😕 Only dots, never "Connected"? Check the name and password (capital letters matter!), and see [troubleshooting](troubleshooting.md#wifi).

## How do devices find each other?

### IP addresses
Every device on your network gets a number from the **router** (the WiFi box), like `192.168.1.42`. It works like a house number: if you know it, you can send messages to it. The router hands out these numbers automatically, so tomorrow your ESP32 might get a different one.

### Names: `.local`
Remembering numbers is annoying. So the ESP32 also announces a name on the network, using **mDNS** (multicast DNS). It shouts into the network: *"Hey everyone, I'm mp3player-1.local, and my number is 192.168.1.42!"* Your laptop listens and remembers it.

This is why the web app can connect to `mp3player-1.local` instead of the number. On some laptops (often Windows), `.local` names don't always work. Then you just use the IP address.

### Signal strength (RSSI)
RSSI is measured in **dBm**, and it's always a negative number. **Closer to zero is better:**

| RSSI | Signal |
|---|---|
| −30 to −60 | 💪 great |
| −60 to −70 | 👍 OK |
| below −75 | 😬 weak: music may stutter |

**Experiment:** walk around the house with the laptop and the ESP32 (on a long USB cable or a power bank). Watch the number. Where is the signal the best? What happens if you put your hand over the antenna (the zigzag line)? Or put the ESP32 inside a metal pan? 🍳

### 2.4 GHz
WiFi uses radio waves. The ESP32 can only use the **2.4 GHz** band, not 5 GHz. Most routers do both, so this usually just works.

---

## ✅ What did you learn?
- [ ] Passwords go in `secrets.h`, which is never shared.
- [ ] Every device on the network has an IP address.
- [ ] mDNS lets you use a name (`.local`) instead of a number.
- [ ] RSSI tells you how strong the WiFi signal is.

## 🤔 Quiz
1. Why don't we write the WiFi password directly in the `.ino` file?
2. Your ESP32 has IP address `192.168.1.42`, and your sister's has `192.168.1.43`. Why is it important that they have different names?
3. Which RSSI is better: −45 or −80?

<details><summary>Answers</summary>

1. Because then it ends up everywhere the code goes (GitHub, friends, ...). `secrets.h` stays private.
2. If both shout "I'm mp3player-1.local!", the laptop doesn't know which one you mean.
3. −45 (closer to 0).
</details>

**Next:** [Lesson 6: The MP3 player](06_the_mp3_player.md)
