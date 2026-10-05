import os
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Harsh's Portfolio Manager",
    page_icon="Ħ",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {display: none !important;}

        /* One seamless background everywhere (matches the app's own #0e0e10) */
        html, body, .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        section.main {
            background-color: #0e0e10 !important;
            overflow: hidden !important;
        }

        /* Remove the centered 800px column and all padding */
        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            max-width: 100% !important;
        }
        [data-testid="stVerticalBlock"] {gap: 0 !important;}

        /* Pin the app iframe to the full viewport (desktop, monitor, mobile) */
        iframe {
            position: fixed !important;
            top: 0; left: 0;
            width: 100vw !important;
            height: 100vh !important;
            height: 100dvh !important;
            border: 0 !important;
            z-index: 1;
            background-color: #0e0e10;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Config & Backend Health Check
# -----------------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "https://ai-portfolio-ntso.onrender.com")

backend_live = False
try:
    res = requests.get(f"{BACKEND_URL}/", timeout=5)
    backend_live = res.status_code == 200
except Exception:
    backend_live = False

status_text = (
    "services are ready" if backend_live else "please wait till the services are up"
)

# -----------------------------------------------------------------------------
# 3. Complete Single-Stage Workspace (HTML / CSS / JS)
# -----------------------------------------------------------------------------
UNIFIED_APP_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
@import url('https://fonts.cdnfonts.com/css/candara');

* {{
    box-sizing: border-box;
}}

html, body {{
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: #0e0e10;
    color: #f5f5f7;
    font-family: 'Candara', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    overflow: hidden;
}}

.intro-stage {{
    position: absolute;
    width: 100%;
    text-align: center;
    top: 35%;
    transform: translateY(-50%);
    pointer-events: none;
}}

.greeting-text {{
    position: absolute;
    width: 100%;
    left: 0;
    font-size: 2.8rem;
    font-weight: 600;
    opacity: 0;
    letter-spacing: -0.02em;
}}

.g1 {{ animation: fadeSeq 2.2s cubic-bezier(0.4, 0, 0.2, 1) 0s forwards; }}
.g2 {{ animation: fadeSeq 2.2s cubic-bezier(0.4, 0, 0.2, 1) 2.2s forwards; }}
.g3 {{ animation: fadeSeq 2.8s cubic-bezier(0.4, 0, 0.2, 1) 4.4s forwards; }}
.status-msg {{ 
    animation: fadeSeq 2.8s cubic-bezier(0.4, 0, 0.2, 1) 7.2s forwards;
    font-size: 1.5rem;
    color: #8e8e93;
}}

@keyframes fadeSeq {{
    0%   {{ opacity: 0; transform: translateY(14px); }}
    20%  {{ opacity: 1; transform: translateY(0); }}
    80%  {{ opacity: 1; transform: translateY(0); }}
    100% {{ opacity: 0; transform: translateY(-14px); }}
}}

.workspace-stage {{
    position: relative;
    width: 100%;
    max-width: 680px;
    height: 100%;
    margin: 0 auto;
    opacity: 0;
    animation: fadeInWorkspace 1.2s cubic-bezier(0.4, 0, 0.2, 1) 10.0s forwards;
}}

@keyframes fadeInWorkspace {{
    0%   {{ opacity: 0; transform: translateY(20px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

/* Landing View Position: Centered Header and Box */
.ask-header {{
    position: absolute;
    top: 38%;
    left: 12px;
    right: 12px;
    transform: translateY(-100%);
    font-size: 2.4rem;
    font-weight: 700;
    text-align: left;
    letter-spacing: -0.015em;
    color: #f5f5f7;
    margin-bottom: 20px;
    transition: opacity 0.3s ease;
}}

.ask-header.hidden {{
    display: none;
}}

.dynamic-word {{
    color: #2997ff;
    display: inline-block;
    opacity: 1;
    transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}

.fade-out {{ opacity: 0 !important; }}

/* Input Box: Starts centered, drops to absolute bottom on chat start */
.gemini-box {{
    position: absolute;
    top: 40%;
    left: 12px;
    right: 12px;
    background-color: #1e1e20;
    border: 1px solid #2f2f32;
    border-radius: 28px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: top 0.4s cubic-bezier(0.4, 0, 0.2, 1), bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    z-index: 10;
}}

/* When active, lock box permanently at the bottom */
.workspace-stage.chat-active .gemini-box {{
    top: auto;
    bottom: 16px;
}}

.gemini-box:focus-within {{
    border-color: #444448;
    box-shadow: 0 0 12px rgba(41, 151, 255, 0.15);
}}

/* Chat Container: Fixed scrolling area above input box */
.chat-container {{
    position: absolute;
    top: 20px;
    bottom: 85px;
    left: calc(50% - 50vw);
    right: calc(50% - 50vw);
    display: none;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    padding-left: calc(50vw - 50% + 12px);
    padding-right: calc(50vw - 50% + 12px);
}}

.workspace-stage.chat-active .chat-container {{
    display: flex;
}}

/* Custom Scrollbar */
.chat-container::-webkit-scrollbar {{
    width: 6px;
}}
.chat-container::-webkit-scrollbar-thumb {{
    background: #2c2c2e;
    border-radius: 3px;
}}

.chat-bubble {{
    max-width: 82%;
    padding: 14px 18px;
    border-radius: 20px;
    font-size: 1.02rem;
    line-height: 1.6;
    word-wrap: break-word;
    white-space: pre-wrap;
    animation: fadeInBubble 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}}

@keyframes fadeInBubble {{
    0%   {{ opacity: 0; transform: translateY(10px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

.user-bubble {{
    align-self: flex-end;
    background-color: #2997ff;
    color: #ffffff;
    border-bottom-right-radius: 4px;
}}

.assistant-bubble {{
    align-self: flex-start;
    background-color: #1e1e20;
    border: 1px solid #2f2f32;
    color: #e5e5ea;
    border-bottom-left-radius: 4px;
}}

.chat-input {{
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #f5f5f7;
    font-size: 1.05rem;
    font-family: inherit;
}}

.chat-input::placeholder {{ 
    color: #8e8e93; 
}}

.plus-btn {{
    background: transparent;
    border: none;
    color: #8e8e93;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s, background 0.2s;
}}

.plus-btn:hover {{
    color: #f5f5f7;
    background: #2c2c2e;
}}

.send-btn {{
    background: #2c2c2e;
    border: none;
    color: #636366;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    cursor: not-allowed;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, color 0.2s, transform 0.1s;
}}

.send-btn.active {{
    background: #007aff;
    color: #ffffff;
    cursor: pointer;
}}

.send-btn.active:active {{
    transform: scale(0.95);
}}

.badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}}
.badge-match {{ background: #1c3d27; color: #30d158; border: 1px solid #286438; }}
.badge-missing {{ background: #3d1c1c; color: #ff453a; border: 1px solid #642828; }}

.loading-dots::after {{
    content: '.';
    animation: dots 1.4s steps(5, end) infinite;
}}

@keyframes dots {{
    0%, 20% {{ content: '.'; }}
    40% {{ content: '..'; }}
    60% {{ content: '...'; }}
    80%, 100% {{ content: ''; }}
}}

/* ---------- Responsive: large monitors ---------- */
@media (min-width: 1600px) {{
    .workspace-stage {{ max-width: 820px; }}
    .greeting-text {{ font-size: 3.4rem; }}
    .status-msg {{ font-size: 1.8rem; }}
    .ask-header {{ font-size: 2.9rem; }}
    .chat-bubble {{ font-size: 1.12rem; }}
}}

/* ---------- Responsive: tablets / phones ---------- */
@media (max-width: 640px) {{
    .greeting-text {{ font-size: 1.9rem; padding: 0 16px; }}
    .status-msg {{ font-size: 1.15rem; }}
    .ask-header {{ font-size: 1.8rem; }}
    .gemini-box {{
        padding: 8px 12px;
        gap: 8px;
        border-radius: 26px;
    }}
    .workspace-stage.chat-active .gemini-box {{
        bottom: calc(12px + env(safe-area-inset-bottom, 0px));
    }}
    .chat-container {{ bottom: calc(76px + env(safe-area-inset-bottom, 0px)); }}
    .chat-bubble {{ max-width: 92%; padding: 12px 15px; font-size: 1rem; }}
    .chat-input {{ font-size: 16px; min-width: 0; }}
}}

/* Short landscape phones */
@media (max-height: 480px) {{
    .greeting-text {{ font-size: 1.6rem; }}
    .ask-header {{ font-size: 1.5rem; top: 30%; }}
    .gemini-box {{ top: 34%; }}
}}
</style>
</head>
<body>

    <div class="intro-stage">
        <div class="greeting-text g1">Hi</div>
        <div class="greeting-text g2">नमस्ते</div>
        <div class="greeting-text g3">Welcome to Harsh's Portfolio Manager</div>
        <div class="greeting-text status-msg">{status_text}</div>
    </div>

    <div class="workspace-stage" id="workspaceStage">
        <div class="ask-header" id="askHeader">
            <span id="typewriter-base"></span><span id="dynamic-target" class="dynamic-word"></span>
        </div>

        <div class="chat-container" id="chatContainer"></div>

        <div class="gemini-box">
            <button class="plus-btn" id="plusBtn" title="Upload JD (.pdf, .docx, .txt)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            </button>
            <input type="file" id="fileInput" accept=".pdf,.docx,.txt" style="display: none;" />
            <input type="text" class="chat-input" id="userInput" placeholder="Ask something or paste a job description..." autocomplete="off" />
            <button class="send-btn" id="sendBtn" disabled>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="19" x2="12" y2="5"></line>
                    <polyline points="5 12 12 5 19 12"></polyline>
                </svg>
            </button>
        </div>
    </div>

<script>
const baseText = "Ask about ";
const firstWord = "Harsh";
const words = ["Harsh", "Internships", "Education", "Projects", "Experience", "Impact", "Tech Stack"];

const baseEl = document.getElementById("typewriter-base");
const dynamicEl = document.getElementById("dynamic-target");
const workspaceStage = document.getElementById("workspaceStage");
const askHeader = document.getElementById("askHeader");
const chatContainer = document.getElementById("chatContainer");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const plusBtn = document.getElementById("plusBtn");
const fileInput = document.getElementById("fileInput");

let chatHistory = [];
let charIndex = 0;
let firstWordIndex = 0;
let wordIndex = 0;

setTimeout(() => {{
    typeWriter();
}}, 10200);

function typeWriter() {{
    if (charIndex < baseText.length) {{
        baseEl.innerHTML += baseText.charAt(charIndex);
        charIndex++;
        setTimeout(typeWriter, 60);
    }} else {{
        typeFirstWord();
    }}
}}

function typeFirstWord() {{
    if (firstWordIndex < firstWord.length) {{
        dynamicEl.innerHTML += firstWord.charAt(firstWordIndex);
        firstWordIndex++;
        setTimeout(typeFirstWord, 70);
    }} else {{
        setTimeout(startDynamicLoop, 2200);
    }}
}}

function startDynamicLoop() {{
    setInterval(() => {{
        dynamicEl.classList.add("fade-out");
        setTimeout(() => {{
            wordIndex = (wordIndex + 1) % words.length;
            dynamicEl.innerHTML = words[wordIndex];
            dynamicEl.classList.remove("fade-out");
        }}, 400);
    }}, 2800);
}}

input.addEventListener("input", () => {{
    if (input.value.trim().length > 0) {{
        sendBtn.classList.add("active");
        sendBtn.removeAttribute("disabled");
    }} else {{
        sendBtn.classList.remove("active");
        sendBtn.setAttribute("disabled", "true");
    }}
}});

input.addEventListener("keypress", (e) => {{
    if (e.key === "Enter" && input.value.trim().length > 0) {{
        sendQuery();
    }}
}});

sendBtn.addEventListener("click", () => {{
    if (input.value.trim().length > 0) {{
        sendQuery();
    }}
}});

plusBtn.addEventListener("click", () => {{
    fileInput.click();
}});

fileInput.addEventListener("change", async () => {{
    if (fileInput.files.length === 0) return;
    const file = fileInput.files[0];
    await sendFile(file);
    fileInput.value = "";
}});

function formatResponse(data) {{
    let html = "";
    if (data.match_score > 0) {{
        html += `<div style="margin-bottom: 12px;"><strong style="font-size: 1.1rem; color: #2997ff;">Match Score: ${{data.match_score}}%</strong></div>`;
        if (data.matching_skills && data.matching_skills.length > 0) {{
            html += `<div style="margin-bottom: 8px;"><strong>Matching Skills:</strong><br>` + 
                    data.matching_skills.map(s => `<span class="badge badge-match">${{s}}</span>`).join('') + `</div>`;
        }}
        if (data.missing_skills && data.missing_skills.length > 0) {{
            html += `<div style="margin-bottom: 12px;"><strong>Missing Skills:</strong><br>` + 
                    data.missing_skills.map(s => `<span class="badge badge-missing">${{s}}</span>`).join('') + `</div>`;
        }}
    }}
    html += `<div>${{data.summary || "No details provided."}}</div>`;
    return html;
}}

function transitionToChat() {{
    if (!workspaceStage.classList.contains("chat-active")) {{
        askHeader.classList.add("hidden");
        workspaceStage.classList.add("chat-active");
    }}
}}

function appendBubble(role, content) {{
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${{role === 'user' ? 'user-bubble' : 'assistant-bubble'}}`;
    bubble.innerHTML = content;
    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return bubble;
}}

async function sendQuery() {{
    const query = input.value.trim();
    if (!query) return;

    transitionToChat();
    appendBubble("user", query);

    const loadingBubble = appendBubble("assistant", '<span class="loading-dots">Thinking...</span>');

    sendBtn.setAttribute("disabled", "true");
    sendBtn.classList.remove("active");
    input.value = "";

    try {{
            const res = await fetch("{BACKEND_URL}/evaluate-stream", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
            user_input: query,
            chat_history: chatHistory
        }})
    }});

    if (res.ok) {{
        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        let streamedText = "";

        while (true) {{
            const {{ value, done }} = await reader.read();

            if (done) break;

            streamedText += decoder.decode(value, {{ stream: true }});

            loadingBubble.innerHTML = streamedText; 

            chatContainer.scrollTop = chatContainer.scrollHeight;
        }}

        streamedText += decoder.decode();

        chatHistory.push({{
            role: "user",
            content: query
        }});

        chatHistory.push({{
            role: "assistant",
            content: streamedText
        }});

        chatContainer.scrollTop = chatContainer.scrollHeight;

    }} else {{
        loadingBubble.innerHTML = "Backend Error: Status Code " + res.status;
    }}
    }} catch (err) {{
        loadingBubble.innerHTML = "Connection Error: Unable to reach AI engine. Render server may still be spinning up. Please try sending again in 10 seconds.";
    }}
}}

async function sendFile(file) {{
    transitionToChat();
    appendBubble("user", `Uploaded file: ${{file.name}}`);

    const loadingBubble = appendBubble("assistant", `<span class="loading-dots">Processing ${{file.name}}</span>`);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("chat_history_str", JSON.stringify(chatHistory));

    try {{
        const res = await fetch("{BACKEND_URL}/evaluate-file", {{
            method: "POST",
            body: formData
        }});

        if (res.ok) {{
            const data = await res.json();
            loadingBubble.innerHTML = formatResponse(data);
            chatHistory.push({{ role: "user", content: `Uploaded file: ${{file.name}}` }});
            chatHistory.push({{ role: "assistant", content: JSON.stringify(data) }});
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }} else {{
            loadingBubble.innerHTML = "Error: Failed to parse uploaded file.";
        }}
    }} catch (err) {{
        loadingBubble.innerHTML = "Connection Error: Unable to reach AI engine.";
    }}
}}
</script>
</body>
</html>
"""

st.components.v1.html(UNIFIED_APP_HTML, height=750)