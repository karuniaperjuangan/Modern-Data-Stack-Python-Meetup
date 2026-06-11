WITH orders AS (
    SELECT * FROM {{ ref('stg_sales_orders') }}
),
dists AS (
    SELECT * FROM {{ ref('stg_distributors') }}
),
aggregated AS (
    SELECT
        o.distributor_id,
        d.distributor_name,
        d.region,
        d.credit_limit,
        SUM(o.net_value) AS total_revenue,
        COUNT(o.order_id) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_coverage
    FROM orders o
    LEFT JOIN dists d ON o.distributor_id = d.distributor_id
    GROUP BY 1, 2, 3, 4
),
ranked AS (
    SELECT
        *,
        ROUND((total_revenue / NULLIF(credit_limit, 0)) * 100, 2) AS credit_utilization_pct,
        DENSE_RANK() OVER (PARTITION BY region ORDER BY total_revenue DESC) AS sales_rank_in_region
    FROM aggregated
)
SELECT * FROM ranked
