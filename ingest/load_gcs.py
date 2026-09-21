import os
from pathlib import Path
from google.cloud import storage

ROOT = Path(__file__).resolve().parents[1]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(ROOT / "google-credentials.json")

PROJECT = "ttf-gas-pipeline"
BUCKET = "ttf-gas-pipeline-lake"
RAW_DIR = ROOT / "ingest" / "raw"

FILES = [
    "ice_ttf_dbnomics.parquet",
    "ttf_monthly_panel.parquet",
]

def upload() -> None:
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(BUCKET)
    for name in FILES:
        local = RAW_DIR / name
        blob = bucket.blob(f"raw/{name}")
        blob.upload_from_filename(local)
        print(f"uploaded gs://{BUCKET}/raw/{name}")

if __name__ == "__main__":
    upload()