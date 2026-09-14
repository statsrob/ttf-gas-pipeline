-- latest available forward curve
with latest as (
    select max(trade_date) as trade_date
    from {{ ref('stg_ttf_panel') }}
)
select
    p.trade_date,
    p.delivery_month,
    p.settle_eur_mwh
from {{ ref('stg_ttf_panel') }} p
join latest l on p.trade_date = l.trade_date