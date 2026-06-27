# PROJECT_MEMORY — Canonical Source of Truth

> Last updated: 2026-06-27
> Project: Sezonski rad Srbija | Poslovi i iskustva radnika

This document is the single source of truth for current project state. A new AI session begins here.

**Permanent rules:** [PROJECT_CANON/](PROJECT_CANON/)
**Future plans:** [ROADMAP.md](ROADMAP.md)
**History:** [CHANGELOG.md](CHANGELOG.md)

---

## AI START HERE

**Current goal:** TASK 008C — PROJECT_CANON Foundation v1.0. Create permanent architecture rules layer, extract roadmap and changelog from PROJECT_MEMORY, add AI START HERE section.

**Current runtime:**
- Branch: `master`, commit: `33681e7`
- VPS operational. DeepSeek-V4-Pro active. Telegram polling active.
- All dangerous gates DISABLED. Operator approval REQUIRED.
- Not pushed.

**Current versions:**
- Brain: 1.0.0
- Memory Engine: 1.0.0
- PROJECT_CANON: 1.0.0
- Runtime API: 0.2.1

**Current priorities:**
1. TASK 008C — PROJECT_CANON (in progress)
2. TASK 008D — Brain version migration
3. TASK 009B — Memory Engine integration
4. Integration tests for brain pipeline

**Current blockers:** None.

**Where to continue:**
1. Read this file fully.
2. Check [PROJECT_CANON/](PROJECT_CANON/) for permanent rules.
3. Check `backend/brain/PROMPTS/SystemPrompt.md` for current LLM system prompt.
4. Check `git log --oneline -5` for recent changes.
5. Run `python backend/brain/BUILD/brain_builder.py` if brain sources changed.
6. Complete the active task above. Update this file when done.

---

## 0. Project Identity

- **Name:** Facebook Group Admin Copilot
- **Group:** Sezonski rad Srbija | Poslovi i iskustva radnika
- **Facebook URL:** https://www.facebook.com/groups/992369183697618
- **Description:** AI-powered moderation assistant for a Facebook group helping seasonal workers in Serbia find jobs, share experiences, and avoid scams.
- **Mission:** Help seasonal workers find safer, clearer job information. Help honest employers publish clearer job offers. Reduce scams, spam, and unclear work conditions.
- **Current phase:** Project infrastructure (PROJECT_CANON, PROJECT_MEMORY).

---

## 1. Vision

**Why:** Seasonal workers in Serbia are vulnerable to scams and unclear conditions. The group helps them help each other, but moderation is time-consuming. The AI copilot reduces operator burden while keeping the human in control.

**Success:** Operator moderates efficiently via Telegram with AI-prepared recommendations. Brain is model-independent, reusable, auditable. Workers receive safer, clearer information.

**Not the goal:** Full automation. Replacing human judgment. Facebook scraping at scale. Job platform. Monetization.

---

## 2. Product

AI moderation copilot for Facebook group administrator.
- **Users:** 1 operator (group admin), ~group members
- **Core functions:** Analyze, classify, extract, risk-assess, recommend action, prepare Serbian text, prepare Russian summary, build digest, send Telegram approval requests, audit trail
- **Value:** Time saved, spam caught, structured leads, safety first

---

## 3. Architecture

See [PROJECT_CANON/ARCHITECTURE.md](PROJECT_CANON/ARCHITECTURE.md) for detailed diagrams.

```
Facebook Group → Runtime Intake → Runtime Agent → Analyst Agent
→ DeepSeek Brain (LLM) → Queue → Telegram Bot → Operator → Facebook Group
```

| Layer | Location | Purpose |
|-------|----------|---------|
| Runtime Intake | `backend/app/runtime_intake/` | Content ingestion (manual paste, extension, watcher) |
| Account Worker | `backend/app/account_worker/` | Selenium Facebook session (read-only by default) |
| Runtime Agent | `backend/app/runtime_agent/` | Queue, scheduler, policy, operator console |
| Analyst Agent | `backend/app/analyst_agent/` | Brain pipeline: classify → extract → risk → digest |
| LLM Provider | `backend/app/llm/` | Provider-agnostic client (DeepSeek primary) |
| Aggregator API | `backend/app/aggregator_api/` | FastAPI server, SQLite, lead storage |
| Telegram Bot | `backend/app/telegram_bot/` | Operator approval via polling inline keyboard |
| Brain Docs | `backend/brain/` | Model-independent brain v1.0.0 package |
| Memory Engine | `backend/memory/` | Runtime memory v1.0.0 (employer/worker/knowledge) |

---

## 4. Current Runtime State

| Field | Value |
|-------|-------|
| Current branch | `master` |
| Current commit | `33681e7` |
| DeepSeek status | Active (provider: deepseek, model: DeepSeek-V4-Pro) |
| LLM primary | deepseek |
| Regex-only mode | false |
| Fallback active | false |
| Telegram status | Active (polling mode, inline keyboard) |
| Queue status | Active |
| Audit status | Active |
| Digest status | Active (template ready, manual approval) |
| All safety gates | DISABLED |
| Facebook automation | ALL DISABLED |
| Autonomous mode | DISABLED |
| Production accepted | false |
| Operator approval | REQUIRED |
| Draft only | true |
| Pushed | No |

---

## 5. Architecture Decisions (ADR)

Full decisions: [PROJECT_CANON/ADR.md](PROJECT_CANON/ADR.md). Summary:

| ADR | Decision |
|-----|----------|
| ADR-001 | Facebook automation forbidden |
| ADR-002 | Operator is final authority |
| ADR-003 | Brain is model-independent |
| ADR-004 | PROJECT_MEMORY stores runtime state |
| ADR-005 | PROJECT_CANON stores permanent rules |
| ADR-006 | DeepSeek is primary LLM provider |
| ADR-007 | Runtime uses JSON contract |
| ADR-008 | Safety over speed |
| ADR-009 | No hallucinated facts |
| ADR-010 | Dangerous gates disabled by default |
| ADR-011 | One task = one feature |
| ADR-012 | Telegram polling mode |

---

## 6. Brain State

- **Version:** 1.0.0
- **SystemPrompt:** 1626 lines, assembled from 14 source files
- **Build command:** `python backend/brain/BUILD/brain_builder.py`
- **Structure:**
  - `CANON/` — 4 files (constitution, operator charter, group policy, safety model)
  - `KNOWLEDGE/` — 7 files (classification, risk, extraction, digest, languages, domain vocab, edge cases)
  - `PROMPTS/` — 4 files (SystemPrompt, FewShot 120 examples, NegativeExamples, JsonContract)
  - `TESTS/` — 3 files (canon tests, decision tests, acceptance)
  - `BUILD/` — builder, loader, validator, manifest, releases

---

## 7. Runtime Components

| Component | Status | Purpose |
|-----------|--------|---------|
| `runtime_agent` | Active | Queue, scheduler, policy, operator console |
| `analyst_agent` | Active | Brain pipeline (classify, extract, risk, digest) |
| `runtime_intake` | Active | Browser extension + manual paste intake |
| `account_worker` | Active (read-only) | Own-group watcher via Selenium |
| `aggregator_api` | Active | FastAPI, database, lead CRUD |
| `telegram_bot` | Active | Operator approval via polling |
| `llm` | Active | DeepSeek client, retry, cache, validator |
| `brain/` | Active | Canonical Brain v1.0.0 package |
| `memory/` | Active | Runtime Memory Engine v1.0.0 |
| `aggregator` | Active | Digest builder, risk scorer, dedup |
| `browser_extension` | Inactive | Facebook visible intake |

---

## 8. Active Tasks

| Task | Status | Description |
|------|--------|-------------|
| TASK 008C | 🔵 In progress | PROJECT_CANON Foundation v1.0 |

---

## 9. Completed Tasks

| Task | Commit | Description |
|------|--------|-------------|
| 006C | `4100a6c` | Stabilize runtime analyst |
| 007A | `ace0a69` | FB Group Runtime Manager Agent V1 |
| 007B | `dbc5747` | DeepSeek Runtime Brain V1 |
| 007B-FIX | `ca3b53f` | Activate DeepSeek brain on VPS |
| 008A | `8455200` | Brain v1.0 Canon Package (expanded FewShot, 120 examples) |
| 008B-BUILD | `9b4f42a` | Brain Build System & Release Pipeline |
| 009A | `732d42a` | Runtime Memory Engine v1.0 |
| 008B | `33681e7` | PROJECT_MEMORY Canon System v1.0 |

Full history: [CHANGELOG.md](CHANGELOG.md)

---

## 10. Known Problems

| # | Problem | Severity | Status |
|---|---------|----------|--------|
| 1 | No automated brain version migration | Medium | TODO |
| 2 | SystemPrompt must be manually rebuilt after source changes | Low | Run `brain_builder.py` |
| 3 | Telegram token logging risk (httpx) | High | Mitigated (httpx INFO suppressed) |
| 4 | No production deploy pipeline | Medium | TODO |
| 5 | No end-to-end tests for brain pipeline | Medium | TODO |
| 6 | Browser extension not actively used | Low | Manual paste primary |

---

## 11. Roadmap Summary

See [ROADMAP.md](ROADMAP.md) for full roadmap.

| Priority | Next items |
|----------|------------|
| P0 | TASK 008C — PROJECT_CANON Foundation |
| P1 | TASK 008D — Brain version migration, TASK 009B — Memory integration, integration tests |
| P2 | Deploy pipeline, health checks, multi-operator, digest auto-gen |
| P3 | Brain v1.1, Cyrillic support, more languages, dashboard |

---

## 12. Git State

| Field | Value |
|-------|-------|
| Branch | `master` |
| Latest commit | `33681e7` |
| Latest message | feat: TASK 008B — PROJECT_MEMORY Canon System v1.0 |
| Git clean | Yes (except Obsidian workspace config) |
| Pushed | No |
| Last check | 2026-06-27 |

---

## 13. Directory Map

See [PROJECT_CANON/DIRECTORY_STANDARD.md](PROJECT_CANON/DIRECTORY_STANDARD.md) for full map with rules.

```
facebook_moderator/
├── backend/                    # Python backend (FastAPI)
│   ├── app/                    # Application code (10 components)
│   ├── brain/                  # Brain v1.0.0 Canon Package
│   └── memory/                 # Memory Engine v1.0.0
├── browser_extension/          # Chrome extension (inactive)
├── docs/
│   ├── architecture/           # Historical architecture docs
│   ├── audits/                 # Task proofs
│   ├── operator/               # Operator guides
│   └── project/                # PROJECT_CANON, PROJECT_MEMORY, ROADMAP, CHANGELOG
├── sezonski-rad-ops/           # Obsidian vault (operator notes)
└── src/ tests/ scripts/        # Legacy TypeScript
```

---

## 14. External Services

| Service | Purpose | Status |
|---------|---------|--------|
| DeepSeek API | Primary LLM (DeepSeek-V4-Pro) | Active |
| Telegram Bot API | Operator approval via inline keyboard | Active (polling) |
| Facebook | Group content source/target | Active (manual) |
| VPS | Backend hosting (no public domain) | Active |
| Obsidian | Operator notes vault | Local |

---

## 15. Environment Variables

Required (values in `.env`, never committed):

```
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
LLM_MAX_TOKENS
LLM_TEMPERATURE
LLM_TIMEOUT
TELEGRAM_BOT_TOKEN
TELEGRAM_OPERATOR_CHAT_ID
```

---

## 16. Dangerous Gates

All gates DISABLED. Full policy: [PROJECT_CANON/DEVELOPMENT_STANDARD.md](PROJECT_CANON/DEVELOPMENT_STANDARD.md)

| Gate | Status |
|------|--------|
| `facebook_account_worker_enabled` | DISABLED |
| `facebook_auto_post_enabled` | DISABLED |
| `facebook_auto_comment_enabled` | DISABLED |
| `facebook_auto_message_enabled` | DISABLED |
| `captcha_bypass_enabled` | DISABLED (HARD FORBIDDEN) |
| `stealth_browser_enabled` | DISABLED |
| `fake_account_enabled` | DISABLED (HARD FORBIDDEN) |
| `review_auto_publish_enabled` | DISABLED |
| `production_accepted` | DISABLED |

Safe defaults: `operator_approval_required` = true, `draft_only_by_default` = true.

---

## 17. Operator Workflow

See [PROJECT_CANON/ARCHITECTURE.md](PROJECT_CANON/ARCHITECTURE.md) for diagram.

1. Content arrives → Intake normalizes
2. Queue schedules → Analyst processes
3. Brain pipeline: classify → extract → risk → recommend
4. Telegram sends to operator: Russian summary + risk + action + [Approve/Edit/Reject/Escalate]
5. Operator decides → audit logged → memory updated
6. If approved → operator manually posts to Facebook

---

## 18. Recent Changes

Last 10 major updates. Full history: [CHANGELOG.md](CHANGELOG.md)

1. **2026-06-27** — TASK 008C: PROJECT_CANON Foundation v1.0 (in progress)
2. **2026-06-27** — TASK 008B: PROJECT_MEMORY Canon System v1.0
3. **2026-06-27** — TASK 008A-FINAL: Brain v1.0 expanded (120 examples, 1626-line SystemPrompt)
4. **2026-06-26** — TASK 009A: Runtime Memory Engine v1.0
5. **2026-06-26** — TASK 008B-BUILD: Brain Build System & Release Pipeline
6. **2026-06-25** — TASK 007B-FIX: Activate DeepSeek brain on VPS
7. **2026-06-25** — TASK 007B: DeepSeek Runtime Brain V1
8. **2026-06-25** — TASK 007A: FB Group Runtime Manager Agent V1
9. **2026-06-25** — TASK 006C: Stabilize runtime analyst
10. **2026-06-24** — Telegram mobile approval bot + security gates

---

## 19. Session Resume

> What an AI needs to know to continue work after a month away.

**Project:** Facebook Group Admin Copilot for "Sezonski rad Srbija" — AI moderation assistant. Operator-in-the-loop. Never autonomous.

**Current state (2026-06-27):**
- Branch `master`, commit `33681e7`. Not pushed.
- VPS operational. Python FastAPI backend. DeepSeek-V4-Pro primary LLM.
- Telegram bot active (polling). All dangerous gates DISABLED.
- Brain v1.0.0 in `backend/brain/`. Memory Engine v1.0.0 in `backend/memory/`.
- PROJECT_CANON v1.0.0 in `docs/project/PROJECT_CANON/` — permanent rules.
- PROJECT_MEMORY in `docs/project/PROJECT_MEMORY.md` — current state (this file).

**What's done:**
- Brain canon package (CANON, KNOWLEDGE, PROMPTS 120 examples, TESTS)
- LLM provider layer (DeepSeek active, model-independent)
- Runtime agent (queue, scheduler, policy engine)
- Analyst agent pipeline (classify → extract → risk → digest)
- Telegram approval bot (inline keyboard, polling)
- Runtime intake (manual paste + browser extension adapter)
- Account worker (own-group watcher, read-only Selenium)
- Aggregator API (FastAPI + SQLite)
- Memory Engine (employer/worker/knowledge with indexes)
- PROJECT_CANON (architecture, ADR, workflow, standards, versioning)

**What's next:**
- TASK 008C: PROJECT_CANON (this task — in progress)
- TASK 008D: Brain version migration system
- TASK 009B: Memory Engine integration with analyst
- Integration tests for brain pipeline
- Production deploy pipeline

**Key constraints:**
- Never push without explicit request.
- Never enable Facebook automation gates.
- Never store or read API keys.
- Brain docs are model-independent.
- Serbian for public text, Russian for operator summary.
- JSON contract only — no markdown output from LLM.

**To continue:** Read this file. Check [PROJECT_CANON/](PROJECT_CANON/). Check `backend/brain/PROMPTS/SystemPrompt.md` for LLM prompt. Check `git log` for recent changes. Run brain builder if brain sources changed.
