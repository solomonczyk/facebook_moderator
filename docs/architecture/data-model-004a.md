---
type: data_model
task: TASK-004A
date: 2026-06-26
---

# Data Model — Seasonal Work Aggregator

## JobLead

The core entity. Every seasonal job opportunity from any source becomes a JobLead.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| lead_id | UUID | yes | Unique identifier |
| source_type | enum | yes | public_web, facebook_operator_screenshot, facebook_visible_capture, telegram_submission, employer_form, worker_form, own_group_comment, own_group_post, manual_admin_entry |
| source_name | string | yes | e.g. "021.rs", "Malinari Srbija", "Sezonski poslovi Srbija" |
| source_url | string | no | URL of the original post/ad |
| source_group | string | no | Facebook group name if applicable |
| source_post_url | string | no | Direct post URL |
| source_captured_at | datetime | yes | When the lead was collected |
| source_capture_method | enum | yes | web_search, operator_screenshot, operator_copy_paste, browser_capture, telegram_bot, direct_form |
| raw_text | text | no | Original unmodified text |
| raw_image_path | string | no | Path to screenshot |
| language | enum | yes | sr, ru, uk, hu, ro, en, other |
| job_type | string | yes | e.g. "branje malina", "berba visanja", "gradjevina" |
| location | string | yes | City/town/village |
| region | string | no | e.g. "Zapadna Srbija", "Vojvodina", "Sumadija" |
| country | string | yes | Default "Srbija" |
| workers_needed | integer | no | Number of workers |
| gender_requirement | enum | no | male, female, couple, any |
| start_date | date | no | When work starts |
| pay_amount | string | no | e.g. "5000", "6000 RSD", "140 RSD/kg" |
| pay_currency | enum | no | RSD, EUR |
| pay_type | enum | no | daily, hourly, per_kg, per_unit, monthly |
| payment_frequency | enum | no | daily, weekly, biweekly, monthly, end_of_season |
| accommodation | boolean | no | true/false/null (unknown) |
| accommodation_details | string | no | e.g. "stan", "bungalov", "kontejner" |
| food | boolean | no | true/false/null |
| food_details | string | no | e.g. "3 obroka", "dorucak i rucak" |
| transport | boolean | no | true/false/by_arrangement |
| transport_details | string | no | |
| working_hours | string | no | e.g. "06-14h", "10h dnevno" |
| registered_work | boolean | no | true/false/by_arrangement |
| employer_name | string | no | Name or company |
| contact_phone | string | no | Phone number(s) |
| contact_viber | boolean | no | |
| contact_whatsapp | boolean | no | |
| contact_facebook | boolean | no | |
| contact_inbox_only | boolean | no | Contact only via FB inbox |
| missing_info | list[string] | yes | What's missing |
| freshness_status | enum | yes | fresh_today, fresh_1_3_days, fresh_4_7_days, stale_over_7_days, unknown_date |
| risk_level | enum | yes | low, medium, high, reject |
| risk_flags | list[enum] | no | asks_for_payment, asks_for_documents, too_good_to_be_true, no_contact, unknown_location, spam_keywords, etc. |
| classification | enum | yes | good_lead, low_info_lead, contact_only_lead, market_context, worker_looking_for_job, employer_looking_for_workers, needs_clarification, duplicate_from_previous_digest, repeat_candidate, suspicious, reject |
| duplicate_status | enum | yes | new, possible_duplicate, duplicate, duplicate_from_previous_digest, repeat_candidate, closed |
| duplicate_of | UUID | no | lead_id of the original |
| moderation_status | enum | yes | new, approved_for_digest, needs_review, rejected, escalated |
| public_digest_allowed | boolean | yes | Can appear in public digest |
| operator_verified | boolean | yes | Operator confirmed |
| created_at | datetime | yes | |
| updated_at | datetime | yes | |

## EmployerProfile

Aggregated from leads and reviews.

| Field | Type | Description |
|-------|------|-------------|
| employer_id | UUID | Unique |
| display_name | string | Primary name |
| known_names | list[string] | Aliases/alternate names |
| phone_numbers | list[string] | Known contact numbers |
| locations | list[string] | Where they operate |
| job_types | list[string] | Types of jobs offered |
| source_count | integer | Number of leads from this employer |
| first_seen_at | datetime | |
| last_seen_at | datetime | |
| active_jobs_count | integer | Current open positions |
| reviews_count | integer | |
| average_worker_rating | float | 1-5 |
| rating_breakdown | dict | Per-category averages |
| risk_flags | list[enum] | |
| moderation_status | enum | |
| right_of_reply_notes | text | Employer responses to reviews |

## WorkerProfile

| Field | Type | Description |
|-------|------|-------------|
| worker_id | UUID | |
| display_name | string | Optional — privacy-controlled |
| phone_numbers | list[string] | |
| preferred_jobs | list[string] | |
| preferred_locations | list[string] | |
| available_from | date | |
| languages | list[enum] | |
| experience_tags | list[string] | e.g. "3 godine sezonski", "gradjevina" |
| worker_reviews_count | integer | |
| employer_feedback_count | integer | |
| moderation_status | enum | |
| privacy_level | enum | public, group_only, private |

## Review

| Field | Type | Description |
|-------|------|-------------|
| review_id | UUID | |
| review_type | enum | worker_review, employer_review |
| target_type | enum | employer, worker |
| target_id | UUID | Employer or worker ID |
| author_type | enum | worker, employer |
| author_id | UUID | |
| job_lead_id | UUID | Linked job if applicable |
| rating_overall | integer | 1-5 |
| rating_pay_accuracy | integer | 1-5 |
| rating_accommodation | integer | 1-5 |
| rating_food | integer | 1-5 |
| rating_working_hours | integer | 1-5 |
| rating_payment_timeliness | integer | 1-5 |
| rating_respect | integer | 1-5 |
| text | text | Review content |
| evidence_files | list[string] | Paths to supporting docs |
| right_of_reply_status | enum | pending, replied, not_needed |
| right_of_reply_text | text | Response from the other party |
| moderation_status | enum | new, approved, rejected, needs_edits, escalated |
| public_allowed | boolean | |
| created_at | datetime | |

## Rating Categories

```yaml
payment_accuracy: "Da li je plaćeno onoliko koliko je dogovoreno"
payment_timeliness: "Da li je isplata bila na vreme"
accommodation_quality: "Kvalitet smeštaja"
food_quality: "Kvalitet hrane"
working_hours_accuracy: "Da li je radno vreme bilo kao što je rečeno"
transport_accuracy: "Da li je prevoz bio kao dogovoreno"
respectful_treatment: "Odnos prema radnicima"
safety: "Bezbednost na radu"
overall: "Ukupna ocena"
```
