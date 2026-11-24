# Stage 8: Recommendations

**Case 1: Reducing cost-to-serve in e-commerce logistics**
For: Head of Logistics. Copied to: CFO, Head of Customer Experience.
All money in BRL, annualised from 20 months of data.

Ranked by expected value. Every figure traces to
`stage-6-quantification.md`, and the two that differ from the dashboard
are reconciled at the end of that document.

---

## 1. Set the delivery promise per lane, starting with the lanes that shorten

**Do this:** replace the single blanket delivery promise with a
lane-specific promise set at each lane's 95th percentile of observed
delivery time, refreshed monthly from a trailing 90-day window.

**Expected effect:** lateness falls from 8.13 to 5.04 percent, which is
**about 1,697 fewer late orders a year**, at the cost of 2.27 days added
to the average promise. 42 of the 100 lanes get a *shorter* promise than
today.

**Sequence it in two waves, and this is the part that matters.** Wave
one moves only the 42 lanes whose promise shortens. That is pure upside:
customers are told a nearer date, service does not degrade, and nothing
is risked. Measure conversion on those lanes for one month. Wave two
then lengthens the under-padded lanes, with the conversion evidence from
wave one in hand. Doing it in one step bets the whole change on an
untested assumption about how customers react to a later promised date.

**Cost:** engineering time to make the promise lane-aware and to
schedule the monthly refresh. No operational spend.
**Effort:** medium. **Owner:** Head of Logistics with Engineering.
**Verification metric:** on-time rate against promise, by lane, monthly.
Target 95 percent within two quarters.
**Risk:** a longer promise may reduce conversion on the lanes in wave
two. The two-wave sequence is the mitigation, and the data to size that
risk does not exist here.

**What not to do:** cut the padding uniformly. Three days off every
lane's promise takes lateness from 8.13 to 13.06 percent. The padding is
not waste, it is covering lane variance.

---

## 2. Enforce dispatch deadlines on the top 100 sellers

**Do this:** publish a dispatch scorecard, open a conversation with the
100 sellers who account for 54.3 percent of all breaches, and make the
dispatch deadline a term rather than a suggestion.

**Expected effect:** a missed dispatch deadline makes a late delivery
**4.71 times more likely** (95 percent CI 4.45 to 4.98). At the base
case of 60 percent preventable, **564 fewer late orders and about 300
fewer poor reviews a year**. Modelled revenue effect 11,122 a year, in a
range of 5,296 to 19,065.

**Treat that money figure as the weakest number in the case.** It rests
on a published rating elasticity from another industry, it is diluted by
a marketplace-wide review base, and it counts none of the service and
refund costs that are absent from the data. The operational effect is
the defensible claim.

**Cost:** seller management time, no spend. **Effort:** low. The
concentration is what makes it cheap: 100 conversations, not 2,941.
**Owner:** Head of Marketplace Operations.
**Verification metric:** breach rate among the top 100, monthly. Target
halved within two quarters.
**Risk:** punitive enforcement drives sellers off the platform. Lead
with support (why are they missing the deadline?) and escalate second.

---

## 3. Renegotiate freight on the 16 north-east lanes

**Do this:** take the 16 lanes charging significantly above what
distance, weight and item count explain into the next carrier
negotiation.

**Expected effect:** 47,040 of excess freight over the period, which is
**28,224 a year, or 2.12 percent of freight spend**.

**Rank it third honestly.** This is the lever the brief expected to
matter most and it is the smallest of the three. Every one of the 16
lanes runs from Sao Paulo to the north or north east and all are low
volume, which is also why there is little negotiating leverage.

**Cost:** negotiation time. **Effort:** medium to high.
**Owner:** Logistics procurement.
**Verification metric:** freight per kilo per kilometre on those lanes,
quarterly.
**Risk:** low volume means low leverage. The excess may be a genuine
cost of serving remote destinations rather than a margin to recover.

---

## 4. Size peak capacity against March, not against the average

**Do this:** plan seasonal capacity and dispatch enforcement against the
peak month rather than the annual mean.

**Expected effect:** prevents under-provisioning in exactly the months
that do the most damage. Lateness runs 8.13 percent on average and
**21.36 percent in March 2018, a factor of 2.63**.

**Cost:** none to decide, real to provision.
**Effort:** low. **Owner:** Logistics planning.
**Verification metric:** peak-month late rate against the annual mean.
**Risk:** none in the recommendation itself.

---

## 5. Fix the split-shipment delivery timestamp

**Do this:** record the final shipment's arrival as the order's delivery
date, not the first.

**Why it is on the list:** 1,274 orders show 1.42 percent late against
8.22 percent, while carrying a 47.22 percent poor-review rate against
12.95 percent. Faster, almost never late, and rated far worse is not
operationally possible. The delivery date is almost certainly recording
the first parcel to arrive while the customer is still waiting.

**Expected effect:** no operational gain. It makes 1.3 percent of orders
measurable, and it removes a trap that will mislead the next analyst who
looks at this data.

**Cost:** engineering time. **Effort:** low.
**Owner:** Engineering, data platform.
**Verification metric:** split-shipment late rate becomes plausible
relative to single-seller orders.

---

## What this case does not recommend

**Do not act on the freight number as a cost-savings story.** Freight is
16.64 percent of item value, but 47 percent of its variation is
explained by distance, weight and item count alone, and the lanes above
that model are 2.12 percent of spend. This is a service case, not a
cost-savings case, and presenting it otherwise would set an expectation
the data cannot meet.

**Do not treat the review-damage money as a forecast.** It is an order
of magnitude with its assumption exposed in one cell of the Excel model.
A reader who disagrees with the benchmark can change it and watch every
downstream number move.

## If I had more data

1. **Carrier identity**, which would move recommendation 3 from lane
   level to carrier level, where the negotiating leverage actually sits.
2. **Service contact and refund costs**, which would replace the
   weakest number in the case with a measured one.
3. **Conversion by promised delivery date**, which would size the risk
   in wave two of recommendation 1 instead of leaving it stated.
