# Edge Cases

## Employer Post with Missing Pay

If employer post has contact + location + job_type but no pay:
- Classification: employer_job_post
- Risk: medium (missing pay)
- Action: approve_with_edits
- Digest: yes, with "Dnevnica nije navedena"

## Employer Post with Only Phone

If employer post only has a phone number and "tražimo radnike":
- Classification: employer_job_post
- Risk: medium (missing location, pay, conditions)
- Action: ask_missing_info
- Digest: no (insufficient info)

## Worker Group with Number of People

"Imam ekipu 30 ljudi sa svojim prevozom":
- Classification: worker_group_available
- Extract: workers_count=30, transport=own
- Missing: job_type, location, pay_expectation, phone
- Action: ask_missing_info

## Review Without Employer Name

"Radio sam u hladnjači, smeštaj loš, plata ok":
- Classification: review_experience
- Missing: employer_name, location, work_period
- Action: approve_with_edits (keep factual, remove emotion)

## Angry Review

"On je lopov i prevarant, ne idite tamo!":
- Classification: review_experience
- Risk: high (insults, absolute accusations)
- Action: escalate (cannot just edit — needs operator decision)

## Anonymous Warning

"Čuvajte se poslodavca iz Surčina, ne plaća!":
- Classification: suspicious
- Risk: high (anonymous accusation)
- Action: escalate

## Repeated Post

Same employer, same phone, similar text as previously seen:
- Classification: duplicate
- Action: mark_duplicate
- Digest: no (unless operator explicitly marks as repeat_candidate)

## Old Post

Post date is >7 days old:
- Freshness: stale
- Action: escalate (may still be valid, operator decides)

## Non-Seasonal Work

"Tražim posao programer, Python, remote":
- Classification: irrelevant
- Action: reject

## Unknown Intermediary

"Tražimo radnike za inostranstvo, javite se agentu":
- Classification: suspicious
- Risk: high (unclear intermediary, non-Serbia)
- Action: escalate

## Mixed Serbian/Russian Text

Text contains both languages:
- Detect primary language by majority words
- Extract info from both
- Public text in Serbian
- Operator summary in Russian

## Unclear Location

"U Srbiji", "na selu", "kod mene":
- Location: extract as-is
- Missing: flag "neprecizna lokacija"
- Digest: may include if contact is present

## Unclear Contact

"Inbox only", no phone:
- Contact: inbox
- Missing: flag "kontakt samo inbox"
- Risk: medium (inbox is less reliable than phone)
- Digest: may include with warning
