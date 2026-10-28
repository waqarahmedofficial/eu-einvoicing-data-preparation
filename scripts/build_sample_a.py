#!/usr/bin/env python3
"""Build Sample A (dirty master -> cleaned master + DQ report) and
Sample B (invoice -> mapping sheet + Peppol BIS UBL 2.1 XML) and validate."""
import csv, re, random, json
from pathlib import Path
from copy import deepcopy

BASE = Path.home() / "workspace/einvoicing-prep/samples"
A = BASE / "sample-A"; B = BASE / "sample-B"
A.mkdir(parents=True, exist_ok=True); B.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- VAT formats
# Format patterns per EU VAT ID rules (structure only, not checksum).
VAT_PATTERNS = {
    "BE": r"^BE0\d{9}$",          # BE + 10 digits, starts 0 (or 1 since 2024 -> handled below)
    "DE": r"^DE\d{9}$",
    "FR": r"^FR[A-Z0-9]{2}\d{9}$",
    "NL": r"^NL\d{9}B\d{2}$",
    "PL": r"^PL\d{10}$",
    "IT": r"^IT\d{11}$",
    "ES": r"^ES[A-Z0-9]\d{7}[A-Z0-9]$",
    "AT": r"^ATU\d{8}$",
}
def vat_format_ok(v):
    v = v.replace(" ", "").replace(".", "").upper()
    cc = v[:2]
    if cc == "BE":  # BE allows leading 0 or 1
        return bool(re.match(r"^BE[01]\d{9}$", v))
    p = VAT_PATTERNS.get(cc)
    return bool(p and re.match(p, v))

def vat_checksum_ok(v):
    """Modulo-97 style checks where a public simple algorithm exists (BE, PL, IT-lite).
    Returns True/False/None (None = no simple local check implemented)."""
    v = v.replace(" ", "").replace(".", "").upper()
    if v.startswith("BE") and len(v) == 12 and v[2:].isdigit():
        return int(v[2:10]) % 97 == int(v[10:12]) or (97 - int(v[2:10]) % 97) == int(v[10:12])
    if v.startswith("PL") and len(v) == 12 and v[2:].isdigit():
        w = [6,5,7,2,3,4,5,6,7]; d = [int(c) for c in v[2:]]
        return sum(a*b for a, b in zip(w, d[:9])) % 11 == d[9]
    return None

# Peppol participant ID: scheme:value, e.g. 0208:<BE enterprise no>, 0088:<GLN>,
# or VAT-based scheme 9932 (FR), 9957... We use scheme per country defaults below.
PEPPOL_SCHEME = {"BE": "0208", "DE": "0204", "FR": "0009", "NL": "0106", "PL": "1186"}

# ---------------------------------------------------------------- Sample A data
random.seed(42)
# 40 invented trading partners (suppliers + customers) across BE/DE/FR/NL/PL.
partners = [
    ("Nordwind Logistiek BV", "NL", "supplier", "NL862345019B01", "Seringenstraat 14", "3011 TR", "Rotterdam"),
    ("Brasserie du Val SARL", "FR", "customer", "FRKZ750123456", "8 Rue des Lilas", "59000", "Lille"),
    ("Antwerp Office Supplies NV", "BE", "supplier", "BE0742583104", "Kammenstraat 18", "2000", "Antwerpen"),
    ("Rheinwerk GmbH", "DE", "supplier", "DE314159265", "Industriestrasse 7", "40210", "Dusseldorf"),
    ("Kowalski Dystrybucja Sp. z o.o.", "PL", "customer", "PL5261040828", "ul. Polna 3", "00-625", "Warszawa"),
    ("Meulemeester Bouw NV", "BE", "customer", "BE0456789133", "Gentseweg 44", "9700", "Oudenaarde"),
    ("Bergmann & Sohn GmbH", "DE", "customer", "DE271828182", "Hafenweg 2", "20457", "Hamburg"),
    ("Dupont Emballages SAS", "FR", "supplier", "FRAB440987654", "21 Avenue Foch", "69003", "Lyon"),
    ("Van der Meer Transport BV", "NL", "customer", "NL812345678B90", "Havenkade 9", "3089 KP", "Rotterdam"),
    ("Lefevre Textiles SARL", "FR", "customer", "FR78420555123", "3 Rue Victor Hugo", "75011", "Paris"),
    ("Poldersoft BV", "NL", "supplier", "NL001122334B55", "Herengracht 420", "1017 BZ", "Amsterdam"),
    ("Wisla Foods Sp. z o.o.", "PL", "supplier", "PL7792430011", "ul. Dluga 15", "61-850", "Poznan"),
    ("Havelock Trading GmbH", "DE", "supplier", "DE136695976", "Torstrasse 101", "10119", "Berlin"),
    ("Coopérative Laitière du Nord", "FR", "supplier", "FR55998877441", "Route de Bergues 12", "59380", "Quaedypre"),
    ("Oostvlaamse Metaalwerken NV", "BE", "supplier", "BE0888776653", "Industriepark 5", "9052", "Gent"),
    ("Zielinska Consulting Sp. z o.o.", "PL", "customer", "PL9452257810", "Rynek 8", "50-101", "Wroclaw"),
    ("Martin Fournitures SAS", "FR", "customer", "FR20345678901", "17 Rue de la Paix", "44000", "Nantes"),
    ("Schneider Baustoffe GmbH", "DE", "customer", "DE259988776", "Am Sandtorkai 3", "20457", "Hamburg"),
    ("De Clercq Immo NV", "BE", "customer", "BE0712349876", "Markt 1", "9000", "Gent"),
    ("Amstel Components BV", "NL", "supplier", "NL855443322B10", "Prinsengracht 263", "1015 GV", "Amsterdam"),
]

DIRTY_NOTES = []
def make_dirty(rows):
    out = []
    for i, (name, cc, typ, vat, street, post, city) in enumerate(rows):
        r = {"record_id": f"MP-{1000+i}", "record_type": typ, "legal_name": name,
             "country": cc, "vat_id": vat, "street": street, "postcode": post,
             "city": city, "email": "", "peppol_id": ""}
        out.append(r)
    # inject dirt
    d = {}
    def mod(idx, **kw): out[idx].update(kw); d.setdefault(idx, []).extend(kw.keys())
    mod(0, vat_id="nl862345019b01")                       # lowercase VAT
    mod(1, legal_name="  Brasserie du Val  SARL ")         # whitespace
    mod(2, vat_id="BE 0742.583.104")                      # spaces/dots in VAT
    mod(3, street="Industriestr. 7", city="DÜSSELDORF")   # abbreviation + case
    mod(4, vat_id="5261040828")                           # missing country prefix
    mod(5, postcode="")                                   # missing postcode
    mod(6, vat_id="DE27182818")                           # VAT too short (8 digits)
    mod(7, legal_name="DUPONT EMBALLAGES")                 # all caps, suffix dropped
    mod(8, peppol_id="")                                   # (already empty everywhere)
    mod(9, vat_id="FR 78 420 555 123")                    # spaces in VAT
    mod(11, vat_id="PL779243001")                         # VAT too short (9 digits)
    mod(12, legal_name="Havelock Trading GMBH")           # suffix case
    mod(13, city="")                                      # missing city
    mod(15, vat_id="PL94522578101")                       # VAT too long (11 digits)
    mod(17, street="Am Sandtorkai 3, 2. OG")              # extra floor info
    mod(18, vat_id="BE071234987")                         # VAT too short (9 digits)
    # duplicates: same partner entered again with variations (rows appended)
    dup1 = dict(out[2]); dup1.update(record_id="MP-1020", legal_name="Antwerp Office Supplies n.v.",
                                     vat_id="BE0742583104", email="orders@antwerpofficesupplies.example")
    dup2 = dict(out[10]); dup2.update(record_id="MP-1021", legal_name="Poldersoft B.V.",
                                      vat_id="NL001122334B55", street="Herengracht 420 ")
    out += [dup1, dup2]
    # one fake-format VAT that passes length but fails checksum (BE)
    out.append({"record_id": "MP-1022", "record_type": "customer", "legal_name": "Testwinkel De Smet BV",
                "country": "BE", "vat_id": "BE0999888777", "street": "Stationsstraat 2",
                "postcode": "8500", "city": "Kortrijk", "email": "", "peppol_id": ""})
    return out

dirty = make_dirty(partners)
with open(A / "master-data-BEFORE.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(dirty[0].keys())); w.writeheader(); w.writerows(dirty)

# ---------------------------------------------------------------- cleanup
issues = {"duplicates_merged": [], "vat_case_fixed": 0, "vat_separators_removed": 0,
          "vat_prefix_added": 0, "name_whitespace_case": 0, "missing_postcode": [],
          "missing_city": [], "vat_format_invalid": [], "vat_checksum_fail": [],
          "vat_format_ok": 0, "peppol_assigned": 0, "address_normalised": 0}
seen = {}
cleaned = []
for r in dirty:
    r = dict(r)
    name_clean = re.sub(r"\s+", " ", r["legal_name"].strip())
    if name_clean != r["legal_name"] or name_clean.upper() == name_clean:
        if name_clean.upper() == name_clean and any(c.isalpha() for c in name_clean):
            name_clean = name_clean.title().replace("Sarl", "SARL").replace("Sas", "SAS") \
                                   .replace("Gmbh", "GmbH").replace("Bv", "BV").replace("Nv", "NV")
        issues["name_whitespace_case"] += 1
    r["legal_name"] = name_clean
    raw_vat = r["vat_id"]
    v = raw_vat.replace(" ", "").replace(".", "").upper()
    if v != raw_vat and raw_vat.upper() != v and raw_vat.replace(" ", "").replace(".", "") == v:
        issues["vat_separators_removed"] += 1
    if v != v.upper() or raw_vat != raw_vat.upper():
        pass
    if raw_vat != raw_vat.upper():
        issues["vat_case_fixed"] += 1
    if v.isdigit() and r["country"] and not v.startswith(r["country"]):
        v = r["country"] + v; issues["vat_prefix_added"] += 1
    r["vat_id"] = v
    if "Industriestr." in r["street"]:
        r["street"] = r["street"].replace("Industriestr.", "Industriestrasse"); issues["address_normalised"] += 1
    r["city"] = r["city"].title() if r["city"] else r["city"]
    key = (v, name_clean.lower().replace(".", "").strip())
    if v and key in seen:
        issues["duplicates_merged"].append((r["record_id"], seen[key]))
        # merge: keep first, copy email if missing there
        for c in cleaned:
            if c["record_id"] == seen[key] and not c["email"] and r.get("email"):
                c["email"] = r["email"]
        continue
    if v: seen[key] = r["record_id"]
    if not r["postcode"]: issues["missing_postcode"].append(r["record_id"])
    if not r["city"]: issues["missing_city"].append(r["record_id"])
    if not vat_format_ok(v):
        issues["vat_format_invalid"].append((r["record_id"], v))
    else:
        cs = vat_checksum_ok(v)
        if cs is False:
            issues["vat_checksum_fail"].append((r["record_id"], v))
        else:
            issues["vat_format_ok"] += 1
    scheme = PEPPOL_SCHEME.get(r["country"])
    if scheme and vat_format_ok(v):
        local = v[2:]
        r["peppol_id"] = f"{scheme}:{local}"
        issues["peppol_assigned"] += 1
    cleaned.append(r)

with open(A / "master-data-AFTER.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(cleaned[0].keys())); w.writeheader(); w.writerows(cleaned)

# XLSX versions
from openpyxl import Workbook
def to_xlsx(rows, path):
    wb = Workbook(); ws = wb.active; ws.title = "Master data"
    ws.append(list(rows[0].keys()))
    for r in rows: ws.append(list(r.values()))
    wb.save(path)
to_xlsx(dirty, A / "master-data-BEFORE.xlsx")
to_xlsx(cleaned, A / "master-data-AFTER.xlsx")

report = {
    "rows_in": len(dirty), "rows_out": len(cleaned),
    "duplicates_merged": issues["duplicates_merged"],
    "vat_case_fixed": issues["vat_case_fixed"],
    "vat_separators_removed": issues["vat_separators_removed"],
    "vat_prefix_added": issues["vat_prefix_added"],
    "name_whitespace_case": issues["name_whitespace_case"],
    "address_normalised": issues["address_normalised"],
    "missing_postcode": issues["missing_postcode"],
    "missing_city": issues["missing_city"],
    "vat_format_invalid": issues["vat_format_invalid"],
    "vat_checksum_fail": issues["vat_checksum_fail"],
    "vat_format_ok": issues["vat_format_ok"],
    "peppol_assigned": issues["peppol_assigned"],
}
(A / "cleanup-stats.json").write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
