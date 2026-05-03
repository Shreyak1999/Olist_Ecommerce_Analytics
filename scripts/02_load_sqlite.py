import pandas as pd
import sqlite3

conn = sqlite3.connect("retailiq.db")

master = pd.read_csv("data/clean/master_orders.csv")
cust = pd.read_csv("data/clean/customer_summary.csv")
monthly = pd.read_csv("data/clean/monthly_sales.csv")

master.to_sql("master_orders", conn, if_exists="replace", index=False)
cust.to_sql("customer_summary", conn, if_exists="replace", index=False)
monthly.to_sql("monthly_sales", conn, if_exists="replace", index=False)

conn.close()

print("Loaded successfully.")