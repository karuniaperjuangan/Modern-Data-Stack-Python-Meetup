WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/sales_items')
)
SELECT
    item_id,
    order_id,
    material_id,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(unit_price AS DOUBLE) AS unit_price,
    CAST(net_value AS DOUBLE) AS net_value,
    CAST(discount_pct AS DOUBLE) AS discount_pct,
    plant
FROM source
