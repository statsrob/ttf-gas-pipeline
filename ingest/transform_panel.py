import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "ingest" / "raw" / "ice_ttf_dbnomics.parquet"
OUT_DIR = ROOT / "ingest" / "raw"
OUT_PATH = OUT_DIR / "ttf_monthly_panel.parquet"

MON = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
PAT = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d{2})$")

def to_panel(raw: pd.DataFrame) -> pd.DataFrame:
    s = raw.copy()
    s["period"] = pd.to_datetime(s["period"])
    label = s["series_name"].str.replace(r"^Daily\s+[–-]\s+", "", regex=True).str.strip()
    m = label.str.extract(PAT)
    s["month_num"] = m[0].map(MON)
    s["year"] = pd.to_numeric(m[1], errors="coerce") + 2000
    s = s.dropna(subset=["month_num", "year", "value"])
    s["delivery_month"] = pd.to_datetime(
        {"year": s["year"].astype(int), "month": s["month_num"].astype(int), "day": 1}
    )
    panel = (
        s.rename(columns={"period": "trade_date", "value": "settle_eur_mwh"})
        [["trade_date", "delivery_month", "settle_eur_mwh"]]
        .drop_duplicates(["trade_date", "delivery_month"])
        .sort_values(["trade_date", "delivery_month"])
        .reset_index(drop=True)
    )
    return panel

if __name__ == "__main__":
    raw = pd.read_parquet(RAW_PATH)
    panel = to_panel(raw)
    panel.to_parquet(OUT_PATH, index=False)
    print(panel.head())
    print("n_dates", panel["trade_date"].nunique())
    print("n_months", panel["delivery_month"].nunique())
    print("rows", len(panel))
    print("saved", OUT_PATH)
    
    
