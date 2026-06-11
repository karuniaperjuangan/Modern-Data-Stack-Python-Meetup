WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/inventory_movements')
)
SELECT
    movement_id,
    material_id,
    plant,
    movement_type,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(posting_date AS DATE) AS posting_date,
    batch,
    storage_location
FROM source
