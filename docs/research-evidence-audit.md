# A-Share Research Evidence Audit

Financial-search Agents often produce plausible prose without preserving enough information to reconstruct what was knowable at the research cutoff. This quality gate audits the evidence packet before anyone interprets the answer.

## What it checks

| Gate | Failure detected | Why it matters |
| --- | --- | --- |
| As-of cutoff | Evidence published or retrieved after `as_of` | Prevents hindsight from entering a historical or live decision |
| Timestamp consistency | Retrieval predates publication | Exposes impossible or corrupted provenance |
| Deduplication | Multiple evidence IDs resolve to the same canonical URL | Prevents duplicate search results from inflating source coverage |
| Content seal | Missing or malformed SHA-256 digest | Makes later evidence mutation visible |
| Primary source | No filing, exchange, regulator, or issuer source | Separates source discovery from authoritative support |
| Claim support | Claim has no valid evidence ID | Keeps conclusions traceable to the frozen packet |

The audit is deterministic. It does not decide whether a claim is true, whether a source is relevant, or whether a security is attractive.

## Run locally

No dependency, API key, market feed, or network request is required:

```bash
python -m open_market_eval audit-research-packet \
  --packet examples/research-packets/leaky-packet.json \
  --output runs/research-packet-audit.json
```

The command writes `research-packet-audit.json` and `research-packet-audit.md`. Add `--strict` to return a nonzero exit code when findings exist.

The [browser workbench](https://alfonsobang.github.io/open-market-eval/research-audit.html) runs the same six failure classes locally in the browser. Pasted content is not uploaded.

## Packet contract

The Draft 2020-12 [`research-packet.schema.json`](../schemas/research-packet.schema.json) defines a minimal interchange format:

- packet identity, A-share market scope, research query, and timezone-aware cutoff;
- evidence title, publisher, URL, publication and retrieval timestamps, content digest, and primary-source flag;
- claims with explicit evidence IDs.

The committed [safe](../examples/research-packets/conservative-packet.json) and [leaky](../examples/research-packets/leaky-packet.json) packets are synthetic software fixtures. They use the reserved `.invalid` domain, contain no market data, and make no investment claim.

## CI gate

```bash
python -m open_market_eval audit-research-packet \
  --packet path/to/sanitized-packet.json \
  --strict
```

A passing packet is ready for a deeper relevance and truth review. It is not a truth certificate.

The v0.6 gate is in public beta. [Submit a false positive, missed risk, schema gap, or sanitized packet](research-evidence-beta.md).
