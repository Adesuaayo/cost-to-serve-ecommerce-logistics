# Stage 6: Quantification

**Case 1: Reducing cost-to-serve in e-commerce logistics**
All money in BRL. Base period: 97,300 orders over 20 months
(January 2017 to August 2018). Annualised figures divide by 20 and
multiply by 12.

| Anchor | Value |
|---|---|
| Item value (GMV), period | 13,329,378 |
| Item value, annualised | 7,997,627 |
| Freight charged, period | 2,218,021 (16.64 percent of item value) |
| Delivered orders measured | 96,203 |
| Late against promise | 8.13 percent |

## Headline: this is a service case, not a cost-savings case

Freight consumes 16.64 percent of item value, but 47 percent of its
variation is explained by distance, weight and item count alone, and the
lanes that charge above that model account for 2.17 percent of freight
spend. There is no large overcharge to recover here. The value available
is in reliability and in the accuracy of the promise, and the analysis is
reported that way rather than dressed up as a saving.

## Lever 2 first, because it is the largest: recalibrate the promise

### The naive version of this recommendation is wrong

The promise is padded by 11.81 days on average, which invites the
conclusion that the padding is waste. It is not. The padding is covering
lane variance, and cutting it uniformly destroys service fast:

| Days cut from the promise, every lane | Resulting late rate |
|---:|---:|
| 0 (today) | 8.13% |
| 1 | 9.65% |
| 2 | 11.26% |
| 3 | 13.06% |
| 4 | 15.05% |
| 5 | 17.36% |
| 6 | 21.12% |
| 10 | 35.97% |

Three days off the promise nearly doubles lateness. Anyone recommending
"reduce the padding" without this curve would damage the business.

### The version that works: set the promise per lane

The padding is uniform while the lanes are not. Setting each lane's
promise at a percentile of its own observed delivery time produces a
genuine trade-off curve, measured across 100 lanes covering 96.8 percent
of orders:

| Promise rule | Avg promise | Change | Lanes shortened | Lanes lengthened | Late rate |
|---|---:|---:|---:|---:|---:|
| Today, blanket pad | 23.40 days | | | | 8.13% |
| Each lane at its 90th percentile | 21.14 days | -2.26 | 78 | 22 | 9.99% |
| Each lane at its 95th percentile | 26.31 days | +2.91 | 42 | 58 | 5.04% |

Two usable options, and they are a choice, not a calculation:

- **The 95th percentile rule cuts late orders by 38 percent** (8.13 to
  5.04 percent, 2,978 fewer late orders over the 20-month
  period and about 1,787 a year) at the cost of
  2.91 days added to the average promise.
- **The 90th percentile rule removes 2.26 days from the average promise**
  (about 130,500 promised-wait days a year across in-scope orders) and
  costs 1.86 points of lateness.

Either way the blanket pad goes, 42 to 78 lanes get a shorter promise
than today, and the business picks a service target deliberately instead
of inheriting one.

### Where the mispricing of time is concentrated

Most over-padded lanes, which can be promised sooner at no service cost:

| Lane | Orders | Promise today | Promise at p95 | Change | Late today |
|---|---:|---:|---:|---:|---:|
| RS to MG | 187 | 30.3 | 20.3 | -10.0 | 2.7% |
| RS to SP | 663 | 28.0 | 18.9 | -9.1 | 2.3% |
| DF to MG | 101 | 26.3 | 18.4 | -7.9 | 1.0% |
| MG to PR | 362 | 27.8 | 21.8 | -6.0 | 1.9% |

Most under-padded lanes, where the promise is a fiction:

| Lane | Orders | Promise today | Promise at p95 | Change | Late today |
|---|---:|---:|---:|---:|---:|
| **SP to RJ** | **8,138** | **26.3** | **40.0** | **+13.6** | **15.5%** |
| SP to AL | 255 | 32.3 | 45.9 | +13.6 | 26.3% |
| SP to CE | 966 | 31.3 | 43.7 | +12.4 | 15.3% |
| PR to RJ | 967 | 29.6 | 42.4 | +12.8 | 14.0% |

SP to RJ is the single most important line in this case: 8,138 orders,
the second largest lane in the business, 15.5 percent late, and needing
13.6 more days than it currently promises. It is not an exotic long-haul
route, it is Sao Paulo to Rio de Janeiro.

## Lever 1: enforce seller dispatch deadlines

8,581 orders breached the dispatch deadline and ran 24.75 percent late,
against 6.50 percent for orders dispatched on time. The excess is
**1,566 late orders attributable to dispatch breach**.

Enforcement is cheap because the problem is concentrated:

| Sellers | Share of all breaches |
|---|---|
| Top 20 by breach count | 24.7 percent |
| Top 50 | 40.6 percent |
| Top 100 | 54.3 percent |

A conversation with 100 sellers addresses more than half the breaches.

### Converting that to money, and why this is the weakest number here

Chain of reasoning, with every assumption named:

1. Preventable share of the breach-driven lateness: 40, 60 or 80 percent.
2. Each late order costs 2.020 review points on average (4.291 on time
   against 2.271 late) and carries a 62.40 percent chance of a 1 or 2
   star review, against 9.24 percent when on time.
3. Revenue effect per one-star rating improvement: 5 to 9 percent.
   Source: Luca, M. (2011, revised 2016), "Reviews, Reputation, and
   Revenue: The Case of Yelp.com", Harvard Business School working paper
   12-016, which found a one-star increase in Yelp rating raised revenue
   by 5 to 9 percent for independent restaurants.

| Preventable | Late orders avoided | Poor reviews avoided | Rating uplift | 5% | 7% | 9% |
|---|---:|---:|---:|---:|---:|---:|
| 40% | 376 | 200 | 0.0132 | 5,296 | 7,414 | 9,533 |
| 60% | 564 | 300 | 0.0199 | 7,944 | 11,122 | 14,299 |
| 80% | 752 | 400 | 0.0265 | 10,592 | 14,829 | 19,065 |

Late orders and poor reviews avoided above are **annual**. Over the full
20-month period they are 1.67 times larger.

Base case: 60 percent preventable at 7 percent per star gives
**11,122 a year**, in a range of 5,296 to 19,065.

**This number should be treated as the weakest in the case, and three
reasons are stated plainly rather than buried:**

1. The Luca elasticity comes from independent restaurants on Yelp, not a
   Brazilian e-commerce marketplace. It is a benchmark, not a
   measurement.
2. The effect is diluted by construction: 940 recovered orders move a
   marketplace-wide average built on 95,560 reviews by only 0.02 stars.
   At seller level, where buyers actually see ratings, the effect is
   concentrated and larger, but this data cannot size that.
3. No returns, refunds or service-contact costs exist in the data, so the
   operational cost of a late order is not counted at all. The true
   figure is therefore higher than modelled, direction known, magnitude
   not.

The defensible claim is the operational one: **564 fewer late orders and
about 300 fewer poor reviews a year at the base case**, which is 940 and
500 over the full 20-month period. The money figure
is offered as an order of magnitude with its assumption exposed in one
cell of the Excel model, where a reader can replace it.

## Lever 3: lane freight excess

16 lanes sit significantly above the freight model after
Benjamini-Hochberg correction, with a combined excess of 47,040 over the
period, or **28,224 a year, which is 2.12 percent of freight spend**.
Every one runs from Sao Paulo to the north or north east, and all are low
volume. Real, recoverable in principle, and the smallest of the three
levers.

## Peak period: size against March, not against the average

Lateness is seasonal and the spread is wide: 8.13 percent on average,
21.36 percent in March 2018, 15.99 percent in February 2018, 14.31
percent in November 2017. The worst month runs **2.63 times the annual
average**. Any capacity or enforcement plan sized against 8 percent will
fail in exactly the months that matter.

## Ranked summary

| Rank | Lever | Quantified effect | Confidence |
|---|---|---|---|
| 1 | Per-lane delivery promise | 38 percent fewer late orders, about 1,787 a year (p95), or 2.26 days off the average promise (p90) | High, measured in-sample |
| 2 | Dispatch enforcement on the top 100 sellers | 564 fewer late orders and about 300 fewer poor reviews a year; 11,122 a year modelled, range 5,296 to 19,065 | Operational effect high, money low |
| 3 | Freight on 16 north-east lanes | 28,224 a year | High on the number, low on recoverability |
| 4 | Re-routing | Not separately sized: the same lanes as rank 3, and no alternative seller locations exist in the data to model a reroute | Not estimable here |

## Methodological notes

- Lateness is measured on timestamps, so an order delivered later in the
  day on its promised date counts as late. On a whole-day definition the
  rate is 6.79 percent rather than 8.13 percent. The timestamp definition
  is used throughout and the difference is 1.34 points.
- Per-lane percentiles are computed in-sample, which flatters them. In
  production the promise should be set from a trailing window, for
  example the last 90 days, and refreshed monthly. Stated as a
  limitation, not corrected here.
- Period and annual figures are separated explicitly throughout. An earlier
  draft of this document reported two 20-month figures as annual: the late
  orders avoided under each lever. Both are corrected above. The modelled
  money figures were unaffected, because the rating uplift is a ratio
  measured on the same 20-month basis in numerator and denominator.
- The lane freight excess is computed on delivered-order counts, which is
  why it reads 47,040 rather than the 48,059 obtained on all-order counts.
- Lanes with fewer than 50 orders are excluded from the promise rules,
  which covers 96.8 percent of orders. The remainder keeps the blanket
  promise until volume supports a lane-specific one.

## Reconciliation with the Power BI dashboard

The dashboard reports two figures differently from the analysis above.
Both differences are definitional rather than errors, and **the
dashboard figures are the ones to quote**, because each rests on the
more defensible basis. The analysis numbers are kept here rather than
overwritten, so the difference is auditable.

| Measure | This analysis | Dashboard | Why they differ |
|---|---:|---:|---|
| Change to the average promise, p95 rule | 2.91 days | **2.27 days** | The analysis measures the promise as elapsed time between purchase and promised date. The dashboard counts calendar-day boundaries, which is what a customer reads off a calendar. The gap is the fraction of the purchase day |
| Late orders avoided a year, p95 rule | 1,787 | **1,697** | The analysis divides by all 96,203 delivered orders. The dashboard divides by the 93,139 orders on lanes that actually have a p95 rule, which is the correct denominator for a rule that does not apply everywhere |

Neither difference moves any conclusion. The p95 rule still cuts
lateness from 8.13 to 5.04 percent, the ranking of the four levers is
unchanged, and SP to RJ remains the single most important lane.

Two notes carried into the limitations page of the dashboard:

1. Promise length is counted in calendar days from purchase to the
   promised date.
2. All p90 and p95 figures are measured on the orders covered by a lane
   rule, which is 96.8 percent of orders.

**How this was caught.** The first version of the dashboard measure
returned 8.06 percent rather than 5.04. `LaneDetail` holds only the 100
lanes with 50 or more orders, so for thinner lanes
`RELATED(LaneDetail[p95])` returned blank, and in DAX any number is
greater than blank. Roughly 3,000 orders were therefore counted as late
that should have been out of scope. The measure produced a plausible
number rather than an error, which is the hardest kind of mistake to
notice, and it was found only by checking the dashboard against the
model rather than by looking at the dashboard alone.
