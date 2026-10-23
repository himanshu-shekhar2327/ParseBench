import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = {
    "liteparse": ROOT / "outputs/liteparse/synthetic_invoice",
    "docling": ROOT / "outputs/docling/synthetic_invoice",
    "llamaparse": ROOT / "outputs/llamaparse/synthetic_invoice",
}

FILES = {
    "liteparse": {
        "docx": "docx.md",
        "xlsx": "xlsx.md",
        "pptx": "pptx.md",
        "png": "image.md",
        "scanned_pdf": "scanned_pdf.md",
    },
    "docling": {
        "docx": "synthetic_invoice_docx.md",
        "xlsx": "synthetic_invoice_xlsx.md",
        "pptx": "synthetic_invoice_pptx.md",
        "png": "synthetic_invoice_png.md",
        "scanned_pdf": "synthetic_invoice_scan_pdf.md",
    },
    "llamaparse": {
        "docx": "synthetic_invoice_docx.md",
        "xlsx": "synthetic_invoice_xlsx.md",
        "pptx": "synthetic_invoice_pptx.md",
        "png": "synthetic_invoice_png.md",
        "scanned_pdf": "synthetic_invoice_scan_pdf.md",
    },
}

EXPECTED_ROWS = [
    ("Notebook", "10", "50", "500"),
    ("Pen Set", "5", "80", "400"),
]


def normalize(text):
    """Normalize HTML entities, Markdown separators, and whitespace."""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("|", " ")
    text = re.sub(r"\\", "", text)
    return re.sub(r"\s+", " ", text).strip()


def number_pattern(value):
    """Accept integers and decimal forms such as 50, 50.0, or 50.00."""
    return re.escape(value) + r"(?:\.0+)?"


def row_matches(row_text, expected):
    """Check whether all four expected values occur in one extracted row."""
    item, quantity, price, amount = expected
    text = normalize(row_text)

    pattern = (
        r"(?<!\w)" + re.escape(item) +
        r"\s+" + number_pattern(quantity) +
        r"\s+" + number_pattern(price) +
        r"\s+" + number_pattern(amount) +
        r"(?!\d)"
    )
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_rows(text):
    """Extract HTML table rows, Markdown table rows, and ordinary text lines."""
    rows = []

    # HTML tables: keep each <tr> together, including its individual cells.
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", text, flags=re.I | re.S):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr,
                           flags=re.I | re.S)
        if cells:
            rows.append(" ".join(cells))

    # Markdown tables: each pipe-delimited line is a separate row.
    for line in text.splitlines():
        if "|" in line:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and not all(
                re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))
                for cell in cells
            ):
                rows.append(" ".join(cells))

    # Fallback for parsers that put each complete row on one ordinary line.
    rows.extend(text.splitlines())

    return rows


def row_value_tokens_present(text, expected):
    """Check whether all expected values appear somewhere in the document.

    This does NOT prove that the values are associated with the correct item.
    """
    normalized = normalize(text)
    item, quantity, price, amount = expected

    checks = [
        re.search(re.escape(item), normalized, flags=re.I) is not None,
        re.search(r"(?<!\d)" + number_pattern(quantity) + r"(?!\d)",
                  normalized) is not None,
        re.search(r"(?<!\d)" + number_pattern(price) + r"(?!\d)",
                  normalized) is not None,
        re.search(r"(?<!\d)" + number_pattern(amount) + r"(?!\d)",
                  normalized) is not None,
    ]
    return all(checks)


def main():
    strict_correct = 0
    value_recovered = 0
    evaluated_rows = 0
    missing_files = 0

    print(
        f"{'PARSER':<12} {'FORMAT':<12} "
        f"{'STRICT ROWS':<13} {'VALUES FOUND':<13} DETAILS"
    )
    print("-" * 90)

    for engine, formats in FILES.items():
        for fmt, filename in formats.items():
            path = OUTPUTS[engine] / filename

            if not path.is_file():
                missing_files += 1
                print(
                    f"{engine:<12} {fmt:<12} "
                    f"{'SKIPPED':<13} {'SKIPPED':<13} "
                    f"Missing: {filename}"
                )
                continue

            text = path.read_text(encoding="utf-8", errors="replace")
            rows = extract_rows(text)
            missing_strict = []
            missing_values = []

            for expected in EXPECTED_ROWS:
                item = expected[0]
                strict_found = any(row_matches(row, expected) for row in rows)
                values_found = row_value_tokens_present(text, expected)

                if strict_found:
                    strict_correct += 1
                else:
                    missing_strict.append(item)

                if values_found:
                    value_recovered += 1
                else:
                    missing_values.append(item)

                evaluated_rows += 1

            strict_count = len(EXPECTED_ROWS) - len(missing_strict)
            value_count = len(EXPECTED_ROWS) - len(missing_values)

            details = (
                "Both rows aligned"
                if not missing_strict
                else "Not aligned: " + ", ".join(missing_strict)
            )

            print(
                f"{engine:<12} {fmt:<12} "
                f"{strict_count}/2{'':<8} "
                f"{value_count}/2{'':<8} {details}"
            )

    print("-" * 90)
    print(f"Strict row preservation: {strict_correct}/{evaluated_rows}")
    print(
        "Strict row preservation rate: "
        f"{strict_correct / evaluated_rows * 100:.1f}%"
        if evaluated_rows else "Strict row preservation rate: N/A"
    )
    print(f"Row-value presence: {value_recovered}/{evaluated_rows}")
    print(
        "Row-value presence rate: "
        f"{value_recovered / evaluated_rows * 100:.1f}%"
        if evaluated_rows else "Row-value presence rate: N/A"
    )
    print(f"Missing output files: {missing_files}")
    print()
    print(
        "Caution: row-value presence only checks whether expected values "
        "occur in the document. It does not validate their relationships."
    )


if __name__ == "__main__":
    main()
