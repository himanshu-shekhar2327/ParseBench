"""Read-only summary metrics for existing Parsebench CSV results."""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

PARSERS = {
    "docling": ("Docling", "docling_full_benchmark.csv", "Local"),
    "liteparse": ("LiteParse", "liteparse_full_benchmark.csv", "Local"),
    "llamaparse": ("LlamaParse", "llamaparse_full_benchmark.csv", "Cloud"),
    "azure": ("Azure DI", "azure_full_benchmark.csv", "Cloud"),
}

# Verified results from the existing synthetic-invoice evaluation scripts.
# These metrics cover targeted invoice samples, not the full benchmark corpus.
ACCURACY_RESULTS = {
    "docling": {
        "field_accuracy_percent": 97.1,
        "field_correct": 34,
        "field_total": 35,
        "structure_accuracy_percent": 60.0,
        "structure_correct": 6,
        "structure_total": 10,
    },
    "liteparse": {
        "field_accuracy_percent": 91.4,
        "field_correct": 32,
        "field_total": 35,
        "structure_accuracy_percent": 40.0,
        "structure_correct": 4,
        "structure_total": 10,
    },
    "llamaparse": {
        "field_accuracy_percent": 94.3,
        "field_correct": 33,
        "field_total": 35,
        "structure_accuracy_percent": 60.0,
        "structure_correct": 6,
        "structure_total": 10,
    },
    "azure": {
        "field_accuracy_percent": 89.3,
        "field_correct": 25,
        "field_total": 28,
        "structure_accuracy_percent": 37.5,
        "structure_correct": 3,
        "structure_total": 8,
    },
}


def get_benchmark_summary():
    metrics = []

    for parser_id, (name, filename, execution) in PARSERS.items():
        path = RESULTS_DIR / filename
        item = {
            "parser_id": parser_id,
            "parser_name": name,
            "execution": execution,
            "source_file": filename,
            "sample_size": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "unsupported_runs": 0,
            "failure_rate_percent": None,
            "median_latency_seconds": None,
            "p95_latency_seconds": None,
            "median_latency_per_page_seconds": None,
            "throughput_pages_per_minute": None,
            "startup_seconds": None,
            "field_accuracy_percent": None,
            "amount_accuracy_percent": None,
            "structure_accuracy_percent": None,
            "line_item_recall_percent": None,
            "field_correct": None,
            "field_total": None,
            "structure_correct": None,
            "structure_total": None,
            "silent_error_rate_percent": None,
            "cost_per_1000_pages_usd": None,
            "cost_per_usable_invoice_usd": None,
            "formats": [],
            "runs_locally": execution == "Local",
            "notes": [],
        }

        if not path.is_file():
            item["notes"].append("Benchmark CSV not found.")
            metrics.append(item)
            continue

        try:
            df = pd.read_csv(path)
        except Exception as exc:
            item["notes"].append(f"Could not read CSV: {type(exc).__name__}")
            metrics.append(item)
            continue

        if df.empty or "status" not in df.columns:
            item["notes"].append("CSV is empty or missing the status column.")
            metrics.append(item)
            continue

        status = df["status"].fillna("").astype(str).str.lower()
        success = status.isin(["success", "succeeded", "ok"])
        unsupported = status.str.contains("unsupported", na=False)
        failed = ~(success | unsupported)

        item["sample_size"] = int(len(df))
        item["successful_runs"] = int(success.sum())
        item["failed_runs"] = int(failed.sum())
        item["unsupported_runs"] = int(unsupported.sum())
        item["failure_rate_percent"] = round(
            100 * (failed.sum() + unsupported.sum()) / len(df), 2
        )

        if "duration_seconds" in df.columns:
            durations = pd.to_numeric(
                df.loc[success, "duration_seconds"], errors="coerce"
            ).dropna()

            if not durations.empty:
                item["median_latency_seconds"] = round(
                    float(durations.median()), 2
                )
                item["p95_latency_seconds"] = round(
                    float(durations.quantile(0.95)), 2
                )

        if "format" in df.columns:
            item["formats"] = sorted(
                df["format"].dropna().astype(str).str.lower().unique().tolist()
            )

        accuracy = ACCURACY_RESULTS.get(parser_id)
        if accuracy:
            item.update(accuracy)
            item["notes"].append(
                "Field recovery is from the targeted synthetic-invoice evaluation."
            )
            item["notes"].append(
                "Table preservation is from the strict synthetic-invoice row evaluator."
            )
            item["notes"].append(
                "These accuracy samples are separate from the full benchmark corpus."
            )

        item["notes"].append(
            "Latency percentiles use saved successful document runs, "
            "not repeated trials of each document."
        )
        item["notes"].append(
            "Overall document accuracy, page-normalized speed, startup time, "
            "and cost are not measured by this summary."
        )
        metrics.append(item)

    return {
        "source": "Existing results/*.csv files",
        "metrics": metrics,
        "methodology": {
            "failure_rate": "(Failed + unsupported) / all runs * 100",
            "accuracy": "Targeted synthetic-invoice field recovery and strict table preservation; not full-corpus accuracy.",
            "cost": "Not measured.",
        },
    }
