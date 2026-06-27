# ADR.md — Accepted Architecture Decisions

> Part of PROJECT_CANON. Append-only. Each ADR is a permanent decision.

---

## ADR-001: Facebook Automation Forbidden

**Date:** 2026-06-21
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** The system must never perform automated Facebook actions (post, comment, message, delete, ban). All Facebook write operations are performed manually by the operator.

**Rationale:** Safety. Automated Facebook actions pose risk of spam detection, group member harm, policy violation, and account suspension. The operator must remain in control of all content published to the group.

**Constraints:** No auto-post, no auto-comment, no auto-message, no auto-delete, no auto-ban.

---

## ADR-002: Operator is Final Authority

**Date:** 2026-06-21
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** The agent provides recommendations. The operator makes final decisions. Operator overrides are recorded in audit log and respected without question.

**Rationale:** The agent is an AI system that can make mistakes. The operator has context the agent lacks. Final authority must rest with the human.

**Constraints:** Agent never overrides operator. Agent never hides its uncertainty. Agent always shows confidence score.

---

## ADR-003: Brain Documentation is Model-Independent

**Date:** 2026-06-25
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** The Brain v1.0 documentation package (CANON, KNOWLEDGE, PROMPTS, TESTS) must work with any LLM provider — DeepSeek, GPT, Claude, or local models. No provider-specific content in brain docs.

**Rationale:** Avoid vendor lock-in. Allow provider switching without rewriting brain documentation. Future-proof the intellectual core.

**Constraints:** SystemPrompt must be provider-agnostic. Few-shot examples must be provider-agnostic. JSON contract is universal.

---

## ADR-004: PROJECT_MEMORY Stores Runtime State

**Date:** 2026-06-27
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** `docs/project/PROJECT_MEMORY.md` is the single source of truth for current project state. It is updated after every task. PROJECT_CANON stores permanent rules. PROJECT_MEMORY stores current state.

**Rationale:** Separate permanent rules from volatile state. New AI sessions read PROJECT_MEMORY first. Prevents stale information accumulation.

**Constraints:** PROJECT_MEMORY must be updated after every task. Stale information must be removed. Max 20 changelog entries.

---

## ADR-005: PROJECT_CANON Stores Permanent Rules

**Date:** 2026-06-27
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** `docs/project/PROJECT_CANON/` contains permanent project rules. These change rarely and only through explicit architectural decisions.

**Rationale:** Permanent rules should not be mixed with volatile state. Separate files allow independent versioning and review.

**Constraints:** PROJECT_CANON changes require explicit ADR or task. No accidental edits. Version is tracked independently.

---

## ADR-006: DeepSeek is Primary LLM Provider

**Date:** 2026-06-25
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** DeepSeek (model: DeepSeek-V4-Pro) is the primary LLM provider for runtime analysis. Provider is configurable via `LLM_PROVIDER` env var.

**Rationale:** Cost efficiency, capability, Anthropic-compatible API, availability on VPS.

**Constraints:** System must remain provider-agnostic. Switching provider requires only env var change + brain rebuild.

---

## ADR-007: Runtime Uses JSON Contract

**Date:** 2026-06-25
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** All LLM responses must be valid JSON matching the defined schema. No markdown output. No free text outside JSON. No chain-of-thought exposure.

**Rationale:** Reliable parsing. Structured data for queue, digest, audit. Avoids parsing ambiguity. Enables validation and fallback.

**Constraints:** SystemPrompt must include exact JSON schema. Validator rejects non-conforming responses. Fallback classifier handles validation failures.

---

## ADR-008: Safety Over Speed

**Date:** 2026-06-25
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** When safety conflicts with speed, choose safety. High-risk content is never published. Low-confidence decisions are escalated. Missing information is flagged, not invented.

**Rationale:** The group serves vulnerable workers. A single bad publication (scam, fraud, fake job) damages trust irreparably. Speed is secondary to safety.

**Constraints:** Confidence < 0.60 → escalate. Risk = high → never publish. Missing info → always flag.

---

## ADR-009: No Hallucinated Facts

**Date:** 2026-06-25
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** The agent must never invent facts. Phone numbers, pay amounts, locations, employer names, conditions — if not present in source text, set to null and flag as missing.

**Rationale:** Hallucinated information can send workers to wrong locations, wrong contacts, or create false expectations. Missing information is safer than wrong information.

**Constraints:** All extraction fields default to null. Missing info list is always populated. SystemPrompt explicitly forbids invention.

---

## ADR-010: Dangerous Gates Disabled by Default

**Date:** 2026-06-24
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** All dangerous gates (Facebook automation, captcha bypass, fake accounts, production mode) are DISABLED by default and must be explicitly enabled with operator approval for each session.

**Rationale:** Default-safe posture. No accidental automation. Gates cannot be enabled by configuration alone — requires code change + operator approval.

**Constraints:** All gates start disabled. Hard-forbidden gates cannot be enabled at all. Gate state is visible in PROJECT_MEMORY.

---

## ADR-011: One Task = One Feature

**Date:** 2026-06-27
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** Each development task implements exactly one feature or one subsystem. Tasks are numbered sequentially (TASK NNN). Each task has: description, tests, proof, commit.

**Rationale:** Atomic commits. Clear audit trail. Testable increments. No mixed concerns.

**Constraints:** Tasks must not mix concerns. Each task produces one commit. Proof is required.

---

## ADR-012: Telegram Polling Mode

**Date:** 2026-06-24
**Status:** ACCEPTED
**Supersedes:** None

**Decision:** Telegram bot uses long polling (getUpdates) instead of webhook. Backend stays on 127.0.0.1.

**Rationale:** VPS has no public domain. Polling simplifies infrastructure. No SSL certificate needed. No public endpoint exposure.

**Constraints:** Polling interval is managed by python-telegram-bot. Operator chat ID is authenticated.
