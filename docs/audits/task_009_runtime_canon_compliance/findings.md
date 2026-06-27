# Findings — Discrepancies and Issues

## FINDING-001: 6 proof.json files claim `committed: false` — commits exist
- **Severity:** HIGH
- **Status:** open
- **Canon reference:** ADR-004 (PROJECT_MEMORY stores state), DEVELOPMENT_STANDARD (proof mandatory)
- **Code reference:** `docs/audits/runtime-analyst-v1/proof.json`, `runtime-manager-agent-v1/proof.json`, `runtime-brain-v1-activation/proof.json`, `brain-build/proof.json`, `memory-v1/proof.json`, `docs/audits/brain-build/proof.json`
- **Evidence:** Each proof has `"committed": false, "commit_hash": null` but corresponding commits (`4100a6c`, `ace0a69`, `ca3b53f`, `9b4f42a`, `732d42a`) exist in git log.
- **Recommended:** Update these 6 proof.json files to set `committed: true` with correct commit hashes. Consider a script to auto-update proof.json on commit.

## FINDING-002: 3 proof.json files reference orphaned commit hashes
- **Severity:** HIGH  
- **Status:** open
- **Canon reference:** ADR-004
- **Code reference:** `docs/audits/brain-v1/proof.json` (claims `f02528a`, actual `8455200`), `docs/audits/project-memory/proof.json` (claims `9f49bab`, actual `33681e7`), `docs/audits/project-canon/proof.json` (claims `1249f9a`, actual `9cd8e09`)
- **Evidence:** All three hashes are orphaned by `git commit --amend`. The proof.json was updated with the pre-amend hash and never corrected. `git log --all --oneline` does not show these hashes on any branch.
- **Recommended:** Update proof.json commit_hash fields to match actual `master` hashes. Consider a post-commit hook or CI check.

## FINDING-003: Task 007B has no proof.json
- **Severity:** MEDIUM
- **Status:** open
- **Canon reference:** ADR-011 (one task = one feature with proof)
- **Code reference:** Git commit `dbc5747` "feat: TASK 007B — DeepSeek Runtime Brain V1"
- **Evidence:** PROJECT_MEMORY §9 lists task 007B as completed. No `docs/audits/deepseek-brain-v1/proof.json` exists. The closest file is `runtime-brain-v1-activation/proof.json` which covers 007B-FIX (VPS activation).
- **Recommended:** Create a retroactive proof.json for task 007B documenting the DeepSeek brain implementation, or explicitly note why it was skipped.

## FINDING-004: PROJECT_MEMORY marks TASK 008C as "in progress"
- **Severity:** MEDIUM
- **Status:** open
- **Canon reference:** ADR-004 (PROJECT_MEMORY must be updated after every task)
- **Code reference:** `docs/project/PROJECT_MEMORY.md` §8 (Active Tasks): "TASK 008C | In progress"
- **Evidence:** Commit `9cd8e09` is TASK 008C. `docs/audits/project-canon/proof.json` has verdict ACCEPTED, status completed. PROJECT_MEMORY §9 (Completed) and §18 (Recent Changes) are stale.
- **Recommended:** Move TASK 008C from Active (§8) to Completed (§9), update §18 changelog entry, update §12 Git State.

## FINDING-005: CHANGELOG missing commit `0cf3ef8`
- **Severity:** LOW
- **Status:** open
- **Canon reference:** DOCUMENT_POLICY.md (CHANGELOG responsibility)
- **Code reference:** `docs/project/CHANGELOG.md`, git commit `0cf3ef8`
- **Evidence:** `0cf3ef8 feat: Task 005C — Risk-managed own group account worker prototype` is absent from CHANGELOG. The CHANGELOG lists only `a188664` (the Selenium fix) for 005C.
- **Recommended:** Add `0cf3ef8` entry to CHANGELOG under 2026-06-23.

## FINDING-006: Dual LLM client implementations
- **Severity:** LOW
- **Status:** open
- **Canon reference:** ADR-006 (DeepSeek is primary), DIRECTORY_STANDARD
- **Code reference:** `backend/app/llm/` (new, provider-agnostic) vs. `backend/app/services/llm_client.py` (legacy, Anthropic-only)
- **Evidence:** Two separate LLM client implementations. The legacy one defaults to `claude-sonnet-4-20250514`. Both read API keys from env. No test coverage for either.
- **Recommended:** Deprecate `services/llm_client.py`, consolidate to `backend/app/llm/`, add tests for the unified client.

## FINDING-007: Clipboard intake enabled by default
- **Severity:** LOW
- **Status:** open  
- **Canon reference:** ADR-010 (dangerous gates disabled by default)
- **Code reference:** `backend/app/runtime_intake/config.py` — `clipboard_intake_enabled` defaults to `True`
- **Evidence:** Unlike other potentially sensitive gates (all `False`), clipboard reading is enabled by default. This could capture sensitive data without operator awareness.
- **Recommended:** Default `clipboard_intake_enabled` to `False`, require explicit operator enablement.
