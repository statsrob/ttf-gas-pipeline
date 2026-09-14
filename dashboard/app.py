import pandas as pd
import streamlit as st
from google.cloud import bigquery

PROJECT = "ttf-gas-pipeline"
FRONT_SQL = """
select trade_date, front_month, front_settle_eur_mwh
from `ttf-gas-pipeline.ttf_gas_dbt.fct_ttf_daily_front`
order by trade_date
"""
STRIP_SQL = """
select trade_date, delivery_month, settle_eur_mwh
from `ttf-gas-pipeline.ttf_gas_dbt.fct_ttf_latest_strip`
order by delivery_month
"""

@st.cache_data(ttl=3600)
def load(sql: str) -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT)
    return client.query(sql).to_dataframe()

st.set_page_config(page_title="TTF Gas Pipeline", layout="wide")
st.title("Dutch TTF gas futures")
st.caption("ICE data via DBnomics. Prices in EUR/MWh.")

front = load(FRONT_SQL)
strip = load(STRIP_SQL)

c1, c2 = st.columns(2)
c1.metric("Latest front month", f"{front['front_settle_eur_mwh'].iloc[-1]:.2f}")
c2.metric("As-of date", str(pd.to_datetime(front["trade_date"].max()).date()))

st.subheader("Front-month price over time")
st.line_chart(front.set_index("trade_date")["front_settle_eur_mwh"])

st.subheader("Latest forward curve")
st.bar_chart(strip.set_index("delivery_month")["settle_eur_mwh"])