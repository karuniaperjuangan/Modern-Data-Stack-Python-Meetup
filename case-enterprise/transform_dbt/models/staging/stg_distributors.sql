WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/distributors')
)
SELECT
    distributor_id,
    distributor_name,
    region,
    province,
    city,
    CAST(credit_limit AS DOUBLE) AS credit_limit,
    CAST(contract_start AS DATE) AS contract_start,
    CAST(contract_end AS DATE) AS contract_end,
    is_active
FROM source
