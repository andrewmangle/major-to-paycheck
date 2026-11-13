"""Checks for the Career Route build. Run: python3 -m unittest discover -s tests"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT  # GitHub Pages serves the repo root
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import data as D  # noqa: E402

BLS = json.loads((ROOT / "bls_wages.json").read_text())
METRO = {"baltimore": "BAL", "dc": "DCM", "nova": "DCM"}


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.payload = build.build()

    def test_site_pages_are_complete_html(self):
        for name in ("index.html", "paycheck.html", "plan.html"):
            html = (SITE / name).read_text()
            self.assertTrue(html.startswith("<!doctype html>"), name)
            self.assertIn("</html>", html, name)
            self.assertNotIn("/*__DATA__*/null", html, name)

    def test_old_links_keep_working(self):
        # old #program-place links on the landing page go to the paycheck page
        self.assertIn('location.replace("paycheck.html" + location.hash)', (ROOT / "index.html").read_text())
        # old site/ addresses redirect to the root, keeping the query and hash
        for name, target in (("index.html", "../"), ("paycheck.html", "../paycheck.html"), ("plan.html", "../plan.html")):
            html = (ROOT / "site" / name).read_text()
            self.assertIn('location.replace("%s" + location.search + location.hash)' % target, html, name)

    def test_hub_links_to_both_tools(self):
        hub = (SITE / "index.html").read_text()
        self.assertIn('href="paycheck.html"', hub)
        self.assertIn('href="plan.html"', hub)

    def test_paycheck_links_back_to_hub(self):
        self.assertIn('"hubUrl":"index.html"', (SITE / "paycheck.html").read_text())

    def test_no_em_dashes(self):
        files = ["index.html", "template.html", "hub_template.html", "plan_template.html", "data.py", "build.py",
                 "README.md", "CLAUDE.md", "SETUP-EMAILS.md", "apps_script_template.gs", "form/setup_signup_form.gs",
                 "paycheck.html", "plan.html", "site/index.html", "site/paycheck.html", "site/plan.html"]
        for f in files:
            self.assertNotIn(chr(0x2014), (ROOT / f).read_text(), f)

    def test_every_program_role_has_pay(self):
        for prog in D.PROGRAMS:
            for rid in prog["roles"]:
                for place in D.PLACES:
                    self.assertGreater(self.payload["roles"][rid]["by_place"][place]["start"], 0, (rid, place))

    def test_no_estimates(self):
        self.assertFalse(self.payload["anyEstimate"])

    def test_first_job_budgets_on_stepping_stone_pay(self):
        expected = {  # role: {place: (first-job pay used for the budget, pay once in the role)}
            "security-analyst": {"baltimore": (50230, 104500), "dc": (61470, 122590)},
            "data-analyst": {"baltimore": (58240, 102800), "dc": (65730, 105700)},
            "database-admin": {"baltimore": (50230, 100790), "dc": (61470, 92350)},
        }
        for rid, places in expected.items():
            for place, (first, role) in places.items():
                b = self.payload["roles"][rid]["by_place"][place]
                self.assertEqual((b["start"], b["first"]["pay"], b["role_start"]), (first, first, role), (rid, place))

    def test_other_roles_use_bls_25th_percentile(self):
        for rid, r in self.payload["roles"].items():
            if D.ROLES[rid].get("start_override") or D.ROLES[rid].get("first_job"):
                continue
            for place, b in r["by_place"].items():
                self.assertEqual(b["start"], BLS[r["soc"]][METRO[place]]["p25"], (rid, place))

    def test_take_home_math_adds_up(self):
        for r in self.payload["roles"].values():
            for b in r["by_place"].values():
                self.assertEqual(b["take_m"], b["gross_m"] - b["fed_m"] - b["fica_m"] - b["state_m"] - b["local_m"])
                self.assertEqual(b["left_m"], b["take_m"] - b["rent"])


class SharedDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build()
        cls.route = json.loads((SITE / "careerroute.json").read_text())

    def test_route_covers_every_program_role_and_place(self):
        for prog in self.route["programs"]:
            for rid in prog["roles"]:
                self.assertIn(rid, self.route["roles"])
        self.assertEqual(set(self.route["places"]), set(D.PLACES))
        for p in self.route["places"].values():
            self.assertTrue(p["states"])

    def test_email_script_finds_the_sheet_from_any_project(self):
        # getActive() is empty when the script is pasted into the form's project, not the Sheet's
        gs = (ROOT / "apps-script" / "Code.gs").read_text()
        self.assertIn("getDestinationId()", gs)
        self.assertNotIn("const ss = SpreadsheetApp.getActive();", gs)

    def test_email_script_is_generated_with_site_urls(self):
        gs = (ROOT / "apps-script" / "Code.gs").read_text()
        self.assertNotIn("/*__ROUTE__*/null", gs)
        site = re.search(r"SITE_URL: '([^']*)'", gs).group(1)
        feed = re.search(r"FEED_URL: '([^']*)'", gs).group(1)
        self.assertTrue(site.startswith("https://") and site.endswith("/major-to-paycheck/"), site)
        self.assertEqual(feed, site + "openings.json")


class TaxTest(unittest.TestCase):
    def test_federal_2026_single(self):
        tx = build.taxes(60000, D.PLACES["dc"])  # taxable 43,900: 10% of 12,400 + 12% of 31,500
        self.assertAlmostEqual(tx["fed"], 1240 + 3780, places=2)
        self.assertAlmostEqual(tx["fica"], 4590, places=2)

    def test_baltimore_local_tax(self):
        tx = build.taxes(60000, D.PLACES["baltimore"])
        self.assertAlmostEqual(tx["local"], (60000 - 3350 - 3200) * 0.032, places=2)


class SignupFormTest(unittest.TestCase):
    """Pre-fill only works when the site sends values that exactly match the live form's choices."""

    @classmethod
    def setUpClass(cls):
        build.build()
        gs = (ROOT / "form" / "setup_signup_form.gs").read_text()
        cls.form_programs = re.findall(r"'([^']+)'", re.search(r"const PROGRAMS = \[(.*?)\];", gs, re.S).group(1))
        cls.form_places = re.findall(r"'([^']+)'", re.search(r"const PLACES = \[(.*?)\];", gs, re.S).group(1))

    def test_site_programs_match_form_dropdown(self):
        for prog in D.PROGRAMS:
            self.assertIn(prog["name"], self.form_programs)

    def test_site_places_match_form_checkboxes(self):
        self.assertEqual(set(D.SIGNUP["place_choices"]), set(D.PLACES))
        for label in D.SIGNUP["place_choices"].values():
            self.assertIn(label, self.form_places)

    def test_form_link_is_the_published_form(self):
        self.assertRegex(D.SIGNUP["form"], r"^https://docs\.google\.com/forms/d/e/[\w-]+/viewform$")

    def test_pre_fill_entries_are_wired(self):
        for key in ("program", "job", "place"):
            self.assertRegex(D.SIGNUP["entries"][key], r"^entry\.\d+$", key)
        self.assertRegex(D.SIGNUP["entries"].get("source", ""), r"^(entry\.\d+)?$")

    def test_email_script_titles_match_the_form(self):
        form_gs = (ROOT / "form" / "setup_signup_form.gs").read_text()
        form_titles = set(re.findall(r"find_\(form, '([^']+)'", form_gs))
        email_gs = (ROOT / "apps_script_template.gs").read_text()
        q = dict(re.findall(r"^\s+(\w+): '([^']+)'", re.search(r"const Q = \{(.*?)\};", email_gs, re.S).group(1), re.M))
        needed = re.findall(r"'(\w+)'", re.search(r"const NEEDED = \[(.*?)\];", email_gs, re.S).group(1))
        for key in needed:
            self.assertIn(q[key], form_titles, key)

    def test_email_script_places_use_form_labels(self):
        route = json.loads((SITE / "careerroute.json").read_text())
        self.assertEqual({pid: p["form"] for pid, p in route["places"].items()}, D.SIGNUP["place_choices"])

    def test_plan_page_pre_fills_the_form(self):
        tpl = (ROOT / "plan_template.html").read_text()
        self.assertIn("const signup = signupUrl(job);", tpl)
        self.assertIn("place_choices", tpl)

    def test_every_page_uses_the_same_form(self):
        hub = (SITE / "index.html").read_text()
        forms = set(re.findall(r"https://docs\.google\.com/forms/[^\"'?\s]+", hub))
        self.assertEqual(forms, {D.SIGNUP["form"]})
        for name in ("paycheck.html", "plan.html"):
            self.assertIn(json.dumps(D.SIGNUP["form"]), (SITE / name).read_text(), name)


if __name__ == "__main__":
    unittest.main()
