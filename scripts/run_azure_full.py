import csv
import time
from pathlib import Path

from parsers.azure_parser import parse_document

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "benchmark_manifest.csv"
OUTPUT_ROOT = ROOT / "outputs" / "azure_full"
RESULTS = ROOT / "results" / "azure_full_benchmark.csv"

FIELDS = [
    "document_id",
    "relative_path",
    "format",
    "status",
    "duration_seconds",
    "output_bytes",
    "error",
]

# Formats directly accepted by the Azure prebuilt-layout API.
SUPPORTED_FORMATS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"
}


def main():
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        documents = list(csv.DictReader(f))

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    print(f"Processing {len(documents)} manifest entries with Azure.\n")

    with RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for index, item in enumerate(documents, 1):
            source = ROOT / "documents" / item["relative_path"]
            output = (OUTPUT_ROOT / item["relative_path"]).with_suffix(".md")
            output.parent.mkdir(parents=True, exist_ok=True)

            row = {
                "document_id": item["document_id"],
                "relative_path": item["relative_path"],
                "format": source.suffix.lower(),
                "status": "failed",
                "duration_seconds": "",
                "output_bytes": 0,
                "error": "",
            }

            print(
                f"[{index}/{len(documents)}] {item['relative_path']}",
                flush=True,
            )

            if source.suffix.lower() not in SUPPORTED_FORMATS:
                row["status"] = "unsupported"
                row["error"] = (
                    "Format is not directly supported by the Azure "
                    "prebuilt-layout API; no conversion attempted."
                )
                writer.writerow(row)
                f.flush()
                print("  UNSUPPORTED | native input format", flush=True)
                continue

            start = time.perf_counter()
            try:
                if not source.is_file():
                    raise FileNotFoundError(f"Missing input: {source}")

                markdown = parse_document(source)
                output.write_text(markdown, encoding="utf-8")

                row["status"] = "success"
                row["output_bytes"] = output.stat().st_size
                print(
                    f"  OK | {row['output_bytes']} bytes",
                    flush=True,
                )

            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"[:2000]
                print(f"  FAILED | {row['error']}", flush=True)

            row["duration_seconds"] = round(
                time.perf_counter() - start, 4
            )
            writer.writerow(row)
            f.flush()

    print(f"\nResults: {RESULTS}")
    print(f"Outputs: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
