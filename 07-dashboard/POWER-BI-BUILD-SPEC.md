# Power BI Build Specification

**Case 1: Reducing cost-to-serve in e-commerce logistics**
Audience: Head of Logistics. Secondary: CFO, Head of Customer Experience.
Tool: Power BI Desktop on Windows. Currency: BRL.

## 1. Tables to load

| Table | Source | Rows | Role |
|---|---|---|---|
| `fact_orders` | `03-data-clean/fact_orders.csv` | 97,300 | Fact. One row per order |
| `LaneDetail` | `03-data-clean/lane_detail.csv` | 100 | Lane dimension plus promise rules |
| `SellerBreach` | `03-data-clean/seller_breach.csv` | 100 | Top breaching sellers, unrelated table |
| `PromiseCurve` | `03-data-clean/promise_curve.csv` | 13 | Uniform-cut trade-off curve |
| `DimDate` | DAX `CALENDAR` | ~610 | Date dimension |

## 2. Model

```
DimDate[Date]        1 --> *  fact_orders[purchase_date]
LaneDetail[lane]     1 --> *  fact_orders[lane]
SellerBreach                  no relationship, used standalone on page 3
ServiceTarget                 what-if parameter table, no relationship
```

Calculated column on `fact_orders`:
`purchase_date = DATEVALUE(fact_orders[purchased_at])`

`SellerBreach` is deliberately left unrelated. It covers 100 of 2,941
sellers, so a relationship would silently filter the fact table down to
those sellers on every page.

## 3. What-if parameter

Modelling tab, New parameter, Numeric range:
name `Service Target`, minimum 90, maximum 95, increment 5, default 95.
This creates the `ServiceTarget` table and a slicer.

## 4. Measures

Load from `07-dashboard/measures.dax`. Core set:

- Orders, Delivered Orders, Item Value, Freight, Freight % of Value,
  Avg Freight per Order
- Late Orders, Late Rate, Avg Days to Deliver, Avg Distance
- Avg Review, Poor Reviews, Poor Review Rate
- Dispatch Breaches, Breach Rate
- Avg Promise Days, Promise Padding Days
- Late Rate at p90, Late Rate at p95, Late Rate at Target
- Promise at Target, Promise Change at Target
- Late Orders Avoided a Year, Poor Reviews Avoided a Year

## 5. Pages

### Page 1: Service and cost overview
1. KPI cards, one row: Orders, Freight % of Value, Late Rate,
   Avg Days to Deliver, Avg Review, Promise Padding Days.
2. Line chart: Late Rate by month, with a constant line at the period
   average. Title: "Lateness is seasonal: plan against March, not the average".
3. Combo chart: Freight % of Value (columns) and Avg Days to Deliver
   (line) by month.
4. Bar chart: Late Rate by distance band.
5. Text box: the one-line headline. "Freight is 16.6 percent of item
   value and largely explained by distance and weight. The value is in
   reliability, not in freight recovery."

### Page 2: Lanes and the delivery promise
1. Slicer: `Service Target` what-if.
2. KPI cards: Late Rate, Late Rate at Target, Late Orders Avoided a Year,
   Promise Change at Target.
3. Scatter: lanes, x = Avg Distance, y = Late Rate, size = Orders,
   colour = Freight above model. Highlights SP to RJ.
4. Table: lane, orders, promise today, promise at target, change,
   late today, late at target. Conditionally formatted on change.
5. Line chart from `PromiseCurve`: days removed against resulting late
   rate. Title: "Why the padding cannot be cut uniformly".

### Page 3: Seller dispatch enforcement
1. KPI cards: Dispatch Breaches, Breach Rate, Late Rate when breached,
   Late Rate when met.
2. Bar chart from `SellerBreach`: top 20 sellers by breaches.
3. Table: seller ref, orders, breaches, breach rate, late rate,
   avg review.
4. Text box: the top 100 sellers carry 54.3 percent of all breaches.

### Page 4: Method and limitations
Text content only, lifted from the cleaning log and the Notes sheet of
the Excel model: source and licence, grain, the nine limitations, the
split-shipment artifact, and the statement that freight is charged
freight and not carrier cost.

## 6. Formatting

- Theme: single accent colour, grey secondary. No default multicolour.
- Every chart title states the finding, not the field names.
- Number formats: BRL with thousands separators, rates as one decimal
  percent, days as one decimal.
- Every page footer: source, period, refresh date.

## 7. Build order on screen

1. Load the four CSVs, one at a time, via Home, Get data, Text/CSV.
2. Check `fact_orders` column types, especially the date and boolean
   columns, in Power Query before Close and Apply.
3. Add the `purchase_date` calculated column.
4. Create `DimDate`, mark as date table, build the two relationships.
5. Create the what-if parameter.
6. Paste the measures from `measures.dax`, one at a time.
7. Build pages 1 to 4 in order.
8. Verify three numbers against the Excel model: Late Rate 8.1 percent,
   Freight % of Value 16.6 percent, Avg Days to Deliver 12.5.
9. Save as `07-dashboard/cost-to-serve-dashboard.pbix`, then export page
   screenshots to the same folder for the README.

## 8. Build log, 24 November 2026

**Done in Power BI Desktop and saved to `cost-to-serve-dashboard.pbix`:**

- Four tables loaded from `03-data-clean`: `fact_orders` (97,300 rows,
  39 columns), `LaneDetail` (100), `SellerBreach` (100),
  `PromiseCurve` (13).
- `fact_orders` loaded through an explicit M script rather than the
  generated one, so every column type is declared rather than guessed.
  The script is in the query's Advanced Editor and adds the
  `purchase_date` column.
- Relationship created: `fact_orders[lane]` many-to-one to
  `LaneDetail[lane]`, single direction, active.
- Measures created: `Total Orders`, `Delivered Orders`, `Late Rate`, and the
  eleven listed below. The order count measure is named **Total Orders**,
  not `Orders`: a measure called `Orders` cannot be found with the Data
  pane search, because the search matches the table name `fact_orders`
  and expands every field instead.

**Two deviations from the plan above, both deliberate:**

1. **No what-if parameter.** The service target is expressed as two
   explicit measures, `Late Rate at p90` and `Late Rate at p95`, shown
   side by side. Fewer moving parts, no parameter table, and the
   comparison is visible at once rather than behind a slider.
2. **Measures are self-contained.** Each one repeats its own base
   calculation instead of referencing another measure. Referencing
   proved brittle while the model was still loading, and self-contained
   measures are immune to creation order.

**Still to create (self-contained forms, paste into the formula bar):**

```
Freight % of Value = DIVIDE(SUM('fact_orders'[freight_value]), SUM('fact_orders'[order_value]))

Poor Review Rate = DIVIDE(CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_poor_review] = TRUE()), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[review_score])))

Breach Rate = DIVIDE(CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[seller_breached_limit] = TRUE()), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[seller_breached_limit])))

Late Rate when Breached = CALCULATE(DIVIDE(CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_late] = TRUE()), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at]))), 'fact_orders'[seller_breached_limit] = TRUE())

Late Rate when Met = CALCULATE(DIVIDE(CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_late] = TRUE()), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at]))), 'fact_orders'[seller_breached_limit] = FALSE())

Avg Promise Days = AVERAGEX('fact_orders', DATEDIFF('fact_orders'[purchased_at], 'fact_orders'[promised_date], DAY))

Promise Padding Days = AVERAGEX('fact_orders', DATEDIFF('fact_orders'[purchased_at], 'fact_orders'[promised_date], DAY)) - AVERAGE('fact_orders'[total_days])

Late Rate at p90 = DIVIDE(COUNTROWS(FILTER('fact_orders', 'fact_orders'[total_days] > RELATED('LaneDetail'[p90]))), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at])))

Late Rate at p95 = DIVIDE(COUNTROWS(FILTER('fact_orders', 'fact_orders'[total_days] > RELATED('LaneDetail'[p95]))), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at])))

Late Orders Avoided a Year at p95 = (DIVIDE(CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_late] = TRUE()), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at]))) - DIVIDE(COUNTROWS(FILTER('fact_orders', 'fact_orders'[total_days] > RELATED('LaneDetail'[p95]))), CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at])))) * CALCULATE(COUNTROWS('fact_orders'), NOT ISBLANK('fact_orders'[delivered_at])) * 12 / 20
```

**How to create one:** Home, New measure, then click into the formula
bar, select all, delete, and paste the line. The formula bar needs the
click before it will accept input.

**Verification targets once the measures exist.** These three numbers
must match the Excel model, and if they do not, the model is wrong:
Late Rate 8.1 percent, Freight % of Value 16.6 percent, Avg of
`total_days` 12.5 days.
