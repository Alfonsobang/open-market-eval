import json
import unittest
from pathlib import Path

from open_market_eval.preflight import audit_backtest_contract, render_preflight_markdown


ROOT = Path(__file__).resolve().parents[1]


class BacktestPreflightTests(unittest.TestCase):
    def load(self, name):
        return json.loads(
            (ROOT / "examples" / "backtests" / name).read_text(encoding="utf-8")
        )

    def test_leaky_contract_exposes_all_eight_failure_classes(self):
        report = audit_backtest_contract(self.load("leaky-a-share-contract.json"))
        self.assertFalse(report["passed"])
        self.assertEqual(report["finding_count"], 8)
        self.assertEqual(report["critical_count"], 6)
        self.assertIn("same_close_execution", {item["code"] for item in report["findings"]})
        self.assertIn("REVIEW REQUIRED", render_preflight_markdown(report))

    def test_conservative_contract_passes_static_checks(self):
        report = audit_backtest_contract(
            self.load("conservative-a-share-contract.json")
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["finding_count"], 0)
        self.assertIn("independent review", render_preflight_markdown(report))

    def test_negative_cost_is_rejected(self):
        contract = self.load("conservative-a-share-contract.json")
        contract["costs"]["slippage_bps"] = -1
        with self.assertRaisesRegex(ValueError, "non-negative"):
            audit_backtest_contract(contract)

    def test_unknown_schema_version_is_rejected(self):
        contract = self.load("conservative-a-share-contract.json")
        contract["schema_version"] = "9.9"
        with self.assertRaisesRegex(ValueError, "schema_version"):
            audit_backtest_contract(contract)


if __name__ == "__main__":
    unittest.main()
