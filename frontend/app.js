// CONFIG
const API_URL = "https://voice-ai-agent-ga39.onrender.com";

function getSupportedMimeType() {
  const types = ["audio/webm;codecs=opus","audio/webm","audio/mp4","audio/ogg;codecs=opus","audio/ogg"];
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return "";
}

let history = [];
let isProcessing = false;
let voiceActive = false;
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyser = null;
let silenceTimer = 0;
let vadInterval = null;
let hasSpoken = false;

const chatArea     = document.getElementById("chatArea");
const messages     = document.getElementById("messages");
const welcome      = document.getElementById("welcome");
const textInput    = document.getElementById("textInput");
const sendBtn      = document.getElementById("sendBtn");
const micBtn       = document.getElementById("micBtn");
const voiceOverlay = document.getElementById("voiceOverlay");
const orb          = document.getElementById("orb");
const vTitle       = document.getElementById("vTitle");
const vSub         = document.getElementById("vSub");
const soundBars    = document.getElementById("soundBars");

function hideWelcome() {
  if (welcome && welcome.style.display !== "none") {
    welcome.style.transition = "opacity .2s";
    welcome.style.opacity = "0";
    setTimeout(() => { if(welcome) welcome.style.display = "none"; }, 200);
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
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendText(); }
}

function toggleSidebar() {
  const s = document.getElementById("sidebar");
  if (window.innerWidth <= 640) { s.classList.toggle("open"); }
  else { s.classList.toggle("collapsed"); }
}

function newChat() {
  history = [];
  messages.innerHTML = "";
  if (welcome) { welcome.style.display = ""; welcome.style.opacity = "1"; }
}

function addMessage(role, text) {
  hideWelcome();
  const row = document.createElement("div");
  row.className = "msg-row " + role;
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
}

function removeTyping() {
  const r = document.getElementById("typingRow");
  if (r) r.remove();
}

function playAudio(base64mp3, bubble) {
  if (!base64mp3) return Promise.resolve();
  return new Promise((resolve) => {
    const audio = new Audio("data:audio/mp3;base64," + base64mp3);
    if (bubble) bubble.classList.add("playing");
    if (voiceActive) {
      orb.classList.add("speaking");
      setVoiceState("বলছে...", "");
      soundBars.classList.remove("active");
    }
    audio.onended = () => {
      if (bubble) bubble.classList.remove("playing");
      if (voiceActive) { orb.classList.remove("speaking"); startListening(); }
      resolve();
    };
    audio.onerror = () => {
      if (bubble) bubble.classList.remove("playing");
      if (voiceActive) startListening();
      resolve();
    };
    audio.play().catch(() => resolve());
  });
}

async function sendText() {
  const text = textInput.value.trim();
  if (!text || isProcessing) return;
  textInput.value = "";
  autoResize(textInput);
  isProcessing = true;
  sendBtn.disabled = true;
  addMessage("user", text);
  history.push({ role: "user", content: text });
  addTyping();
  try {
    const res = await fetch(API_URL + "/voice/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, history }),
    });
    const data = await res.json();
    removeTyping();
    if (data.error) { addMessage("ai", "⚠️ " + data.error); return; }
    const bubble = addMessage("ai", data.ai_text);
    history.push({ role: "assistant", content: data.ai_text });
    if (data.audio_base64) await playAudio(data.audio_base64, bubble);
  } catch (e) {
    removeTyping();
    addMessage("ai", "⚠️ সংযোগ ব্যর্থ। Render চালু আছে কিনা দেখুন।");
  } finally {
    isProcessing = false;
    sendBtn.disabled = false;
  }
}

async function sendSuggestion(text) {
  textInput.value = text;
  await sendText();
}

async function toggleVoice() {
  if (voiceActive) { stopVoice(); } else { await startVoice(); }
}

async function startVoice() {
  if (!window.MediaRecorder) {
    alert("এই browser এ voice সাপোর্ট নেই। Chrome ব্যবহার করুন।");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 }
    });
    voiceActive = true;
    micBtn.classList.add("active");
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.4;
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
    } catch (e) { analyser = null; }
    voiceOverlay.classList.add("show");
    window._voiceStream = stream;
    startListening();
  } catch (e) {
    let msg = "মাইক্রোফোন চালু করা যায়নি।\n\n";
    if (e.name === "NotAllowedError" || e.name === "PermissionDeniedError") {
      msg += "Browser Settings থেকে এই সাইটের Microphone Allow করুন, তারপর Page Reload করুন।";
    } else if (e.name === "NotFoundError") {
      msg += "কোনো মাইক্রোফোন পাওয়া যায়নি।";
    } else { msg += e.message; }
    alert(msg);
  }
}

function stopVoice() {
  voiceActive = false;
  micBtn.classList.remove("active");
  voiceOverlay.classList.remove("show");
  if (vadInterval) { clearInterval(vadInterval); vadInterval = null; }
  if (mediaRecorder && mediaRecorder.state !== "inactive") { try { mediaRecorder.stop(); } catch(e) {} }
  if (audioContext) { try { audioContext.close(); } catch(e) {} audioContext = null; analyser = null; }
  if (window._voiceStream) { window._voiceStream.getTracks().forEach(t => t.stop()); window._voiceStream = null; }
  orb.classList.remove("speaking", "thinking");
  soundBars.classList.remove("active");
}

function setVoiceState(title, sub) {
  if (vTitle) vTitle.textContent = title;
  if (vSub) vSub.textContent = sub;
}

function startListening() {
  if (!voiceActive || !window._voiceStream) return;
  audioChunks = [];
  hasSpoken = false;
  silenceTimer = 0;
  setVoiceState("শুনছি...", "কথা বলুন, থামলে নিজেই পাঠাবে");
  orb.classList.remove("speaking", "thinking");
  soundBars.classList.add("active");
  const mimeType = getSupportedMimeType();
  try {
    mediaRecorder = new MediaRecorder(window._voiceStream, mimeType ? { mimeType } : {});
  } catch (e) {
    mediaRecorder = new MediaRecorder(window._voiceStream);
  }
  mediaRecorder.ondataavailable = (e) => { if (e.data && e.data.size > 0) audioChunks.push(e.data); };
  mediaRecorder.onstop = () => {
    if (!voiceActive) return;
    if (hasSpoken && audioChunks.length > 0) { processVoiceAudio(); }
    else { setTimeout(() => voiceActive && startListening(), 300); }
  };
  mediaRecorder.start(100);
  if (vadInterval) clearInterval(vadInterval);
  vadInterval = setInterval(() => {
    if (!voiceActive) { clearInterval(vadInterval); return; }
    if (analyser) {
      const data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(data);
      const avg = data.reduce((a, b) => a + b, 0) / data.length;
      updateSoundBars(data);
      if (avg > 10) { hasSpoken = true; silenceTimer = 0; }
      else if (hasSpoken) {
        silenceTimer++;
        if (silenceTimer > 30) {
          clearInterval(vadInterval); vadInterval = null;
          if (mediaRecorder.state === "recording") mediaRecorder.stop();
        }
      }
    } else { animateBarsRandom(); }
  }, 50);
  if (!analyser) {
    setTimeout(() => {
      if (voiceActive && mediaRecorder && mediaRecorder.state === "recording") {
        hasSpoken = true; mediaRecorder.stop();
      }
    }, 5000);
  }
}

function updateSoundBars(freqData) {
  const bars = soundBars.querySelectorAll("span");
  const step = Math.floor(freqData.length / bars.length);
  bars.forEach((bar, i) => {
    const val = freqData[i * step] / 255;
    bar.style.height = (4 + val * 26) + "px";
    bar.style.opacity = 0.4 + val * 0.6;
  });
}

function animateBarsRandom() {
  const bars = soundBars.querySelectorAll("span");
  bars.forEach(bar => {
    bar.style.height = (4 + Math.random() * 22) + "px";
    bar.style.opacity = 0.3 + Math.random() * 0.7;
  });
}

async function processVoiceAudio() {
  if (!voiceActive) return;
  soundBars.classList.remove("active");
  orb.classList.add("thinking");
  setVoiceState("ভাবছি...", "");
  const mimeType = mediaRecorder ? mediaRecorder.mimeType : "audio/webm";
  const blob = new Blob(audioChunks, { type: mimeType || "audio/webm" });
  const formData = new FormData();
  const ext = mimeType.includes("mp4") ? "mp4" : mimeType.includes("ogg") ? "ogg" : "webm";
  formData.append("file", blob, "audio." + ext);
  formData.append("history", JSON.stringify(history));
  try {
    const res = await fetch(API_URL + "/voice/talk", { method: "POST", body: formData });
    const data = await res.json();
    orb.classList.remove("thinking");
    if (data.error || !data.transcription) {
      setVoiceState("বোঝা যায়নি", "আবার বলুন");
      setTimeout(() => voiceActive && startListening(), 1500);
      return;
    }
    addMessage("user", data.transcription);
    history.push({ role: "user", content: data.transcription });
    const bubble = addMessage("ai", data.ai_text);
    history.push({ role: "assistant", content: data.ai_text });
    await playAudio(data.audio_base64, bubble);
  } catch (e) {
    orb.classList.remove("thinking");
    if (voiceActive) {
      setVoiceState("সংযোগ সমস্যা", "আবার চেষ্টা করছে...");
      setTimeout(() => voiceActive && startListening(), 2000);
    }
  }
}