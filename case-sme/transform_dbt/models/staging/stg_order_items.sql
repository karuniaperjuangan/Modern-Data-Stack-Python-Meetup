WITH source AS (
    SELECT * FROM {{ source('raw', 'order_items') }}
),
products AS (
    SELECT * FROM {{ source('raw', 'products') }}
),
joined AS (
    SELECT
        s.item_id,
        s.order_id,
        s.product_id,
        p.product_name,
        p.category,
        s.quantity,
        s.unit_price,
        s.subtotal,
        p.cost AS unit_cost,
        (s.quantity * p.cost) AS total_cost,
        (s.subtotal - (s.quantity * p.cost)) AS gross_profit
    FROM source s
    LEFT JOIN products p ON s.product_id = p.product_id
)
SELECT * FROM joined
