// ── CONFIG ────────────────────────────────────────────────────────────────────
const API_URL = "https://voice-ai-agent-ga39.onrender.com";

// ── STATE ─────────────────────────────────────────────────────────────────────
let history = [];
let isProcessing = false;

// Voice state
let voiceActive = false;
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyser = null;
let silenceTimer = 0;
let vadInterval = null;
let hasSpoken = false;   // user কথা বলেছে কিনা

// ── DOM ───────────────────────────────────────────────────────────────────────
const chatArea    = document.getElementById("chatArea");
const messages    = document.getElementById("messages");
const welcome     = document.getElementById("welcome");
const textInput   = document.getElementById("textInput");
const sendBtn     = document.getElementById("sendBtn");
const micBtn      = document.getElementById("micBtn");
const voiceOverlay = document.getElementById("voiceOverlay");
const orb         = document.getElementById("orb");
const vTitle      = document.getElementById("vTitle");
const vSub        = document.getElementById("vSub");
const soundBars   = document.getElementById("soundBars");

// ── HELPERS ───────────────────────────────────────────────────────────────────
function hideWelcome() {
  if (welcome.style.display !== "none") {
    welcome.style.transition = "opacity .2s";
    welcome.style.opacity = "0";
    setTimeout(() => welcome.style.display = "none", 200);
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 160) + "px";
}

function scrollBottom() {
  chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: "smooth" });
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendText();
  }
}

function toggleSidebar() {
  const s = document.getElementById("sidebar");
  if (window.innerWidth <= 640) {
    s.classList.toggle("open");
  } else {
    s.classList.toggle("collapsed");
  }
}

function newChat() {
  history = [];
  messages.innerHTML = "";
  welcome.style.display = "";
  welcome.style.opacity = "1";
}

// ── ADD MESSAGE ───────────────────────────────────────────────────────────────
function addMessage(role, text) {
  hideWelcome();
  const row = document.createElement("div");
  row.className = `msg-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = role === "user" ? "আ" : "✦";

  const body = document.createElement("div");
  body.className = "msg-body";

  const name = document.createElement("div");
  name.className = "msg-name";
  name.textContent = role === "user" ? "আপনি" : "AI Agent";

  const bubble = document.createElement("div");
  bubble.className = "msg-text";
  bubble.textContent = text;

  body.appendChild(name);
  body.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(body);
  messages.appendChild(row);
  scrollBottom();
  return bubble;
}

// Typing indicator
function addTyping() {
  hideWelcome();
  const row = document.createElement("div");
  row.className = "msg-row ai";
  row.id = "typingRow";

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = "✦";

  const body = document.createElement("div");
  body.className = "msg-body";

  const name = document.createElement("div");
  name.className = "msg-name";
  name.textContent = "AI Agent";

  const dots = document.createElement("div");
  dots.className = "typing-dots";
  dots.innerHTML = "<span></span><span></span><span></span>";

  body.appendChild(name);
  body.appendChild(dots);
  row.appendChild(avatar);
  row.appendChild(body);
  messages.appendChild(row);
  scrollBottom();
  return row;
}

function removeTyping() {
  const r = document.getElementById("typingRow");
  if (r) r.remove();
}

// ── PLAY AUDIO ────────────────────────────────────────────────────────────────
function playAudio(base64mp3, bubble) {
  if (!base64mp3) return Promise.resolve();
  return new Promise((resolve) => {
    const audio = new Audio("data:audio/mp3;base64," + base64mp3);
    if (bubble) bubble.classList.add("playing");

    // Voice overlay এ থাকলে speaking mode
    if (voiceActive) {
      orb.classList.add("speaking");
      setVoiceState("বলছে...", "");
      soundBars.classList.remove("active");
    }

    audio.onended = () => {
      if (bubble) bubble.classList.remove("playing");
      if (voiceActive) {
        orb.classList.remove("speaking");
        // Voice mode এ থাকলে আবার শুনতে শুরু করো
        startListening();
      }
      resolve();
    };
    audio.onerror = () => {
      if (voiceActive) startListening();
      resolve();
    };
    audio.play().catch(resolve);
  });
}

// ── TEXT CHAT ─────────────────────────────────────────────────────────────────
async function sendText() {
  const text = textInput.value.trim();
  if (!text || isProcessing) return;

  textInput.value = "";
  autoResize(textInput);
  isProcessing = true;
  sendBtn.disabled = true;

  addMessage("user", text);
  history.push({ role: "user", content: text });

  const typingRow = addTyping();

  try {
    const res = await fetch(`${API_URL}/voice/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, history }),
    });
    const data = await res.json();
    removeTyping();

    if (data.error) {
      addMessage("ai", "⚠️ " + data.error);
      return;
    }

    const bubble = addMessage("ai", data.ai_text);
    history.push({ role: "assistant", content: data.ai_text });

    // Text mode এ audio silent play (কোনো overlay নেই)
    if (data.audio_base64) {
      await playAudio(data.audio_base64, bubble);
    }

  } catch (e) {
    removeTyping();
    addMessage("ai", "⚠️ সংযোগ ব্যর্থ হয়েছে। Render URL চেক করুন।");
  } finally {
    isProcessing = false;
    sendBtn.disabled = false;
  }
}

async function sendSuggestion(text) {
  textInput.value = text;
  await sendText();
}

// ── VOICE MODE ────────────────────────────────────────────────────────────────
async function toggleVoice() {
  if (voiceActive) {
    stopVoice();
  } else {
    await startVoice();
  }
}

async function startVoice() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    voiceActive = true;
    micBtn.classList.add("active");

    // Audio context for VAD
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.4;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    // Show overlay
    voiceOverlay.classList.add("show");

    // Start listening
    startListening();

    // Store stream for cleanup
    window._voiceStream = stream;

  } catch (e) {
    alert("মাইক অ্যাক্সেস পাওয়া যায়নি। Browser permission দিন।");
  }
}

function stopVoice() {
  voiceActive = false;
  micBtn.classList.remove("active");
  voiceOverlay.classList.remove("show");

  if (vadInterval) { clearInterval(vadInterval); vadInterval = null; }
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (window._voiceStream) {
    window._voiceStream.getTracks().forEach(t => t.stop());
    window._voiceStream = null;
  }
  orb.classList.remove("speaking", "thinking");
  soundBars.classList.remove("active");
}

function setVoiceState(title, sub) {
  vTitle.textContent = title;
  vSub.textContent = sub;
}

function startListening() {
  if (!voiceActive) return;

  audioChunks = [];
  hasSpoken = false;
  silenceTimer = 0;

  setVoiceState("শুনছি...", "কথা বলুন, থামলে নিজেই পাঠাবে");
  orb.classList.remove("speaking", "thinking");
  soundBars.classList.add("active");

  mediaRecorder = new MediaRecorder(window._voiceStream, { mimeType: "audio/webm" });
  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) audioChunks.push(e.data);
  };
  mediaRecorder.onstop = () => {
    if (hasSpoken && voiceActive) {
      processVoiceAudio();
    } else if (voiceActive) {
      // কেউ কিছু বলেনি — আবার শোনো
      startListening();
    }
  };

  mediaRecorder.start(100); // 100ms chunks

  // VAD — silence detection
  if (vadInterval) clearInterval(vadInterval);
  vadInterval = setInterval(() => {
    if (!analyser || !voiceActive) return;
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    const avg = data.reduce((a, b) => a + b, 0) / data.length;

    // Real-time bar animation
    updateSoundBars(data);

    if (avg > 12) {
      hasSpoken = true;
      silenceTimer = 0;
    } else if (hasSpoken) {
      silenceTimer++;
      // ~1.5 সেকেন্ড silence (interval 50ms × 30 = 1.5s)
      if (silenceTimer > 30) {
        clearInterval(vadInterval);
        vadInterval = null;
        if (mediaRecorder && mediaRecorder.state === "recording") {
          mediaRecorder.stop();
        }
      }
    }
  }, 50);
}

function updateSoundBars(freqData) {
  const bars = soundBars.querySelectorAll("span");
  const step = Math.floor(freqData.length / bars.length);
  bars.forEach((bar, i) => {
    const val = freqData[i * step] / 255;
    const h = 4 + val * 26;
    bar.style.height = h + "px";
    bar.style.opacity = 0.4 + val * 0.6;
  });
}

async function processVoiceAudio() {
  if (!voiceActive) return;

  soundBars.classList.remove("active");
  orb.classList.add("thinking");
  setVoiceState("ভাবছি...", "");

  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("file", blob, "audio.webm");
  formData.append("history", JSON.stringify(history));

  try {
    const res = await fetch(`${API_URL}/voice/talk`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    orb.classList.remove("thinking");

    if (data.error || !data.transcription) {
      setVoiceState("বোঝা যায়নি", "আবার বলুন");
      setTimeout(() => voiceActive && startListening(), 1500);
      return;
    }

    // Chat এ দেখাও
    addMessage("user", data.transcription);
    history.push({ role: "user", content: data.transcription });

    const bubble = addMessage("ai", data.ai_text);
    history.push({ role: "assistant", content: data.ai_text });

    // Audio play করো (শেষ হলে আবার শুনবে)
    await playAudio(data.audio_base64, bubble);

  } catch (e) {
    orb.classList.remove("thinking");
    if (voiceActive) {
      setVoiceState("সংযোগ সমস্যা", "পুনরায় চেষ্টা করছে...");
      setTimeout(() => voiceActive && startListening(), 2000);
    }
  }
}
