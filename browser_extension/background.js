// Background service worker — minimal by design.
// No background scraping. No auto-actions.

const BACKEND_URL = "http://localhost:8000/api/runtime-intake/browser-selection";

chrome.runtime.onInstalled.addListener(() => {
  console.log("Sezonski Rad Intake extension installed. Capture mode: user-click only.");
});

// The extension does NOT:
// - Auto-scroll
// - Auto-click
// - Auto-post
// - Auto-comment
// - Read cookies
// - Store credentials
// - Run background tasks
// - Scrape external groups
