import ibis

def channel_sales_mix(con):
    """Analyze monthly channel sales mix using Ibis"""
    # DuckDB catalog scanning of Iceberg tables registered in the catalog
    # For ibis, since we are connected to duckdb, we can scan files via path or catalog name
    # We will register them as tables in duckdb, then query them.
    # To keep it portable and fast:
    orders = con.table("stg_sales_orders")
    
    # Cast/Extract month
    orders_mutated = orders.mutate(sales_month=orders.order_date.truncate("M"))
    
    grouped = (
        orders_mutated.group_by([orders_mutated.sales_month, orders_mutated.distribution_channel])
        .agg(
            monthly_revenue=orders_mutated.net_value.sum(),
            order_count=orders_mutated.order_id.count()
        )
        .order_by(["sales_month", "distribution_channel"])
    )
    return grouped

def brand_margin_analysis(con):
    """Analyze margins per brand and category using Ibis"""
    items = con.table("stg_sales_items")
    mats = con.table("stg_materials")
    
    joined = items.join(mats, items.material_id == mats.material_id)
    
    grouped = (
        joined.group_by([mats.brand, mats.category])
        .agg(
            total_qty=joined.quantity.sum(),
            gross_revenue=joined.net_value.sum(),
            total_cost=(joined.quantity * joined.cost_price).sum()
        )
    )
    
    mutated = grouped.mutate(
        gross_profit=grouped.gross_revenue - grouped.total_cost
    )
    # Gross margin %
    result = mutated.mutate(
        gross_margin_pct=(mutated.gross_profit / mutated.gross_revenue) * 100
    )
    return result

def regional_performance(con):
    """Analyze sales volumes and revenues per region/province using Ibis"""
    orders = con.table("stg_sales_orders")
    custs = con.table("stg_customers")
    
    joined = orders.join(custs, orders.customer_id == custs.customer_id)
    
    grouped = (
        joined.group_by([custs.region, custs.province])
        .agg(
            total_revenue=joined.net_value.sum(),
            order_count=joined.order_id.count()
        )
        .order_by(ibis.desc("total_revenue"))
    )
    return grouped

def distributor_scorecard(con):
    """Scorecard performance evaluation for distributors using Ibis"""
    orders = con.table("stg_sales_orders")
    dists = con.table("stg_distributors")
    
    joined = orders.join(dists, orders.distributor_id == dists.distributor_id)
    
    grouped = (
        joined.group_by([
            joined.distributor_id,
            joined.distributor_name,
            joined.region,
            joined.credit_limit
        ])
        .agg(
            total_revenue=joined.net_value.sum(),
            order_count=joined.order_id.count(),
            customer_coverage=joined.customer_id.nunique()
        )
    )
    
    # Calculate credit utilization ratio
    result = grouped.mutate(
        credit_utilization_pct=(grouped.total_revenue / grouped.credit_limit) * 100
    ).order_by(ibis.desc("total_revenue"))
    return result
