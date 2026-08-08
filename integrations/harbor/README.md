# Harbor integration

`market-forecast/` is a small Harbor 1.3 task that evaluates schema compliance, evidence cutoff discipline, and safe framing with a deterministic verifier.

`a-share-backtest-audit/` is a Harbor 1.3 A-share research task that asks an agent to detect a T+1 violation and an impossible limit-up fill without inventing additional defects.

`a-share-research-evidence/` is a Harbor 1.3 financial-search task that asks an agent to detect post-cutoff evidence and a broken claim citation while preserving four clean controls.

All three task configurations parse cleanly with Harbor 0.20.0, include an Oracle `solve.sh`, write numeric verifier rewards, package fixtures into the container, and run without network access. Repository CI also runs all deterministic verifiers outside the container.

```bash
harbor run -p integrations/harbor/a-share-backtest-audit -a oracle --print-config
```

The command above validates configuration loading only. A complete Oracle trial additionally requires a supported container environment. These are independent integration examples for [harbor-framework/harbor](https://github.com/harbor-framework/harbor), not an endorsement by the Harbor maintainers. See Harbor's official [task structure](https://www.harborframework.com/docs/tasks) documentation.

Chinese Windows users who encounter a CP936 `UnicodeEncodeError` after `harbor dataset init` can use the [verified workaround](../../docs/harbor-windows-cp936.md) or read the [Chinese troubleshooting note](../../docs/harbor-windows-cp936.zh-CN.md).
