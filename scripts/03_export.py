# scripts/03_export.py

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================
DB_PATH = "retailiq.db"
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# CONNECT DB
# =====================================================
conn = sqlite3.connect(DB_PATH)

# =====================================================
# SQL QUERIES
# =====================================================
queries = {

    # ---------------------------------------------
    # 1. KPI SUMMARY (1 ROW)
    # ---------------------------------------------
    "kpi_summary.csv": """
        SELECT
            ROUND(SUM(revenue),2) AS total_revenue,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_unique_id) AS total_customers,
            ROUND(SUM(revenue) * 1.0 /
                COUNT(DISTINCT order_id),2) AS aov,
            ROUND(AVG(review_score),2) AS avg_review_score,
            ROUND(AVG(delivery_days),2) AS avg_delivery_days
        FROM sales_ready
    """,

    # ---------------------------------------------
    # 2. MONTHLY DASHBOARD
    # ---------------------------------------------
    "monthly_dashboard.csv": """
        SELECT
            purchase_month,
            ROUND(SUM(revenue),2) AS revenue,
            COUNT(DISTINCT order_id) AS orders,
            COUNT(DISTINCT customer_unique_id) AS customers,
            ROUND(
                SUM(revenue) * 1.0 /
                COUNT(DISTINCT order_id),2
            ) AS aov
        FROM sales_ready
        GROUP BY purchase_month
        ORDER BY purchase_month
    """,

    # ---------------------------------------------
    # 3. CATEGORY SALES
    # ---------------------------------------------
    "category_sales.csv": """
        SELECT
            COALESCE(
                product_category_name_english,
                'Unknown'
            ) AS category,
            ROUND(SUM(revenue),2) AS revenue,
            COUNT(DISTINCT order_id) AS orders,
            ROUND(AVG(review_score),2) AS avg_review
        FROM sales_ready
        GROUP BY category
        ORDER BY revenue DESC
    """,

    # ---------------------------------------------
    # 4. STATE SALES
    # ---------------------------------------------
    "state_sales.csv": """
        SELECT
            customer_state,
            ROUND(SUM(revenue),2) AS revenue,
            COUNT(DISTINCT customer_unique_id) AS customers,
            ROUND(AVG(delivery_days),2) AS avg_delivery_days
        FROM sales_ready
        GROUP BY customer_state
        ORDER BY revenue DESC
    """,

    # ---------------------------------------------
    # 5. CUSTOMER SEGMENTS
    # ---------------------------------------------
    "customer_segments.csv": """
        SELECT
            churn_flag,
            COUNT(*) AS customers,
            ROUND(SUM(total_spend),2) AS total_spend,
            ROUND(AVG(total_spend),2) AS avg_spend
        FROM customer_summary
        GROUP BY churn_flag
    """,

    # ---------------------------------------------
    # 6. TOP CUSTOMERS
    # ---------------------------------------------
    "top_customers.csv": """
        SELECT
            customer_unique_id,
            total_orders,
            ROUND(total_spend,2) AS total_spend,
            days_since_last,
            churn_flag
        FROM customer_summary
        ORDER BY total_spend DESC
        LIMIT 100
    """,

    # ---------------------------------------------
    # 7. DELIVERY STATUS
    # ---------------------------------------------
    "delay_analysis.csv": """
        SELECT
            CASE
                WHEN delivery_days > 10
                THEN 'Late'
                ELSE 'On Time'
            END AS delivery_status,
            COUNT(*) AS orders
        FROM master_orders
        GROUP BY delivery_status
    """,

    # ---------------------------------------------
    # 8. REVIEW DISTRIBUTION
    # ---------------------------------------------
    "review_distribution.csv": """
        SELECT
            review_score,
            COUNT(*) AS orders
        FROM master_orders
        GROUP BY review_score
        ORDER BY review_score
    """
}

# =====================================================
# EXPORT LOOP
# =====================================================
print("=" * 50)
print("RetailIQ Export Started")
print("=" * 50)

for filename, query in queries.items():
    try:
        df = pd.read_sql_query(query, conn)
        filepath = EXPORT_DIR / filename
        df.to_csv(filepath, index=False)
        print(f"✔ Created: {filename} | Rows: {len(df)}")

    except Exception as e:
        print(f"✘ Failed: {filename}")
        print(e)

# =====================================================
# METADATA FILE
# =====================================================
meta = pd.DataFrame({
    "last_refresh": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "database": [DB_PATH],
    "exports_created": [len(queries)]
})

meta.to_csv(EXPORT_DIR / "refresh_log.csv", index=False)

# =====================================================
# CLOSE
# =====================================================
conn.close()

print("=" * 50)
print("All Exports Completed Successfully")
print("=" * 50)