// Popup script: handles capture button and sends to backend.

const BACKEND_URL = "http://localhost:8000/api/runtime-intake/browser-selection";

document.getElementById("captureBtn").addEventListener("click", async () => {
  const statusEl = document.getElementById("status");
  const resultEl = document.getElementById("result");

  statusEl.textContent = "Capturing...";
  statusEl.className = "status loading";

  try {
    // Get selected text from active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      statusEl.textContent = "Error: No active tab found.";
      statusEl.className = "status error";
      return;
    }

    const selection = await chrome.tabs.sendMessage(tab.id, { action: "getSelectedText" });
    if (!selection || !selection.selectedText) {
      statusEl.textContent = "No text selected. Select text on Facebook and try again.";
      statusEl.className = "status error";
      return;
    }

    // Send to local backend
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page_url: selection.pageUrl,
        page_title: selection.pageTitle,
        selected_text: selection.selectedText,
        source_group: selection.sourceGroup,
        operator: "Andrii",
      }),
    });

    const data = await response.json();

    if (data.success) {
      statusEl.textContent = `Sent! Classification: ${data.classification}`;
      statusEl.className = "status success";

      document.getElementById("classification").textContent = data.classification;
      document.getElementById("suggested").textContent = data.suggested_reply?.substring(0, 150) || "—";
      resultEl.className = "result visible";
    } else {
      statusEl.textContent = `Error: ${data.errors?.join(", ") || "Unknown"}`;
      statusEl.className = "status error";
    }
  } catch (err) {
    statusEl.textContent = `Connection error: ${err.message}. Is the backend running?`;
    statusEl.className = "status error";
  }
});
