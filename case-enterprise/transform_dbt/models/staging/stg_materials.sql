WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/materials')
),
cleaned AS (
    SELECT
        material_id,
        material_name,
        brand,
        category,
        subcategory,
        CAST(unit_price AS DOUBLE) AS unit_price,
        CAST(cost_price AS DOUBLE) AS cost_price,
        (CAST(unit_price AS DOUBLE) - CAST(cost_price AS DOUBLE)) AS unit_margin,
        ROUND(((CAST(unit_price AS DOUBLE) - CAST(cost_price AS DOUBLE)) / NULLIF(CAST(unit_price AS DOUBLE), 0)) * 100, 2) AS margin_pct,
        CASE
            WHEN CAST(unit_price AS DOUBLE) >= 100000 THEN 'premium'
            WHEN CAST(unit_price AS DOUBLE) >= 40000 THEN 'mid'
            ELSE 'mass'
        END AS segment,
        uom,
        weight_gram,
        is_active,
        CAST(launch_date AS DATE) AS launch_date
    FROM source
)
SELECT * FROM cleaned
