---
title: Operating Rules
updated: 2026-06-26
---

# Operating Rules — Sezonski rad Srbija

## Core Principle: Trust

The group's main value is **trust**. Every action must protect the group from spam, fraud, insults, defamation, and dangerous content.

---

## Source of Truth

- **Obsidian Vault** is the single source of truth.
- ❌ Notion is not used.
- ❌ Google Sheets is not the primary CRM.
- ❌ No parallel databases outside the vault.
- ✅ All data lives in markdown files with YAML frontmatter.
- ✅ Export is allowed for backup, not for primary storage.

---

## Operator-in-the-Loop

Every Facebook action requires a human operator:

| Action | Who? |
|--------|------|
| Publish a post | Operator manually |
| Send a message | Operator manually |
| Approve/reject a member | Operator manually |
| Delete a post | Operator manually |
| Ban a member | Operator manually |
| Contact an employer | Operator manually |
| Reply to a comment | Operator manually |

The AI agent **prepares, classifies, drafts, tracks** — never acts directly on Facebook.

---

## Manual Publication Gates

### Gate 1: Any Post

```yaml
operator_approved: true
posted_to_facebook: false  # true after manual publication
```

### Gate 2: Negative Review

```yaml
safe_version_created: true
operator_approved: true
legal_risk: low  # must be low before publishing
contains_insults: false
contains_personal_data: false
```

### Gate 3: Employer Conflict

```yaml
status: escalated
manual_review_required: true
```

### Gate 4: Outreach Message

```yaml
operator_approved: true
operator_posted: false  # true after manual send
```

---

## Vacancy Rules

Every vacancy must be checked for 12 required fields:

1. Location (city/town)
2. Type of work
3. Start date
4. Number of workers needed
5. Pay amount
6. Payment method
7. Working hours
8. Accommodation (yes/no)
9. Food (yes/no)
10. Transport (yes/no/po dogovoru)
11. Contact phone/Viber/WhatsApp
12. Worker registration (yes/no/po dogovoru)

Missing core fields → `status: needs_clarification`

Suspicious vacancy → `status: suspicious` + escalate to admin

---

## Review Rules

Negative reviews must be rewritten to safe language:

- ❌ "On je prevarant i lopov."
- ✅ "Prema mom ličnom iskustvu, dogovoreni uslovi nisu bili ispoštovani."

- ❌ "Ne idite tamo, gazda vara ljude."
- ✅ "Ja ne bih preporučio/la ovo mesto bez dodatne provere uslova."

Before publishing a negative review:
- `safe_version_created: true`
- `contains_insults: false`
- `contains_personal_data: false`
- `legal_risk: low`

---

## Personal Data Rules

Never publish:

- JMBG
- Passport number
- Full home address
- Third-party phone number without consent
- Private message screenshots with visible personal data
- Bank account numbers
- Documents (ID cards, etc.)
- Children's data

Allowed:

- Employer contact if provided for the vacancy
- Company name
- Public Facebook page
- City / general location

---

## Outreach Rules

- Max 3–5 contacts per day.
- Use the appropriate language template.
- Never spam or mass-message.
- Never promise "verified" vacancies.
- Never use "crna lista" or "najbolji poslodavci" labels.
- Always log outreach actions.

---

## Moderation Rules

Use the Admin Copilot (SYSTEM_PROMPT.md in the parent project) for every post before publishing.

Verdicts:
- **APPROVE** → publish as-is
- **APPROVE_WITH_EDITS** → apply safe rewrite, operator confirms, publish
- **NEEDS_CLARIFICATION** → ask author, wait, do not publish yet
- **REJECT** → do not publish, log reason
- **ESCALATE** → admin manual review required

---

## Data Hygiene

- Each entity gets its own markdown file.
- One vacancy per file, one review per file, one worker per file.
- File naming: `YYYY-MM-DD-descriptive-slug.md`.
- Never duplicate records across multiple files.
- Update `date_modified` when changing a record.
- Archive completed/expired items — do not delete.
