import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "outputs" / "azure_full"

FILES = {
    "digital_pdf": OUTPUT_ROOT / "digital_pdf" / "synthetic_invoice.md",
    "png": OUTPUT_ROOT / "images" / "synthetic_invoice.md",
    "invoice_scan_png": OUTPUT_ROOT / "invoices" / "images" / "invoice_scan.md",
    "scanned_pdf": OUTPUT_ROOT / "scanned_pdf" / "synthetic_invoice_scan.md",
}

EXPECTED_ROWS = [
    ("Notebook", "10", "50", "500"),
    ("Pen Set", "5", "80", "400"),
]


def normalize(text):
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("|", " ")
    text = re.sub(r"\\", "", text)
    return re.sub(r"\s+", " ", text).strip()


def number_pattern(value):
    return re.escape(value) + r"(?:\.0+)?"

def row_matches(row_text, expected):
    item, quantity, price, amount = expected
    text = normalize(row_text)
    pattern = (
        r"(?<!\w)" + re.escape(item)
        + r"\s+" + number_pattern(quantity)
        + r"\s+" + number_pattern(price)
        + r"\s+" + number_pattern(amount)
        + r"(?!\d)"
    )
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_rows(text):
    rows = []

    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", text, flags=re.I | re.S):
        cells = re.findall(
            r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr,
            flags=re.I | re.S
        )
        if cells:
            rows.append(" ".join(cells))

    for line in text.splitlines():
        if "|" in line:
            cells = [
                cell.strip()
                for cell in line.strip().strip("|").split("|")
            ]
            if cells and not all(
                re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))
                for cell in cells
            ):
                rows.append(" ".join(cells))

    rows.extend(text.splitlines())
    return rows


def values_present(text, expected):
    normalized = normalize(text)
    item, quantity, price, amount = expected
    patterns = [
        re.escape(item),
        r"(?<!\d)" + number_pattern(quantity) + r"(?!\d)",
        r"(?<!\d)" + number_pattern(price) + r"(?!\d)",
        r"(?<!\d)" + number_pattern(amount) + r"(?!\d)",
    ]
    return all(
        re.search(pattern, normalized, flags=re.I) is not None
        for pattern in patterns
    )


def main():
    strict_total = 0
    values_total = 0
    evaluated = 0
    missing_files = 0

    print(
        f"{'FORMAT':<18} {'STRICT ROWS':<13} "
        f"{'VALUES FOUND':<13} DETAILS"
    )
    print("-" * 80)

    for fmt, path in FILES.items():
        if not path.is_file():
            missing_files += 1
            print(f"{fmt:<18} {'SKIPPED':<13} {'SKIPPED':<13} Missing output")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        rows = extract_rows(text)
        strict_count = 0
        values_count = 0
        missing = []

        for expected in EXPECTED_ROWS:
            strict = any(row_matches(row, expected) for row in rows)
            values = values_present(text, expected)

            strict_count += int(strict)
            values_count += int(values)

            if not strict:
                missing.append(expected[0])

        strict_total += strict_count
        values_total += values_count
        evaluated += len(EXPECTED_ROWS)

        details = (
            "Both rows aligned"
            if not missing
            else "Not aligned: " + ", ".join(missing)
        )

        print(
            f"{fmt:<18} {strict_count}/2{'':<8} "
            f"{values_count}/2{'':<8} {details}"
        )

    print("-" * 80)
    print(f"Strict row preservation: {strict_total}/{evaluated}")
    if evaluated:
        print(f"Strict rate: {strict_total / evaluated * 100:.1f}%")
        print(f"Row-value presence: {values_total}/{evaluated}")
        print(f"Value-presence rate: {values_total / evaluated * 100:.1f}%")
    print(f"Missing output files: {missing_files}")
    print("Note: value presence does not prove correct item-to-value relationships.")


if __name__ == "__main__":
    main()
