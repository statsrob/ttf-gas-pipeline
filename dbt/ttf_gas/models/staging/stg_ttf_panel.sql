select
    trade_date,
    delivery_month,
    settle_eur_mwh
from {{ source('raw', 'stg_ttf_panel') }}
where settle_eur_mwh is not null