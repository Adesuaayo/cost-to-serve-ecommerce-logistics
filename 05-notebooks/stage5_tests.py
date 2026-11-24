import sys, numpy as np, pandas as pd, duckdb
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

FACT = sys.argv[1]
con = duckdb.connect()
df = con.execute(f"SELECT * FROM '{FACT}'").df()
pd.set_option("display.width", 200)

print("rows:", len(df))

# ---------------- H01: lateness model ----------------
print("\n================ H₀1: on-time delivery and structural factors ================")
d = df[df.is_late.notna() & df.distance_km.notna() & df.weight_kg.notna()].copy()
d["log_distance"] = np.log1p(d.distance_km)
d["log_weight"] = np.log1p(d.weight_kg)
d["cross_state"] = (d.lane_type == "cross state").astype(int)
d["split"] = d.is_split_shipment.astype(int)
d["late"] = d.is_late.astype(int)

def logit(frame, cols, label):
    X = sm.add_constant(frame[cols])
    m = sm.Logit(frame["late"], X).fit(disp=0)
    out = pd.DataFrame({"coef": m.params, "p": m.pvalues})
    ci = m.conf_int()
    out["OR"] = np.exp(m.params).round(3)
    out["OR_lo"] = np.exp(ci[0]).round(3)
    out["OR_hi"] = np.exp(ci[1]).round(3)
    out["p"] = out["p"].apply(lambda v: f"{v:.3g}")
    print(f"\n--- {label}  (n={len(frame):,})  pseudo R2={m.prsquared:.4f} ---")
    print(out[["OR", "OR_lo", "OR_hi", "p"]].to_string())
    return m

m1 = logit(d, ["log_distance", "log_weight", "n_items", "split", "cross_state"],
           "Model 1: structural factors only")

d2 = d[(~d.timing_anomaly) & d.seller_breached_limit.notna()].copy()
d2["breach"] = d2.seller_breached_limit.astype(int)
m2 = logit(d2, ["log_distance", "log_weight", "n_items", "split", "cross_state", "breach"],
           "Model 2: adding seller dispatch breach")

# ---------------- H02: review score and lateness ----------------
print("\n================ H₀2: review score and days late ================")
r = df[df.review_score.notna() & df.days_vs_promise.notna()].copy()
rho, p_rho = stats.spearmanr(r.days_vs_promise, r.review_score)
print(f"Spearman rho = {rho:.4f}  p = {p_rho:.3g}  n = {len(r):,}")

bands = pd.cut(r.days_vs_promise, [-999, -10, -3, 0, 3, 10, 9999],
               labels=["10+ early", "3-10 early", "0-3 early", "0-3 late", "3-10 late", "10+ late"])
groups = [r.review_score[bands == b].values for b in bands.cat.categories]
H, p_kw = stats.kruskal(*groups)
print(f"Kruskal-Wallis H = {H:,.1f}  p = {p_kw:.3g}  across {len(groups)} lateness bands")

on_time = r[r.days_vs_promise <= 0]
late = r[r.days_vs_promise > 0]
p_ot = (on_time.review_score <= 2).mean()
p_lt = (late.review_score <= 2).mean()
n1, n2 = len(on_time), len(late)
se = np.sqrt(p_ot*(1-p_ot)/n1 + p_lt*(1-p_lt)/n2)
diff = p_lt - p_ot
print(f"\nPoor review rate (1 or 2 star):")
print(f"  on time or early : {p_ot*100:6.2f}%  (n={n1:,})")
print(f"  late             : {p_lt*100:6.2f}%  (n={n2:,})")
print(f"  difference       : {diff*100:6.2f} points, 95% CI [{(diff-1.96*se)*100:.2f}, {(diff+1.96*se)*100:.2f}]")
print(f"  relative risk    : {p_lt/p_ot:.2f}x")
print(f"  mean review      : {on_time.review_score.mean():.3f} vs {late.review_score.mean():.3f}")

# marginal damage per day late, first 15 days
sub = r[(r.days_vs_promise > 0) & (r.days_vs_promise <= 15)]
sl, ic, rv, pv, _ = stats.linregress(sub.days_vs_promise, sub.review_score)
print(f"\nWithin the first 15 late days: review score falls {abs(sl):.3f} points per extra day late (p={pv:.3g})")

# ---------------- H03: promise bias ----------------
print("\n================ H₀3: is the delivery promise unbiased? ================")
g = df[df.days_vs_promise.notna()].days_vs_promise.astype(float)
t, p_t = stats.ttest_1samp(g, 0)
w, p_w = stats.wilcoxon(g, zero_method="zsplit")
print(f"n = {len(g):,}  mean = {g.mean():.2f} days  median = {g.median():.0f} days  sd = {g.std():.2f}")
print(f"One-sample t = {t:,.1f}  p = {p_t:.3g}   Wilcoxon p = {p_w:.3g}")
ci = stats.t.interval(0.95, len(g)-1, loc=g.mean(), scale=stats.sem(g))
print(f"95% CI on the mean gap: [{ci[0]:.2f}, {ci[1]:.2f}] days (negative means early)")
print(f"Promised window mean: {(df.promised_date - df.purchased_at).dt.total_seconds().div(86400).mean():.2f} days")
print(f"Actual delivery mean: {df.total_days.mean():.2f} days")

# ---------------- Freight residual model by lane ----------------
print("\n================ Freight expected vs actual, by lane ================")
fr = df[df.freight_value.notna() & df.distance_km.notna() & df.weight_kg.notna()].copy()
fr["log_distance"] = np.log1p(fr.distance_km)
fr["log_weight"] = np.log1p(fr.weight_kg)
X = sm.add_constant(fr[["log_distance", "log_weight", "n_items"]])
ols = sm.OLS(fr.freight_value, X).fit()
print(f"OLS freight ~ log(distance) + log(weight) + items : R2 = {ols.rsquared:.4f}, n = {len(fr):,}")
print(pd.DataFrame({"coef": ols.params.round(3), "p": ols.pvalues.apply(lambda v: f'{v:.3g}')}).to_string())
fr["resid"] = ols.resid

lane = fr.groupby("lane").agg(orders=("resid", "size"), mean_resid=("resid", "mean"),
                              sd=("resid", "std"), freight_total=("freight_value", "sum"),
                              pct_late=("is_late", "mean")).reset_index()
lane = lane[lane.orders >= 200].copy()
lane["t"] = lane.mean_resid / (lane.sd / np.sqrt(lane.orders))
lane["p"] = 2 * stats.t.sf(lane.t.abs(), lane.orders - 1)
lane["p_adj"] = multipletests(lane.p, method="fdr_bh")[1]
lane["excess_freight_total"] = (lane.mean_resid * lane.orders).round(0)
lane["pct_late"] = (lane.pct_late * 100).round(2)
lane = lane.sort_values("excess_freight_total", ascending=False)
cols = ["lane", "orders", "mean_resid", "excess_freight_total", "freight_total", "pct_late", "p_adj"]
print(f"\nLanes with 200+ orders: {len(lane)}. Significant after Benjamini-Hochberg: {(lane.p_adj<0.05).sum()}")
print("\nTop 10 lanes charging MORE than distance, weight and item count explain:")
print(lane.head(10)[cols].round({"mean_resid":2,"p_adj":4}).to_string(index=False))
print("\nTop 5 lanes charging LESS than the model expects:")
print(lane.tail(5)[cols].round({"mean_resid":2,"p_adj":4}).to_string(index=False))

# ---------------- split shipment artifact check ----------------
print("\n================ Split shipment anomaly check ================")
s = df[df.is_split_shipment]
print(f"split orders: {len(s):,}  pct_late {100*s.is_late.mean():.2f}%  mean review {s.review_score.mean():.3f}")
print(f"single orders: {(~df.is_split_shipment).sum():,}  pct_late {100*df[~df.is_split_shipment].is_late.mean():.2f}%  mean review {df[~df.is_split_shipment].review_score.mean():.3f}")
print(f"split mean total_days {s.total_days.mean():.2f} vs single {df[~df.is_split_shipment].total_days.mean():.2f}")
print(f"split poor-review rate {100*(s.review_score<=2).mean():.2f}% vs single {100*(df[~df.is_split_shipment].review_score<=2).mean():.2f}%")
