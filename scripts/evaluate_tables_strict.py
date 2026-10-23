import re
import csv
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = {
    "liteparse": (ROOT / "outputs/liteparse/synthetic_invoice", {
        "docx": "docx.md",
        "xlsx": "xlsx.md",
        "pptx": "pptx.md",
        "png": "image.md",
        "scanned_pdf": "scanned_pdf.md",
    }),
    "docling": (ROOT / "outputs/docling/synthetic_invoice", {
        "docx": "synthetic_invoice_docx.md",
        "xlsx": "synthetic_invoice_xlsx.md",
        "pptx": "synthetic_invoice_pptx.md",
        "png": "synthetic_invoice_png.md",
        "scanned_pdf": "synthetic_invoice_scan_pdf.md",
    }),
    "llamaparse": (ROOT / "outputs/llamaparse/synthetic_invoice", {
        "docx": "synthetic_invoice_docx.md",
        "xlsx": "synthetic_invoice_xlsx.md",
        "pptx": "synthetic_invoice_pptx.md",
        "png": "synthetic_invoice_png.md",
        "scanned_pdf": "synthetic_invoice_scan_pdf.md",
    }),
}

EXPECTED_ROWS = [
    ("Notebook", "10", "50", "500"),
    ("Pen Set", "5", "80", "400"),
]


def clean(value):
    value = unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("|", " ")
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value.replace(",", "")


def cell_matches(cell, expected):
    text = clean(cell)
    value = re.escape(expected)
    return re.search(r"(?<!\d)" + value + r"(?:\.0+)?(?!\d)", text) is not None


def extract_table_rows(text):
    rows = []

    # HTML tables: preserve cell boundaries and detect merged cells.
    for tr in re.findall(r"<tr\b([^>]*)>(.*?)</tr>", text, flags=re.I | re.S):
        attrs, body = tr
        cells = re.findall(
            r"<t[dh]\b([^>]*)>(.*?)</t[dh]>",
            body, flags=re.I | re.S
        )
        if cells:
            values = [clean(content) for _, content in cells]
            merged = any(
                re.search(r"\bcolspan\s*=\s*[\"']?([2-9]\d*)", attr, re.I)
                for attr, _ in cells
            )
            rows.append((values, merged))

    # Markdown tables: each cell is separated by a pipe.
    for line in text.splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        cells = [clean(c) for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            continue
        rows.append((cells, False))

    return rows


def row_is_structurally_correct(rows, expected):
    item, qty, price, amount = expected

    for cells, merged in rows:
        if merged or len(cells) < 4:
            continue

        # Find the item cell, then require the next three cells
        # to hold quantity, unit price, and amount respectively.
        for i, cell in enumerate(cells):
            if item.lower() in cell and i + 3 < len(cells):
                if (
                    cell_matches(cells[i + 1], qty)
                    and cell_matches(cells[i + 2], price)
                    and cell_matches(cells[i + 3], amount)
                ):
                    return True
    return False


def main():
    evaluated = 0
    correct = 0
    missing_files = 0

    print(f"{'PARSER':<12} {'FORMAT':<12} {'STRICT ROWS':<13} DETAILS")
    print("-" * 65)

    for parser, (folder, formats) in OUTPUTS.items():
        for fmt, filename in formats.items():
            path = folder / filename

            if not path.is_file():
                missing_files += 1
                print(f"{parser:<12} {fmt:<12} {'SKIPPED':<13} Missing {filename}")
                continue

            text = path.read_text(encoding="utf-8", errors="replace")
            rows = extract_table_rows(text)
            row_results = [
                row_is_structurally_correct(rows, expected)
                for expected in EXPECTED_ROWS
            ]

            passed = sum(row_results)
            evaluated += len(EXPECTED_ROWS)
            correct += passed
            missing = [
                EXPECTED_ROWS[i][0]
                for i, ok in enumerate(row_results) if not ok
            ]
            details = "Both rows preserved" if not missing else (
                "Not preserved: " + ", ".join(missing)
            )
            print(f"{parser:<12} {fmt:<12} {passed}/2{'':<8} {details}")

    print("-" * 65)
    print(f"Strict rows preserved: {correct}/{evaluated}")
    if evaluated:
        print(f"Strict row preservation rate: {correct / evaluated * 100:.1f}%")
    print(f"Missing files: {missing_files}")
    print("Note: checks separate item, quantity, price and amount cells in order.")


if __name__ == "__main__":
    main()
