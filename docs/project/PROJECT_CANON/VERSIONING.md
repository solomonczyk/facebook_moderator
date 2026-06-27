# VERSIONING.md — Version Numbering Rules

> Part of PROJECT_CANON. Defines how project artifacts are versioned.

---

## Versioned Artifacts

| Artifact | Current Version | Location | Scheme |
|----------|----------------|----------|--------|
| Brain | 1.0.0 | `backend/brain/VERSION.md` | SemVer |
| Memory Engine | 1.0.0 | `backend/memory/VERSION.md` | SemVer |
| PROJECT_CANON | 1.0.0 | `docs/project/PROJECT_CANON/README.md` | SemVer |
| PROJECT_MEMORY | (by date) | `docs/project/PROJECT_MEMORY.md` | Last-updated date |
| Runtime | 0.2.1 | `backend/app/aggregator_api/main.py` | SemVer (API version) |

---

## Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └── Backward-compatible fixes, typos, clarifications
  │     │
  │     └──────── New backward-compatible functionality, new documents
  │
  └────────────── Breaking changes, incompatible format changes
```

---

## Brain Version Rules

**MAJOR bump when:**
- JSON contract changes incompatibly
- Classification categories change
- Risk model fundamentally changes
- SystemPrompt structure is reorganized

**MINOR bump when:**
- New knowledge documents added
- New edge cases covered
- Few-shot examples expanded
- New language support

**PATCH bump when:**
- Typos and wording fixes
- Example corrections
- Build system fixes that don't change output

---

## Memory Engine Version Rules

**MAJOR bump when:**
- Schema format changes incompatibly
- Index structure changes

**MINOR bump when:**
- New schema types added
- New index types added

**PATCH bump when:**
- Engine bug fixes
- Performance improvements

---

## PROJECT_CANON Version Rules

**MAJOR bump when:**
- Architecture fundamentally changes
- ADRs are removed or contradicted
- Development standards are rewritten

**MINOR bump when:**
- New ADRs added
- New canon documents added
- Existing documents expanded

**PATCH bump when:**
- Typos, formatting, clarifications

---

## PROJECT_MEMORY Version Rules

PROJECT_MEMORY is not semantically versioned. It tracks state by date (`Last updated: YYYY-MM-DD`). The git commit hash provides precise versioning.

---

## Runtime (API) Version Rules

Follows SemVer based on FastAPI app version in `backend/app/aggregator_api/main.py`.

---

## Version Update Rules

1. **Version files must be updated** when the corresponding artifact changes.
2. **Version is recorded in PROJECT_MEMORY** under the relevant state section.
3. **Brain version changes** trigger a brain rebuild.
4. **PROJECT_CANON version changes** are tracked in the canon README.
5. **All version files are committed** with their changes.

---

## Current Versions (2026-06-27)

| Artifact | Version |
|----------|---------|
| Brain | 1.0.0 |
| Memory Engine | 1.0.0 |
| PROJECT_CANON | 1.0.0 |
| Runtime API | 0.2.1 |
