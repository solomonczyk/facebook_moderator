---
type: architecture
section: source_ingestion
task: TASK-004A
date: 2026-06-26
---

# Source Ingestion Architecture

## Design Principle

The system accepts leads from ANY source. No source is privileged. Every source goes through the same normalization, dedup, and scoring pipeline.

## Intake Methods

### 1. Public Web Collector (active)

What it does: Searches public Serbian job boards and classifieds via web search APIs (no Facebook).

Sources:
- 021.rs (classifieds — most productive)
- Euronews.rs, Alo.rs, Blic.rs (market context)
- KupujemProdajem, Halo Oglasi (when indexed)
- Infostud, Jooble (when indexed)
- NSZ.gov.rs (national employment service)

Method: Web search → fetch pages → extract leads → normalize.

Limitations:
- Facebook groups NOT accessible via web search
- Many Serbian classifieds are poorly indexed
- 021.rs is currently the only consistent source

### 2. Operator-Provided Facebook Screenshots (active)

Method:
1. Operator opens Facebook group manually
2. Operator copies post text or takes screenshot
3. Operator pastes into intake form / sends to agent
4. Agent extracts lead data
5. Agent normalizes → dedup → scores

This is currently the PRIMARY method for Facebook leads.

### 3. Facebook Visible Capture (designed, disabled by default)

See: [facebook-capture-risk-model-004a.md](facebook-capture-risk-model-004a.md)

### 4. Telegram Submission (designed)

Future bot that accepts:
- `/posao [text]` — submit a job lead
- Employer/worker registration commands
- All submissions → moderation queue

### 5. Employer Form (designed)

Web form where employers post jobs directly:
- Required: location, job type, pay, accommodation, food, contact, working hours, registration
- Goes to moderation queue
- Employer gets a profile after first submission

### 6. Worker Form (designed)

Web form where workers register:
- Optional: name, preferred jobs, location, availability, languages, experience
- Privacy-controlled: worker chooses what's public
- Worker gets a profile

## Ingestion Pipeline

```
[Raw Input]
     ↓
[Extract: text, phone, location, job_type, pay, conditions]
     ↓
[Normalize: → JobLead schema]
     ↓
[Dedup: phone, location, text similarity, image hash]
     ↓
[Score: freshness + risk]
     ↓
[Classify: good_lead, low_info, contact_only, etc.]
     ↓
[Queue: moderation → approved → digest / rejected]
```

## Normalization Rules

- Phone numbers: strip spaces, normalize to +381 format
- Location: map village → municipality → region
- Pay: extract numeric amount + currency + period
- Job type: map synonyms (branje = berba, radnici = berači)
- Missing info: auto-detect what's absent

## Rate Limiting

- Web searches: max 20/day (respect robots.txt)
- Facebook capture: max 1 group per 5 minutes, max 10 posts per session
- Telegram bot: max 1 submission per 30 seconds per user
- Employer/worker forms: no limit (moderated)
