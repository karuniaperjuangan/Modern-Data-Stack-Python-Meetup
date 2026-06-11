WITH source AS (
    SELECT * FROM {{ source('raw', 'inventory') }}
),
ingredients AS (
    SELECT * FROM {{ source('raw', 'ingredients') }}
),
joined AS (
    SELECT
        s.inventory_id,
        s.branch_id,
        s.ingredient_id,
        i.ingredient_name,
        i.unit_cost,
        s.quantity,
        s.unit,
        s.last_updated,
        (s.quantity * i.unit_cost) AS stock_value,
        EXTRACT(EPOCH FROM (NOW() - s.last_updated)) / 86400.0 AS days_since_update
    FROM source s
    LEFT JOIN ingredients i ON s.ingredient_id = i.ingredient_id
)
SELECT * FROM joined
