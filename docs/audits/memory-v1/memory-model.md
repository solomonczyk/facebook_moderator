---
type: audit
task: TASK-009A
section: memory_model
date: 2026-06-26
---

# Memory Model — v1.0

## Domains

| Domain | Storage | Purpose |
|--------|---------|---------|
| Employers | JSON files per employer | Known employers, trust scores, history |
| Workers | JSON files per worker | Known workers, experience, availability |
| Cases | JSON files per case | Complaints, fraud, investigations |
| Knowledge | JSON files per entry | Crops, salaries, regions, terminology |

## Principles

- Facts only — never hallucinate
- Append-only history — timeline preserved
- Every record: source, timestamp, confidence, operator_verified
- Brain decides, Memory provides context
- SHA256-based phone hashing for privacy-safe indexes

## Indexes

- phone_index.json — hashed phone → entity list
- name_index.json — normalized name → entity list
- location_index.json — normalized location → entity list

## Trust Model

- Score 0.0–1.0, starts at 0.5
- Positive signals: +0.05 each
- Negative signals: -0.10 each
- Verified: +0.10
- Complaints: -0.05 each
- Always clamped [0.0, 1.0]
