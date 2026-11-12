"""Checks for the Major to Paycheck build. Run: python3 -m unittest discover -s tests"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import data as D  # noqa: E402

BLS = json.loads((ROOT / "bls_wages.json").read_text())
METRO = {"baltimore": "BAL", "dc": "DCM", "nova": "DCM"}


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.payload = build.build()
        cls.html = (ROOT / "index.html").read_text()

    def test_pages_copy_is_complete_html(self):
        self.assertTrue(self.html.startswith("<!doctype html>"))
        self.assertIn("</html>", self.html)
        self.assertNotIn("/*__DATA__*/null", self.html)

    def test_no_em_dashes(self):
        for f in ("index.html", "template.html", "data.py", "build.py", "README.md", "CLAUDE.md",
                  "form/setup_signup_form.gs"):
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


class TaxTest(unittest.TestCase):
    def test_federal_2026_single(self):
        tx = build.taxes(60000, D.PLACES["dc"])  # taxable 43,900: 10% of 12,400 + 12% of 31,500
        self.assertAlmostEqual(tx["fed"], 1240 + 3780, places=2)
        self.assertAlmostEqual(tx["fica"], 4590, places=2)

    def test_baltimore_local_tax(self):
        tx = build.taxes(60000, D.PLACES["baltimore"])
        self.assertAlmostEqual(tx["local"], (60000 - 3350 - 3200) * 0.032, places=2)


class SignupFormTest(unittest.TestCase):
    """Pre-fill only works when the site sends values that exactly match the form's choices."""

    @classmethod
    def setUpClass(cls):
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

    def test_form_link_is_a_google_form(self):
        self.assertRegex(D.SIGNUP["form"], r"^https://docs\.google\.com/forms/d/(e/)?[\w-]+/viewform$")

    def test_entries_are_blank_or_entry_numbers(self):
        for key in ("program", "job", "place"):
            self.assertRegex(D.SIGNUP["entries"][key], r"^(entry\.\d+)?$", key)


if __name__ == "__main__":
    unittest.main()
