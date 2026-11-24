import numpy as np, pandas as pd, duckdb, json, statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests
FACT="/mnt/user-data/outputs/case01/03-data-clean/fact_orders.parquet"
con=duckdb.connect(); df=con.execute(f"SELECT * FROM '{FACT}'").df()
d=df[df.delivered_at.notna()&df.days_vs_promise.notna()].copy()
d["promised_window"]=(d.promised_date-d.purchased_at).dt.total_seconds()/86400
MONTHS=20.0
r=df[df.review_score.notna()&df.days_vs_promise.notna()]

# lane table
g=d.groupby("lane").agg(orders=("total_days","size"),cur_promise=("promised_window","mean"),
   p90=("total_days",lambda s:np.quantile(s,0.90)),p95=("total_days",lambda s:np.quantile(s,0.95)),
   avg_days=("total_days","mean"),cur_late=("is_late","mean"),
   freight_total=("freight_value","sum"),order_value=("order_value","sum"),
   avg_review=("review_score","mean")).reset_index()
g=g[g.orders>=50].copy()
m=d.merge(g[["lane","p90","p95"]],on="lane")
lp=m.assign(l90=m.total_days>m.p90,l95=m.total_days>m.p95).groupby("lane").agg(
    late_p90=("l90","mean"),late_p95=("l95","mean")).reset_index()
g=g.merge(lp,on="lane")

fr=df.dropna(subset=["freight_value","distance_km","weight_kg"]).copy()
fr["ld"]=np.log1p(fr.distance_km);fr["lw"]=np.log1p(fr.weight_kg)
ols=sm.OLS(fr.freight_value,sm.add_constant(fr[["ld","lw","n_items"]])).fit()
fr["resid"]=ols.resid
L=fr.groupby("lane").agg(n=("resid","size"),mean_resid=("resid","mean"),sd=("resid","std")).reset_index()
L["p"]=2*stats.t.sf((L.mean_resid/(L.sd/np.sqrt(L.n))).abs(),L.n-1)
L.loc[L.n>=200,"p_adj"]=multipletests(L.loc[L.n>=200,"p"],method="fdr_bh")[1]
g=g.merge(L[["lane","mean_resid","p_adj"]],on="lane",how="left")
g["excess_freight"]=(g.mean_resid*g.orders)
g=g.sort_values("orders",ascending=False)
g.round(4).to_csv("lane_detail.csv",index=False)

# promise curve, aligned to the timestamp definition of lateness
cur=[]
for cut in range(0,13):
    cur.append({"days_removed":cut,"late_rate":( d.days_vs_promise > -(cut+1) ).mean()})
pd.DataFrame(cur).to_csv("promise_curve.csv",index=False)

mm=df.groupby(df.purchase_month.dt.to_period("M").astype(str)).agg(
    orders=("order_id","size"),gmv=("order_value","sum"),freight=("freight_value","sum"),
    avg_days=("total_days","mean"),late=("is_late","mean"),review=("review_score","mean")).reset_index()
mm.columns=["month","orders","gmv","freight","avg_days","late_rate","avg_review"]
mm.round(4).to_csv("monthly.csv",index=False)

sb=df[df.seller_breached_limit.notna()].groupby("primary_seller_id").agg(
    orders=("order_id","size"),breaches=("seller_breached_limit","sum"),
    late=("is_late","mean"),review=("review_score","mean"),
    freight=("freight_value","sum")).reset_index()
sb["breach_rate"]=sb.breaches/sb.orders
sb=sb[sb.orders>=20].sort_values("breaches",ascending=False).head(100)
sb["seller_ref"]=["S%03d"%(i+1) for i in range(len(sb))]
sb[["seller_ref","primary_seller_id","orders","breaches","breach_rate","late","review","freight"]].round(4).to_csv("seller_breach.csv",index=False)

b=df[df.seller_breached_limit.notna()&df.is_late.notna()]
br=b[b.seller_breached_limit]; ok=b[~b.seller_breached_limit]
C={"months":MONTHS,"delivered_orders":int(len(d)),"reviews":int(len(r)),
 "gmv_period":float(df.order_value.sum()),"freight_period":float(df.freight_value.sum()),
 "breached_orders":int(len(br)),"late_rate_breached":float(br.is_late.mean()),
 "late_rate_met":float(ok.is_late.mean()),
 "poor_rate_late":float((r[r.days_vs_promise>0].review_score<=2).mean()),
 "poor_rate_ontime":float((r[r.days_vs_promise<=0].review_score<=2).mean()),
 "review_points_per_late":float(r[r.days_vs_promise<=0].review_score.mean()-r[r.days_vs_promise>0].review_score.mean()),
 "cur_late_rate":float(df.is_late.mean()),
 "lane_coverage_orders":int(g.orders.sum()),
 "excess_freight_period":float(g.loc[(g.mean_resid>0)&(g.p_adj<0.05),"excess_freight"].sum()),
 "peak_late_rate":float(mm.late_rate.max())}
w=g.orders/g.orders.sum()
C.update({"avg_promise_today":float((g.cur_promise*w).sum()),
 "avg_promise_p90":float((g.p90*w).sum()),"avg_promise_p95":float((g.p95*w).sum()),
 "late_rate_p90":float((m.total_days>m.p90).mean()),"late_rate_p95":float((m.total_days>m.p95).mean())})
json.dump(C,open("constants.json","w"),indent=1)
print(json.dumps(C,indent=1))
print("\nlanes:",len(g),"period excess late orders:",round(C["breached_orders"]*(C["late_rate_breached"]-C["late_rate_met"])))
print("ANNUAL excess late orders:",round(C["breached_orders"]*(C["late_rate_breached"]-C["late_rate_met"])*12/MONTHS))
print("promise p95 late orders avoided, period:",round((C["cur_late_rate"]-C["late_rate_p95"])*C["delivered_orders"]),
      " annual:",round((C["cur_late_rate"]-C["late_rate_p95"])*C["delivered_orders"]*12/MONTHS))
