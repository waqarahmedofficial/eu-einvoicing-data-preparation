# STUDY PACK — EU E-Invoicing Mandate Data Preparation

**Purpose:** the working knowledge base behind our e-invoicing data-preparation service. Every mandate date below was checked against official or primary sources on 2026-10-23 (see VERIFICATION.md for the source-by-source verdicts). Where sources disagreed with the research brief, the corrected position is stated.

---

## A. Mandate map — who must do what, by when

| Jurisdiction | Obligation | From when | Format / channel | Status notes |
|---|---|---|---|---|
| **EU-wide (ViDA)** | Structured e-invoicing + digital reporting for **intra-EU B2B** transactions; replaces EC Sales Lists. Member states may mandate domestic e-invoicing without prior EU derogation (already in force). Domestic real-time-reporting systems must align to the EU model by 1 Jan 2035. | **1 Jul 2030** (DRR); ViDA in force 14 Apr 2025 (Council Directive (EU) 2025/516) | EN 16931-based | Confirmed on the European Commission's Taxation & Customs ViDA page. |
| **Belgium** | All Belgian-established VAT-registered businesses must **issue and receive** structured e-invoices for domestic B2B. PDF/paper no longer legally valid. Art. 44-exempt sectors out of scope. | **1 Jan 2026 (live)** | Peppol BIS Billing 3.0 (UBL), EN 16931, via the Peppol network | Tolerance period ended 31 Mar 2026; fines €1,500 / €3,000 / €5,000 per breach sequence. Near-real-time **e-reporting planned Jan 2028** — a second data wave. |
| **Poland** | All B2B invoices issued/received through the state clearance platform **KSeF**, format **FA(3)** XML (national schema, *not* Peppol). | **1 Feb 2026** large taxpayers (2024 sales > PLN 200m); **1 Apr 2026** all other VAT-registered businesses; micro (≤ PLN 10,000/month invoiced) from **1 Jan 2027** | KSeF platform + FA(3) | Receiving via KSeF mandatory for everyone since 1 Feb 2026. No penalties during 2026; fines from 1 Jan 2027 (a bill proposes 2028). Foreign companies without a Polish fixed establishment are out of the issuing scope. |
| **France** | **Receive:** every VAT-taxable business. **Issue + e-reporting:** large & mid-sized (GE/ETI) first, then SMEs/micro. All flows via a state-registered platform (**Plateforme Agréée**, PA); the old public portal (PPF) survives only as the central directory. | Receive + GE/ETI issue: **1 Sep 2026 (live)**; SME/micro issue: **1 Sep 2027** | Factur-X, UBL or CII (all EN 16931) via a PA | Start-up tolerance applies for businesses with a documented compliance trajectory — this is the current selling window for French SME suppliers. |
| **Germany** | **Receive:** all domestic B2B businesses (since 1 Jan 2025 — a PDF is legally no longer an "e-invoice"). **Issue:** phased by prior-year turnover. No central clearance platform; direct exchange (e-mail/Peppol) is allowed. | Issue: **1 Jan 2027** if prior-year turnover > €800,000; **1 Jan 2028** for everyone | XRechnung or ZUGFeRD 2.x (EN 16931 profiles) | BMF guidance letters published; no postponement adopted. The 2027 wave is the largest single data-prep market in the EU. |
| **United Kingdom** | Mandatory e-invoicing for **all VAT invoices** (B2B + B2G). Peppol confirmed (Jun 2026) as the core interoperability network. **No** real-time reporting to HMRC at launch. | **April 2029** | Format/technical rules to be published in the implementation roadmap at Budget 2026 (28 Oct 2026) | Confirmed in the HMRC/DBT consultation response (Autumn Budget 2025) and HMRC's Transformation Roadmap update (Jul 2026). Treat UK specifics as pre-confirmation until the roadmap lands. |

**Corrections vs. the original research brief:** (1) Poland is a *clearance* model on a national schema (FA(3)) — Peppol prep does not transfer 1:1; the data-prep skill (master data, VAT IDs, field mapping) transfers, the syntax differs. (2) France's public portal no longer routes invoices (Décret n° 2026-677) — clients *must* contract a PA, which is why PAs and their partner channels are the buyers. (3) Germany's receiving duty dates from Jan 2025, not from the 2027 issuing wave. (4) Belgium adds a 2028 e-reporting wave on top of the 2026 invoicing mandate.

## B. The EN 16931 data model in plain terms

EN 16931 is a **semantic** standard: it defines *what* an invoice must say, not the file syntax. The same model is then bound to UBL 2.1 XML or UN/CEFACT CII XML. Data is organised in **Business Groups (BG)** containing **Business Terms (BT)**, each with a cardinality (1..1 = mandatory exactly once; 0..1 = optional; 1..n = repeating).

The core of every compliant invoice (~30 elements a preparer touches daily):

- **Document level (BG-1…BG-3):** invoice number (BT-1), issue date (BT-2), type code (BT-3: 380 invoice, 381 credit note, 389 self-billed…), currency (BT-5), VAT accounting currency if different (BT-6), tax point date (BT-7), due date (BT-9), buyer reference (BT-10), PO reference (BT-13), preceding-invoice reference for corrections (BT-25/26), payment terms (BT-20), specification identifier (BT-24).
- **Seller (BG-4) and Buyer (BG-7):** name (BT-27 / BT-44), postal address (BG-5 / BG-8: street BT-35/50, city BT-37/52, postcode BT-38/53, country BT-40/55), **VAT identifier (BT-31 / BT-48)**, seller tax-representative block (BG-11) when applicable, electronic address (BT-34 / BT-49 — the Peppol endpoint), contact (BG-6 / BG-12).
- **Delivery (BG-13…BG-15):** deliver-to name/address, actual delivery date (BT-72).
- **Payment (BG-16…BG-19):** payment means code (BT-81; 58 = SEPA credit transfer), payee IBAN (BT-84), payment reference (BT-83), card details where relevant.
- **Allowances/charges (BG-20/BG-21)** at document level and **per line (BG-27/BG-28)**, each with reason codes and the VAT category they belong to.
- **VAT breakdown (BG-23):** one subtotal per VAT category/rate: taxable amount (BT-116), tax amount (BT-117), category code (BT-118), rate (BT-119), exemption reason (BT-120/121) where applicable.
- **Totals (BG-22):** sum of line net amounts (BT-106), document allowances (BT-107) / charges (BT-108), tax-exclusive total (BT-109), total VAT (BT-110, plus BT-111 in VAT currency), tax-inclusive total (BT-112), prepaid amount (BT-113), rounding (BT-114), **payable amount (BT-115)**.
- **Lines (BG-25):** line ID (BT-126), quantity + unit code (BT-129/130, UN/ECE Rec 20 — e.g. C62 = piece, HUR = hour, KGM = kilogram), line net amount (BT-131), item name (BT-153), item VAT category/rate (BT-151/152), net price (BT-146) and price base quantity (BT-149/150).

**VAT-category codes (BT-118 / BT-151)** — the ones that decide the tax logic:
`S` standard rate · `Z` zero rate · `E` exempt from VAT · `AE` **reverse charge** (buyer accounts for the VAT — the standard case for intra-EU B2B services) · `K` intra-EU supply of goods (exempt with credit, reported) · `G` export outside the EU · `O` outside scope · `L`/`M` Canary Islands / Ceuta-Melilla special cases. Rule of thumb for prep work: the *category drives everything downstream* — rate field present or absent, exemption-reason text required for E/AE/K/G, and which totals must reconcile (the EN 16931 BR-CO arithmetic rules).

## C. Peppol BIS Billing 3.0 + UBL 2.1, field by field

Peppol BIS Billing 3.0 is a **CIUS** of EN 16931: a stricter profile ("compliant" specification identifier BT-24 = `urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0`), transported as **UBL 2.1 XML** over the Peppol network (4-corner model: sender → its Access Point → receiver's Access Point → receiver). Document root: `<Invoice>` in the UBL Invoice-2 namespace; `cac:` = aggregate components, `cbc:` = basic components. Element order inside each block is fixed by the UBL schema — out-of-order XML fails XSD validation before business rules even run.

| Order in XML | UBL element | BT | Notes for the preparer |
|---|---|---|---|
| 1 | `cbc:UBLVersionID` | — | Always `2.1`. |
| 2 | `cbc:CustomizationID` | BT-24 | The Peppol string above (rule PEPPOL-EN16931-R004). |
| 3 | `cbc:ProfileID` | BT-23 | `urn:fdc:peppol.eu:2017:poacc:billing:01:1.0` (R001: mandatory in Peppol). |
| 4 | `cbc:ID` | BT-1 | Invoice number. |
| 5 | `cbc:IssueDate` / `cbc:DueDate` | BT-2 / BT-9 | `YYYY-MM-DD` only (rule F001). Due date or payment terms must exist on invoices (BR-CO-25). |
| 6 | `cbc:InvoiceTypeCode` | BT-3 | UNTDID 1001 subset. |
| 7 | `cbc:Note` | BG-1 | Max one note in Peppol (R002). |
| 8 | `cbc:DocumentCurrencyCode` (+ `TaxCurrencyCode`) | BT-5 / BT-6 | Tax currency must differ from invoice currency when both present (R005). |
| 9 | `cbc:BuyerReference` | BT-10 | **Peppol R003:** buyer reference *or* PO reference is mandatory — the #1 rejection cause in practice. |
| 10 | `cac:OrderReference/cbc:ID` | BT-13 | The buyer's PO number. |
| 11 | `cac:BillingReference` | BT-25/26 | Mandatory for credit notes/corrections (preceding invoice). |
| 12 | `cac:AccountingSupplierParty` | BG-4 | Contains `cbc:EndpointID` (BT-34, schemeID = Peppol scheme, R020 mandatory), PartyName, PostalAddress, PartyTaxScheme/`cbc:CompanyID` (BT-31), PartyLegalEntity, Contact. |
| 13 | `cac:AccountingCustomerParty` | BG-7 | Same shape; EndpointID = BT-49 (R010 mandatory). |
| 14 | `cac:Delivery` | BG-13…15 | Delivery date/location where relevant. |
| 15 | `cac:PaymentMeans` | BG-16…18 | `PaymentMeansCode` (BT-81) + `PayeeFinancialAccount/cbc:ID` = IBAN (BT-84). |
| 16 | `cac:PaymentTerms/cbc:Note` | BT-20 | Free-text terms when no due date. |
| 17 | `cac:AllowanceCharge` (document level) | BG-20/21 | With `ChargeIndicator`, amount, and its TaxCategory. |
| 18 | `cac:TaxTotal` (×1, or ×2 with tax currency) | BG-23 + BT-110 | `TaxSubtotal` per category: TaxableAmount (BT-116), TaxAmount (BT-117), TaxCategory ID (BT-118), Percent (BT-119), exemption reason where required. |
| 19 | `cac:LegalMonetaryTotal` | BG-22 | LineExtensionAmount (BT-106) → TaxExclusiveAmount (BT-109) → TaxInclusiveAmount (BT-112) → PayableAmount (BT-115). Must satisfy BR-CO-10/13/14/15 arithmetic. |
| 20 | `cac:InvoiceLine` (1..n) | BG-25 | `cbc:ID` (BT-126), `InvoicedQuantity` with `unitCode` (BT-129), `LineExtensionAmount` (BT-131) = qty × price ± line allowances, `cac:Item` (name BT-153 + ClassifiedTaxCategory BT-151/152), `cac:Price/PriceAmount` (BT-146). |

**Validation layers, in the order a file fails:** (1) XML well-formedness → (2) UBL 2.1 XSD (structure/order) → (3) EN 16931 Schematron (BR-* business rules incl. all arithmetic) → (4) Peppol Schematron (PEPPOL-EN16931-R* rules) → (5) national CIUS rules (e.g. XRechnung BR-DE-*) → (6) Access Point / clearance-platform checks (KSeF, PA) → (7) the *buyer's* own AP/ERP rules. Our pre-submission reports test layers 1–4 locally (see Sample B validation log for exactly what was run) so clients fix data once, upstream, instead of per-rejection.

## D. The services we sell (data-prep layer only)

We prepare and prove data. We do **not** transmit invoices, hold Peppol credentials, or give VAT advice — transmission stays with the client's certified Access Point / Plateforme Agréée / KSeF setup, and tax treatment stays with their accountant. That boundary is a selling point, not a weakness: platforms license the pipe; nobody licenses clean data.

1. **Supplier/customer master-data clean-up** — dedupe, legal-name and address standardisation, missing-field report. *Deliverable: cleaned file + data-quality report (the Sample A format).*
2. **VAT-ID validation batches** — format + check-digit validation for all EU country patterns, exception list with reasons, and VIES-confirmation workflow support (confirmations run in the client's/partner's environment; we prepare and reconcile the batch).
3. **Peppol-readiness data setup** — participant-ID mapping per national scheme, endpoint/address completeness checks, onboarding data packs in the exact shape an Access Point or PA asks for.
4. **Invoice field-mapping sheets** — ERP/accounting export → EN 16931 BT → UBL/CII element → rule, per document type (the Sample B format), including code-list mapping (units, payment means, VAT categories) and worked example invoices.
5. **Pre-submission validation reports** — batches of draft invoices run through well-formedness + XSD + EN 16931 Schematron checks locally; a per-invoice exception report (rule ID, field, fix) *before* the client's platform rejects them.
6. **Country-wave data packs** — the same five services scoped to one mandate wave (e.g. "German 2027 issuers", "French SME 2027", "Belgian 2028 e-reporting"), priced per batch.
