
-- KPI SUMMARY
SELECT
SUM(revenue) AS total_revenue,
COUNT(DISTINCT order_id) AS total_orders,
COUNT(DISTINCT customer_unique_id) AS total_customers,
ROUND(SUM(revenue)*1.0/COUNT(DISTINCT order_id),2) AS aov,
ROUND(AVG(review_score),2) AS avg_review_score
FROM sales_ready;

-- CATEGORY SALES
SELECT
product_category_name_english AS category,
SUM(revenue) AS revenue,
COUNT(DISTINCT order_id) AS orders,
ROUND(AVG(review_score),2) AS avg_review
FROM sales_ready
GROUP BY 1
ORDER BY revenue DESC;

-- STATE SALES
SELECT
customer_state,
SUM(revenue) AS revenue,
COUNT(DISTINCT customer_unique_id) AS customers,
ROUND(AVG(delivery_days),2) AS avg_delivery_days
FROM sales_ready
GROUP BY 1
ORDER BY revenue DESC;

-- CUSTOMER SEGMENTS
SELECT
churn_flag,
COUNT(*) AS customers,
SUM(total_spend) AS total_spend,
ROUND(AVG(total_spend),2) AS avg_spend
FROM customer_summary
GROUP BY 1;

-- TOP CUSTOMERS
SELECT
customer_unique_id,
total_orders,
ROUND(total_spend,2) AS total_spend,
days_since_last,
churn_flag
FROM customer_summary
ORDER BY total_spend DESC
LIMIT 100;

-- DELAY ANALYSIS
SELECT
CASE
WHEN delivery_days > 10 THEN 'Late'
ELSE 'On Time'
END AS delivery_status,
COUNT(*) AS orders
FROM master_orders
GROUP BY 1;

-- REVIEW DISTRIBUTION
SELECT
review_score,
COUNT(*) AS orders
FROM master_orders
GROUP BY 1
ORDER BY 1;

-- MONTHLY DASHBOARD
SELECT
purchase_month,
SUM(revenue) AS revenue,
COUNT(DISTINCT order_id) AS orders,
COUNT(DISTINCT customer_unique_id) AS customers,
ROUND(SUM(revenue)*1.0/COUNT(DISTINCT order_id),2) AS aov
FROM sales_ready
GROUP BY purchase_month
ORDER BY purchase_month;