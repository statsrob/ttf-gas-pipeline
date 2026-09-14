-- front-month contract per trade date (time series)
with ranked as (
    select
        trade_date,
        delivery_month,
        settle_eur_mwh,
        row_number() over (
            partition by trade_date
            order by delivery_month
        ) as rn
    from {{ ref('stg_ttf_panel') }}
    where delivery_month >= date_trunc(trade_date, month)
)
select
    trade_date,
    delivery_month as front_month,
    settle_eur_mwh as front_settle_eur_mwh
from ranked
where rn = 1