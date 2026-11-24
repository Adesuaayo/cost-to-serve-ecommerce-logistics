-- =====================================================================
-- Case 1: Reducing cost-to-serve in e-commerce logistics
-- Stage 3: cleaning, validation and analysis base table
-- Engine: DuckDB
-- Input : nine raw Olist CSVs (read via views created by the runner)
-- Output: fact_orders, one row per in-scope order
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Geography: reduce geolocation to one centroid per postcode prefix.
--    Raw table holds 1,000,163 rows for 19,015 prefixes, so joining it
--    unreduced would multiply the fact table. Coordinates outside
--    Brazil's bounding box are discarded before the median is taken.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE geo_prefix AS
SELECT
    geolocation_zip_code_prefix          AS zip_prefix,
    median(geolocation_lat)              AS lat,
    median(geolocation_lng)              AS lng,
    count(*)                             AS n_points
FROM geolocation
WHERE geolocation_lat BETWEEN -34.0 AND  5.3
  AND geolocation_lng BETWEEN -74.0 AND -34.8
GROUP BY 1;

-- State-level fallback for the 164 postcodes absent from geolocation.
CREATE OR REPLACE TABLE geo_state AS
SELECT
    geolocation_state                    AS state,
    median(geolocation_lat)              AS lat,
    median(geolocation_lng)              AS lng
FROM geolocation
WHERE geolocation_lat BETWEEN -34.0 AND  5.3
  AND geolocation_lng BETWEEN -74.0 AND -34.8
GROUP BY 1;

-- ---------------------------------------------------------------------
-- 2. Reviews: collapse to one row per order.
--    review_id is not unique (99,224 rows, 98,410 ids, 98,673 orders),
--    so the most recently created review per order is kept.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE review_order AS
SELECT order_id, review_score, review_creation_date
FROM (
    SELECT
        order_id,
        review_score,
        review_creation_date,
        row_number() OVER (
            PARTITION BY order_id
            ORDER BY review_creation_date DESC, review_id
        ) AS rn
    FROM reviews
    WHERE review_score BETWEEN 1 AND 5
)
WHERE rn = 1;

-- ---------------------------------------------------------------------
-- 3. Items: aggregate to order grain and identify the dominant seller.
--    Freight is charged per item, so order freight is the item sum.
--    The dominant seller (highest item value) defines the order's lane
--    for split shipments, which are flagged separately.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE item_order AS
WITH ranked_seller AS (
    SELECT
        order_id,
        seller_id,
        sum(price)   AS seller_value,
        count(*)     AS seller_items,
        row_number() OVER (
            PARTITION BY order_id
            ORDER BY sum(price) DESC, count(*) DESC, seller_id
        ) AS rn
    FROM order_items
    GROUP BY order_id, seller_id
),
cat AS (
    SELECT
        i.order_id,
        coalesce(t.product_category_name_english,
                 p.product_category_name,
                 'unknown') AS category,
        sum(i.price)        AS cat_value,
        row_number() OVER (
            PARTITION BY i.order_id
            ORDER BY sum(i.price) DESC, 2
        ) AS rn
    FROM order_items i
    LEFT JOIN products p USING (product_id)
    LEFT JOIN category_tr t
           ON t.product_category_name = p.product_category_name
    GROUP BY 1, 2
),
agg AS (
    SELECT
        i.order_id,
        count(*)                                   AS n_items,
        count(DISTINCT i.seller_id)                AS n_sellers,
        round(sum(i.price), 2)                     AS order_value,
        round(sum(i.freight_value), 2)             AS freight_value,
        round(sum(coalesce(p.product_weight_g, 0)) / 1000.0, 3) AS weight_kg,
        sum(CASE WHEN p.product_weight_g IS NULL
                   OR p.product_weight_g = 0 THEN 1 ELSE 0 END) AS items_missing_weight,
        max(i.shipping_limit_date)                 AS shipping_limit_date
    FROM order_items i
    LEFT JOIN products p USING (product_id)
    GROUP BY 1
)
SELECT
    a.*,
    s.seller_id        AS primary_seller_id,
    c.category         AS primary_category
FROM agg a
LEFT JOIN ranked_seller s ON s.order_id = a.order_id AND s.rn = 1
LEFT JOIN cat          c ON c.order_id = a.order_id AND c.rn = 1;

-- ---------------------------------------------------------------------
-- 4. Fact table: one row per in-scope order.
--    Scope: status delivered or shipped, purchased 2017-01-01 to
--    2018-08-31, has at least one item, and a delivery date when the
--    status says delivered. Distance is great-circle between the
--    dominant seller's postcode centroid and the customer's.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE fact_orders AS
WITH base AS (
    SELECT
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp              AS purchased_at,
        o.order_approved_at                     AS approved_at,
        o.order_delivered_carrier_date          AS handover_at,
        o.order_delivered_customer_date         AS delivered_at,
        o.order_estimated_delivery_date         AS promised_date,
        c.customer_state,
        c.customer_city,
        c.customer_zip_code_prefix              AS cust_zip,
        s.seller_state,
        s.seller_city,
        s.seller_zip_code_prefix                AS sell_zip,
        i.n_items, i.n_sellers, i.order_value, i.freight_value,
        i.weight_kg, i.items_missing_weight, i.shipping_limit_date,
        i.primary_seller_id, i.primary_category,
        r.review_score,
        coalesce(gc.lat, gcs.lat)               AS cust_lat,
        coalesce(gc.lng, gcs.lng)               AS cust_lng,
        coalesce(gs.lat, gss.lat)               AS sell_lat,
        coalesce(gs.lng, gss.lng)               AS sell_lng,
        CASE WHEN gc.zip_prefix IS NULL OR gs.zip_prefix IS NULL
             THEN TRUE ELSE FALSE END           AS geo_fallback_used
    FROM orders o
    JOIN customers  c ON c.customer_id = o.customer_id
    JOIN item_order i ON i.order_id    = o.order_id
    LEFT JOIN sellers s ON s.seller_id = i.primary_seller_id
    LEFT JOIN review_order r ON r.order_id = o.order_id
    LEFT JOIN geo_prefix gc ON gc.zip_prefix = c.customer_zip_code_prefix
    LEFT JOIN geo_prefix gs ON gs.zip_prefix = s.seller_zip_code_prefix
    LEFT JOIN geo_state  gcs ON gcs.state    = c.customer_state
    LEFT JOIN geo_state  gss ON gss.state    = s.seller_state
    WHERE o.order_status IN ('delivered', 'shipped')
      AND o.order_purchase_timestamp >= TIMESTAMP '2017-01-01 00:00:00'
      AND o.order_purchase_timestamp <  TIMESTAMP '2018-09-01 00:00:00'
      AND NOT (o.order_status = 'delivered'
               AND o.order_delivered_customer_date IS NULL)
)
SELECT
    order_id,
    order_status,
    purchased_at,
    date_trunc('month', purchased_at)                   AS purchase_month,
    approved_at, handover_at, delivered_at, promised_date,
    seller_state, customer_state,
    seller_state || ' to ' || customer_state            AS lane,
    CASE WHEN seller_state = customer_state THEN 'within state'
         ELSE 'cross state' END                         AS lane_type,
    seller_city, customer_city, primary_seller_id, primary_category,
    n_items, n_sellers,
    CASE WHEN n_sellers > 1 THEN TRUE ELSE FALSE END    AS is_split_shipment,
    order_value, freight_value,
    round(freight_value + order_value, 2)               AS order_total,
    round(100.0 * freight_value / nullif(order_value, 0), 2) AS freight_pct_of_value,
    weight_kg, items_missing_weight, geo_fallback_used,
    -- great-circle distance, kilometres
    round(2 * 6371 * asin(sqrt(
        pow(sin(radians(cust_lat - sell_lat) / 2), 2) +
        cos(radians(sell_lat)) * cos(radians(cust_lat)) *
        pow(sin(radians(cust_lng - sell_lng) / 2), 2))), 1) AS distance_km,
    -- timing decomposition
    round(date_diff('hour', purchased_at, approved_at) / 24.0, 2)  AS approval_days,
    round(date_diff('hour', approved_at,  handover_at) / 24.0, 2)  AS dispatch_days,
    round(date_diff('hour', handover_at,  delivered_at) / 24.0, 2) AS transit_days,
    round(date_diff('hour', purchased_at, delivered_at) / 24.0, 2) AS total_days,
    date_diff('day', promised_date, delivered_at)                  AS days_vs_promise,
    CASE WHEN delivered_at > promised_date THEN TRUE
         WHEN delivered_at IS NULL THEN NULL ELSE FALSE END        AS is_late,
    round(date_diff('hour', shipping_limit_date, handover_at) / 24.0, 2) AS dispatch_vs_limit_days,
    CASE WHEN handover_at > shipping_limit_date THEN TRUE
         WHEN handover_at IS NULL THEN NULL ELSE FALSE END         AS seller_breached_limit,
    review_score,
    CASE WHEN review_score <= 2 THEN TRUE
         WHEN review_score IS NULL THEN NULL ELSE FALSE END        AS is_poor_review
FROM base;

-- ---------------------------------------------------------------------
-- 5. Timing quality flag.
--    Validation found three impossible or implausible timing patterns.
--    They are flagged rather than deleted, so that order-level money
--    totals stay complete and reconcile to source, while leg-level
--    timing analysis can exclude them explicitly:
--      a) transit_days < 0        : delivery recorded before carrier handover
--      b) dispatch_days < 0      : carrier handover recorded before payment approval
--      c) total_days > 200       : implausible end-to-end duration
-- ---------------------------------------------------------------------
ALTER TABLE fact_orders ADD COLUMN timing_anomaly BOOLEAN;

UPDATE fact_orders
SET timing_anomaly = (
        coalesce(transit_days, 0)  < 0
     OR coalesce(dispatch_days, 0) < 0
     OR coalesce(total_days, 0)    > 200
);
