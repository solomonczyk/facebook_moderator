---
type: architecture
section: facebook_capture
task: TASK-004A
date: 2026-06-26
status: disabled_by_default
---

# Facebook Capture — Risk Model

## Default: DISABLED

```yaml
facebook_capture_enabled: false
```

## What Is Allowed (when enabled)

The operator may use a **local browser-side visible capture** tool that:

1. Runs on the operator's own device only
2. Requires the operator to be manually logged into Facebook in their browser
3. Does NOT extract or store credentials
4. Does NOT export cookies
5. Does NOT use headless browsers or VPS
6. Does NOT bypass captchas
7. Does NOT use anti-detection / stealth techniques
8. Does NOT auto-post
9. Does NOT auto-comment
10. Does NOT auto-message
11. Does NOT auto-join groups
12. Captures ONLY: visible post text, screenshot reference, group name, post date, post URL
13. Rate-limits: max 1 group per 5 minutes, max 10 posts per session
14. Operator can pause/stop at any time
15. All captured content goes to moderation queue — never auto-published

## What Is FORBIDDEN (permanently)

1. Facebook cookie extraction or session theft
2. Headless Facebook login bot
3. VPS-based Facebook scraping with stolen cookies
4. Captcha bypass services
5. Anti-detection / stealth browser evasion
6. Fake Facebook accounts
7. Auto-joining Facebook groups from fake accounts
8. Auto-posting in external Facebook groups
9. Auto-commenting in external Facebook groups
10. Auto-messaging employers or workers
11. Collecting private member profile data
12. Storing Facebook credentials
13. Exporting Facebook cookies to another machine
14. Running capture on a server/VPS without operator's physical device
15. Bypassing Facebook rate limits

## Why These Restrictions Exist

1. **Account safety**: The operator's Facebook account must not be banned.
2. **Legal compliance**: Unauthorized scraping violates Facebook ToS and Serbian data protection law.
3. **Group reputation**: The "Sezonski rad Srbija" group must not be associated with spam or bot activity.
4. **Trust**: The platform's core value is trust. Automation that looks like spam destroys trust.

## Implementation Requirements

If Facebook visible capture is ever enabled:

- Must be a browser extension or local script, NOT a cloud service
- Must show a visible indicator when capture is active
- Must allow the operator to review every captured item before it enters the pipeline
- Must log all capture actions with timestamps
- Must have an emergency stop button
- Must NOT run in the background — operator must initiate each capture session

## Gate

```yaml
facebook_capture_enabled: false
requires_operator_device: true
requires_operator_login_in_browser: true
stores_credentials: false
stores_cookies: false
auto_actions: false
output_to_moderation_queue: true
operator_can_pause_stop: true
rate_limited: true
```
