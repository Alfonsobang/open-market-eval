from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


def _metric(label: str, value: str, note: str) -> str:
    return (
        '<article class="metric">'
        f'<p class="metric-label">{html.escape(label)}</p>'
        f'<p class="metric-value">{html.escape(value)}</p>'
        f'<p class="metric-note">{html.escape(note)}</p>'
        "</article>"
    )


def _calibration_chart(score: dict[str, Any]) -> str:
    points = []
    for bucket in score["calibration"]:
        x = 46 + bucket["mean_probability"] * 288
        y = 208 - bucket["observed_frequency"] * 168
        label = (
            f"{bucket['bin']}: n={bucket['count']}, "
            f"p={bucket['mean_probability']:.2f}, observed={bucket['observed_frequency']:.2f}"
        )
        points.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="point">'
            f"<title>{html.escape(label)}</title></circle>"
        )
    return "".join(
        [
            '<svg class="chart" viewBox="0 0 380 240" role="img" '
            'aria-label="Calibration chart for the synthetic smoke benchmark">',
            '<line x1="46" y1="208" x2="334" y2="40" class="ideal" />',
            '<line x1="46" y1="208" x2="334" y2="208" class="axis" />',
            '<line x1="46" y1="208" x2="46" y2="40" class="axis" />',
            '<text x="190" y="232" text-anchor="middle">Predicted probability</text>',
            '<text x="14" y="124" text-anchor="middle" transform="rotate(-90 14 124)">Observed</text>',
            '<text x="46" y="224" text-anchor="middle">0</text>',
            '<text x="334" y="224" text-anchor="middle">1</text>',
            *points,
            "</svg>",
        ]
    )


def render_dashboard(score: dict[str, Any], questions: list[dict[str, Any]]) -> str:
    question_rows = []
    for question in questions:
        tags = " ".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in question["tags"])
        question_rows.append(
            '<tr class="live-question" data-close="{}">'.format(html.escape(question["close_time"]))
            + f'<td><strong>{html.escape(question["title"])}</strong><div class="tags">{tags}</div></td>'
            + f'<td><time datetime="{html.escape(question["close_time"])}">{html.escape(question["close_time"])}</time></td>'
            + '<td><span class="status">Open</span></td>'
            + "</tr>"
        )

    prediction_rows = []
    for row in score["predictions"]:
        prediction_rows.append(
            f"<tr><td><code>{html.escape(row['question_id'])}</code></td>"
            f"<td>{row['probability']:.2f}</td><td>{row['outcome']}</td>"
            f"<td>{row['brier']:.4f}</td></tr>"
        )

    metrics = "".join(
        [
            _metric("Resolved forecasts", str(score["n_scored"]), "Synthetic smoke fixture"),
            _metric("Mean Brier", f'{score["mean_brier"]:.4f}', "Lower is better"),
            _metric("Skill vs 0.5", f'{score["brier_skill_vs_0_5"]:.1%}', "Synthetic result only"),
            _metric(
                "Calibration error",
                f'{score["expected_calibration_error"]:.4f}',
                "Small sample; diagnostic only",
            ),
        ]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="OpenMarketEval: auditable evaluation for AI market-event forecasting agents.">
  <title>OpenMarketEval Dashboard</title>
  <style>
    :root {{ --ink:#172027; --muted:#5f6b73; --line:#d8dee3; --paper:#ffffff; --wash:#f4f6f7; --green:#1f9d55; --red:#e64b3c; --blue:#1769d2; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font:15px/1.55 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    a {{ color:var(--blue); }}
    .shell {{ width:min(1120px, calc(100% - 32px)); margin:0 auto; }}
    header {{ border-bottom:1px solid var(--line); background:var(--paper); }}
    nav {{ min-height:64px; display:flex; align-items:center; justify-content:space-between; gap:20px; }}
    .brand {{ color:var(--ink); font-weight:800; font-size:18px; text-decoration:none; }}
    nav div {{ display:flex; gap:18px; flex-wrap:wrap; }}
    nav div a {{ color:var(--muted); text-decoration:none; }}
    .hero {{ padding:48px 0 34px; border-bottom:1px solid var(--line); }}
    .eyebrow {{ margin:0 0 8px; color:var(--green); font-weight:750; text-transform:uppercase; font-size:12px; }}
    h1 {{ margin:0; max-width:850px; font-size:clamp(34px, 5vw, 62px); line-height:1.05; letter-spacing:0; }}
    .lede {{ max-width:760px; margin:18px 0 24px; color:var(--muted); font-size:19px; }}
    .actions {{ display:flex; gap:12px; flex-wrap:wrap; }}
    .button {{ display:inline-flex; align-items:center; min-height:42px; padding:0 15px; border:1px solid var(--ink); border-radius:6px; color:var(--paper); background:var(--ink); text-decoration:none; font-weight:700; }}
    .button.secondary {{ color:var(--ink); background:var(--paper); }}
    .preview {{ margin-top:32px; width:100%; aspect-ratio:2/1; object-fit:cover; border:1px solid var(--line); border-radius:6px; }}
    section {{ padding:40px 0; border-bottom:1px solid var(--line); }}
    .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:24px; margin-bottom:20px; }}
    h2 {{ margin:0; font-size:28px; letter-spacing:0; }}
    .section-head p, .note {{ color:var(--muted); margin:0; max-width:660px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); border:1px solid var(--line); border-radius:6px; overflow:hidden; }}
    .metric {{ min-width:0; padding:18px; border-right:1px solid var(--line); }}
    .metric:last-child {{ border-right:0; }}
    .metric p {{ margin:0; }}
    .metric-label {{ color:var(--muted); font-size:13px; }}
    .metric-value {{ margin-top:5px !important; font-size:30px; font-weight:800; }}
    .metric-note {{ margin-top:3px !important; color:var(--muted); font-size:12px; }}
    .analysis {{ margin-top:24px; display:grid; grid-template-columns:minmax(300px,.85fr) minmax(0,1.15fr); gap:28px; align-items:center; }}
    .chart {{ width:100%; max-height:310px; color:var(--muted); }}
    .chart text {{ fill:var(--muted); font-size:11px; }}
    .axis {{ stroke:var(--ink); stroke-width:1.5; }} .ideal {{ stroke:var(--green); stroke-width:2; stroke-dasharray:6 5; }} .point {{ fill:var(--blue); stroke:white; stroke-width:2; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; min-width:680px; }}
    th, td {{ padding:13px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }}
    th {{ color:var(--muted); background:var(--wash); font-size:12px; text-transform:uppercase; }}
    tr:last-child td {{ border-bottom:0; }}
    td:nth-child(n+2) {{ white-space:nowrap; }}
    .tags {{ display:flex; gap:6px; margin-top:7px; flex-wrap:wrap; }}
    .tag {{ padding:2px 6px; border:1px solid var(--line); border-radius:4px; color:var(--muted); font-size:11px; }}
    .status {{ color:var(--green); font-weight:750; }} .status.closed {{ color:var(--red); }}
    .warning {{ margin:0 0 20px; padding:13px 15px; border-left:4px solid var(--red); background:#fff4f2; }}
    footer {{ padding:32px 0 48px; color:var(--muted); }}
    code {{ font-family:ui-monospace, SFMono-Regular, Consolas, monospace; font-size:13px; }}
    @media (max-width:800px) {{ .metrics {{ grid-template-columns:repeat(2,1fr); }} .metric:nth-child(2) {{ border-right:0; }} .metric:nth-child(-n+2) {{ border-bottom:1px solid var(--line); }} .analysis {{ grid-template-columns:1fr; }} .section-head {{ align-items:start; flex-direction:column; }} }}
    @media (min-width:801px) {{ .hero {{ padding-top:34px; padding-bottom:22px; }} .preview {{ height:150px; margin-top:20px; aspect-ratio:auto; object-position:center 48%; }} }}
    @media (max-width:520px) {{ nav {{ align-items:flex-start; padding:16px 0; flex-direction:column; }} .hero {{ padding-top:32px; }} .metrics {{ grid-template-columns:1fr; }} .metric {{ border-right:0; border-bottom:1px solid var(--line); }} .metric:nth-child(2) {{ border-right:0; }} .metric:last-child {{ border-bottom:0; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="#top">OpenMarketEval</a><div><a href="#live">Live round</a><a href="#scorecard">Scorecard</a><a href="https://github.com/Alfonsobang/open-market-eval">GitHub</a></div></nav></header>
  <main id="top">
    <div class="hero"><div class="shell">
      <p class="eyebrow">Open evaluation for market-event agents</p>
      <h1>Forecast before the event. Publish every miss.</h1>
      <p class="lede">Timestamp evidence, seal probability forecasts, resolve against primary sources, and measure calibration instead of showcasing isolated wins.</p>
      <div class="actions"><a class="button" href="#live">View open questions</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval#one-minute-demo">Run locally</a></div>
      <img class="preview" src="assets/open-market-eval-social-preview.png" alt="OpenMarketEval forecast, seal, resolve, and score lifecycle">
    </div></div>
    <section id="live"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Round 2026-08</p><h2>Open macro and policy questions</h2></div><p>Six public-source questions with fixed close times. Submit forecasts before close; outcomes will be resolved from BLS, BEA, ECB, or Federal Reserve releases.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Question</th><th>Forecast closes</th><th>Status</th></tr></thead><tbody>{''.join(question_rows)}</tbody></table></div>
    </div></section>
    <section id="scorecard"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Harness smoke test</p><h2>Evaluation output</h2></div><p>These metrics verify the software path and report format. They are not live model performance.</p></div>
      <p class="warning"><strong>Synthetic fixture:</strong> do not interpret these values as investment, trading, or forecasting results.</p>
      <div class="metrics">{metrics}</div>
      <div class="analysis"><div>{_calibration_chart(score)}</div><div class="table-wrap"><table><thead><tr><th>Question</th><th>p</th><th>Outcome</th><th>Brier</th></tr></thead><tbody>{''.join(prediction_rows)}</tbody></table></div></div>
    </div></section>
  </main>
  <footer><div class="shell">OpenMarketEval evaluates research processes. Nothing here is investment advice. <a href="https://github.com/Alfonsobang/open-market-eval/blob/main/CONTRIBUTING.md">Contribute a question or adapter</a>.</div></footer>
  <script>
    for (const row of document.querySelectorAll('.live-question')) {{
      const closed = Date.now() >= Date.parse(row.dataset.close);
      const status = row.querySelector('.status');
      status.textContent = closed ? 'Closed' : 'Open';
      status.classList.toggle('closed', closed);
    }}
  </script>
</body>
</html>
"""


def build_site(
    score: dict[str, Any],
    questions: list[dict[str, Any]],
    output: str | Path,
    image_path: str | Path,
) -> None:
    destination = Path(output)
    assets = destination / "assets"
    data = destination / "data"
    assets.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(render_dashboard(score, questions), encoding="utf-8")
    shutil.copyfile(image_path, assets / "open-market-eval-social-preview.png")
    (data / "smoke-scorecard.json").write_text(
        json.dumps(score, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (data / "live-questions.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for question in questions:
            handle.write(json.dumps(question, sort_keys=True) + "\n")
