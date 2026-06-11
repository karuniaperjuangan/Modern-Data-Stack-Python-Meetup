-- =========================================================
-- Simulated SAP S/4HANA Tables
-- =========================================================

CREATE SCHEMA IF NOT EXISTS sap;

-- Customer Master (SAP: KNA1)
CREATE TABLE sap.customers (
    customer_id VARCHAR(20) PRIMARY KEY,    -- SAP: KUNNR
    customer_name VARCHAR(200) NOT NULL,     -- SAP: NAME1
    customer_type VARCHAR(20) NOT NULL,      -- distributor, retailer, modern_trade
    city VARCHAR(100),
    province VARCHAR(100),
    region VARCHAR(50),                      -- Sumatera, Jawa, Kalimantan, etc.
    channel VARCHAR(20),                     -- GT, MT, Ecommerce
    credit_limit DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_date DATE DEFAULT CURRENT_DATE
);

-- Distributor Master
CREATE TABLE sap.distributors (
    distributor_id VARCHAR(20) PRIMARY KEY,
    distributor_name VARCHAR(200) NOT NULL,
    region VARCHAR(50),
    province VARCHAR(100),
    city VARCHAR(100),
    credit_limit DECIMAL(15,2) DEFAULT 0,
    contract_start DATE,
    contract_end DATE,
    is_active BOOLEAN DEFAULT true
);

-- Material Master (SAP: MARA + MAKT)
CREATE TABLE sap.materials (
    material_id VARCHAR(20) PRIMARY KEY,     -- SAP: MATNR
    material_name VARCHAR(200) NOT NULL,      -- SAP: MAKTX
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,            -- skincare, makeup, bodycare, haircare, mensgrooming
    subcategory VARCHAR(100),
    unit_price DECIMAL(12,2) NOT NULL,
    cost_price DECIMAL(12,2) NOT NULL,
    uom VARCHAR(10) DEFAULT 'pcs',           -- SAP: MEINS
    weight_gram DECIMAL(8,2),
    is_active BOOLEAN DEFAULT true,
    launch_date DATE
);

-- Sales Order Header (SAP: VBAK)
CREATE TABLE sap.sales_orders (
    order_id VARCHAR(20) PRIMARY KEY,        -- SAP: VBELN
    customer_id VARCHAR(20) REFERENCES sap.customers(customer_id),
    distributor_id VARCHAR(20) REFERENCES sap.distributors(distributor_id),
    order_date DATE NOT NULL,                -- SAP: AUDAT
    sales_org VARCHAR(10) NOT NULL,          -- SAP: VKORG (1000, 2000, 3000)
    distribution_channel VARCHAR(10),        -- SAP: VTWEG (10=GT, 20=MT, 30=Ecom)
    net_value DECIMAL(15,2) NOT NULL,        -- SAP: NETWR
    currency VARCHAR(5) DEFAULT 'IDR',       -- SAP: WAERK
    status VARCHAR(20) DEFAULT 'created',    -- created, confirmed, delivered, invoiced
    plant VARCHAR(10)                        -- SAP: WERKS (TNG, SMG, SBY)
);

-- Sales Order Items (SAP: VBAP)
CREATE TABLE sap.sales_items (
    item_id VARCHAR(30) PRIMARY KEY,         -- SAP: VBELN + POSNR
    order_id VARCHAR(20) REFERENCES sap.sales_orders(order_id),
    material_id VARCHAR(20) REFERENCES sap.materials(material_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    net_value DECIMAL(15,2) NOT NULL,
    discount_pct DECIMAL(5,2) DEFAULT 0,
    plant VARCHAR(10)                        -- SAP: WERKS
);

-- Inventory Movements (SAP: MSEG)
CREATE TABLE sap.inventory_movements (
    movement_id VARCHAR(20) PRIMARY KEY,     -- SAP: MBLNR + ZEILE
    material_id VARCHAR(20) REFERENCES sap.materials(material_id),
    plant VARCHAR(10) NOT NULL,              -- TNG, SMG, SBY
    movement_type VARCHAR(5) NOT NULL,       -- 101, 201, 301, 601
    quantity DECIMAL(12,2) NOT NULL,
    posting_date DATE NOT NULL,              -- SAP: BUDAT
    batch VARCHAR(20),
    storage_location VARCHAR(10)
);

-- E-commerce Orders (from marketplace APIs)
CREATE TABLE sap.ecommerce_orders (
    ecom_order_id VARCHAR(30) PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,           -- shopee, tokopedia, tiktokshop, lazada
    order_date DATE NOT NULL,
    product_sku VARCHAR(20) REFERENCES sap.materials(material_id),
    quantity INTEGER NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    platform_fee DECIMAL(12,2) DEFAULT 0,
    shipping_cost DECIMAL(12,2) DEFAULT 0,
    shipping_city VARCHAR(100),
    shipping_province VARCHAR(100),
    status VARCHAR(20) DEFAULT 'paid'        -- paid, shipped, delivered, returned
);

-- GL Postings (SAP: BSEG)
CREATE TABLE sap.gl_postings (
    posting_id VARCHAR(30) PRIMARY KEY,
    document_number VARCHAR(20),             -- SAP: BELNR
    posting_date DATE NOT NULL,              -- SAP: BUDAT
    gl_account VARCHAR(10) NOT NULL,         -- SAP: HKONT
    gl_account_name VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(5) DEFAULT 'IDR',
    cost_center VARCHAR(20),                 -- SAP: KOSTL
    profit_center VARCHAR(20),               -- SAP: PRCTR
    posting_type VARCHAR(10) NOT NULL        -- debit, credit
);

-- Create indexes
CREATE INDEX idx_sales_orders_date ON sap.sales_orders(order_date);
CREATE INDEX idx_sales_orders_customer ON sap.sales_orders(customer_id);
CREATE INDEX idx_sales_orders_distributor ON sap.sales_orders(distributor_id);
CREATE INDEX idx_sales_items_order ON sap.sales_items(order_id);
CREATE INDEX idx_sales_items_material ON sap.sales_items(material_id);
CREATE INDEX idx_inv_movements_material ON sap.inventory_movements(material_id);
CREATE INDEX idx_inv_movements_date ON sap.inventory_movements(posting_date);
CREATE INDEX idx_ecom_orders_date ON sap.ecommerce_orders(order_date);
CREATE INDEX idx_ecom_orders_platform ON sap.ecommerce_orders(platform);
CREATE INDEX idx_gl_postings_date ON sap.gl_postings(posting_date);
CREATE INDEX idx_gl_postings_account ON sap.gl_postings(gl_account);
