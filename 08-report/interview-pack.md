# Interview Pack

**Case 1: Reducing cost-to-serve in e-commerce logistics**

## Three resume bullets

- Analysed 97,300 e-commerce orders in SQL and Python to find that a
  blanket delivery promise, not freight cost, drove service failure;
  designed a per-lane promise rule that cuts late deliveries from 8.1 to
  5.0 percent, about **1,697 fewer late orders a year**.
- Modelled late-delivery risk with logistic regression and found a
  missed seller dispatch deadline raises the odds of a late delivery
  **4.71 times** (95% CI 4.45 to 4.98), and that the top 100 sellers
  carry 54 percent of all breaches, turning a 2,941-seller problem into
  a 100-conversation one.
- Built a scenario-driven Excel model and a four-page Power BI report
  for a logistics audience, with every assumption exposed as an editable
  input and a limitations page stating what the numbers cannot carry.

## LinkedIn narrative

A marketplace spends 16.6 percent of item value on freight. The obvious
project is to go and claw some of it back.

I ran that analysis and it did not hold up. Distance, weight and item
count explain 47 percent of freight variation on their own, and the
lanes charging more than the model expects come to about 2 percent of
freight spend. There was no big overcharge to find.

What I found instead was the delivery promise. It was padded by nearly
12 days against a 12.5-day actual delivery, and still missed one order
in twelve. The tempting recommendation is to cut the padding. I checked
what that would cost first: three days off every lane takes lateness
from 8.1 to 13.1 percent. The padding was not waste, it was covering the
fact that some lanes are far less predictable than others.

Setting the promise per lane instead cuts lateness to 5.0 percent and
actually shortens the promise on 42 of 100 lanes.

The part I enjoyed most was a finding I had to throw away. Split
shipments looked more reliable than single-seller orders: 1.4 percent
late against 8.2. They also carried a 47 percent poor-review rate
against 13. Faster, rarely late, and rated far worse is not
operationally possible, and the explanation is that the delivery date
records the first parcel to arrive rather than the last. I reported it
as a data defect instead of a finding.

Full write-up and dashboard in the comments.

## STAR answer

**Situation.** A Brazilian marketplace was spending 16.6 percent of item
value on freight and wanted to know where to direct a fixed logistics
budget across four levers.

**Task.** Rank the levers by expected value and give the Head of
Logistics something to act on before the quarterly budget lock.

**Action.** I cleaned 97,300 orders in SQL with every rule logged, built
a lane-level model of freight against distance and weight, ran three
hypothesis tests chosen because each underwrote one lever, and converted
the results into money with every assumption named. When the freight
analysis came back small, I reported that rather than inflating it, and
redirected the work to the delivery promise and seller dispatch, where
the effects were an order of magnitude larger.

**Result.** A ranked set of recommendations with owners and verification
metrics. The lead recommendation cuts late deliveries by 38 percent and
shortens the promise on nearly half the lanes. I also found and
documented a timestamp defect that would have led the next analyst to
conclude split shipments were more reliable, when the opposite is true.

---

## Ten questions, with answers

### The three that attack the method

**1. Your freight finding is 2 percent of spend. Isn't this analysis a failure?**

The brief was to rank four levers, not to confirm that one of them was
large. Ranking freight third on honest evidence is the analysis
succeeding. The failure mode would have been presenting 28,000 a year as
a cost-savings story to a Head of Logistics who then budgets against it.
The value sits in reliability instead, and I moved the work there as
soon as the freight residuals came back small.

**2. You used a Yelp restaurant elasticity to value reviews in a Brazilian marketplace. Defend that.**

I cannot defend it as a measurement, and I do not. It is labelled the
weakest number in the case for three stated reasons: wrong industry,
dilution across a 95,560-review base, and no service or refund costs in
the data. It sits in one cell of the Excel model so any reader can
replace it. The claim I defend is the operational one: 564 fewer late
orders and 300 fewer poor reviews a year. The money is an order of
magnitude, not a forecast.

**3. Your p95 rule is fitted on the same data you evaluate it on. That is overfitting.**

Correct, and it is stated as a limitation. The percentiles are in
sample, so the 5.04 percent is optimistic. In production the promise
should come from a trailing 90-day window refreshed monthly, which is
what I recommend. If I were taking this further I would hold out the
last three months, fit on the rest and measure the rule on data it had
never seen.

### Seven more

**4. Why three hypothesis tests and not more?**

The base table holds 97,300 orders. At that sample size almost any
difference is statistically significant, so a longer list would have
produced a longer list of significant findings that nobody can act on. I
kept the three that each underwrite a specific lever and handled the
rest as models and ranked tables, because the decision needed an ordered
list, not a verdict on whether differences exist.

**5. You say dispatch breaches cause lateness. How do you know it is not the reverse, or a confounder?**

I do not claim causation from the regression alone. What I have is a
4.71 odds ratio that survives controlling for distance, weight, item
count and lane type, and a plausible mechanism: a parcel handed to the
carrier late arrives late. Reverse causation is hard to argue because
the dispatch deadline precedes delivery. A confounder is possible,
seller size being the obvious candidate, which is why the recommendation
is to open a conversation with the top 100 sellers rather than to
penalise them immediately.

**6. Split shipments showed lower lateness. Why did you discard that?**

Because it is not credible. Split orders show 1.42 percent late against
8.22, a shorter average delivery, and a 47 percent poor-review rate
against 13. Faster and rarely late should not produce worse reviews. The
most likely explanation is that the delivery timestamp records the first
parcel to arrive while the customer is still waiting for the rest. I
discounted the coefficient, excluded split orders from timing
conclusions, kept their reviews as corroborating evidence, and
recommended fixing the timestamp.

**7. Your dashboard says 2.27 days and your report says 2.91. Which is right?**

Both, on different conventions, and the dashboard is the better one. My
Python measured the promise as elapsed time between purchase and
promised date; the dashboard counts calendar-day boundaries, which is
what a customer reads off a calendar. The reconciliation is documented
rather than resolved by quietly changing one number, because an
auditable difference is worth more than a tidy one.

**8. Why lane level and not carrier level?**

Because carrier identity is not in the data. Lane is the finest grain
the data supports. If I had carrier, recommendation three would move
there, which is where the negotiating leverage actually sits, and I
would expect the recoverable amount to be larger than 2 percent.

**9. How would you put this into production?**

The promise rule is the only piece that needs engineering. It needs the
promise calculation to become lane-aware and a monthly job to refresh
the percentiles from a trailing 90-day window. I would roll it out in
two waves: first the 42 lanes whose promise shortens, which risks
nothing, measure conversion for a month, then the lanes that lengthen
with that evidence in hand.

**10. What would you do with more data?**

Three things, in order. Carrier identity, to move the freight work to
where leverage exists. Service contact and refund costs, to replace the
weakest number in the case with a measured one. Conversion by promised
delivery date, to size the one risk in my lead recommendation instead of
leaving it stated.
