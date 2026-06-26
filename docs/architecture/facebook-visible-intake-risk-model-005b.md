---
type: architecture
section: intake_risk_model
task: TASK-005B
date: 2026-06-26
---

# Facebook Visible Intake — Risk Model

## Default: Safe Modes Only

```yaml
manual_paste_enabled: true
clipboard_intake_enabled: true
selected_text_extension_enabled: true
own_group_visible_intake_enabled: false
external_group_visible_intake_enabled: false
```

## What Each Mode Does

| Mode | Facebook Access | Auto-Actions | Risk |
|------|----------------|-------------|------|
| Manual Paste | None (operator copies) | None | None |
| Clipboard | None (OS clipboard) | None | None |
| Browser Selected Text | activeTab only, user click | None | None |
| Own Group Visible | Reads viewport, user click | None | Low |
| External Group | Would need to read other groups | None | Medium |

## Hard Forbidden (all modes)

- Credential storage
- Cookie reading/export
- Auto-scrolling
- Auto-posting
- Auto-commenting
- Auto-messaging
- Background scraping
- Profile data collection
