import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "documents"
OUTPUT = ROOT / "results" / "benchmark_manifest.csv"

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["document_id", "relative_path", "extension", "category", "size_bytes"],
    )
    writer.writeheader()

    files = sorted(p for p in DOCS.rglob("*") if p.is_file())

    for index, path in enumerate(files, start=1):
        relative = path.relative_to(DOCS)
        parts = relative.parts

        if path.suffix.lower() == ".pdf":
            category = "research_pdf" if (
                parts[0] == "digital_pdf"
                and path.name != "synthetic_invoice.pdf"
            ) else (
                "scanned_pdf" if path.name == "synthetic_invoice_scan.pdf"
                else "synthetic_invoice_pdf"
            )
        elif path.suffix.lower() == ".png":
            category = "invoice_image"
        else:
            category = "office_document"

        writer.writerow({
            "document_id": f"DOC-{index:03d}",
            "relative_path": relative.as_posix(),
            "extension": path.suffix.lower(),
            "category": category,
            "size_bytes": path.stat().st_size,
        })

print(f"Created: {OUTPUT.relative_to(ROOT)}")
print(f"Documents: {len(files)}")
