---
type: architecture
section: trust_rating_review
task: TASK-004A
date: 2026-06-26
---

# Trust, Rating & Review Model

## Core Principle

Ratings are **reported experiences**, not legal conclusions. The platform does not verify claims — it moderates and presents them transparently.

## Review Rules

1. Reviews are NOT published automatically — moderation required.
2. Personal insults are NOT allowed.
3. Private documents are NOT published.
4. Phone numbers shown only when intentionally public in job ads or profiles.
5. Employer has right of reply.
6. Worker has right of reply.
7. Category-based ratings, not just emotional text.
8. Claims about fraud, non-payment, abuse, unsafe housing → escalated.
9. Public display says "reported experience", not "fact".
10. Removal/editing requests supported.

## Rating Categories

| Category | Serbian Label | What It Measures |
|----------|--------------|------------------|
| payment_accuracy | Tačnost isplate | Was the promised amount paid? |
| payment_timeliness | Redovnost isplate | Was payment on time? |
| accommodation_quality | Kvalitet smeštaja | Housing conditions |
| food_quality | Kvalitet hrane | Food quality and quantity |
| working_hours_accuracy | Radno vreme | Were hours as promised? |
| transport_accuracy | Prevoz | Was transport as agreed? |
| respectful_treatment | Odnos prema radnicima | Respect and dignity |
| safety | Bezbednost | Physical safety at work |
| overall | Ukupna ocena | Overall experience |

## Safe Wording Requirements

### NEVER publish:

> "On je prevarant i lopov."
> "Ne idite tamo."
> "Svi su tamo lopovi."
> "Gazda vara ljude."

### Instead use:

> "Prema prijavi radnika, dogovoreni uslovi nisu bili ispoštovani."
> "Radnici su prijavili neisplatu."
> "Prema iskustvu korisnika, uslovi smeštaja nisu odgovarali dogovoru."
> "Uslovi nisu potvrđeni od strane platforme."

## Right of Reply

When a negative review is published:

1. The reviewed party (employer or worker) is notified.
2. They may submit a reply.
3. Reply is moderated (same rules: no insults, no personal data).
4. Reply is published alongside the original review.
5. If the dispute cannot be resolved → both statements remain visible, marked as "sporno".

## Trust Score

A composite score (1-5) calculated from:
- Average category ratings (weighted by review count)
- Number of independent reviews (minimum 3 for public display)
- Recency of reviews (newer reviews weighted higher)
- Right-of-reply status (unreplied negative reviews flagged)

**Rule:** Trust score is NOT displayed publicly until at least 3 independent reviews exist for the entity.

## Moderation Escalation

ESCALATE to manual admin review when:
- Claims of non-payment
- Claims of threats, violence, or illegal activity
- Named individuals with serious accusations
- Legal risk to the platform
- Coordinated attack (multiple negative reviews from new accounts in short time)
