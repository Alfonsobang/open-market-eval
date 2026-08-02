import copy
import unittest

from open_market_eval.validation import validate_forecast, validate_question


QUESTION = {
    "id": "q1",
    "title": "Test?",
    "close_time": "2025-01-02T00:00:00Z",
    "resolve_by": "2025-01-03T00:00:00Z",
    "resolution_criteria": "Objective rule.",
    "resolution_sources": ["fixture://source"],
    "tags": ["test"],
}
FORECAST = {
    "question_id": "q1",
    "forecaster": "test",
    "probability": 0.6,
    "created_at": "2025-01-01T12:00:00Z",
    "evidence_cutoff": "2025-01-01T12:00:00Z",
    "thesis": "Test thesis.",
    "evidence": [
        {"url": "fixture://evidence", "published_at": "2025-01-01T10:00:00Z"}
    ],
    "falsifiers": ["Contrary evidence"],
}


class ValidationTests(unittest.TestCase):
    def test_valid_bundle(self):
        validate_question(QUESTION)
        validate_forecast(FORECAST, QUESTION)

    def test_rejects_hindsight(self):
        forecast = copy.deepcopy(FORECAST)
        forecast["created_at"] = "2025-01-02T01:00:00Z"
        with self.assertRaisesRegex(ValueError, "after close_time"):
            validate_forecast(forecast, QUESTION)

    def test_rejects_future_evidence(self):
        forecast = copy.deepcopy(FORECAST)
        forecast["evidence"][0]["published_at"] = "2025-01-01T13:00:00Z"
        with self.assertRaisesRegex(ValueError, "after evidence_cutoff"):
            validate_forecast(forecast, QUESTION)


if __name__ == "__main__":
    unittest.main()
