# The web app

A simple MP3 player that runs in your browser and streams the music to your breadboard player over WiFi.

## Start it

**Double-click `index.html`.** It opens in your browser. Use **Chrome** or **Edge**.

Then:
1. Type your player's name (`mp3player-1.local`) or its IP address, and click **Connect**.
2. Add MP3 files (button, or drag & drop).
3. Click a song. 🎶

### If connecting doesn't work from a double-clicked file
Some browsers are stricter with files opened from your disk. Start a tiny web server instead. Open a terminal in this folder and run:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

> Don't put this web app on an `https://` website. Browsers don't allow `https` pages to open unencrypted `ws://` connections, and the ESP32 only speaks `ws://`.

### Testing without a player
Run `tools/fake_device.py` (see the [parent guide](../docs/00_parent_guide.md#testing-the-web-app-without-hardware)) and connect to `localhost:8181`.

## The code

There are no frameworks and no build step. It's plain HTML, CSS and JavaScript, so you can open the files and read them. Read them in this order:

| File | What it does |
|---|---|
| `index.html` | the page: boxes, buttons, slider |
| `style.css` | how it looks (colours are at the top) |
| `device.js` | the WebSocket connection to the player: sending and receiving messages |
| `player.js` | MP3 → samples, and streaming them with credits |
| `app.js` | connects the page to the player: playlist, buttons, volume, message log |

The messages between the web app and the player are explained in [lesson 7](../docs/07_how_it_works.md#all-the-commands).
