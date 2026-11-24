-- =====================================================================
-- Case 1: Stage 4 exploration
-- Input : 03-data-clean/fact_orders.parquet (view named f by the runner)
-- Each query answers one question from section 6 of the brief.
-- Timing queries exclude timing_anomaly rows, per the cleaning log.
-- =====================================================================

-- Q1. Monthly shape: volume, value, freight burden, service level
-- name: monthly_trend
SELECT purchase_month::DATE AS month, count(*) AS orders,
       round(sum(order_value), 0) AS gmv,
       round(100.0 * sum(freight_value) / sum(order_value), 2) AS freight_pct,
       round(avg(total_days), 2) AS avg_days,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late
FROM f GROUP BY 1 ORDER BY 1;

-- Q2. How concentrated is the freight burden across orders?
-- name: freight_share_percentiles
SELECT round(quantile_cont(freight_pct_of_value, 0.10), 1) AS p10,
       round(quantile_cont(freight_pct_of_value, 0.25), 1) AS p25,
       round(quantile_cont(freight_pct_of_value, 0.50), 1) AS p50,
       round(quantile_cont(freight_pct_of_value, 0.75), 1) AS p75,
       round(quantile_cont(freight_pct_of_value, 0.90), 1) AS p90,
       round(quantile_cont(freight_pct_of_value, 0.99), 1) AS p99,
       sum(CASE WHEN freight_pct_of_value > 50 THEN 1 ELSE 0 END) AS orders_over_50pct
FROM f;

-- Q3. Does crossing a state border change cost and service?
-- name: by_lane_type
SELECT lane_type, count(*) AS orders,
       round(avg(distance_km), 0) AS avg_km,
       round(avg(freight_value), 2) AS avg_freight,
       round(100.0 * sum(freight_value) / sum(order_value), 2) AS freight_pct,
       round(avg(total_days), 2) AS avg_days,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late
FROM f GROUP BY 1 ORDER BY 2 DESC;

-- Q4. Where is time lost: seller leg, carrier leg, or approval?
-- name: time_by_leg
SELECT round(avg(approval_days), 2) AS approval_days,
       round(avg(dispatch_days), 2) AS seller_dispatch_days,
       round(avg(transit_days), 2) AS carrier_transit_days,
       round(avg(total_days), 2) AS total_days,
       round(100.0 * avg(dispatch_days) / avg(total_days), 1) AS pct_seller_leg,
       round(100.0 * avg(transit_days) / avg(total_days), 1) AS pct_carrier_leg
FROM f WHERE NOT timing_anomaly AND delivered_at IS NOT NULL;

-- Q5. Lateness by distance band
-- name: by_distance_band
SELECT CASE WHEN distance_km <   50 THEN '1. under 50km'
            WHEN distance_km <  200 THEN '2. 50 to 200km'
            WHEN distance_km <  600 THEN '3. 200 to 600km'
            WHEN distance_km < 1500 THEN '4. 600 to 1500km'
            ELSE '5. over 1500km' END AS distance_band,
       count(*) AS orders, round(avg(freight_value), 2) AS avg_freight,
       round(100.0 * sum(freight_value) / sum(order_value), 2) AS freight_pct,
       round(avg(total_days), 2) AS avg_days,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late,
       round(avg(review_score), 3) AS avg_review
FROM f GROUP BY 1 ORDER BY 1;

-- Q6. Do split shipments behave differently?
-- name: by_split
SELECT is_split_shipment, count(*) AS orders,
       round(avg(n_items), 2) AS avg_items,
       round(avg(freight_value), 2) AS avg_freight,
       round(avg(total_days), 2) AS avg_days,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late,
       round(avg(review_score), 3) AS avg_review
FROM f GROUP BY 1;

-- Q7. The damage link: review score against lateness
-- name: review_by_lateness
SELECT CASE WHEN days_vs_promise <= -10 THEN '1. 10+ days early'
            WHEN days_vs_promise <   -3 THEN '2. 3 to 10 days early'
            WHEN days_vs_promise <=   0 THEN '3. on time, 0 to 3 early'
            WHEN days_vs_promise <=   3 THEN '4. up to 3 days late'
            WHEN days_vs_promise <=  10 THEN '5. 3 to 10 days late'
            ELSE '6. over 10 days late' END AS lateness_band,
       count(*) AS orders, round(avg(review_score), 3) AS avg_review,
       round(100.0 * avg(CASE WHEN is_poor_review THEN 1.0 ELSE 0 END), 2) AS pct_1_or_2_star,
       round(100.0 * avg(CASE WHEN review_score = 5 THEN 1.0 ELSE 0 END), 2) AS pct_5_star
FROM f WHERE review_score IS NOT NULL AND days_vs_promise IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- Q8. Seller dispatch deadline breaches, and what follows them
-- name: by_sla_breach
SELECT seller_breached_limit, count(*) AS orders,
       round(avg(dispatch_vs_limit_days), 2) AS avg_days_vs_limit,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late,
       round(avg(review_score), 3) AS avg_review
FROM f WHERE seller_breached_limit IS NOT NULL GROUP BY 1 ORDER BY 1;

-- Q9. Promise padding: how far ahead of promise do orders arrive?
-- name: promise_padding
SELECT round(avg(days_vs_promise), 2) AS avg_days_vs_promise,
       round(quantile_cont(days_vs_promise, 0.50), 1) AS median_days_vs_promise,
       round(quantile_cont(days_vs_promise, 0.90), 1) AS p90,
       round(100.0 * avg(CASE WHEN days_vs_promise < -20 THEN 1.0 ELSE 0 END), 2) AS pct_over_20_days_early,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late,
       round(avg(date_diff('day', purchased_at, promised_date)), 2) AS avg_promised_window_days,
       round(avg(total_days), 2) AS avg_actual_days
FROM f WHERE delivered_at IS NOT NULL;

-- Q10. Worst lanes on service, volume threshold applied
-- name: worst_lanes
SELECT lane, count(*) AS orders, round(avg(distance_km), 0) AS avg_km,
       round(avg(freight_value), 2) AS avg_freight,
       round(100.0 * sum(freight_value) / sum(order_value), 2) AS freight_pct,
       round(avg(total_days), 2) AS avg_days,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late,
       round(avg(review_score), 3) AS avg_review
FROM f GROUP BY 1 HAVING count(*) >= 200
ORDER BY pct_late DESC LIMIT 12;

-- Q11. Biggest lanes by volume, for context against the worst list
-- name: biggest_lanes
SELECT lane, count(*) AS orders, round(sum(freight_value), 0) AS freight_total,
       round(100.0 * sum(freight_value) / sum(order_value), 2) AS freight_pct,
       round(100.0 * avg(CASE WHEN is_late THEN 1.0 ELSE 0 END), 2) AS pct_late
FROM f GROUP BY 1 ORDER BY orders DESC LIMIT 10;
