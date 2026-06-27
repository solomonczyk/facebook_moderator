# PROJECT_MEMORY — Canonical Source of Truth

> Last updated: 2026-06-27
> Project: Sezonski rad Srbija | Poslovi i iskustva radnika

This document is the single source of truth for the project state. A new AI session must be able to resume work by reading this document alone.

---

## 0. Project Identity

- **Name:** Facebook Group Admin Copilot
- **Group:** Sezonski rad Srbija | Poslovi i iskustva radnika
- **Facebook URL:** https://www.facebook.com/groups/992369183697618
- **Description:** AI-powered moderation assistant for a Facebook group helping seasonal workers in Serbia find jobs, share experiences, and avoid scams.
- **Mission:** Help seasonal workers find safer, clearer job information. Help honest employers publish clearer job offers. Reduce scams, spam, and unclear work conditions.
- **Current state:** Active development. VPS runtime operational. Operator-in-the-loop mode. DeepSeek V4-Pro active. No Facebook automation.

---

## 1. Vision

**Why the project exists:** Seasonal workers in Serbia (agriculture, construction) are vulnerable to scams, unclear working conditions, and misinformation on Facebook. The group helps workers help each other, but moderating it is time-consuming. The AI copilot reduces operator burden while keeping the human in control.

**Success:** Operator can moderate the group efficiently via Telegram with AI-prepared recommendations. Brain package is model-independent, reusable, and auditable. Workers receive safer, clearer job information. Employers publish more complete offers.

**Not the goal:** Full automation. Replacing human judgment. Scraping Facebook at scale. Building a job platform. Monetization.

---

## 2. Product

- **Product:** AI moderation copilot for Facebook group administrator.
- **Users:** 1 operator (group admin), ~group members (seasonal workers, employers).
- **Value:** Time saved on moderation, spam catch rate, structured job leads, safety first.
- **Core functions:**
  - Analyze incoming content (posts, comments, messages)
  - Classify content (employer job, worker request, spam, suspicious, review, question)
  - Extract structured fields (job type, location, pay, contact, conditions)
  - Assess risk (low / medium / high)
  - Recommend action (approve / edit / reject / escalate / mark_spam)
  - Prepare safe Serbian public text
  - Prepare Russian operator summary
  - Build daily digest of job leads
  - Send operator approval requests via Telegram
  - Maintain audit trail

---

## 3. Architecture

```
Facebook Group
     │
     ▼
Runtime Intake (browser extension / manual paste / own-group watcher)
     │
     ▼
Runtime Agent (queue, scheduler, policy engine)
     │
     ▼
Analyst Agent (brain — classification, extraction, risk, digest)
     │
     ▼
DeepSeek Brain (LLM — JSON contract, no markdown, no free text)
     │
     ▼
Queue → Telegram Bot (polling mode, inline keyboard approval)
     │
     ▼
Operator (approve / reject / edit / escalate)
     │
     ▼
Facebook Group (manual posting by operator)
```

### Layer descriptions

| Layer | Location | Purpose |
|-------|----------|---------|
| Runtime Intake | `backend/app/runtime_intake/` | Accept content from browser extension, manual paste, own-group watcher |
| Account Worker | `backend/app/account_worker/` | Browser session for Facebook interactions (OWN group only, read-only by default) |
| Runtime Agent | `backend/app/runtime_agent/` | Queue, scheduler, action execution, operator console, policy enforcement |
| Analyst Agent | `backend/app/analyst_agent/` | Brain pipeline: classify → extract → risk → digest → action |
| LLM Provider | `backend/app/llm/` | Provider-agnostic LLM client (DeepSeek primary), retry, cache, validation |
| Aggregator API | `backend/app/aggregator_api/` | FastAPI server, database, lead storage, normalize/dedup/freshness |
| Telegram Bot | `backend/app/telegram_bot/` | Operator approval via inline keyboard, polling mode |
| Brain Docs | `backend/brain/` | Canonical documentation package (model-independent) |
| Memory Engine | `backend/memory/` | Runtime memory storage for employers, workers, knowledge |

---

## 4. Current Runtime State

| Field | Value |
|-------|-------|
| Current branch | `master` |
| Current commit | `8455200` |
| DeepSeek status | Active (provider: deepseek, model: DeepSeek-V4-Pro) |
| LLM primary | deepseek |
| Regex-only mode | false |
| Fallback active | false |
| Telegram status | Active (polling mode, inline keyboard) |
| Queue status | Active |
| Audit status | Active |
| Digest status | Active (template ready, manual approval) |
| Safety gates | ALL disabled |
| Facebook auto-post | DISABLED |
| Facebook auto-comment | DISABLED |
| Facebook auto-message | DISABLED |
| Autonomous mode | DISABLED |
| Production accepted | false |
| Operator approval | REQUIRED |
| Draft only | true |

---

## 5. Accepted Architecture Decisions (ADR)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Facebook automation is forbidden | Safety. Operator must perform all Facebook actions manually. |
| ADR-002 | Operator is always final authority | Agent recommends, operator decides. Override is tracked in audit. |
| ADR-003 | Brain documentation is model-independent | Works with DeepSeek, GPT, Claude, local models. No provider lock-in. |
| ADR-004 | DeepSeek is primary LLM provider | Cost, capability, availability. |
| ADR-005 | JSON contract only — no markdown, no free text | Structured output for reliable parsing. No chain-of-thought exposure. |
| ADR-006 | Serbian for public text, Russian for operator summary | Group language policy. Operator preference. |
| ADR-007 | Safety first — when in doubt, escalate | Low confidence → operator. High risk → never publish. |
| ADR-008 | Telegram polling mode, not webhook | VPS without public domain. Simplifies infrastructure. |
| ADR-009 | Brain build system assembles SystemPrompt from canon files | Single-source-of-truth. Reproducible. Checksum-verified. |
| ADR-010 | Memory Engine for persistent knowledge | Employers, workers, locations indexed. Avoids re-analysis. |

---

## 6. Brain State

- **Brain version:** 1.0.0
- **Build date:** 2026-06-27
- **SystemPrompt:** 1626 lines, assembled from 14 source files

### Existing documents

```
backend/brain/
├── VERSION.md
├── README.md
├── CANON/
│   ├── 00_AGENT_CONSTITUTION.md    (93 lines)
│   ├── 01_OPERATOR_CHARTER.md      (71 lines)
│   ├── 02_GROUP_POLICY.md          (79 lines)
│   └── 03_SAFETY_MODEL.md          (100 lines)
├── KNOWLEDGE/
│   ├── Classification.md           (87 lines)
│   ├── Risk.md                     (38 lines)
│   ├── Extraction.md               (36 lines)
│   ├── Digest.md                   (51 lines)
│   ├── Languages.md                (43 lines)
│   ├── SerbianSeasonalWork.md      (63 lines)
│   └── EdgeCases.md                (95 lines)
├── PROMPTS/
│   ├── SystemPrompt.md             (1626 lines)
│   ├── FewShot.md                  (631 lines, 120 examples)
│   ├── NegativeExamples.md         (51 lines)
│   └── JsonContract.md             (59 lines)
├── TESTS/
│   ├── CanonTests.md
│   ├── DecisionTests.md
│   └── Acceptance.md
└── BUILD/
    ├── brain_builder.py
    ├── brain_loader.py
    ├── brain_validator.py
    ├── brain_manifest.yaml
    └── releases/
```

### Missing

- TASK 008C: Runtime integration tests for Brain
- TASK 008D: Brain version migration system

---

## 7. Runtime Components

| Component | Status | Purpose | Tests | Owner |
|-----------|--------|---------|-------|-------|
| `runtime_agent` | Active | Queue, scheduler, policy, operator console | backend/tests/ | — |
| `analyst_agent` | Active | Brain pipeline (classify, extract, risk, digest) | docs/audits/runtime-analyst-v1/ | — |
| `runtime_intake` | Active | Browser extension + manual paste intake | — | — |
| `account_worker` | Active (read-only) | Own-group watcher via Selenium | — | — |
| `aggregator_api` | Active | FastAPI, database, lead CRUD | — | — |
| `telegram_bot` | Active | Operator approval via polling | docs/audits/runtime-analyst-v1/ | — |
| `llm` | Active | DeepSeek client, retry, cache, validator | — | — |
| `brain/` (docs) | Active | Canonical Brain v1.0.0 package | backend/brain/TESTS/ | — |
| `memory/` | Active | Runtime Memory Engine v1.0.0 | — | — |
| `aggregator` | Active | Digest builder, risk scorer, dedup | — | — |
| `browser_extension` | Inactive | Facebook visible intake (005B) | — | — |

---

## 8. Active Tasks

| Task | Status | Description |
|------|--------|-------------|
| TASK 008A | ✅ Committed | Brain v1.0 Canon Package (commit: `8455200`) |
| TASK 008B | 🔵 In progress | PROJECT_MEMORY Canon System v1.0 |
| TASK 009A | ✅ Committed | Runtime Memory Engine v1.0 (commit: `732d42a`) |

---

## 9. Completed Tasks

| Task | Commit | Description |
|------|--------|-------------|
| 004Z | `bd10d8a` | Proof infrastructure |
| 005A | `146d324` | Runtime Agent Control Plane |
| 005B | `e441cb0` | Local Facebook Runtime Intake MVP |
| 005C | `a188664` | Own-group account worker with Selenium |
| 006C | `4100a6c` | Stabilize runtime analyst |
| 007A | `ace0a69` | FB Group Runtime Manager Agent V1 |
| 007B | `dbc5747` | DeepSeek Runtime Brain V1 |
| 007B-FIX | `ca3b53f` | Activate DeepSeek brain on VPS |
| 008A | `aaedd57` | Brain v1.0 Canon Package (initial) |
| 008A-FINAL | `8455200` | Brain v1.0 Canon Package (expanded FewShot) |
| 008B-BUILD | `9b4f42a` | Brain Build System & Release Pipeline |
| 009A | `732d42a` | Runtime Memory Engine v1.0 |

---

## 10. Known Problems

| # | Problem | Severity | Status |
|---|---------|----------|--------|
| 1 | No automated brain version migration | Medium | TODO (008D) |
| 2 | SystemPrompt.md manually rebuilt after FewShot changes | Low | Workaround: run `python backend/brain/BUILD/brain_builder.py` |
| 3 | Telegram token logging risk (httpx) | High | Mitigated: `df01890` suppresses httpx INFO |
| 4 | No production deploy pipeline | Medium | TODO |
| 5 | Browser extension not actively used | Low | Manual paste is primary intake |
| 6 | No end-to-end tests for brain pipeline | Medium | TODO |

---

## 11. Future Roadmap

| Priority | Item | Status |
|----------|------|--------|
| P0 | TASK 008B — PROJECT_MEMORY | 🔵 In progress |
| P1 | TASK 008C — Runtime integration tests for Brain | Not started |
| P1 | TASK 008D — Brain version migration system | Not started |
| P2 | TASK 009B — Memory Engine integration with analyst | Not started |
| P2 | Production deploy pipeline | Not started |
| P3 | Brain v1.1 (more edge cases, language improvements) | Not started |
| P3 | Multi-operator Telegram support | Not started |

---

## 12. Git State

| Field | Value |
|-------|-------|
| Branch | `master` |
| Latest commit | `8455200` |
| Latest commit message | feat: TASK 008A — FB Runtime Manager Brain v1.0 Canon Package |
| Git clean | Yes (except Obsidian workspace config) |
| Pushed | No |
| Last check | 2026-06-27 |

---

## 13. Directory Map

```
facebook_moderator/
├── backend/                        # Python backend (FastAPI)
│   ├── app/
│   │   ├── account_worker/         # Selenium-based Facebook account worker
│   │   ├── agents/                 # Runtime manager agent
│   │   ├── aggregator/             # Digest builder, risk scorer, dedup
│   │   ├── aggregator_api/         # FastAPI server, database, API
│   │   ├── analyst_agent/          # Brain pipeline (classify, extract, risk)
│   │   ├── llm/                    # Provider-agnostic LLM client
│   │   ├── runtime_agent/          # Queue, scheduler, policy, operator console
│   │   ├── runtime_intake/         # Browser extension + manual paste
│   │   ├── schemas/                # Shared data schemas
│   │   ├── services/               # Shared services
│   │   └── telegram_bot/           # Telegram operator approval bot
│   ├── brain/                      # Brain v1.0 Canon Package
│   │   ├── CANON/                  # Identity, mission, operator charter, safety
│   │   ├── KNOWLEDGE/              # Classification, risk, extraction, digest
│   │   ├── PROMPTS/                # SystemPrompt, FewShot, NegativeExamples, JsonContract
│   │   ├── TESTS/                  # Canon tests, decision tests, acceptance
│   │   └── BUILD/                  # Brain build system & releases
│   ├── memory/                     # Runtime Memory Engine v1.0
│   │   ├── ENGINE/                 # Memory engine and validator
│   │   ├── INDEX/                  # Location, name, phone indexes
│   │   └── SCHEMA/                 # Case, employer, worker, knowledge schemas
│   └── tests/                      # Backend tests
├── browser_extension/              # Chrome extension for Facebook intake
├── docs/
│   ├── architecture/               # Architecture decision documents
│   ├── audits/                     # Task proofs and audit reports
│   ├── operator/                   # Operator how-to guides
│   └── project/                    # PROJECT_MEMORY (this file)
├── scripts/                        # Build/validation scripts
├── sample_inputs/                  # Test sample inputs
├── sample_outputs/                 # Test sample outputs
├── tests/                          # TypeScript tests (vitest)
├── src/                            # TypeScript source (legacy)
└── sezonski-rad-ops/               # Obsidian vault (operator notes)
```

---

## 14. External Services

| Service | Purpose | Status |
|---------|---------|--------|
| DeepSeek API | Primary LLM provider (DeepSeek-V4-Pro) | Active |
| Telegram Bot API | Operator approval via inline keyboard | Active (polling) |
| Facebook | Group content source and target | Active (manual) |
| VPS | Hosting (backend runtime, no public domain) | Active |
| Obsidian | Operator notes vault (`sezonski-rad-ops/`) | Local |

---

## 15. Environment Variables

Required variables (values stored in `.env`, never committed):

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

All gates are **DISABLED** by default. Status as of 2026-06-27:

| Gate | Status | Description |
|------|--------|-------------|
| `facebook_account_worker_enabled` | DISABLED | Selenium account worker |
| `facebook_external_group_capture_enabled` | DISABLED | Capture from external groups |
| `facebook_own_group_capture_enabled` | DISABLED | Capture from own group |
| `facebook_auto_reply_enabled` | DISABLED | Auto-reply to posts |
| `facebook_auto_post_enabled` | DISABLED | Auto-post to group |
| `facebook_auto_comment_enabled` | DISABLED | Auto-comment on posts |
| `facebook_auto_message_enabled` | DISABLED | Auto-send messages |
| `captcha_bypass_enabled` | DISABLED | Captcha bypass (HARD FORBIDDEN) |
| `stealth_browser_enabled` | DISABLED | Stealth browser mode |
| `fake_account_enabled` | DISABLED | Fake accounts (HARD FORBIDDEN) |
| `review_auto_publish_enabled` | DISABLED | Auto-publish reviews |
| `production_accepted` | DISABLED | Production mode |

**Safe defaults active:**
- `operator_approval_required`: true
- `draft_only_by_default`: true
- `max_queue_items_per_run`: 50

---

## 17. Operator Workflow

```
1. Content arrives (manual paste, browser extension, or own-group watcher)
       │
2. Runtime Intake → normalizes, deduplicates, enriches
       │
3. Runtime Agent → queues, prioritizes
       │
4. Analyst Agent → runs Brain pipeline:
   ├── classify (9 categories)
   ├── extract (12 fields)
   ├── assess risk (low / medium / high)
   ├── recommend action
   ├── prepare Serbian public text
   ├── prepare Russian operator summary
   └── prepare reply to author
       │
5. Queue → Telegram Bot → sends to operator:
   ├── Russian summary
   ├── Risk level + confidence
   ├── Recommended action
   ├── Prepared text (editable)
   └── Inline keyboard: [Approve] [Edit] [Reject] [Escalate]
       │
6. Operator decides:
   ├── Approve → operator manually posts to Facebook
   ├── Edit → operator modifies text, then posts
   ├── Reject → content not published
   └── Escalate → operator handles personally
       │
7. Audit log records decision for all future analysis
```

---

## 18. Conversation Changelog

Recent project changes (last 20):

1. **2026-06-27** — TASK 008A: Brain v1.0 Canon Package expanded (FewShot 120 examples, SystemPrompt 1626 lines)
2. **2026-06-26** — TASK 009A: Runtime Memory Engine v1.0
3. **2026-06-26** — TASK 008B: Brain Build System & Release Pipeline
4. **2026-06-26** — TASK 008A: Brain v1.0 Canon Package initial
5. **2026-06-25** — TASK 007B-FIX: Activate DeepSeek brain on VPS
6. **2026-06-25** — TASK 007B: DeepSeek Runtime Brain V1
7. **2026-06-25** — TASK 007A: FB Group Runtime Manager Agent V1
8. **2026-06-25** — TASK 006C: Stabilize runtime analyst
9. **2026-06-25** — Telegram bot async polling fix
10. **2026-06-25** — Suppress httpx logging to prevent token in journal
11. **2026-06-24** — TASK 006B: Analyst agent proof + VPS smoke test
12. **2026-06-24** — TASK 006B: Autonomous Analyst Agent with security gates
13. **2026-06-24** — TASK 006A-LIVE: Telegram mobile approval bot
14. **2026-06-23** — VPS deployment with port conflict protection
15. **2026-06-23** — TASK 005C: Own-group account worker with real Selenium
16. **2026-06-22** — TASK 005B: Local Facebook Runtime Intake MVP
17. **2026-06-22** — TASK 005A: Runtime Agent Control Plane
18. **2026-06-21** — TASK 004Z: Proof infrastructure
19. **2026-06-21** — Initial commit: Facebook Group Admin Copilot + Seasonal Work Aggregator
20. **2026-06-21** — Project inception

---

## 19. Session Resume

> What an AI needs to know to continue work after a month away.

**Project:** Facebook Group Admin Copilot for "Sezonski rad Srbija" — an AI moderation assistant that analyzes Facebook group content, classifies it, extracts structured job data, assesses risk, and prepares safe Serbian-language posts. Operator-in-the-loop. Never autonomous.

**Current state (2026-06-27):**
- Branch `master`, commit `8455200`. Not pushed.
- VPS runtime operational. Backend is Python FastAPI. DeepSeek-V4-Pro is primary LLM.
- Telegram bot active (polling mode) for operator approval.
- All dangerous gates DISABLED. No Facebook automation.
- Brain v1.0.0 documented in `backend/brain/` with 120 few-shot examples.
- Memory Engine v1.0.0 in `backend/memory/`.
- Build system: run `python backend/brain/BUILD/brain_builder.py` to rebuild SystemPrompt.md from source files.

**What's done:**
- Brain canon package complete (CANON, KNOWLEDGE, PROMPTS, TESTS)
- LLM provider layer (DeepSeek active, model-independent)
- Runtime agent with queue, scheduler, policy engine
- Analyst agent pipeline (classify → extract → risk → digest)
- Telegram approval bot with inline keyboard
- Runtime intake (manual paste + browser extension adapter)
- Account worker (own-group watcher, read-only Selenium)
- Aggregator API (FastAPI + SQLite)
- Memory Engine (employer/worker/knowledge storage with indexes)

**What's next:**
- TASK 008B: PROJECT_MEMORY (this task — in progress)
- TASK 008C: Runtime integration tests for Brain
- TASK 008D: Brain version migration system
- Production deploy pipeline

**Key constraints:**
- Never push without explicit request.
- Never enable Facebook automation gates.
- Never store or read API keys.
- Brain docs are model-independent.
- Serbian for public text, Russian for operator summary.
- JSON contract only — no markdown output from LLM.

**To continue:** Read this file. Check `backend/brain/PROMPTS/SystemPrompt.md` for the current LLM system prompt. Check git log for recent changes. Run the brain builder if source files changed.
