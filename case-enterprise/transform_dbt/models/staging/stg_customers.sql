WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/customers')
)
SELECT
    customer_id,
    customer_name,
    customer_type,
    city,
    province,
    region,
    channel,
    CAST(credit_limit AS DOUBLE) AS credit_limit,
    is_active,
    CAST(created_date AS DATE) AS created_date
FROM source
