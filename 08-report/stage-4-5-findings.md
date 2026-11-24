# Stages 4 and 5: Exploration and Analysis Findings

**Case 1: Reducing cost-to-serve in e-commerce logistics**
Base table: 97,300 orders, January 2017 to August 2018. All money in BRL.
Scripts: `04-sql/02_exploration.sql`, `05-notebooks/stage5_tests.py`.

## Headline

The money in this case is not in what freight costs. It is in what
lateness destroys, and lateness is driven by the seller's dispatch leg
rather than by distance.

## 1. The cost picture

| Measure | Value |
|---|---|
| Freight charged | 2,218,021 on 13,329,378 of item value, 16.64 percent |
| Median freight share of a single order | 22.4 percent |
| 90th percentile | 62.3 percent |
| Orders where freight exceeds half the item value | 15,435, which is 15.9 percent |

The aggregate share (16.64 percent) is value-weighted and therefore
flattering. Order by order the median burden is 22.4 percent, because
small-value orders carry disproportionate freight.

Cost rises monotonically with distance, as expected:

| Distance band | Orders | Avg freight | Freight share | Avg days | Late | Avg review |
|---|---:|---:|---:|---:|---:|---:|
| under 50 km | 11,866 | 13.12 | 11.9% | 6.1 | 6.45% | 4.261 |
| 50 to 200 km | 12,978 | 15.65 | 12.4% | 8.0 | 6.10% | 4.275 |
| 200 to 600 km | 38,544 | 22.06 | 16.5% | 12.4 | 7.54% | 4.119 |
| 600 to 1500 km | 24,951 | 26.14 | 17.8% | 15.4 | 8.85% | 4.083 |
| over 1500 km | 8,961 | 39.82 | 22.6% | 20.5 | 12.84% | 3.963 |

## 2. Freight expected against actual, by lane

OLS of freight on log distance, log weight and item count explains 47.0
percent of freight variation (n = 97,300). Residuals were averaged by
lane, restricted to the 49 lanes with at least 200 orders, and p-values
adjusted with Benjamini-Hochberg. 31 of the 49 lanes differ significantly
from the model.

Highest excess freight, meaning charged above what distance, weight and
item count explain:

| Lane | Orders | Excess per order | Excess total | Late |
|---|---:|---:|---:|---:|
| SP to MA | 502 | 12.28 | 6,167 | 21.06% |
| SP to PB | 345 | 17.55 | 6,055 | 11.01% |
| SP to PE | 1,153 | 4.12 | 4,755 | 10.83% |
| SP to CE | 997 | 4.73 | 4,711 | 15.32% |
| SP to PI | 335 | 10.88 | 3,645 | 18.29% |

**This is the finding that reorders the recommendations.** Total excess
freight across the ten worst lanes is roughly 39,700, which is 1.8
percent of freight spend and 0.3 percent of item value. Every one of
those lanes runs from Sao Paulo to the north east, and all are low
volume. Renegotiating them is real but small money, and it is the lever
the brief originally expected to matter most.

Short-haul lanes are charged below model expectation, with SP to SP at
45,758 below, consistent with a fixed handling cost spread over short
distances.

## 3. H₀1: on-time delivery and structural factors

Rejected. Logistic regression on lateness.

| Factor | Odds ratio | 95% CI | p |
|---|---:|---|---:|
| Seller missed dispatch deadline | **4.709** | 4.451 to 4.983 | <0.001 |
| Cross-state lane | 1.361 | 1.259 to 1.471 | <0.001 |
| Distance, per log unit | 1.085 | 1.055 to 1.115 | <0.001 |
| Weight, per log unit | 1.051 | 1.019 to 1.084 | 0.002 |
| Items in order | 0.887 | 0.841 to 0.935 | <0.001 |

Pseudo R squared rises from 0.0095 to 0.0546 when the dispatch breach is
added, a near sixfold improvement in explanatory power. A seller who
misses the dispatch deadline makes a late delivery about 4.7 times more
likely, while doubling the distance barely moves the odds.

This matters because the two facts look contradictory at first. The
carrier leg consumes 9.37 of the 12.59 average days (74.4 percent) and
the seller leg only 2.82 days (22.4 percent). The seller leg is the
smaller part of the clock and the larger part of the failure. Time spent
is not the same as time lost.

| Dispatch deadline | Orders | Avg days vs limit | Late | Avg review |
|---|---:|---:|---:|---:|
| Met | 88,597 | -4.00 | 6.43% | 4.178 |
| Missed | 8,702 | +2.95 | 24.41% | 3.677 |

## 4. H₀2: review score and lateness

Rejected, and this is the load-bearing result of the case.

- Spearman rho = -0.177, p < 0.001, n = 95,560
- Kruskal-Wallis H = 10,333.8 across six lateness bands, p < 0.001

| Delivery against promise | Orders | Avg review | 1 or 2 star | 5 star |
|---|---:|---:|---:|---:|
| 10 or more days early | 61,270 | 4.325 | 8.86% | 63.98% |
| 3 to 10 days early | 21,930 | 4.247 | 9.72% | 59.75% |
| On time, 0 to 3 days early | 5,982 | 4.112 | 11.47% | 54.11% |
| Up to 3 days late | 1,851 | 3.291 | 32.14% | 33.17% |
| 3 to 10 days late | 2,504 | 1.971 | 71.49% | 11.86% |
| Over 10 days late | 2,023 | 1.709 | 78.84% | 7.17% |

Poor review rate is 9.24 percent when delivery is on time or early and
62.40 percent when it is late: a gap of 53.16 points, 95 percent CI
[51.95, 54.36], a relative risk of 6.75. Within the first 15 late days
each additional day costs 0.160 review points.

The damage is a cliff, not a slope. Arriving one day late nearly triples
the poor review rate (11.47 to 32.14 percent). There is no grace period.

## 5. H₀3: is the delivery promise unbiased?

Rejected. The promise is not an estimate, it is padding.

| Measure | Value |
|---|---|
| Mean actual minus promised | -11.81 days (early) |
| 95 percent CI | [-11.87, -11.74] |
| Median | -12 days |
| Mean promised window | 23.66 days |
| Mean actual delivery | 12.54 days |
| Orders arriving over 20 days early | 13.76 percent |
| Still late | 8.13 percent |

The promise is roughly double the actual delivery time, and is still
missed one time in twelve. The company is paying twice: customers wait
for a date they did not need to wait for, and the business still absorbs
the review damage when the padded date is missed.

## 6. A data artifact found, not a finding to act on

Split shipments (1,274 orders containing items from more than one seller)
show an impossible pattern:

| Measure | Split orders | Single-seller orders |
|---|---:|---:|
| Late | 1.42% | 8.22% |
| Mean total days | 9.14 | 12.58 |
| Mean review score | 2.860 | 4.150 |
| Poor review rate | 47.22% | 12.95% |

Split orders are recorded as faster and almost never late, yet are rated
far worse, with a poor review rate nearly four times higher. That
combination is not operationally plausible. The likely cause is that
`order_delivered_customer_date` records the first shipment to arrive, not
the last, so a split order is marked delivered while the customer is
still waiting for the rest and rates the order accordingly.

Consequences, applied from here on:

1. The split shipment coefficient in the lateness model (odds ratio 0.21)
   is an artifact and must not be read as split shipments being more
   reliable. It is reported and discounted, not used.
2. Split shipments are excluded from delivery timing conclusions.
3. Their review scores are retained, since those are genuine customer
   reactions, and treated as corroborating evidence that incomplete
   delivery damages satisfaction.
4. This is stated plainly in the final report. It is 1.3 percent of
   orders, so it does not threaten the main results.

## 7. Service level over time, with a seasonal warning

Lateness is not stable. It spikes to 14.17 percent in November 2017,
15.85 percent in February 2018 and 20.96 percent in March 2018, against
a floor of 1.35 percent in June 2018. Average delivery time improved
across the period, from 12.65 days in January 2017 to 7.73 days in
August 2018, while freight share rose from 14.23 to 17.46 percent.

Any recommendation must therefore be sized against peak-period lateness,
not the 8 percent annual average, or it will under-provision exactly when
the damage is worst.

## 8. Where this leaves the four levers

| Lever | Evidence | Provisional rank |
|---|---|---|
| Enforce seller dispatch deadlines | Odds ratio 4.71, affects 8,702 orders | 1 |
| Recalibrate the delivery promise | 11.8 days of padding, costs nothing to change | 2 |
| Re-route long north-east lanes | Real but small, about 39,700 of excess freight | 3 |
| Renegotiate freight on those lanes | Same lanes, same small money, harder to execute | 4 |

Stage 6 converts ranks 1 and 2 into money using the review damage
relationship, and sizes rank 3 directly from the residual model.
