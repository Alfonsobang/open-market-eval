import copy
import json
import unittest
from pathlib import Path

from open_market_eval.fact_qa import (
    score_fact_qa_submission,
    validate_fact_qa_pack,
)
from open_market_eval.io import read_jsonl


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "benchmarks" / "a-share-point-in-time-qa"


class FactQATests(unittest.TestCase):
    def setUp(self):
        self.tasks = read_jsonl(PACK / "tasks.jsonl")
        self.labels = read_jsonl(PACK / "labels.jsonl")
        self.manifest = json.loads((PACK / "sources.json").read_text(encoding="utf-8"))

    def test_pack_has_ten_tasks_and_five_primary_sources(self):
        summary = validate_fact_qa_pack(self.tasks, self.labels, self.manifest)
        self.assertEqual(
            summary,
            {"task_count": 10, "source_count": 5, "field_count": 2},
        )

    def test_reference_labels_score_exactly(self):
        score = score_fact_qa_submission(copy.deepcopy(self.labels), self.labels)
        self.assertEqual(score["exact_task_accuracy"], 1.0)
        self.assertEqual(score["mean_field_accuracy"], 1.0)
        self.assertEqual(score["source_count"], 5)

    def test_unit_error_is_isolated_from_numeric_value(self):
        submission = copy.deepcopy(self.labels)
        submission[0]["unit"] = "CNY_YUAN"
        score = score_fact_qa_submission(submission, self.labels)
        self.assertEqual(score["exact_task_accuracy"], 0.9)
        self.assertEqual(score["field_accuracy"]["unit"], 0.9)
        self.assertEqual(score["field_accuracy"]["value"], 1.0)

    def test_comma_formatted_numeric_string_is_accepted(self):
        submission = copy.deepcopy(self.labels)
        submission[0]["value"] = "407,149,600.00"
        score = score_fact_qa_submission(submission, self.labels)
        self.assertTrue(score["cases"][0]["field_matches"]["value"])

    def test_missing_task_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing tasks"):
            score_fact_qa_submission(self.labels[:-1], self.labels)

    def test_inconsistent_label_unit_conversion_is_rejected(self):
        labels = copy.deepcopy(self.labels)
        labels[0]["normalized_value_yuan"] = "407149600"
        with self.assertRaisesRegex(ValueError, "inconsistent normalized value"):
            score_fact_qa_submission(labels, labels)

    def test_malformed_rights_contract_is_rejected_cleanly(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["rights"] = "unknown"
        with self.assertRaisesRegex(ValueError, "link-only PDF handling"):
            validate_fact_qa_pack(self.tasks, self.labels, manifest)

    def test_task_security_code_must_match_its_source(self):
        tasks = copy.deepcopy(self.tasks)
        tasks[0]["security_code"] = "000001"
        with self.assertRaisesRegex(ValueError, "security code"):
            validate_fact_qa_pack(tasks, self.labels, self.manifest)

    def test_task_cutoff_must_match_the_publication_date(self):
        tasks = copy.deepcopy(self.tasks)
        tasks[0]["as_of"] = "2025-03-30T23:59:59+08:00"
        with self.assertRaisesRegex(ValueError, "publication date"):
            validate_fact_qa_pack(tasks, self.labels, self.manifest)


if __name__ == "__main__":
    unittest.main()
