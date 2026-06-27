# Few-Shot Examples

Each example includes input text and the expected output classification, risk, recommended action, digest eligibility, and reasoning.

---

## Employer Job Posts (20 examples)

### E01
**Input:** Tražimo 5 radnika za berbu malina Arilje, smeštaj i 3 obroka obezbeđeni, dnevnica 5000 RSD. Kontakt 064-111-222.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Complete employer post with location, pay, conditions, and contact. Missing disclaimer.

### E02
**Input:** Potrebni radnici za plastenik, Subotica. Smeštaj obezbeđen. 060-123-4567
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post with job type, location, accommodation, and contact. Missing pay and food info.

### E03
**Input:** Zapošljavamo radnike za pakovanje voća. Plata 4000 dnevno. Kontakt 065-123-456.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post with job type, pay, and contact. Missing location and conditions.

### E04
**Input:** Berba malina — tražimo berače. Arilje. Smeštaj i hrana. 063-111-222.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Clear employer post. Location, conditions, contact present. Missing pay and worker count.

### E05
**Input:** Hitno potrebni radnici za berbu višanja, Čačak. Dnevnica 5000. 064-555-666.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Complete: job type, location, pay, contact. Acceptable as-is with disclaimer.

### E06
**Input:** Treba nam 10 radnika za građevinu u Novom Sadu. Plata 60000 mesečno. Smeštaj obezbeđen. Kontakt 069-333-444.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Complete employer post for construction. All key fields present.

### E07
**Input:** Gazdinstvo traži radnike za berbu jabuka, Bajina Bašta. Dnevnica po dogovoru. Hrana obezbeđena. 062-111-333.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post. Pay unclear ("po dogovoru"). Missing accommodation and transport info.

### E08
**Input:** Firma "Voće plus" zapošljava sezonske radnike u hladnjači. Lokacija Smederevo. Rad u dve smene. Plata redovna. 061-222-444.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Named employer, location, job type. Missing concrete pay amount, conditions details.

### E09
**Input:** Tražimo radnice za sortiranje borovnica. Srem, okolina Šida. Prevoz organizovan. Dnevnica 4500. Kontakt Viber 064-777-888.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post with job type, location, pay, transport, Viber contact. Missing food/accommodation.

### E10
**Input:** Potrebni berači za maline — berba počinje 1. jula. Ivanjica. Smeštaj u bungalovu, 3 obroka. Dnevnica 5000-6000 u zavisnosti od učinka. Pozvati 064-123-789.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Well-written employer post. Start date, location, accommodation type, food, pay range, contact.

### E11
**Input:** Tražimo 3 radnika za farmu, okolina Beograda. Dnevnica 4000. Smeštaj obezbeđen. WhatsApp 065-111-222.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post. Job type vague ("farma"). Missing food and transport info.

### E12
**Input:** Berba kupina — potrebni radnici hitno. Prijepolje. Plata po kilogramu 120 RSD. Smeštaj i hrana obezbeđeni. Kontakt 063-444-555.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Complete employer post. Location, pay type (per kg), conditions, contact.

### E13
**Input:** Strani poslodavac traži radnike za sezonski rad u poljoprivredi. Srbija, okolina Subotice. Smeštaj kontejner. Plata 5500 dnevno. Javite se na 060-333-111.
**Classification:** employer_job_post | **Risk:** medium | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post. "Strani poslodavac" vague. Accommodation "kontejner" worth noting. Otherwise complete.

### E14
**Input:** Tražimo radnike za branje šljiva. Šumadija, okolina Kragujevca. Dnevnica 5000, isplata na ruke. Smeštaj i prevoz obezbeđeni. Kontakt 064-123-987.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Clear, complete employer post. All key fields present.

### E15
**Input:** Potreban radnik za održavanje plastenika. Okolina Leskovca. Plata 60000 mesečno. Smeštaj moguć. 062-555-777.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post. "Smeštaj moguć" is unclear. Missing food and transport info.

### E16
**Input:** Tražimo 15 radnika za berbu trešanja, okolina Čačka. Prevoz organizovan, smeštaj obezbeđen. Dnevnica 5000. Kontakt Viber/WhatsApp 064-999-000.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Complete employer post with worker count, location, conditions, pay, multi-channel contact.

### E17
**Input:** Zapošljavamo sezonske radnike za branje i pakovanje jagoda. Srem. Rad 8h dnevno. Plata 4500 dnevno + smeštaj. 069-111-555.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Good employer post. Working hours specified, pay with accommodation. Missing food info.

### E18
**Input:** Tražimo radnike za berbu jabuka. Južna Srbija, okolina Vranja. Dnevnica po dogovoru. Hrana obezbeđena. Kontakt 063-222-111.
**Classification:** employer_job_post | **Risk:** medium | **Action:** approve_with_edits | **Digest:** true
**Reason:** Employer post but location vague ("Južna Srbija") and pay unclear. Missing accommodation.

### E19
**Input:** Hitno! Trebaju radnici za sezonski rad u Nemačkoj. Organizovan prevoz iz Srbije. Smeštaj obezbeđen. Plata 2000e mesečno. Kontakt agencija 064-111-333.
**Classification:** employer_job_post | **Risk:** medium | **Action:** escalate | **Digest:** false
**Reason:** Cross-border job via agency. "Agencija" needs verification. Not Serbia-based work.

### E20
**Input:** Berba borovnica — Subotica. Tražimo 20 radnika. Smeštaj, 2 obroka, prevoz — sve obezbeđeno. Dnevnica 5000 RSD. Početak 5. jula. Prijava na 064-555-000.
**Classification:** employer_job_post | **Risk:** low | **Action:** approve | **Digest:** true
**Reason:** Exemplary employer post. All fields covered: count, location, conditions, pay, start date, contact.

---

## Worker Requests (20 examples)

### W01
**Input:** Tražim posao, imam iskustvo u poljoprivredi. 064-123-4567
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker seeking job. Missing: location preference, job type, availability.

### W02
**Input:** Treba mi posao u građevini, Subotica. Radio sam 3 godine.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with location and field specified. Missing: contact, availability, pay expectation.

### W03
**Input:** Student traži sezonski posao, dostupan jul-avgust. Mogu bilo koji posao. Kontakt 065-111-222.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with availability window. Missing: location preference, specific job type.

### W04
**Input:** Tražim posao branje malina, imam 2 godine iskustva. Arilje ili okolina. 060-333-444.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with job type, experience, location preference, and contact.

### W05
**Input:** Treba mi posao u poljoprivredi, bilo gde u Vojvodini. Imam svoj prevoz. 063-555-666.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with transport, region, and contact. Missing specific job type.

### W06
**Input:** Radio sam 5 godina u plastenicima, tražim posao. Dostupan od ponedeljka. Javite se inbox.
**Classification:** worker_request | **Risk:** medium | **Action:** approve_with_edits | **Digest:** false
**Reason:** Experienced worker but contact is inbox only. Missing location preference and phone.

### W07
**Input:** Žena 45 godina traži posao u pakovanju ili sortiranju. Okolina Beograda. Kontakt 064-777-888.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with age context, job type preferences, location, and contact.

### W08
**Input:** Tražim hitno posao! Bilo šta, samo da ima smeštaj. Mogu odmah. 062-111-000.
**Classification:** worker_request | **Risk:** medium | **Action:** ask_missing_info | **Digest:** false
**Reason:** Urgent worker request. Vague ("bilo šta"). Missing: location preference, job experience, specific skills.

### W09
**Input:** Radnik iz Ukrajine traži sezonski posao u Srbiji. Iskustvo u građevini i poljoprivredi. Govorim ruski, ukrajinski. Viber +380-99-111-22-33.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Foreign worker seeking work in Serbia. Languages specified, experience, international contact.

### W10
**Input:** Tražim posao berba, pakovanje — imam iskustvo. Srem ili okolina. 069-222-333.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with job types, region, and contact. Missing availability details.

### W11
**Input:** Dvoje radnika traži posao — muž i žena. Iskustvo u berbi voća. Treba nam smeštaj. 064-111-444.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Couple seeking work. Need accommodation. Missing location preference and availability.

### W12
**Input:** Tražim sezonski posao, mogu da radim kao berač ili u pakovanju. Imam 28 godina. Kontakt 065-333-111.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Young worker with job type preferences and contact. Missing location preference.

### W13
**Input:** Treba mi posao na farmi ili gazdinstvu. Radim sve poslove. Okolina Novog Sada. 060-444-222.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker seeking farm work with location and contact.

### W14
**Input:** Iskusan radnik u hladnjači traži posao. Radio 3 sezone. Smederevo, Požarevac, okolina. 063-111-555.
**Classification:** worker_request | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Experienced worker, specific field, location area, contact provided.

### W15
**Input:** Tražim posao — imam iskustvo u berbi malina i kupina. Trebam prevoz. 062-777-333.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with specific crop experience. Needs transport. Missing location preference.

### W16
**Input:** Mladić 20 godina traži sezonski posao. Bez iskustva ali spreman da radi. Mogu bilo gde. 064-000-111.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Young first-time worker. No experience but willing. Missing job type preference.

### W17
**Input:** Tražim posao, najbolje berba ili plastenik. Iz Arilja sam. Imam smeštaj kod kuće. 060-555-000.
**Classification:** worker_request | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Worker from key raspberry region with local housing. Good candidate for local farms.

### W18
**Input:** Radnica traži posao u sortiranju voća ili pakovanju. Okolina Čačka. Dostupna od 1. jula. Kontakt 064-222-555.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with specific job types, location, start date, and contact.

### W19
**Input:** Treba mi posao hitno! Samohrana majka, imam iskustvo u berbi. Okolina Kraljeva. Molim ponude. Inbox ili 063-999-111.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Worker with urgency note. Has experience, location, and contact. Personal context noted.

### W20
**Input:** Tražim posao sezonski rad. Govorim srpski i mađarski. Iskustvo u poljoprivredi Mađarska 2 godine. Sada u Subotici. Kontakt 064-888-222.
**Classification:** worker_request | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Bilingual worker with international experience. Located in Subotica with contact.

---

## Worker Groups (20 examples)

### WG01
**Input:** Imam ekipu 30 ljudi sa svojim prevozom, tražimo berbu. Kontakt 064-988-5113
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Large group with transport. Missing: location preference, job type detail, availability, pay expectation.

### WG02
**Input:** Nas je 5, tražimo poslodavca za berbu. Dostupni od ponedeljka.
**Classification:** worker_group_available | **Risk:** medium | **Action:** ask_missing_info | **Digest:** false
**Reason:** Small group. Missing: contact, location, transport status, accommodation needs.

### WG03
**Input:** Grupa radnika dostupna za sezonski rad. Ima nas 12. Svoj kombi. Tražimo posao u poljoprivredi. Kontakt 065-111-999.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Group of 12 with vehicle. Missing: location preference, availability dates, pay expectation.

### WG04
**Input:** Moja ekipa traži posao, 10 ljudi. Svi sa iskustvom u berbi. Treba nam smeštaj. Javite se na Viber 064-222-111.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Experienced group needing accommodation. Missing: location preference, availability.

### WG05
**Input:** Tri porodice traže sezonski posao — ukupno 8 radnika. Imamo svoj prevoz, treba nam smeštaj. Kontakt 062-333-444.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Family group (8 workers) with transport. Need accommodation. Missing job type and location.

### WG06
**Input:** Ekipa od 6 radnika iz Prijepolja traži berbu. Imamo iskustvo. Dostupni odmah. 060-111-222.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Group from specific town, experienced, available immediately. Missing pay expectation.

### WG07
**Input:** Nas 15 iz Bosne traži sezonski posao u Srbiji. Iskustvo u građevini i poljoprivredi. Treba smeštaj. 064-555-111.
**Classification:** worker_group_available | **Risk:** medium | **Action:** ask_missing_info | **Digest:** false
**Reason:** Cross-border group. Need accommodation. Missing: specific location, availability dates, pay expectation.

### WG08
**Input:** Imam ekipu od 4 čoveka, tražimo posao na građevini. Svi smo majstori. Kontakt 063-777-222.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Small skilled group, specific trade. Missing location preference and availability.

### WG09
**Input:** Ekipa berača iz Ivanjice, 20 ljudi. Tražimo poslodavca za sezonu malina. Svi iskusni. 064-999-555.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Large experienced group from key raspberry region. Specific crop season. Good match potential.

### WG10
**Input:** Nas je 3, braća. Tražimo bilo koji posao u poljoprivredi. Imamo svoj auto. Okolina Čačka. Kontakt Viber 065-111-000.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Small family group with transport and general location. Missing job type preferences.

### WG11
**Input:** Grupa 8 radnika traži posao u berbi višanja ili malina. Svi sa iskustvom 3+ sezone. Treba smeštaj i hrana. Dostupni od 25. juna. 069-333-000.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Experienced group. Good detail: crop preference, experience level, start date. Missing pay expectation.

### WG12
**Input:** Ekipa 25 ljudi iz okoline Užica traži posao. Imamo 2 kombija. Tražimo berbu. Kontakt 064-111-777.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Large local group with vehicles. Missing availability dates and pay expectation.

### WG13
**Input:** Radnici iz Makedonije — grupa 7 ljudi. Tražimo sezonski posao u Srbiji. Govorimo srpski. Treba smeštaj. 062-444-111.
**Classification:** worker_group_available | **Risk:** medium | **Action:** ask_missing_info | **Digest:** false
**Reason:** Cross-border group speaking Serbian. Need accommodation. Missing specific job type and location.

### WG14
**Input:** Dve porodice, ukupno 6 radnika. Tražimo posao u plasteniku ili pakovanju. Treba smeštaj. Javite se na 060-666-333.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Family groups with job type preferences. Need accommodation. Missing location.

### WG15
**Input:** Imam grupu od 12 iskusnih berača. Tražimo berbu borovnica, Srem ili okolina. Svi imamo dokumenta. Kontakt 064-888-999.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Experienced group with specific crop and region preference. Documentation mentioned.

### WG16
**Input:** Tražimo poslodavca za sezonu. Nas 4, svi radili u hladnjači. Imamo svoj smeštaj u Smederevu. 063-555-888.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Small group with own accommodation in specific city. Cold storage experience.

### WG17
**Input:** Ekipa 9 ljudi, sve radnice. Iskustvo u sortiranju i pakovanju voća. Treba prevoz. Okolina Subotice. Kontakt 069-111-777.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Female worker group with specific skills. Need transport. Missing availability dates.

### WG18
**Input:** Nas 18 iz Leskovca, tražimo bilo koji sezonski posao. Svi sa iskustvom. Imamo prevoz. Treba smeštaj. 062-222-000.
**Classification:** worker_group_available | **Risk:** low | **Action:** ask_missing_info | **Digest:** false
**Reason:** Large group from south Serbia. Have transport, need accommodation. No job type preference.

### WG19
**Input:** Grupa radnika iz Rumunije, 5 ljudi. Tražimo posao 2 meseca u Srbiji. Iskustvo u poljoprivredi. Kontakt WhatsApp +40-722-111-222.
**Classification:** worker_group_available | **Risk:** medium | **Action:** ask_missing_info | **Digest:** false
**Reason:** Foreign group, limited duration. International contact. Missing specific job type and location.

### WG20
**Input:** Ekipa berača malina — 22 čoveka, Arilje, Ivanjica, Guča. Svi iskusni. Imamo svoj smeštaj i prevoz. Tražimo poslodavca za celu sezonu. Kontakt 064-511-9883.
**Classification:** worker_group_available | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Large experienced group from key raspberry triangle. Self-sufficient (own housing, transport). Full season.

---

## Spam (20 examples)

### S01
**Input:** KAZINO online! Dobijate 500e bonusa! www.casino.rs
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Explicit casino promotion. Never publish. Highest risk.

### S02
**Input:** Crypto trading, bitcoin, forex. Zaradite od kuće!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Crypto/forex scam bait. Multiple spam signals. Mark as spam.

### S03
**Input:** Brza zarada! 200e dnevno bez iskustva! Klikni ovde: bit.ly/xxx
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** "Brza zarada" + suspicious link. Classic spam pattern.

### S04
**Input:** Laka zarada od kuće. Samo 2 sata dnevno. Plata 1000e nedeljno! Inbox.
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** "Laka zarada" + unrealistic pay + inbox only. Multiple red flags.

### S05
**Input:** Online kladionica — duplirajte svoj depozit! Besplatan bonus!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Betting promotion. "Kladionica" explicit. Mark as spam.

### S06
**Input:** Forex trading signali. Profit zagarantovan. Pridružite se VIP grupi!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Forex + guaranteed profit claim. Both are spam signals.

### S07
**Input:** Kripto valute — investirajte danas, zaradite sutra! Bitcoin, Ethereum.
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Crypto investment pitch. No relation to seasonal work.

### S08
**Input:** MLM posao! Postanite distributer, zaradite 5000e mesečno. Javite se za detalje.
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** MLM / network marketing. Pyramid scheme bait. Mark as spam.

### S09
**Input:** Prodajem preparate za mršavljenje! Čudo prirode! www.dodatak-ishrani.rs
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Unrelated product sales. External link. Not seasonal work.

### S10
**Input:** Zaradite pare od telefona! Samo instalirajte aplikaciju: link u opisu!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Phone app promotion scam. Suspicious link. Mark as spam.

### S11
**Input:** KAZINO BONUS DO 100000 RSD! Registrujte se odmah!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Casino bonus offer. Explicit gambling promotion.

### S12
**Input:** Trebate pare hitno? Krediti do 500000 RSD bez žiranta!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Loan/credit offer. Financial product targeting vulnerable workers.

### S13
**Input:** Posao! Plata 3000e mesečno! Samo 2 sata rada dnevno od kuće! Javite se sada!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Unrealistic pay + minimal hours. Classic too-good-to-be-true spam.

### S14
**Input:** Besplatno!!! Klikni i osvoji iPhone! www.nagrada-rs.com
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Prize scam. External link. No seasonal work context.

### S15
**Input:** Chain message: "Pošalji ovo 10 prijatelja ili će ti se desiti..."
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Chain message / spam. No content value. Mark as spam.

### S16
**Input:** Online posao — kucanje tekstova. Plata 500e dnevno. Inbox za info.
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Fake online job (typing scam). Unrealistic pay. Not seasonal work.

### S17
**Input:** Prodajem zlato, nakit, satovi — povoljno! Kontakt 06x-xxx-xxx.
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Unrelated product sales. Not seasonal work. Mark as spam.

### S18
**Input:** Zarada na internetu — GARANTOVANO! Samo 15 minuta dnevno!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** "Garantovano" internet earning scam. Multiple spam signals.

### S19
**Input:** Seks oglas!!! Devojke iz tvog grada! Klikni link: xxx-xxx.xyz
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Adult content spam. Explicit and unrelated. Immediate mark as spam.

### S20
**Input:** Investicioni fond — uložite 100e, dobijate 1000e za 30 dana!
**Classification:** spam | **Risk:** high | **Action:** mark_spam | **Digest:** false
**Reason:** Investment/Ponzi scheme. Explicit scam pattern. Mark as spam.

---

## Suspicious (20 examples)

### X01
**Input:** Uplata unapred 50e za rezervaciju mesta. Depozit obavezan.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Advance payment + deposit. This is NEVER acceptable. Escalate immediately.

### X02
**Input:** Pošaljite sliku pasoša i lične karte. Plata 2000e dnevno!
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Document photo request + unrealistic pay. Identity theft risk. Escalate.

### X03
**Input:** JMBG obavezan za prijavu. Pošaljite dokumenta pre dolaska.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** JMBG request + documents before arrival. Could be legitimate registration but MUST be escalated.

### X04
**Input:** Tražimo radnike za inostranstvo — javite se agentu. Ne znamo tačno koja zemlja.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Unknown intermediary + unknown destination country. Classic trafficking red flag.

### X05
**Input:** Samo inbox! Plata neverovatna, uslovi odlični. Ne pitajte mnogo.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Secrecy pattern. Inbox only. Avoids questions. Highly suspicious.

### X06
**Input:** Trebate posao? Javite se meni. Ja sve sredim. Samo donesite pare za dokumentaciju.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Intermediary asking for money for "documentation." Exploitation red flag.

### X07
**Input:** Posao u Švajcarskoj! Plata 5000e. Ne treba znanje jezika. Javite se odmah, mesta ograničena!
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Unrealistic foreign job. "Mesta ograničena" urgency tactic. Likely trafficking or scam.

### X08
**Input:** Dokumenta unapred: lična karta, zdravstvena knjižica, diploma. Pošaljite skenirano pre dolaska.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Multiple document requests before any contract or meeting. Escalate.

### X09
**Input:** Rad na brodu — krstarenje. Plata 3000e mesečno. Samo uplatite kotizaciju 200e za ukrcavanje.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Advance payment ("kotizacija") for job placement. Classic recruitment scam. Escalate.

### X10
**Input:** Tražimo devojke za rad u inostranstvu. Smeštaj i avionska karta obezbeđeni. Javite se sa slikom.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Targeting women specifically + requesting photo + abroad. Trafficking red flags. Escalate.

### X11
**Input:** Posrednik traži radnike za "ozbiljnog" poslodavca. Ne otkrivamo ime firme. Plata odlična.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Anonymous intermediary hiding employer name. Non-transparent. Escalate.

### X12
**Input:** Berba u Grčkoj — sve plaćeno! Samo ponesite pasoš. Javite se agentu na Viber.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Foreign job via unknown agent. Unclear terms. Passport-only requirement concerning. Escalate.

### X13
**Input:** Hitno! 50 radnika za Italiju! Poljoprivreda. Bez prijave. Plaćanje na ruke. Kontakt WhatsApp.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** "Bez prijave" = undeclared work abroad. Illegal arrangement. Worker exploitation risk. Escalate.

### X14
**Input:** Tražim radnike za svoju firmu. Ne mogu da kažem koja firma. Javite se privatno.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Employer hiding identity. "Javite se privatno" secrecy pattern. Escalate.

### X15
**Input:** Plata 2000e dnevno!!! Samo 4 sata rada. Nije šala! Kontaktirajte me odmah.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Impossible pay claim. Excessive exclamation marks. Urgency pressure. Escalate.

### X16
**Input:** Pošaljite CV sa slikom na email. Radno mesto: menadžer. Ne treba iskustvo. Plata 2500e.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** CV with photo requested. Manager position without experience requirement. Unrealistic pay. Escalate.

### X17
**Input:** Agencija za zapošljavanje traži radnike. Naplaćujemo proviziju 10% od prve plate.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Agency charging workers commission. Potentially illegal recruitment fee. Escalate.

### X18
**Input:** Treba 100 radnika za berbu! Lokacija: saznaćete kad dođete. Autobus polazi iz Beograda.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Hidden location. Large recruitment without transparency. Transport to unknown. Escalate.

### X19
**Input:** Posao za penzionere — lako, plata 500e dnevno. Samo ponesite ličnu kartu i zdravstvenu.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Targeting elderly with unrealistic pay. Document collection. Escalate.

### X20
**Input:** Zapošljavamo! Radna viza za EU. Mi sredimo sve. Samo platite administrativnu taksu 300e unapred.
**Classification:** suspicious | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Advance payment for "visa processing." Classic migration scam. Escalate immediately.

---

## Reviews (10 examples)

### R01
**Input:** Radio sam u hladnjači u Smederevu tri meseca. Plata 55000, smeštaj loš.
**Classification:** review_experience | **Risk:** medium | **Action:** approve_with_edits | **Digest:** false
**Reason:** Genuine worker review. Edit: soften "smeštaj loš" to "smeštaj nije bio na očekivanom nivou."

### R02
**Input:** Moje iskustvo sa poslodavcem iz Valjeva — korektan, plata redovna, smeštaj pristojan. Preporučujem!
**Classification:** review_experience | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Positive review. Edit: add "prema mom iskustvu" framing and disclaimer.

### R03
**Input:** Ne preporučujem ovo mesto! Gazda ne isplaćuje radnike na vreme!
**Classification:** review_experience | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Serious accusation (non-payment). Cannot verify. Must escalate to operator.

### R04
**Input:** Radila sam tri meseca na farmi kod Novog Sada. Plata redovna, ali smeštaj u kontejneru.
**Classification:** review_experience | **Risk:** medium | **Action:** approve_with_edits | **Digest:** false
**Reason:** Factual review. Edit: keep experience but add neutral framing. Note accommodation type.

### R05
**Input:** Gazda korektan, smeštaj dobar, hrana odlična. Radio berbu malina prošle sezone.
**Classification:** review_experience | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Positive experience sharing. Edit: add temporal context (prošle sezone) and disclaimer.

### R06
**Input:** Užasno iskustvo! Radili smo 12 sati dnevno, plata kasnila 2 nedelje!
**Classification:** review_experience | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Serious allegations: excessive hours + late payment. Emotional language. Escalate for operator decision.

### R07
**Input:** Preporučujem gazdinstvo Petrović iz okoline Arilja. Sve po dogovoru, smeštaj čist, hrana domaća.
**Classification:** review_experience | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Positive named review. Edit: add "prema mom iskustvu iz [sezona]" framing.

### R08
**Input:** Radio sam u Nemačkoj preko ove agencije. Sve je bilo ok, ali provizija je bila velika.
**Classification:** review_experience | **Risk:** medium | **Action:** approve_with_edits | **Digest:** false
**Reason:** Review with agency mention. Flag agency info. Keep factual, add disclaimer.

### R09
**Input:** Berači, čuvajte se! Poslodavac iz Bajine Bašte ne plaća dogovoreno!
**Classification:** review_experience | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Warning with serious accusation but no details. Unverifiable claim. Escalate.

### R10
**Input:** Dve sezone radim kod istog poslodavca u Sremu. Berba borovnica. Uslovi su fer. Plata 5000 dnevno redovno.
**Classification:** review_experience | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Balanced, specific, multi-season review with concrete details. Acceptable as-is.

---

## Questions (10 examples)

### Q01
**Input:** Da li neko zna kakvi su uslovi za sezonski rad u hladnjači?
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** General question about cold storage work conditions. No red flags.

### Q02
**Input:** Kako da proverim poslodavca pre nego što odem na sezonski rad?
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Worker protection question. Encourage this type of inquiry. Safe to publish.

### Q03
**Input:** Kolika je dnevnica za maline ove sezone?
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Market information question. No sensitive data. Safe to publish.

### Q04
**Input:** Da li poslodavac mora da prijavi radnike za sezonski rad? Šta ako ne prijavi?
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Legal rights question. Important for workers. Safe to publish.

### Q05
**Input:** Gde mogu naći smeštaj ako radim u Arilju? Da li ima neki jeftin smeštaj?
**Classification:** question | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Practical accommodation question. Add: "Proverite smeštaj direktno sa poslodavcem."

### Q06
**Input:** Šta treba da ponesem kad idem na sezonski rad? Prvi put idem.
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** First-time worker practical question. Encourage group help. Safe.

### Q07
**Input:** Da li neko ima iskustvo sa radom u plasteniku? Kakva je razlika u odnosu na berbu?
**Classification:** question | **Risk:** low | **Action:** approve | **Digest:** false
**Reason:** Experience comparison question. Neutral, informative. Safe to publish.

### Q08
**Input:** Hitno pitanje! Poslodavac mi ne isplaćuje platu već 2 nedelje. Šta da radim?
**Classification:** question | **Risk:** high | **Action:** escalate | **Digest:** false
**Reason:** Worker in distress. Active non-payment situation. Legal implications. Escalate for operator attention.

### Q09
**Input:** Da li neko zna da li ima posla u okolini Leskovca? Tražim za brata.
**Classification:** question | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Job inquiry for relative. Vague but harmless. Edit: suggest posting as worker_request with specifics.

### Q10
**Input:** Planiram da idem na sezonski rad u Srbiju iz BiH. Šta mi treba od dokumenata?
**Classification:** question | **Risk:** low | **Action:** approve_with_edits | **Digest:** false
**Reason:** Cross-border work documentation question. Important practical info. Add disclaimer about verifying requirements.
