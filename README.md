# TTF Gas Pipeline

End-to-end batch data pipeline for Dutch TTF natural gas futures.

Built for the DataTalksClub Data Engineering Zoomcamp project: ingest, data lake, warehouse, transforms, orchestration, and dashboard.

## Problem

TTF (Title Transfer Facility) is the main European natural gas price benchmark. Energy analysts need a repeatable way to:

- see how the front-month TTF price has moved over time
- see the current forward curve (price by delivery month)

Doing this from a notebook does not scale. This project turns the exploration notebook into a daily pipeline.

## What the project does

1. Extracts ICE Dutch TTF gas futures from DBnomics (free, no API key).
2. Saves raw parquet to a GCS data lake.
3. Loads a cleaned panel into BigQuery.
4. Transforms the panel with dbt into dashboard tables.
5. Shows two Streamlit charts.
6. Repeats the load every day with Kestra.

## Architecture

```text
DBnomics ICE DUTCH_TTF_GAS_FUTURES
        |
        v
Python extract + transform
        |
        v
GCS data lake (raw parquet)
        |
        v
BigQuery  ttf_gas.stg_ttf_panel
  partition: trade_date
  cluster:   delivery_month
        |
        v
dbt marts
  fct_ttf_daily_front
  fct_ttf_latest_strip
        |
        v
Streamlit dashboard
```

Orchestration: Kestra DAG, daily at 06:00 UTC.  
Infrastructure: GCP + Terraform.

## Why the warehouse is designed this way

Table: `ttf-gas-pipeline.ttf_gas.stg_ttf_panel`

| Setting | Field | Reason |
|---|---|---|
| Partition (DAY) | `trade_date` | Dashboard and dbt queries filter by date. Partitioning avoids full table scans. |
| Cluster | `delivery_month` | Curve queries filter/sort by contract month. Clustering keeps those rows close. |

## Stack

| Layer | Tool |
|---|---|
| Cloud | GCP |
| IaC | Terraform |
| Lake | GCS bucket `ttf-gas-pipeline-lake` |
| Warehouse | BigQuery dataset `ttf_gas` |
| Orchestration | Kestra on Docker Compose |
| Transforms | dbt-bigquery |
| Dashboard | Streamlit |
| Source | DBnomics `ICE` / `DUTCH_TTF_GAS_FUTURES` |

All tools can be used on a GCP free-tier project.

## Repo layout

```text
ttf-gas-pipeline/
  terraform/                 # GCS bucket + BigQuery dataset
  ingest/
    extract_ttf.py           # DBnomics extract
    transform_panel.py       # monthly panel
    load_gcs.py              # upload to lake
    load_bq.py               # load warehouse
    raw/                     # local parquet (gitignored)
  kestra/flows/ttf_gas_daily.yml
  dbt/ttf_gas/               # staging + marts
  dashboard/app.py
  notebooks/explore.ipynb
  docker-compose.yml
  requirements.txt
```

## Prerequisites

- macOS, VS Code, Python 3.13
- Docker Desktop
- Terraform
- Google Cloud SDK (`gcloud`)
- GCP project `ttf-gas-pipeline` with billing enabled

## How to run

### 1. Clone and Python env

```bash
git clone https://github.com/statsrob/ttf-gas-pipeline.git
cd ttf-gas-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. GCP auth

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project ttf-gas-pipeline
```

### 3. Infrastructure

```bash
cd terraform
terraform init
terraform apply
cd ..
```

This creates:

- GCS bucket `ttf-gas-pipeline-lake`
- BigQuery dataset `ttf_gas`

If the bucket name is taken, change `bucket_name` in `terraform/terraform.tfvars`.

### 4. dbt profile

Create `~/.dbt/profiles.yml`:

```yaml
ttf_gas:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: ttf-gas-pipeline
      dataset: ttf_gas_dbt
      location: EU
      threads: 2
```

A copy is in `dbt/ttf_gas/profiles.yml.example`.

### 5. Run the pipeline once

```bash
python ingest/extract_ttf.py
python ingest/transform_panel.py
python ingest/load_gcs.py
python ingest/load_bq.py
cd dbt/ttf_gas
dbt debug
dbt run
cd ../..
```

Expected panel size is about 150k rows (one row per trade date × monthly contract).

### 6. Dashboard

```bash
streamlit run dashboard/app.py
```

Open the local URL (usually http://localhost:8501).

Tiles:

1. Front-month TTF price over time (line chart).
2. Latest forward curve by delivery month (bar chart).

### 7. Daily orchestration (Kestra)

```bash
docker compose up -d
```

Open http://localhost:8080

- Complete the local admin setup the first time.
- Open flow `ttf` / `ttf_gas_daily`.
- Click Execute.

Tasks in the DAG:

1. `extract` — DBnomics to parquet
2. `transform` — monthly panel
3. `load_gcs` — upload lake
4. `load_bq` — load warehouse
5. `dbt_run` — rebuild marts

Schedule: `0 6 * * *` (06:00 UTC).

Docker Desktop and `docker compose up -d` must be running for the schedule to fire.

Kestra 2.x blocks Docker bind mounts unless enabled. This repo sets `volume-enabled: true` in `docker-compose.yml`.

## Data notes

- Provider: ICE via DBnomics
- Dataset: `DUTCH_TTF_GAS_FUTURES`
- Kept contracts: monthly labels such as `Dec22`, `Jan23`
- Seasonal contracts (`Summer`, `Winter`, `Cal`) are dropped
- Unit: EUR/MWh
- Grain: `trade_date` × `delivery_month`

## Reproducibility notes

- Do not commit `.env`, credentials, parquet files, or Terraform state.
- Use `.env.example` and `dbt/ttf_gas/profiles.yml.example`.
- Project id and bucket name are in `terraform/terraform.tfvars`.
- Kestra mounts the repo via `HOST_PROJECT_DIR=${PWD}` from docker compose.

## Rubric mapping

| Criterion | How this repo meets it |
|---|---|
| Problem description | This README |
| Cloud + IaC | GCP + Terraform |
| Batch ingestion | Kestra DAG, lake upload |
| Data warehouse | BigQuery partition + cluster |
| Transforms | dbt staging + marts |
| Dashboard | Streamlit, 2 tiles |
| Reproducibility | This README + scripts |
