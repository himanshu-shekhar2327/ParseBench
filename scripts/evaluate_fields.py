
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument(
    "engine",
    choices=["liteparse", "docling", "llamaparse"],
    help="Parser output directory to evaluate",
)
args = parser.parse_args()

OUTPUT_DIR = ROOT / "outputs" / args.engine / "synthetic_invoice"
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

# Evaluate the same five formats for both engines.
COMMON_FORMATS = {"docx", "xlsx", "pptx", "png", "scanned_pdf"}



def get_format(path):
    name = path.stem.lower()

    # LiteParse uses short filenames such as docx.md.
    if name in {"docx", "xlsx", "pptx"}:
        return name
    if name == "image":
        return "png"
    if name == "scanned_pdf":
        return "scanned_pdf"

    # Docling uses names such as synthetic_invoice_docx.md.
    if name.endswith("_scan_pdf"):
        return "scanned_pdf"

    for fmt in ("docx", "xlsx", "pptx", "png"):
        if name.endswith("_" + fmt):
            return fmt

    return None



def found(field, expected, text):
    if field in {"subtotal", "tax", "total"}:
        pattern = rf"(?<!\d){re.escape(expected)}(?:\.0+)?(?!\d)"
        return re.search(pattern, text) is not None

    normalized_text = re.sub(r"\s+", " ", text).casefold()
    normalized_expected = re.sub(r"\s+", " ", expected).casefold()
    return normalized_expected in normalized_text


files = []
for path in sorted(OUTPUT_DIR.glob("*.md")):
    fmt = get_format(path)
    if fmt in COMMON_FORMATS:
        files.append((fmt, path))

if not files:
    raise SystemExit(f"No comparable Markdown files found in {OUTPUT_DIR}")

passed_total = 0
checks_total = 0

print(f"Engine: {args.engine}")
print(f"{'FORMAT':<14} {'FIELDS CORRECT':<16} MISSING FIELDS")
print("-" * 75)

for fmt, path in files:
    text = path.read_text(encoding="utf-8")
    missing = [
        field for field, expected in checks.items()
        if not found(field, expected, text)
    ]

    passed = len(checks) - len(missing)
    passed_total += passed
    checks_total += len(checks)

    print(
        f"{fmt:<14} {passed}/{len(checks):<14} "
        f"{', '.join(missing) or 'None'}"
    )

print("-" * 75)
print(f"Total: {passed_total}/{checks_total}")
print(f"Field recovery rate: {passed_total / checks_total * 100:.1f}%")
print("This is expected-field recovery, not full document accuracy.")
