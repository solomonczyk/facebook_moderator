# Test Cases — Facebook Group Admin Copilot

## Overview

15 test cases covering every verdict, post type, and language as specified in the system design (section 21). Each test case includes the raw input, expected verdict, expected post type, and justification linked to the moderation policy.

---

## Test Case 001: Full Vacancy — APPROVE

**Input:**
> Tražimo radnike za berbu jabuka u Čačku. Početak 1. septembra. Potrebno 10 radnika. Plata 5.000 din dnevno, isplata svake subote na ruke. Radno vreme 7-15h. Smeštaj obezbeđen, hrana obezbeđena (doručak i ručak). Prevoz po dogovoru. Radnici prijavljeni. Kontakt: Marko 064-123-45-67.

**Expected Verdict:** APPROVE
**Expected Post Type:** vacancy
**Expected Risk:** low
**Expected Language:** Serbian

**Justification:** All 12 required vacancy fields are present: location, job type, start date, workers count, pay amount, payment method, working hours, accommodation, food, transport, contact, and worker registration. No problematic language.

---

## Test Case 002: Incomplete Vacancy — No Pay

**Input:**
> Potrebni radnici za građevinu u Novom Sadu. Radimo svaki dan. Javite se na 064-555-33-22.

**Expected Verdict:** NEEDS_CLARIFICATION
**Expected Post Type:** vacancy
**Expected Risk:** medium
**Expected Language:** Serbian

**Justification:** Missing most required fields: pay amount, payment method, working hours, start date, number of workers needed, accommodation info, food info, transport, worker registration. Contact is present but insufficient.

---

## Test Case 003: Incomplete Vacancy — No City

**Input:**
> Tražimo 5 radnika za pakovanje. Plata 60.000 mesečno. Smeštaj obezbeđen. Kontakt: 060-111-22-33.

**Expected Verdict:** NEEDS_CLARIFICATION
**Expected Post Type:** vacancy
**Expected Risk:** medium
**Expected Language:** Serbian

**Justification:** Missing location (city/town) — a critical field. Also missing: payment method, working hours, start date, food info, transport, worker registration.

---

## Test Case 004: Suspicious Vacancy — "Brza Zarada"

**Input:**
> BRZA ZARADA! Tražimo radnike, plata neverovatna! Bez iskustva, puno para! Javite se u inbox za više informacija.

**Expected Verdict:** REJECT
**Expected Post Type:** vacancy
**Expected Risk:** high
**Expected Language:** Serbian

**Justification:** Classic fraud pattern: "brza zarada", "bez iskustva, puno para", no concrete information, inbox-only contact. All red flags for scam. Per policy: suspicious vacancies with "easy money" language → REJECT.

---

## Test Case 005: Negative Worker Review — Factual

**Input:**
> Radio sam u hladnjači u Smederevu prošlog leta, tri meseca. Obećali su 70.000 mesečno sa smeštajem, ali su na kraju plaćali 55.000, a smeštaj je bio kontejner bez grejanja. Posao težak. Ne bih se vratio.

**Expected Verdict:** APPROVE
**Expected Post Type:** worker_review
**Expected Risk:** low
**Expected Language:** Serbian

**Justification:** Specific, factual, first-person experience. Concrete details about pay discrepancy and accommodation conditions. No insults, no personal data, no absolute accusations. Useful content for the group.

---

## Test Case 006: Review with Insults

**Input:**
> Ovaj govnar iz Leskovca je običan lopov! Radio sam kod njega i nije mi platio zadnju platu. Svi su tamo prevaranti i stoka. Ne idite tamo!

**Expected Verdict:** APPROVE_WITH_EDITS
**Expected Post Type:** worker_review
**Expected Risk:** high
**Expected Language:** Serbian

**Justification:** Has useful core experience (non-payment) but contains insults ("govnar", "stoka") and absolute accusations ("lopov", "prevaranti"). Per policy: useful content with insults → APPROVE_WITH_EDITS, apply safe rewrite rules.

**Safe rewrite required:**
> Radio sam kod poslodavca u Leskovcu. Prema mom ličnom iskustvu, nije mi isplatio poslednju platu. Ja ne bih preporučio ovo mesto bez dodatne provere uslova.

---

## Test Case 007: Review with Someone Else's Phone Number

**Input:**
> Radio sam sa Milanom iz Subotice. Loš poslodavac. Evo njegov broj: 064-987-65-43, zovite ga i recite mu da je prevarant.

**Expected Verdict:** APPROVE_WITH_EDITS
**Expected Post Type:** worker_review
**Expected Risk:** high
**Expected Language:** Serbian

**Justification:** Contains third-party phone number published without consent and call to harass. Per policy: personal data of others must be removed. The phone number + "zovite ga" is a serious personal data violation.

---

## Test Case 008: Off-Topic Post

**Input:**
> Prodajem iPhone 15, star mesec dana, kao nov. Cena 600 evra. Beograd, lično preuzimanje. 063-555-12-34.

**Expected Verdict:** REJECT
**Expected Post Type:** spam
**Expected Risk:** low
**Expected Language:** Serbian

**Justification:** Phone sale, completely unrelated to seasonal work in Serbia. Per policy: off-topic content → REJECT.

---

## Test Case 009: Job Request — Russian

**Input:**
> Здравствуйте, я из России. Ищу сезонную работу в Сербии, строительство или сельское хозяйство. Есть ли у кого-то контакты работодателей? Готов приступить через неделю.

**Expected Verdict:** APPROVE
**Expected Post Type:** job_request
**Expected Risk:** low
**Expected Language:** Russian

**Justification:** Relevant job request from a Russian-speaking worker. Clear, specific (construction or agriculture), ready timeline provided. No violations. Requires Serbian translation.

---

## Test Case 010: Complete Employer Vacancy

**Input:**
> Firma "Voćarstvo Jović" traži 20 radnika za berbu trešanja u okolini Valjeva. Početak 20. juna. Plata 4.500 din po danu, isplata dnevno. Radno vreme 6-14h. Smeštaj u našim bungalovima, hrana obezbeđena. Prevoz organizujemo iz Valjeva. Radnici prijavljeni na dan. Kontakt: Jovan 065-111-22-33 (Viber/WhatsApp).

**Expected Verdict:** APPROVE
**Expected Post Type:** vacancy
**Expected Risk:** low
**Expected Language:** Serbian

**Justification:** Complete vacancy with all 12 required fields and company name. Professional tone, no issues. Gold standard for group vacancies.

---

## Test Case 011: Russian → Serbian Translation Needed

**Input:**
> Я работал на стройке в Белграде два месяца. Зарплату платили вовремя, жильё было нормальное, питание за свой счёт. Работодатель адекватный. Могу рекомендовать.

**Expected Verdict:** APPROVE
**Expected Post Type:** worker_review
**Expected Risk:** low
**Expected Language:** Russian

**Justification:** Positive personal review in Russian. Needs Serbian translation for the group. No violations.

---

## Test Case 012: Hungarian → Serbian Translation Needed

**Input:**
> Sziasztok! Magyarországról jöttem. Keresek munkát Szerbiában mezőgazdaságban. Van tapasztalatom. Tudok dolgozni azonnal. Van valakinek elérhetősége? Köszönöm.

**Expected Verdict:** APPROVE
**Expected Post Type:** job_request
**Expected Risk:** low
**Expected Language:** Hungarian

**Justification:** Hungarian worker seeking agricultural work in Serbia. Clear request with relevant details. Needs Serbian translation.

---

## Test Case 013: Romanian → Serbian Translation Needed

**Input:**
> Bună ziua! Am lucrat în Vârșeț la o fabrică sezonieră. Condițiile au fost bune, salariul plătit la timp. Cazare oferită, mâncarea nu. Recomand pentru cei care caută muncă stabilă sezonieră.

**Expected Verdict:** APPROVE
**Expected Post Type:** worker_review
**Expected Risk:** low
**Expected Language:** Romanian

**Justification:** Positive Romanian review of seasonal factory work in Vršac. Factual, specific. Needs Serbian translation.

---

## Test Case 014: Worker-Employer Conflict

**Input:**
> Ovaj poslodavac "Gradnja Plus" iz Kragujevca nije isplatio plate za 3 meseca! Nas 10 radnika smo oštećeni! Znam da je on prijavio firmu na drugog čoveka da bi izbegao tužbe. Imaćemo protest ispred opštine! Ko hoće da nam se pridruži neka se javi.

**Expected Verdict:** ESCALATE
**Expected Post Type:** conflict
**Expected Risk:** high
**Expected Language:** Serbian

**Justification:** Serious allegations: multi-worker non-payment, alleged company registration fraud, call for public protest. Named company — high legal risk. Per policy: any post with serious allegations + potential legal risk → ESCALATE to admin.

---

## Test Case 015: Spam — Casino

**Input:**
> 🎰 NOVI ONLINE KAZINO U SRBIJI 🎰 Dobijate 500€ bonusa na prvi depozit! Igrajte rulet, blackjack, slotove! www.casino-balkan.rs Iskoristite priliku!

**Expected Verdict:** REJECT
**Expected Post Type:** spam
**Expected Risk:** high
**Expected Language:** Serbian

**Justification:** Casino advertisement, completely unrelated to seasonal work. Gambling is a prohibited topic. Per policy: spam → REJECT.

---

## Coverage Matrix

| # | Verdict | Post Type | Language | Risk |
|---|---------|-----------|----------|------|
| 001 | APPROVE | vacancy | Serbian | low |
| 002 | NEEDS_CLARIFICATION | vacancy | Serbian | medium |
| 003 | NEEDS_CLARIFICATION | vacancy | Serbian | medium |
| 004 | REJECT | vacancy | Serbian | high |
| 005 | APPROVE | worker_review | Serbian | low |
| 006 | APPROVE_WITH_EDITS | worker_review | Serbian | high |
| 007 | APPROVE_WITH_EDITS | worker_review | Serbian | high |
| 008 | REJECT | spam | Serbian | low |
| 009 | APPROVE | job_request | Russian | low |
| 010 | APPROVE | vacancy | Serbian | low |
| 011 | APPROVE | worker_review | Russian | low |
| 012 | APPROVE | job_request | Hungarian | low |
| 013 | APPROVE | worker_review | Romanian | low |
| 014 | ESCALATE | conflict | Serbian | high |
| 015 | REJECT | spam | Serbian | high |

**Verdict coverage:** APPROVE (7), APPROVE_WITH_EDITS (2), NEEDS_CLARIFICATION (2), REJECT (3), ESCALATE (1)
**Post type coverage:** vacancy (4), worker_review (5), job_request (2), spam (2), conflict (1), others (1)
**Language coverage:** Serbian (11), Russian (2), Hungarian (1), Romanian (1)
**Risk coverage:** low (9), medium (2), high (4)
