import csv
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "benchmark_manifest.csv"
OUTPUT_ROOT = ROOT / "outputs" / "liteparse_full"
RESULTS = ROOT / "results" / "liteparse_full_benchmark.csv"

SUPPORTED = {".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

FIELDS = [
    "document_id", "relative_path", "format", "status",
    "duration_seconds", "output_bytes", "error",
]


def main():
    if not MANIFEST.is_file():
        raise SystemExit(f"Manifest not found: {MANIFEST}")

    with MANIFEST.open(newline="", encoding="utf-8") as f:
        documents = list(csv.DictReader(f))

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for i, item in enumerate(documents, 1):
            relative = Path(item["relative_path"])
            source = ROOT / "documents" / relative
            output = (OUTPUT_ROOT / relative).with_suffix(".md")
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

            print(f"[{i}/{len(documents)}] {item['relative_path']}", flush=True)

            if source.suffix.lower() not in SUPPORTED:
                row["status"] = "unsupported"
                row["error"] = "Format not in configured LiteParse CLI support list"
                print("  UNSUPPORTED", flush=True)
            elif not source.is_file():
                row["error"] = "Input file missing"
                print("  FAILED: input file missing", flush=True)
            else:
                start = time.perf_counter()
                try:
                    completed = subprocess.run(
                        [
                            "lit", "parse", str(source),
                            "--format", "markdown",
                            "-o", str(output),
                            "--quiet",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=600,
                        check=False,
                    )

                    if completed.returncode != 0:
                        detail = (completed.stderr or completed.stdout or "").strip()
                        raise RuntimeError(detail or f"CLI exited {completed.returncode}")

                    if not output.is_file():
                        raise RuntimeError("CLI succeeded but output file was not created")

                    row["status"] = "success"
                    row["output_bytes"] = output.stat().st_size
                    print(f"  OK | {row['output_bytes']} bytes", flush=True)

                except Exception as exc:
                    row["error"] = f"{type(exc).__name__}: {exc}"[:2000]
                    print(f"  FAILED: {row['error']}", flush=True)
                finally:
                    row["duration_seconds"] = round(time.perf_counter() - start, 4)

            writer.writerow(row)
            f.flush()

    print(f"\nResults: {RESULTS}")
    print(f"Outputs: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
