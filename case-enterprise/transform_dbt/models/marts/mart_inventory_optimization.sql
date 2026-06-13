{{ config(materialized='external', location='s3://lakehouse/warehouse/marts/mart_inventory_optimization/mart_inventory_optimization.parquet') }}

WITH aging AS (
    SELECT * FROM {{ ref('int_inventory_aging') }}
)
SELECT
    material_id,
    material_name,
    plant,
    current_quantity,
    cost_price,
    inventory_value,
    stock_age_days,
    age_bucket,
    CASE
        WHEN stock_age_days > 90 THEN TRUE
        ELSE FALSE
    END AS dead_stock_flag
FROM aging
ORDER BY inventory_value DESC
