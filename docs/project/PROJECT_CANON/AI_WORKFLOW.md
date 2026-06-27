# AI_WORKFLOW.md — AI Development Lifecycle

> Part of PROJECT_CANON. Defines the standard workflow for all AI-assisted development.

---

## Complete Workflow

```
IDEA / TASK REQUEST
     │
     ▼
TASK DEFINITION
  ├── Verdict: NEEDS IMPLEMENTATION
  ├── Goal: clear one-sentence description
  ├── Scope: allowed / forbidden
  ├── Required output: files, structure, format
  ├── Tests: acceptance criteria
  └── Git: commit message template
     │
     ▼
EXPLORE (read-only)
  ├── Read relevant code, docs, git history
  ├── Understand current state from PROJECT_MEMORY
  ├── Check PROJECT_CANON for applicable rules
  └── Identify gaps and dependencies
     │
     ▼
IMPLEMENT (write)
  ├── Create / modify files
  ├── Follow DEVELOPMENT_STANDARD.md
  ├── Match surrounding code style
  ├── No forbidden changes (see task scope)
  └── Run brain builder if brain sources changed
     │
     ▼
TEST
  ├── Verify files exist
  ├── Verify content matches requirements
  ├── Run security checks (no secrets, no .env)
  ├── Run git status (clean working tree for task files)
  └── Verify acceptance criteria
     │
     ▼
PROOF
  ├── Create proof.json in docs/audits/<task-name>/
  ├── Create implementation-report.md
  └── Verify proof matches delivery
     │
     ▼
COMMIT
  ├── git add <task files only>
  ├── git commit -m "feat: TASK NNN — <description>"
  ├── End with: Co-Authored-By: Claude <noreply@anthropic.com>
  └── Never push without explicit request
     │
     ▼
UPDATE PROJECT_MEMORY
  ├── Update Current Runtime State
  ├── Update Active Tasks / Completed Tasks
  ├── Update Brain Version (if changed)
  ├── Update Git State (commit hash)
  ├── Update Conversation Changelog
  ├── Update Known Problems
  └── Update Session Resume
     │
     ▼
NEXT SESSION READY
  └── New AI reads PROJECT_MEMORY → immediately knows state
```

---

## Task States

| State | Meaning |
|-------|---------|
| NEEDS IMPLEMENTATION | Task defined, not started |
| IN PROGRESS | Currently implementing |
| COMMITTED | Code committed, not pushed |
| ACCEPTED | Operator reviewed, accepted |
| REJECTED | Operator reviewed, rejected |
| DEFERRED | Postponed to later milestone |

---

## Commit Rules

1. **One task = one commit.** No mixed commits.
2. **Commit message format:** `feat: TASK NNN — <one-line description>`
3. **Co-author trailer required:** `Co-Authored-By: Claude <noreply@anthropic.com>`
4. **Push forbidden** unless explicitly requested by operator.
5. **Amend allowed** for proof.json updates within same task.

---

## Forbidden Actions During Implementation

1. Modify runtime behavior (unless task explicitly allows)
2. Change LLM provider configuration
3. Change Telegram bot logic
4. Change queue logic
5. Enable autonomous mode
6. Enable Facebook automation gates
7. Touch `.env` or API keys
8. Push to remote
9. Modify files outside task scope
10. Use `--force` with git

---

## Security Check Checklist

Before every commit:

```bash
# 1. Check git status
git status --short

# 2. Scan diff for secrets
git diff --cached | grep -Ei "sk-|api_key|token|secret|authorization"

# 3. Verify .env not tracked
git ls-files .env

# 4. Verify no dangerous gate changes
git diff --cached -- "*config.py" | grep -i "enabled.*true"
```

If any check fails → stop immediately, fix, do not commit.

---

## After Task Completion

1. Update PROJECT_MEMORY.md with new state
2. Update ROADMAP.md if priorities changed
3. Update CHANGELOG.md with one-line entry
4. Run brain builder if brain sources changed
5. Verify git clean (task files only)
6. Report delivery to operator
