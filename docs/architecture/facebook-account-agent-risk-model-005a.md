---
type: architecture
section: facebook_risk_model
task: TASK-005A
date: 2026-06-26
status: all_modes_disabled_by_default
---

# Facebook Account Agent — Risk Model

## Mode 1: Safe Draft (default, active)

**What it does:**
- Operator pastes text via clipboard or types manually
- Agent classifies content
- Agent creates DB records
- Agent generates draft replies and posts
- Operator manually copies and publishes

**Risk:** None. No Facebook access.

**Default:** This is the only active mode.

## Mode 2: Assisted Own-Group (disabled)

**What it does:**
- Agent monitors only operator-visible own-group content
- Content comes from operator's own browser (copy-paste or browser extension text selection)
- Agent creates drafts and action queue items
- Operator approves each action
- Agent prepares text but does NOT submit automatically

**Risk:** None. Still requires operator to publish.

**Gate:** `facebook_own_group_capture_enabled: false`

## Mode 3: Account Browser Worker (disabled, high-risk)

**What it does:**
- Agent uses a logged-in browser session on operator's device
- Reads visible content from own Facebook group
- May prepare own-group replies and posts
- Does NOT post to external groups
- Does NOT send messages
- Does NOT extract credentials or cookies
- Rate-limited
- Full audit log
- Operator can pause or kill the worker at any time

**What it does NOT do:**
- No external group posting
- No auto-messaging
- No credential extraction
- No cookie export
- No captcha bypass
- No stealth/anti-detection
- No fake accounts
- No auto-joining groups

**Risk:** Medium. Requires operator's browser to be open and logged in. Operator must trust the local worker.

**Gate:** `facebook_account_worker_enabled: false`

## Hard Forbidden (all modes, permanent)

```text
captcha_bypass
stealth_evasion
fake_accounts
credential_extraction
cookie_export_to_remote
private_member_data_collection
fake_vacancies
fake_reviews
auto_posting_to_external_groups
auto_messaging_employers_or_workers
```

## Enabling a Mode

To enable Mode 2 or Mode 3:

1. Operator reads this risk document
2. Operator explicitly sets the gate to `true`
3. Operator confirms in the audit log
4. Gate change is logged immutably
5. Operator can disable at any time

No gate may be enabled by the agent itself.
