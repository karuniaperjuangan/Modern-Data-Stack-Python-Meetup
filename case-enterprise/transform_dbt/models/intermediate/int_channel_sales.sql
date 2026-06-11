WITH sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS sales_month,
        distribution_channel AS channel,
        SUM(net_value) AS monthly_revenue,
        COUNT(order_id) AS order_count
    FROM {{ ref('stg_sales_orders') }}
    GROUP BY 1, 2
),
ecom AS (
    SELECT
        DATE_TRUNC('month', order_date) AS sales_month,
        'Ecommerce' AS channel,
        SUM(revenue) AS monthly_revenue,
        COUNT(ecom_order_id) AS order_count
    FROM {{ ref('stg_ecommerce_orders') }}
    WHERE status != 'returned'
    GROUP BY 1, 2
),
union_sales AS (
    SELECT * FROM sales
    UNION ALL
    SELECT * FROM ecom
),
monthly_totals AS (
    SELECT 
        sales_month,
        SUM(monthly_revenue) AS total_revenue
    FROM union_sales
    GROUP BY 1
),
share_growth AS (
    SELECT
        u.sales_month,
        u.channel,
        u.monthly_revenue,
        u.order_count,
        ROUND((u.monthly_revenue / NULLIF(t.total_revenue, 0)) * 100, 2) AS channel_share_pct,
        LAG(u.monthly_revenue, 12) OVER (PARTITION BY u.channel ORDER BY u.sales_month) AS prev_year_revenue
    FROM union_sales u
    LEFT JOIN monthly_totals t ON u.sales_month = t.sales_month
)
SELECT
    sales_month,
    channel,
    monthly_revenue,
    order_count,
    channel_share_pct,
    ROUND(((monthly_revenue - prev_year_revenue) / NULLIF(prev_year_revenue, 0)) * 100, 2) AS yoy_growth_pct
FROM share_growth
ORDER BY sales_month DESC, channel
