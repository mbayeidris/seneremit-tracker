select
    operateur,
    type_operation,
    frais_fixe_xof,
    frais_pourcentage,
    plafond_xof,
    source,
    date_verification
from {{ source('raw', 'raw_fintech_tariffs') }}