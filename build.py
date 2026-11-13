"""Build the Major to Paycheck page: python3 build.py  ->  major-to-paycheck.html"""
import json
import urllib.parse
from pathlib import Path

import data as D

HERE = Path(__file__).parent


def bracket_tax(income, brackets):
    tax, lower = 0.0, 0.0
    for upper, rate in brackets:
        top = income if upper is None else min(income, upper)
        if top > lower:
            tax += (top - lower) * rate
        if upper is None or income <= upper:
            break
        lower = upper
    return tax


def lookup(table, income):
    for upper, value in table:
        if upper is None or income <= upper:
            return value
    return 0


def taxes(gross, place):
    t = D.TAX
    fed = bracket_tax(max(0, gross - t["fed"]["std"]), t["fed"]["brackets"])
    fica = gross * t["fica"]
    code = place["tax"]
    st = t[code]
    taxable = gross - st["std"] - (lookup(st["exemption"], gross) if "exemption" in st else 0)
    taxable = max(0, taxable)
    state = bracket_tax(taxable, st["brackets"])
    local = taxable * place["local_rate"]
    return {"fed": fed, "fica": fica, "state": state, "local": local}


def verdict(rent_share):
    if rent_share <= 0.30:
        return "comfortable"
    if rent_share <= 0.40:
        return "tight"
    return "hard"


BLS_FILE = HERE / "bls_wages.json"
BLS = json.loads(BLS_FILE.read_text()) if BLS_FILE.exists() else {}


def pay_for(role, metro):
    w = D.WAGES[role["soc"]]
    official = BLS.get(role["soc"], {}).get(metro, {})
    median = official.get("median") or w[metro]
    if role.get("start_override"):
        return D.GS_2026_DCB[role["start_override"]], "gs", median
    exact = official.get("p25") or (w.get("p25") or {}).get(metro)
    if exact:
        return exact, "bls", median
    return round(median * D.P25_RATIO / 500) * 500, "est", median


def full_page(fragment):
    head, body = fragment.split("</style>", 1)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</style>\n</head>\n<body>" + body + "\n</body>\n</html>\n")


def build():
    places = {}
    for pid, p in D.PLACES.items():
        places[pid] = {k: p[k] for k in ("name", "long", "rent", "tax", "local_name")}
        places[pid]["state_name"] = {"MD": "Maryland tax", "DC": "DC tax", "VA": "Virginia tax"}[p["tax"]]

    roles = {}
    for rid, r in D.ROLES.items():
        out = {k: r.get(k) for k in ("title", "does", "screens", "close", "note")}
        out["soc"] = r["soc"]
        out["bls_title"] = D.WAGES[r["soc"]]["title"]
        out["by_place"] = {}
        for pid, p in D.PLACES.items():
            start, src, median = pay_for(r, p["metro"])
            role_start, first = start, None
            if r.get("first_job"):
                fsoc, flabel = r["first_job"]
                fpay = BLS[fsoc][p["metro"]]["p25"]
                first = {"label": flabel, "soc": fsoc, "pay": fpay}
                start, src = fpay, "first"
            emp = BLS.get(r["soc"], {}).get(p["metro"], {}).get("emp")
            tx = taxes(start, p)
            m = lambda v: round(v / 12)
            gross_m = m(start)
            take = gross_m - m(tx["fed"]) - m(tx["fica"]) - m(tx["state"]) - m(tx["local"])
            share = p["rent"] / (start / 12)
            out["by_place"][pid] = {
                "start": start, "start_src": src, "median": median, "role_start": role_start,
                "first": first, "emp": emp,
                "metro_name": {"BAL": "Baltimore area", "DCM": "DC metro area"}[p["metro"]],
                "gross_m": gross_m, "fed_m": m(tx["fed"]), "fica_m": m(tx["fica"]),
                "state_m": m(tx["state"]), "local_m": m(tx["local"]),
                "take_m": take, "rent": p["rent"], "left_m": take - p["rent"],
                "rent_share": round(share, 3), "verdict": verdict(share),
                "linkedin": "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(
                    {"keywords": r["search"], "location": p["linkedin"], "f_E": "1,2"}),
                "usajobs": "https://www.usajobs.gov/search/results/?" + urllib.parse.urlencode(
                    {"k": r["search"], "l": p["usajobs"], "hp": "student"}),
            }
        roles[rid] = out

    payload = {"asOf": D.DATA_AS_OF, "ratio": D.P25_RATIO, "places": places, "roles": roles,
               "programs": D.PROGRAMS, "sources": D.SOURCES,
               "gs7": D.GS_2026_DCB["GS-7"], "signup": D.SIGNUP,
               "anyEstimate": any(b["start_src"] == "est" for r in roles.values() for b in r["by_place"].values())}
    template = (HERE / "template.html").read_text()
    fragment = template.replace("/*__DATA__*/null", json.dumps({**payload, "hubUrl": ""}, separators=(",", ":")))
    out = HERE / "major-to-paycheck.html"
    out.write_text(fragment)
    # GitHub Pages site: Career Route landing page at index.html, Major to Paycheck at paycheck.html
    site = HERE / "site"
    site.mkdir(exist_ok=True)
    paged = template.replace("/*__DATA__*/null", json.dumps({**payload, "hubUrl": "index.html"}, separators=(",", ":")))
    (site / "paycheck.html").write_text(full_page(paged))
    (site / "index.html").write_text(full_page((HERE / "hub_template.html").read_text()))

    # 90-day route (gap plan) page
    plan_data = {
        "programs": [{"id": p["id"], "name": p["name"], "roles": p["roles"]} for p in D.PROGRAMS],
        "places": {pid: {"name": p["name"]} for pid, p in D.PLACES.items()},
        "roles": {rid: {"title": r["title"], "screens": r["screens"], "close": r["close"], "search": D.ROLES[rid]["search"],
                        "by_place": {pid: {k: b[k] for k in ("start", "take_m", "rent", "left_m", "first", "linkedin", "usajobs")}
                                     for pid, b in r["by_place"].items()}}
                  for rid, r in roles.items()},
        "signup": D.SIGNUP, "siteBase": "",
        "mangleUrl": "https://andrewmangle.com/score.html?utm_source=career-route&utm_medium=plan&utm_campaign=bsu-cob",
    }
    plan_t = (HERE / "plan_template.html").read_text()
    (site / "plan.html").write_text(full_page(plan_t.replace("/*__DATA__*/null", json.dumps({**plan_data, "hubUrl": "index.html"}, separators=(",", ":")))))

    # Shared map of programs, jobs, places and federal series, used by the openings feed and the email script
    route = {
        "programs": [{"id": p["id"], "name": p["name"], "roles": p["roles"]} for p in D.PROGRAMS],
        "roles": {rid: {"title": r["title"], "search": r["search"], "series": D.ROLE_SERIES.get(rid, [])}
                  for rid, r in D.ROLES.items()},
        "places": {pid: {"name": p["name"], "states": D.PLACE_STATES[pid], "linkedin": p["linkedin"],
                         "usajobs": p["usajobs"]} for pid, p in D.PLACES.items()},
    }
    (site / "careerroute.json").write_text(json.dumps(route, indent=1))
    gs = HERE / "apps_script_template.gs"
    if gs.exists():
        (HERE / "apps-script").mkdir(exist_ok=True)
        (HERE / "apps-script" / "Code.gs").write_text(
            gs.read_text().replace("/*__ROUTE__*/null", json.dumps(route, separators=(",", ":"))))
    return out, payload


if __name__ == "__main__":
    out, payload = build()
    print(out, len(out.read_text()) // 1024, "KB")
