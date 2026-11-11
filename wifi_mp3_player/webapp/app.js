// ============================================================
//  app.js - connects the buttons on the page to the player.
//  (device.js talks to the ESP32, player.js streams the music.)
// ============================================================

const device = new Device();
const player = new Player(device);
const $ = (id) => document.getElementById(id);

const playlist = [];      // the songs: { file, name, duration }
let current = -1;         // which song is selected (-1 = none)

// ------------------------------------------------------------
// Message log
// ------------------------------------------------------------
function log(kind, text) {
  const line = document.createElement('div');
  line.className = kind;
  const time = new Date().toLocaleTimeString();
  line.textContent = time + '  ' + text;
  const box = $('log');
  const atBottom = box.scrollTop + box.clientHeight >= box.scrollHeight - 5;
  box.appendChild(line);
  while (box.childElementCount > 300) box.firstChild.remove();   // keep the last 300 lines
  if (atBottom) box.scrollTop = box.scrollHeight;
}

device.on('log', (direction, text) => {
  if (text.startsWith('credit') && !$('show-credits').checked) return;
  log(direction, (direction === 'in' ? '← ' : '→ ') + text);
});
device.on('underrun', () => {
  if (player.state === 'playing' && player.sentSamples < (player.samples ? player.samples.length : 0)) {
    log('error', 'The player ran out of sound! (WiFi too slow?)');
  }
});
device.on('other', (text) => { if (text.startsWith('error')) log('error', text); });

// ------------------------------------------------------------
// 1. Connecting
// ------------------------------------------------------------
function loadSetting(key, fallback) {
  try { return localStorage.getItem(key) || fallback; } catch (e) { return fallback; }
}
function saveSetting(key, value) {
  try { localStorage.setItem(key, value); } catch (e) { /* not important */ }
}

$('address').value = loadSetting('address', 'mp3player-1.local');

$('connect-form').addEventListener('submit', (event) => {
  event.preventDefault();
  if (device.wantConnection) {
    device.disconnect();
    return;
  }
  const address = $('address').value.trim();
  if (!address) return;
  saveSetting('address', address);
  device.connect(address);
});

let failedAttempts = 0;
device.on('status', (status, info) => {
  const dot = $('status-dot');
  dot.className = 'dot';
  if (status === 'connecting') {
    dot.classList.add('connecting');
    $('status-text').textContent = 'Connecting to ' + info + ' ...';
  } else if (status === 'connected') {
    dot.classList.add('connected');
    $('status-text').textContent = 'Connected';
    failedAttempts = 0;
    $('connect-help').hidden = true;
    log('info', 'Connected to ' + info);
  } else {
    if (device.wantConnection) {
      failedAttempts++;
      $('status-text').textContent = info === true ? 'Connection lost. Trying again...' : 'Could not connect. Trying again...';
      if (failedAttempts >= 2) $('connect-help').hidden = false;
    } else {
      $('status-text').textContent = 'Not connected';
    }
    if (info === true) log('info', 'Disconnected');
  }
  $('connect-button').textContent = device.wantConnection ? 'Disconnect' : 'Connect';
});

device.on('hello', (name) => {
  $('status-text').textContent = 'Connected to ' + name;
});

// ------------------------------------------------------------
// 3. Playlist
// ------------------------------------------------------------
function formatTime(seconds) {
  if (!isFinite(seconds) || seconds < 0) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return m + ':' + String(s).padStart(2, '0');
}

function addFiles(files) {
  for (const file of files) {
    const isAudio = file.type.startsWith('audio/') || /\.(mp3|wav|ogg|m4a|flac)$/i.test(file.name);
    if (!isAudio) {
      log('error', file.name + ' is not an audio file');
      continue;
    }
    const song = { file, name: file.name.replace(/\.[^.]+$/, ''), duration: null };
    playlist.push(song);

    // Ask the browser how long the song is (it only reads the start of the file).
    const probe = new Audio();
    probe.preload = 'metadata';
    probe.src = URL.createObjectURL(file);
    probe.onloadedmetadata = () => {
      song.duration = probe.duration;
      URL.revokeObjectURL(probe.src);
      renderPlaylist();
    };
  }
  renderPlaylist();
}

function renderPlaylist() {
  const list = $('playlist');
  list.innerHTML = '';
  playlist.forEach((song, index) => {
    const item = document.createElement('li');
    if (index === current) item.classList.add('current');

    const name = document.createElement('span');
    name.className = 'name';
    name.textContent = song.name;

    const duration = document.createElement('span');
    duration.className = 'duration';
    duration.textContent = song.duration ? formatTime(song.duration) : '';

    const remove = document.createElement('button');
    remove.className = 'remove';
    remove.textContent = '✕';
    remove.title = 'Remove from playlist';
    remove.addEventListener('click', (event) => {
      event.stopPropagation();          // don't also start playing this song
      removeSong(index);
    });

    item.append(name, duration, remove);
    item.addEventListener('click', () => playSong(index));
    list.appendChild(item);
  });
}

function removeSong(index) {
  if (index === current) {
    player.stop();
    current = -1;
    $('now-title').textContent = 'Nothing yet';
  } else if (index < current) {
    current--;
  }
  playlist.splice(index, 1);
  renderPlaylist();
}

$('file-input').addEventListener('change', (event) => {
  addFiles(event.target.files);
  event.target.value = '';              // so you can add the same file again
});

// Drag and drop
const dropzone = $('dropzone');
document.addEventListener('dragover', (event) => { event.preventDefault(); dropzone.classList.add('dragging'); });
document.addEventListener('dragleave', (event) => { if (!event.relatedTarget) dropzone.classList.remove('dragging'); });
document.addEventListener('drop', (event) => {
  event.preventDefault();
  dropzone.classList.remove('dragging');
  addFiles(event.dataTransfer.files);
});

// ------------------------------------------------------------
// 2. Playing
// ------------------------------------------------------------
async function playSong(index) {
  if (playlist.length === 0) return;
  if (!device.connected) {
    log('error', 'Connect to your player first (step 1)');
    $('status-text').textContent = 'Connect to your player first!';
    return;
  }
  current = (index + playlist.length) % playlist.length;   // wrap around
  renderPlaylist();
  const song = playlist[current];
  $('now-title').textContent = song.name;
  log('info', 'Loading ' + song.file.name + ' ...');
  try {
    await player.play(song.file);
  } catch (error) {
    log('error', error.message);
  }
}

function togglePlay() {
  if (player.state === 'playing') player.pause();
  else if (player.state === 'paused') player.resume();
  else if (player.state === 'idle') playSong(current >= 0 ? current : 0);
}

function nextSong() {
  playSong(current + 1);
}

function previousSong() {
  // Like a real MP3 player: if the song has played for more than 3 seconds,
  // "previous" goes back to the start of the same song.
  if (player.position > 3) playSong(current);
  else playSong(current - 1);
}

$('play-button').addEventListener('click', togglePlay);
$('next-button').addEventListener('click', nextSong);
$('prev-button').addEventListener('click', previousSong);

player.on('state', (state) => {
  const button = $('play-button');
  if (state === 'playing') { button.textContent = '⏸'; button.setAttribute('aria-label', 'Pause'); }
  else if (state === 'loading' || state === 'stopping') { button.textContent = '⏳'; }
  else { button.textContent = '▶'; button.setAttribute('aria-label', 'Play'); }
});

// When a song is finished, play the next one (but stop after the last song).
player.on('ended', () => {
  log('info', 'Song finished');
  if (current < playlist.length - 1) playSong(current + 1);
});

// The buttons on the breadboard!
device.on('button', (name) => {
  if (name === 'play') togglePlay();
  if (name === 'next') nextSong();
  if (name === 'prev') previousSong();
});

// ------------------------------------------------------------
// Volume: the slider and the knob on the breadboard stay in sync
// ------------------------------------------------------------
const slider = $('volume');
let lastVolumeSent = 0;
let volumeTimer = null;

function sendVolume() {
  clearTimeout(volumeTimer);
  device.send('volume ' + slider.value);
  lastVolumeSent = Date.now();
}

slider.addEventListener('input', () => {
  $('volume-value').textContent = slider.value;
  // Don't send 100 messages per second while dragging: at most one every 60 ms.
  if (Date.now() - lastVolumeSent > 60) sendVolume();
  else { clearTimeout(volumeTimer); volumeTimer = setTimeout(sendVolume, 60); }
});

device.on('volume', (value) => {           // the knob was turned
  slider.value = value;
  $('volume-value').textContent = value;
});

// ------------------------------------------------------------
// Progress bar and statistics, updated 5 times per second
// ------------------------------------------------------------
let bytesSent = 0;
let bytesThisSecond = 0;
let speed = 0;
player.on('sent', (bytes) => { bytesSent += bytes; bytesThisSecond += bytes; });
setInterval(() => { speed = bytesThisSecond; bytesThisSecond = 0; }, 1000);

setInterval(() => {
  const active = player.state === 'playing' || player.state === 'paused';
  const position = active ? player.position : 0;
  const duration = active ? player.duration : (playlist[current] ? playlist[current].duration : 0);
  $('time-now').textContent = formatTime(position);
  $('time-total').textContent = formatTime(duration);
  $('progress-bar').style.width = duration ? (100 * position / duration) + '%' : '0';
  $('stats').textContent =
    'Sent: ' + Math.round(bytesSent / 1024) + ' KB · ' +
    'Speed: ' + (speed / 1024).toFixed(1) + ' KB/s · ' +
    'Credits: ' + player.credits;
}, 200);

// ------------------------------------------------------------
// 4. Typing your own commands
// ------------------------------------------------------------
$('command-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const text = $('command').value.trim();
  if (!text) return;
  if (!device.send(text)) log('error', 'Not connected');
  $('command').value = '';
});
