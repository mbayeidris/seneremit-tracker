with taux_eur as (
    select taux
    from {{ ref('stg_exchange_rates') }}
    where devise_origine = 'EUR'
),

international as (
    select
        firm as operateur,
        'international' as type_operateur,
        source_name as corridor_origine,
        period,
        "cc2 total cost %" as cout_total_pourcentage,
        "cc2 denomination amount" * (select taux from taux_eur)
            * ("cc2 total cost %" / 100.0) as cout_total_xof
    from {{ ref('stg_worldbank_remittances') }}
),

local as (
    select
        operateur,
        'local' as type_operateur,
        'Senegal' as corridor_origine,
        null as period,
        (case
            when plafond_xof is null then 50000 * frais_pourcentage
            else least(50000 * frais_pourcentage, plafond_xof)
        end) / 50000.0 * 100 as cout_total_pourcentage,
        case
            when plafond_xof is null then 50000 * frais_pourcentage
            else least(50000 * frais_pourcentage, plafond_xof)
        end as cout_total_xof
    from {{ ref('stg_fintech_tariffs') }}
    where type_operation in ('transfert_argent', 'retrait')
),

tout_combine as (
    select * from international
    union all
    select * from local
)

select * from tout_combine
where cout_total_pourcentage is not null