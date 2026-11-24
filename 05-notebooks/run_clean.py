import sys, duckdb, json
RAW, SQL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
con = duckdb.connect()
tables = {
 "customers":"olist_customers_dataset.csv","geolocation":"olist_geolocation_dataset.csv",
 "order_items":"olist_order_items_dataset.csv","payments":"olist_order_payments_dataset.csv",
 "reviews":"olist_order_reviews_dataset.csv","orders":"olist_orders_dataset.csv",
 "products":"olist_products_dataset.csv","sellers":"olist_sellers_dataset.csv",
 "category_tr":"product_category_name_translation.csv"}
for t,f in tables.items():
    con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_csv_auto('{RAW}/{f}', header=true)")

one = lambda s: con.execute(s).fetchone()[0]
log = {}
log["orders_raw"] = one("SELECT count(*) FROM orders")
log["geo_raw_rows"] = one("SELECT count(*) FROM geolocation")
log["geo_outside_brazil"] = one("""SELECT count(*) FROM geolocation WHERE NOT
 (geolocation_lat BETWEEN -34.0 AND 5.3 AND geolocation_lng BETWEEN -74.0 AND -34.8)""")
log["reviews_raw"] = one("SELECT count(*) FROM reviews")
log["reviews_bad_score"] = one("SELECT count(*) FROM reviews WHERE review_score NOT BETWEEN 1 AND 5 OR review_score IS NULL")

con.execute(open(SQL).read())

log["geo_prefix_rows"] = one("SELECT count(*) FROM geo_prefix")
log["reviews_dedup_rows"] = one("SELECT count(*) FROM review_order")
log["reviews_dropped_dupes"] = log["reviews_raw"] - log["reviews_bad_score"] - log["reviews_dedup_rows"]
log["item_order_rows"] = one("SELECT count(*) FROM item_order")

# exclusion accounting, each measured against the raw orders table
log["excl_status"] = one("SELECT count(*) FROM orders WHERE order_status NOT IN ('delivered','shipped')")
log["excl_no_items"] = one("""SELECT count(*) FROM orders o WHERE o.order_status IN ('delivered','shipped')
 AND NOT EXISTS (SELECT 1 FROM item_order i WHERE i.order_id=o.order_id)""")
log["excl_period"] = one("""SELECT count(*) FROM orders o JOIN item_order i USING(order_id)
 WHERE o.order_status IN ('delivered','shipped')
 AND (o.order_purchase_timestamp < TIMESTAMP '2017-01-01' OR o.order_purchase_timestamp >= TIMESTAMP '2018-09-01')""")
log["excl_delivered_no_date"] = one("""SELECT count(*) FROM orders o JOIN item_order i USING(order_id)
 WHERE o.order_status='delivered' AND o.order_delivered_customer_date IS NULL
 AND o.order_purchase_timestamp >= TIMESTAMP '2017-01-01' AND o.order_purchase_timestamp < TIMESTAMP '2018-09-01'""")
log["fact_rows"] = one("SELECT count(*) FROM fact_orders")

print(json.dumps(log, indent=1))

print("\n=== VALIDATION ===")
checks = {
 "fact_orders duplicate order_id":"SELECT count(*)-count(DISTINCT order_id) FROM fact_orders",
 "null lane":"SELECT count(*) FROM fact_orders WHERE lane IS NULL",
 "null distance_km":"SELECT count(*) FROM fact_orders WHERE distance_km IS NULL",
 "negative distance":"SELECT count(*) FROM fact_orders WHERE distance_km < 0",
 "distance over 5000km":"SELECT count(*) FROM fact_orders WHERE distance_km > 5000",
 "negative freight":"SELECT count(*) FROM fact_orders WHERE freight_value < 0",
 "zero order_value":"SELECT count(*) FROM fact_orders WHERE order_value <= 0",
 "negative total_days":"SELECT count(*) FROM fact_orders WHERE total_days < 0",
 "negative transit_days":"SELECT count(*) FROM fact_orders WHERE transit_days < 0",
 "negative dispatch_days":"SELECT count(*) FROM fact_orders WHERE dispatch_days < 0",
 "total_days over 200":"SELECT count(*) FROM fact_orders WHERE total_days > 200",
 "geo fallback used":"SELECT count(*) FROM fact_orders WHERE geo_fallback_used",
 "items missing weight":"SELECT count(*) FROM fact_orders WHERE items_missing_weight > 0",
 "null review_score":"SELECT count(*) FROM fact_orders WHERE review_score IS NULL",
 "null is_late":"SELECT count(*) FROM fact_orders WHERE is_late IS NULL",
 "zero freight orders":"SELECT count(*) FROM fact_orders WHERE freight_value = 0",
 "unknown category":"SELECT count(*) FROM fact_orders WHERE primary_category='unknown'",
}
for k,s in checks.items():
    print(f"{k:34s} {one(s):>8,}")

print("\n=== RECONCILIATION AGAINST RAW ===")
print(con.execute("""
SELECT 'fact order_value total' k, round(sum(order_value),2) v FROM fact_orders
UNION ALL SELECT 'raw item price total (in-scope orders)',
 round(sum(i.price),2) FROM order_items i JOIN fact_orders f USING(order_id)
UNION ALL SELECT 'fact freight total', round(sum(freight_value),2) FROM fact_orders
UNION ALL SELECT 'raw item freight total (in-scope orders)',
 round(sum(i.freight_value),2) FROM order_items i JOIN fact_orders f USING(order_id)
""").df().to_string(index=False))

print("\n=== HEADLINE SHAPE ===")
print(con.execute("""
SELECT count(*) orders, round(sum(order_value),0) gmv, round(sum(freight_value),0) freight,
 round(100.0*sum(freight_value)/sum(order_value),2) freight_pct_gmv,
 round(avg(total_days),2) avg_days, round(avg(distance_km),0) avg_km,
 round(100.0*avg(CASE WHEN is_late THEN 1.0 ELSE 0 END),2) pct_late,
 round(avg(review_score),3) avg_review,
 min(purchased_at)::DATE first_day, max(purchased_at)::DATE last_day
FROM fact_orders""").df().to_string(index=False))

con.execute(f"COPY fact_orders TO '{OUT}/fact_orders.parquet' (FORMAT parquet)")
con.execute(f"COPY fact_orders TO '{OUT}/fact_orders.csv' (HEADER, DELIMITER ',')")
con.execute(f"COPY geo_prefix TO '{OUT}/dim_geo_prefix.csv' (HEADER, DELIMITER ',')")
print("\nexported")
