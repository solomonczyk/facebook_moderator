# ARCHITECTURE.md — System Architecture

> Part of PROJECT_CANON. Defines the permanent system architecture.

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                     FACEBOOK GROUP                       │
│   Sezonski rad Srbija | Poslovi i iskustva radnika      │
└──────────┬──────────────────────────────────┬───────────┘
           │ content in                       │ content out
           ▼                                  ▲
┌──────────────────────┐          ┌───────────────────────┐
│   RUNTIME INTAKE     │          │    OPERATOR (human)    │
│   browser extension  │          │    manual post         │
│   manual paste       │          │    manual edit         │
│   own-group watcher  │          │    manual reject       │
└──────────┬───────────┘          └───────────┬───────────┘
           │ lead                             │ decision
           ▼                                  ▲
┌──────────────────────────────────────────────────────────┐
│                    RUNTIME AGENT                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  INTAKE  │  │  QUEUE   │  │ ANALYST  │  │ OPERATOR │ │
│  │  SERVICE │──│ SCHEDULER│──│  AGENT   │──│ CONSOLE  │ │
│  └──────────┘  └──────────┘  └─────┬────┘  └─────┬────┘ │
│                                    │              │      │
│                     ┌──────────────┘              │      │
│                     ▼                             │      │
│              ┌─────────────┐                      │      │
│              │  LLM LAYER  │                      │      │
│              │  DeepSeek   │                      │      │
│              └──────┬──────┘                      │      │
│                     │ JSON response               │      │
│                     ▼                             │      │
│              ┌─────────────┐                      │      │
│              │  VALIDATOR  │                      │      │
│              └──────┬──────┘                      │      │
│                     │ validated decision          │      │
│                     ▼                             ▼      │
│              ┌──────────────────────────────────────────┐│
│              │           TELEGRAM BOT                    ││
│              │      (polling, inline keyboard)           ││
│              └──────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
           │                                    ▲
           ▼                                    │
┌──────────────────────┐            ┌──────────────────────┐
│   AGGREGATOR API     │            │    MEMORY ENGINE     │
│   FastAPI + SQLite   │◄──────────►│  employer / worker   │
│   digest / normalize │            │  knowledge / index   │
└──────────────────────┘            └──────────────────────┘
```

---

## Runtime Architecture

### Runtime Agent (`backend/app/runtime_agent/`)

The central orchestrator. Manages:
- **Action Queue:** FIFO queue of pending items awaiting operator decision
- **Scheduler:** Prioritizes items, batches digest candidates
- **Policy Engine:** Enforces dangerous gates and safety constraints
- **Operator Console:** Tracks operator decisions and overrides
- **Audit Log:** Immutable record of all agent decisions
- **Events:** Internal event bus for cross-component communication

### Analyst Agent (`backend/app/analyst_agent/`)

The brain pipeline. Transforms raw content into structured decisions:
1. **Sanitize:** Remove markup, normalize whitespace
2. **Classify:** Determine content type (9 categories)
3. **Extract:** Pull structured fields (12 fields)
4. **Risk:** Score low / medium / high
5. **Recommend:** Propose action
6. **Prepare:** Serbian public text, Russian summary, reply

### Runtime Intake (`backend/app/runtime_intake/`)

Content ingestion layer:
- **Manual Paste API:** Operator pastes text via API
- **Browser Extension Adapter:** Receives events from Chrome extension
- **Own-Group Watcher Adapter:** Receives events from Selenium watcher
- **Event Mapper:** Normalizes all intake into standard Lead format

### Account Worker (`backend/app/account_worker/`)

Selenium-based Facebook session:
- **Own Group Watcher:** Monitors own group for new content
- **Read-only by default:** No write actions without operator approval
- **Rate Limiter:** Respects Facebook rate limits
- **Emergency Stop:** Kills all browser sessions on critical error
- **Seen Store:** Tracks already-processed content

---

## Queue Architecture

```
INTAKE → NORMALIZE → DEDUP → ENRICH → QUEUE → PRIORITIZE → ANALYZE → TELEGRAM
                                                                         │
                                                                   ┌─────┴─────┐
                                                                   │  APPROVE  │
                                                                   │   EDIT    │
                                                                   │  REJECT   │
                                                                   │ ESCALATE  │
                                                                   └───────────┘
```

Queue items flow:
1. Content ingested → normalized to Lead format
2. Duplicate detection → seen before? skip
3. Enrichment → add location context, memory lookups
4. Queue insertion → FIFO with priority overrides
5. Analyst processing → Brain pipeline
6. Telegram delivery → operator notification
7. Operator decision → audit logged, memory updated

---

## Telegram Architecture

```
BACKEND (127.0.0.1)                    TELEGRAM CLOUD
     │                                       │
     │  python-telegram-bot (polling)        │
     │  getUpdates() ──────────────────────► │
     │  ◄────────────────────── messages     │
     │                                       │
     │  sendMessage() ─────────────────────► │
     │  editMessageReplyMarkup() ──────────► │
     │                                       │
     ▼                                       ▼
OPERATOR PHONE                        TELEGRAM API
```

- **Mode:** Long polling (no webhook, no public domain)
- **Auth:** `TELEGRAM_BOT_TOKEN` + `TELEGRAM_OPERATOR_CHAT_ID`
- **Messages:** Inline keyboard with callback data
- **Safety:** httpx INFO logging suppressed to prevent token in journal

---

## LLM Architecture

```
ANALYST AGENT
     │
     ▼
LLM PROVIDER LAYER (`backend/app/llm/`)
     │
     ├── config.py     → load from env, provider-agnostic
     ├── client.py     → HTTP client (DeepSeek Anthropic-compatible endpoint)
     ├── provider.py   → provider dispatch (deepseek / anthropic / openai)
     ├── retry.py      → exponential backoff, timeout handling
     ├── cache.py      → response cache for identical inputs
     └── validator.py  → JSON schema validation, fallback classifier
     │
     ▼
DEEPSEEK API (api.deepseek.com/anthropic)
     │
     ▼
JSON RESPONSE → validated → analyst decision
```

Provider configuration:
- `LLM_PROVIDER=deepseek`
- `LLM_MODEL=DeepSeek-V4-Pro`
- `LLM_BASE_URL=https://api.deepseek.com/anthropic`
- Anthropic-compatible Messages API

---

## Document Hierarchy

```
PROJECT_CANON/ARCHITECTURE.md  ← this file (permanent architecture)
         │
         ▼
backend/brain/PROMPTS/SystemPrompt.md  ← assembled LLM prompt (1626 lines)
         │
         ├── CANON/    ← agent identity, safety, policy
         ├── KNOWLEDGE/← classification, risk, extraction, digest
         └── PROMPTS/  ← few-shot, negative examples, JSON contract
```

---

## Data Flow

```
RAW CONTENT (Facebook post / comment / message)
     │
     ▼
SANITIZE → remove markup, normalize whitespace, strip PII hints
     │
     ▼
CLASSIFY → 1 of 9 categories (employer_job_post, worker_request, spam, ...)
     │
     ▼
EXTRACT → 12 structured fields (job_type, location, pay, contact, ...)
     │
     ▼
RISK → low / medium / high (based on flags, missing info, patterns)
     │
     ▼
RECOMMEND → approve / approve_with_edits / reject / ask_missing_info / mark_spam / escalate
     │
     ▼
PREPARE → Serbian public text + Russian operator summary + reply to author
     │
     ▼
VALIDATE → JSON schema check, forbidden words check, confidence check
     │
     ▼
QUEUE → Telegram → OPERATOR DECISION → audit log + memory update
```

---

## Operator Workflow

```
1. Content arrives → intake normalizes
2. Queue schedules → analyst processes
3. Brain classifies → extracts → risk → recommends
4. Telegram sends → operator sees:
   ├── Russian summary (1-2 sentences)
   ├── Risk level + confidence
   ├── Recommended action
   ├── Prepared Serbian text (editable)
   └── [Approve] [Edit] [Reject] [Escalate]
5. Operator decides → action executed or escalated
6. Audit log updated → memory engine updated
7. If approved: operator manually posts to Facebook
```

---

## Safety Architecture

```
EVERY ACTION ──► DANGEROUS GATE CHECK ──► DISABLED? → BLOCK
                                              │
                                         ENABLED?
                                              │
                                    ┌─────────┴─────────┐
                                    │ OPERATOR APPROVAL  │
                                    │     REQUIRED?      │
                                    └─────────┬─────────┘
                                         YES  │  NO (never)
                                              │
                                         ┌────┴────┐
                                         │ TELEGRAM│
                                         │ APPROVAL│
                                         └────┬────┘
                                              │
                                    ┌─────────┴─────────┐
                                    │   AUDIT LOGGED    │
                                    └──────────────────┘
```

All dangerous gates are DISABLED. Operator approval is REQUIRED. Actions are logged.
