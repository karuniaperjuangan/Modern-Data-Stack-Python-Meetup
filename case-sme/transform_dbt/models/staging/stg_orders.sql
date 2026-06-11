WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),
cleaned AS (
    SELECT
        order_id,
        branch_id,
        order_date,
        DATE(order_date) AS order_date_day,
        EXTRACT(HOUR FROM order_date) AS order_hour,
        EXTRACT(ISODOW FROM order_date) AS day_of_week,
        customer_count,
        payment_type,
        total_amount
    FROM source
    WHERE total_amount > 0
)
SELECT * FROM cleaned
