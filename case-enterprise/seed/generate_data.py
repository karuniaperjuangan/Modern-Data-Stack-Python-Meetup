import os
import random
import uuid
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from faker import Faker

def main():
    print("Starting data generation for Enterprise case...")
    random.seed(42)
    fake = Faker('id_ID')

    # Read DB connection from env
    db_url = os.environ.get("ERP_DATABASE_URL", "postgresql://erp_user:erp_password_2024@postgres:5432/erp_db")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Clean up existing data for idempotency
    print("Cleaning up old tables...")
    cur.execute("""
        TRUNCATE sap.gl_postings, sap.ecommerce_orders, sap.inventory_movements, 
                 sap.sales_items, sap.sales_orders, sap.materials, 
                 sap.distributors, sap.customers CASCADE;
    """)

    # 1. Materials (200 records)
    print("Generating materials...")
    BRANDS = {
        "Jelita": {"category": "skincare", "segment": "premium", "sku_count": 25,
                   "subcategories": ["cleanser", "toner", "serum", "moisturizer", "sunscreen", "eye cream", "mask"]},
        "Pesona": {"category": "makeup", "segment": "mass", "sku_count": 30,
                   "subcategories": ["foundation", "powder", "lipstick", "lip cream", "eyeshadow", "mascara", "blush", "eyeliner"]},
        "Cahaya": {"category": "bodycare", "segment": "mid", "sku_count": 20,
                   "subcategories": ["body lotion", "body wash", "hand cream", "body scrub", "deodorant"]},
        "Lestari": {"category": "skincare", "segment": "mass", "sku_count": 20,
                    "subcategories": ["cleanser", "moisturizer", "mask", "toner", "lip balm"]},
        "Dewi": {"category": "haircare", "segment": "mid", "sku_count": 15,
                 "subcategories": ["shampoo", "conditioner", "hair mask", "hair oil", "hair serum"]},
        "Bintang": {"category": "mensgrooming", "segment": "mass", "sku_count": 12,
                    "subcategories": ["face wash", "moisturizer", "deodorant", "hair gel", "aftershave"]},
        "Nusa": {"category": "babycare", "segment": "mid", "sku_count": 10,
                 "subcategories": ["baby lotion", "baby wash", "baby oil", "diaper cream", "baby powder"]}
    }

    materials = []
    brand_codes = {"Jelita": "JLT", "Pesona": "PSN", "Cahaya": "CHY", "Lestari": "LST", "Dewi": "DWI", "Bintang": "BTG", "Nusa": "NUS"}
    
    for brand, info in BRANDS.items():
        b_code = brand_codes[brand]
        for idx in range(1, info["sku_count"] + 1):
            mat_id = f"MAT-{b_code}-{idx:04d}"
            sub = random.choice(info["subcategories"])
            mat_name = f"{brand} {sub.title()} Spec-{idx}"
            
            # Pricing based on segment
            if info["segment"] == "premium":
                price = round(random.uniform(100000.00, 300000.00), -3)
            elif info["segment"] == "mid":
                price = round(random.uniform(40000.00, 100000.00), -3)
            else:
                price = round(random.uniform(15000.00, 45000.00), -3)
                
            cost = round(price * random.uniform(0.35, 0.50), -3)
            launch_date = datetime.now() - timedelta(days=random.randint(180, 720))
            
            materials.append((mat_id, mat_name, brand, info["category"], sub, price, cost, 'pcs', random.uniform(50, 400), True, launch_date.date()))

    cur.executemany("""
        INSERT INTO sap.materials (material_id, material_name, brand, category, subcategory, unit_price, cost_price, uom, weight_gram, is_active, launch_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, materials)

    # 2. Distributors (50 records)
    print("Generating distributors...")
    REGIONS_DISTRIBUTION = {
        "Jawa": 25,
        "Sumatera": 10,
        "Kalimantan": 5,
        "Sulawesi": 5,
        "Bali & Nusa Tenggara": 3,
        "Papua & Maluku": 2
    }
    distributors = []
    dist_id_counter = 1
    region_codes = {"Jawa": "JAW", "Sumatera": "SUM", "Kalimantan": "KAL", "Sulawesi": "SUL", "Bali & Nusa Tenggara": "BAL", "Papua & Maluku": "PAP"}
    
    for region, count in REGIONS_DISTRIBUTION.items():
        r_code = region_codes[region]
        for _ in range(count):
            dist_id = f"DIST-{r_code}-{dist_id_counter:03d}"
            dist_name = f"PT {fake.company()}"
            city = fake.city()
            prov = fake.state()
            credit = round(random.uniform(500000000.00, 5000000000.00), -6)
            start_c = datetime.now() - timedelta(days=random.randint(365, 1500))
            end_c = datetime.now() + timedelta(days=random.randint(365, 1000))
            
            distributors.append((dist_id, dist_name, region, prov, city, credit, start_c.date(), end_c.date(), True))
            dist_id_counter += 1

    cur.executemany("""
        INSERT INTO sap.distributors (distributor_id, distributor_name, region, province, city, credit_limit, contract_start, contract_end, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, distributors)

    # 3. Customers (1,000 records)
    print("Generating customers...")
    customers = []
    channels = ["GT", "MT", "Ecommerce"]
    cust_types = ["retailer", "distributor", "modern_trade"]
    
    # Pre-fetch distributor IDs to map customers to nearby distributors
    cur.execute("SELECT distributor_id, region, province, city FROM sap.distributors;")
    db_dists = cur.fetchall()
    
    for idx in range(1, 1001):
        cust_id = f"CUST-{idx:06d}"
        cust_name = fake.name()
        c_type = random.choices(cust_types, weights=[60, 15, 25])[0]
        channel = random.choices(channels, weights=[60, 25, 15])[0]
        
        # Match customer to a distributor region
        matched_dist = random.choice(db_dists)
        city = fake.city()
        prov = matched_dist[2]
        region = matched_dist[1]
        
        credit = round(random.uniform(10000000.00, 500000000.00), -5)
        created = datetime.now() - timedelta(days=random.randint(30, 365))
        
        customers.append((cust_id, cust_name, c_type, city, prov, region, channel, credit, True, created.date()))

    cur.executemany("""
        INSERT INTO sap.customers (customer_id, customer_name, customer_type, city, province, region, channel, credit_limit, is_active, created_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, customers)

    # Fetch IDs for subsequent batches
    cur.execute("SELECT customer_id, channel, region FROM sap.customers;")
    db_custs = cur.fetchall()
    
    cur.execute("SELECT material_id, unit_price, cost_price FROM sap.materials;")
    db_materials = [(row[0], float(row[1]), float(row[2])) for row in cur.fetchall()]

    # 4 & 5. Sales Orders & Sales Items (~15,000 orders, ~50,000 items)
    print("Generating sales orders & sales items...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365) # 12 months
    
    orders_batch = []
    items_batch = []
    
    order_seq = 1
    item_seq = 1
    
    current_date = start_date
    while current_date <= end_date:
        # Seasonality check: Ramadhan (approx 3 months ago from June, e.g., March/April)
        month = current_date.month
        is_ramadhan = month in [3, 4]
        is_december = month == 12
        
        # Base count
        daily_base = 35
        if is_ramadhan:
            daily_base = int(daily_base * 1.4)
        elif is_december:
            daily_base = int(daily_base * 1.20)
            
        # Add random noise
        orders_today = daily_base + random.randint(-5, 15)
        
        for _ in range(orders_today):
            cust = random.choice(db_custs)
            c_id, channel, region = cust
            
            # Match distributor based on customer region
            dists_in_region = [d[0] for d in db_dists if d[1] == region]
            dist_id = random.choice(dists_in_region) if dists_in_region else db_dists[0][0]
            
            # SAP VBAK specs
            order_id = f"SO-{current_date.strftime('%Y%m')}-{order_seq:06d}"
            sales_org = random.choice(["1000", "2000", "3000"])
            dist_chan = "10" if channel == "GT" else ("20" if channel == "MT" else "30")
            plant = random.choices(["TNG", "SMG", "SBY"], weights=[50, 30, 20])[0]
            status = random.choices(["created", "confirmed", "delivered", "invoiced"], weights=[5, 10, 15, 70])[0]
            
            # Select items
            num_items = random.randint(1, 8)
            selected_mats = random.sample(db_materials, num_items)
            
            net_value = 0
            order_items = []
            
            for m_idx, mat in enumerate(selected_mats):
                m_id, price, cost = mat
                qty = random.randint(10, 500)
                disc = random.choices([0, 5, 10, 15], weights=[70, 15, 10, 5])[0]
                item_val = price * qty * (1 - disc/100.0)
                net_value += item_val
                
                item_id = f"{order_id}-{m_idx+1:03d}"
                order_items.append((item_id, order_id, m_id, qty, price, item_val, disc, plant))
                item_seq += 1
                
            orders_batch.append((order_id, c_id, dist_id, current_date.date(), sales_org, dist_chan, net_value, 'IDR', status, plant))
            items_batch.extend(order_items)
            order_seq += 1
            
        current_date += timedelta(days=1)

    print(f"Inserting {len(orders_batch)} sales orders & {len(items_batch)} sales items...")
    execute_values(cur, """
        INSERT INTO sap.sales_orders (order_id, customer_id, distributor_id, order_date, sales_org, distribution_channel, net_value, currency, status, plant)
        VALUES %s;
    """, orders_batch)
    
    execute_values(cur, """
        INSERT INTO sap.sales_items (item_id, order_id, material_id, quantity, unit_price, net_value, discount_pct, plant)
        VALUES %s;
    """, items_batch)

    # 6. Inventory Movements (30,000 records)
    print("Generating inventory movements...")
    movements = []
    m_seq = 1
    cur.execute("SELECT order_id, plant, order_date FROM sap.sales_orders WHERE status IN ('delivered', 'invoiced');")
    db_delivered_orders = cur.fetchall()
    
    # Map order items to orders
    cur.execute("SELECT order_id, material_id, quantity FROM sap.sales_items;")
    db_order_items = cur.fetchall()
    order_items_map = {}
    for row in db_order_items:
        o_id, mat_id, qty = row
        if o_id not in order_items_map:
            order_items_map[o_id] = []
        order_items_map[o_id].append((mat_id, qty))

    # Generate receipt movements (101) & sales issue (601)
    for o_id, plant, o_date in db_delivered_orders:
        o_items = order_items_map.get(o_id, [])
        for mat_id, qty in o_items:
            # 601: Sales Issue
            m_id = f"MVMT-{o_date.strftime('%Y%m')}-{m_seq:06d}"
            movements.append((m_id, mat_id, plant, "601", qty, o_date, f"B-{random.randint(100, 999)}", "SL01"))
            m_seq += 1
            
            # Simulate corresponding production receipts (101) with some probability
            if random.random() < 0.4:
                m_id_rec = f"MVMT-{o_date.strftime('%Y%m')}-{m_seq:06d}"
                rec_qty = qty * random.uniform(1.2, 1.5)
                movements.append((m_id_rec, mat_id, plant, "101", rec_qty, o_date - timedelta(days=random.randint(1, 7)), f"B-{random.randint(100, 999)}", "PR01"))
                m_seq += 1

    print(f"Inserting {len(movements)} inventory movements...")
    execute_values(cur, """
        INSERT INTO sap.inventory_movements (movement_id, material_id, plant, movement_type, quantity, posting_date, batch, storage_location)
        VALUES %s;
    """, movements)

    # 7. E-commerce Orders (5,000 records)
    print("Generating ecommerce orders...")
    platforms = ["shopee", "tokopedia", "tiktokshop", "lazada"]
    plat_fee_pct = {"shopee": 6.5, "tokopedia": 5.0, "tiktokshop": 4.0, "lazada": 6.0}
    ecom_orders = []
    
    current_date = start_date
    e_seq = 1
    while current_date <= end_date:
        daily_count = random.randint(10, 25)
        # Spike on Double Days (11.11 & 12.12)
        if (current_date.month == 11 and current_date.day == 11) or (current_date.month == 12 and current_date.day == 12):
            daily_count = daily_count * 5
            
        for _ in range(daily_count):
            plat = random.choices(platforms, weights=[40, 30, 20, 10])[0]
            mat = random.choice(db_materials)
            m_id, price, cost = mat
            qty = random.randint(1, 5)
            rev = price * qty
            fee = rev * (plat_fee_pct[plat] / 100.0)
            ship_cost = random.randint(10000, 30000)
            city = fake.city()
            prov = fake.state()
            status = random.choices(["paid", "shipped", "delivered", "returned"], weights=[5, 5, 85, 5])[0]
            
            order_id = f"ECO-{plat[:3].upper()}-{current_date.strftime('%Y%m%d')}-{e_seq:06d}"
            ecom_orders.append((order_id, plat, current_date.date(), m_id, qty, rev, fee, ship_cost, city, prov, status))
            e_seq += 1
            
        current_date += timedelta(days=1)

    print(f"Inserting {len(ecom_orders)} ecommerce orders...")
    execute_values(cur, """
        INSERT INTO sap.ecommerce_orders (ecom_order_id, platform, order_date, product_sku, quantity, revenue, platform_fee, shipping_cost, shipping_city, shipping_province, status)
        VALUES %s;
    """, ecom_orders)

    # 8. GL Postings (20,000 records)
    print("Generating general ledger postings...")
    gl_postings = []
    gl_accounts = {
        "1100": "Cash & Bank",
        "1200": "Accounts Receivable",
        "1300": "Inventory",
        "4000": "Sales Revenue",
        "5000": "Cost of Goods Sold",
        "6000": "Operating Expenses",
        "6100": "Marketing Expenses",
        "6200": "Distribution Expenses"
    }
    
    gl_seq = 1
    # Sample postings based on daily invoice collections
    for idx, order in enumerate(orders_batch[:4000]): # Sub-sample to keep batch sizes and execution times fast
        o_id, c_id, d_id, o_date, sales_org, dist_chan, val, cur_code, status, plant = order
        doc_num = f"DOC-{o_date.strftime('%Y')}-{idx:06d}"
        
        # AR Posting (Debit AR)
        p_id_ar = f"GL-{o_date.strftime('%Y%m')}-{gl_seq:06d}"
        gl_postings.append((p_id_ar, doc_num, o_date, "1200", "Accounts Receivable", val, "IDR", "CC_SALES", "PR_BEAUTY", "debit"))
        gl_seq += 1
        
        # Revenue Posting (Credit Revenue)
        p_id_rev = f"GL-{o_date.strftime('%Y%m')}-{gl_seq:06d}"
        gl_postings.append((p_id_rev, doc_num, o_date, "4000", "Sales Revenue", val, "IDR", "CC_SALES", "PR_BEAUTY", "credit"))
        gl_seq += 1

    print(f"Inserting {len(gl_postings)} GL postings...")
    execute_values(cur, """
        INSERT INTO sap.gl_postings (posting_id, document_number, posting_date, gl_account, gl_account_name, amount, currency, cost_center, profit_center, posting_type)
        VALUES %s;
    """, gl_postings)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Simulated SAP ERP data seeding successfully completed!")

if __name__ == "__main__":
    main()
