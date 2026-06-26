// Content script: captures user-selected text from the active page.
// Runs only when the user clicks the extension button (activeTab permission).

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getSelectedText") {
    const selectedText = window.getSelection()?.toString()?.trim() || "";
    const pageUrl = window.location.href;
    const pageTitle = document.title;

    // Detect Facebook group context
    let sourceGroup = "";
    try {
      const groupEl = document.querySelector('[class*="group"] h1, [class*="Group"] h1, title');
      if (groupEl) sourceGroup = groupEl.textContent?.trim() || "";
    } catch {
      // Not a Facebook group page
    }

    sendResponse({
      selectedText,
      pageUrl,
      pageTitle,
      sourceGroup,
    });
  }
  return true;
});
