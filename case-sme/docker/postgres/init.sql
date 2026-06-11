-- Enable pg_duckdb extension
CREATE EXTENSION IF NOT EXISTS pg_duckdb;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;

-- === RAW TABLES ===

-- Branches
CREATE TABLE raw.branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50) DEFAULT 'Surabaya',
    phone VARCHAR(20),
    opened_date DATE
);

-- Products (Menu)
CREATE TABLE raw.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- makanan_utama, sambal, minuman, tambahan
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true
);

-- Orders
CREATE TABLE raw.orders (
    order_id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES raw.branches(branch_id),
    order_date TIMESTAMP NOT NULL,
    customer_count INTEGER DEFAULT 1,
    payment_type VARCHAR(20) NOT NULL, -- cash, qris, transfer
    total_amount DECIMAL(12,2) NOT NULL
);

-- Order Items
CREATE TABLE raw.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Suppliers
CREATE TABLE raw.suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    category VARCHAR(50)
);

-- Ingredients
CREATE TABLE raw.ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- kg, liter, pcs, ikat
    supplier_id INTEGER REFERENCES raw.suppliers(supplier_id),
    unit_cost DECIMAL(10,2)
);

-- Inventory
CREATE TABLE raw.inventory (
    inventory_id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES raw.branches(branch_id),
    ingredient_id INTEGER REFERENCES raw.ingredients(ingredient_id),
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_orders_branch_id ON raw.orders(branch_id);
CREATE INDEX idx_orders_date ON raw.orders(order_date);
CREATE INDEX idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX idx_order_items_product_id ON raw.order_items(product_id);
CREATE INDEX idx_inventory_branch ON raw.inventory(branch_id);
CREATE INDEX idx_inventory_ingredient ON raw.inventory(ingredient_id);
