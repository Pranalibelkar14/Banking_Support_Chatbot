document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("send-btn");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const suggestionsDiv = document.getElementById("suggestions");
  const newChatBtn = document.getElementById("new-chat");
  const showFaqsBtn = document.getElementById("show-faqs");
  const historyList = document.getElementById("history-list");

  // render initial suggestions
  renderSuggestions(initialSuggestions);

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
  });
  newChatBtn.addEventListener("click", newChat);
  showFaqsBtn.addEventListener("click", fetchFaqs);

  async function sendMessage(textOverride) {
    const text = textOverride || userInput.value.trim();
    if (!text) return;

    appendMessage(text, "user-message");
    userInput.value = "";

    const typingEl = appendTyping();

    try {
      const res = await fetch("/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      typingEl.remove();
      appendMessage(data.response, "bot-message");

      // update suggestions if provided
      if (data.suggestions && Array.isArray(data.suggestions)) {
        renderSuggestions(data.suggestions);
      }

      // update history panel
      refreshHistory();
    } catch (err) {
      typingEl.remove();
      appendMessage("Sorry, something went wrong. Try again.", "bot-message");
      console.error(err);
    }
  }

  function appendMessage(text, className) {
    const el = document.createElement("div");
    el.className = "message " + className;
    el.textContent = text;
    chatBox.appendChild(el);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function appendTyping() {
    const el = document.createElement("div");
    el.className = "message bot-message";
    el.textContent = "Typing...";
    chatBox.appendChild(el);
    chatBox.scrollTop = chatBox.scrollHeight;
    return el;
  }

  function renderSuggestions(items) {
    suggestionsDiv.innerHTML = "";
    items.slice(0, 8).forEach((text) => {
      const btn = document.createElement("button");
      btn.textContent = text;
      btn.addEventListener("click", () => sendMessage(text));
      suggestionsDiv.appendChild(btn);
    });
  }

  async function newChat() {
    await fetch("/new_chat", { method: "POST" });
    chatBox.innerHTML = '<div class="message bot-message">New chat started. How can I help?</div>';
    refreshHistory();
  }

  async function fetchFaqs() {
    const res = await fetch("/faqs");
    const data = await res.json();
    if (data.faqs) {
      renderSuggestions(data.faqs.slice(0, 12));
    }
  }

  async function refreshHistory() {
    // simple refresh by reloading the page's history area via GET to / (not necessary but we keep UI synced)
    // Instead we could add an endpoint to fetch history; for now reloading history panel via DOM is enough.
    // For demo: do nothing — the server-side rendered history is populated on full page load.
    // You can implement /history endpoint later to fetch session history as JSON.
  }
});
