import csv
import time
from pathlib import Path

from docling.document_converter import DocumentConverter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "docling" / "synthetic_invoice"
RESULTS_CSV = ROOT / "results" / "docling_results.csv"

# Start with the six controlled samples, not the full research-paper corpus.
SAMPLE_FILES = [
    ROOT / "documents/digital_pdf/synthetic_invoice.pdf",
    ROOT / "documents/scanned_pdf/synthetic_invoice_scan.pdf",
    ROOT / "documents/docx/synthetic_invoice.docx",
    ROOT / "documents/xlsx/synthetic_invoice.xlsx",
    ROOT / "documents/pptx/synthetic_invoice.pptx",
    ROOT / "documents/images/synthetic_invoice.png",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    converter = DocumentConverter()
    fields = [
        "document",
        "format",
        "status",
        "duration_seconds",
        "output_bytes",
        "error",
    ]

    succeeded = 0

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()

        for index, source in enumerate(SAMPLE_FILES, start=1):
            print(f"[{index}/{len(SAMPLE_FILES)}] {source.name}")

            row = {
                "document": str(source.relative_to(ROOT)),
                "format": source.suffix.lower(),
                "status": "failed",
                "duration_seconds": 0,
                "output_bytes": 0,
                "error": "",
            }

            start = time.perf_counter()

            try:
                if not source.is_file():
                    raise FileNotFoundError(f"Missing input: {source}")

                result = converter.convert(source)
                markdown = result.document.export_to_markdown()

                output_path = OUTPUT_DIR / f"{source.stem}_{source.suffix[1:]}.md"
                output_path.write_text(markdown, encoding="utf-8")

                row["status"] = "success"
                row["output_bytes"] = output_path.stat().st_size
                succeeded += 1

                print(f"  OK | output={output_path.name}")

            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                print(f"  FAILED | {row['error']}")

            row["duration_seconds"] = round(
                time.perf_counter() - start, 4
            )
            writer.writerow(row)
            csv_file.flush()

    print("\nDocling sample benchmark complete.")
    print(f"Successful: {succeeded}/{len(SAMPLE_FILES)}")
    print(f"Results: {RESULTS_CSV}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
