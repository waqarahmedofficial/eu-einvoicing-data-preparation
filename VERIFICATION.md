# VERIFICATION GATE — EU E-Invoicing Data Preparation
**Date:** 2026-10-23 · **Gate rule (user order):** no packaging claim may exceed what this file supports. PACKAGING.md was written only after both verdicts below.

---

## VERDICT 1 — PERFORMABILITY: ✅ YES, for the data-preparation layer (proven hands-on)

The samples are not mock-ups; both were executed end-to-end in this build with free tooling (Python/openpyxl, lxml, SaxonC-HE), and the outputs are in `samples/`.

**Sample A — master-data clean-up (executed).** A 23-record dirty supplier/customer file (BE/DE/FR/NL/PL) was cleaned by script: 2 duplicates merged, VAT IDs canonicalised (case, separators, missing prefix), legal names/addresses normalised, VAT format rules applied for 8 country patterns, check digits verified where a public algorithm exists (BE mod-97, PL weighted mod-11), Peppol participant IDs formatted for 17 records. Result: 21 clean records + a data-quality report flagging 7 records for client confirmation with reasons (4 malformed VAT IDs, 1 mod-97 failure, 1 missing postcode, 1 missing city). Stats: `samples/sample-A/cleanup-stats.json`, report: `samples/sample-A/data-quality-report.md`.

**Sample B — invoice mapping + UBL generation (executed and validated).** One sample invoice was mapped field-by-field (26-row mapping sheet: source field → BT number → UBL path → rule → value) and generated as Peppol BIS Billing 3.0 / UBL 2.1 XML. Validation actually run (`samples/sample-B/validation-log.txt`):
1. Well-formedness — PASS.
2. **UBL 2.1 XSD validation against the official OASIS schemas** (downloaded from docs.oasis-open.org) — PASS.
3. **Official CEN EN 16931 Schematron** (EN16931-UBL-validation.xslt v1.3.17, ConnectingEurope/CEN artefacts), run locally with SaxonC-HE — **PASS, 0 failed assertions** (SVRL kept in `work/svrl-output.xml`).
4. Peppol-specific rules — checked via a 13-rule Python subset (BT-24 value, R001/R003/R010/R020, BR-CO-10/13/15 arithmetic, date format, IBAN mod-97) — PASS all 13.

**What we can do today, step by step, on a real client job:**
- Clean and dedupe supplier/customer master files (CSV/XLSX/ERP exports) and produce the data-quality report format buyers actually purchase.
- Validate VAT-ID format + check digits in batch; prepare VIES batch files and reconcile results.
- Build Peppol participant-ID mapping sheets and onboarding data packs.
- Produce field-mapping sheets (ERP export → EN 16931 BT → UBL/CII) with code-list mappings.
- Generate example/test UBL invoices from mapped data and pre-validate batches (well-formed + XSD + EN 16931 Schematron) with per-invoice exception reports.

**What needs the client's/partner's platform or account (we prepare, they transmit):**
- Sending/receiving on the Peppol network — requires a **certified Access Point** account (the client's, Qvalia's, Storecove's…). We never hold the Peppol role.
- France: transmission only via a **Plateforme Agréée**; Poland: submission only via **KSeF** with the taxpayer's own credentials/token.
- Live VIES confirmations at production scale and Peppol directory lookups run inside the client's/partner's environment (we prepare and reconcile the batch files).
- The Peppol-specific Schematron layer (PEPPOL-EN16931-R*) in its official compiled form is distributed through Access Point tooling; locally we cover it with the rule subset above plus the full CEN schematron — stated plainly to clients, never dressed up as an official Peppol validation certificate.

**What we cannot / will not do:**
- VAT advice or tax treatment decisions (reverse-charge applicability, exemptions) — the client's accountant decides; we map the data to their decision.
- Anything requiring the client's credentials, certificates, or KSeF tokens to be held by us.
- SDS/VAT filings, registrations, or acting as a Peppol Service Provider.

## VERDICT 2 — REALITY: ✅ YES, demand and targets confirmed from primary sources

**Mandates (primary sources read or directly corroborated):**
- **ViDA / EU 2030** — European Commission, Taxation & Customs Union (taxation-customs.ec.europa.eu): ViDA adopted 11 Mar 2025, in force 14 Apr 2025 (Directive (EU) 2025/516); digital reporting for cross-border B2B from **1 Jul 2030**; member states may mandate domestic e-invoicing without derogation. ✅ Primary source read.
- **UK April 2029** — GOV.UK, HMRC/DBT consultation response "Promoting electronic invoicing across UK businesses and the public sector": government decision to implement **mandatory VAT e-invoicing from 2029**; HMRC Transformation Roadmap (Jul 2026) restates "from April 2029". ✅ Primary source read.
- **Belgium 1 Jan 2026** — official portal einvoice.belgium.be (FPS Finance/BOSA) live; FPS Finance's 19 Dec 2025 clarification and the €1,500/€3,000/€5,000 fine sequence reported by KPMG, Deloitte and Avalara from the Royal Decree of 14 Jul 2025. Mandate is in force *now* (post-tolerance since 1 Apr 2026). ✅ Verified (official portal + FPS clarification).
- **Poland KSeF** — Ministry of Finance platform (podatki.gov.pl/ksef live): 1 Feb 2026 (2024 sales > PLN 200m), 1 Apr 2026 (all others), micro from 1 Jan 2027; FA(3) schema; penalties from 2027. ✅ Verified (ministry platform + ministry press-release reporting).
- **France** — DGFiP/Ministry of the Economy: all businesses receive from 1 Sep 2026, GE/ETI issue from 1 Sep 2026, SMEs issue 1 Sep 2027; Plateforme Agréée model finalised by Décret n° 2026-677 (PPF reduced to central directory). ✅ Verified (DGFiP guidance + decree reporting).
- **Germany** — Wachstumschancengesetz + BMF guidance letters: receive since 1 Jan 2025; issue 1 Jan 2027 (> €800k prior-year turnover), 1 Jan 2028 (all). ✅ Verified (BMF topic pages + statutory reporting; no postponement adopted).

**First targets (routes re-checked on the companies' own sites, 2026-10-23):**
- **Qvalia (qvalia.com/partner) — ✅ VERIFIED, read live.** Certified Peppol Access Point/SMP. Three partner models (Embedded API, **White-label platform** explicitly aimed at accounting agencies/ERP providers/IT consultancies, Hosted Access Point). Page states partners own "your own onboarding and support flow" — i.e. customer onboarding/data setup is the partner's job, which is precisely the service we sell. Sandbox offered ("most partners can start testing within hours"); free end-user e-invoicing tier exists. Partner contact is via their partner page contact route (form/demo request = signup step, user's).
- **Storecove — ⚠️ PARTIALLY VERIFIED.** Own site confirms: certified Access Point, API product, and a **free 30-day sandbox test account on request** (storecove.com). A formal partner/reseller programme is described on peppol.nu (the Peppol supplier directory: "strong partner program… resell Peppol services") but a dedicated partner page on Storecove's own site was not separately verified. → Included in pitch drafts as a *test-account + services enquiry* (not as a "partner programme application"), with this caveat carried into PACKAGING.md.
- **Sovos — ❌ UNVERIFIED route.** Named in the research as hiring/partner-ecosystem evidence only; no specific partner/vendor route was re-checked on sovos.com in this gate. → **Excluded from pitch drafts** until a route is verified.
- **Belgian accounting-firm segment (e.g. z80.be)** — named in research as openly selling Peppol cleanups; its own route was not re-checked in this gate → segment pitch held as a template only, marked UNVERIFIED per-firm, not sent anywhere (nothing is sent in this pack at all).

**Bottom line:** Both verdicts are YES for the data-preparation layer, with the transmission boundary and the Storecove/Sovos caveats above. PACKAGING.md claims nothing beyond this file.
