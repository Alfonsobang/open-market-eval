# A-Share Point-in-Time QA v0.1

A small, source-backed development pack for a deceptively hard financial-agent workflow: finding one number in the correct filing version, preserving its declared unit, normalizing it to yuan, and citing the correct page.

[中文说明](README.zh-CN.md)

[Open the browser lab](https://alfonsobang.github.io/open-market-eval/filing-qa.html) to try all 10 tasks without installing anything.

## What is included

- 10 public tasks across five Shenzhen-listed companies.
- Two fields per 2024 annual report: operating revenue and research and development investment.
- Five official CNINFO filing URLs with publication dates, byte counts, and SHA-256 digests.
- Public labels for raw value, declared unit, normalized yuan value, period, scope, PDF page, and source ID.
- A deterministic scorer that reports exact-task and per-field accuracy.

This is a public development pack, not a hidden leaderboard. It tests extraction and provenance contracts; it does not measure investment skill.

## Run it

Create one JSONL row per task using [`submission-template.jsonl`](submission-template.jsonl), then score it:

```bash
python -m open_market_eval score-fact-qa \
  --submission path/to/fact-answers.jsonl \
  --output runs/fact-qa-scorecard.json
```

Each row must contain:

```json
{
  "task_id": "pit-300750-revenue-2024",
  "value": "362012554",
  "unit": "CNY_THOUSAND",
  "normalized_value_yuan": "362012554000",
  "period": "2024",
  "scope": "listed_company_consolidated",
  "pdf_page": 9,
  "source_id": "cninfo-300750-2024-annual"
}
```

Numeric values are strings so large financial values are not rounded by JSON number parsers. `pdf_page` is the 1-based physical PDF page, not the page number printed inside the report.

## Quality controls

- **Version:** every task identifies one annual-report artifact and an end-of-publication-date cutoff.
- **Seal:** every source records the SHA-256 and byte length observed on 2026-08-13.
- **Units:** `CNY_THOUSAND` and `CNY_YUAN` are scored separately from the normalized value.
- **Citation:** the exact 1-based PDF page and source ID are required.
- **Rights:** filing PDFs are not committed or redistributed; the repository stores links, metadata, and factual labels.

If an official file changes, do not silently replace its digest or labels. Open a new benchmark version and document the change.

## Known limitations

- Only five companies, one report period, and two fields are covered.
- Publication cutoffs are date-level, not intraday timestamps.
- Labels are public and therefore suitable for development and regression testing, not claims about hidden-test generalization.
- A correct answer does not validate a company, security, forecast, or investment thesis.

Nothing in this pack is investment advice.
