select
    devise_origine, 
    devise_cible, 
    taux, 
    date_taux
from {{ source('raw', 'raw_exchange_rates') }}