"""Build the Major to Paycheck page: python3 build.py  ->  index.html (served by GitHub Pages)"""
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


def first_job(role, metro):
    """Pay range for the stepping-stone job(s) most new grads take before this role, or None."""
    fj = role.get("first_job")
    if not fj:
        return None
    pays = sorted({pay_for(D.ROLES[v], metro)[0] for v in fj["via"]})
    return {"label": fj["label"], "low": pays[0], "high": pays[-1]}


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
            tx = taxes(start, p)
            m = lambda v: round(v / 12)
            gross_m = m(start)
            take = gross_m - m(tx["fed"]) - m(tx["fica"]) - m(tx["state"]) - m(tx["local"])
            share = p["rent"] / (start / 12)
            out["by_place"][pid] = {
                "start": start, "start_src": src, "median": median,
                "gross_m": gross_m, "fed_m": m(tx["fed"]), "fica_m": m(tx["fica"]),
                "state_m": m(tx["state"]), "local_m": m(tx["local"]),
                "take_m": take, "rent": p["rent"], "left_m": take - p["rent"],
                "rent_share": round(share, 3), "verdict": verdict(share),
                "first_job": first_job(r, p["metro"]),
                "linkedin": "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(
                    {"keywords": r["search"], "location": p["linkedin"], "f_E": "1,2"}),
                "usajobs": "https://www.usajobs.gov/search/results/?" + urllib.parse.urlencode(
                    {"k": r["search"], "l": p["usajobs"], "hp": "student"}),
            }
        roles[rid] = out

    payload = {"asOf": D.DATA_AS_OF, "ratio": D.P25_RATIO, "places": places, "roles": roles,
               "programs": D.PROGRAMS, "sources": D.SOURCES,
               "gs7": D.GS_2026_DCB["GS-7"],
               "anyEstimate": any(b["start_src"] == "est" for r in roles.values() for b in r["by_place"].values())}
    html = (HERE / "template.html").read_text()
    html = html.replace("/*__DATA__*/null", json.dumps(payload, separators=(",", ":")))
    out = HERE / "index.html"
    out.write_text(html)
    return out, payload


if __name__ == "__main__":
    out, payload = build()
    print(out, len(out.read_text()) // 1024, "KB")
