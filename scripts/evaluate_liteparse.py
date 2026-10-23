
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "docling" / "synthetic_invoice"
GROUND_TRUTH = ROOT / "results" / "ground_truth.json"

with GROUND_TRUTH.open(encoding="utf-8") as f:
    truth = json.load(f)

# Numeric patterns accept both 900 and 900.00.
checks = {
    "vendor": truth["vendor"],
    "invoice_number": truth["invoice_number"],
    "invoice_date": truth["invoice_date"],
    "customer": truth["customer"],
    "subtotal": "900",
    "tax": "162",
    "total": "1062",
}

def field_found(field, expected, text):
    if field in {"subtotal", "tax", "total"}:
        pattern = rf"(?<!\d){re.escape(expected)}(?:\.0+)?(?!\d)"
        return re.search(pattern, text) is not None

    # Ignore case and differences in whitespace.
    normalized_text = re.sub(r"\s+", " ", text).casefold()
    normalized_expected = re.sub(r"\s+", " ", expected).casefold()
    return normalized_expected in normalized_text


files = sorted(OUTPUT_DIR.glob("*.md"))
if not files:
    raise SystemExit(f"No Markdown outputs found in {OUTPUT_DIR}")

total_checks = 0
total_passed = 0

print(f"{'FORMAT':<14} {'FIELDS CORRECT':<16} DETAILS")
print("-" * 85)

for path in files:
    text = path.read_text(encoding="utf-8")
    passed = []

    for field, expected in checks.items():
        total_checks += 1
        if field_found(field, expected, text):
            total_passed += 1
            passed.append(field)

    missing = [field for field in checks if field not in passed]

    print(
        f"{path.stem:<14} {len(passed)}/{len(checks):<14} "
        f"Missing/misread: {', '.join(missing) or 'None'}"
    )

print("-" * 85)
print(f"Overall field recovery: {total_passed}/{total_checks}")
print(f"Field recovery rate: {100 * total_passed / total_checks:.1f}%")
print("Note: this measures expected-field presence, not full document accuracy.")
