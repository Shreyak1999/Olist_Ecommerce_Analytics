import pandas as pd
import numpy as np
from pathlib import Path


# -----------------------------------
# Load CSVs
# -----------------------------------
orders = pd.read_csv("data/raw/olist_orders_dataset.csv")
items = pd.read_csv("data/raw/olist_order_items_dataset.csv")
customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
products = pd.read_csv("data/raw/olist_products_dataset.csv")
reviews = pd.read_csv("data/raw/olist_order_reviews_dataset.csv")
payments = pd.read_csv("data/raw/olist_order_payments_dataset.csv")
sellers = pd.read_csv("data/raw/olist_sellers_dataset.csv")
cats = pd.read_csv("data/raw/product_category_name_translation.csv")

# -----------------------------------
# Standardize Columns
# -----------------------------------
for df in [orders, items, customers, products, reviews, payments, sellers, cats]:
    df.columns = df.columns.str.lower().str.strip()

# -----------------------------------
# Convert Dates
# -----------------------------------
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for c in date_cols:
    if c in orders.columns:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")

# -----------------------------------
# Product Category Translation
# -----------------------------------
products = products.merge(
    cats,
    on="product_category_name",
    how="left"
)

# -----------------------------------
# Aggregate Payments (one row/order)
# -----------------------------------
pay_agg = payments.groupby("order_id", as_index=False).agg(
    total_payment_value=("payment_value", "sum"),
    max_installments=("payment_installments", "max")
)

# -----------------------------------
# Aggregate Reviews (one row/order)
# -----------------------------------
rev_agg = reviews.groupby("order_id", as_index=False).agg(
    review_score=("review_score", "mean")
)

# -----------------------------------
# Aggregate Order Items (one row/order)
# IMPORTANT: Prevent duplication
# -----------------------------------
item_agg = items.groupby("order_id", as_index=False).agg(
    total_items=("order_item_id", "count"),
    revenue=("price", "sum"),
    freight_value=("freight_value", "sum"),
    seller_count=("seller_id", "nunique")
)

# Top category per order
item_prod = items.merge(
    products[["product_id", "product_category_name_english"]],
    on="product_id",
    how="left"
)

top_cat = (
    item_prod.groupby(["order_id", "product_category_name_english"])
    .size()
    .reset_index(name="cnt")
    .sort_values(["order_id", "cnt"], ascending=[True, False])
    .drop_duplicates("order_id")
    [["order_id", "product_category_name_english"]]
)

item_agg = item_agg.merge(top_cat, on="order_id", how="left")

# -----------------------------------
# Build Master Table (one row/order)
# -----------------------------------
master = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(item_agg, on="order_id", how="left")
    .merge(pay_agg, on="order_id", how="left")
    .merge(rev_agg, on="order_id", how="left")
)

# -----------------------------------
# Feature Engineering
# -----------------------------------
master["delivery_days"] = (
    master["order_delivered_customer_date"]
    - master["order_purchase_timestamp"]
).dt.days

master["approval_hours"] = (
    master["order_approved_at"]
    - master["order_purchase_timestamp"]
).dt.total_seconds() / 3600

master["purchase_month"] = master["order_purchase_timestamp"].dt.to_period("M").astype(str)

master["purchase_year"] = master["order_purchase_timestamp"].dt.year

master["is_delayed"] = np.where(
    master["order_delivered_customer_date"] >
    master["order_estimated_delivery_date"],
    1, 0
)

master["aov"] = master["revenue"]

# Fill Nulls
master["review_score"] = master["review_score"].fillna(0)
master["delivery_days"] = master["delivery_days"].fillna(0)

# -----------------------------------
# Sales Table
# -----------------------------------
sales_df = master[
    master["order_status"].isin(["delivered","shipped","invoiced"])
].copy()

sales_df = sales_df[sales_df["revenue"].notna()]

# -----------------------------------
# Save Master Orders Table
# -----------------------------------
master.to_csv("data/clean/master_orders.csv", index=False)

# -----------------------------------
# Sales Table
# -----------------------------------
sales_df.to_csv("data/clean/sales_ready.csv", index=False)

# -----------------------------------
# Customer Summary
# -----------------------------------
customer_summary = master.groupby("customer_unique_id", as_index=False).agg(
    total_orders=("order_id", "nunique"),
    total_spend=("revenue", "sum"),
    avg_review=("review_score", "mean"),
    last_order=("order_purchase_timestamp", "max")
)

max_date = master["order_purchase_timestamp"].max()

customer_summary["days_since_last"] = (
    max_date - customer_summary["last_order"]
).dt.days

customer_summary["churn_flag"] = np.where(
    customer_summary["days_since_last"] > 120,
    "High Risk",
    "Active"
)

customer_summary.to_csv("data/clean/customer_summary.csv", index=False)

# -----------------------------------
# Monthly Sales
# -----------------------------------
monthly = master.groupby("purchase_month", as_index=False).agg(
    revenue=("revenue", "sum"),
    orders=("order_id", "nunique"),
    customers=("customer_unique_id", "nunique")
)

monthly["aov"] = monthly["revenue"] / monthly["orders"]

monthly.to_csv("data/clean/monthly_sales.csv", index=False)

# -----------------------------------
# Done
# -----------------------------------
print("Files created:")
print("master_orders.csv")
print("sales_ready.csv")
print("customer_summary.csv")
print("monthly_sales.csv")
print("Master Shape:", master.shape)