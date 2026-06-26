---
title: Daily Workflow
updated: 2026-06-26
---

# Daily Workflow — Sezonski rad Srbija

## Operator-in-the-Loop Principle

Every Facebook action is performed **manually** by the human operator. The AI agent only prepares, classifies, drafts, and tracks. Nothing is ever auto-posted, auto-sent, or auto-moderated.

---

## Morning — Sourcing (1–2 hours)

**Goal:** Find 10–20 potential vacancies from external sources.

### Process

1. Search public Facebook groups, job boards, Telegram/Viber channels for seasonal work ads in Serbia.
2. For each vacancy found:
   - Copy the ad text.
   - Create a new file in `vacancies/` from `_template-vacancy.md`.
   - Fill in all available fields.
   - Set `status: new`.
   - Set `source` to where you found it (facebook_group, telegram, website, referral).
   - Set `risk_level` based on completeness and red flags.
3. Do NOT post anything yet. Sourcing is collection only.
4. For suspicious vacancies (`risk_level: high`), add `notes` explaining why.

### Red Flags During Sourcing

- "brza zarada", "laka zarada", "bez iskustva puno para"
- No company name or employer identity
- Contact only via private message
- Requests for advance payment
- Unrealistic pay
- No location

### Output

- 10–20 new files in `vacancies/`
- Dashboard vacancy queue updated (Dataview auto-refresh)

---

## Day — Outreach (1 hour, max 3–5 contacts)

**Goal:** Contact other groups and authors to grow the group.

### Process

1. Select 3–5 outreach targets from `outreach/target-groups/` with status `new` or `approved_target`.
2. Prepare a message using the multilingual templates in `templates/`.
3. **GATE:** `operator_approved: true` must be set before sending.
4. Operator manually sends the message on Facebook.
5. After sending:
   - Update `last_contacted` with today's date.
   - Set `operator_posted: true`.
   - Set `status: posted_once` or `waiting_result`.
   - Log the action in `outreach/daily-logs/` with today's date.

### Outreach Rules

- Maximum 3–5 contacts per day — never spam.
- Always use the appropriate language template.
- Never promise "verified" or "guaranteed" jobs.
- Never mass-message or auto-invite.

### Output

- 3–5 outreach actions logged
- `outreach/daily-logs/YYYY-MM-DD.md` created

---

## Evening — Publishing (1 hour)

**Goal:** Select and publish 1–3 useful posts to the group.

### Process

1. Choose posts from:
   - `post-queue/ready/` (pre-approved drafts)
   - `vacancies/` with `status: ready_to_post`
   - `reviews/` with `status: ready_to_post`
2. Run each post through the **Admin Copilot** for final check.
3. **GATE:** Confirm `operator_approved: true`.
4. Operator manually publishes to Facebook.
5. After publishing:
   - Set `posted_to_facebook: true`.
   - Add `facebook_post_url`.
   - Move post file to `post-queue/posted/`.
   - Update vacancy/review status to `posted`.

### Content Mix

Aim for variety across the week:
- Vacancy posts (Mon, Wed, Fri)
- Worker experience / safety advice (Tue, Thu)
- Engagement questions (Sat)
- Admin updates / group news (as needed)

### Output

- 1–3 posts published to Facebook
- Post queue updated
- Daily report updated with KPI

---

## End of Day — Reporting (15 minutes)

1. Open `reports/_template-daily-report.md`.
2. Fill in today's KPIs.
3. Note any escalated cases or conflicts.
4. Note any suspicious patterns observed.
5. Save report to `reports/YYYY-MM-DD.md`.

---

## Weekly — Content Planning (Sunday, 1 hour)

1. Open `04-content-plan.md`.
2. Review last week's KPIs.
3. Plan 7 days of content:
   - 2–3 vacancy posts
   - 1–2 worker reviews
   - 1–2 engagement/safety posts
   - 1 admin or group update
4. Prepare drafts in `post-queue/ready/`.
5. Update `04-content-plan.md` with next week's plan.

---

## Operator Checklist (Daily)

- [ ] Morning sourcing completed (10+ vacancies found)
- [ ] Outreach completed (3–5 groups contacted)
- [ ] Red-flag items flagged to admin
- [ ] Pending moderation cases reviewed
- [ ] 1–3 posts published
- [ ] All published posts have `facebook_post_url`
- [ ] Dashboard KPIs updated
- [ ] Daily report saved
- [ ] No auto-actions performed — all manual
