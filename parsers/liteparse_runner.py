
import argparse
import csv
import time
import traceback
from pathlib import Path

from liteparse import LiteParse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "documents"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "liteparse"
DEFAULT_RESULTS = PROJECT_ROOT / "results" / "liteparse_results.csv"


def find_pdfs(input_dir: Path):
    """Return all PDFs recursively in a directory."""
    return sorted(
        path for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def parse_documents(
    input_dir: Path,
    output_dir: Path,
    results_csv: Path,
):
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    pdf_files = find_pdfs(input_dir)
    if not pdf_files:
        print(f"No PDFs found under: {input_dir}")
        print("Add PDFs to the documents/ directory and retry.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    results_csv.parent.mkdir(parents=True, exist_ok=True)

    parser = LiteParse(
        output_format="markdown",
        quiet=True,
    )

    fieldnames = [
        "document",
        "relative_path",
        "status",
        "pages",
        "duration_seconds",
        "output_bytes",
        "error",
    ]

    # Append results so interrupted runs do not erase previous records.
    file_exists = results_csv.exists() and results_csv.stat().st_size > 0

    with results_csv.open(
        "a", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for index, pdf_path in enumerate(pdf_files, start=1):
            relative_path = pdf_path.relative_to(input_dir)
            output_path = (
                output_dir / relative_path
            ).with_suffix(".md")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"[{index}/{len(pdf_files)}] {relative_path}")

            start = time.perf_counter()
            pages = 0
            output_bytes = 0
            status = "failed"
            error = ""

            try:
                result = parser.parse(str(pdf_path))
                text = result.text or ""

                output_path.write_text(text, encoding="utf-8")

                pages = result.total_pages
                output_bytes = output_path.stat().st_size
                status = "success"

                print(
                    f"  OK | pages={pages} | "
                    f"output={output_bytes} bytes"
                )

            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                print(f"  FAILED | {error}")

            duration = time.perf_counter() - start

            writer.writerow({
                "document": pdf_path.name,
                "relative_path": str(relative_path),
                "status": status,
                "pages": pages,
                "duration_seconds": round(duration, 4),
                "output_bytes": output_bytes,
                "error": error,
            })

            # Keep progress/results available if the run is interrupted.
            csv_file.flush()

    print("\nLiteParse batch complete.")
    print(f"Documents discovered: {len(pdf_files)}")
    print(f"Results saved to: {results_csv}")
    print(f"Parsed outputs saved under: {output_dir}")


def main():
    cli = argparse.ArgumentParser(
        description="Batch benchmark LiteParse on PDF documents."
    )
    cli.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Directory containing PDFs, including subfolders.",
    )
    cli.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for parsed Markdown outputs.",
    )
    cli.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS,
        help="CSV file for benchmark measurements.",
    )

    args = cli.parse_args()

    parse_documents(
        input_dir=args.input.resolve(),
        output_dir=args.output.resolve(),
        results_csv=args.results.resolve(),
    )


if __name__ == "__main__":
    main()
