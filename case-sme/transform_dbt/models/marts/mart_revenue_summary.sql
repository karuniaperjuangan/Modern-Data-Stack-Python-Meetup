WITH daily AS (
    SELECT * FROM {{ ref('int_daily_sales') }}
),
monthly AS (
    SELECT
        DATE_TRUNC('month', order_date_day) AS month,
        branch_name,
        SUM(daily_revenue) AS monthly_revenue,
        SUM(daily_orders) AS monthly_orders,
        SUM(daily_customers) AS monthly_customers,
        ROUND(SUM(daily_revenue) / NULLIF(SUM(daily_orders), 0), 0) AS avg_ticket_size
    FROM daily
    GROUP BY 1, 2
),
growth AS (
    SELECT
        *,
        LAG(monthly_revenue) OVER (PARTITION BY branch_name ORDER BY month) AS prev_month_revenue,
        SUM(monthly_revenue) OVER (PARTITION BY branch_name ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_revenue
    FROM monthly
)
SELECT
    month,
    branch_name,
    monthly_revenue,
    monthly_orders,
    monthly_customers,
    avg_ticket_size,
    running_total_revenue,
    ROUND(((monthly_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0)) * 100, 2) AS mom_growth_pct
FROM growth
ORDER BY month DESC, branch_name
