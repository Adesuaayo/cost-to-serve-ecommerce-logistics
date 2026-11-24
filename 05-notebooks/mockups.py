import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import pandas as pd, numpy as np

SURF="#fcfcfb"; CARD="#ffffff"; INK="#0b0b0b"; INK2="#52514e"; MUTED="#8a8984"
BLUE="#2a78d6"; RED="#e34948"; GRID="#e6e5e1"; BAR="#2a78d6"
W,H=16.0,9.0
D="/mnt/user-data/outputs/case01/03-data-clean/"
mon=pd.read_csv(D+"monthly.csv"); lane=pd.read_csv(D+"lane_detail.csv"); 
sell=pd.read_csv(D+"seller_breach.csv"); curve=pd.read_csv(D+"promise_curve.csv")
mon["m"]=pd.to_datetime(mon.month)

def page(title, sub):
    fig=plt.figure(figsize=(W,H),dpi=110); fig.patch.set_facecolor(SURF)
    fig.text(0.028,0.945,title,fontsize=21,fontweight="bold",color=INK,va="center")
    fig.text(0.028,0.905,sub,fontsize=11,color=INK2,va="center")
    fig.add_artist(plt.Line2D([0.028,0.972],[0.878,0.878],color=GRID,lw=1.2))
    fig.text(0.028,0.028,"Source: Olist Brazilian e-commerce, Jan 2017 to Aug 2018, 97,300 orders. Freight is charged freight, a cost-to-serve proxy. Refreshed 24 Nov 2026.",
             fontsize=8.5,color=MUTED)
    return fig

def card(fig,x,y,w,h,label,value,note="",accent=INK):
    ax=fig.add_axes([x,y,w,h]); ax.set_axis_off(); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.add_patch(FancyBboxPatch((0.01,0.03),0.98,0.94,boxstyle="round,pad=0.01,rounding_size=0.04",
        fc=CARD,ec=GRID,lw=1.1,transform=ax.transAxes))
    ax.text(0.07,0.72,label,fontsize=9.5,color=INK2,transform=ax.transAxes,va="center")
    ax.text(0.07,0.40,value,fontsize=25,fontweight="bold",color=accent,transform=ax.transAxes,va="center")
    if note: ax.text(0.07,0.14,note,fontsize=8.5,color=MUTED,transform=ax.transAxes,va="center")

def panel(fig,x,y,w,h,title,spec):
    ax=fig.add_axes([x,y,w,h]); ax.set_facecolor(CARD)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2,labelsize=8.5,length=3)
    ax.grid(axis="y",color=GRID,lw=0.8); ax.set_axisbelow(True)
    fig.text(x,y+h+0.052,title,fontsize=12,fontweight="bold",color=INK,va="center")
    fig.text(x,y+h+0.022,spec,fontsize=8.5,color=MUTED,va="center")
    return ax

def pct(v): return f"{v*100:.1f}%"

# ---------------- PAGE 1 ----------------
fig=page("Service and cost overview","Page 1 of 4  ·  Built for the Head of Logistics")
card(fig,0.028,0.745,0.148,0.115,"Orders","97,300")
card(fig,0.186,0.745,0.148,0.115,"Freight % of item value","16.6%","2,218,021 BRL charged")
card(fig,0.344,0.745,0.148,0.115,"Late against promise","8.1%",accent=RED)
card(fig,0.502,0.745,0.148,0.115,"Avg days to deliver","12.5")
card(fig,0.660,0.745,0.148,0.115,"Avg review score","4.13")
card(fig,0.818,0.745,0.154,0.115,"Promise padding","11.8 days",accent=RED)

ax=panel(fig,0.028,0.45,0.44,0.20,"Lateness is seasonal: plan against March, not the average",
         "Line chart  ·  Axis: purchase_month  ·  Values: Late Rate  ·  Constant line at 8.1%")
ax.plot(mon.m,mon.late_rate,color=BLUE,lw=2)
ax.axhline(0.0813,color=RED,lw=1.4,ls="--")
ax.text(mon.m.iloc[1],0.089,"period average 8.1%",fontsize=8,color=RED)
pk=mon.loc[mon.late_rate.idxmax()]
ax.annotate(f"Mar 2018\n{pct(pk.late_rate)}",xy=(pk.m,pk.late_rate),xytext=(-55,-6),
            textcoords="offset points",fontsize=8.5,color=INK,
            arrowprops=dict(arrowstyle="-",color=MUTED,lw=0.9))
ax.yaxis.set_major_formatter(lambda v,p:f"{v*100:.0f}%")

ax=panel(fig,0.532,0.45,0.44,0.20,"Freight share rose while delivery got faster",
         "Line chart  ·  Axis: purchase_month  ·  Values: Freight % of Value  ·  never a second y-axis")
ax.plot(mon.m,mon.freight/mon.gmv,color=BLUE,lw=2)
ax.yaxis.set_major_formatter(lambda v,p:f"{v*100:.0f}%")
ax.annotate("14.2% in Jan 2017",xy=(mon.m.iloc[0],mon.freight.iloc[0]/mon.gmv.iloc[0]),
            xytext=(14,-2),textcoords="offset points",fontsize=8.5,color=INK)
ax.annotate("17.5% by Aug 2018",xy=(mon.m.iloc[-1],mon.freight.iloc[-1]/mon.gmv.iloc[-1]),
            xytext=(-96,6),textcoords="offset points",fontsize=8.5,color=INK)

bands=["under 50 km","50 to 200","200 to 600","600 to 1500","over 1500"]
late=[6.45,6.10,7.54,8.85,12.84]; rev=[4.261,4.275,4.119,4.083,3.963]
ax=panel(fig,0.028,0.115,0.44,0.185,"Distance raises cost and lateness together",
         "Clustered bar  ·  Axis: distance band  ·  Values: Late Rate")
b=ax.bar(bands,late,color=BAR,width=0.55)
for r,v in zip(b,late): ax.text(r.get_x()+r.get_width()/2,v+0.3,f"{v:.1f}%",ha="center",fontsize=8.5,color=INK)
ax.set_ylim(0,15); ax.set_yticks([]); ax.tick_params(axis="x",labelsize=8)

ax=panel(fig,0.532,0.115,0.44,0.185,"One day late nearly triples poor reviews",
         "Clustered bar  ·  Axis: lateness band  ·  Values: share of 1 and 2 star reviews")
lb=["10+ early","3-10 early","0-3 early","0-3 LATE","3-10 late","10+ late"]
pv=[8.86,9.72,11.47,32.14,71.49,78.84]
cols=[BLUE,BLUE,BLUE,RED,RED,RED]
b=ax.bar(lb,pv,color=cols,width=0.6)
for r,v in zip(b,pv): ax.text(r.get_x()+r.get_width()/2,v+1.5,f"{v:.0f}%",ha="center",fontsize=8.5,color=INK)
ax.set_ylim(0,92); ax.set_yticks([]); ax.tick_params(axis="x",labelsize=8)
fig.text(0.532,0.068,"Blue: delivered on time or early.   Red: delivered late.",fontsize=8.5,color=INK2)
fig.savefig("/mnt/user-data/outputs/case01/07-dashboard/page-1-service-and-cost-overview.png",facecolor=SURF)
plt.close(fig)

# ---------------- PAGE 2 ----------------
fig=page("Lanes and the delivery promise","Page 2 of 4  ·  Where the promise is wrong, and by how much")
card(fig,0.028,0.745,0.22,0.115,"Late rate today","8.1%",accent=RED)
card(fig,0.258,0.745,0.22,0.115,"Late rate at the p95 rule","5.0%","38% fewer late orders")
card(fig,0.488,0.745,0.22,0.115,"Late orders avoided a year","1,787")
card(fig,0.718,0.745,0.254,0.115,"Change to the average promise","+2.9 days","42 lanes still get a shorter promise")

big=lane[lane.orders>=200].copy()
ax=panel(fig,0.028,0.46,0.44,0.19,"SP to RJ is the problem: high volume and high lateness",
         "Scatter  ·  X: avg_days  ·  Y: cur_late  ·  Size: orders  ·  LaneDetail table")
ax.scatter(big.avg_days,big.cur_late*100,s=big.orders/18,color=BLUE,alpha=0.45,edgecolor="none")
hl=big[big.lane.isin(["SP to RJ","SP to AL","SP to MA"])]
ax.scatter(hl.avg_days,hl.cur_late*100,s=hl.orders/18,color=RED,alpha=0.85,edgecolor="none")
for _,r in hl.iterrows():
    off=(10,6) if r.lane=="SP to RJ" else (-118,4)
    ax.annotate(f"{r.lane}  {r.orders:,.0f} orders",xy=(r.avg_days,r.cur_late*100),
                xytext=off,textcoords="offset points",fontsize=8.5,color=INK)
ax.set_xlabel("average days from purchase to delivery",fontsize=8.5,color=INK2)
ax.set_ylabel("late rate %",fontsize=8.5,color=INK2)

ax=panel(fig,0.532,0.46,0.44,0.19,"Why the padding cannot be cut uniformly",
         "Line chart  ·  Axis: days_removed  ·  Values: late_rate  ·  PromiseCurve table")
ax.plot(curve.days_removed,curve.late_rate*100,color=BLUE,lw=2,marker="o",ms=4)
ax.axhline(8.13,color=RED,lw=1.2,ls="--")
ax.text(0.3,9.6,"today, 8.1% late",fontsize=8.5,color=RED)
ax.annotate("3 days off the promise\nnearly doubles lateness",xy=(3,13.06),xytext=(4.2,22),
            fontsize=9,color=INK,arrowprops=dict(arrowstyle="->",color=MUTED,lw=1))
ax.set_xlabel("days removed from every lane's promise",fontsize=8.5,color=INK2)
ax.set_ylabel("late rate %",fontsize=8.5,color=INK2)

ax=panel(fig,0.028,0.075,0.944,0.23,"Lane table: where the promise is wrong, and by how much",
         "Table  ·  Columns: lane, orders, promise today, promise at p95, change, late today  ·  Conditional formatting on change")
ax.set_axis_off()
t=big.copy(); t["chg"]=t.p95-t.cur_promise
t=pd.concat([t.nlargest(4,"chg"),t.nsmallest(3,"chg")])
cols=["Lane","Orders","Promise today","Promise at p95","Change","Late today"]
xs=[0.02,0.17,0.30,0.46,0.62,0.76]
for cx,c in zip(xs,cols): ax.text(cx,0.90,c,fontsize=9.5,fontweight="bold",color=INK2,transform=ax.transAxes)
ax.add_artist(plt.Line2D([0.02,0.95],[0.84,0.84],color=GRID,lw=1,transform=ax.transAxes))
for i,(_,r) in enumerate(t.iterrows()):
    yy=0.75-i*0.105; c=RED if r.chg>0 else BLUE
    vals=[r.lane,f"{r.orders:,.0f}",f"{r.cur_promise:.1f} days",f"{r.p95:.1f} days",
          f"{r.chg:+.1f} days",f"{r.cur_late*100:.1f}%"]
    for j,(cx,v) in enumerate(zip(xs,vals)):
        ax.text(cx,yy,v,fontsize=9.5,color=(c if j in (4,) else INK),
                fontweight=("bold" if j==4 else "normal"),transform=ax.transAxes)
fig.savefig("/mnt/user-data/outputs/case01/07-dashboard/page-2-lanes-and-promise.png",facecolor=SURF)
plt.close(fig)

# ---------------- PAGE 3 ----------------
fig=page("Seller dispatch enforcement","Page 3 of 4  ·  The cheapest lever, because the problem is concentrated")
card(fig,0.028,0.745,0.22,0.115,"Dispatch deadline breaches","8,702","8.9% of orders")
card(fig,0.258,0.745,0.22,0.115,"Late when deadline breached","24.8%",accent=RED)
card(fig,0.488,0.745,0.22,0.115,"Late when deadline met","6.5%")
card(fig,0.718,0.745,0.254,0.115,"Odds of lateness after a breach","4.7x","95% CI 4.45 to 4.98")

top=sell.nlargest(20,"breaches").iloc[::-1]
ax=panel(fig,0.028,0.085,0.44,0.56,"The top 100 sellers carry 54% of all breaches",
         "Bar chart  ·  Axis: seller_ref  ·  Values: breaches  ·  SellerBreach table, top 20")
ax.barh(top.seller_ref,top.breaches,color=BAR,height=0.62)
for i,(r,v) in enumerate(zip(top.seller_ref,top.breaches)):
    ax.text(v+4,i,f"{v:,.0f}",va="center",fontsize=8,color=INK)
ax.set_xlim(0,top.breaches.max()*1.18); ax.set_xticks([]); ax.tick_params(axis="y",labelsize=7.5)
ax.grid(False)

ax=panel(fig,0.532,0.085,0.44,0.56,"Breaching sellers are worse on everything, not just speed",
         "Table  ·  Columns: seller_ref, orders, breaches, breach rate, late rate, avg review")
ax.set_axis_off()
t=sell.nlargest(10,"breaches")
cols=["Seller","Orders","Breaches","Breach rate","Late rate","Avg review"]
xs=[0.02,0.20,0.36,0.54,0.72,0.87]
for cx,c in zip(xs,cols): ax.text(cx,0.95,c,fontsize=9.5,fontweight="bold",color=INK2,transform=ax.transAxes)
ax.add_artist(plt.Line2D([0.02,0.98],[0.91,0.91],color=GRID,lw=1,transform=ax.transAxes))
for i,(_,r) in enumerate(t.iterrows()):
    yy=0.83-i*0.082
    vals=[r.seller_ref,f"{r.orders:,.0f}",f"{r.breaches:,.0f}",f"{r.breach_rate*100:.1f}%",
          f"{r.late*100:.1f}%",f"{r.review:.2f}"]
    for j,(cx,v) in enumerate(zip(xs,vals)):
        col=RED if (j==4 and r.late>0.15) or (j==5 and r.review<3.5) else INK
        ax.text(cx,yy,v,fontsize=9.5,color=col,transform=ax.transAxes)
ax.text(0.02,0.04,"Red marks a late rate above 15% or an average review below 3.5.",
        fontsize=8.5,color=INK2,transform=ax.transAxes)
fig.savefig("/mnt/user-data/outputs/case01/07-dashboard/page-3-dispatch-enforcement.png",facecolor=SURF)
plt.close(fig)

# ---------------- PAGE 4 ----------------
fig=page("Method and limitations","Page 4 of 4  ·  Read this before acting on anything in the other three pages")
blocks=[("What this is built from",
  ["Olist Brazilian e-commerce, 97,300 orders, 5 Jan 2017 to 29 Aug 2018, licence CC BY-NC-SA 4.0.",
   "Cleaned by 01_build_clean_base.sql. Every rule and its row count is in CLEANING-LOG.md.",
   "Item value and freight reconcile to source to the cent: 13,329,378 and 2,218,021 BRL."]),
 ("What the numbers can and cannot carry",
  ["Freight is the amount charged to the customer, not the carrier's cost. It is a cost-to-serve proxy.",
   "Carrier identity is absent, so renegotiation lands at lane level, not carrier level.",
   "No returns, refunds or service-contact costs exist here, so the cost of a late order is understated.",
   "Repeat purchasing is near absent (about 3% of customers), so damage runs through review score,",
   "    using a published benchmark of 5 to 9 percent of revenue per star, not a measurement from this data."]),
 ("Three things found that change how the data reads",
  ["Split shipments record the first arrival as the delivery date, so their lateness is understated.",
   "    They show 1.4% late yet a 47% poor-review rate. Excluded from timing conclusions.",
   "Lane percentiles are computed in sample. In production, set the promise from a trailing 90-day window.",
   "Lateness uses timestamps. On a whole-day definition the rate is 6.8 rather than 8.1 percent."]),
 ("What the three tests found",
  ["A missed dispatch deadline makes a late delivery 4.71 times more likely (95% CI 4.45 to 4.98).",
   "Poor reviews run 9.2% when on time and 62.4% when late: a 53 point gap, relative risk 6.75.",
   "The promise is padded by 11.81 days (95% CI 11.74 to 11.87) and still missed one time in twelve."])]
y=0.835
for head,lines in blocks:
    fig.text(0.028,y,head,fontsize=13,fontweight="bold",color=INK)
    y-=0.042
    for l in lines:
        fig.text(0.028,y,l,fontsize=10.5,color=INK2); y-=0.032
    y-=0.028
fig.savefig("/mnt/user-data/outputs/case01/07-dashboard/page-4-method-and-limitations.png",facecolor=SURF)
plt.close(fig)
print("done")
