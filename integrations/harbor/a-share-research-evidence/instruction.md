# A-share financial-search evidence audit

Read `fixtures/research_packet.json` and write `/logs/artifacts/evidence_audit.json`.

The report must contain `packet_id` and a `findings` array. Each finding must contain one allowed `code`, a severity of `critical`, `high`, `medium`, or `low`, and a concrete evidence sentence grounded in the fixture.

Allowed codes:

- `cutoff_violation`
- `timestamp_inconsistency`
- `duplicate_evidence`
- `unsealed_evidence`
- `primary_source_missing`
- `unsupported_claim`

Report only defects supported by the packet. False positives are failures. Do not assess investment merit or add facts that are not present in the fixture.
