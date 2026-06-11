WITH source AS (
    SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/sap/ecommerce_orders')
)
SELECT
    ecom_order_id,
    platform,
    CAST(order_date AS DATE) AS order_date,
    product_sku,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(revenue AS DOUBLE) AS revenue,
    CAST(platform_fee AS DOUBLE) AS platform_fee,
    CAST(shipping_cost AS DOUBLE) AS shipping_cost,
    shipping_city,
    shipping_province,
    status
FROM source
