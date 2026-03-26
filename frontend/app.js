const API_URL = "https://your-backend-url.onrender.com/voice/text";

async function sendText() {
    const text = document.getElementById("text").value;

    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text})
    });

    const data = await res.json();
    document.getElementById("response").innerText = data.ai_reply;
}
