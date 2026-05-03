SELECT ROUND(SUM(revenue), 2) AS total_revenue
FROM master_orders;

SELECT COUNT(DISTINCT order_id) AS total_orders
FROM master_orders;

SELECT COUNT(DISTINCT customer_unique_id) AS customers
FROM master_orders;

SELECT ROUND(SUM(revenue) /
COUNT(DISTINCT order_id),2) AS aov
FROM master_orders;

SELECT ROUND(AVG(review_score),2) AS avg_review
FROM master_orders;