#!/usr/bin/env python3
"""
fake_device.py - pretends to be an MP3 player on the breadboard.

Use it to try the web app without any hardware:

    pip install -r requirements.txt
    python fake_device.py

Then, in the web app, connect to  localhost:8181

It speaks exactly the same protocol as the real ESP32 firmware:
  - it "plays" the sound at the real speed (it doesn't make sound itself,
    but it saves everything it receives to received.wav, so you can listen
    to it afterwards)
  - it sends "credit" messages when a chunk has been played
  - type  prev / play / next  (and Enter) in this window to "press" a button
  - type  volume 30  to "turn the knob"
"""

import argparse
import asyncio
import sys
import time
import wave

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

BUFFER_BYTES = 32768   # same as config.h
CHUNK_BYTES = 2048


class FakePlayer:
    def __init__(self, name, wav_path):
        self.name = name
        self.wav_path = wav_path
        self.client = None
        self.volume = 40
        self.reset()

    def reset(self):
        self.streaming = False
        self.paused = False
        self.rate = 22050
        self.level = 0.0            # bytes waiting in the buffer
        self.since_credit = 0.0     # bytes played since the last credit
        self.had_sound = False
        self.received = 0
        self.dropped = 0
        self.started_at = None
        self.close_wav()

    def close_wav(self):
        wav = getattr(self, "wav", None)
        if wav:
            wav.close()
            print(f"   saved {self.wav_path}")
        self.wav = None

    async def send(self, text):
        if self.client:
            try:
                await self.client.send(text)
            except ConnectionClosed:
                pass

    # ---- messages from the web app ----
    async def on_text(self, text):
        print(f"<- {text}")
        words = text.split()
        if not words:
            return
        word, args = words[0], [int(w) for w in words[1:] if w.lstrip("-").isdigit()]
        if word == "start":
            self.reset()
            self.rate = args[0] if args else 22050
            self.streaming = True
            self.started_at = time.monotonic()
            self.wav = wave.open(self.wav_path, "wb")
            self.wav.setnchannels(1)
            self.wav.setsampwidth(2)
            self.wav.setframerate(self.rate)
        elif word == "stop":
            self.print_stats()
            self.reset()
            await self.send("stopped")
        elif word == "pause":
            self.paused = True
        elif word == "resume":
            self.paused = False
        elif word == "volume":
            self.volume = max(0, min(100, args[0] if args else self.volume))
        elif word == "ping":
            await self.send("pong")
        elif word == "hello":
            await self.send_hello()
        elif word == "beep":
            print("   (beep!)")
        else:
            await self.send(f"error unknown command: {word}")

    def on_binary(self, data):
        if not self.streaming:
            return
        space = BUFFER_BYTES - self.level
        if len(data) > space:
            self.dropped += len(data) - space
            print(f"!! buffer overflow: {len(data) - space:.0f} bytes dropped "
                  f"(the web app sent more than its credits allowed)")
            data = data[: int(space)]
        self.level += len(data)
        self.received += len(data)
        if self.wav:
            self.wav.writeframes(data)

    async def send_hello(self):
        await self.send(f"hello {self.name} {BUFFER_BYTES} {CHUNK_BYTES}")
        await self.send(f"volume {self.volume}")

    def print_stats(self):
        if self.started_at:
            secs = time.monotonic() - self.started_at
            print(f"   received {self.received / 1024:.0f} KB in {secs:.1f} s "
                  f"({self.received / 1024 / max(secs, 0.001):.1f} KB/s), "
                  f"dropped {self.dropped:.0f} bytes")

    # ---- the "speaker": takes bytes out of the buffer at the real speed ----
    async def play_loop(self):
        last = time.monotonic()
        while True:
            await asyncio.sleep(0.01)
            now = time.monotonic()
            dt, last = now - last, now
            if not self.streaming or self.paused:
                continue
            want = self.rate * 2 * dt          # 2 bytes per sample
            played = min(want, self.level)
            self.level -= played
            if played > 0:
                self.had_sound = True
                self.since_credit += played
                credits = int(self.since_credit // CHUNK_BYTES)
                if credits:
                    self.since_credit -= credits * CHUNK_BYTES
                    await self.send(f"credit {credits}")
            elif self.had_sound:
                self.had_sound = False
                await self.send("underrun")
                print("   underrun (buffer empty - the song ended, or the web app is too slow)")


async def keyboard_loop(player):
    """Read commands typed in this window: prev / play / next / volume N."""
    while True:
        raw = await asyncio.to_thread(sys.stdin.readline)
        if raw == "":          # no keyboard (e.g. started in the background): stop listening
            return
        line = raw.strip()
        if not line:
            continue
        if line in ("prev", "play", "next"):
            await player.send(f"button {line}")
            print(f"-> button {line}")
        elif line.startswith("volume"):
            await player.send(line)
            print(f"-> {line}")
        else:
            print("Type: prev, play, next, or volume <0-100>")


async def main():
    parser = argparse.ArgumentParser(description="Pretend to be a breadboard MP3 player.")
    parser.add_argument("--port", type=int, default=8181)
    parser.add_argument("--name", default="fake-player")
    parser.add_argument("--wav", default="received.wav")
    args = parser.parse_args()

    player = FakePlayer(args.name, args.wav)

    async def handler(ws):
        if player.client:
            await player.client.close()        # newest web app wins, like the real one
        player.reset()
        player.client = ws
        print(f"Web app connected from {ws.remote_address[0]}")
        await player.send_hello()
        try:
            async for message in ws:
                if isinstance(message, bytes):
                    player.on_binary(message)
                else:
                    await player.on_text(message)
        except ConnectionClosed:
            pass
        finally:
            if player.client is ws:
                print("Web app disconnected")
                player.print_stats()
                player.reset()
                player.client = None

    async with serve(handler, "0.0.0.0", args.port, max_size=2**20):
        print(f"Fake player '{args.name}' is listening. Connect the web app to: localhost:{args.port}")
        print("Type prev / play / next / volume 30 and press Enter to simulate the hardware.")
        await asyncio.gather(player.play_loop(), keyboard_loop(player))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
