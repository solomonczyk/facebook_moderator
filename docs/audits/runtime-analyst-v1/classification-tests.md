---
type: audit
task: TASK-006C
section: classification
date: 2026-06-26
---

# Classification Tests — Runtime Analyst v1

## Employer Classification

| Input | Expected | Actual | Pass |
|-------|----------|--------|------|
| "Tražimo 5 radnika za berbu malina Arilje" | employer_job_post | employer_job_post | ✅ |
| "Potrebni radnici za branje višanja" | employer_job_post | employer_job_post | ✅ |
| "Zapošljavamo radnike za plastenik" | employer_job_post | employer_job_post | ✅ |
| "Firma traži radnike za pakovanje" | employer_job_post | employer_job_post | ✅ |
| "Treba nam ekipa za berbu jabuka" | employer_job_post | employer_job_post | ✅ |
| "Radnici potrebni za sortiranje voća" | employer_job_post | employer_job_post | ✅ |
| "Berba malina — tražimo berače" | employer_job_post | employer_job_post | ✅ |

## Worker Classification

| Input | Expected | Actual | Pass |
|-------|----------|--------|------|
| "Tražim posao branje malina" | worker_looking_for_job | worker_looking_for_job | ✅ |
| "Imam ekipu 30 ljudi sa prevozom" | worker_group_available | worker_group_available | ✅ |
| "Nas je 5, tražimo poslodavca" | worker_group_available | worker_group_available | ✅ |
| "Dostupni smo za sezonski rad" | worker_group_available | worker_group_available | ✅ |

## Spam Detection

| Input | Expected | Actual | Pass |
|-------|----------|--------|------|
| "BRZA ZARADA kazino online kripto" | spam (high) | spam (high) | ✅ |
| "Forex trading pasivna zarada" | spam (high) | spam (high) | ✅ |
| "Uplata unapred depozit garantovan" | spam (high) | spam (high) | ✅ |

## Order Verification

Employer patterns checked BEFORE worker patterns. "Tražimo 5 radnika" is correctly employer_job_post, not worker_group_available.
