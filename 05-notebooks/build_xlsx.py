import json, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

C=json.load(open("constants.json"))
lane=pd.read_csv("lane_detail.csv"); curve=pd.read_csv("promise_curve.csv")
mon=pd.read_csv("monthly.csv"); sell=pd.read_csv("seller_breach.csv")

AR="Arial"
H1=Font(name=AR,size=14,bold=True); H2=Font(name=AR,size=11,bold=True,color="FFFFFF")
BOLD=Font(name=AR,size=10,bold=True); BODY=Font(name=AR,size=10)
IN=Font(name=AR,size=10,color="0000FF")                 # editable input
LINK=Font(name=AR,size=10,color="008000")               # link to another sheet
HDRFILL=PatternFill("solid",fgColor="1F3864")
KEYFILL=PatternFill("solid",fgColor="FFFF00")
BANDFILL=PatternFill("solid",fgColor="F2F2F2")
THIN=Border(*[Side(style="thin",color="BFBFBF")]*4)
MONEY='#,##0;(#,##0);-'; PCT='0.0%'; NUM='#,##0'; DEC='0.00'

wb=Workbook()

def hdr(ws,row,labels,widths=None):
    for i,l in enumerate(labels,start=1):
        c=ws.cell(row=row,column=i,value=l); c.font=H2; c.fill=HDRFILL
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    if widths:
        for i,w in enumerate(widths,start=1): ws.column_dimensions[get_column_letter(i)].width=w

# ---------------- README ----------------
ws=wb.active; ws.title="README"
ws.column_dimensions["A"].width=110
lines=[("Case 1: Reducing cost-to-serve in e-commerce logistics",H1),
 ("Decision model for the Head of Logistics",BOLD),("",BODY),
 ("What this workbook does",BOLD),
 ("Sizes the three levers available on cost-to-serve and delivery reliability, and lets you change every",BODY),
 ("assumption behind the numbers. Nothing is hardcoded inside a formula.",BODY),("",BODY),
 ("How to use it",BOLD),
 ("1. Open Assumptions. Set the scenario in cell B3 to Base, Downside or Upside.",BODY),
 ("2. Change any blue figure on that sheet. Everything downstream recalculates.",BODY),
 ("3. Dispatch and Promise show the two main levers. Sensitivity shows the range.",BODY),
 ("4. LaneDetail, Monthly and SellerBreach hold the underlying measured data.",BODY),("",BODY),
 ("Colour legend",BOLD),
 ("Blue text: an input you may edit. Black text: a formula. Green text: a link to another sheet.",BODY),
 ("Yellow fill: a key assumption that materially moves the answer.",BODY),("",BODY),
 ("Data source",BOLD),
 ("Brazilian E-Commerce Public Dataset by Olist (Kaggle, olistbr/brazilian-ecommerce), licence CC BY-NC-SA 4.0.",BODY),
 ("97,300 orders, January 2017 to August 2018. All money in Brazilian reais (BRL).",BODY),
 ("Cleaned by 04-sql/01_build_clean_base.sql. Cleaning rules in 03-data-clean/CLEANING-LOG.md.",BODY),
 ("Refreshed: 24 November 2026.",BODY),("",BODY),
 ("The one number to treat with caution",BOLD),
 ("The revenue effect per star is a benchmark from another industry, not a measurement from this data.",BODY),
 ("It sits in one cell (Assumptions B7) so you can replace it. See Notes for the full limitation list.",BODY)]
for i,(t,f) in enumerate(lines,start=1):
    c=ws.cell(row=i,column=1,value=t); c.font=f

# ---------------- Assumptions ----------------
a=wb.create_sheet("Assumptions")
a["A1"]="Assumptions and scenario inputs"; a["A1"].font=H1
a["A3"]="Scenario"; a["A3"].font=BOLD
a["B3"]="Base"; a["B3"].font=IN; a["B3"].fill=KEYFILL; a["B3"].border=THIN
dv=DataValidation(type="list",formula1='"Base,Downside,Upside"',allow_blank=False)
a.add_data_validation(dv); dv.add(a["B3"])
a["C3"]="Change this cell to switch every scenario value below"; a["C3"].font=BODY
hdr(a,5,["Assumption","Base","Downside","Upside","Active","Unit","Source"],[52,12,12,12,14,16,46])
lev=[("Preventable share of dispatch-breach lateness",0.6,0.4,0.8,PCT,"share","Analyst judgement, stated not measured"),
     ("Revenue effect per 1-star rating gain",0.07,0.05,0.09,PCT,"of revenue","Luca 2011 rev 2016, HBS WP 12-016: 5 to 9 pct"),
     ("Cost per late order (service plus goodwill)",0,0,0,MONEY,"BRL","Not in the data. Default zero: set your own"),
     ("Service target for the promise rule",95,90,95,NUM,"percentile","Business choice, see Promise sheet")]
for i,(lab,b,dn,up,fmt,unit,src) in enumerate(lev):
    rw=6+i
    a.cell(row=rw,column=1,value=lab).font=BODY
    for col,val in ((2,b),(3,dn),(4,up)):
        c=a.cell(row=rw,column=col,value=val); c.font=IN; c.number_format=fmt; c.border=THIN
        if i in (0,1,2): c.fill=KEYFILL
    c=a.cell(row=rw,column=5,value=f"=INDEX(B{rw}:D{rw},MATCH($B$3,$B$5:$D$5,0))")
    c.font=BOLD; c.number_format=fmt; c.border=THIN
    a.cell(row=rw,column=6,value=unit).font=BODY
    a.cell(row=rw,column=7,value=src).font=BODY

a["A11"]="Measured from the cleaned data. Do not edit."; a["A11"].font=BOLD
hdr(a,12,["Measure","Value","Unit","Source"],[52,14,16,46])
meas=[("Months in the measured period",C["months"],DEC,"months","fact_orders"),
 ("Delivered orders measured",C["delivered_orders"],NUM,"orders","fact_orders"),
 ("Reviews carrying a score",C["reviews"],NUM,"reviews","fact_orders"),
 ("Item value, period",C["gmv_period"],MONEY,"BRL","fact_orders"),
 ("Freight charged, period",C["freight_period"],MONEY,"BRL","fact_orders"),
 ("Orders that breached the dispatch deadline",C["breached_orders"],NUM,"orders","fact_orders"),
 ("Late rate when the deadline was breached",C["late_rate_breached"],PCT,"share","fact_orders"),
 ("Late rate when the deadline was met",C["late_rate_met"],PCT,"share","fact_orders"),
 ("Poor review rate, late delivery",C["poor_rate_late"],PCT,"share","fact_orders"),
 ("Poor review rate, on time or early",C["poor_rate_ontime"],PCT,"share","fact_orders"),
 ("Review points lost per late order",C["review_points_per_late"],DEC,"stars","fact_orders"),
 ("Current late rate",C["cur_late_rate"],PCT,"share","fact_orders"),
 ("Late rate under the 90th percentile rule",C["late_rate_p90"],PCT,"share","LaneDetail"),
 ("Late rate under the 95th percentile rule",C["late_rate_p95"],PCT,"share","LaneDetail"),
 ("Average promise today, volume weighted",C["avg_promise_today"],DEC,"days","LaneDetail"),
 ("Average promise under the 90th percentile rule",C["avg_promise_p90"],DEC,"days","LaneDetail"),
 ("Average promise under the 95th percentile rule",C["avg_promise_p95"],DEC,"days","LaneDetail"),
 ("Lane freight charged above model, period",C["excess_freight_period"],MONEY,"BRL","LaneDetail"),
 ("Worst month late rate",C["peak_late_rate"],PCT,"share","Monthly"),
 ("Orders covered by lane-specific rules",C["lane_coverage_orders"],NUM,"orders","LaneDetail")]
for i,(lab,val,fmt,unit,src) in enumerate(meas):
    rw=13+i
    a.cell(row=rw,column=1,value=lab).font=BODY
    c=a.cell(row=rw,column=2,value=val); c.font=BODY; c.number_format=fmt; c.border=THIN
    a.cell(row=rw,column=3,value=unit).font=BODY
    a.cell(row=rw,column=4,value=src).font=BODY
    if i%2: 
        for col in range(1,5): a.cell(row=rw,column=col).fill=BANDFILL

# ---------------- Dispatch ----------------
dsp=wb.create_sheet("Dispatch")
dsp["A1"]="Lever 1: enforce seller dispatch deadlines"; dsp["A1"].font=H1
dsp["A2"]="Every value below is a formula. Change the scenario or any blue input on Assumptions."; dsp["A2"].font=BODY
hdr(dsp,4,["Step","Value","Unit","Where it comes from"],[56,16,14,52])
rows=[("Orders that breached the dispatch deadline","=Assumptions!B18",NUM,"orders","Measured"),
 ("Late rate when breached","=Assumptions!B19",PCT,"share","Measured"),
 ("Late rate when met","=Assumptions!B20",PCT,"share","Measured"),
 ("Excess late orders over the period","=B5*(B6-B7)",NUM,"orders","Breached orders times the gap in late rates"),
 ("Excess late orders a year","=B8*12/Assumptions!B13",NUM,"orders","Annualised over the measured months"),
 ("Preventable share (scenario)","=Assumptions!E6",PCT,"share","Assumption"),
 ("Late orders avoided a year","=B9*B10",NUM,"orders","Annual excess times preventable share"),
 ("Poor reviews avoided a year","=B11*(Assumptions!B21-Assumptions!B22)",NUM,"reviews","Gap in poor review rates"),
 ("Review points recovered, period","=B8*B10*Assumptions!B23",NUM,"stars","Avoided late orders times points lost each"),
 ("Steady-state rating uplift","=B13/Assumptions!B15",'0.0000',"stars","Points recovered over the review base"),
 ("Revenue effect per star (scenario)","=Assumptions!E7",PCT,"of revenue","Assumption, benchmark from another industry"),
 ("Item value a year","=Assumptions!B16*12/Assumptions!B13",MONEY,"BRL","Annualised"),
 ("Value from the rating effect, a year","=B14*B15*B16",MONEY,"BRL","Rating uplift times elasticity times revenue"),
 ("Cost per late order (scenario)","=Assumptions!E8",MONEY,"BRL","Assumption, default zero"),
 ("Value from avoided late orders, a year","=B11*B18",MONEY,"BRL","Late orders avoided times cost each"),
 ("Total annual value of this lever","=B17+B19",MONEY,"BRL","Sum of the two value lines")]
for i,(lab,f,fmt,unit,src) in enumerate(rows):
    rw=5+i
    dsp.cell(row=rw,column=1,value=lab).font=BODY
    c=dsp.cell(row=rw,column=2,value=f); c.number_format=fmt; c.border=THIN
    c.font=LINK if f.startswith("=Assumptions") else BODY
    dsp.cell(row=rw,column=3,value=unit).font=BODY
    dsp.cell(row=rw,column=4,value=src).font=BODY
for col in range(1,5):
    dsp.cell(row=20,column=col).font=BOLD; dsp.cell(row=20,column=col).fill=BANDFILL
dsp["A23"]="Targeting note: the top 100 sellers by breach count carry 54.3 percent of all breaches. See SellerBreach."
dsp["A23"].font=BODY

# ---------------- Promise ----------------
pr=wb.create_sheet("Promise")
pr["A1"]="Lever 2: set the delivery promise per lane"; pr["A1"].font=H1
pr["A2"]="Change the service target on Assumptions row 9 to compare the 90th and 95th percentile rules."; pr["A2"].font=BODY
hdr(pr,4,["Step","Value","Unit","Where it comes from"],[56,16,14,52])
prows=[("Service target (scenario)","=Assumptions!E9",NUM,"percentile","Assumption"),
 ("Current late rate","=Assumptions!B24",PCT,"share","Measured"),
 ("Late rate under the chosen rule","=IF(B5=95,Assumptions!B26,Assumptions!B25)",PCT,"share","Measured per lane, then pooled"),
 ("Change in late rate","=B7-B6",PCT,"points","Negative is better"),
 ("Delivered orders a year","=Assumptions!B14*12/Assumptions!B13",NUM,"orders","Annualised"),
 ("Late orders avoided a year","=-B8*B9",NUM,"orders","Change in rate times annual orders"),
 ("Average promise today","=Assumptions!B27",DEC,"days","Measured, volume weighted"),
 ("Average promise under the chosen rule","=IF(B5=95,Assumptions!B29,Assumptions!B28)",DEC,"days","Measured per lane, then pooled"),
 ("Change in the promise","=B12-B11",DEC,"days","Positive means customers are promised a later date"),
 ("Promised wait days removed a year","=-B13*B9",NUM,"days","Change in promise times annual orders"),
 ("Poor reviews avoided a year","=B10*(Assumptions!B21-Assumptions!B22)",NUM,"reviews","Gap in poor review rates"),
 ("Value from the rating effect, a year","=B10*Assumptions!B23/Assumptions!B15*Dispatch!B15*Dispatch!B16",MONEY,"BRL","Same chain as the dispatch lever"),
 ("Value from avoided late orders, a year","=B10*Dispatch!B18",MONEY,"BRL","Late orders avoided times cost each"),
 ("Total annual value of this lever","=B16+B17",MONEY,"BRL","Sum of the two value lines")]
for i,(lab,f,fmt,unit,src) in enumerate(prows):
    rw=5+i
    pr.cell(row=rw,column=1,value=lab).font=BODY
    c=pr.cell(row=rw,column=2,value=f); c.number_format=fmt; c.border=THIN
    c.font=LINK if f.startswith("=Assumptions") else BODY
    pr.cell(row=rw,column=3,value=unit).font=BODY
    pr.cell(row=rw,column=4,value=src).font=BODY
for col in range(1,5):
    pr.cell(row=18,column=col).font=BOLD; pr.cell(row=18,column=col).fill=BANDFILL
pr["A21"]="What a uniform cut to the promise would cost. Measured, not modelled."; pr["A21"].font=BOLD
hdr(pr,22,["Days removed from every lane's promise","Resulting late rate"],[40,22])
for i,row in curve.iterrows():
    rw=23+i
    c=pr.cell(row=rw,column=1,value=int(row.days_removed)); c.font=BODY; c.number_format=NUM
    c2=pr.cell(row=rw,column=2,value=float(row.late_rate)); c2.font=BODY; c2.number_format=PCT
pr.cell(row=23+len(curve)+1,column=1,
  value="Read: three days off the promise nearly doubles lateness. The pad covers lane variance, so it cannot be cut uniformly.").font=BODY

# ---------------- Sensitivity ----------------
sn=wb.create_sheet("Sensitivity")
sn["A1"]="Sensitivity: annual value of dispatch enforcement (BRL)"; sn["A1"].font=H1
sn["A2"]="Rows: preventable share of breach lateness. Columns: revenue effect per star. Cost per late order is taken from Assumptions."
sn["A2"].font=BODY
prevs=[0.3,0.4,0.5,0.6,0.7,0.8,0.9]; elasts=[0.04,0.05,0.06,0.07,0.08,0.09,0.10]
sn.column_dimensions["A"].width=22
sn.cell(row=4,column=1,value="Preventable share").font=H2; sn.cell(row=4,column=1).fill=HDRFILL
for j,e in enumerate(elasts):
    c=sn.cell(row=4,column=2+j,value=e); c.font=H2; c.fill=HDRFILL; c.number_format=PCT
    sn.column_dimensions[get_column_letter(2+j)].width=13
for i,p in enumerate(prevs):
    rw=5+i
    c=sn.cell(row=rw,column=1,value=p); c.font=BOLD; c.number_format=PCT; c.fill=BANDFILL
    for j,e in enumerate(elasts):
        col=get_column_letter(2+j)
        f=(f"=$A{rw}*Dispatch!$B$8*Assumptions!$B$23/Assumptions!$B$15*{col}$4*Dispatch!$B$16"
           f"+$A{rw}*Dispatch!$B$9*Assumptions!$E$8")
        cc=sn.cell(row=rw,column=2+j,value=f); cc.font=BODY; cc.number_format=MONEY; cc.border=THIN
sn.cell(row=13,column=1,value="Base case is 60 percent preventable at 7 percent per star.").font=BODY
sn.cell(row=14,column=1,value="Every figure here excludes service and refund costs, which are absent from the data.").font=BODY

# ---------------- data sheets ----------------
def datasheet(name,frame,cols,fmts,widths,title,note=None):
    s=wb.create_sheet(name); s["A1"]=title; s["A1"].font=H1
    if note: s["A2"]=note; s["A2"].font=BODY
    hdr(s,4,cols,widths)
    for i,(_,row) in enumerate(frame.iterrows()):
        rw=5+i
        for j,(key,fmt) in enumerate(fmts):
            v=row[key]
            c=s.cell(row=rw,column=1+j,value=(float(v) if isinstance(v,float) else v))
            c.font=BODY; c.border=THIN
            if fmt: c.number_format=fmt
        if i%2:
            for j in range(len(fmts)): s.cell(row=rw,column=1+j).fill=BANDFILL
    s.freeze_panes="A5"
    return s

lane2=lane.copy()
lane2["late_rate_pct"]=lane2.cur_late
lane2["p95_change"]=lane2.p95-lane2.cur_promise
datasheet("LaneDetail",lane2,
 ["Lane","Orders","Promise today (days)","Avg actual (days)","Promise at p90 (days)","Promise at p95 (days)",
  "Change at p95 (days)","Late today","Late at p90","Late at p95","Freight (BRL)","Freight above model (BRL)","Avg review"],
 [("lane",None),("orders",NUM),("cur_promise",DEC),("avg_days",DEC),("p90",DEC),("p95",DEC),("p95_change",DEC),
  ("cur_late",PCT),("late_p90",PCT),("late_p95",PCT),("freight_total",MONEY),("excess_freight",MONEY),("avg_review",DEC)],
 [14,10,16,14,16,16,16,11,11,11,14,18,11],
 "Lane detail: 100 lanes with 50 or more orders, covering 96.8 percent of orders",
 "Promise at p90 and p95 is that lane's own delivery time distribution. Freight above model is the residual from freight ~ log(distance) + log(weight) + items.")

mon2=mon.copy(); mon2["freight_pct"]=mon2.freight/mon2.gmv
datasheet("Monthly",mon2,
 ["Month","Orders","Item value (BRL)","Freight (BRL)","Freight share","Avg days","Late rate","Avg review"],
 [("month",None),("orders",NUM),("gmv",MONEY),("freight",MONEY),("freight_pct",PCT),("avg_days",DEC),("late_rate",PCT),("avg_review",DEC)],
 [12,10,18,16,13,11,11,11],
 "Monthly trend","Lateness peaks at 21.4 percent in March 2018 against an 8.1 percent average, so plan against the peak.")

datasheet("SellerBreach",sell,
 ["Seller ref","Seller id (hashed)","Orders","Dispatch breaches","Breach rate","Late rate","Avg review","Freight (BRL)"],
 [("seller_ref",None),("primary_seller_id",None),("orders",NUM),("breaches",NUM),("breach_rate",PCT),("late",PCT),("review",DEC),("freight",MONEY)],
 [11,36,10,16,12,11,11,14],
 "Top 100 sellers by dispatch breach count (20 or more orders each)",
 "These 100 sellers carry 54.3 percent of all dispatch deadline breaches, which is what makes enforcement cheap.")

# ---------------- Notes ----------------
nt=wb.create_sheet("Notes"); nt.column_dimensions["A"].width=112
notes=[("Notes, limitations and change log",H1),("",BODY),
 ("Source and grain",BOLD),
 ("Brazilian E-Commerce Public Dataset by Olist, Kaggle (olistbr/brazilian-ecommerce). Licence CC BY-NC-SA 4.0.",BODY),
 ("Grain: one row per order. 97,300 orders, 5 January 2017 to 29 August 2018. Currency: BRL.",BODY),
 ("Built from 03-data-clean/fact_orders.parquet. Refreshed 24 November 2026.",BODY),("",BODY),
 ("Limitations, in the order they matter",BOLD),
 ("1. Freight is the amount charged to the customer, not the carrier's cost. It is a cost-to-serve proxy.",BODY),
 ("2. The revenue effect per star is a benchmark from Luca 2011 (independent restaurants on Yelp, 5 to 9 percent",BODY),
 ("   per star), not a measurement from this marketplace. It is the weakest number in the model.",BODY),
 ("3. The rating effect is diluted by construction: avoided orders move an average built on 95,560 reviews.",BODY),
 ("   At seller level, where buyers actually look, the effect is concentrated and larger. This data cannot size that.",BODY),
 ("4. Service contact, refund and goodwill costs are absent from the data, so cost per late order defaults to zero.",BODY),
 ("   The true value of every lever is therefore higher than modelled: direction known, magnitude not.",BODY),
 ("5. Per-lane promise percentiles are computed in-sample, which flatters them. In production, set the promise",BODY),
 ("   from a trailing 90-day window and refresh monthly.",BODY),
 ("6. Repeat purchasing is almost absent (about 3 percent of customers), so no churn-based damage model is possible.",BODY),
 ("7. Carrier identity is not in the data, so renegotiation lands at lane level, not carrier level.",BODY),
 ("8. Split shipments (1.3 percent of orders) record the first arrival as the delivery date, so their lateness is",BODY),
 ("   understated. They are excluded from timing conclusions. See 08-report/stage-4-5-findings.md section 6.",BODY),
 ("9. Lateness uses timestamps. On a whole-day definition the rate is 6.79 rather than 8.13 percent.",BODY),("",BODY),
 ("Making this workbook refresh itself",BOLD),
 ("The data sheets are a snapshot. To make them refreshable in Excel, use Data, Get Data, From File, From Parquet",BODY),
 ("and point at 03-data-clean/fact_orders.parquet, or paste this into the Power Query advanced editor:",BODY),
 ('let Source = Parquet.Document(File.Contents("fact_orders.parquet")) in Source',BODY),
 ("Then rebuild the LaneDetail, Monthly and SellerBreach sheets as query output tables. The Assumptions, Dispatch,",BODY),
 ("Promise and Sensitivity sheets need no change, since they reference Assumptions rather than the data sheets.",BODY),("",BODY),
 ("Change log",BOLD),
 ("24 Nov 2026: built. Hypotheses cut from six to three. Period and annual figures separated after a review found",BODY),
 ("   two 20-month figures reported as annual. All annual lines in this workbook are annualised explicitly.",BODY)]
for i,(t,f) in enumerate(notes,start=1):
    nt.cell(row=i,column=1,value=t).font=f

for s in wb.worksheets: s.sheet_view.showGridLines=False
out="/mnt/user-data/outputs/case01/06-excel/cost-to-serve-model.xlsx"
import os; os.makedirs(os.path.dirname(out),exist_ok=True)
wb.save(out); print("saved",out)
