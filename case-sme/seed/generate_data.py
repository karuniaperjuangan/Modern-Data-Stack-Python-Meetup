import os
import random
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from faker import Faker

def main():
    print("Starting data generation for SME case...")
    random.seed(42)
    fake = Faker('id_ID')

    # Read DB connection from env
    db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Disable constraints & Clean up existing data for idempotency
    print("Cleaning up old tables...")
    cur.execute("""
        TRUNCATE raw.inventory, raw.order_items, raw.orders, 
                 raw.ingredients, raw.suppliers, raw.products, 
                 raw.branches CASCADE;
    """)

    # 1. Branches (3 records)
    print("Generating branches...")
    branches = [
        ("Rungkut", "Jl. Rungkut Asri No. 15, Surabaya", "Surabaya", "031-8712345", datetime.strptime("2010-03-15", "%Y-%m-%d").date()),
        ("Wiyung", "Jl. Wiyung Indah No. 8, Surabaya", "Surabaya", "031-7523456", datetime.strptime("2018-07-20", "%Y-%m-%d").date()),
        ("Kenjeran", "Jl. Kenjeran No. 120, Surabaya", "Surabaya", "031-3814567", datetime.strptime("2021-01-10", "%Y-%m-%d").date()),
    ]
    cur.executemany("""
        INSERT INTO raw.branches (branch_name, address, city, phone, opened_date)
        VALUES (%s, %s, %s, %s, %s);
    """, branches)

    # 2. Products (16 records)
    print("Generating products...")
    products = [
        ("Bebek Goreng Kremes", "makanan_utama", 35000.00, 15000.00, True),
        ("Bebek Goreng Sambal Ijo", "makanan_utama", 37000.00, 16000.00, True),
        ("Bebek Bakar", "makanan_utama", 40000.00, 18000.00, True),
        ("Bebek Goreng Crispy", "makanan_utama", 38000.00, 17000.00, True),
        ("Ayam Goreng Kremes", "makanan_utama", 25000.00, 10000.00, True),
        ("Ayam Bakar", "makanan_utama", 28000.00, 12000.00, True),
        ("Nasi Putih", "tambahan", 5000.00, 1500.00, True),
        ("Lalapan Komplit", "tambahan", 5000.00, 1500.00, True),
        ("Tahu/Tempe Goreng", "tambahan", 5000.00, 2000.00, True),
        ("Sambal Korek (Ekstra)", "sambal", 3000.00, 800.00, True),
        ("Sambal Matah", "sambal", 4000.00, 1200.00, True),
        ("Sambal Bawang", "sambal", 3000.00, 800.00, True),
        ("Es Teh Manis", "minuman", 5000.00, 1000.00, True),
        ("Es Jeruk", "minuman", 7000.00, 2000.00, True),
        ("Teh Hangat", "minuman", 4000.00, 800.00, True),
        ("Jus Alpukat", "minuman", 12000.00, 4500.00, True)
    ]
    cur.executemany("""
        INSERT INTO raw.products (product_name, category, price, cost, is_active)
        VALUES (%s, %s, %s, %s, %s);
    """, products)

    # 3. Suppliers (8 records)
    print("Generating suppliers...")
    suppliers = [
        ("Kemitraan Ayam Bebek Jawa Timur", "081234567890", "Krian, Sidoarjo", "Ayam & Bebek"),
        ("Tani Makmur Sidoarjo", "081234567891", "Gedangan, Sidoarjo", "Sayur & Sambal"),
        ("Minyak Sawit Jaya", "081234567892", "Rungkut, Surabaya", "Minyak"),
        ("Distributor Beras Cianjur Surabaya", "081234567893", "Kenjeran, Surabaya", "Beras"),
        ("Minuman Sehat Indonesia", "081234567894", "Wiyung, Surabaya", "Minuman"),
        ("Kemasan Cantik SBY", "081234567895", "Gubeng, Surabaya", "Kemasan"),
        ("Koperasi Bumbu Nusantara", "081234567896", "Keputran, Surabaya", "Bumbu"),
        ("Es Kristal Higienis", "081234567897", "Tegalsari, Surabaya", "Es")
    ]
    cur.executemany("""
        INSERT INTO raw.suppliers (supplier_name, phone, address, category)
        VALUES (%s, %s, %s, %s);
    """, suppliers)

    # 4. Ingredients (20 records)
    print("Generating ingredients...")
    ingredients = [
        # (name, unit, supplier_id, unit_cost) - we need to query supplier IDs first
    ]
    cur.execute("SELECT supplier_id, category FROM raw.suppliers;")
    supp_map = {row[1]: row[0] for row in cur.fetchall()}
    
    ingredients_raw = [
        ("Bebek Mentah", "ekor", supp_map["Ayam & Bebek"], 45000.00),
        ("Ayam Mentah", "ekor", supp_map["Ayam & Bebek"], 25000.00),
        ("Beras", "kg", supp_map["Beras"], 13000.00),
        ("Minyak Goreng", "liter", supp_map["Minyak"], 16000.00),
        ("Bawang Merah", "kg", supp_map["Bumbu"], 35000.00),
        ("Bawang Putih", "kg", supp_map["Bumbu"], 30000.00),
        ("Cabai Rawit", "kg", supp_map["Sayur & Sambal"], 50000.00),
        ("Cabai Merah", "kg", supp_map["Sayur & Sambal"], 40000.00),
        ("Tomat", "kg", supp_map["Sayur & Sambal"], 15000.00),
        ("Kencur", "kg", supp_map["Bumbu"], 25000.00),
        ("Laos", "kg", supp_map["Bumbu"], 12000.00),
        ("Kunyit", "kg", supp_map["Bumbu"], 10000.00),
        ("Ketumbar", "kg", supp_map["Bumbu"], 15000.00),
        ("Garam", "kg", supp_map["Bumbu"], 8000.00),
        ("Gula", "kg", supp_map["Bumbu"], 14000.00),
        ("Jeruk Nipis", "kg", supp_map["Sayur & Sambal"], 18000.00),
        ("Timun", "kg", supp_map["Sayur & Sambal"], 8000.00),
        ("Kemangi", "ikat", supp_map["Sayur & Sambal"], 1500.00),
        ("Selada", "kg", supp_map["Sayur & Sambal"], 12000.00),
        ("Es Batu", "bag", supp_map["Es"], 10000.00)
    ]
    cur.executemany("""
        INSERT INTO raw.ingredients (ingredient_name, unit, supplier_id, unit_cost)
        VALUES (%s, %s, %s, %s);
    """, ingredients_raw)

    # Fetch IDs for branches, products and ingredients to generate dependent data
    cur.execute("SELECT branch_id, branch_name FROM raw.branches;")
    branch_ids = {row[1]: row[0] for row in cur.fetchall()}
    
    cur.execute("SELECT product_id, product_name, category, price, cost FROM raw.products;")
    db_products = cur.fetchall() # list of (id, name, cat, price, cost)
    
    cur.execute("SELECT ingredient_id, unit FROM raw.ingredients;")
    db_ingredients = cur.fetchall() # list of (id, unit)

    # 5. Inventory (60 records) - 3 branches * 20 ingredients
    print("Generating inventory...")
    inventories = []
    for branch_name, b_id in branch_ids.items():
        for ing_id, unit in db_ingredients:
            # Rungkut has more stock, Kenjeran has less
            multiplier = 1.2 if branch_name == "Rungkut" else (0.8 if branch_name == "Kenjeran" else 1.0)
            if unit == "kg":
                qty = round(random.uniform(10.0, 150.0) * multiplier, 2)
            elif unit == "ekor":
                qty = round(random.uniform(20.0, 100.0) * multiplier, 2)
            elif unit == "liter":
                qty = round(random.uniform(30.0, 200.0) * multiplier, 2)
            else:
                qty = round(random.uniform(5.0, 30.0) * multiplier, 2)
                
            inventories.append((b_id, ing_id, qty, unit, datetime.now() - timedelta(hours=random.randint(1, 12))))

    cur.executemany("""
        INSERT INTO raw.inventory (branch_id, ingredient_id, quantity, unit, last_updated)
        VALUES (%s, %s, %s, %s, %s);
    """, inventories)

    # 6 & 7. Orders & Order Items (~3,000 orders, ~7,500 items)
    print("Generating orders & order items...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180) # 6 months
    
    current_date = start_date
    order_id_counter = 1
    item_id_counter = 1
    
    orders_batch = []
    items_batch = []

    # Map products by categories for easier combination generation
    cat_products = {}
    for p in db_products:
        p_id, p_name, category, price, cost = p
        if category not in cat_products:
            cat_products[category] = []
        cat_products[category].append(p)

    while current_date <= end_date:
        # Determine number of orders for the day
        is_weekend = current_date.weekday() >= 5
        # Base daily order count: Rungkut (40), Wiyung (35), Kenjeran (25)
        # We will simulate all 3 branches in one loop per day
        
        # Seasonality check: Ramadhan (approx days 90-120 in our 180 day timeline)
        day_index = (current_date - start_date).days
        is_ramadhan = 90 <= day_index <= 120
        
        # Monthly growth trend (+5% per month)
        month_factor = 1.0 + (day_index // 30) * 0.05
        
        for branch_name, b_id in branch_ids.items():
            base_orders = 25 if branch_name == "Rungkut" else (20 if branch_name == "Wiyung" else 15)
            
            # Apply multipliers
            weekend_mult = random.uniform(1.4, 1.6) if is_weekend else 1.0
            ramadhan_mult = random.uniform(1.3, 1.5) if is_ramadhan else 1.0
            
            day_orders_count = int(base_orders * weekend_mult * ramadhan_mult * month_factor)
            
            for _ in range(day_orders_count):
                # Generate order time
                # Peak hours: 11:00-14:00 (40%), 17:00-21:00 (40%), other (20%)
                rand_hour_type = random.random()
                if rand_hour_type < 0.40:
                    hour = random.randint(11, 13)
                elif rand_hour_type < 0.80:
                    hour = random.randint(17, 20)
                else:
                    hour = random.choice([9, 10, 14, 15, 16, 21, 22])
                
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                order_time = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Customer count (1 to 6 people)
                cust_count = random.choices([1, 2, 3, 4, 5, 6], weights=[15, 45, 20, 12, 5, 3])[0]
                
                # Payment method
                pay_type = random.choices(["cash", "qris", "transfer"], weights=[50, 35, 15])[0]
                
                # Select products for this order
                selected_items = []
                # Always order at least one food item per 1-2 people
                food_qty = max(1, cust_count - random.randint(0, 1))
                
                # Pick food items (weighted towards Bebek Goreng Kremes)
                for _ in range(food_qty):
                    main_foods = cat_products["makanan_utama"]
                    # Bebek Goreng Kremes is at index 0, make it ~30% popular
                    weights = [30 if p[1] == "Bebek Goreng Kremes" else 10 for p in main_foods]
                    food_item = random.choices(main_foods, weights=weights)[0]
                    
                    # check if already added, if so increase quantity
                    existing = next((x for x in selected_items if x[0] == food_item[0]), None)
                    if existing:
                        idx = selected_items.index(existing)
                        selected_items[idx] = (food_item[0], food_item[3], existing[2] + 1)
                    else:
                        selected_items.append((food_item[0], food_item[3], 1))
                
                # Drinks (typically match food quantity)
                for _ in range(food_qty):
                    drink_item = random.choice(cat_products["minman"]) if "minman" in cat_products else random.choice(cat_products["minuman"])
                    existing = next((x for x in selected_items if x[0] == drink_item[0]), None)
                    if existing:
                        idx = selected_items.index(existing)
                        selected_items[idx] = (drink_item[0], drink_item[3], existing[2] + 1)
                    else:
                        selected_items.append((drink_item[0], drink_item[3], 1))
                        
                # Add extras (sambal, tahu, tempe, lalapan) with some probability
                if random.random() < 0.6:
                    for _ in range(random.randint(1, 2)):
                        extra_cat = random.choice(["sambal", "tambahan"])
                        extra_item = random.choice(cat_products[extra_cat])
                        existing = next((x for x in selected_items if x[0] == extra_item[0]), None)
                        if existing:
                            idx = selected_items.index(existing)
                            selected_items[idx] = (extra_item[0], extra_item[3], existing[2] + 1)
                        else:
                            selected_items.append((extra_item[0], extra_item[3], 1))
                
                # Calculate totals
                total_amount = 0
                order_items_to_insert = []
                
                for p_id, price, qty in selected_items:
                    subtotal = price * qty
                    total_amount += subtotal
                    order_items_to_insert.append((item_id_counter, order_id_counter, p_id, qty, price, subtotal))
                    item_id_counter += 1
                
                orders_batch.append((order_id_counter, b_id, order_time, cust_count, pay_type, total_amount))
                items_batch.extend(order_items_to_insert)
                
                order_id_counter += 1
        
        current_date += timedelta(days=1)

    print(f"Inserting {len(orders_batch)} orders and {len(items_batch)} order items...")
    
    # Bulk insert orders
    execute_values(cur, """
        INSERT INTO raw.orders (order_id, branch_id, order_date, customer_count, payment_type, total_amount)
        VALUES %s;
    """, orders_batch)
    
    # Bulk insert order items
    execute_values(cur, """
        INSERT INTO raw.order_items (item_id, order_id, product_id, quantity, unit_price, subtotal)
        VALUES %s;
    """, items_batch)

    conn.commit()
    
    # Verify counts
    cur.execute("SELECT count(*) FROM raw.branches;")
    print(f"Branches: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.products;")
    print(f"Products: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.suppliers;")
    print(f"Suppliers: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.ingredients;")
    print(f"Ingredients: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.inventory;")
    print(f"Inventory status rows: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.orders;")
    print(f"Orders: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM raw.order_items;")
    print(f"Order Items: {cur.fetchone()[0]}")

    cur.close()
    conn.close()
    print("✅ SME data seeding successfully completed!")

if __name__ == "__main__":
    main()
