// ── CONFIG ────────────────────────────────────────────────────────────────────
const API_URL = "https://your-backend-url.onrender.com";  // ← Render URL বসাও

// ── STATE ─────────────────────────────────────────────────────────────────────
let history = [];          // conversation history
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let isProcessing = false;

// ── DOM REFS ──────────────────────────────────────────────────────────────────
const chatBox   = document.getElementById("chatBox");
const statusBar = document.getElementById("statusBar");
const micBtn    = document.getElementById("micBtn");
const micLabel  = document.getElementById("micLabel");
const textInput = document.getElementById("textInput");
const sendBtn   = document.getElementById("sendBtn");

// ── STATUS HELPERS ────────────────────────────────────────────────────────────
function setStatus(text, type = "") {
    statusBar.textContent = text;
    statusBar.className = "status-bar " + type;
}

// ── CHAT UI ───────────────────────────────────────────────────────────────────
function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    const bubble = document.createElement("span");
    bubble.className = "bubble";
    bubble.textContent = text;
    div.appendChild(bubble);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return bubble;
}

// ── PLAY AUDIO ────────────────────────────────────────────────────────────────
function playAudio(base64mp3, bubble) {
    if (!base64mp3) return Promise.resolve();
    return new Promise((resolve) => {
        const audio = new Audio("data:audio/mp3;base64," + base64mp3);
        bubble.classList.add("playing");
        setStatus("AI বলছে...", "speaking");
        audio.onended = () => {
            bubble.classList.remove("playing");
            setStatus("প্রস্তুত");
            resolve();
        };
        audio.onerror = () => { resolve(); };
        audio.play();
    });
}

// ── PROCESS RESPONSE ──────────────────────────────────────────────────────────
async function handleResponse(data) {
    if (data.error) {
        setStatus("⚠️ " + data.error, "error");
        return;
    }

    // Show user transcription (for voice input)
    if (data.transcription && data.transcription !== textInput.value) {
        // already added for text, skip duplicate
    }

    // Show AI reply
    const aiBubble = addMessage("ai", data.ai_text);

    // Save to history
    history.push({ role: "assistant", content: data.ai_text });

    // Play audio
    await playAudio(data.audio_base64, aiBubble);
}

// ── TEXT SEND ─────────────────────────────────────────────────────────────────
async function sendText() {
    const text = textInput.value.trim();
    if (!text || isProcessing) return;

    textInput.value = "";
    isProcessing = true;
    sendBtn.disabled = true;

    addMessage("user", text);
    history.push({ role: "user", content: text });
    setStatus("ভাবছি...", "thinking");

    try {
        const res = await fetch(`${API_URL}/voice/text`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, history }),
        });
        const data = await res.json();
        await handleResponse(data);
    } catch (e) {
        setStatus("সংযোগ ব্যর্থ — Render URL ঠিক আছে কি?", "error");
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
    }
}

// ── MIC TOGGLE ────────────────────────────────────────────────────────────────
async function toggleMic() {
    if (isProcessing) return;

    if (isRecording) {
        // Stop recording
        mediaRecorder.stop();
    } else {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                // Stop mic stream
                stream.getTracks().forEach(t => t.stop());
                micBtn.classList.remove("active");
                micLabel.textContent = "চাপুন";
                isRecording = false;
                isProcessing = true;

                const blob = new Blob(audioChunks, { type: "audio/webm" });
                setStatus("পাঠাচ্ছি...", "thinking");

                const formData = new FormData();
                formData.append("file", blob, "audio.webm");
                formData.append("history", JSON.stringify(history));

                try {
                    const res = await fetch(`${API_URL}/voice/talk`, {
                        method: "POST",
                        body: formData,
                    });
                    const data = await res.json();

                    if (data.transcription) {
                        addMessage("user", data.transcription);
                        history.push({ role: "user", content: data.transcription });
                    }

                    await handleResponse(data);
                } catch (e) {
                    setStatus("সংযোগ ব্যর্থ — Render URL ঠিক আছে কি?", "error");
                } finally {
                    isProcessing = false;
                }
            };

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add("active");
            micLabel.textContent = "থামুন";
            setStatus("শুনছি...", "listening");

        } catch (e) {
            setStatus("মাইক অ্যাক্সেস পাওয়া যায়নি — browser permission দিন", "error");
        }
    }
}

// ── CLEAR HISTORY ─────────────────────────────────────────────────────────────
function clearHistory() {
    history = [];
    chatBox.innerHTML = "";
    addMessage("ai", "ইতিহাস মুছে ফেলা হয়েছে। নতুন কথোপকথন শুরু করুন।");
    setStatus("প্রস্তুত");
}

// ── ENTER KEY ─────────────────────────────────────────────────────────────────
textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendText();
});
