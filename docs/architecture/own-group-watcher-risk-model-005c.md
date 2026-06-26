---
type: architecture
section: risk_model
task: TASK-005C
date: 2026-06-26
---

# Own Group Watcher — Risk Model

## Risk Level: Low-Medium

The worker operates on the operator's own device, own browser, own group.

## Mitigations

| Risk | Mitigation |
|------|-----------|
| Accidental posting | Worker has no submit capability |
| Over-scrolling | Rate limiter: max 2 scrolls, 15s between |
| Duplicate processing | SHA256 content hashing |
| Runaway worker | Emergency stop flag |
| Credential theft | No credential storage, manual login only |
| External group access | URL validation — own group ID only |
| Cookie export | Not implemented, forbidden |
| Captcha | Not bypassed, worker pauses if detected |

## What could go wrong and how we handle it

1. **Worker runs too fast** → Rate limiter blocks
2. **Worker sees the same post twice** → Seen store deduplicates
3. **Worker encounters a login wall** → Pauses, signals operator
4. **Operator wants to stop immediately** → Emergency stop
5. **Browser crashes** → Worker detects, logs, stops gracefully
