# Major to Paycheck

Prototype for Bowie State College of Business students: pick a program and a place (Baltimore, DC,
Northern Virginia) and see entry roles, early-career pay, take-home after 2026 taxes, rent, and hiring gaps.

Live at https://andrewmangle.github.io/major-to-paycheck/ (GitHub Pages, `main` branch, root folder).

- `index.html`: the finished, self-contained page that GitHub Pages serves. Generated, so don't edit it by hand.
- `data.py`: programs, roles, hiring advice, rents, tax rules, sign-up form settings, sources. Edit content here.
- `build.py` + `template.html`: `python3 build.py` rebuilds `index.html` (and `major-to-paycheck.html` for the
  Claude artifact host).
- `load_bls.py`: reads the BLS OEWS metro file (MSA_M2025_dl.xlsx from oesm25ma.zip) into `bls_wages.json`.
  Needs `pip install -r requirements.txt`.
- `form/setup_signup_form.gs`: Apps Script that sets up the Google Form behind "Get openings for this job".
- `tests/`: `python3 -m unittest discover -s tests` checks the build, tax math and form pre-fill values.
- `CLAUDE.md`: briefing and open tasks for Claude Code.

To publish a change (from WSL): `python3 build.py`, run the tests, then `git commit -am "..." && git push`.

Wages: BLS OEWS May 2025 (25th percentile = early-career pay, median). Economist uses 2026 GS-7 DC-Baltimore.
Rent: HUD FY2027 one-bedroom Fair Market Rent. Taxes: 2026 federal, MD + Baltimore City, DC, VA, single filer.
