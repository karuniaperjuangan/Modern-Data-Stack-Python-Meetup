WITH source AS (
    -- Read from Iceberg table directly using duckdb adapter scan helper
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/sales_orders')
),
cleaned AS (
    SELECT
        order_id,
        customer_id,
        distributor_id,
        CAST(order_date AS DATE) AS order_date,
        sales_org,
        CASE
            WHEN distribution_channel = '10' THEN 'GT'
            WHEN distribution_channel = '20' THEN 'MT'
            WHEN distribution_channel = '30' THEN 'Ecommerce'
            ELSE 'Unknown'
        END AS distribution_channel,
        CAST(net_value AS DOUBLE) AS net_value,
        currency,
        status,
        CASE
            WHEN plant = 'TNG' THEN 'Tangerang'
            WHEN plant = 'SMG' THEN 'Semarang'
            WHEN plant = 'SBY' THEN 'Surabaya'
            ELSE plant
        END AS plant_city
    FROM source
    WHERE status != 'cancelled'
)
SELECT * FROM cleaned
