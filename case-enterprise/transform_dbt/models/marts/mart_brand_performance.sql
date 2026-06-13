{{ config(materialized='external', location='s3://lakehouse/warehouse/marts/mart_brand_performance/mart_brand_performance.parquet') }}

WITH product_perf AS (
    SELECT 
        brand,
        category,
        SUM(gross_revenue) AS total_revenue,
        SUM(total_cogs) AS total_cogs,
        SUM(gross_profit) AS total_profit
    FROM {{ ref('int_product_margin') }}
    GROUP BY 1, 2
)
SELECT
    brand,
    category,
    total_revenue,
    total_cogs,
    total_profit,
    ROUND((total_profit / NULLIF(total_revenue, 0)) * 100, 2) AS gross_margin_pct
FROM product_perf
ORDER BY brand, total_revenue DESC
