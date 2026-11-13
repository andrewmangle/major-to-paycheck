# Career Route

Free tools for Bowie State College of Business students, in three steps: Major to Paycheck (where can my
major take me, and can I live on it), the Mangle Metric (where do I stand), and Fed Intern Drop (what's open
now), plus a 90-day route that ties them together.

Live at https://andrewmangle.github.io/major-to-paycheck/ (GitHub Pages serves the repo root).

- `index.html`: Career Route landing page. Built from `hub_template.html`.
- `paycheck.html`: Major to Paycheck. Built from `template.html` and `data.py`.
- `plan.html`: the 90-day route. Built from `plan_template.html`.
- `careerroute.json`: programs, jobs, places and federal series, shared with the openings feed and emails.
- `site/`: hand-written redirects so old `site/...` links still reach the pages in the root.
- `data.py`: programs, roles, hiring advice, rents, tax rules, sign-up form settings, sources. Edit content here.
- `build.py`: `python3 build.py` rebuilds `index.html`, `paycheck.html`, `plan.html`, `careerroute.json` and `apps-script/Code.gs`.
- `load_bls.py`: reads the BLS OEWS metro file (MSA_M2025_dl.xlsx from oesm25ma.zip) into `bls_wages.json`.
- `apps_script_template.gs` -> `apps-script/Code.gs`: sign-up emails. See `SETUP-EMAILS.md`.
- `form/setup_signup_form.gs`: the script that set up the live sign-up form.
- `tests/`: `python3 -m unittest discover -s tests`.
- `CLAUDE.md`: briefing and open tasks for Claude Code.

To publish a change (from WSL): `python3 build.py`, run the tests, then `git commit -am "..." && git push`.

Wages: BLS OEWS May 2025 (25th percentile = early-career pay, median). Economist uses 2026 GS-7 DC-Baltimore.
Rent: HUD FY2027 one-bedroom Fair Market Rent. Taxes: 2026 federal, MD + Baltimore City, DC, VA, single filer.
