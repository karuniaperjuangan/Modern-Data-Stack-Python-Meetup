WITH items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),
aggregated AS (
    SELECT
        product_id,
        product_name,
        category,
        SUM(quantity) AS total_qty,
        SUM(subtotal) AS total_revenue,
        SUM(total_cost) AS total_cost,
        SUM(gross_profit) AS total_profit,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(AVG(quantity), 2) AS avg_qty_per_order
    FROM items
    GROUP BY 1, 2, 3
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        ROUND((total_profit / NULLIF(total_revenue, 0)) * 100, 2) AS gross_margin_pct
    FROM aggregated
)
SELECT * FROM ranked
