---
type: roadmap
task: TASK-004A
date: 2026-06-26
version: 0.1.0
---

# MVP Roadmap — Seasonal Work Aggregator

## Layer 1 — Lead Aggregator MVP

**Status:** In progress (manual pipeline exists, automation being designed)

**Goal:** Collect, normalize, deduplicate, score, and publish seasonal job leads from any source.

**Components:**

| Component | Status |
|-----------|--------|
| Source-agnostic lead intake | Manual pipeline active (web + operator FB screenshots) |
| Lead normalization schema | Designed (TASK-004A data-model) |
| Duplicate detection | Designed, manual implementation in Obsidian |
| Freshness scoring | Designed, manual |
| Risk scoring | Designed, manual |
| Daily digest generator | Active (live-market-feed package) |
| Moderation queue | Active (moderation/ in Obsidian) |
| Post queue | Active (post-queue/ in Obsidian) |
| Obsidian export | Active (all data in Obsidian vault) |

**Next:** TASK-004B — Python backend for automated pipeline.

---

## Layer 2 — Employer / Worker Directory

**Status:** Not started

**Goal:** Build profiles from accumulated leads and submissions.

**Components:**

| Component | Status |
|-----------|--------|
| Employer profile schema | Designed |
| Worker profile schema | Designed |
| Employer extraction from leads | Not started |
| Worker extraction from leads | Not started |
| Contact history tracking | Not started |
| Job history per employer | Not started |

**Dependencies:** Layer 1 must be automated first (manual profiles don't scale).

---

## Layer 3 — Ratings and Reviews

**Status:** Not started

**Goal:** Enable workers to rate employers and vice versa, with moderation.

**Components:**

| Component | Status |
|-----------|--------|
| Review schema | Designed |
| Rating categories | Designed (9 categories) |
| Review moderation engine | Designed |
| Right of reply system | Designed |
| Public trust score | Designed (minimum 3 reviews) |
| Review form (worker) | Not started |
| Review form (employer) | Not started |

**Dependencies:** Layer 2 (need employer/worker profiles to attach reviews to).

---

## Layer 4 — Self-Sustaining Marketplace

**Status:** Vision

**Goal:** Employers post directly, workers apply directly. Facebook becomes a traffic source, not a data source.

**Components:**

| Component | Status |
|-----------|--------|
| Employer posting form | Designed |
| Worker application form | Designed |
| Auto-digest from internal data | Not started |
| Facebook → traffic source only | Not started |
| Matchmaking / recommendations | Vision |

**Dependencies:** Layers 1-3 must be fully functional.

---

## Timeline Estimate

| Layer | Effort | Dependencies |
|-------|--------|-------------|
| Layer 1 MVP | 2-4 weeks | None |
| Layer 2 Directory | 2-3 weeks | Layer 1 |
| Layer 3 Ratings | 3-4 weeks | Layer 2 |
| Layer 4 Marketplace | 4-8 weeks | Layer 3 |

Total: ~3-5 months to full marketplace MVP.

---

## Immediate Next Actions

1. **TASK-004B**: Python backend — models, schemas, lead normalizer
2. **TASK-004C**: Duplicate detector + freshness/risk scorers (Python)
3. **TASK-004D**: Digest builder + Obsidian export (Python)
4. **TASK-004E**: Simple web UI for operator lead intake
