#!/usr/bin/env python3
"""Sample B: sample invoice -> field-mapping sheet (CSV/XLSX) + Peppol BIS
Billing 3.0 UBL 2.1 XML, then validation:
 1) XML well-formedness (lxml parse)
 2) UBL 2.1 XSD validation (official OASIS schemas, downloaded)
 3) EN 16931 / Peppol BIS rule subset implemented in Python (arithmetic,
    mandatory terms, code lists, Peppol identifiers) - results logged.
What is NOT done: official Peppol Schematron (needs an XSLT 2.0/Schematron
engine not available offline here) - stated in the validation log."""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from lxml import etree

BASE = Path.home() / "workspace/einvoicing-prep/samples/sample-B"
WORK = Path.home() / "workspace/einvoicing-prep/work"
BASE.mkdir(parents=True, exist_ok=True)

def D(x): return Decimal(str(x))
def m(x): return str(D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

# ---------------------------------------------------------------- the invoice
inv = {
    "id": "INV-2026-0042", "issue_date": "2026-10-15", "due_date": "2026-11-14",
    "type_code": "380", "currency": "EUR", "buyer_reference": "PO-8814 / Dept FIN",
    "order_reference": "PO-8814",
    "seller": {"name": "Van Acker Packaging BV", "street": "Dokweg 12", "city": "Gent",
               "postcode": "9000", "country": "BE", "vat": "BE0742583104",
               "endpoint_scheme": "0208", "endpoint": "0742583104",
               "email": "invoicing@vanackerpackaging.example"},
    "buyer": {"name": "Rheinwerk GmbH", "street": "Industriestrasse 7", "city": "Dusseldorf",
              "postcode": "40210", "country": "DE", "vat": "DE314159265",
              "endpoint_scheme": "0204", "endpoint": "314159265"},
    "payee_iban": "BE68 5390 0754 7034", "payment_means_code": "58",  # SEPA credit transfer
    "lines": [
        {"id": "1", "qty": 120, "unit": "C62", "name": "Corrugated shipping boxes 40x30x30 cm",
         "price": "1.85", "vat_cat": "S", "vat_rate": "21"},
        {"id": "2", "qty": 40, "unit": "C62", "name": "Packing tape rolls 50 mm x 66 m",
         "price": "2.40", "vat_cat": "S", "vat_rate": "21"},
        {"id": "3", "qty": 1, "unit": "C62", "name": "Pallet delivery service (BE->DE)",
         "price": "145.00", "vat_cat": "S", "vat_rate": "21"},
    ],
}
for ln in inv["lines"]:
    ln["ext"] = m(D(ln["qty"]) * D(ln["price"]))
net_total = m(sum(D(l["ext"]) for l in inv["lines"]))
vat_total = m(D(net_total) * D("21") / D("100"))
gross = m(D(net_total) + D(vat_total))
inv["totals"] = {"line_ext": net_total, "tax_exclusive": net_total, "tax": vat_total,
                 "tax_inclusive": gross, "payable": gross}

# ---------------------------------------------------------------- mapping sheet
MAP = [
    ("erp_inv_no", "BT-1", "Invoice number", "/Invoice/cbc:ID", "Copy as-is; unique per seller", inv["id"]),
    ("erp_inv_date", "BT-2", "Issue date", "/Invoice/cbc:IssueDate", "Format YYYY-MM-DD", inv["issue_date"]),
    ("constant", "BT-3", "Invoice type code", "/Invoice/cbc:InvoiceTypeCode", "UNTDID 1001: 380 = commercial invoice", "380"),
    ("erp_currency", "BT-5", "Invoice currency code", "/Invoice/cbc:DocumentCurrencyCode", "ISO 4217", "EUR"),
    ("buyer_ref", "BT-10", "Buyer reference", "/Invoice/cbc:BuyerReference", "Peppol R003: buyer reference OR PO reference required", inv["buyer_reference"]),
    ("erp_po_no", "BT-13", "Purchase order reference", "/Invoice/cac:OrderReference/cbc:ID", "From buyer PO", "PO-8814"),
    ("erp_due_date", "BT-9", "Payment due date", "/Invoice/cbc:DueDate", "YYYY-MM-DD", inv["due_date"]),
    ("seller_legal_name", "BT-27", "Seller name", ".../AccountingSupplierParty/.../PartyName/cbc:Name", "Legal (registered) name, not trade name", inv["seller"]["name"]),
    ("seller_vat_no", "BT-31", "Seller VAT identifier", ".../PartyTaxScheme/cbc:CompanyID", "Country prefix + number, no spaces", inv["seller"]["vat"]),
    ("seller_peppol_id", "BT-34", "Seller electronic address", ".../AccountingSupplierParty/.../cbc:EndpointID", "Peppol R020: mandatory; schemeID = Peppol scheme", "0208:0742583104"),
    ("buyer_legal_name", "BT-44", "Buyer name", ".../AccountingCustomerParty/.../PartyName/cbc:Name", "Legal name", inv["buyer"]["name"]),
    ("buyer_vat_no", "BT-48", "Buyer VAT identifier", ".../PartyTaxScheme/cbc:CompanyID", "Required when buyer is VAT-registered", inv["buyer"]["vat"]),
    ("buyer_peppol_id", "BT-49", "Buyer electronic address", ".../AccountingCustomerParty/.../cbc:EndpointID", "Peppol R010: mandatory", "0204:314159265"),
    ("bank_iban", "BT-84", "Payee financial account", ".../PaymentMeans/cac:PayeeFinancialAccount/cbc:ID", "IBAN, spaces removed in XML", inv["payee_iban"].replace(" ", "")),
    ("sum_lines", "BT-106", "Sum of line net amounts", ".../LegalMonetaryTotal/cbc:LineExtensionAmount", "= SUM(line extensions)", net_total),
    ("total_net", "BT-109", "Tax-exclusive total", ".../LegalMonetaryTotal/cbc:TaxExclusiveAmount", "= BT-106 - allowances + charges", net_total),
    ("total_vat", "BT-110", "Total VAT amount", ".../LegalMonetaryTotal/cbc:TaxAmount", "= SUM(VAT category breakdowns)", vat_total),
    ("total_gross", "BT-112", "Tax-inclusive total", ".../LegalMonetaryTotal/cbc:TaxInclusiveAmount", "= BT-109 + BT-110", gross),
    ("total_payable", "BT-115", "Amount due", ".../LegalMonetaryTotal/cbc:PayableAmount", "= BT-112 - prepaid + rounding", gross),
    ("line_vat_rate", "BT-119", "VAT category rate (per category)", ".../TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:Percent", "Per VAT category group", "21"),
    ("line_id", "BT-126", "Line identifier", ".../InvoiceLine/cbc:ID", "Unique within invoice", "1..3"),
    ("line_qty", "BT-129", "Invoiced quantity", ".../InvoiceLine/cbc:InvoicedQuantity", "unitCode from UN/ECE Rec 20 (C62 = one/piece)", "120 / 40 / 1"),
    ("line_net", "BT-131", "Line net amount", ".../InvoiceLine/cbc:LineExtensionAmount", "= qty x price (excl. VAT)", "222.00 / 96.00 / 145.00"),
    ("line_item_name", "BT-153", "Item name", ".../InvoiceLine/cac:Item/cbc:Name", "Short item name", "3 lines"),
    ("line_price", "BT-146", "Item net price", ".../InvoiceLine/cac:Price/cbc:PriceAmount", "Excl. VAT, per unit", "1.85 / 2.40 / 145.00"),
]
import csv
with open(BASE / "field-mapping-sheet.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["source_field", "BT", "business_term", "UBL_path", "rule", "sample_value"])
    w.writerows(MAP)
from openpyxl import Workbook
wb = Workbook(); ws = wb.active; ws.title = "Field mapping"
ws.append(["source_field", "BT", "business_term", "UBL_path", "rule", "sample_value"])
for r in MAP: ws.append(list(r))
wb.save(BASE / "field-mapping-sheet.xlsx")

# ---------------------------------------------------------------- UBL XML
NS = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
      "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
UBL = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
def E(tag, text=None, parent=None, **attrs):
    el = etree.SubElement(parent, tag, attrs) if parent is not None else etree.Element(tag, attrs)
    if text is not None: el.text = str(text)
    return el
q = lambda p, n: f"{{{NS[p]}}}{n}"
root = etree.Element(f"{{{UBL}}}Invoice", nsmap={None: UBL, "cac": NS["cac"], "cbc": NS["cbc"]})
E(q("cbc", "UBLVersionID"), "2.1", root)
E(q("cbc", "CustomizationID"), "urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0", root)
E(q("cbc", "ProfileID"), "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0", root)
E(q("cbc", "ID"), inv["id"], root)
E(q("cbc", "IssueDate"), inv["issue_date"], root)
E(q("cbc", "DueDate"), inv["due_date"], root)
E(q("cbc", "InvoiceTypeCode"), inv["type_code"], root)
E(q("cbc", "DocumentCurrencyCode"), inv["currency"], root)
E(q("cbc", "BuyerReference"), inv["buyer_reference"], root)
o = E(q("cac", "OrderReference"), parent=root); E(q("cbc", "ID"), inv["order_reference"], o)

def party(p, role):
    wrap = E(q("cac", role), parent=root)
    py = E(q("cac", "Party"), parent=wrap)
    E(q("cbc", "EndpointID"), p["endpoint"], py, schemeID=p["endpoint_scheme"])
    pn = E(q("cac", "PartyName"), parent=py); E(q("cbc", "Name"), p["name"], pn)
    pa = E(q("cac", "PostalAddress"), parent=py)
    E(q("cbc", "StreetName"), p["street"], pa); E(q("cbc", "CityName"), p["city"], pa)
    E(q("cbc", "PostalZone"), p["postcode"], pa)
    cn = E(q("cac", "Country"), parent=pa); E(q("cbc", "IdentificationCode"), p["country"], cn)
    pts = E(q("cac", "PartyTaxScheme"), parent=py)
    E(q("cbc", "CompanyID"), p["vat"], pts)
    ts = E(q("cac", "TaxScheme"), parent=pts); E(q("cbc", "ID"), "VAT", ts)
    pl = E(q("cac", "PartyLegalEntity"), parent=py); E(q("cbc", "RegistrationName"), p["name"], pl)
    if p.get("email"):
        ct = E(q("cac", "Contact"), parent=py); E(q("cbc", "ElectronicMail"), p["email"], ct)
party(inv["seller"], "AccountingSupplierParty")
party(inv["buyer"], "AccountingCustomerParty")

pm = E(q("cac", "PaymentMeans"), parent=root)
E(q("cbc", "PaymentMeansCode"), inv["payment_means_code"], pm)
pfa = E(q("cac", "PayeeFinancialAccount"), parent=pm)
E(q("cbc", "ID"), inv["payee_iban"].replace(" ", ""), pfa)

tt = E(q("cac", "TaxTotal"), parent=root)
E(q("cbc", "TaxAmount"), inv["totals"]["tax"], tt, currencyID="EUR")
st = E(q("cac", "TaxSubtotal"), parent=tt)
E(q("cbc", "TaxableAmount"), net_total, st, currencyID="EUR")
E(q("cbc", "TaxAmount"), inv["totals"]["tax"], st, currencyID="EUR")
tc = E(q("cac", "TaxCategory"), parent=st)
E(q("cbc", "ID"), "S", tc); E(q("cbc", "Percent"), "21", tc)
ts2 = E(q("cac", "TaxScheme"), parent=tc); E(q("cbc", "ID"), "VAT", ts2)

lmt = E(q("cac", "LegalMonetaryTotal"), parent=root)
E(q("cbc", "LineExtensionAmount"), inv["totals"]["line_ext"], lmt, currencyID="EUR")
E(q("cbc", "TaxExclusiveAmount"), inv["totals"]["tax_exclusive"], lmt, currencyID="EUR")
E(q("cbc", "TaxInclusiveAmount"), inv["totals"]["tax_inclusive"], lmt, currencyID="EUR")
E(q("cbc", "PayableAmount"), inv["totals"]["payable"], lmt, currencyID="EUR")

for ln in inv["lines"]:
    il = E(q("cac", "InvoiceLine"), parent=root)
    E(q("cbc", "ID"), ln["id"], il)
    E(q("cbc", "InvoicedQuantity"), ln["qty"], il, unitCode=ln["unit"])
    E(q("cbc", "LineExtensionAmount"), ln["ext"], il, currencyID="EUR")
    it = E(q("cac", "Item"), parent=il)
    E(q("cbc", "Name"), ln["name"], it)
    ctc = E(q("cac", "ClassifiedTaxCategory"), parent=it)
    E(q("cbc", "ID"), ln["vat_cat"], ctc); E(q("cbc", "Percent"), ln["vat_rate"], ctc)
    tsx = E(q("cac", "TaxScheme"), parent=ctc); E(q("cbc", "ID"), "VAT", tsx)
    pr = E(q("cac", "Price"), parent=il)
    E(q("cbc", "PriceAmount"), m(ln["price"]), pr, currencyID="EUR")

xml_bytes = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
(BASE / "sample-invoice-UBL.xml").write_bytes(xml_bytes)

# ---------------------------------------------------------------- validation
log = []
doc = etree.fromstring(xml_bytes)
log.append("1. Well-formed XML: PASS (parsed by lxml without error)")

schema = etree.XMLSchema(etree.parse(str(WORK / "xsd/maindoc/UBL-Invoice-2.1.xsd")))
ok = schema.validate(doc)
log.append(f"2. UBL 2.1 XSD validation (official OASIS schemas): {'PASS' if ok else 'FAIL'}")
for e in schema.error_log: log.append(f"     XSD: {e}")

R = []
def chk(name, cond, detail=""): R.append((name, bool(cond), detail))
x = lambda p: doc.xpath(p, namespaces={**NS, "ubl": UBL})
chk("BT-24 CustomizationID = Peppol BIS 3.0 value", x("//cbc:CustomizationID/text()") ==
    ["urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0"])
chk("BT-23 ProfileID present (Peppol R001)", len(x("//cbc:ProfileID")) == 1)
chk("Mandatory BT-1/2/3/5 present", all(x(f"//cbc:{t}") for t in ["ID", "IssueDate", "InvoiceTypeCode", "DocumentCurrencyCode"]))
chk("Peppol R003: BuyerReference or OrderReference present", bool(x("//cbc:BuyerReference") or x("//cac:OrderReference")))
chk("Peppol R010/R020: buyer+seller EndpointID with schemeID",
    all(x(f"//cac:{r}//cbc:EndpointID/@schemeID") for r in ["AccountingSupplierParty", "AccountingCustomerParty"]))
chk("BT-31/BT-48 VAT IDs match country format",
    bool(__import__("re").match(r"^BE[01]\d{9}$", inv["seller"]["vat"])) and
    bool(__import__("re").match(r"^DE\d{9}$", inv["buyer"]["vat"])))
chk("BR-CO-10: LineExtensionAmount = sum of line extensions",
    D(x("//cac:LegalMonetaryTotal/cbc:LineExtensionAmount/text()")[0]) ==
    sum(D(t) for t in x("//cac:InvoiceLine/cbc:LineExtensionAmount/text()")))
chk("BR-CO-13/14: TaxExclusive = LineExtension (no allowances/charges)", D(net_total) == D(inv["totals"]["tax_exclusive"]))
chk("BR-CO-15: TaxInclusive = TaxExclusive + TaxAmount",
    D(inv["totals"]["tax_inclusive"]) == D(inv["totals"]["tax_exclusive"]) + D(inv["totals"]["tax"]))
chk("Line arithmetic: each LineExtension = qty x price",
    all(D(l["ext"]) == D(l["qty"]) * D(l["price"]) for l in inv["lines"]))
chk("VAT breakdown: TaxSubtotal taxable = sum of lines in category S",
    D(x("//cac:TaxSubtotal/cbc:TaxableAmount/text()")[0]) == D(net_total))
chk("Dates formatted YYYY-MM-DD (Peppol F001)",
    all(__import__("re").match(r"^\d{4}-\d{2}-\d{2}$", d) for d in x("//cbc:IssueDate/text()") + x("//cbc:DueDate/text()")))
def iban_ok(iban):
    s = iban.replace(" ", "")
    num = "".join(str(int(c, 36)) if c.isalpha() else c for c in (s[4:] + s[:4]))
    return int(num) % 97 == 1
chk("IBAN format (BT-84): BE IBAN passes ISO 13616 mod-97 check",
    iban_ok(inv["payee_iban"]) and len(inv["payee_iban"].replace(" ", "")) == 16)
fails = [r for r in R if not r[1]]
log.append(f"3. EN 16931 / Peppol BIS rule subset (Python, {len(R)} checks): "
           f"{'PASS all' if not fails else 'FAIL: ' + str([f[0] for f in fails])}")
for n, c, d in R: log.append(f"     [{'PASS' if c else 'FAIL'}] {n}")
log.append("4. NOT performed: official Peppol BIS Schematron validation (requires an XSLT 2.0/"
           "Schematron engine or an online validator account) and live VIES lookups of the "
           "sample VAT IDs (sample data uses invented numbers and .example domains).")
(BASE / "validation-log.txt").write_text("\n".join(log) + "\n")
print("\n".join(log))
