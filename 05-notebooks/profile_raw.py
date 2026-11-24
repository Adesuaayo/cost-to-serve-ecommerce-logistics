import sys, duckdb
RAW = sys.argv[1]
con = duckdb.connect()
tables = {
 "customers":"olist_customers_dataset.csv",
 "geolocation":"olist_geolocation_dataset.csv",
 "order_items":"olist_order_items_dataset.csv",
 "payments":"olist_order_payments_dataset.csv",
 "reviews":"olist_order_reviews_dataset.csv",
 "orders":"olist_orders_dataset.csv",
 "products":"olist_products_dataset.csv",
 "sellers":"olist_sellers_dataset.csv",
 "category_tr":"product_category_name_translation.csv",
}
for t,f in tables.items():
    con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_csv_auto('{RAW}/{f}', header=true)")

def q(label, sql):
    print("\n### " + label)
    try:
        print(con.execute(sql).df().to_string(index=False))
    except Exception as e:
        print("ERR", e)

print("=== ROW COUNTS AND COLUMNS ===")
for t in tables:
    n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    cols = [c[0] for c in con.execute(f"DESCRIBE {t}").fetchall()]
    print(f"{t:14s} rows={n:>9,}  cols={len(cols)}  {cols}")

q("orders: status distribution", """
SELECT order_status, count(*) n, round(100.0*count(*)/sum(count(*)) OVER (),2) pct
FROM orders GROUP BY 1 ORDER BY n DESC""")

q("orders: date coverage and null delivery dates", """
SELECT min(order_purchase_timestamp) first_order, max(order_purchase_timestamp) last_order,
 sum(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) null_delivered,
 sum(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END) null_approved,
 sum(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 ELSE 0 END) null_carrier,
 sum(CASE WHEN order_estimated_delivery_date IS NULL THEN 1 ELSE 0 END) null_estimated
FROM orders""")

q("orders: delivered orders missing actual delivery date", """
SELECT order_status, count(*) n FROM orders
WHERE order_delivered_customer_date IS NULL GROUP BY 1 ORDER BY n DESC""")

q("orders: volume by year", """
SELECT year(order_purchase_timestamp) yr, count(*) n FROM orders GROUP BY 1 ORDER BY 1""")

q("key uniqueness", """
SELECT 'orders.order_id' k, count(*) rows, count(DISTINCT order_id) distinct_k FROM orders
UNION ALL SELECT 'customers.customer_id', count(*), count(DISTINCT customer_id) FROM customers
UNION ALL SELECT 'customers.customer_unique_id', count(*), count(DISTINCT customer_unique_id) FROM customers
UNION ALL SELECT 'sellers.seller_id', count(*), count(DISTINCT seller_id) FROM sellers
UNION ALL SELECT 'products.product_id', count(*), count(DISTINCT product_id) FROM products
UNION ALL SELECT 'reviews.review_id', count(*), count(DISTINCT review_id) FROM reviews
UNION ALL SELECT 'reviews.order_id', count(*), count(DISTINCT order_id) FROM reviews
UNION ALL SELECT 'geolocation.zip_prefix', count(*), count(DISTINCT geolocation_zip_code_prefix) FROM geolocation""")

q("order_items: items per order", """
SELECT items, count(*) orders FROM (SELECT order_id, count(*) items FROM order_items GROUP BY 1)
GROUP BY 1 ORDER BY 1 LIMIT 12""")

q("order_items: sellers per order (multi-seller split shipments)", """
SELECT sellers_in_order, count(*) orders FROM
 (SELECT order_id, count(DISTINCT seller_id) sellers_in_order FROM order_items GROUP BY 1)
GROUP BY 1 ORDER BY 1""")

q("order_items: price and freight stats", """
SELECT count(*) items, round(min(price),2) min_price, round(median(price),2) med_price,
 round(max(price),2) max_price, round(min(freight_value),2) min_fr,
 round(median(freight_value),2) med_fr, round(max(freight_value),2) max_fr,
 sum(CASE WHEN freight_value = 0 THEN 1 ELSE 0 END) zero_freight,
 sum(CASE WHEN freight_value IS NULL THEN 1 ELSE 0 END) null_freight
FROM order_items""")

q("join integrity", """
SELECT 'orders without items' chk, count(*) n FROM orders o
 WHERE NOT EXISTS (SELECT 1 FROM order_items i WHERE i.order_id=o.order_id)
UNION ALL SELECT 'items without parent order', count(*) FROM order_items i
 WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.order_id=i.order_id)
UNION ALL SELECT 'orders without customer row', count(*) FROM orders o
 WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id=o.customer_id)
UNION ALL SELECT 'items with missing seller row', count(*) FROM order_items i
 WHERE NOT EXISTS (SELECT 1 FROM sellers s WHERE s.seller_id=i.seller_id)
UNION ALL SELECT 'items with missing product row', count(*) FROM order_items i
 WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.product_id=i.product_id)
UNION ALL SELECT 'orders without review', count(*) FROM orders o
 WHERE NOT EXISTS (SELECT 1 FROM reviews r WHERE r.order_id=o.order_id)""")

q("products: nulls on weight and dimensions", """
SELECT count(*) rows,
 sum(CASE WHEN product_weight_g IS NULL THEN 1 ELSE 0 END) null_weight,
 sum(CASE WHEN product_length_cm IS NULL THEN 1 ELSE 0 END) null_length,
 sum(CASE WHEN product_category_name IS NULL THEN 1 ELSE 0 END) null_category,
 sum(CASE WHEN product_weight_g = 0 THEN 1 ELSE 0 END) zero_weight
FROM products""")

q("customers: repeat purchase rate on customer_unique_id", """
SELECT orders_per_customer, count(*) customers FROM
 (SELECT c.customer_unique_id, count(DISTINCT o.order_id) orders_per_customer
  FROM orders o JOIN customers c USING(customer_id) GROUP BY 1)
GROUP BY 1 ORDER BY 1 LIMIT 8""")

q("reviews: score distribution", """
SELECT review_score, count(*) n, round(100.0*count(*)/sum(count(*)) OVER (),2) pct
FROM reviews GROUP BY 1 ORDER BY 1""")

q("geolocation: coverage of customer and seller zip prefixes", """
SELECT 'customer zips not in geolocation' chk, count(DISTINCT customer_zip_code_prefix) n
 FROM customers c WHERE NOT EXISTS
 (SELECT 1 FROM geolocation g WHERE g.geolocation_zip_code_prefix=c.customer_zip_code_prefix)
UNION ALL SELECT 'seller zips not in geolocation', count(DISTINCT seller_zip_code_prefix)
 FROM sellers s WHERE NOT EXISTS
 (SELECT 1 FROM geolocation g WHERE g.geolocation_zip_code_prefix=s.seller_zip_code_prefix)""")

q("lateness on delivered orders", """
SELECT count(*) delivered,
 sum(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) late,
 round(100.0*sum(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END)/count(*),2) pct_late,
 round(avg(date_diff('day', order_purchase_timestamp, order_delivered_customer_date)),2) avg_days_to_deliver,
 round(avg(date_diff('day', order_estimated_delivery_date, order_delivered_customer_date)),2) avg_days_vs_promise
FROM orders WHERE order_status='delivered' AND order_delivered_customer_date IS NOT NULL""")
