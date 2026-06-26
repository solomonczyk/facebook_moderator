# Negative Examples — What NOT To Do

## Employer Mistaken as Worker

❌ "Tražimo 5 radnika za berbu malina Arilje" → worker_request
✅ Correct: employer_job_post

## Spam Treated as Job

❌ "KAZINO online brza zarada" → employer_job_post
✅ Correct: spam, risk=high, never publish

## Missing Pay Invented

❌ Pay field: "5000 RSD dnevno" (not in source text)
✅ Correct: pay=null, missing_info includes "plata"

## Public Text Says "Guaranteed"

❌ "Garantovano proveren poslodavac"
✅ Correct: NEVER use garantovano/provereno/sigurno

## Suspicious Passport Request Approved

❌ "Pošaljite sliku pasoša" → approve
✅ Correct: suspicious, risk=high, escalate

## No-Contact Job Added to Digest

❌ Job with no phone, no location → digest_candidate=true
✅ Correct: digest_candidate=false if missing contact AND location

## Angry Review Published with Insults

❌ "On je lopov i prevarant, ne idite tamo!" → approve
✅ Correct: escalate. Rewrite as "Prema mom iskustvu, uslovi nisu bili ispoštovani"

## Operator Uncertainty Hidden

❌ confidence=0.40, but recommended_action=approve
✅ Correct: confidence<0.60 → escalate

## Foreign Job Marked as Serbia

❌ "Posao u Nemačkoj, plata 2000e" → employer_job_post, country=Srbija
✅ Correct: suspicious or irrelevant, country=not Serbia

## Fake Review Created

❌ Agent writes: "Radio sam tamo, sve super, preporučujem"
✅ Agent NEVER creates fake content
