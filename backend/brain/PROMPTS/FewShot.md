# Few-Shot Examples

## Employer (20 examples)

### E01
Input: Tražimo 5 radnika za berbu malina Arilje, smeštaj i 3 obroka obezbeđeni, dnevnica 5000 RSD. Kontakt 064-111-222.
Classification: employer_job_post | Risk: low | Action: approve_with_edits | Digest: true

### E02
Input: Potrebni radnici za plastenik, Subotica. Smeštaj obezbeđen. 060-123-4567
Classification: employer_job_post | Risk: low | Action: approve_with_edits | Digest: true

### E03
Input: Zapošljavamo radnike za pakovanje voća. Plata 4000 dnevno. Kontakt 065-123-456.
Classification: employer_job_post | Risk: low | Action: approve_with_edits | Digest: true

### E04
Input: Berba malina — tražimo berače. Arilje. Smeštaj i hrana. 063-111-222.
Classification: employer_job_post | Risk: low | Action: approve_with_edits | Digest: true

### E05
Input: Hitno potrebni radnici za berbu višanja, Čačak. Dnevnica 5000. 064-555-666.
Classification: employer_job_post | Risk: low | Action: approve | Digest: true

### E06–E20
*(Pattern: any text with employer signal + job type + location + contact → employer_job_post)*

## Worker Request (20 examples)

### W01
Input: Tražim posao, imam iskustvo u poljoprivredi. 064-123-4567
Classification: worker_request | Risk: low | Action: approve_with_edits | Digest: false

### W02
Input: Treba mi posao u građevini, Subotica. Radio sam 3 godine.
Classification: worker_request | Risk: low | Action: approve_with_edits | Digest: false

### W03–W20
*(Pattern: any text with "tražim posao"/"treba mi" + no employer signal → worker_request)*

## Worker Group (20 examples)

### WG01
Input: Imam ekipu 30 ljudi sa svojim prevozom, tražimo berbu. Kontakt 064-988-5113
Classification: worker_group_available | Risk: low | Action: ask_missing_info | Digest: false

### WG02
Input: Nas je 5, tražimo poslodavca za berbu. Dostupni od ponedeljka.
Classification: worker_group_available | Risk: low | Action: ask_missing_info | Digest: false

### WG03–WG20
*(Pattern: "imam ekipu"/"nas je N"/"grupa radnika" + no employer signal → worker_group_available)*

## Spam (20 examples)

### S01
Input: KAZINO online! Dobijate 500e bonusa! www.casino.rs
Classification: spam | Risk: high | Action: mark_spam | Digest: false

### S02
Input: Crypto trading, bitcoin, forex. Zaradite od kuće!
Classification: spam | Risk: high | Action: mark_spam | Digest: false

### S03–S20
*(Pattern: casino/crypto/forex/kladionica/brza zarada → spam, high, never publish)*

## Suspicious (20 examples)

### X01
Input: Uplata unapred 50e za rezervaciju mesta. Depozit obavezan.
Classification: suspicious | Risk: high | Action: escalate | Digest: false

### X02
Input: Pošaljite sliku pasoša i lične karte. Plata 2000e dnevno!
Classification: suspicious | Risk: high | Action: escalate | Digest: false

### X03–X20
*(Pattern: advance payment/document request/JMBG/unrealistic pay → suspicious)*

## Review (10 examples)

### R01
Input: Radio sam u hladnjači u Smederevu tri meseca. Plata 55000, smeštaj loš.
Classification: review_experience | Risk: medium | Action: approve_with_edits | Digest: false

### R02–R10
*(Pattern: "radio sam"/"moje iskustvo" → review)*

## Question (10 examples)

### Q01
Input: Da li neko zna kakvi su uslovi za sezonski rad u hladnjači?
Classification: question | Risk: low | Action: approve | Digest: false

### Q02–Q10
*(Pattern: "da li"/"kako"/"gde" + no job offer/request → question)*
