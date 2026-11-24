# Stage 2: Data Dictionary

**Source:** Brazilian E-Commerce Public Dataset by Olist (`olistbr/brazilian-ecommerce`), Kaggle.
**Licence:** CC BY-NC-SA 4.0. Non-commercial use with attribution, share-alike.
**Retrieved:** 24 November 2026.
**Coverage:** 4 September 2016 to 17 October 2018.
**Anonymisation note:** seller and customer identifiers are hashed by the
publisher, company names are replaced with Game of Thrones house names in
review text, and postcodes are truncated to the first five digits. All
figures are in Brazilian reais (BRL).

## Tables

| Table | Rows | Grain | Primary key | Role in this case |
|---|---|---|---|---|
| `orders` | 99,441 | one row per order | `order_id` (unique) | Spine. Status and the four timestamps |
| `order_items` | 112,650 | one row per item within an order | `order_id` + `order_item_id` | Price, freight, seller, product |
| `customers` | 99,441 | one row per order-scoped customer id | `customer_id` (unique) | Destination state and postcode |
| `sellers` | 3,095 | one row per seller | `seller_id` (unique) | Origin state and postcode |
| `products` | 32,951 | one row per product | `product_id` (unique) | Category, weight, dimensions |
| `reviews` | 99,224 | roughly one row per order | `review_id` (NOT unique) | Review score, the damage measure |
| `payments` | 103,886 | one row per payment instalment line | `order_id` + `payment_sequential` | Payment type and value |
| `geolocation` | 1,000,163 | many rows per postcode prefix | none | Coordinates for distance |
| `category_tr` | 71 | one row per category | `product_category_name` | Portuguese to English names |

## Key columns used in this case

| Column | Table | Type | Notes |
|---|---|---|---|
| `order_purchase_timestamp` | orders | timestamp | Complete, no nulls. Defines the period filter |
| `order_approved_at` | orders | timestamp | 160 nulls |
| `order_delivered_carrier_date` | orders | timestamp | 1,783 nulls. Seller to carrier handover |
| `order_delivered_customer_date` | orders | timestamp | 2,965 nulls, of which 8 are status delivered |
| `order_estimated_delivery_date` | orders | date | Complete. The promise made to the customer |
| `order_status` | orders | text | 8 values, 97.02 percent delivered |
| `price` | order_items | numeric | Median 74.99, max 6,735.00 |
| `freight_value` | order_items | numeric | Median 16.26, max 409.68, 383 items at zero |
| `shipping_limit_date` | order_items | timestamp | Seller dispatch deadline, enables SLA work |
| `product_weight_g` | products | numeric | 2 nulls, 4 at zero |
| `review_score` | reviews | integer 1 to 5 | 57.78 percent are 5, 11.51 percent are 1 |

## Relationship map

```
orders (order_id)
  |-- 1:1  customers (customer_id)        destination state and postcode
  |-- 1:N  order_items (order_id)         price, freight, seller, product
  |          |-- N:1 sellers (seller_id)  origin state and postcode
  |          |-- N:1 products (product_id) category, weight, dimensions
  |                    |-- N:1 category_tr
  |-- 1:N  payments (order_id)
  |-- 1:N  reviews (order_id)             usually 1, sometimes more

sellers.seller_zip_code_prefix   --> geolocation (centroid per prefix)
customers.customer_zip_code_prefix --> geolocation (centroid per prefix)
```

## Referential integrity checks

| Check | Result | Treatment |
|---|---|---|
| Items without a parent order | 0 | None needed |
| Orders without a customer row | 0 | None needed |
| Items with a missing seller row | 0 | None needed |
| Items with a missing product row | 0 | None needed |
| Orders with no items | 775 | Excluded, cannot compute freight |
| Orders with no review | 768 | Retained, review score left null |
| Customer postcodes absent from geolocation | 157 | State centroid fallback |
| Seller postcodes absent from geolocation | 7 | State centroid fallback |

## Data quality findings

1. **`review_id` is not unique.** 99,224 rows hold 98,410 distinct review
   ids and 98,673 distinct order ids. Reviews must be de-duplicated to one
   per order before joining, or order counts will inflate.
2. **`geolocation` is one-to-many on postcode prefix.** 1,000,163 rows for
   19,015 prefixes. Joining it raw multiplies the fact table. It must be
   reduced to one centroid per prefix first.
3. **Eight orders are marked delivered with no delivery date.** Excluded
   from timing analysis, since the outcome is unknown.
4. **The delivery promise looks padded, not estimated.** Across 96,470
   delivered orders, actual delivery runs on average 11.88 days earlier
   than promised, with 8.11 percent still late. A promise that is both
   heavily padded and missed one time in twelve is a finding in its own
   right, not a data error.
5. **383 items carry zero freight.** Flagged rather than dropped, since
   free shipping is a commercial choice, not a defect.
6. **610 products have no category** and 2 have no weight or dimensions.
   Bucketed as "unknown" rather than dropped, so order totals stay intact.
7. **2016 is a ramp-up period:** 329 orders, against 45,101 in 2017 and
   54,011 in 2018. Excluded by the scope filter.
8. **The final weeks are right-censored.** Data ends 17 October 2018, so
   orders purchased close to that date may not yet show delivery. Scope
   therefore stops at 31 August 2018.
9. **Repeat purchasing is near-absent:** 96,096 unique customers for
   99,441 orders, so about 3.1 percent of customers order more than once.
   This rules out a churn-based damage model, as recorded in the brief.

## Known biases

- **Marketplace, not retailer.** Fulfilment is by thousands of small
  sellers, so dispatch variance is wider than a single-warehouse operation
  would show. Conclusions transfer to marketplace and 3PL contexts more
  readily than to own-warehouse retail.
- **Charged freight, not carrier cost.** As recorded in the brief, this is
  a cost-to-serve proxy.
- **Review selection.** 99.2 percent of orders have a review, which is
  unusually high and suggests prompted collection, so the score
  distribution is less self-selected than typical review data but may be
  shaped by the prompt timing.
- **Geographic concentration.** Brazilian volume is heavily weighted to
  the south east, so lanes serving the north will have thin samples.
  Minimum volume thresholds are required before ranking any lane.
