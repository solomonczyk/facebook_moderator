# ROADMAP — Future Plans

> Last updated: 2026-06-27
> Supersedes: PROJECT_MEMORY §11 (Future Roadmap)

This document tracks the project roadmap. PROJECT_MEMORY keeps only a priority summary.

---

## Priority Legend

| Code | Meaning |
|------|---------|
| P0 | Active / immediate |
| P1 | Next milestone |
| P2 | Planned |
| P3 | Future / nice-to-have |

---

## Active (P0)

| Task | Description | Status |
|------|-------------|--------|
| TASK 008C | PROJECT_CANON Foundation v1.0 | 🔵 In progress |

---

## Next Milestone (P1)

| Task | Description | Status |
|------|-------------|--------|
| TASK 008D | Brain version migration system | Not started |
| TASK 009B | Memory Engine integration with analyst agent | Not started |
| — | Runtime integration tests for Brain pipeline | Not started |
| — | End-to-end test: intake → analyze → Telegram → operator decision | Not started |

---

## Planned (P2)

| Task | Description | Status |
|------|-------------|--------|
| — | Production deploy pipeline | Not started |
| — | Automated VPS health checks | Not started |
| — | Multi-operator Telegram support | Not started |
| — | Digest auto-generation (operator-gated) | Not started |
| — | Worker request matching (memory engine) | Not started |

---

## Future (P3)

| Task | Description | Status |
|------|-------------|--------|
| — | Brain v1.1 (more edge cases, language improvements) | Not started |
| — | Serbian Cyrillic support in public posts | Not started |
| — | Hungarian and Romanian language support | Not started |
| — | Facebook group statistics dashboard | Not started |
| — | Automated employer verification (public records) | Not started |
| — | Seasonal trend analysis | Not started |

---

## Completed Recently

See [CHANGELOG.md](CHANGELOG.md) for full history.

| Task | Commit | Date |
|------|--------|------|
| TASK 008B | `33681e7` | 2026-06-27 |
| TASK 008A | `8455200` | 2026-06-27 |
| TASK 009A | `732d42a` | 2026-06-26 |
| TASK 008B-BUILD | `9b4f42a` | 2026-06-26 |
| TASK 007B-FIX | `ca3b53f` | 2026-06-25 |
| TASK 007B | `dbc5747` | 2026-06-25 |
| TASK 007A | `ace0a69` | 2026-06-25 |
| TASK 006C | `4100a6c` | 2026-06-25 |

---

## Milestones

### Milestone 1: Core Runtime ✅
- [x] Runtime agent, intake, analyst
- [x] DeepSeek integration
- [x] Telegram operator approval
- [x] Brain v1.0 documentation

### Milestone 2: Project Infrastructure 🔵
- [x] PROJECT_MEMORY
- [ ] PROJECT_CANON ← in progress
- [ ] ROADMAP
- [ ] CHANGELOG

### Milestone 3: Production Readiness
- [ ] Integration tests
- [ ] Deploy pipeline
- [ ] Monitoring
- [ ] Operator documentation

### Milestone 4: Scale
- [ ] Multi-operator
- [ ] Multi-group
- [ ] Dashboard
