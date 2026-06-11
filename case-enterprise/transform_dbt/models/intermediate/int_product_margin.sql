WITH items AS (
    SELECT * FROM {{ ref('stg_sales_items') }}
),
mats AS (
    SELECT * FROM {{ ref('stg_materials') }}
),
calculated AS (
    SELECT
        i.material_id,
        m.material_name,
        m.brand,
        m.category,
        SUM(i.quantity) AS total_qty,
        SUM(i.net_value) AS gross_revenue,
        SUM(i.quantity * m.cost_price) AS total_cogs,
        (SUM(i.net_value) - SUM(i.quantity * m.cost_price)) AS gross_profit
    FROM items i
    LEFT JOIN mats m ON i.material_id = m.material_id
    GROUP BY 1, 2, 3, 4
),
ranked AS (
    SELECT
        *,
        ROUND((gross_profit / NULLIF(gross_revenue, 0)) * 100, 2) AS margin_pct,
        DENSE_RANK() OVER (PARTITION BY brand ORDER BY gross_revenue DESC) AS sales_rank_in_brand
    FROM calculated
)
SELECT * FROM ranked
