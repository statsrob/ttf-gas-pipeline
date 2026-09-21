import os
from pathlib import Path
from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(ROOT / "google-credentials.json")

PROJECT = "ttf-gas-pipeline"
DATASET = "ttf_gas"
BUCKET = "ttf-gas-pipeline-lake"
TABLE = "stg_ttf_panel"
URI = f"gs://{BUCKET}/raw/ttf_monthly_panel.parquet"

def load() -> None:
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.{DATASET}.{TABLE}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="trade_date",
        ),
        clustering_fields=["delivery_month"],
    )
    job = client.load_table_from_uri(URI, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)
    print(f"loaded {table.num_rows} rows into {table_id}")
    print("partition:", table.time_partitioning)
    print("cluster:", table.clustering_fields)

if __name__ == "__main__":
    load()