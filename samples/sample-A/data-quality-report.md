# Sample A — Data Quality Report
**Supplier & customer master-data clean-up for e-invoicing readiness**
Sample client file: 23 trading-partner records (suppliers + customers, BE / DE / FR / NL / PL) — *all data invented for this sample.*
Files: `master-data-BEFORE.csv/.xlsx` → `master-data-AFTER.csv/.xlsx`

## Result summary
| Measure | Count |
|---|---|
| Records received | 23 |
| Records after clean-up | 21 |
| Duplicate records merged | 2 |
| VAT IDs fully validated (format + checksum where a public check exists) | 16 |
| Peppol participant IDs assigned (scheme format) | 17 |
| Records needing client confirmation before go-live | 7 |

## Issues found and fixed automatically
| Issue category | Count | What was done |
|---|---|---|
| Duplicate partner records | 2 | MP-1020 merged into MP-1002 (same VAT ID, name variant "n.v."); MP-1021 merged into MP-1010 ("B.V." variant). Contact e-mail from the duplicate was preserved on the surviving record. |
| VAT ID with spaces/dots ("BE 0742.583.104") | 2 | Separators stripped → canonical form. |
| VAT ID in lower case | 1 | Uppercased. |
| VAT ID missing country prefix ("5261040828") | 1 | Prefix PL added from the record's country field and re-validated (PL weighted check digit passes). |
| Legal-name whitespace / all-caps / suffix case | 2 | Trimmed, spacing normalised, legal-form suffixes standardised (SARL, SAS, GmbH, BV, NV). |
| Address abbreviation ("Industriestr.") | 1 | Expanded to the full street-name form. |

## Flagged for client confirmation (NOT silently changed)
| Record | Issue | Recommended action |
|---|---|---|
| MP-1006 Bergmann & Sohn GmbH | VAT ID `DE27182818` has 8 digits; German VAT IDs have 9 | Ask the partner to confirm the full VAT ID |
| MP-1011 Wisla Foods Sp. z o.o. | VAT ID `PL779243001` has 9 digits; Polish NIP has 10 | Confirm the missing digit |
| MP-1015 Zielinska Consulting Sp. z o.o. | VAT ID `PL94522578101` has 11 digits | Confirm which digit is wrong; likely a duplicated keystroke |
| MP-1018 De Clercq Immo NV | VAT ID `BE071234987` has 9 digits; Belgian numbers have 10 | Confirm the full enterprise/VAT number |
| MP-1022 Testwinkel De Smet BV | VAT ID `BE0999888777` passes the format check but **fails the modulo-97 check digit** | Very likely a typing error — confirm before any invoice is sent; Peppol ID assigned provisionally and marked for verification |
| MP-1005 Meulemeester Bouw NV | Postcode missing | Needed for a complete EN 16931 postal address (BG-5) — request from partner |
| MP-1013 Coopérative Laitière du Nord | City missing | Needed for BG-5 — request from partner |

## Method notes (how a client can trust this report)
- VAT IDs were checked in three layers: (1) canonicalisation (spaces, dots, case, prefix), (2) the official per-country **format** rules, (3) the published **check-digit** algorithms where they exist in simple public form (BE mod-97, PL weighted mod-11). Format validity does **not** prove a number is registered — that is what the EU **VIES** service confirms, and a VIES batch check against the live register is step 2 of a production clean-up (run inside the client's or partner's environment).
- Peppol participant IDs were formatted as `scheme:identifier` using the usual national schemes (BE 0208, DE 0204, FR 0009, NL 0106). Final assignment must match the identifier the partner is actually registered with in the Peppol directory — verified at onboarding through the client's Access Point, not assumed from the VAT number alone.
