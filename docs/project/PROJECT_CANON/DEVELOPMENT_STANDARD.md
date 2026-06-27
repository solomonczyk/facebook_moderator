# DEVELOPMENT_STANDARD.md — Coding and Task Standards

> Part of PROJECT_CANON. Defines how development is done.

---

## Core Rules

### One Task = One Feature

Each task implements exactly one feature, subsystem, or document package. Tasks are numbered sequentially (`TASK NNN` or `TASK NNN-letter`). Tasks must not mix concerns.

### Tests Mandatory

Every task must include tests:
- **Feature code:** Python tests in `backend/tests/` or inline test assertions
- **Documentation tasks:** Structure/content verification in `TESTS/` directory
- **Infrastructure tasks:** Smoke test or proof of operation

### Proof Mandatory

Every task must produce:
- `docs/audits/<task-name>/proof.json` — machine-readable completion proof
- `docs/audits/<task-name>/implementation-report.md` — human-readable summary

### Git Clean Mandatory

Before commit:
- Working tree must be clean relative to task scope
- No unrelated files staged
- No `.env` or secrets staged
- No `__pycache__` or build artifacts staged

---

## Dangerous Gates

These gates control risky capabilities. Default state: **ALL DISABLED**.

| Gate | Default | Can be enabled? |
|------|---------|-----------------|
| `facebook_auto_post_enabled` | false | Only with explicit operator approval |
| `facebook_auto_comment_enabled` | false | Only with explicit operator approval |
| `facebook_auto_message_enabled` | false | Only with explicit operator approval |
| `captcha_bypass_enabled` | false | **NEVER** (HARD FORBIDDEN) |
| `stealth_browser_enabled` | false | Only with explicit operator approval |
| `fake_account_enabled` | false | **NEVER** (HARD FORBIDDEN) |
| `production_accepted` | false | Only with explicit operator approval |

**Rule:** No task may enable a dangerous gate without explicit operator instruction. HARD FORBIDDEN gates can never be enabled.

---

## Operator Review

- All content destined for Facebook must pass operator review
- Agent recommendations are advisory, not binding
- Operator can override any agent decision
- Override is logged in audit trail

---

## Production Gate

`production_accepted` is the master switch for production behavior:
- When `false`: draft mode, all outputs are drafts, no Facebook writes
- When `true`: operator-approved content may be published (still not automated)
- Setting to `true` requires explicit operator command

---

## Code Style

### Python (backend/)
- Follow PEP 8
- Docstrings for public functions
- Type hints where practical
- Logging: use `logging.getLogger("sezonski.<component>")`
- Config: use dataclasses, load from env

### Markdown (docs/)
- Use `#` hierarchy (no level skip)
- Code blocks with language tag
- Tables with aligned columns
- Links to other project files with relative paths

### File Naming
- Python: `snake_case.py`
- Markdown: `PascalCase.md` for canon docs, `kebab-case.md` for task docs
- Directories: `snake_case/` for code, `kebab-case/` for docs

---

## Environment Variables

- Never hardcode values
- Use `.env` file (gitignored)
- Reference via `os.getenv("VAR", default)`
- Never commit `.env`
- List required vars in PROJECT_MEMORY (names only, no values)

---

## Brain Build System

When brain source files change:
```bash
python backend/brain/BUILD/brain_builder.py
```
This regenerates:
- `PROMPTS/SystemPrompt.md`
- `BUILD/releases/brain-<version>.md`
- `BUILD/releases/brain-<version>.json`
- `BUILD/releases/latest.json`
