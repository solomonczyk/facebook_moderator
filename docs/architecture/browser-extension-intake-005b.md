---
type: architecture
section: browser_extension
task: TASK-005B
date: 2026-06-26
---

# Browser Extension Intake

## How It Works

1. Operator opens Facebook in their browser
2. Operator selects text from a post or comment
3. Operator clicks the extension button
4. Extension captures: selected text, page URL, page title
5. Extension sends to local backend: `POST /api/runtime-intake/browser-selection`
6. Backend maps to runtime event → agent processes

## What It Does NOT Do

- No credential storage
- No cookie reading
- No auto-scrolling
- No auto-clicking
- No auto-posting
- No auto-commenting
- No messaging
- No background scraping
- No reading external groups without operator action

## Permissions Required

```json
{
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["http://localhost:8000/*"]
}
```

`activeTab` — access current tab only when operator clicks extension.
`storage` — save preferences locally.
`localhost` — send captured content to local backend only.

No Facebook permissions. No cookies. No background scripts.
