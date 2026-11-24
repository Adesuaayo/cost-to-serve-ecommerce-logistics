# Stage 3: Cleaning Log

**Case 1: Reducing cost-to-serve in e-commerce logistics**
Run date: 24 November 2026. Engine: DuckDB.
Script: `04-sql/01_build_clean_base.sql`, executed by `05-notebooks/run_clean.py`.
Output: `03-data-clean/fact_orders.parquet` and `.csv`, 97,300 rows, 38 columns.

Every rule below is reproducible by re-running the script. No row was
edited by hand.

## 1. Row accounting, orders

| Step | Rule | Rows affected | Running total |
|---|---|---:|---:|
| Start | Raw `orders` table | | 99,441 |
| Exclude | Status not in (delivered, shipped), so no delivery outcome exists | 1,856 | 97,585 |
| Exclude | Order has no items, so freight cannot be computed | 1 | 97,584 |
| Exclude | Purchased before 1 Jan 2017 or on/after 1 Sep 2018, per scope | 276 | 97,308 |
| Exclude | Status delivered but delivery date missing, outcome unknown | 8 | 97,300 |
| **Final** | **`fact_orders`** | | **97,300** |

Coverage retained: 97.8 percent of raw orders.

## 2. Supporting table rules

| Table | Rule | Rows affected | Result |
|---|---|---:|---|
| `geolocation` | Discard coordinates outside Brazil's bounding box (lat -34.0 to 5.3, lng -74.0 to -34.8) | 47 | Bad points removed before averaging |
| `geolocation` | Reduce to one median centroid per postcode prefix | 1,000,163 to 19,010 | Prevents fact-table multiplication on join |
| `reviews` | Keep the most recent review per order, since `review_id` is not unique | 551 removed | 98,673 rows, one per order |
| `reviews` | Reject scores outside 1 to 5 | 0 | No invalid scores exist |
| `order_items` | Aggregate 112,650 items to order grain | to 98,666 | Freight summed, dominant seller and category assigned |

## 3. Derived fields and the rules behind them

| Field | Rule |
|---|---|
| `lane` | Dominant seller's state to customer's state. The dominant seller is the one with the highest item value in the order |
| `is_split_shipment` | True when an order contains items from more than one seller (1,278 orders in scope) |
| `distance_km` | Great-circle distance between seller and customer postcode centroids |
| `freight_pct_of_value` | Freight divided by item value, as a percentage |
| `approval_days` | Purchase to payment approval |
| `dispatch_days` | Payment approval to carrier handover, the seller's leg |
| `transit_days` | Carrier handover to customer delivery, the carrier's leg |
| `total_days` | Purchase to customer delivery |
| `days_vs_promise` | Delivery date minus promised date. Positive means late |
| `seller_breached_limit` | Carrier handover later than `shipping_limit_date` (8,702 orders) |

## 4. Anomalies flagged, not deleted

Order-level money totals must reconcile to source, so no row was dropped
for a timing problem. Instead `timing_anomaly` marks 1,261 orders
(1.3 percent), to be excluded explicitly from leg-level timing analysis.

| Pattern | Rows | Interpretation |
|---|---:|---|
| `transit_days` negative | 18 | Delivery recorded before carrier handover, impossible |
| `dispatch_days` negative | 1,241 | Handover recorded before payment approval, likely a late-written approval timestamp |
| `total_days` over 200 days | 2 | Implausible duration, retained as outliers |

## 5. Other conditions retained and flagged

| Condition | Rows | Treatment |
|---|---:|---|
| Postcode absent from geolocation, state centroid used | 484 | `geo_fallback_used` true. Distance is coarser for these |
| Order contains an item with missing or zero weight | 22 | `items_missing_weight` greater than zero |
| Zero freight charged | 338 | Retained. Free shipping is a commercial choice, not a defect |
| Product category unknown | 1,378 | Bucketed as `unknown` so order totals stay whole |
| No review submitted | 716 | `review_score` null. Excluded from review analysis only |
| Status shipped, not yet delivered at data cut-off | 1,097 | `is_late` null. Retained for in-flight volume, excluded from delivery timing |

## 6. Validation results

| Check | Result |
|---|---|
| Duplicate `order_id` in `fact_orders` | 0 |
| Null `lane` | 0 |
| Null or negative `distance_km` | 0 |
| Distance above 5,000 km | 0 |
| Negative `freight_value` | 0 |
| Order value at or below zero | 0 |
| Negative `total_days` | 0 |
| Item value total, fact against raw, in-scope orders | 13,329,377.94 BRL both sides, exact match |
| Freight total, fact against raw, in-scope orders | 2,218,020.78 BRL both sides, exact match |

Both money columns reconcile to the source to the cent, which is the
check that matters most: the cleaning changed the row count and the grain,
and changed no money.

## 7. Shape of the analysis base table

| Measure | Value |
|---|---|
| Orders | 97,300 |
| Period | 5 January 2017 to 29 August 2018 |
| Item value (GMV) | 13,329,378 BRL |
| Freight charged | 2,218,021 BRL |
| **Freight as a share of item value** | **16.64 percent** |
| Average days from purchase to delivery | 12.54 |
| Average seller to customer distance | 603 km |
| Late against promise | 8.04 percent |
| Average review score | 4.134 |
| Distinct lanes | 414 |
| Distinct dominant sellers | 2,941 |
| Distinct product categories | 74 |
| Orders where the seller missed the dispatch deadline | 8,702 (8.9 percent) |
