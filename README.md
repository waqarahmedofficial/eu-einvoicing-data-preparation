# EU E-Invoicing Data Preparation & Validation

**Get your data ready for EU e-invoicing mandates: cleaned master data, field-mapping sheets, and pre-validated UBL invoices — the preparation layer, done properly and evidenced.**

Built by **Waqar Ahmed**, spreadsheet & data specialist (7+ years: data cleaning, validation, reconciliation and reporting).

## Who this is for

Accounting firms, ERP implementers, Peppol Access Point partners and finance teams preparing clients for the e-invoicing mandates now landing across Europe (Belgium live since 1 Jan 2026; France from Sep 2026; Poland KSeF phasing through 2026–27; Germany issuing from 2027; EU-wide ViDA digital reporting from 2030). The expensive failures in these projects are data failures — dirty VAT IDs, unmapped fields, invoices that fail validation. That is the layer I work on.

## What the proof in this repo shows

Both samples were **executed end-to-end** with free tooling, and the outputs are committed here.

**Sample A — master-data clean-up** (`samples/sample-A/`)
A 23-record dirty supplier/customer file (BE/DE/FR/NL/PL) cleaned by script: 2 duplicates merged, VAT IDs canonicalised, legal names/addresses normalised, VAT format rules applied for 8 country patterns, check digits verified where a public algorithm exists (BE mod-97, PL weighted mod-11), Peppol participant IDs formatted for 17 records.
**Result: 21 clean records** + a data-quality report flagging 7 records for client confirmation with reasons (4 malformed VAT IDs, 1 mod-97 failure, 1 missing postcode, 1 missing city).

**Sample B — invoice mapping + UBL generation** (`samples/sample-B/`)
One invoice mapped field-by-field (26-row mapping sheet: source field → EN 16931 business term → UBL path → rule → value) and generated as **Peppol BIS Billing 3.0 / UBL 2.1** XML, then actually validated:

| Validation | Result |
|---|---|
| XML well-formedness | PASS |
| UBL 2.1 XSD (official OASIS schemas) | PASS |
| Official CEN **EN 16931 Schematron** (v1.3.17, SaxonC-HE) | **PASS — 0 failed assertions** |
| Peppol rule subset (13 rules: identifiers, arithmetic BR-CO checks, date formats, IBAN mod-97) | PASS — all 13 |

`VERIFICATION.md` records the full verification gate behind these claims, including the mandate research from primary sources (European Commission, GOV.UK, FPS Finance, DGFiP, BMF). `STUDY.md` holds the field-by-field model notes.

## Scope — stated plainly

**What I do:** clean and dedupe master files; validate VAT-ID format + check digits in batch and prepare VIES batch files; build Peppol participant-ID mapping sheets and onboarding data packs; produce field-mapping sheets (ERP export → EN 16931 → UBL/CII); generate example/test UBL invoices and pre-validate batches with per-invoice exception reports.

**What I do not do:** transmit invoices on the Peppol network (that requires a certified Access Point — yours or your client's); hold client credentials, certificates or KSeF tokens; give VAT/tax-treatment advice (your accountant decides — I map the data to their decision); file anything with any authority. **This service is data preparation and validation only.**

One more honesty note: the official compiled Peppol Schematron ships through Access Point tooling; locally I cover that layer with the full CEN EN 16931 Schematron plus the 13-rule Peppol subset above — and I say so, rather than dressing it up as an official Peppol validation certificate.

## How the work runs

1. **Sample first** — you share an anonymised export sample; I confirm what can be cleaned/mapped and what cannot, in writing.
2. **Clean / map** — master-data clean-up with a data-quality report, and/or the field-mapping sheet for your ERP export.
3. **Validate** — generated UBL is run through the same XSD + Schematron stack proven here; failures come back as a per-invoice exception report.
4. **Deliver** — clean data, mapping sheets, validated examples and reports, ready for your Access Point or platform step.

## Tools

Python · lxml · SaxonC-HE · UBL 2.1 · EN 16931 · Peppol BIS Billing 3.0

## About these samples

Proof of capability on **invented data only** (fictional companies, `.example` domains). Format/check-digit validity is not registration — live VIES confirmation runs in the client's/partner's environment at production time, as stated in `VERIFICATION.md`.

## Work with me

I take on freelance projects through Contra: **https://contra.com/mr_world_z7lsrx86**

Communication is **written-only** (chat/email) — clear briefs, documented handovers, no calls needed. Payment via Payoneer or bank transfer.
