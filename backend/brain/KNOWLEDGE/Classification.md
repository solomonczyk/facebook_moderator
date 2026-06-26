# Classification Policy

## Categories

### employer_job_post

**Definition**: An employer, recruiter, or intermediary posting a seasonal job offer.

**Indicators**: tražimo, potrebni radnici, zapošljavamo, firma traži, hitno potrebno, za berbu, za branje, plastenik, hladnjača, plata, dnevnica, smeštaj obezbeđen.

**Action**: approve_with_edits (if incomplete) or approve (if complete).

**Digest**: YES, if has location + contact + job_type.

**Example**: "Tražimo 5 radnika za berbu malina Arilje. Smeštaj i 3 obroka obezbeđeni. Dnevnica 5000 RSD. Kontakt 064-111-222."

### worker_request

**Definition**: An individual worker looking for a job.

**Indicators**: tražim posao, treba mi posao, dostupan sam, imam iskustvo, radio sam.

**Action**: approve_with_edits. Ask for: location preference, job type, availability, phone.

**Digest**: NO (separate worker section).

### worker_group_available

**Definition**: A group/team of workers available for hire.

**Indicators**: imam ekipu, imamo grupu, nas je N, grupa radnika, sa svojim prevozom, N ljudi, tražimo poslodavca.

**Action**: approve_with_edits. Ask for: job type preference, availability date, pay expectation, phone, accommodation needs.

**Digest**: NO (separate worker section).

### review_experience

**Definition**: Worker sharing experience with an employer or worksite.

**Indicators**: radio sam, radila sam, moje iskustvo, preporučujem, ne preporučujem, uslovi su bili, plata je bila.

**Action**: approve_with_edits. Remove insults, keep facts. Add safe wording: "Prema mom iskustvu..."

**Digest**: NO.

### question

**Definition**: Question about seasonal work, conditions, procedures, or rights.

**Indicators**: pitanje, da li neko zna, kako da, gde mogu, koliko, šta treba.

**Action**: approve or approve_with_edits.

**Digest**: NO.

### spam

**Definition**: Unwanted commercial content, scams, casino, crypto.

**Indicators**: kazino, casino, crypto, bitcoin, forex, brza zarada, laka zarada, kladionica, online kazino, klikni.

**Action**: mark_spam. NEVER publish.

**Risk**: ALWAYS high.

### suspicious

**Definition**: Content with red flags: advance payment, document requests, too-good-to-be-true, unclear intermediary.

**Indicators**: uplata unapred, depozit, JMBG, slika pasoša, lična karta, plata 2000e, pošaljite dokumenta, samo inbox.

**Action**: escalate. NEVER publish.

**Risk**: ALWAYS high.

### irrelevant

**Definition**: Content not related to seasonal work in Serbia.

**Action**: reject.

### unclear

**Definition**: Cannot determine what the content is about.

**Action**: escalate.
