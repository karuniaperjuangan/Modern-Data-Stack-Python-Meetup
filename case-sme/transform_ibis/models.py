import ibis

def daily_revenue(con):
    """Calculate daily revenue per branch using Ibis expressions"""
    orders = con.table("orders", database="raw")
    branches = con.table("branches", database="raw")
    
    # Cast timestamp to date
    orders_mutated = orders.mutate(order_date_day=orders.order_date.date())
    
    joined = orders_mutated.join(branches, orders_mutated.branch_id == branches.branch_id)
    
    grouped = (
        joined.group_by([joined.order_date_day, joined.branch_name])
        .agg(daily_revenue=joined.total_amount.sum())
        .order_by([ibis.desc("order_date_day"), "branch_name"])
    )
    return grouped

def menu_popularity(con):
    """Rank menu popularity (quantity and revenue) using Ibis expressions"""
    items = con.table("order_items", database="raw")
    products = con.table("products", database="raw")
    
    joined = items.join(products, items.product_id == products.product_id)
    
    grouped = (
        joined.group_by([products.product_name, products.category])
        .agg(
            total_quantity=items.quantity.sum(),
            total_revenue=items.subtotal.sum(),
            order_count=items.order_id.nunique()
        )
        .order_by(ibis.desc("total_revenue"))
    )
    return grouped

def peak_hours(con):
    """Analyze peak hours order distributions per branch using Ibis expressions"""
    orders = con.table("orders", database="raw")
    branches = con.table("branches", database="raw")
    
    orders_mutated = orders.mutate(hour=orders.order_date.hour())
    
    joined = orders_mutated.join(branches, orders_mutated.branch_id == branches.branch_id)
    
    grouped = (
        joined.group_by([joined.branch_name, joined.hour])
        .agg(
            order_count=joined.order_id.count(),
            avg_amount=joined.total_amount.mean()
        )
        .order_by([joined.branch_name, ibis.desc("order_count")])
    )
    return grouped

def branch_comparison(con):
    """Compare performance metrics between branches using Ibis expressions"""
    orders = con.table("orders", database="raw")
    branches = con.table("branches", database="raw")
    
    joined = orders.join(branches, orders.branch_id == branches.branch_id)
    
    grouped = (
        joined.group_by([branches.branch_name])
        .agg(
            total_revenue=joined.total_amount.sum(),
            total_orders=joined.order_id.count(),
            avg_ticket_size=joined.total_amount.mean(),
            total_customers=joined.customer_count.sum()
        )
    )
    return grouped
