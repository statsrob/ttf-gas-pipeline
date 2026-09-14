from pathlib import Path
from dbnomics import fetch_series
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "ingest" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = RAW_DIR / "ice_ttf_dbnomics.parquet"

def extract() -> pd.DataFrame:
    print("Fetching ICE DUTCH_TTF_GAS_FUTURES from DBnomics...")
    raw = fetch_series("ICE", "DUTCH_TTF_GAS_FUTURES", max_nb_series=500)
    raw.to_parquet(RAW_PATH, index=False)
    print(f"saved {RAW_PATH} {raw.shape}")
    return raw

if __name__ == "__main__":
    df = extract()
    print(df.head())
    print("series", df["series_code"].nunique())
    print("period", df["period"].min(), "->", df["period"].max())