WITH perf AS (
    SELECT * FROM {{ ref('int_product_performance') }}
),
totals AS (
    SELECT SUM(total_revenue) AS grand_total_revenue FROM perf
),
calculated AS (
    SELECT
        p.*,
        ROUND((p.total_revenue / t.grand_total_revenue) * 100, 2) AS revenue_share_pct
    FROM perf p, totals t
),
pareto AS (
    SELECT
        *,
        SUM(revenue_share_pct) OVER (ORDER BY total_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue_share_pct
    FROM calculated
)
SELECT * FROM pareto
ORDER BY total_revenue DESC
