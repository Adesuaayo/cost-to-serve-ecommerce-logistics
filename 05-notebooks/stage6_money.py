import sys, numpy as np, pandas as pd, duckdb
FACT = sys.argv[1]
con = duckdb.connect(); df = con.execute(f"SELECT * FROM '{FACT}'").df()
pd.set_option("display.width", 220)
d = df[df.delivered_at.notna() & df.days_vs_promise.notna()].copy()
print(f"delivered orders in scope: {len(d):,}")

MONTHS = 20.0
gmv = df.order_value.sum(); gmv_yr = gmv / MONTHS * 12
print(f"GMV {gmv:,.0f} over {MONTHS:.0f} months -> annualised {gmv_yr:,.0f}")
print(f"freight {df.freight_value.sum():,.0f}")

print("\n=============== LEVER 2: PROMISE RECALIBRATION ===============")
print("\n--- A. Uniform promise reduction, what it costs in lateness ---")
rows=[]
for cut in range(0,16,1):
    rows.append({"promise_cut_days":cut,
                 "late_rate_pct":round(100*(d.days_vs_promise > -cut).mean(),2)})
print(pd.DataFrame(rows).to_string(index=False))

print("\n--- B. Per-lane promise set at a service percentile of actual delivery ---")
cur_window = (d.promised_date - d.purchased_at).dt.total_seconds()/86400
d = d.assign(promised_window=cur_window)
lane_stats=[]
for pct,label in [(0.90,"p90"),(0.95,"p95")]:
    g = d.groupby("lane").agg(orders=("total_days","size"),
                              cur_window=("promised_window","mean"),
                              new_window=("total_days", lambda s: np.quantile(s,pct)),
                              cur_late=("is_late","mean")).reset_index()
    g = g[g.orders>=50]
    g["delta"] = g.new_window - g.cur_window
    w = g.orders/g.orders.sum()
    cov = g.orders.sum()/len(d)
    # new late rate: per lane, orders delivered later than the new promise
    m = d.merge(g[["lane","new_window"]],on="lane")
    newlate = (m.total_days > m.new_window).mean()
    lane_stats.append({"target":label,"lanes":len(g),"coverage_pct":round(100*cur_window.notna().mean()*cov,1),
      "avg_cur_promise":round((g.cur_window*w).sum(),2),
      "avg_new_promise":round((g.new_window*w).sum(),2),
      "avg_change_days":round((g.delta*w).sum(),2),
      "lanes_shortened":int((g.delta<0).sum()),"lanes_lengthened":int((g.delta>0).sum()),
      "new_late_rate_pct":round(100*newlate,2)})
print(pd.DataFrame(lane_stats).to_string(index=False))

g95 = d.groupby("lane").agg(orders=("total_days","size"), cur_window=("promised_window","mean"),
     new_window=("total_days", lambda s: np.quantile(s,0.95)), cur_late=("is_late","mean")).reset_index()
g95 = g95[g95.orders>=50].copy(); g95["delta"]=g95.new_window-g95.cur_window
g95["cur_late"]=(g95.cur_late*100).round(2)
print("\nBiggest promise cuts available (over-padded lanes):")
print(g95.nsmallest(8,"delta")[["lane","orders","cur_window","new_window","delta","cur_late"]].round(1).to_string(index=False))
print("\nLanes needing a longer promise (under-padded, where lateness lives):")
print(g95.nlargest(8,"delta")[["lane","orders","cur_window","new_window","delta","cur_late"]].round(1).to_string(index=False))
days_saved = -(g95.delta*g95.orders).sum()
print(f"\nCustomer waiting days removed from the promise across these lanes: {days_saved:,.0f}")
print(f"Annualised: {days_saved/MONTHS*12:,.0f} promised-wait days per year")

print("\n=============== LEVER 1: DISPATCH ENFORCEMENT ===============")
b = df[df.seller_breached_limit.notna() & df.is_late.notna()]
br = b[b.seller_breached_limit]; ok = b[~b.seller_breached_limit]
late_br, late_ok = br.is_late.mean(), ok.is_late.mean()
print(f"breached {len(br):,} orders, late {100*late_br:.2f}%   met {len(ok):,} orders, late {100*late_ok:.2f}%")
excess_late = len(br)*(late_br-late_ok)
print(f"excess late orders attributable to breach: {excess_late:,.0f}")

r = df[df.review_score.notna() & df.days_vs_promise.notna()]
poor_late = (r[r.days_vs_promise>0].review_score<=2).mean()
poor_ot   = (r[r.days_vs_promise<=0].review_score<=2).mean()
mean_late = r[r.days_vs_promise>0].review_score.mean()
mean_ot   = r[r.days_vs_promise<=0].review_score.mean()
pts = mean_ot-mean_late
print(f"poor-review rate late {100*poor_late:.2f}% vs on-time {100*poor_ot:.2f}%; review points lost per late order {pts:.3f}")

seller = df[df.seller_breached_limit.notna()].groupby("primary_seller_id").agg(
    orders=("order_id","size"), breaches=("seller_breached_limit","sum")).reset_index()
seller["rate"]=seller.breaches/seller.orders
tot_b = seller.breaches.sum()
s2 = seller[seller.orders>=20].sort_values("breaches",ascending=False)
for n in (20,50,100):
    print(f"top {n} sellers by breach count cover {100*s2.head(n).breaches.sum()/tot_b:.1f}% of all breaches "
          f"({s2.head(n).breaches.sum():,.0f} of {tot_b:,.0f})")

print("\n--- Scenario grid: preventable share x revenue effect per star ---")
n_reviews = len(r)
out=[]
for prev in (0.4,0.6,0.8):
    la = excess_late*prev
    poor_avoided = la*(poor_late-poor_ot)
    rating_up = la*pts/n_reviews
    for elast in (0.05,0.07,0.09):
        out.append({"preventable":f"{prev:.0%}","late_avoided":round(la),
          "poor_reviews_avoided":round(poor_avoided),"rating_uplift":round(rating_up,4),
          "rev_per_star":f"{elast:.0%}","gmv_effect_annual":round(rating_up*elast*gmv_yr)})
print(pd.DataFrame(out).to_string(index=False))

print("\n=============== LEVER 3: LANE FREIGHT EXCESS ===============")
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests
fr=df.dropna(subset=["freight_value","distance_km","weight_kg"]).copy()
fr["ld"]=np.log1p(fr.distance_km); fr["lw"]=np.log1p(fr.weight_kg)
ols=sm.OLS(fr.freight_value, sm.add_constant(fr[["ld","lw","n_items"]])).fit()
fr["resid"]=ols.resid
L=fr.groupby("lane").agg(orders=("resid","size"),mean_resid=("resid","mean"),sd=("resid","std")).reset_index()
L=L[L.orders>=200].copy()
L["p"]=2*stats.t.sf((L.mean_resid/(L.sd/np.sqrt(L.orders))).abs(), L.orders-1)
L["p_adj"]=multipletests(L.p,method="fdr_bh")[1]
pos=L[(L.mean_resid>0)&(L.p_adj<0.05)]
print(f"lanes significantly above model: {len(pos)}; total excess {(pos.mean_resid*pos.orders).sum():,.0f}")
print(f"annualised excess: {(pos.mean_resid*pos.orders).sum()/MONTHS*12:,.0f}")
print(f"as share of freight spend: {100*(pos.mean_resid*pos.orders).sum()/df.freight_value.sum():.2f}%")

print("\n=============== PEAK PERIOD SIZING ===============")
mm=df.groupby(df.purchase_month.dt.to_period("M")).agg(orders=("order_id","size"),late=("is_late","mean")).reset_index()
mm["late"]=(mm.late*100).round(2)
peak=mm.nlargest(3,"late"); print("worst 3 months:"); print(peak.to_string(index=False))
print(f"annual mean late rate {100*df.is_late.mean():.2f}%, peak month {mm.late.max():.2f}%, ratio {mm.late.max()/(100*df.is_late.mean()):.2f}x")
