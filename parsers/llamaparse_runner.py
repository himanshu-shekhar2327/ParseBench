
import csv
import os
import time
from pathlib import Path

from llama_cloud import LlamaCloud

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "llamaparse" / "synthetic_invoice"
RESULTS_CSV = ROOT / "results" / "llamaparse_results.csv"

SAMPLE_FILES = [
    ROOT / "documents/digital_pdf/synthetic_invoice.pdf",
    ROOT / "documents/scanned_pdf/synthetic_invoice_scan.pdf",
    ROOT / "documents/docx/synthetic_invoice.docx",
    ROOT / "documents/xlsx/synthetic_invoice.xlsx",
    ROOT / "documents/pptx/synthetic_invoice.pptx",
    ROOT / "documents/images/synthetic_invoice.png",
]

TIER = "fast"


def main():
    if not os.environ.get("LLAMA_CLOUD_API_KEY"):
        raise SystemExit(
            "LLAMA_CLOUD_API_KEY is missing. "
            "Configure it in your terminal before running."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    client = LlamaCloud()

    fields = [
        "document",
        "format",
        "tier",
        "status",
        "duration_seconds",
        "output_bytes",
        "error",
    ]

    succeeded = 0

    with RESULTS_CSV.open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()

        for index, source in enumerate(SAMPLE_FILES, start=1):
            print(f"[{index}/{len(SAMPLE_FILES)}] {source.name}")

            row = {
                "document": str(source.relative_to(ROOT)),
                "format": source.suffix.lower(),
                "tier": TIER,
                "status": "failed",
                "duration_seconds": 0,
                "output_bytes": 0,
                "error": "",
            }

            start = time.perf_counter()

            try:
                if not source.is_file():
                    raise FileNotFoundError(
                        f"Input file not found: {source}"
                    )

                # Upload the source document.
                uploaded = client.files.create(
                    file=str(source),
                    purpose="parse",
                )

                # Submit and wait for the parsing job.
                result = client.parsing.parse(
                    file_id=uploaded.id,
                    tier=TIER,
                    version="latest",
                    expand=["markdown"],
                )

                markdown_result = result.markdown
                pages = (
                    getattr(markdown_result, "pages", None) or []
                )

                if not pages:
                    raise RuntimeError(
                        "Parsing returned no Markdown pages."
                    )

                page_texts = []
                for page in pages:
                    if getattr(page, "success", True):
                        text = getattr(page, "markdown", None)
                        if text:
                            page_texts.append(text)

                if not page_texts:
                    raise RuntimeError(
                        "No successful pages contained Markdown."
                    )

                markdown = "\n\n".join(page_texts)

                # Keep filenames compatible with our Docling evaluator.
                output_path = (
                    OUTPUT_DIR / f"{source.stem}_{source.suffix[1:]}.md"
                )
                output_path.write_text(
                    markdown, encoding="utf-8"
                )

                row["status"] = "success"
                row["output_bytes"] = output_path.stat().st_size
                succeeded += 1

                print(
                    f"  OK | pages={len(pages)} | "
                    f"output={output_path.name}"
                )

            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                print(f"  FAILED | {row['error']}")

            row["duration_seconds"] = round(
                time.perf_counter() - start, 4
            )

            writer.writerow(row)
            csv_file.flush()

    print("\nLlamaParse sample benchmark complete.")
    print(f"Tier: {TIER}")
    print(f"Successful: {succeeded}/{len(SAMPLE_FILES)}")
    print(f"Results: {RESULTS_CSV}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
