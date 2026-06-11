WITH movements AS (
    SELECT * FROM {{ ref('stg_inventory_movements') }}
),
mats AS (
    SELECT * FROM {{ ref('stg_materials') }}
),
-- Calculate current stock levels by plant and material based on movement inputs (101) minus issues (601/201/301)
stock_balance AS (
    SELECT
        material_id,
        plant,
        SUM(
            CASE 
                WHEN movement_type = '101' THEN quantity
                ELSE -quantity
            END
        ) AS current_quantity
    FROM movements
    GROUP BY 1, 2
),
aging_base AS (
    SELECT
        s.material_id,
        s.plant,
        s.current_quantity,
        m.material_name,
        m.brand,
        m.category,
        m.cost_price,
        (s.current_quantity * m.cost_price) AS inventory_value,
        -- Find the last production date (101) to compute stock age
        (
            SELECT MAX(posting_date)
            FROM movements m2
            WHERE m2.material_id = s.material_id 
              AND m2.plant = s.plant 
              AND m2.movement_type = '101'
        ) AS last_receipt_date
    FROM stock_balance s
    LEFT JOIN mats m ON s.material_id = m.material_id
    WHERE s.current_quantity > 0
),
aged AS (
    SELECT
        *,
        COALESCE(DATEDIFF('day', last_receipt_date, CAST('2025-06-11' AS DATE)), 15) AS stock_age_days
    FROM aging_base
)
SELECT
    *,
    CASE
        WHEN stock_age_days <= 30 THEN '0-30 days'
        WHEN stock_age_days <= 60 THEN '31-60 days'
        WHEN stock_age_days <= 90 THEN '61-90 days'
        ELSE '90+ days'
    END AS age_bucket
FROM aged
