WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
branches AS (
    SELECT * FROM {{ source('raw', 'branches') }}
),
aggregated AS (
    SELECT
        o.order_date_day,
        o.branch_id,
        b.branch_name,
        SUM(o.total_amount) AS daily_revenue,
        COUNT(o.order_id) AS daily_orders,
        SUM(o.customer_count) AS daily_customers
    FROM orders o
    LEFT JOIN branches b ON o.branch_id = b.branch_id
    GROUP BY 1, 2, 3
)
SELECT * FROM aggregated
