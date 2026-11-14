import sys
from pathlib import Path
import os
from google.cloud import bigquery

PROJECT = "green-llm-observatory"
#TABLE = f"{PROJECT}.observatory.responses"
TABLE = os.environ.get("BQ_TABLE", f"{PROJECT}.observatory.responses")
LOCATION = "EU"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

SCHEMA = [
    bigquery.SchemaField("run_id", "STRING"),
    bigquery.SchemaField("repeat", "INTEGER"),
    bigquery.SchemaField("temperature", "FLOAT"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("prompt_id", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("correct", "BOOLEAN"),
    bigquery.SchemaField("lenient_correct", "BOOLEAN"),
    bigquery.SchemaField("output", "STRING"),
    bigquery.SchemaField("latency_s", "FLOAT"),
    bigquery.SchemaField("total_latency_s", "FLOAT"),
    bigquery.SchemaField("input_tokens", "INTEGER"),
    bigquery.SchemaField("output_tokens", "INTEGER"),
    bigquery.SchemaField("thought_tokens", "INTEGER"),
    bigquery.SchemaField("total_tokens", "INTEGER"),
    bigquery.SchemaField("attempts", "INTEGER"),
    bigquery.SchemaField("error", "STRING"),
    bigquery.SchemaField("harness_version", "STRING"),
    bigquery.SchemaField("language", "STRING"),
    bigquery.SchemaField("pair_id", "STRING"),
]


def already_loaded(client, run_id):
    """True if rows from this run are already in the table."""
    job = client.query(
        f"SELECT COUNT(*) AS n FROM `{TABLE}` WHERE run_id = @run_id",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        ),
        location=LOCATION,
    )
    return list(job.result())[0].n > 0


def load_file(client, path):
    run_id = path.stem.removeprefix("run_")
    if already_loaded(client, run_id):
        print(f"Skipped: run {run_id} is already in BigQuery.")
        return

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    with path.open("rb") as f:
        job = client.load_table_from_file(f, TABLE, job_config=job_config, location=LOCATION)
    job.result()  # wait until the load finishes
    print(f"Loaded {job.output_rows} rows from {path.name} into {TABLE}")


def main():
    client = bigquery.Client(project=PROJECT)
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = sorted(RESULTS_DIR.glob("run_*.jsonl"))[-1]
    load_file(client, path)


if __name__ == "__main__":
    main()