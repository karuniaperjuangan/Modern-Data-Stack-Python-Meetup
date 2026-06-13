{{ config(materialized='external', location='s3://lakehouse/warehouse/marts/mart_distribution_network/mart_distribution_network.parquet') }}

WITH dist_perf AS (
    SELECT * FROM {{ ref('int_distributor_performance') }}
)
SELECT
    distributor_id,
    distributor_name,
    region,
    credit_limit,
    total_revenue,
    order_count,
    customer_coverage,
    credit_utilization_pct,
    sales_rank_in_region
FROM dist_perf
ORDER BY region, sales_rank_in_region
