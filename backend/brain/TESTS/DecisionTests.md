# Decision Tests — 50 Cases

## Employer (10)

1. Tražimo 5 radnika za berbu malina Arilje → employer_job_post, approve_with_edits
2. Potrebni radnici za plastenik Subotica → employer_job_post
3. Zapošljavamo radnike za pakovanje → employer_job_post
4. Berba malina tražimo berače Arilje → employer_job_post
5. Hitno potrebni radnici berba višanja Čačak → employer_job_post
6. Firma traži radnike za građevinu Novi Sad → employer_job_post
7. Treba nam ekipa za berbu jabuka → employer_job_post
8. Radnici potrebni za sortiranje voća → employer_job_post
9. Berba borovnica Srem, smeštaj, 064-111-222 → employer_job_post
10. Tražimo radnice za pakovanje, dnevnica 4000 → employer_job_post

## Worker Request (5)

11. Tražim posao branje malina → worker_request
12. Treba mi posao u poljoprivredi → worker_request
13. Dostupan sam za sezonski rad → worker_request
14. Radio sam 3 godine, tražim posao → worker_request
15. Ima li ko posla za građevinca → worker_request

## Worker Group (5)

16. Imam ekipu 30 ljudi sa prevozom → worker_group_available
17. Nas je 5, tražimo poslodavca → worker_group_available
18. Grupa radnika dostupna za berbu → worker_group_available
19. Moja ekipa traži posao, 10 ljudi → worker_group_available
20. Dostupni smo za sezonski rad, 3 radnika → worker_group_available

## Spam (8)

21. KAZINO online bonus 500e → spam, risk=high
22. Crypto trading bitcoin forex → spam, risk=high
23. Brza zarada od kuće → spam, risk=high
24. Laka zarada bez iskustva → spam, risk=high
25. Online kladionica depozit → spam, risk=high
26. Forex trading pasivna zarada → spam, risk=high
27. Kripto valute investicija → spam, risk=high
28. MLM mrežni marketing posao → spam, risk=high

## Suspicious (7)

29. Uplata unapred 50e depozit → suspicious, risk=high
30. Pošaljite sliku pasoša → suspicious, risk=high
31. JMBG obavezan za prijavu → suspicious, risk=high
32. Plata 2000e dnevno bez iskustva → suspicious, risk=high
33. Dokumenta unapred, lična karta → suspicious, risk=high
34. Samo inbox, plata neverovatna → suspicious, risk=high
35. Tražimo za inostranstvo, agent → suspicious, risk=high

## Review (5)

36. Radio sam u hladnjači Smederevo → review_experience
37. Moje iskustvo sa poslodavcem Valjevo → review_experience
38. Ne preporučujem ovo mesto → review_experience
39. Radila sam tri meseca, plata redovna → review_experience
40. Gazda korektan, smeštaj dobar → review_experience

## Question (3)

41. Da li neko zna uslove u hladnjači → question
42. Kako da proverim poslodavca → question
43. Kolika je dnevnica za maline → question

## Edge Cases (7)

44. Employer with missing pay → approve_with_edits, digest=true, missing_info includes pay
45. Employer with only phone → ask_missing_info, digest=false
46. Old post >7 days → escalate
47. Mixed Serbian/Russian → extract both, public in Serbian
48. Inbox only, no phone → risk=medium, contact=inbox
49. Repeated post → mark_duplicate
50. Non-Serbia job → irrelevant or suspicious
