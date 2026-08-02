# Time-safe market forecast

Read `fixtures/question.json` and write `/logs/artifacts/forecast.json`.

Return `question_id`, `probability`, `evidence_cutoff`, `thesis`, `evidence`, `falsifiers`, and `not_investment_advice`. Use only evidence whose `published_at` is no later than the question's evidence cutoff. The probability must be between 0 and 1.
