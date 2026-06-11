WITH stock AS (
    SELECT * FROM {{ ref('stg_inventory') }}
),
branches AS (
    SELECT * FROM {{ source('raw', 'branches') }}
),
-- Simple estimation of daily ingredient usage (derived from sales orders of the last 30 days)
usage AS (
    SELECT
        o.branch_id,
        oi.product_id,
        SUM(oi.quantity) / 180.0 AS avg_daily_qty -- historic average over 6 months
    FROM {{ ref('stg_order_items') }} oi
    JOIN {{ ref('stg_orders') }} o ON oi.order_id = o.order_id
    GROUP BY 1, 2
),
-- Map products to ingredients (simulated bill of materials)
bom AS (
    -- For simplicity, let's map main foods to ingredients
    -- Bebek Goreng/Bakar needs Bebek Mentah (0.25 ekor per portion)
    -- Ayam Goreng/Bakar needs Ayam Mentah (0.25 ekor per portion)
    -- Nasi Putih needs Beras (0.1 kg per portion)
    -- Everything needs Oil (0.05 liter per portion) and spices/chili
    SELECT product_id, ingredient_id, qty_required FROM (
        VALUES
            (1, 1, 0.25), -- Bebek Kremes -> Bebek Mentah
            (2, 1, 0.25), -- Bebek Ijo -> Bebek Mentah
            (3, 1, 0.25), -- Bebek Bakar -> Bebek Mentah
            (4, 1, 0.25), -- Bebek Crispy -> Bebek Mentah
            (5, 2, 0.25), -- Ayam Kremes -> Ayam Mentah
            (6, 2, 0.25), -- Ayam Bakar -> Ayam Mentah
            (7, 3, 0.10)  -- Nasi -> Beras
    ) AS t(product_id, ingredient_id, qty_required)
),
daily_ing_usage AS (
    SELECT
        u.branch_id,
        b.ingredient_id,
        SUM(u.avg_daily_qty * b.qty_required) AS daily_usage_rate
    FROM usage u
    JOIN bom b ON u.product_id = b.product_id
    GROUP BY 1, 2
),
forecast AS (
    SELECT
        s.inventory_id,
        br.branch_name,
        s.ingredient_name,
        s.quantity AS current_stock,
        s.unit,
        s.unit_cost,
        s.stock_value,
        COALESCE(u.daily_usage_rate, 1.5) AS est_daily_usage, -- fallback usage rate
        s.days_since_update
    FROM stock s
    LEFT JOIN daily_ing_usage u ON s.branch_id = u.branch_id AND s.ingredient_id = u.ingredient_id
    LEFT JOIN branches br ON s.branch_id = br.branch_id
)
SELECT
    *,
    ROUND(current_stock / NULLIF(est_daily_usage, 0), 1) AS days_of_stock_remaining,
    CASE
        WHEN (current_stock / NULLIF(est_daily_usage, 0)) <= 3.0 THEN TRUE
        ELSE FALSE
    END AS reorder_flag
FROM forecast
