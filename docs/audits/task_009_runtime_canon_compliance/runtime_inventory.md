# Runtime Inventory

> Complete module inventory of `backend/app/`. 60+ Python files, 8 components.

## Components

### 1. Runtime Agent (`backend/app/runtime_agent/`) — CENTRAL ORCHESTRATOR
- `config.py` (59 lines) — RuntimeConfig dataclass, all safety gates (disabled), HARD_FORBIDDEN list, `is_gate_enabled()`
- `agent_core.py` (145 lines) — RuntimeAgent main pipeline: validate → classify → store → queue
- `action_queue.py` (139 lines) — In-memory ActionQueue with approve/reject/edit/spam state machine
- `policy.py` (44 lines) — PolicyEngine enforces gates, `requires_operator_approval()` always True
- `brain.py` (232 lines) — Deterministic rule-based classifier (Serbian regex patterns)
- `tools.py` (77 lines) — AgentTools wraps LeadService, generates digests, exports Obsidian
- `events.py` (73 lines) — RuntimeEvent dataclass, EventType enum
- `memory.py` (23 lines) — LRU AgentMemory (max 100 items)
- `audit_log.py` (46 lines) — Immutable AuditLog
- `scheduler.py` (27 lines) — TaskScheduler for daily digest
- `api.py` (145 lines) — FastAPI router: /events, /queue, /queue/{id}/approve/reject/edit, /status, /digest/run
- `operator_console.py` (24 lines) — Summary view of pending queue items
- **Tests:** 6 files (policy_gates, action_queue, audit_log, agent_core, integration with intake)

### 2. Analyst Agent (`backend/app/analyst_agent/`) — AUTONOMOUS DECISION ENGINE
- `analyst_core.py` (185 lines) — Pipeline: sanitize → analyze → risk → policy validate → execute/escalate. Gated by `autonomous_mode_enabled`
- `brain.py` (244 lines) — Deterministic classifier, JSON-safe parser, prompt-injection defense
- `config.py` (46 lines) — AnalystConfig, kill switch, `can_operate()` pre-flight check
- `policy.py` (156 lines) — FINAL authority: 26-item HARD_FORBIDDEN set, action allowlist
- `risk_scorer.py` (62 lines) — Risk 0-100 based on action type, missing info, spam flags
- `audit.py` (64 lines) — Immutable AnalystAudit
- `api.py` (80 lines) — FastAPI router: /status, /process-queue, /analyze-item, /kill-switch, /audit
- `telegram_escalation.py` (87 lines) — Raw httpx Telegram send (bypasses telegram_bot module)
- **Tests:** 1 file (19 tests: config, policy, brain, risk scorer, audit)

### 3. Telegram Bot (`backend/app/telegram_bot/`) — OPERATOR INTERFACE
- `bot.py` (395 lines) — Full bot: /status, /queue, /digest, /addlead, inline keyboard [Approve][Edit][Reject][Spam]
- **Tests:** None (0 test files)

### 4. LLM Client (`backend/app/llm/`) — PROVIDER LAYER
- `config.py` (28 lines) — LLMConfig, loads from env, defaults to DeepSeek-V4-Pro
- `client.py` (128 lines) — Anthropic SDK wrapper, cache-first, retry pipeline
- `provider.py` (16 lines) — LLMResponse dataclass
- `cache.py` (53 lines) — SHA256 LRU cache (500 entries)
- `retry.py` (49 lines) — Exponential backoff with JSON validation
- `validator.py` (49 lines) — JSON extraction, markdown stripping, schema validation
- **Tests:** None (0 test files)

### 5. Runtime Intake (`backend/app/runtime_intake/`) — CONTENT INGESTION
- `intake_service.py` (52 lines) — Wraps RuntimeAgent.process_event(), guarded by IntakeConfig
- `intake_models.py` (64 lines) — Request/response dataclasses
- `event_mapper.py` (75 lines) — Maps intake payloads to RuntimeEvent
- `config.py` (46 lines) — IntakeConfig, safety gates (clipboard_intake_enabled=True by default — FINDING-007)
- `audit.py` (38 lines) — IntakeAudit
- `manual_paste_api.py` (105 lines) — FastAPI router: /manual-paste, /browser-selection, /clipboard, /visible-group
- `clipboard_intake.py` (37 lines) — Platform-specific clipboard reading (PowerShell/pbpaste/xclip)
- `browser_event_adapter.py` (23 lines) — Browser payload validation
- `own_group_visible_adapter.py` (37 lines) — Guarded adapter for own-group capture
- **Tests:** 3 files (event_mapper, policy_gates, runtime_agent_integration)

### 6. Account Worker (`backend/app/account_worker/`) — SELENIUM BROWSER
- `browser_session.py` (136 lines) — Chrome via Selenium, visible-only, headless FORBIDDEN
- `config.py` (87 lines) — WorkerConfig, `can_start()` pre-flight blocks dangerous gates
- `content_extractor.py` (59 lines) — HTML text extraction, SHA256 dedup
- `emergency_stop.py` (40 lines) — Emergency stop flag
- `event_sender.py` (37 lines) — CapturedItem → RuntimeEvent conversion
- `own_group_watcher.py` (121 lines) — Full capture pipeline orchestrator
- `rate_limiter.py` (38 lines) — Rolling 1-hour rate limit
- `seen_store.py` (34 lines) — SHA256 dedup (1000 items)
- `worker_api.py` (74 lines) — FastAPI router: start/stop/pause/resume/emergency-stop/run-once
- `worker_service.py` (60 lines) — Bridges watcher with runtime agent
- `worker_models.py` (38 lines) — State machine enums
- `audit.py` (36 lines) — WorkerAudit
- **Tests:** 7 files (config, seen_store, content_extractor, event_sender, rate_limiter, emergency_stop, smoke_test)

### 7. Aggregator (`backend/app/aggregator/`) — DATA MODELS & PROCESSING
- `models.py` (279 lines) — JobLead, EmployerProfile, WorkerProfile, Review, 15 enums
- `lead_normalizer.py` (102 lines) — Raw text → JobLead normalization
- `duplicate_detector.py` (57 lines) — Phone/URL/text similarity dedup
- `freshness_scorer.py` (42 lines) — Freshness scoring (today/stale >7d)
- `risk_scorer.py` (76 lines) — Risk flags, LOW/MEDIUM/HIGH/REJECT
- `digest_builder.py` (109 lines) — Daily digest markdown builder
- `moderation_queue.py` (86 lines) — In-memory moderation workflow
- `schemas.py` (70 lines) — Dictionary schema validation
- **Tests:** 6 files (models, digest, dedup, freshness, normalize, risk)

### 8. Aggregator API (`backend/app/aggregator_api/`) — FASTAPI SERVER
- `main.py` (130 lines) — Entry point, registers all routers, starts Telegram bot thread
- `api.py` (147 lines) — Leads CRUD, digest, obsidian export
- `database.py` (23 lines) — SQLite via SQLAlchemy
- `db_models.py` (159 lines) — ORM models
- `repositories.py` (135 lines) — CRUD operations
- `service.py` (214 lines) — Full intake pipeline, moderation with override protection
- `obsidian_export.py` (71 lines) — Obsidian markdown export
- **Tests:** 4 files (database_schema, obsidian_export, lead_service, duplicate_storage)

### Additional
- `backend/app/agents/facebook_runtime_manager.py` (233 lines) — LLM-powered multi-step pipeline
- `backend/app/agents/manager_api.py` (41 lines) — /manager/analyze, /manager/status
- `backend/app/schemas/runtime_manager.py` (83 lines) — Pydantic models, forbidden words validator
- `backend/app/services/llm_client.py` (140 lines) — Legacy Anthropic-only client

## Test Coverage Summary
- **30 test files total.** All tests pass with `PYTHONPATH=backend`.
- **0 tests for:** telegram_bot, llm client (new), llm client (legacy services/), all API routers
- **Best tested:** analyst_agent (19 tests), account_worker (7 test files), aggregator (6 test files)
