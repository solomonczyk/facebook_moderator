---
type: test_cases
task: sezonski_rad_ops_001
date: 2026-06-26
---

# Test Cases — Sezonski Rad Ops 001

## Structural Tests

### T1: Vault Structure
- [ ] `sezonski-rad-ops/` folder exists
- [ ] All required subdirectories exist (15 directories)
- [ ] No Notion-related files present
- [ ] No Google Sheets links as primary storage

### T2: Root Files
- [ ] `00-dashboard.md` exists
- [ ] `01-daily-workflow.md` exists
- [ ] `02-rules.md` exists
- [ ] `03-risk-policy.md` exists
- [ ] `04-content-plan.md` exists
- [ ] `README.md` exists

### T3: Entity Templates
- [ ] `vacancies/_template-vacancy.md` exists with YAML frontmatter
- [ ] `workers/_template-worker.md` exists with YAML frontmatter
- [ ] `reviews/_template-review.md` exists with YAML frontmatter
- [ ] `employers/_template-employer.md` exists with YAML frontmatter
- [ ] `outreach/_template-target.md` exists with YAML frontmatter
- [ ] `outreach/_template-outreach-log.md` exists with YAML frontmatter
- [ ] `moderation/_template-moderation-case.md` exists with YAML frontmatter
- [ ] `post-queue/_template-post.md` exists with YAML frontmatter

## YAML Schema Tests

### T4: Vacancy YAML
- [ ] Contains: type, status, source, location, job_type, employer_name
- [ ] Contains: pay_amount, pay_type, pay_frequency, working_hours
- [ ] Contains: accommodation, food, transport, registered_work
- [ ] Contains: contact_public, risk_level
- [ ] Contains: operator_approved, posted_to_group, verified_by_operator
- [ ] Status values defined (9 values)

### T5: Worker YAML
- [ ] Contains: type, status, location, desired_job_type, experience
- [ ] Contains: available_from, needs_accommodation, can_travel
- [ ] Contains: operator_approved, posted_to_group
- [ ] Status values defined (8 values)

### T6: Review YAML
- [ ] Contains: type, status, employer_name_optional, job_type, work_period
- [ ] Contains: promised_conditions, actual_conditions, pay_received
- [ ] Contains: accommodation_rating through overall_rating
- [ ] Contains: contains_personal_data, contains_insults, legal_risk
- [ ] Contains: safe_version_created, operator_approved
- [ ] Status values defined (8 values)

### T7: Outreach YAML
- [ ] Contains: type, status, platform, group_name, group_url
- [ ] Contains: language, operator_posted, operator_approved
- [ ] Status values defined (8 values)

### T8: Post Queue YAML
- [ ] Contains: type, status, language, post_category
- [ ] Contains: operator_approved, posted_to_facebook, facebook_post_url
- [ ] post_category values defined (7 values)

## Constraint Tests

### T9: No Notion
- [ ] No Notion URL references in any file
- [ ] No Notion schema definitions
- [ ] No "notion" keyword in operational files
- [ ] `google_sheets_used_as_crm: false` in proof.json

### T10: No Google Sheets as CRM
- [ ] No Google Sheets URLs as primary data storage
- [ ] No "Google Sheets CRM" references
- [ ] `google_sheets_used_as_crm: false` in proof.json

### T11: No Duplicate Storage
- [ ] No parallel CSV database outside vault
- [ ] No Airtable references
- [ ] No parallel Notion database
- [ ] `duplicate_storage_created: false` in proof.json

### T12: Manual Gates
- [ ] `operator_approved` field in all publishable entity templates
- [ ] `operator_posted` / `posted_to_facebook` field in outreach and post templates
- [ ] `manual_operator_required: true` in proof.json
- [ ] Publication gate documented in rules

### T13: Facebook Constraints
- [ ] `facebook_auto_actions_enabled: false` in proof.json
- [ ] `facebook_scraping_enabled: false` in proof.json
- [ ] No auto-posting instructions in workflow
- [ ] Daily workflow confirms manual actions only

### T14: Fake Content Forbidden
- [ ] `fake_vacancies_forbidden: true` in proof.json
- [ ] `fake_reviews_forbidden: true` in proof.json
- [ ] No templates for generating fake content
- [ ] Rules explicitly forbid fake content

### T15: Multilingual Coverage
- [ ] Serbian templates: 10 files
- [ ] Russian templates: 10 files
- [ ] Ukrainian templates: 10 files
- [ ] Hungarian templates: 10 files
- [ ] Romanian templates: 10 files
- [ ] Total: 50 multilingual template files

## Validation Status

| Test | Status | Notes |
|------|--------|-------|
| T1 | | |
| T2 | | |
| T3 | | |
| T4 | | |
| T5 | | |
| T6 | | |
| T7 | | |
| T8 | | |
| T9 | | |
| T10 | | |
| T11 | | |
| T12 | | |
| T13 | | |
| T14 | | |
| T15 | | |

---
*Run validation: manually check each test or use scripts/validate-obsidian-structure.sh*
