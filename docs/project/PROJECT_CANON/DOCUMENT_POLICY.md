# DOCUMENT_POLICY.md — Document Hierarchy and Responsibilities

> Part of PROJECT_CANON. Defines the project documentation system.

---

## Document Hierarchy

```
                         ┌─────────────────────┐
                         │   BRAIN CANON        │
                         │   backend/brain/     │
                         │   Agent rules        │
                         │   (model-independent)│
                         └──────────┬──────────┘
                                    │ feeds into
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                    PROJECT_CANON                              │
│                    docs/project/PROJECT_CANON/                │
│                    Permanent project rules                    │
│                                                              │
│  ARCHITECTURE.md    ADR.md    AI_WORKFLOW.md                  │
│  DEVELOPMENT_STANDARD.md    DOCUMENT_POLICY.md               │
│  DIRECTORY_STANDARD.md    RELEASE_POLICY.md    VERSIONING.md │
└──────────────────────────────┬───────────────────────────────┘
                               │ rules govern
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    PROJECT_MEMORY                             │
│                    docs/project/PROJECT_MEMORY.md             │
│                    Current project state                      │
│                    (updated after every task)                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
   ┌────────────┐    ┌──────────────┐    ┌──────────────┐
   │  ROADMAP   │    │  CHANGELOG   │    │  SESSION     │
   │  .md       │    │  .md         │    │  RESUME      │
   │  Future    │    │  History     │    │  AI start    │
   └────────────┘    └──────────────┘    └──────────────┘
```

---

## Layer Responsibilities

### Brain Canon (`backend/brain/`)

**What:** Agent identity, safety rules, classification logic, extraction rules, digest rules, language policy, examples, JSON contract.

**Responsibility:** Define how the agent thinks and behaves. Model-independent. Used as source material for SystemPrompt assembly.

**Who edits:** AI (with operator approval for content changes). Operator (for policy changes).

**Update frequency:** When agent behavior changes (new classification, new safety rule, new edge case).

### PROJECT_CANON (`docs/project/PROJECT_CANON/`)

**What:** Permanent project rules — architecture, ADRs, workflow, coding standards, document policy, directory structure, release policy, versioning.

**Responsibility:** Define how the project is built and maintained. Changes require explicit decision.

**Who edits:** AI (proposing). Operator (approving).

**Update frequency:** Rare (major architectural shifts, new ADRs, process changes).

### PROJECT_MEMORY (`docs/project/PROJECT_MEMORY.md`)

**What:** Current project state — branch, commit, runtime status, active tasks, completed tasks, known problems, session resume.

**Responsibility:** Be the single file a new AI session reads to understand current state.

**Who edits:** AI (after every task). Operator (for manual state changes).

**Update frequency:** After every task.

### ROADMAP (`docs/project/ROADMAP.md`)

**What:** Future plans — prioritized task list, milestones, long-term vision items.

**Responsibility:** Track what comes next. PROJECT_MEMORY keeps only a summary.

**Who edits:** AI (as tasks complete). Operator (for priority changes).

**Update frequency:** When tasks complete or priorities shift.

### CHANGELOG (`docs/project/CHANGELOG.md`)

**What:** Project history — all completed tasks with dates, commits, descriptions.

**Responsibility:** Full history. PROJECT_MEMORY keeps only last 10–20 entries.

**Who edits:** AI (after every task).

**Update frequency:** After every task.

---

## Anti-Duplication Rule

Never store the same information in two places:

| If you need... | Look in... |
|----------------|------------|
| Agent rules | `backend/brain/CANON/` |
| Project rules | `docs/project/PROJECT_CANON/` |
| Current state | `docs/project/PROJECT_MEMORY.md` |
| History | `docs/project/CHANGELOG.md` |
| Future plans | `docs/project/ROADMAP.md` |
| Task proof | `docs/audits/<task>/` |

---

## Document Lifecycle

```
CREATE → fill with accurate content
     │
     ▼
MAINTAIN → update after each relevant change
     │
     ▼
PRUNE → remove outdated info
     │
     ▼
ARCHIVE → move to docs/archive/ (rare)
```
