---
type: operator_guide
task: TASK-005B
date: 2026-06-26
---

# How to Use — Runtime Intake

## Mode A: Manual Paste

1. Copy text from Facebook post/comment
2. Open `POST /api/runtime-intake/manual-paste`
3. Paste text + source info
4. Agent processes → queue → operator reviews

## Mode B: Clipboard

1. Copy text from Facebook (Ctrl+C)
2. Run clipboard intake command or POST /api/runtime-intake/clipboard
3. Agent processes automatically

## Mode C: Browser Extension

1. Install extension from `browser_extension/`
2. Open Facebook
3. Select text from a post/comment
4. Click extension icon
5. Click "Capture Selection"
6. Success notification appears
7. Agent processes → operator reviews queue

## After Intake

1. Open `GET /api/runtime-agent/queue`
2. Review pending items
3. Approve / Edit / Reject each
4. Manually post approved content to Facebook

No auto-posting. Everything goes through operator approval.
