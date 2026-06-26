---
type: operator_action_list
date: 2026-06-26
operator: Andrii
status: pending
---

# Operator Action List — 2026-06-26

## Šta operator treba ručno da uradi danas

### 1. Pregledaj i odobri postove za objavu (5 postova)

Sledeći postovi su spremni u `post-queue/ready/`. Svaki post treba pregledati, odobriti (`operator_approved: true`) i ručno objaviti na Facebook grupi.

| # | Post | Vrsta | Prioritet |
|---|------|-------|-----------|
| 1 | [[../post-queue/ready/2026-06-26-prvi-post-dobrodoslica]] | Dobrodošlica | 🔴 Prvi |
| 2 | [[../post-queue/ready/2026-06-26-sezona-malina-arilje-info]] | Info o sezoni | 🟠 Drugi |
| 3 | [[../post-queue/ready/2026-06-26-vocarsvo-jovic-oglas]] | Javni oglas | 🟡 Treći |
| 4 | [[../post-queue/ready/2026-06-26-kako-proveriti-poslodavca]] | Savet | 🟢 Četvrti |
| 5 | [[../post-queue/ready/2026-06-26-poziv-poslodavcima]] | Poziv | 🔵 Peti |

**Proces za svaki post:**
1. Otvori post u `post-queue/ready/`
2. Kopiraj tekst
3. Pokreni Admin Copilot proveru (opciono)
4. Postavi `operator_approved: true`
5. Ručno objavi na Facebook grupi
6. Dodaj `facebook_post_url` u YAML
7. Promeni `posted_to_facebook: true`
8. Pomeri fajl u `post-queue/posted/`

---

### 2. Outreach — prvi kontakti (izaberi 3 od 10)

Targeti su spremni u `outreach/target-groups/`. Izaberi **maksimalno 3** za prvi dan.

| # | Target | Jezik | Poruka |
|---|--------|-------|--------|
| 1 | [[../outreach/target-groups/sezonski-poslovi-hrvatska]] | Srpski | `cross-post` |
| 2 | [[../outreach/target-groups/beraci-malina-zapadna-srbija]] | Srpski | `invitation_worker` |
| 3 | [[../outreach/target-groups/rabota-v-serbii-rus]] | Ruski | `cross-post` |
| 4 | [[../outreach/target-groups/ukrajinci-u-srbiji]] | Ukrajinski | `invitation_worker` |
| 5 | [[../outreach/target-groups/poslovi-srem]] | Srpski | `invitation_employer` |
| 6 | [[../outreach/target-groups/sezonski-rad-srbija-bih]] | Srpski | `cross-post` |
| 7 | [[../outreach/target-groups/poslovi-subotica]] | Srpski | `invitation_worker` |
| 8 | [[../outreach/target-groups/poslovi-za-strance-srbija]] | Engleski | `cross_post` |
| 9 | [[../outreach/target-groups/magyarok-szerbiaban]] | Mađarski | `invitation_worker` |
| 10 | [[../outreach/target-groups/romanii-in-serbia]] | Rumunski | `invitation_worker` |

**Proces za svaki target:**
1. Otvori target fajl
2. Idi u `templates/<jezik>/` i kopiraj odgovarajuću poruku
3. Postavi `operator_approved: true`
4. Ručno postavi poruku u ciljnu grupu
5. Postavi `operator_posted: true`
6. Dodaj datum u `last_contacted`
7. Zabeleži rezultat
8. Kreiraj dnevni log u `outreach/daily-logs/YYYY-MM-DD.md`

---

### 3. Provera vakansija (opciono)

Svih 10 vakansija u `vacancies/` ima status `needs_clarification`. Nijedna nije potvrđena direktno kod poslodavca.

Ako želiš da započneš proveru:
1. Izaberi jednu vakansiju (npr. `2026-06-26-berba-malina-arilje`)
2. Kontaktiraj poslodavca telefonom (ako ima kontakt) ili putem platforme
3. Postavi `verified_by_operator: true` nakon provere
4. Promeni `status: ready_to_post` ako je sve potvrđeno

---

### 4. Dnevni izveštaj

Na kraju dana:
1. Ažuriraj `reports/2026-06-26.md` sa današnjim brojkama
2. Ažuriraj KPI u `00-dashboard.md`

---

## Provera — pre nego što počneš

- [ ] Pročitao/la sam `02-rules.md` i razumem pravila
- [ ] Razumem da nijedna vakansija nije proverena
- [ ] Razumem da sve akcije na Facebooku radim ručno
- [ ] Razumem da ne obećavam "proverene poslove"

---

## Podsetnik

> ⚠️ **Operator-in-the-Loop:** Sve Facebook akcije se izvode ručno. Agent samo priprema, klasifikuje i predlaže. Ništa nije automatizovano.

> 📌 **Format objave:** Svaki javni oglas mora imati napomenu: "Grupa nije poslodavac i ne garantuje uslove. Pre odlaska obavezno proverite..."

> 🚫 **Ne objavljuj:** lažne vakansije, lažne recenzije, tuđe lične podatke, spam, kazino, kredite, kripto.
