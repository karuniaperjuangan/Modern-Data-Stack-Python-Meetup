WITH channel_sales AS (
    SELECT * FROM {{ ref('int_channel_sales') }}
),
monthly_agg AS (
    SELECT
        sales_month,
        SUM(monthly_revenue) AS total_revenue,
        SUM(order_count) AS total_orders,
        -- Get E-commerce portion specifically
        SUM(CASE WHEN channel = 'Ecommerce' THEN monthly_revenue ELSE 0 END) AS ecommerce_revenue
    FROM channel_sales
    GROUP BY 1
),
prev_kpi AS (
    SELECT
        *,
        LAG(total_revenue) OVER (ORDER BY sales_month) AS prev_month_revenue,
        LAG(total_revenue, 12) OVER (ORDER BY sales_month) AS yoy_prev_revenue
    FROM monthly_agg
)
SELECT
    sales_month,
    total_revenue,
    total_orders,
    ecommerce_revenue,
    ROUND((ecommerce_revenue / NULLIF(total_revenue, 0)) * 100, 2) AS ecommerce_share_pct,
    ROUND(((total_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0)) * 100, 2) AS mom_growth_pct,
    ROUND(((total_revenue - yoy_prev_revenue) / NULLIF(yoy_prev_revenue, 0)) * 100, 2) AS yoy_growth_pct
FROM prev_kpi
ORDER BY sales_month DESC
