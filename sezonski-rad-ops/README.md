---
type: readme
project: sezonski-rad-ops
version: 0.1.0
updated: 2026-06-26
---

# Sezonski Rad Ops — Obsidian Operations Vault

## Overview

This is the operations layer for the Facebook group **"Sezonski rad Srbija | Poslovi i iskustva radnika"**.

It is an Obsidian vault that serves as the **single source of truth** for:
- Vacancy tracking
- Worker requests
- Employer reviews
- Outreach campaigns
- Publication queue
- Moderation cases
- Daily/weekly reporting

**Every Facebook action is manual.** The vault tracks what needs to be done and records what was done. Nothing is automated.

---

## Quick Start

1. Open this folder as an **Obsidian vault**.
2. Install the **Dataview** plugin (community plugin).
3. Start with `00-dashboard.md` — it shows queues, tasks, and KPIs.
4. Follow `01-daily-workflow.md` for the daily routine.
5. Read `02-rules.md` for operating rules.
6. Read `03-risk-policy.md` for risk and escalation.

---

## Daily Routine

### Morning — Sourcing
- Find 10–20 vacancies from external sources.
- Create a file in `vacancies/` from `_template-vacancy.md`.
- Set `status: new`.

### Day — Outreach
- Select 3–5 groups from `outreach/target-groups/`.
- Prepare messages from `templates/<language>/`.
- Manually send messages.
- Log actions in `outreach/daily-logs/`.

### Evening — Publishing
- Select 1–3 posts to publish.
- Run through Admin Copilot (parent project).
- Manually publish to Facebook.
- Update status and add `facebook_post_url`.

### End of Day — Report
- Fill in daily report from `reports/_template-daily-report.md`.
- Update KPIs in dashboard.

---

## Structure

| Directory | Purpose |
|-----------|---------|
| `vacancies/` | Job ads found and being prepared |
| `workers/` | Workers looking for jobs |
| `reviews/` | Worker reviews of employers |
| `employers/` | Employer profiles |
| `outreach/` | Groups to contact + contact logs |
| `moderation/` | Moderation cases (queue + resolved) |
| `post-queue/` | Posts to publish (ready/posted/rejected) |
| `templates/` | Multilingual message templates |
| `reports/` | Daily and weekly report templates |

---

## Languages

Templates available in 5 languages:
- 🇷🇸 Serbian (primary)
- 🇷🇺 Russian
- 🇺🇦 Ukrainian
- 🇭🇺 Hungarian
- 🇷🇴 Romanian

---

## Key Principles

1. **Operator-in-the-Loop** — All Facebook actions are manual.
2. **Single Source of Truth** — Obsidian vault only. No Notion. No Google Sheets CRM.
3. **Manual Gates** — `operator_approved: true` required before any publication.
4. **No Fake Content** — No fake reviews, no fake vacancies, no auto-generated content.
5. **Trust First** — Every published post protects the group's trust.

---

## Status

**ACCEPTED FOR MANUAL OPS MVP**

`production_accepted: false` — requires operator validation on real cases.

---

## Related

- [Admin Copilot](../SYSTEM_PROMPT.md) — AI moderation assistant
- [Moderation Policy](../MODERATION_POLICY.md) — Full moderation rules
