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


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out, cls.payload = build.build()
        cls.html = cls.out.read_text()

    def test_page_is_complete_html(self):
        self.assertTrue(self.html.startswith("<!doctype html>"))
        self.assertIn("</html>", self.html)
        self.assertNotIn("/*__DATA__*/null", self.html)

    def test_no_em_dashes(self):
        self.assertNotIn(chr(0x2014), self.html)  # em dash

    def test_every_program_role_exists_with_pay(self):
        for prog in D.PROGRAMS:
            for rid in prog["roles"]:
                self.assertIn(rid, self.payload["roles"], rid)
                for place in D.PLACES:
                    self.assertGreater(self.payload["roles"][rid]["by_place"][place]["start"], 0)

    def test_all_pay_comes_from_bls_or_gs(self):
        self.assertFalse(self.payload["anyEstimate"])

    def test_first_job_numbers(self):
        roles = self.payload["roles"]
        expected = {
            # role: {place: (first-job low, first-job high, this job)}
            "security-analyst": {"baltimore": (50230, 50230, 104500), "dc": (61470, 61470, 122590)},
            "data-analyst": {"baltimore": (58240, 58240, 102800), "dc": (65730, 65730, 105700)},
            "database-admin": {"baltimore": (50230, 58240, 100790), "dc": (61470, 65730, 92350)},
        }
        for rid, places in expected.items():
            for place, (low, high, start) in places.items():
                b = roles[rid]["by_place"][place]
                self.assertEqual((b["first_job"]["low"], b["first_job"]["high"], b["start"]), (low, high, start))
        with_first_job = {rid for rid, r in roles.items() if r["by_place"]["baltimore"]["first_job"]}
        self.assertEqual(with_first_job, set(expected))

    def test_first_job_via_points_at_real_roles(self):
        for rid, r in D.ROLES.items():
            for via in (r.get("first_job") or {}).get("via", []):
                self.assertIn(via, D.ROLES, f"{rid} first_job via {via}")

    def test_payload_matches_bls_file(self):
        bls = json.loads((ROOT / "bls_wages.json").read_text())
        metro = {"baltimore": "BAL", "dc": "DCM", "nova": "DCM"}
        for rid, r in self.payload["roles"].items():
            if D.ROLES[rid].get("start_override"):
                continue
            for place, b in r["by_place"].items():
                self.assertEqual(b["start"], bls[r["soc"]][metro[place]]["p25"], (rid, place))


class TaxTest(unittest.TestCase):
    def test_federal_2026_single(self):
        # $60,000 wage: taxable 43,900 -> 10% of 12,400 + 12% of 31,500
        tx = build.taxes(60000, D.PLACES["dc"])
        self.assertAlmostEqual(tx["fed"], 1240 + 3780, places=2)
        self.assertAlmostEqual(tx["fica"], 4590, places=2)

    def test_dc_has_no_local_tax(self):
        self.assertEqual(build.taxes(60000, D.PLACES["dc"])["local"], 0)

    def test_baltimore_local_tax(self):
        tx = build.taxes(60000, D.PLACES["baltimore"])
        taxable = 60000 - 3350 - 3200
        self.assertAlmostEqual(tx["local"], taxable * 0.032, places=2)

    def test_take_home_math_adds_up(self):
        _, payload = build.build()
        for r in payload["roles"].values():
            for b in r["by_place"].values():
                self.assertEqual(b["take_m"], b["gross_m"] - b["fed_m"] - b["fica_m"] - b["state_m"] - b["local_m"])
                self.assertEqual(b["left_m"], b["take_m"] - b["rent"])


class TemplateTest(unittest.TestCase):
    def test_first_job_line_wording(self):
        tpl = (ROOT / "template.html").read_text()
        self.assertIn("Most new grads start in support or analyst jobs", tpl)
        self.assertTrue(re.search(r"Where most people start:.*this job after experience", tpl, re.S))


if __name__ == "__main__":
    unittest.main()
