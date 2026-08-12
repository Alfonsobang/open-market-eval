# A-share point-in-time fact QA

Read `fixtures/filing_page.json` and answer the question using only the frozen factual table in that file.

Write `/logs/artifacts/fact_answer.json` with exactly these fields:

- `task_id`
- `value` as a decimal string in the filing's declared unit
- `unit` using the unit identifier supplied by the fixture
- `normalized_value_yuan` as a decimal string
- `period`
- `scope`
- `pdf_page` as a 1-based physical PDF page
- `source_id`

Preserve the disclosed value before converting units. Do not infer facts that are absent from the fixture, assess investment merit, or recommend a security.
