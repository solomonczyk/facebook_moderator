# Field Extraction Rules

## Fields

| Field | Serbian Examples | Rules |
|-------|-----------------|-------|
| job_type | branje malina, berba višanja, građevina, pakovanje, plastenik | Extract as-is from text |
| location | Arilje, okolina Ivanjice, Subotica, Srem, Vojvodina | City > village > region |
| workers_needed | 5, 10-15, nekoliko | Number, null if unclear |
| start_date | 1. jul, odmah, sledeće nedelje | Extract as-is |
| pay | 5000 RSD dnevno, 140 RSD/kg, 60000 mesečno | Include amount + unit |
| payment_type | dnevno, po kg, po satu, mesečno | From context |
| accommodation | da, ne, smeštaj obezbeđen, bungalov, kontejner | da/ne + details |
| food | da, ne, 3 obroka, doručak i ručak | da/ne + details |
| transport | da, ne, po dogovoru, organizovan | da/ne + details |
| working_hours | 06-14h, 8 sati, 10h dnevno | Extract as-is |
| contact | 064-123-4567, inbox, Viber, WhatsApp | Phone number string |
| language | srpski, ruski, engleski, mađarski | Detected from text |

## Serbian Domain Terms

- dnevnica = daily wage
- po kilogramu = per kg
- po satu = per hour
- smeštaj obezbeđen = accommodation provided
- hrana obezbeđena = food provided
- prevoz = transport
- Viber / WhatsApp = messenger contacts
- gazdinstvo = farm/family farm
- radnici = workers
- berači = pickers

## Do Not Invent

If a field is not present in the source text, set it to null. Never fabricate phone numbers, pay amounts, locations, or employer names.
