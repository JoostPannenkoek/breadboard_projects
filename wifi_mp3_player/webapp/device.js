// ============================================================
//  device.js - talks to the MP3 player on the breadboard.
//
//  We use a WebSocket: a connection that stays open, so the browser and
//  the ESP32 can both send messages at any moment.
//    - text messages are commands:  "volume 50", "button next", ...
//    - binary messages are sound:   1024 samples per message
// ============================================================

class Device {
  constructor() {
    this.ws = null;
    this.name = null;          // the player's name, e.g. "mp3player-1"
    this.bufferBytes = 0;      // how big the player's waiting room is
    this.chunkBytes = 0;       // how big one chunk of sound is
    this.connected = false;
    this.wantConnection = false;
    this.address = '';
    this.listeners = {};
  }

  // ----- A tiny event system: device.on('button', fn) -----
  on(event, callback) {
    (this.listeners[event] = this.listeners[event] || []).push(callback);
  }
  emit(event, ...args) {
    (this.listeners[event] || []).forEach((callback) => callback(...args));
  }

  // "mp3player-1.local" -> ws://mp3player-1.local:81/
  // "192.168.1.42:8181" -> ws://192.168.1.42:8181/
  static makeUrl(address) {
    let a = address.trim().replace(/^wss?:\/\//, '').replace(/^https?:\/\//, '').replace(/\/.*$/, '');
    if (!/:\d+$/.test(a)) a += ':81';
    return 'ws://' + a + '/';
  }

  connect(address) {
    this.disconnect();
    this.address = address;
    this.wantConnection = true;
    this.openSocket();
  }

  openSocket() {
    const url = Device.makeUrl(this.address);
    this.emit('status', 'connecting', url);
    let ws;
    try {
      ws = new WebSocket(url);
    } catch (e) {
      this.emit('status', 'error', e.message);
      return;
    }
    ws.binaryType = 'arraybuffer';
    this.ws = ws;

    ws.onopen = () => {
      this.connected = true;
      this.emit('status', 'connected', url);
    };
    ws.onmessage = (event) => {
      if (typeof event.data === 'string') this.handleText(event.data);
    };
    ws.onclose = () => {
      if (this.ws !== ws) return;          // an old connection, ignore it
      const wasConnected = this.connected;
      this.connected = false;
      this.ws = null;
      this.emit('status', 'disconnected', wasConnected);
      // Try again in 3 seconds, unless the user pressed "Disconnect".
      if (this.wantConnection) {
        clearTimeout(this.retryTimer);
        this.retryTimer = setTimeout(() => this.wantConnection && this.openSocket(), 3000);
      }
    };
  }

  disconnect() {
    this.wantConnection = false;
    clearTimeout(this.retryTimer);
    if (this.ws) {
      const ws = this.ws;
      this.ws = null;
      this.connected = false;
      ws.close();
      this.emit('status', 'disconnected', true);
    }
  }

  // Send a text command, for example device.send('volume 50')
  send(text) {
    if (!this.connected) return false;
    this.ws.send(text);
    this.emit('log', 'out', text);
    return true;
  }

  // Send one chunk of sound (an Int16Array with samples)
  sendChunk(samples) {
    if (!this.connected) return false;
    this.ws.send(samples);
    return true;
  }

  // A text message arrived from the player.
  handleText(text) {
    this.emit('log', 'in', text);
    const words = text.trim().split(/\s+/);
    const command = words[0];
    switch (command) {
      case 'hello':                 // hello <name> <bufferBytes> <chunkBytes>
        this.name = words[1];
        this.bufferBytes = parseInt(words[2], 10);
        this.chunkBytes = parseInt(words[3], 10);
        this.emit('hello', this.name);
        break;
      case 'credit':                // credit <n>: n chunks were played
        this.emit('credit', parseInt(words[1], 10));
        break;
      case 'button':                // button prev|play|next
        this.emit('button', words[1]);
        break;
      case 'volume':                // volume <0..100>: the knob was turned
        this.emit('volume', parseInt(words[1], 10));
        break;
      case 'stopped':
      case 'underrun':
      case 'pong':
        this.emit(command);
        break;
      default:
        this.emit('other', text);
    }
  }
}
