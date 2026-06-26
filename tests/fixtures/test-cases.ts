import type { TestCase } from '../../src/types.js';

/**
 * 15 test cases covering all verdicts, post types, and languages.
 * Maps to spec section 21 requirements.
 */
export const TEST_CASES: TestCase[] = [
  // 1. Good complete vacancy
  {
    id: '001_full_vacancy',
    description: 'Хорошая полная вакансия — все 12 обязательных полей присутствуют',
    input: `Tražimo radnike za berbu jabuka u Čačku. Početak 1. septembra. Potrebno 10 radnika. Plata 5.000 din dnevno, isplata svake subote na ruke. Radno vreme 7-15h. Smeštaj obezbeđen, hrana obezbeđena (doručak i ručak). Prevoz po dogovoru. Radnici prijavljeni. Kontakt: Marko 064-123-45-67.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'vacancy',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Serbian',
    expectedProblems: [],
    notes: 'All 12 required fields present: location, job type, start date, workers count, pay, payment method, hours, accommodation, food, transport, contact, registration.',
  },

  // 2. Incomplete vacancy — no pay
  {
    id: '002_incomplete_vacancy_no_pay',
    description: 'Неполная вакансия без оплаты',
    input: `Potrebni radnici za građevinu u Novom Sadu. Radimo svaki dan. Javite se na 064-555-33-22.`,
    expectedVerdict: 'NEEDS_CLARIFICATION',
    expectedPostType: 'vacancy',
    expectedRiskLevel: 'medium',
    expectedLanguage: 'Serbian',
    expectedProblems: ['plata', 'nije navedena', 'nepotpun'],
    notes: 'Missing: pay, payment method, hours, accommodation, food, registration, start date.',
  },

  // 3. Incomplete vacancy — no city
  {
    id: '003_incomplete_vacancy_no_city',
    description: 'Неполная вакансия без города',
    input: `Tražimo 5 radnika za pakovanje. Plata 60.000 mesečno. Smeštaj obezbeđen. Kontakt: 060-111-22-33.`,
    expectedVerdict: 'NEEDS_CLARIFICATION',
    expectedPostType: 'vacancy',
    expectedRiskLevel: 'medium',
    expectedLanguage: 'Serbian',
    expectedProblems: ['mesto rada', 'grad', 'lokacija'],
    notes: 'Missing: city/location, start date, payment method, hours, food, transport, registration. Has pay and contact.',
  },

  // 4. Suspicious vacancy "brza zarada"
  {
    id: '004_suspicious_vacancy_brza_zarada',
    description: 'Подозрительная вакансия с "brza zarada"',
    input: `BRZA ZARADA! Tražimo radnike, plata neverovatna! Bez iskustva, puno para! Javite se u inbox za više informacija.`,
    expectedVerdict: 'REJECT',
    expectedPostType: 'vacancy',
    expectedRiskLevel: 'high',
    expectedLanguage: 'Serbian',
    expectedProblems: ['brza zarada', 'bez iskustva', 'puno para', 'inbox', 'nepotpun'],
    notes: 'Suspicious: "brza zarada", "bez iskustva puno para", no concrete info, inbox-only contact, no pay details, no location.',
  },

  // 5. Worker review — personal negative experience
  {
    id: '005_negative_review',
    description: 'Отзыв с личным негативным опытом',
    input: `Radio sam u hladnjači u Smederevu prošlog leta, tri meseca. Obećali su 70.000 mesečno sa smeštajem, ali su na kraju plaćali 55.000, a smeštaj je bio kontejner bez grejanja. Posao težak. Ne bih se vratio.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'worker_review',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Serbian',
    expectedProblems: [],
    notes: 'Specific, factual, first-person, no insults. Concrete details about pay discrepancy and conditions.',
  },

  // 6. Review with insults
  {
    id: '006_review_with_insults',
    description: 'Отзыв с оскорблениями',
    input: `Ovaj govnar iz Leskovca je običan lopov! Radio sam kod njega i nije mi platio zadnju platu. Svi su tamo prevaranti i stoka. Ne idite tamo!`,
    expectedVerdict: 'APPROVE_WITH_EDITS',
    expectedPostType: 'worker_review',
    expectedRiskLevel: 'high',
    expectedLanguage: 'Serbian',
    expectedProblems: ['uvreda', 'lopov', 'stoka', 'govnar', 'apsolutne optužbe'],
    notes: 'Has useful core experience (non-payment) but contains insults and absolute accusations. Needs safe rewrite.',
  },

  // 7. Review with someone else's phone number
  {
    id: '007_review_with_personal_data',
    description: 'Отзыв с чужим номером телефона',
    input: `Radio sam sa Milanom iz Subotice. Loš poslodavac. Evo njegov broj: 064-987-65-43, zovite ga i recite mu da je prevarant.`,
    expectedVerdict: 'APPROVE_WITH_EDITS',
    expectedPostType: 'worker_review',
    expectedRiskLevel: 'high',
    expectedLanguage: 'Serbian',
    expectedProblems: ['lični podaci', 'broj telefona', 'treće lice', 'prevarant'],
    notes: 'Contains third-party phone number published without consent + insult. Core experience is thin. Needs phone number removed and insult cleaned.',
  },

  // 8. Off-topic post
  {
    id: '008_off_topic',
    description: 'Пост не по теме',
    input: `Prodajem iPhone 15, star mesec dana, kao nov. Cena 600 evra. Beograd, lično preuzimanje. 063-555-12-34.`,
    expectedVerdict: 'REJECT',
    expectedPostType: 'spam',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Serbian',
    expectedProblems: ['nije povezano', 'sezonski rad', 'prodaja'],
    notes: 'Phone sale, completely unrelated to seasonal work. Clear REJECT.',
  },

  // 9. Worker job request
  {
    id: '009_job_request_ru',
    description: 'Вопрос работника о работе (на русском)',
    input: `Здравствуйте, я из России. Ищу сезонную работу в Сербии, строительство или сельское хозяйство. Есть ли у кого-то контакты работодателей? Готов приступить через неделю.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'job_request',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Russian',
    expectedProblems: [],
    notes: 'Relevant job request in Russian. Needs Serbian translation in SERBIAN_VERSION. No violations.',
  },

  // 10. Employer seeking workers
  {
    id: '010_employer_seeking_workers',
    description: 'Работодатель просит работников',
    input: `Firma "Voćarstvo Jović" traži 20 radnika za berbu trešanja u okolini Valjeva. Početak 20. juna. Plata 4.500 din po danu, isplata dnevno. Radno vreme 6-14h. Smeštaj u našim bungalovima, hrana obezbeđena. Prevoz organizujemo iz Valjeva. Radnici prijavljeni na dan. Kontakt: Jovan 065-111-22-33 (Viber/WhatsApp).`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'vacancy',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Serbian',
    expectedProblems: [],
    notes: 'Complete employer vacancy with all required fields and company name. Clean.',
  },

  // 11. Russian text → Serbian adaptation
  {
    id: '011_russian_to_serbian',
    description: 'Русский текст → сербская адаптация',
    input: `Я работал на стройке в Белграде два месяца. Зарплату платили вовремя, жильё было нормальное, питание за свой счёт. Работодатель адекватный. Могу рекомендовать.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'worker_review',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Russian',
    expectedProblems: [],
    notes: 'Positive review in Russian. Needs Serbian translation. Should preserve factual tone.',
  },

  // 12. Hungarian text → Serbian adaptation
  {
    id: '012_hungarian_to_serbian',
    description: 'Венгерский текст → сербская адаптация',
    input: `Sziasztok! Magyarországról jöttem. Keresek munkát Szerbiában mezőgazdaságban. Van tapasztalatom. Tudok dolgozni azonnal. Van valakinek elérhetősége? Köszönöm.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'job_request',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Hungarian',
    expectedProblems: [],
    notes: 'Hungarian job request. Needs Serbian translation. Worker looking for agricultural work.',
  },

  // 13. Romanian text → Serbian adaptation
  {
    id: '013_romanian_to_serbian',
    description: 'Румынский текст → сербская адаптация',
    input: `Bună ziua! Am lucrat în Vârșeț la o fabrică sezonieră. Condițiile au fost bune, salariul plătit la timp. Cazare oferită, mâncarea nu. Recomand pentru cei care caută muncă stabilă sezonieră.`,
    expectedVerdict: 'APPROVE',
    expectedPostType: 'worker_review',
    expectedRiskLevel: 'low',
    expectedLanguage: 'Romanian',
    expectedProblems: [],
    notes: 'Romanian positive review. Needs Serbian translation. Good factual content.',
  },

  // 14. Conflict between worker and employer
  {
    id: '014_conflict_worker_employer',
    description: 'Конфликт между работником и работодателем',
    input: `Ovaj poslodavac "Gradnja Plus" iz Kragujevca nije isplatio plate za 3 meseca! Nas 10 radnika smo oštećeni! Znam da je on prijavio firmu na drugog čoveka da bi izbegao tužbe. Imaćemo protest ispred opštine! Ko hoće da nam se pridruži neka se javi.`,
    expectedVerdict: 'ESCALATE',
    expectedPostType: 'conflict',
    expectedRiskLevel: 'high',
    expectedLanguage: 'Serbian',
    expectedProblems: [
      'neisplata plata',
      'optužbe',
      'protest',
      'pravni rizik',
      'navodna prevara sa firmom',
    ],
    notes: 'Serious allegations: non-payment of multiple workers, alleged fraud with company registration, call for protest. High legal risk. Must ESCALATE.',
  },

  // 15. Spam/casino
  {
    id: '015_spam_casino',
    description: 'Спам/казино',
    input: `🎰 NOVI ONLINE KAZINO U SRBIJI 🎰 Dobijate 500€ bonusa na prvi depozit! Igrajte rulet, blackjack, slotove! www.casino-balkan.rs Iskoristite priliku!`,
    expectedVerdict: 'REJECT',
    expectedPostType: 'spam',
    expectedRiskLevel: 'high',
    expectedLanguage: 'Serbian',
    expectedProblems: ['kazino', 'kockanje', 'spam', 'nepovezano'],
    notes: 'Casino ad, clear spam, completely unrelated to seasonal work.',
  },
];

export default TEST_CASES;
