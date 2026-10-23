import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "outputs" / "azure_full"
GROUND_TRUTH = ROOT / "results" / "ground_truth.json"

with GROUND_TRUTH.open(encoding="utf-8") as f:
    truth = json.load(f)

checks = {
    "vendor": truth["vendor"],
    "invoice_number": truth["invoice_number"],
    "invoice_date": truth["invoice_date"],
    "customer": truth["customer"],
    "subtotal": "900",
    "tax": "162",
    "total": "1062",
}

files = {
    "digital_pdf": OUTPUT_ROOT / "digital_pdf" / "synthetic_invoice.md",
    "png": OUTPUT_ROOT / "images" / "synthetic_invoice.md",
    "invoice_scan_png": OUTPUT_ROOT / "invoices" / "images" / "invoice_scan.md",
    "scanned_pdf": OUTPUT_ROOT / "scanned_pdf" / "synthetic_invoice_scan.md",
}

def found(field, expected, text):
    if field in {"subtotal", "tax", "total"}:
        pattern = rf"(?<!\d){re.escape(expected)}(?:\.0+)?(?!\d)"
        return re.search(pattern, text) is not None

    normalized_text = re.sub(r"\s+", " ", text).casefold()
    normalized_expected = re.sub(r"\s+", " ", expected).casefold()
    return normalized_expected in normalized_text

passed_total = 0
checks_total = 0

print("Engine: Azure Document Intelligence")
print(f"{'FORMAT':<18} {'FIELDS CORRECT':<16} MISSING FIELDS")
print("-" * 80)

for fmt, path in files.items():
    if not path.exists():
        print(f"{fmt:<18} MISSING OUTPUT: {path}")
        continue

    text = path.read_text(encoding="utf-8")
    missing = [
        field for field, expected in checks.items()
        if not found(field, expected, text)
    ]

    passed = len(checks) - len(missing)
    passed_total += passed
    checks_total += len(checks)

    print(f"{fmt:<18} {passed}/{len(checks):<14} {', '.join(missing) or 'None'}")

print("-" * 80)
if checks_total:
    print(f"Total: {passed_total}/{checks_total}")
    print(f"Expected-field recovery: {passed_total / checks_total * 100:.1f}%")
print("Note: field recovery does not measure table structure or full document accuracy.")
