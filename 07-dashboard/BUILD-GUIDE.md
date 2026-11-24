# Power BI Build Guide

**Case 1: Reducing cost-to-serve in e-commerce logistics**
File: `07-dashboard/cost-to-serve-dashboard.pbix` (already holds the data
model, the lane relationship and three measures).
Designs: `page-1` to `page-4` PNGs in this folder. Build to match them.

Work in this order. Each step is finished before the next one starts.

**State as of 24 November 2026:** the data model, both calculated
columns and all fourteen measures are built, formatted and saved in
`cost-to-serve-dashboard.pbix`. What remains is visual assembly, which
starts at step 3. Nothing in steps 1 and 2 needs doing again.

Measures in the file: Total Orders, Delivered Orders, Late Rate,
Freight % of Value, Poor Review Rate, Breach Rate, Dispatch Breaches,
Late Rate when Breached, Late Rate when Met, Avg Promise Days,
Promise Padding Days, Late Rate at p90, Late Rate at p95,
Late Orders Avoided a Year at p95, Promise Change at p95.
Calculated columns: `purchase_date`, `distance_band`, `lateness_band`.
All eight rate measures are formatted as percentages.

## Step 0: set the theme first, not last

View ribbon, Themes, Browse for themes, pick
`cost-to-serve-theme.json` from this folder.

Do this before building anything. It sets the page background, the card
borders, the fonts and the colour order, so every visual you add comes
out already formatted and you never touch a colour picker. The first
colour is blue (normal), the second red (reserved for lateness and
damage, never for an ordinary series).

## Step 1: create the remaining measures  (DONE, 24 Nov 2026)

All measures exist in the saved file and are formatted. Skip to step 3.
The instructions below are kept so the build is reproducible from the
raw data, and because the formula-bar quirk catches everyone once.



Home ribbon, New measure. Then, and this matters, **click into the
formula bar before typing**: Power BI creates the measure with the name
selected in the ribbon, not in the formula bar, so typing straight away
goes nowhere. Click the formula bar, select all, delete, paste the line,
press Enter.

Every line is in `POWER-BI-BUILD-SPEC.md` section 8 under "Still to
create". Create all ten. Each is self-contained, so order does not
matter and none depends on another.

If a name clash warning appears, check the Home table box in the Measure
tools ribbon reads `fact_orders`, not `LaneDetail`. `LaneDetail` already
has a column called `orders`, which is what causes it.

## Step 2: format the measures  (DONE, 24 Nov 2026)



Select each measure, then set it in the Measure tools ribbon:

| Measure | Format | Decimals |
|---|---|---|
| Late Rate, Late Rate at p90, Late Rate at p95, Freight % of Value, Poor Review Rate, Breach Rate, Late Rate when Breached, Late Rate when Met | Percentage | 1 |
| Avg Promise Days, Promise Padding Days | Decimal number | 1 |
| Orders, Delivered Orders, Late Orders Avoided a Year at p95 | Whole number | 0 |

Doing this once here means you never format them again, in any visual.

## Step 3: page 1, service and cost overview

Rename Page 1 to "Service and cost".

**Six cards across the top.** Visual: Card. One field each:
Total Orders; Freight % of Value; Late Rate; `total_days` set to Average;
`review_score` set to Average; Promise Padding Days.
To change an aggregation, click the arrow on the field in the Values
well and pick Average.

**Line chart, lower left.** X: `purchase_month`. Y: Late Rate.
Add a constant line: Format pane, Analytics, Y-axis constant line,
value 0.0813, red, dashed, label "period average".
Title: "Lateness is seasonal: plan against March, not the average".

**Line chart, lower right.** X: `purchase_month`. Y: Freight % of Value.
Title: "Freight share rose while delivery got faster".
Do not put days and freight on one chart with two y-axes. Two measures
on two scales always means two charts.

**Bar chart.** Uses the `distance_band` calculated column, which is
already in the model. It was created as:

```
distance_band =
SWITCH(TRUE(),
    'fact_orders'[distance_km] < 50, "1. under 50 km",
    'fact_orders'[distance_km] < 200, "2. 50 to 200 km",
    'fact_orders'[distance_km] < 600, "3. 200 to 600 km",
    'fact_orders'[distance_km] < 1500, "4. 600 to 1500 km",
    "5. over 1500 km")
```

X: `distance_band`. Y: Late Rate. Turn on data labels.

**Second bar chart.** Uses `lateness_band`, also already in the model,
created as:

```
lateness_band =
SWITCH(TRUE(),
    ISBLANK('fact_orders'[days_vs_promise]), "not delivered",
    'fact_orders'[days_vs_promise] <= -10, "1. 10+ days early",
    'fact_orders'[days_vs_promise] < -3, "2. 3 to 10 early",
    'fact_orders'[days_vs_promise] <= 0, "3. 0 to 3 early",
    'fact_orders'[days_vs_promise] <= 3, "4. up to 3 late",
    'fact_orders'[days_vs_promise] <= 10, "5. 3 to 10 late",
    "6. over 10 days late")
```

X: `lateness_band`. Y: Poor Review Rate. Filter out "not delivered" on
the visual filter. Title: "One day late nearly triples poor reviews".

## Step 4: page 2, lanes and the delivery promise

Four cards: Late Rate; Late Rate at p95; Late Orders Avoided a Year at
p95; and a card built from a new measure:

```
Promise Change at p95 = AVERAGEX('fact_orders', RELATED('LaneDetail'[p95])) - AVERAGEX('fact_orders', DATEDIFF('fact_orders'[purchased_at], 'fact_orders'[promised_date], DAY))
```

**Scatter chart.** Details: `LaneDetail[lane]`. X: `avg_days` (Average).
Y: `cur_late` (Average). Size: `orders` (Sum).
Filter the visual to lanes with 200 or more orders, otherwise thin lanes
dominate on noise. Title: "SP to RJ is the problem: high volume and high
lateness".

**Line chart.** X: `PromiseCurve[days_removed]`. Y: `late_rate`.
Constant line at 0.0813, red, dashed.
Title: "Why the padding cannot be cut uniformly".

**Table, full width.** Columns: `lane`, `orders`, `cur_promise`, `p95`,
a new column `promise_change = LaneDetail[p95] - LaneDetail[cur_promise]`,
and `cur_late`. Sort by `promise_change` descending.
Conditional formatting on `promise_change`: Format pane, Cell elements,
Font colour, rules, above 0 red, below 0 blue.

## Step 5: page 3, seller dispatch enforcement

Four cards: Dispatch Breaches (count), Breach Rate, Late Rate when
Breached, Late Rate when Met.

**Bar chart.** Y: `SellerBreach[seller_ref]`. X: `breaches`.
Top 20 filter: visual filter, Top N, 20, by `breaches`.

**Table.** `seller_ref`, `orders`, `breaches`, `breach_rate`, `late`,
`review`. Conditional formatting: `late` above 0.15 red, `review` below
3.5 red.

`SellerBreach` has no relationship to `fact_orders`, and that is
deliberate. It covers 100 of 2,941 sellers, so relating it would
silently filter every other page down to those hundred.

## Step 6: page 4, method and limitations

Text boxes only, copied from `page-4` PNG, or straight out of
`03-data-clean/CLEANING-LOG.md` and the Notes sheet of the Excel model.

Most portfolio dashboards have no page like this. It is the page that
tells an interviewer you know what your numbers cannot carry, and it is
worth more than another chart.

## Step 7: verify before you call it finished

Put a blank card on any page and check these against the Excel model:

| Measure | Must read |
|---|---|
| Late Rate | 8.1% |
| Freight % of Value | 16.6% |
| Average of `total_days` | 12.5 |
| Orders | 97,300 |
| Late Rate at p95 | 5.0% |

If any of these is out, stop and find out why before building further.
A dashboard that disagrees with its own model is worse than no
dashboard, because it will be wrong in front of someone.

## Step 8: export for the portfolio

File, Export, Export to PDF gives one page per report page. For the
README, use Windows Snipping Tool on each page at full screen and save
the PNGs next to these designs. A recruiter sees the screenshots long
before they ever open a .pbix.
