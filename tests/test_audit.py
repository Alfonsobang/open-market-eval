import unittest

from open_market_eval.audit import score_audit_submission
from open_market_eval.io import read_jsonl


class AuditScoringTests(unittest.TestCase):
    def setUp(self):
        root = "benchmarks/a-share-backtest-forensics"
        self.labels = read_jsonl(f"{root}/labels.jsonl")
        self.submission = read_jsonl(f"{root}/example-submission.jsonl")

    def test_reference_format_scores_without_false_positives(self):
        score = score_audit_submission(self.submission, self.labels)
        self.assertEqual(score["case_count"], 10)
        self.assertEqual(score["issue_class_count"], 8)
        self.assertEqual(score["false_positive"], 0)
        self.assertEqual(score["false_negative"], 2)
        self.assertAlmostEqual(score["precision"], 1.0)
        self.assertAlmostEqual(score["recall"], 10 / 12)
        self.assertAlmostEqual(score["exact_case_accuracy"], 0.8)

    def test_unknown_issue_code_is_rejected(self):
        self.submission[0]["findings"][0]["code"] = "magic_alpha"
        with self.assertRaisesRegex(ValueError, "unknown issue code"):
            score_audit_submission(self.submission, self.labels)

    def test_missing_case_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing cases"):
            score_audit_submission(self.submission[:-1], self.labels)


if __name__ == "__main__":
    unittest.main()
