# Stage 1: Business Brief

**Case 1: Reducing cost-to-serve in e-commerce logistics**
Framing: logistics operations, with delivery reliability damage folded in as the cost multiplier on lateness.
Date: 2026-11-24

## 1. Business context

Olist is a Brazilian marketplace that places small sellers onto large
e-commerce platforms and coordinates fulfilment through partner carriers.
The data covers 99,441 orders placed between 4 September 2016 and
17 October 2018, fulfilled by 3,095 sellers to customers across all
Brazilian states, with 112,650 order items.

The company charges customers a freight amount per item and bears the
operational consequences of how long delivery takes. Both halves of that
sentence are measurable in this data, which is why this case is viable.

## 2. The decision

Which delivery lanes, sellers and product classes do we intervene on in
the next planning quarter, and which of four levers do we pull on each:

1. Re-route: shift fulfilment to a closer seller or consolidation point.
2. Renegotiate: change the freight arrangement on the lane.
3. Enforce: hold sellers to dispatch deadlines.
4. Recalibrate: change the delivery date promised to the customer.

The logistics budget is fixed, so this is a ranking exercise, not a wish
list. Every recommendation must therefore carry an expected value, and the
final list must be ordered.

## 3. Decision maker and audience

- **Primary:** Head of Logistics, who owns lane and carrier arrangements
  and seller dispatch performance.
- **Secondary:** CFO, who cares about freight as a share of order value.
- **Secondary:** Head of Customer Experience, who owns the review score
  consequence of late delivery.

## 4. Decision deadline

Recommendation required two weeks before the quarterly budget lock, so
that lane changes can be negotiated before the next peak period.

## 5. Cost of getting it wrong

Two distinct failure modes, and they pull in opposite directions:

- **Wasted spend:** directing the budget at lanes that are already cheap
  and reliable, which buys nothing.
- **Unaddressed damage:** missing the lanes where late delivery is
  destroying review scores, which costs future revenue and seller
  confidence invisibly, because nobody files a complaint against a lane.

A ranking that confuses high volume with high loss produces both failures
at once. That is the specific error this analysis exists to prevent.

## 6. Questions that follow from the decision

1. What does it cost to serve an order, by lane (seller state to customer
   state), and what drives the variation: distance, weight, item count,
   or split shipment across multiple sellers?
2. What share of order value is consumed by freight, by lane and by
   product class, and where is that share worst?
3. Which lanes and which sellers breach the delivery promise, by how much,
   and how fat is the tail?
4. Where in the chain is time lost: seller dispatch, carrier handover, or
   the final leg to the customer?
5. What does lateness cost in review score, and what is a one-star review
   worth in revenue terms?
6. Is the delivery promise itself miscalibrated, and in which direction?
7. Ranked by expected value, which interventions should take the budget?

## 7. Hypotheses to test

Three formal tests, each chosen because it underwrites one specific lever
in the decision. The remaining questions in section 6 are answered with
models and ranked tables rather than significance tests, for the reason
set out below.

H₀1: On-time delivery is independent of split shipment, distance and
order weight. Tested jointly with a logistic regression on lateness, with
lane type, distance, weight, item count and split shipment as covariates.
Underwrites the enforce and re-route levers.

H₀2: Review score is independent of days late. Tested with a
non-parametric trend test across lateness bands, and modelled for the
damage estimate. This is the load-bearing test of the case, because the
revenue-at-risk figure rests entirely on it.

H₀3: The delivery promise is unbiased, meaning the mean difference
between the promised and actual delivery date is zero. One-sample test,
reported with the distribution by lane rather than as a single number.
Underwrites the recalibrate lever.

### Why three and not six

The analysis base table holds 97,300 orders. At that sample size almost
any difference reaches statistical significance, so a longer list of
tests would produce a longer list of significant findings that a Head of
Logistics cannot act on. Three consequences follow, and all three are
stated in the report:

1. Effect sizes and confidence intervals lead the findings. P-values are
   reported but never carry an argument on their own.
2. Where several comparisons sit inside one family (lanes, sellers),
   p-values are adjusted with the Benjamini-Hochberg procedure.
3. Lane and seller rankings apply a minimum volume threshold, because a
   lane with 30 orders will top any unadjusted ranking on noise alone.

Freight variation across lanes, time lost by leg, and seller dispatch
performance are treated as models and ranked tables, not tests, because
the decision needs an ordered list of where to intervene rather than a
verdict on whether a difference exists.

Profiling already puts H₀3 under immediate suspicion: delivered orders
arrive on average 11.9 days ahead of the promised date, which suggests
the promise is padded rather than estimated. If that holds, recalibration
becomes a live lever at near-zero cost.

## 8. Success metrics

| Metric | Why it matters | Owner |
|---|---|---|
| Freight value per delivered order | The cost-to-serve proxy | Logistics |
| Freight as a share of order value | Recovery and pricing view | CFO |
| On-time rate against promise | Service commitment kept | Logistics |
| Mean and 90th percentile days late | Tail risk, not just average | Logistics |
| Days from purchase to delivery | Customer-experienced speed | CX |
| Share of 1 and 2 star reviews | Reliability damage | CX |
| Revenue at risk from lateness | Translates service into money | CFO |

## 9. Scope

**In scope:** orders with status delivered or shipped, purchased between
1 January 2017 and 31 August 2018. Lane defined as seller state to
customer state. Unit of analysis: the order, with a parallel item-level
table for product class work.

**Out of scope and why:**
- 2016 orders (329 in total, a ramp-up period that would distort trend).
- Orders purchased after 31 August 2018, because deliveries are still in
  flight at the data cut-off and including them would understate delivery
  times.
- Cancellations, fraud and returns: no return data exists here.
- Carrier-level recommendations: carrier identity is not in the data.
- True margin: cost of goods is not in the data.

## 10. Limitations to carry through to the report

1. `freight_value` is the amount charged to the customer, allocated per
   item, not the carrier's actual cost. Throughout this case it is used as
   a cost-to-serve proxy, and every conclusion is worded accordingly.
2. Carrier identity is absent, so renegotiation recommendations land at
   lane level, not at carrier level.
3. Repeat purchasing is almost absent: 96,096 unique customers across
   99,441 orders, so only about 3 percent of customers ever order twice.
   Revenue damage from lateness therefore runs through review score and a
   stated benchmark, not through observed repeat behaviour. This is
   declared rather than hidden, because an interviewer will look for it.
4. 610 products carry no category and 2 carry no weight, which caps
   product-class coverage slightly below 100 percent.
5. Geolocation has 1,000,163 rows for 19,015 distinct postcode prefixes,
   so coordinates must be reduced to one centroid per prefix before any
   distance calculation.

## 11. Definition of done

Stage 8 recommendations ranked by expected value, each with cost, effort,
owner and a verification metric, supported by an Excel scenario model and
a Power BI dashboard built for the Head of Logistics, plus the interview
pack.
