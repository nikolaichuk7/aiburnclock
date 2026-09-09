#!/usr/bin/env python3
"""
aiburnclock.org — data pipeline + static site builder.

Sources (all public, all linked on the methodology page):
  Treasury "Debt to the Penny"           daily total public debt
  USAspending.gov                        federal contract obligations whose descriptions name AI, by FY / state / recipient / agency
  Census NST-EST2024                     state population
  Census Annual Survey of State Govt Finances  state debt outstanding (optional file data/state-debt.json)
  Gartner press releases (2026)          AI spend growth parameters (static, cited)
  XERJ measurements (2026)               retrieval-first ratios (static, cited)

Run:  python3 build.py            -> refreshes data/*.json and writes site/ (index, 51 state pages, widget, data.json)
      python3 build.py --no-fetch -> rebuild site from cached data
"""
import csv, json, os, sys, time, urllib.request, html
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"; SITE = HERE / "site"
UA = {"User-Agent": "Mozilla/5.0 (aiburnclock.org data pipeline; contact: hello@aiburnclock.org)", "content-type": "application/json"}
KW = ["artificial intelligence", "machine learning", "large language model", "generative AI", "LLM", "AI-enabled", "natural language processing"]
FY = {"FY2025": ("2024-10-01", "2025-09-30"), "FY2026": ("2025-10-01", "2026-09-30")}

STATES = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}

# ---- parameters shown on the page with their sources; every one is a slider ----
PARAMS = {
  "inference_share": {"default": 0.25, "min": 0.05, "max": 0.60, "label": "share of AI spend that is model inference (tokens)",
                      "note": "Gartner: AI models and platforms are the fastest-growing slice (+63 % in 2026) but infrastructure is >45 % of the total; 25 % is a middle estimate. Move it."},
  "agent_share":     {"default": 0.40, "min": 0.10, "max": 0.90, "label": "share of inference done by agents that read files and documents",
                      "note": "Coding agents, document assistants, RAG pipelines. No public census exists; 40 % is an estimate. Move it."},
  "overhead":        {"default": 0.63, "min": 0.30, "max": 0.97, "label": "share of that reading an index would have avoided",
                      "note": "Measured: 2.7x fewer output tokens on real coding tasks (xerj.org case study) gives 1 - 1/2.7 = 63 %; on one Next.js codebase, 16x to 47x less read (94-98 %). Default is the conservative one."},
  "growth_y1":       {"default": 0.47, "min": 0.10, "max": 0.80, "label": "AI spend growth next year", "note": "Gartner, May 2026: worldwide AI spending +47 % in 2026."},
  "growth_taper":    {"default": 0.20, "min": 0.05, "max": 0.40, "label": "growth by year 5 (tapering to this)", "note": "Assumption: growth halves as the market matures."},
}

def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read())
def post(url, body):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), headers=UA), timeout=240).read())

def fetch():
    out = {"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    debt = get("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?sort=-record_date&page%5Bsize%5D=30")["data"]
    out["debt"] = [{"date": r["record_date"], "total": float(r["tot_pub_debt_out_amt"]), "public": float(r["debt_held_public_amt"])} for r in debt]
    ai = {}
    for fy, (a, b) in FY.items():
        sot = post("https://api.usaspending.gov/api/v2/search/spending_over_time/",
                   {"group": "month", "filters": {"keywords": KW, "time_period": [{"start_date": a, "end_date": b}], "award_type_codes": ["A", "B", "C", "D"]}})
        ai[fy] = {"total": sum(float(r["aggregated_amount"]) for r in sot["results"]),
                  "monthly": [{"fy": r["time_period"]["fiscal_year"], "month": r["time_period"]["month"], "amount": float(r["aggregated_amount"])} for r in sot["results"]]}
    f = {"keywords": KW, "time_period": [{"start_date": FY["FY2026"][0], "end_date": FY["FY2026"][1]}], "award_type_codes": ["A", "B", "C", "D"]}
    geo = post("https://api.usaspending.gov/api/v2/search/spending_by_geography/", {"scope": "place_of_performance", "geo_layer": "state", "filters": f})
    ai["by_state_FY2026"] = {r["shape_code"]: float(r["aggregated_amount"]) for r in geo["results"]}
    ai["top_recipients_FY2026"] = [{"name": r.get("name") or r.get("code") or "?", "amount": float(r["amount"])} for r in post("https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/", {"filters": f, "limit": 10, "page": 1})["results"]]
    ai["top_agencies_FY2026"] = [{"name": r.get("name") or r.get("code") or "?", "amount": float(r["amount"])} for r in post("https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/", {"filters": f, "limit": 10, "page": 1})["results"]]
    out["usaspending"] = ai
    (DATA / "fetched.json").write_text(json.dumps(out, indent=1))
    hist = DATA / "history"; hist.mkdir(exist_ok=True)
    (hist / (out["fetched_utc"][:10] + ".json")).write_text(json.dumps({"debt": out["debt"][0], "ai_fy2026": out["usaspending"]["FY2026"]["total"],
        "by_state": out["usaspending"]["by_state_FY2026"]}))
    return out

def population():
    pop = {}
    with open(DATA / "NST-EST2024-ALLDATA.csv", encoding="latin-1") as fh:
        for row in csv.DictReader(fh):
            if row["SUMLEV"] == "040":
                pop[row["NAME"]] = int(row["POPESTIMATE2024"])
    return pop

def assemble(raw):
    pop_by_name = population(); name_to_code = {v: k for k, v in STATES.items()}
    pop = {name_to_code[n]: p for n, p in pop_by_name.items() if n in name_to_code}
    us_pop = sum(pop.values())
    state_debt = json.loads((DATA / "state-debt.json").read_text()) if (DATA / "state-debt.json").exists() else {}
    debt = raw["debt"]; latest = debt[0]
    # daily rate over the last ~30 calendar days of records
    if len(debt) > 1:
        d0, d1 = debt[-1], debt[0]
        days = (time.mktime(time.strptime(d1["date"], "%Y-%m-%d")) - time.mktime(time.strptime(d0["date"], "%Y-%m-%d"))) / 86400 or 1
        per_sec = (d1["total"] - d0["total"]) / (days * 86400)
    else:
        per_sec = 0
    ai = raw["usaspending"]
    fy26 = ai["FY2026"]["total"]; fy25 = ai["FY2025"]["total"]
    # annualise FY2026 (fiscal year started 2025-10-01)
    days_elapsed = max(1, (time.time() - time.mktime(time.strptime("2025-10-01", "%Y-%m-%d"))) / 86400)
    fy26_annualised = fy26 / min(days_elapsed, 365) * 365
    states = []
    for code, name in STATES.items():
        amt = ai["by_state_FY2026"].get(code, 0.0)
        states.append({"code": code, "name": name, "ai_fy2026": amt, "pop": pop.get(code), "ai_per_capita": (amt / pop[code]) if pop.get(code) else None,
                       "debt": state_debt.get(code)})
    states.sort(key=lambda s: -s["ai_fy2026"])
    # since the previous release
    hist = sorted((DATA / "history").glob("*.json")) if (DATA / "history").exists() else []
    prev = None
    for h in reversed(hist):
        if h.stem < raw["fetched_utc"][:10]:
            prev = json.loads(h.read_text()); prev["date"] = h.stem; break
    since = None
    if prev:
        since = {"date": prev["date"], "debt_delta": latest["total"] - prev["debt"]["total"], "ai_delta": fy26 - prev["ai_fy2026"],
                 "states_up": sorted(((c, ai["by_state_FY2026"].get(c, 0) - prev["by_state"].get(c, 0)) for c in STATES), key=lambda x: -x[1])[:3]}
    return {
        "since": since,
        "fetched_utc": raw["fetched_utc"],
        "debt": {"date": latest["date"], "total": latest["total"], "held_by_public": latest["public"], "per_second": per_sec},
        "federal_ai": {"fy2025": fy25, "fy2026_to_date": fy26, "fy2026_annualised": fy26_annualised, "keywords": KW,
                       "monthly": ai["FY2026"]["monthly"], "top_recipients": ai["top_recipients_FY2026"], "top_agencies": ai["top_agencies_FY2026"]},
        "world_ai_2026": 2.59e12, "world_ai_growth_2026": 0.47, "world_genai_models_2026": 32.6e9,
        "us_population": us_pop, "states": states, "params": PARAMS,
        "measurements": {"xerj_case_study_ratio": 2.7, "nextjs_codebase_ratios": [16, 38, 47]},
    }

def money(n, digits=1):
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= div: return f"${n/div:,.{digits}f}{unit}"
    return f"${n:,.0f}"

def render(data):
    SITE.mkdir(exist_ok=True); (SITE / "state").mkdir(exist_ok=True)
    tpl = (HERE / "templates" / "index.html").read_text()
    common = {"DATA_JSON": json.dumps(data), "FETCHED": data["fetched_utc"][:10], "DEBT_TOTAL": money(data["debt"]["total"], 3),
              "FED_AI_FY26": money(data["federal_ai"]["fy2026_to_date"]), "FED_AI_FY25": money(data["federal_ai"]["fy2025"])}
    # story starters, one line per state, for the press page
    ranked = data["states"]; us = sum(x["ai_fy2026"] for x in ranked) or 1
    lines = []
    for i, st in enumerate(ranked):
        if st["ai_fy2026"] <= 0: continue
        pc = f"${st['ai_fy2026']/st['pop']:.2f} per resident" if st.get("pop") else ""
        lines.append(f"<li><b>{st['name']}</b>: {money(st['ai_fy2026'])} in federal contracts naming AI performed in the state this fiscal year, ranked {i+1} of 51, {100*st['ai_fy2026']/us:.1f} % of the US total{', ' + pc if pc else ''}"
                     + (f"; state debt at end of FY2023 {money(st['debt']['debt_fy2023'])} (Census)" if st.get("debt") else "") + f". <a href=\"/state/{st['code'].lower()}/\">Release</a></li>")
    common["STORY_STARTERS"] = "\n".join(lines)
    common["SINCE"] = (f"Since the previous release ({data['since']['date']}): total public debt {'+' if data['since']['debt_delta']>=0 else ''}{money(data['since']['debt_delta'])}; "
                       f"federal contracts naming AI {'+' if data['since']['ai_delta']>=0 else ''}{money(data['since']['ai_delta'])}; largest state increases: "
                       + ", ".join(f"{c} {'+' if d>=0 else ''}{money(d)}" for c, d in data['since']['states_up'])) if data.get("since") else "First release of this series; the change line begins with the next one."
    (SITE / "index.html").write_text(fill(tpl, {**common, "PAGE_STATE": "null", "TITLE": "AI Burn Clock"}))
    stpl = (HERE / "templates" / "state.html").read_text()
    for s in data["states"]:
        d = SITE / "state" / s["code"].lower(); d.mkdir(exist_ok=True)
        (d / "index.html").write_text(fill(stpl, {**common, "PAGE_STATE": json.dumps(s), "STATE_NAME": s["name"], "STATE_CODE": s["code"], "STATE_LOWER": s["code"].lower(),
                                                  "STATE_AI": money(s["ai_fy2026"]), "TITLE": f"AI Burn Clock · {s['name']}"}))
    (SITE / "data.json").write_text(json.dumps(data))
    for f in ("widget.html", "embed.js", "methodology.html", "press.html", "robots.txt", "og.svg", "emblem.svg", "favicon.svg"):
        p = HERE / "templates" / f
        if p.exists(): (SITE / f).write_text(fill(p.read_text(), common))
    # sitemap
    urls = ["https://aiburnclock.org/", "https://aiburnclock.org/methodology.html", "https://aiburnclock.org/press.html"] + [f"https://aiburnclock.org/state/{s['code'].lower()}/" for s in data["states"]]
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>")
    print(f"site: {len(data['states'])} state pages, debt {money(data['debt']['total'],3)}, federal AI FY2026 {money(data['federal_ai']['fy2026_to_date'])}")

def fill(tpl, ctx):
    for k, v in ctx.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    return tpl

if __name__ == "__main__":
    raw = json.loads((DATA / "fetched.json").read_text()) if "--no-fetch" in sys.argv else fetch()
    render(assemble(raw))
