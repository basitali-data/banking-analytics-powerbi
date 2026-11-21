"""Writes two report pages (PBIR format) into data/banking.Report. Run with Power BI Desktop closed, then open data/banking.pbip."""
import json, pathlib, shutil
R = pathlib.Path(__file__).parent / "data" / "banking.Report" / "definition" / "pages"
VS = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
PS = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"

def m(t, p): return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": p}}, "queryRef": f"{t}.{p}", "nativeQueryRef": p}
def c(t, p): return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": p}}, "queryRef": f"{t}.{p}", "nativeQueryRef": p}
def lit(s): return {"expr": {"Literal": {"Value": f"'{s}'"}}}

def visual(name, vtype, x, y, w, h, roles, title):
    return {"$schema": VS, "name": name, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h},
            "visual": {"visualType": vtype, "query": {"queryState": {r: {"projections": p} for r, p in roles.items()}},
                       "visualContainerObjects": {"title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": lit(title)}}]}}}

CH, LN, D = "fact_channel_activity", "fact_loan_portfolio", "dim_date"
pages = {
 "p1digital": ("Digital Channels", [
   visual("k1", "card", 20, 20, 300, 140, {"Values": [m(CH, "Active Users")]}, "Active users"),
   visual("k2", "card", 340, 20, 300, 140, {"Values": [m(CH, "Digital Share %")]}, "Digital share of users"),
   visual("k3", "card", 660, 20, 300, 140, {"Values": [m(CH, "Total Transactions")]}, "Transactions"),
   visual("s1", "slicer", 980, 20, 420, 140, {"Values": [c(CH, "segment")]}, "Customer segment"),
   visual("s2", "slicer", 1420, 20, 480, 140, {"Values": [c(CH, "region")]}, "Region"),
   visual("l1", "lineChart", 20, 180, 1180, 420, {"Category": [c(D, "month_start")], "Y": [m(CH, "Active Users")], "Series": [c(CH, "channel")]}, "Active users by channel over time (branch to digital shift)"),
   visual("b1", "clusteredBarChart", 1220, 180, 680, 420, {"Category": [c(CH, "channel")], "Y": [m(CH, "Total Transactions")]}, "Transactions by channel"),
   visual("l2", "lineChart", 20, 620, 1180, 440, {"Category": [c(D, "month_start")], "Y": [m(CH, "Digital Share %")]}, "Digital share trend"),
   visual("t1", "tableEx", 1220, 620, 680, 440, {"Values": [c(CH, "channel"), m(CH, "Active Users"), m(CH, "Total Transactions"), m(CH, "Digital Users")]}, "Channel summary"),
 ]),
 "p2risk": ("Credit Risk & Portfolio", [
   visual("k1", "card", 20, 20, 360, 140, {"Values": [m(LN, "Outstanding (AED)")]}, "Outstanding (AED)"),
   visual("k2", "card", 400, 20, 300, 140, {"Values": [m(LN, "PAR 30+ %")]}, "Portfolio at risk 30+"),
   visual("k3", "card", 720, 20, 300, 140, {"Values": [m(LN, "NPL 90+ %")]}, "Non-performing 90+"),
   visual("k4", "card", 1040, 20, 320, 140, {"Values": [m(LN, "Write-offs (AED)")]}, "Write-offs (AED)"),
   visual("s1", "slicer", 1380, 20, 520, 140, {"Values": [c(LN, "product")]}, "Product"),
   visual("l1", "lineChart", 20, 180, 1180, 420, {"Category": [c(D, "month_start")], "Y": [m(LN, "PAR 30+ %")], "Series": [c(LN, "product")]}, "PAR 30+ trend by product"),
   visual("b1", "clusteredBarChart", 1220, 180, 680, 420, {"Category": [c(LN, "product")], "Y": [m(LN, "Outstanding (AED)")]}, "Outstanding by product"),
   visual("b2", "clusteredColumnChart", 20, 620, 1180, 440, {"Category": [c(LN, "region")], "Y": [m(LN, "NPL 90+ %")]}, "Non-performing 90+ by region"),
   visual("t1", "tableEx", 1220, 620, 680, 440, {"Values": [c(LN, "product"), m(LN, "Outstanding (AED)"), m(LN, "PAR 30+ %"), m(LN, "NPL 90+ %")]}, "Risk summary by product"),
 ]),
}
for d in R.iterdir():
    if d.is_dir(): shutil.rmtree(d)
for pid, (title, vis) in pages.items():
    pd = R / pid; (pd / "visuals").mkdir(parents=True, exist_ok=True)
    (pd / "page.json").write_text(json.dumps({"$schema": PS, "name": pid, "displayName": title, "displayOption": "FitToPage", "height": 1080, "width": 1920}, indent=2), encoding="utf-8")
    for v in vis:
        vd = pd / "visuals" / v["name"]; vd.mkdir(parents=True, exist_ok=True)
        (vd / "visual.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
pj = R / "pages.json"; meta = json.loads(pj.read_text(encoding="utf-8"))
meta["pageOrder"] = list(pages); meta["activePageName"] = "p1digital"
pj.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("pages written")
