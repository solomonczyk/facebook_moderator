# RELEASE_POLICY.md — Release Stages and Gates

> Part of PROJECT_CANON. Defines the release pipeline.

---

## Release Stages

```
DEVELOPMENT ──► ACCEPTED ──► OPERATOR REVIEW ──► PRODUCTION CANDIDATE
                                                       │
                                                       ▼
                                               PRODUCTION ACCEPTED
```

---

### DEVELOPMENT

**Definition:** Task is implemented, committed, but not yet reviewed by operator.

**Gate:** All automated checks pass:
- [ ] Files created/modified match task scope
- [ ] Tests present and passing
- [ ] Proof artifacts created
- [ ] Security checks pass (no secrets, .env not tracked)
- [ ] Git clean (task files only)
- [ ] Commit message follows format

**Exit:** Operator marks task as ACCEPTED or REJECTED.

---

### ACCEPTED

**Definition:** Operator has reviewed and accepted the task. Code committed to master. Not pushed.

**Gate:** Operator confirms:
- [ ] Implementation matches task description
- [ ] Tests are adequate
- [ ] No unwanted side effects
- [ ] PROJECT_MEMORY updated

**Exit:** Operator initiates push OR task enters OPERATOR REVIEW for production.

---

### OPERATOR REVIEW

**Definition:** Operator reviews the complete feature in operation. VPS runtime is running accepted code.

**Gate:** Operator confirms:
- [ ] Feature works as expected on VPS
- [ ] No runtime errors in logs
- [ ] Telegram bot functioning
- [ ] Queue processing correctly
- [ ] No unexpected LLM behavior

**Exit:** Feature is marked as PRODUCTION CANDIDATE or returned to DEVELOPMENT.

---

### PRODUCTION CANDIDATE

**Definition:** Feature has passed operator review. Ready for production use. `production_accepted` gate still DISABLED until operator explicitly enables.

**Gate:**
- [ ] All OPERATOR REVIEW checks passed
- [ ] No known high-severity issues
- [ ] Rollback plan documented

**Exit:** Operator sets `production_accepted = true`.

---

### PRODUCTION ACCEPTED

**Definition:** Feature is in production use. `production_accepted = true`. Operator manually publishes to Facebook.

**Constraints:**
- [ ] Dangerous gates remain as configured
- [ ] Monitoring active
- [ ] Audit log active

---

## Emergency Fix

**Definition:** Critical bug that must be fixed immediately.

**Process:**
1. Create hotfix branch from master
2. Implement fix with minimal scope
3. Test on VPS
4. Commit with `fix:` prefix
5. Operator reviews and merges to master
6. Update PROJECT_MEMORY

**Relaxed rules:**
- Proof artifacts optional (add after fix)
- Full test suite optional (smoke test minimum)
- Document after fix, not before

---

## Hotfix

Same as Emergency Fix but for non-critical bugs.

**Process:** Same as Emergency Fix, but proof artifacts required.

---

## Rollback

**Definition:** Revert to previous known-good state.

**Process:**
1. Identify last known-good commit from git log
2. Operator approves rollback
3. `git revert <bad-commit>` or `git reset --hard <good-commit>`
4. Verify system operational
5. Update PROJECT_MEMORY
6. Document rollback reason in CHANGELOG

---

## Gate Summary

| Stage | Auto gates | Operator gates |
|-------|-----------|----------------|
| DEVELOPMENT | Tests, security, git clean | — |
| ACCEPTED | — | Feature review |
| OPERATOR REVIEW | — | Runtime verification |
| PRODUCTION CANDIDATE | — | Final sign-off |
| PRODUCTION ACCEPTED | Dangerous gates check | Enable production |
| EMERGENCY FIX | Security only | Post-fix review |
| ROLLBACK | — | Rollback approval |
