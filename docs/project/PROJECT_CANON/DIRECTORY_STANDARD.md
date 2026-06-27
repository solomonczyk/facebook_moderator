# DIRECTORY_STANDARD.md — Project Directory Structure

> Part of PROJECT_CANON. Defines the meaning of every top-level directory.

---

## Directory Map

```
facebook_moderator/                # Project root
│
├── backend/                       # Python backend (primary runtime)
│   ├── app/                       # Application code
│   │   ├── account_worker/        # Selenium Facebook session (own-group watcher)
│   │   ├── agents/                # Runtime manager agent definitions
│   │   ├── aggregator/            # Digest builder, risk scorer, dedup, normalize
│   │   ├── aggregator_api/        # FastAPI server, database (SQLite), REST API
│   │   ├── analyst_agent/         # Brain pipeline: classify → extract → risk → digest
│   │   ├── llm/                   # Provider-agnostic LLM client (DeepSeek primary)
│   │   ├── runtime_agent/         # Queue, scheduler, policy engine, operator console
│   │   ├── runtime_intake/        # Content ingestion (manual paste, extension, watcher)
│   │   ├── schemas/               # Shared Pydantic data models
│   │   ├── services/              # Shared service layer
│   │   └── telegram_bot/          # Telegram operator approval bot (polling)
│   ├── brain/                     # Brain v1.0 Canon Package
│   │   ├── CANON/                 # Agent identity, mission, safety, policy
│   │   ├── KNOWLEDGE/             # Classification, risk, extraction, digest, languages
│   │   ├── PROMPTS/               # SystemPrompt, FewShot, NegativeExamples, JsonContract
│   │   ├── TESTS/                 # Canon tests, decision tests, acceptance
│   │   └── BUILD/                 # Brain build system and release artifacts
│   ├── memory/                    # Runtime Memory Engine v1.0
│   │   ├── ENGINE/                # Memory engine, validator
│   │   ├── INDEX/                 # Location, name, phone indexes (JSON)
│   │   └── SCHEMA/                # Case, employer, worker, knowledge JSON schemas
│   └── tests/                     # Backend Python tests
│
├── browser_extension/             # Chrome extension for Facebook visible intake
│
├── docs/                          # All project documentation
│   ├── architecture/              # Historical architecture docs (004A–005C era)
│   ├── audits/                    # Task proofs and audit reports
│   │   ├── brain-build/           # Brain build system proof
│   │   ├── brain-v1/              # Brain v1.0 canon package proof
│   │   ├── memory-v1/             # Memory engine proof
│   │   ├── project-canon/         # PROJECT_CANON proof
│   │   ├── project-memory/        # PROJECT_MEMORY proof
│   │   ├── runtime-analyst-v1/    # Runtime analyst test proofs
│   │   ├── runtime-brain-v1-activation/  # DeepSeek activation proof
│   │   └── runtime-manager-agent-v1/     # Runtime manager proof
│   ├── operator/                  # Operator how-to guides
│   └── project/                   # Project management docs
│       ├── PROJECT_MEMORY.md      # Current project state (canonical source of truth)
│       ├── PROJECT_CANON/         # Permanent project rules
│       ├── ROADMAP.md             # Future plans
│       └── CHANGELOG.md           # Project history
│
├── sample_inputs/                 # Test sample inputs
├── sample_outputs/                # Test sample outputs
├── scripts/                       # Build and validation scripts
├── src/                           # TypeScript source (legacy copilot, pre-Python migration)
├── tests/                         # TypeScript tests (vitest, legacy)
├── sezonski-rad-ops/              # Obsidian vault (operator personal notes)
│
├── .env                           # Environment variables (NEVER COMMITTED)
├── .gitignore                     # Git ignore rules
├── package.json                   # Node.js dependencies (legacy copilot + scripts)
├── tsconfig.json                  # TypeScript config (legacy)
├── MODERATION_POLICY.md           # Human-readable moderation policy
├── SYSTEM_PROMPT.md               # Legacy system prompt (superseded by brain/)
├── TEST_CASES.md                  # Legacy test cases (superseded by brain/TESTS/)
└── README.md                      # Project README
```

---

## Directory Rules

### Backend (`backend/`)
- All runtime code lives here
- Python 3.12+
- FastAPI framework
- SQLite database
- Each subdirectory in `app/` is an independent component

### Brain (`backend/brain/`)
- Model-independent documentation
- Source of truth for agent behavior
- Built into SystemPrompt.md by brain_builder.py
- Versioned independently (semver)

### Docs (`docs/`)
- `architecture/` — historical, rarely updated (pre-CANON era)
- `audits/` — one directory per task, contains proof artifacts
- `project/` — PROJECT_CANON, PROJECT_MEMORY, ROADMAP, CHANGELOG
- `operator/` — operator-facing guides

### Tests
- `backend/tests/` — Python backend tests
- `tests/` — TypeScript tests (legacy)
- Brain tests: `backend/brain/TESTS/`

---

## Anti-Patterns

- ❌ Don't put runtime code in `docs/`
- ❌ Don't put documentation in `backend/app/`
- ❌ Don't mix Python and TypeScript in the same test directory
- ❌ Don't create top-level directories without updating this file
