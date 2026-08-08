# Backtest Preflight Beta

Backtest Preflight checks eight declared A-share research assumptions before anyone interprets returns. The current beta asks independent researchers to find false positives, missed risks, unclear repair text, and assumptions the contract cannot yet express.

The checker runs locally in the browser. **Do not share strategy code, market data, positions, returns, private research, credentials, real user data, or proprietary workflows.**

## Participate

1. Open the [browser checker](https://alfonsobang.github.io/open-market-eval/#preflight).
2. Select assumptions matching a setup you can discuss safely.
3. Run the eight checks and review the result.
4. Submit the structured [Preflight feedback form](https://github.com/Alfonsobang/open-market-eval/issues/new?template=preflight-feedback.yml).

Optionally reproduce the result in CI:

```bash
python -m open_market_eval audit-spec \
  --spec path/to/backtest-contract.json \
  --output runs/preflight.json \
  --strict
```

## Exit criteria

- Five independently designed, sanitized contracts have been reviewed.
- Every confirmed false positive or missed risk has a minimal reproducible fixture.
- Confirmed defects become regression tests before the next contract version.
- Ambiguous assumptions are documented instead of silently treated as a pass.
- No report contains private data or investment-performance claims.

Development-pack and preflight outputs are research-quality diagnostics, not investment advice or evidence of market-beating performance.
