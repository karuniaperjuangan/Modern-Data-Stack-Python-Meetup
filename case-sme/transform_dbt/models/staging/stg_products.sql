WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
)
SELECT
    product_id,
    product_name,
    category,
    price,
    cost,
    is_active
FROM source
