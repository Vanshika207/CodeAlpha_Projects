const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const typingIndicator = document.getElementById("typingIndicator");
const clearChatBtn = document.getElementById("clearChatBtn");
const themeToggle = document.getElementById("themeToggle");
const faqSearch = document.getElementById("faqSearch");
const searchResults = document.getElementById("searchResults");
const sessionAsked = document.getElementById("sessionAsked");
const matchRate = document.getElementById("matchRate");
const globalQueries = document.getElementById("globalQueries");
const resetStatsBtn = document.getElementById("resetStatsBtn");

const state = {
    asked: 0,
    matched: 0,
};

function refreshIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function getTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function updateStats(confidence) {
    state.asked += 1;
    if (confidence >= 30) {
        state.matched += 1;
    }
    sessionAsked.textContent = state.asked;
    matchRate.textContent = `${Math.round((state.matched / state.asked) * 100)}%`;
}

function createMessage(message, sender, meta = {}) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${sender === "bot" ? "bot-avatar" : "user-avatar"}`;
    avatar.innerHTML = sender === "bot" ? '<i data-lucide="bot"></i>' : '<i data-lucide="user"></i>';

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = message;

    content.appendChild(bubble);

    if (sender === "bot" && typeof meta.confidence === "number") {
        const confidence = document.createElement("div");
        confidence.className = "confidence-card";
        confidence.innerHTML = `
            <div class="confidence-row">
                <span>Confidence: <strong>${meta.confidence}%</strong></span>
                <span>${meta.confidenceLabel || "Match score"}</span>
            </div>
        `;
        content.appendChild(confidence);
    }

    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = meta.time || getTime();
    content.appendChild(time);

    row.appendChild(avatar);
    row.appendChild(content);
    chatWindow.appendChild(row);
    refreshIcons();
    scrollToBottom();
}

function setTyping(isTyping) {
    typingIndicator.classList.toggle("d-none", !isTyping);
    scrollToBottom();
}

async function askQuestion(question) {
    const message = question.trim();
    if (!message) return;

    createMessage(message, "user");
    messageInput.value = "";
    setTyping(true);

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to process your question.");
        }

        setTimeout(() => {
            setTyping(false);
            createMessage(data.answer, "bot", {
                confidence: data.confidence,
                confidenceLabel: data.confidence_label,
                time: data.timestamp,
            });
            globalQueries.textContent = data.total_questions;
            updateStats(data.confidence);
        }, 450);
    } catch (error) {
        setTyping(false);
        createMessage("Something went wrong. Please make sure the Flask server is running.", "bot", {
            confidence: 0,
            confidenceLabel: "Error",
        });
    }
}

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    askQuestion(messageInput.value);
});

document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => askQuestion(button.dataset.question));
});

clearChatBtn.addEventListener("click", () => {
    chatWindow.innerHTML = "";
    createMessage("Chat cleared. Ask me a fresh library question whenever you are ready.", "bot", {
        confidence: 100,
        confidenceLabel: "Ready",
    });
});

resetStatsBtn.addEventListener("click", () => {
    state.asked = 0;
    state.matched = 0;
    sessionAsked.textContent = "0";
    matchRate.textContent = "0%";
});

themeToggle.addEventListener("click", () => {
    const isDark = document.body.dataset.theme === "dark";
    document.body.dataset.theme = isDark ? "light" : "dark";
    themeToggle.innerHTML = isDark
        ? '<i data-lucide="moon"></i><span>Dark Mode</span>'
        : '<i data-lucide="sun"></i><span>Light Mode</span>';
    refreshIcons();
});

faqSearch.addEventListener("input", async () => {
    const query = faqSearch.value.trim();
    if (!query) {
        searchResults.innerHTML = "<p>Type keywords to search.</p>";
        return;
    }

    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const results = await response.json();

    if (!results.length) {
        searchResults.innerHTML = "<p>No FAQ found.</p>";
        return;
    }

    searchResults.innerHTML = "";
    results.forEach((item) => {
        const button = document.createElement("button");
        button.className = "search-result";
        button.textContent = item.question;
        button.addEventListener("click", () => askQuestion(item.question));
        searchResults.appendChild(button);
    });
});

refreshIcons();
