{{ config(materialized='external', location='s3://lakehouse/warehouse/marts/mart_channel_comparison/mart_channel_comparison.parquet') }}

WITH channel_sales AS (
    SELECT * FROM {{ ref('int_channel_sales') }}
)
SELECT
    sales_month,
    channel,
    monthly_revenue,
    order_count,
    channel_share_pct,
    yoy_growth_pct
FROM channel_sales
ORDER BY sales_month DESC, channel
