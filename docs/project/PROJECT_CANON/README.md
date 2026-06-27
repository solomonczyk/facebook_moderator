# PROJECT_CANON — Permanent Rules Layer

> Version: 1.0.0
> Created: 2026-06-27
> Project: Sezonski rad Srbija | Poslovi i iskustva radnika

## What This Is

PROJECT_CANON contains the **permanent rules** of the project. These rules change rarely and only through deliberate decisions.

PROJECT_CANON does **not** store state — that is PROJECT_MEMORY's job.

## Document Map

| Document | Purpose | Changes |
|----------|---------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, layers, data flow | Rare (major refactors) |
| [ADR.md](ADR.md) | Accepted Architecture Decisions | Append-only |
| [AI_WORKFLOW.md](AI_WORKFLOW.md) | AI development lifecycle | Stable |
| [DEVELOPMENT_STANDARD.md](DEVELOPMENT_STANDARD.md) | Coding and task standards | Rare |
| [DOCUMENT_POLICY.md](DOCUMENT_POLICY.md) | Document hierarchy and responsibilities | Rare |
| [DIRECTORY_STANDARD.md](DIRECTORY_STANDARD.md) | Project directory structure | When structure changes |
| [RELEASE_POLICY.md](RELEASE_POLICY.md) | Release stages and gates | Rare |
| [VERSIONING.md](VERSIONING.md) | Version numbering rules | Rare |

## Relationship to PROJECT_MEMORY

```
PROJECT_CANON/     ← permanent rules (what and why)
PROJECT_MEMORY.md  ← current state (what now)
ROADMAP.md         ← future plans (what next)
CHANGELOG.md       ← history (what happened)
```

## Principles

1. **Canon is law.** All development must follow PROJECT_CANON rules.
2. **Canon changes require explicit decision.** No accidental edits.
3. **Canon is compact.** Each document covers one topic. No duplication.
4. **Canon is model-independent.** Works for human and AI readers.
5. **Canon is versioned.** Changes increment canon version.
