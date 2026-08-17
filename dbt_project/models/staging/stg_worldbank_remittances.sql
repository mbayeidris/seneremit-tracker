select
    "period",
    source_name,
    destination_name,
    firm,
    firm_type,
    "payment instrument",
    "cc1 denomination amount",
    "cc1 total cost %",
    "cc1 lcu fee",
    "cc2 denomination amount",
    "cc2 total cost %",
    "cc2 lcu fee",
    "date",
    corridor
from {{ source('raw', 'raw_worldbank_remittances') }}