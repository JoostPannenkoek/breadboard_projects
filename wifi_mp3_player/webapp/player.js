// ============================================================
//  player.js - turns an MP3 file into numbers and streams them.
//
//  1. The browser DECODES the MP3 into samples (numbers between -1 and 1).
//  2. We RESAMPLE to 22050 samples per second, and mix left + right into
//     one channel (mono), because our player has one speaker.
//  3. We turn the numbers into 16-bit integers (-32768 .. 32767).
//  4. We send them in chunks of 1024 samples. We may only send a chunk when
//     we have a "credit". The player gives a credit back each time it has
//     played a chunk. That way its waiting room never overflows.
// ============================================================

const SAMPLE_RATE = 22050;      // samples per second (try 44100 as a challenge!)
const CHUNK_SAMPLES = 1024;     // samples per chunk (1024 samples = 2048 bytes)

class Player {
  constructor(device) {
    this.device = device;
    this.state = 'idle';        // 'idle' | 'loading' | 'playing' | 'paused' | 'stopping'
    this.samples = null;        // Int16Array with the whole song
    this.sentSamples = 0;       // how far we have sent
    this.playedChunks = 0;      // how many chunks the player has played
    this.sentChunks = 0;
    this.credits = 0;           // how many chunks we are allowed to send right now
    this.playCount = 0;
    this.listeners = {};

    device.on('credit', (n) => this.onCredit(n));
    device.on('stopped', () => this.onStopped());
    device.on('status', (status) => {
      if (status !== 'connected' && this.state !== 'idle' && this.state !== 'loading') {
        this.setState('idle');
      }
    });
  }

  on(event, callback) {
    (this.listeners[event] = this.listeners[event] || []).push(callback);
  }
  emit(event, ...args) {
    (this.listeners[event] || []).forEach((callback) => callback(...args));
  }
  setState(state) {
    this.state = state;
    this.emit('state', state);
  }

  // ----- Step 1-3: MP3 file -> Int16Array of samples -----
  static async decode(file) {
    const bytes = await file.arrayBuffer();
    // Decode the MP3. (An OfflineAudioContext doesn't need a click to start.)
    const decoder = new OfflineAudioContext(1, 1, 44100);
    const decoded = await decoder.decodeAudioData(bytes);

    // Resample + mix to mono: we "play" the song into a silent recorder
    // that records 1 channel at 22050 samples per second.
    const length = Math.ceil(decoded.duration * SAMPLE_RATE);
    const recorder = new OfflineAudioContext(1, length, SAMPLE_RATE);
    const source = recorder.createBufferSource();
    source.buffer = decoded;
    source.connect(recorder.destination);
    source.start();
    const rendered = await recorder.startRendering();

    // Float numbers (-1.0 .. 1.0) -> 16-bit integers (-32768 .. 32767)
    const floats = rendered.getChannelData(0);
    const samples = new Int16Array(floats.length);
    for (let i = 0; i < floats.length; i++) {
      const s = Math.max(-1, Math.min(1, floats[i]));   // clamp, so it can't overflow
      samples[i] = s < 0 ? s * 32768 : s * 32767;
    }
    return samples;
  }

  // ----- Step 4: streaming -----
  async play(file) {
    if (!this.device.connected || !this.device.chunkBytes) throw new Error('Not connected to a player');
    const myTurn = ++this.playCount;           // remember which "play" this is
    await this.stop();
    if (myTurn !== this.playCount) return;     // another song was clicked meanwhile
    this.setState('loading');
    let samples;
    try {
      samples = await Player.decode(file);
    } catch (e) {
      if (myTurn === this.playCount) this.setState('idle');
      throw new Error('Could not read this file as audio (' + e.message + ')');
    }
    // Someone pressed stop, or clicked another song, while we were loading
    if (myTurn !== this.playCount || this.state !== 'loading') return;
    if (!this.device.connected) { this.setState('idle'); return; }

    this.samples = samples;
    this.sentSamples = 0;
    this.sentChunks = 0;
    this.playedChunks = 0;
    // Fill the waiting room, but leave 2 chunks of space just to be safe.
    this.credits = Math.floor(this.device.bufferBytes / this.device.chunkBytes) - 2;
    this.device.send('start ' + SAMPLE_RATE);
    this.setState('playing');
    this.pump();
  }

  // Send as many chunks as we have credits for.
  pump() {
    while (this.state === 'playing' && this.credits > 0 && this.sentSamples < this.samples.length) {
      // Always send a full chunk; the last one is padded with silence (zeros).
      const chunk = new Int16Array(CHUNK_SAMPLES);
      chunk.set(this.samples.subarray(this.sentSamples, this.sentSamples + CHUNK_SAMPLES));
      if (!this.device.sendChunk(chunk)) return;
      this.sentSamples += CHUNK_SAMPLES;
      this.sentChunks++;
      this.credits--;
      this.emit('sent', chunk.byteLength);
    }
  }

  onCredit(n) {
    if (this.state !== 'playing' && this.state !== 'paused') return;
    this.credits += n;
    this.playedChunks += n;
    this.pump();
    // Every chunk we sent has been played: the song is finished!
    if (this.sentSamples >= this.samples.length && this.playedChunks >= this.sentChunks) {
      this.setState('idle');
      this.emit('ended');
    }
  }

  pause() {
    if (this.state !== 'playing') return;
    this.device.send('pause');
    this.setState('paused');
  }

  resume() {
    if (this.state !== 'paused') return;
    this.device.send('resume');
    this.setState('playing');
    this.pump();
  }

  // Stop, and wait until the player says "stopped" (or 2 seconds have passed).
  stop() {
    if (this.state === 'stopping') return this.stopPromise;   // already stopping
    if (this.state === 'idle') return Promise.resolve();
    if (this.state === 'loading') { this.setState('idle'); return Promise.resolve(); }
    this.setState('stopping');
    this.device.send('stop');
    const promise = new Promise((resolve) => { this.stopResolve = resolve; });
    this.stopPromise = promise;
    // If the player never answers, give up waiting after 2 seconds.
    setTimeout(() => { if (this.stopPromise === promise) this.onStopped(); }, 2000);
    return promise;
  }

  onStopped() {
    this.stopPromise = null;
    if (this.state === 'stopping') this.setState('idle');
    if (this.stopResolve) { this.stopResolve(); this.stopResolve = null; }
  }

  // Where are we in the song, in seconds?
  get position() {
    if (!this.samples || this.state === 'idle') return 0;
    return Math.min(this.playedChunks * CHUNK_SAMPLES, this.samples.length) / SAMPLE_RATE;
  }
  get duration() {
    return this.samples ? this.samples.length / SAMPLE_RATE : 0;
  }
}
