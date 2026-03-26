// ─── CONFIG ───────────────────────────────────────────────────────────────────
// Replace this with your actual Render backend URL after deployment
const API_URL = "https://voice-ai-agent-ga39.onrender.com/";

// ─── HELPERS ──────────────────────────────────────────────────────────────────
function showLoader(show) {
    document.getElementById("loader").style.display = show ? "block" : "none";
}

function showError(message) {
    const card = document.getElementById("errorCard");
    document.getElementById("errorText").innerText = "⚠️ " + message;
    card.style.display = "block";
}

function clearError() {
    document.getElementById("errorCard").style.display = "none";
}

function showResponse(aiReply, transcription = null) {
    const card = document.getElementById("responseCard");
    const transcriptionDiv = document.getElementById("transcription");
    const transcriptionText = document.getElementById("transcriptionText");
    const responseEl = document.getElementById("response");

    if (transcription) {
        transcriptionDiv.style.display = "block";
        transcriptionText.innerText = transcription;
    } else {
        transcriptionDiv.style.display = "none";
    }

    responseEl.innerText = aiReply;
    card.style.display = "block";
}

// ─── TEXT CHAT ────────────────────────────────────────────────────────────────
async function sendText() {
    const text = document.getElementById("text").value.trim();
    if (!text) {
        showError("Please type a message first.");
        return;
    }

    clearError();
    showLoader(true);
    document.getElementById("sendBtn").disabled = true;

    try {
        const res = await fetch(`${API_URL}/voice/text`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();

        if (data.status === "success") {
            showResponse(data.data.ai_reply);
        } else {
            showError(data.message || "Unknown error from server.");
        }
    } catch (err) {
        showError(err.message || "Could not connect to backend.");
    } finally {
        showLoader(false);
        document.getElementById("sendBtn").disabled = false;
    }
}

// ─── AUDIO UPLOAD ─────────────────────────────────────────────────────────────
async function transcribeAudio() {
    const fileInput = document.getElementById("audioFile");
    const file = fileInput.files[0];

    if (!file) {
        showError("Please select an audio file first.");
        return;
    }

    clearError();
    showLoader(true);
    document.getElementById("transcribeBtn").disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${API_URL}/voice/voice`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();

        if (data.status === "success") {
            showResponse(data.data.ai_reply, data.data.transcription);
        } else {
            showError(data.message || "Unknown error from server.");
        }
    } catch (err) {
        showError(err.message || "Could not connect to backend.");
    } finally {
        showLoader(false);
        document.getElementById("transcribeBtn").disabled = false;
    }
}

// ─── ENTER KEY SUPPORT ────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("text").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendText();
        }
    });
});
