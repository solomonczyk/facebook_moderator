# Sezonski Rad Intake — Browser Extension

Captures user-selected text from Facebook and sends it to the local runtime agent.

## Install

1. Open Chrome/Edge → `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `browser_extension/` folder

## Use

1. Open Facebook in your browser
2. Select text from a post or comment
3. Click the extension icon
4. Click "Capture Selection"
5. Text is sent to `localhost:8000` → runtime agent processes

## What it does NOT do

- No auto-scrolling
- No auto-clicking
- No auto-posting
- No cookie reading
- No credential storage
- No background scraping

## Requirements

- Backend running on `localhost:8000`
- `POST /api/runtime-intake/browser-selection` endpoint active
