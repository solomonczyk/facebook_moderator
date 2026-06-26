---
type: architecture
task: TASK-004A
version: 0.1.0
date: 2026-06-26
status: draft
production_accepted: false
---

# Seasonal Work Aggregator — Architecture

## Project

Sezonski rad Srbija | Poslovi i iskustva radnika

## Core Business Goal

Fresh seasonal job market feed + trust layer for workers and employers in Serbia.

## Strategic Shift

The project is no longer just a Facebook group. Facebook is a **temporary acquisition channel**, not the source of truth. The system must become a standalone aggregator that collects, normalizes, deduplicates, scores, and publishes seasonal job leads from any source — with Facebook being one of many inputs.

---

## Architecture Layers

### Layer 1 — Lead Aggregator MVP (current)

```
[Sources] → [Intake] → [Normalizer] → [Dedup] → [Freshness/Risk Score] → [Digest Builder] → [Export]
                                                                                  ↓
                                                                           [Moderation Queue]
```

Components:
- Source-agnostic intake (public web, operator screenshots, Telegram, forms)
- Normalized lead schema
- Duplicate detection
- Freshness scoring
- Risk scoring
- Daily digest generator
- Obsidian/Markdown export
- Moderation queue

### Layer 2 — Employer/Worker Directory (next)

```
[Leads] → [Employer Extractor] → [Employer Profile DB]
       → [Worker Extractor]   → [Worker Profile DB]
                                     ↓
                              [Contact History]
                              [Job History]
```

### Layer 3 — Ratings and Reviews (after directory)

```
[Worker Review Form] → [Moderation] → [Public Trust Score]
[Employer Reply Form] → [Moderation] → [Rating Breakdown]
```

### Layer 4 — Self-Sustaining Marketplace (final)

```
[Employer Posting Form] → [Auto-digest]
[Worker Application]    → [Matchmaking]
                         [Facebook = traffic source only]
```

---

## System Boundaries

### What the system DOES

- Collects seasonal job leads from multiple public and operator-provided sources
- Normalizes them into a consistent schema
- Detects duplicates across sources
- Scores freshness and risk
- Builds daily digests for the Facebook group
- Builds employer and worker profiles from accumulated data
- Accepts reviews through moderated forms
- Exports to Obsidian-compatible Markdown

### What the system DOES NOT do

- Does NOT log into Facebook automatically
- Does NOT use cookies, sessions, or credentials from the operator
- Does NOT run headless browsers for Facebook
- Does NOT auto-post, auto-comment, or auto-message
- Does NOT create fake vacancies or reviews
- Does NOT bypass captchas or anti-bot protection
- Does NOT collect private member data
- Does NOT publish reviews without moderation

---

## Component Overview

| Component | Responsibility | Status |
|-----------|---------------|--------|
| Lead Intake | Accept leads from any source | Designed |
| Lead Normalizer | Convert any format → normalized schema | Designed |
| Duplicate Detector | Phone, location, text, image matching | Designed |
| Freshness Scorer | fresh_today through stale_over_7_days | Designed |
| Risk Scorer | 12 risk flags, low/medium/high/reject | Designed |
| Digest Builder | 3–10 leads + disclaimer + missing info | Designed |
| Moderation Queue | Review, approve, reject, escalate | Designed |
| Post Queue | Ready → Posted → Rejected | Designed |
| Employer Profile | Aggregate from leads + reviews | Designed |
| Worker Profile | Aggregate from submissions + reviews | Designed |
| Review Engine | Category ratings + moderation + right of reply | Designed |
| Obsidian Export | Markdown + YAML frontmatter | Designed |

---

## Facebook Capture Model

See: [facebook-capture-risk-model-004a.md](facebook-capture-risk-model-004a.md)

Default: **DISABLED**.

When enabled (operator decision only):
- Runs on operator's device only
- Operator manually logged into Facebook in browser
- No credential extraction
- No cookie export
- Captures only: visible post text, screenshot, group name, post date, post URL
- Rate-limited
- Operator can pause/stop
- All output goes to moderation queue — never auto-published

---

## Dangerous Gates

All dangerous actions are **disabled by default**:

```yaml
facebook_capture_enabled: false
external_group_auto_posting: forbidden
auto_commenting: forbidden
auto_messaging: forbidden
review_publication: moderation_required
employer_rating_publication: moderation_required
worker_rating_publication: moderation_required
production_accepted: false
```

No gate may be enabled without explicit operator confirmation.

---

## Source Types

| Type | Description | Auto? | Status |
|------|-------------|-------|--------|
| public_web | Public job boards, classifieds, news | Semi (web search + manual review) | Active |
| facebook_operator_screenshot | Operator copies from FB | Manual | Active |
| facebook_visible_capture | Browser-side visible-only capture | Semi (operator device) | Disabled by default |
| telegram_submission | TG bot/channel submits a lead | Semi | Designed |
| employer_form | Employer posts directly | Auto (moderated) | Designed |
| worker_form | Worker submits profile | Auto (moderated) | Designed |
| own_group_comment | Comments in own FB group | Manual | Active |
| own_group_post | Posts in own FB group | Manual | Active |
| manual_admin_entry | Admin types a lead | Manual | Active |

---

## Next Steps

1. **TASK 004B**: Implement Lead Intake API + normalized database schema (Python)
2. **TASK 004C**: Implement duplicate detector + freshness/risk scorers
3. **TASK 004D**: Implement digest builder + Obsidian export
4. **TASK 004E**: Employer/Worker directory
5. **TASK 004F**: Reviews and ratings engine
