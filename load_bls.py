"""Pull exact BLS wages for our occupations from the OEWS metro file into bls_wages.json.
Usage: python3 load_bls.py path/to/oesm25ma/MSA_M2025_dl.xlsx  (needs: pip install -r requirements.txt)"""
import json, sys
from pathlib import Path
import pandas as pd
import data as D

AREAS = {"12580": "BAL", "47900": "DCM"}
df = pd.read_excel(sys.argv[1], dtype=str)
df.columns = [c.upper() for c in df.columns]
df = df[df["AREA"].isin(AREAS) & df["OCC_CODE"].isin(D.WAGES)]
out = {}
for _, r in df.iterrows():
    def num(v):
        v = str(v).replace(",", "").strip()
        return int(float(v)) if v.replace(".", "").isdigit() else None
    out.setdefault(r["OCC_CODE"], {})[AREAS[r["AREA"]]] = {
        "p25": num(r["A_PCT25"]), "median": num(r["A_MEDIAN"]), "emp": num(r["TOT_EMP"]), "title": r["OCC_TITLE"]}
json.dump(out, open(Path(__file__).parent / "bls_wages.json", "w"), indent=1)
missing = [(s, m) for s in D.WAGES for m in AREAS.values() if not out.get(s, {}).get(m, {}).get("p25")]
print(f"{len(out)} occupations loaded; missing p25: {missing or 'none'}")
for s, v in sorted(out.items()):
    b, d = v.get("BAL", {}), v.get("DCM", {})
    print(f"{s} {D.WAGES[s]['title'][:34]:34} BAL p25 {b.get('p25')} med {b.get('median')} (was {D.WAGES[s]['BAL']}) | DCM p25 {d.get('p25')} med {d.get('median')} (was {D.WAGES[s]['DCM']})")
