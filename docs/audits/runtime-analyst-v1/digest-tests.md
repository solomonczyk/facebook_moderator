---
type: audit
task: TASK-006C
section: digest
date: 2026-06-26
---

# Digest Tests — Runtime Analyst v1

## Candidate Selection

- good_lead + location + contact + job_type → included ✅
- low_info_lead + location + contact + job_type → included ✅
- contact_only_lead → included with warning ✅
- spam → excluded ✅
- suspicious → excluded ✅
- rejected → excluded ✅

## Missing Pay Warning

When pay_amount is missing:
"Dnevnica nije navedena. Proverite direktno kod poslodavca." is automatically added. ✅

## Disclaimer

Every digest includes:
"Grupa nije poslodavac i ne garantuje uslove..." ✅
