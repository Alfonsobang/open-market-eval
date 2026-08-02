from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


RESEARCH_REFERENCES = [
    {
        "name": "ForecastBench",
        "meta": "Karger, Bastani, Tetlock et al. · 2024",
        "url": "https://arxiv.org/abs/2409.19839",
        "theme": "Live time-gating",
        "note": "Future-only questions and a continuously refreshed benchmark reduce temporal leakage.",
    },
    {
        "name": "Approaching Human-Level Forecasting",
        "meta": "Halawi, Zhang, Yueh-Han, Steinhardt · 2024",
        "url": "https://arxiv.org/abs/2402.18563",
        "theme": "Retrieval + aggregation",
        "note": "Search, evidence retrieval, probabilistic reasoning, and forecast aggregation form an end-to-end agent loop.",
    },
    {
        "name": "Pitfalls in Evaluating LM Forecasters",
        "meta": "Paleka, Goel, Geiping, Tramèr · 2025",
        "url": "https://arxiv.org/abs/2506.00723",
        "theme": "Leakage controls",
        "note": "Temporal leakage and weak real-world extrapolation can invalidate otherwise impressive results.",
    },
    {
        "name": "Consistency Checks for LM Forecasters",
        "meta": "Paleka, Sudhir, Tramèr et al. · ICLR 2025",
        "url": "https://arxiv.org/abs/2412.18544",
        "theme": "Arbitrage consistency",
        "note": "Logically related questions can expose incoherent probabilities before outcomes resolve.",
    },
    {
        "name": "ForecastBench-Sim",
        "meta": "Lee, Merrill, Karger · 2026 preprint",
        "url": "https://arxiv.org/abs/2606.18686",
        "theme": "Simulated worlds",
        "note": "Controlled rollouts make rare events, interventions, and immediate resolution testable at scale.",
    },
    {
        "name": "FinBench",
        "meta": "Ghosh, Devarakonda · 2026 preprint",
        "url": "https://arxiv.org/abs/2607.16229",
        "theme": "Financial calibration",
        "note": "Strict time gates, Brier scores, and prediction intervals target the confidence-competence gap.",
    },
    {
        "name": "Harbor",
        "meta": "harbor-framework · active open source",
        "url": "https://github.com/harbor-framework/harbor",
        "theme": "Executable verifiers",
        "note": "Containerized tasks, programmatic verification, repeated trials, and trajectory artifacts support agent evaluation.",
    },
    {
        "name": "Inspect AI",
        "meta": "UK AI Security Institute · open source",
        "url": "https://www.aisi.gov.uk/blog/open-sourcing-our-testing-framework-inspect",
        "theme": "Tool traces + sandboxing",
        "note": "Composable datasets, agents, tools, scorers, and sandboxed execution make tool-using evaluations inspectable.",
    },
]


def _metric(label: str, value: str, note: str, accent: str = "cyan") -> str:
    return (
        f'<article class="metric accent-{accent}">'
        f'<p class="metric-label">{html.escape(label)}</p>'
        f'<p class="metric-value">{html.escape(value)}</p>'
        f'<p class="metric-note">{html.escape(note)}</p>'
        "</article>"
    )


def _source_agency(question: dict[str, Any]) -> str:
    tags = set(question.get("tags", []))
    for tag, agency in (("bls", "BLS"), ("bea", "BEA"), ("ecb", "ECB"), ("federal-reserve", "Federal Reserve")):
        if tag in tags:
            return agency
    return "Official source"


def _calibration_chart(score: dict[str, Any]) -> str:
    points = []
    for bucket in score["calibration"]:
        x = 50 + bucket["mean_probability"] * 288
        y = 210 - bucket["observed_frequency"] * 168
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
            '<svg class="chart" viewBox="0 0 390 242" role="img" '
            'aria-label="Calibration chart for the synthetic smoke benchmark">',
            '<line x1="50" y1="210" x2="338" y2="42" class="ideal" />',
            '<line x1="50" y1="210" x2="338" y2="210" class="axis" />',
            '<line x1="50" y1="210" x2="50" y2="42" class="axis" />',
            '<text x="194" y="235" text-anchor="middle">Predicted probability</text>',
            '<text x="15" y="126" text-anchor="middle" transform="rotate(-90 15 126)">Observed frequency</text>',
            '<text x="50" y="225" text-anchor="middle">0</text>',
            '<text x="338" y="225" text-anchor="middle">1</text>',
            *points,
            "</svg>",
        ]
    )


def _research_cards() -> str:
    cards = []
    accents = ("cyan", "green", "coral", "amber")
    for index, reference in enumerate(RESEARCH_REFERENCES):
        cards.append(
            f'<a class="research-card accent-{accents[index % len(accents)]}" '
            f'href="{html.escape(reference["url"])}" target="_blank" rel="noreferrer">'
            f'<span class="research-theme">{html.escape(reference["theme"])}</span>'
            f'<h3>{html.escape(reference["name"])}</h3>'
            f'<p class="research-meta">{html.escape(reference["meta"])}</p>'
            f'<p>{html.escape(reference["note"])}</p>'
            '<span class="research-link">Open source ↗</span></a>'
        )
    return "".join(cards)


def render_dashboard(score: dict[str, Any], questions: list[dict[str, Any]]) -> str:
    agencies = sorted({_source_agency(question) for question in questions})
    question_rows = []
    for question in questions:
        tags = " ".join(
            f'<span class="tag">{html.escape(tag)}</span>' for tag in question["tags"][:2]
        )
        source = question["resolution_sources"][0]
        question_rows.append(
            f'<tr class="live-question" data-close="{html.escape(question["close_time"])}">'
            f'<td><span class="agency">{html.escape(_source_agency(question))}</span>'
            f'<strong>{html.escape(question["title"])}</strong><div class="tags">{tags}</div></td>'
            f'<td><time datetime="{html.escape(question["close_time"])}">{html.escape(question["close_time"])}</time>'
            '<span class="countdown">Calculating</span></td>'
            f'<td><a class="source-link" href="{html.escape(source)}" target="_blank" rel="noreferrer">Primary source ↗</a></td>'
            '<td><span class="status">Open</span></td></tr>'
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
            _metric("Resolved forecasts", str(score["n_scored"]), "Synthetic smoke fixture", "cyan"),
            _metric("Mean Brier", f'{score["mean_brier"]:.4f}', "Lower is better", "green"),
            _metric("Skill vs 0.5", f'{score["brier_skill_vs_0_5"]:.1%}', "Synthetic result only", "coral"),
            _metric("Calibration error", f'{score["expected_calibration_error"]:.4f}', "Small-sample diagnostic", "amber"),
        ]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="OpenMarketEval: live, auditable evaluation for AI market-event forecasting agents.">
  <meta name="theme-color" content="#f8fbfc">
  <title>OpenMarketEval · Live Agent Forecasting Evaluation</title>
  <style>
    :root {{ --ink:#10191f; --muted:#5c6972; --line:#d5dfe4; --paper:#ffffff; --wash:#f3f7f8; --deep:#10232d; --cyan:#00a8d6; --green:#169b62; --coral:#f0523d; --amber:#d68a00; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font:15px/1.58 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    a {{ color:inherit; }}
    .shell {{ width:min(1180px, calc(100% - 40px)); margin:0 auto; }}
    header {{ position:sticky; top:0; z-index:10; border-bottom:1px solid rgba(16,25,31,.12); background:rgba(255,255,255,.94); backdrop-filter:blur(14px); }}
    nav {{ min-height:64px; display:flex; align-items:center; justify-content:space-between; gap:22px; }}
    .brand {{ display:flex; align-items:center; gap:10px; color:var(--ink); font-weight:850; font-size:18px; text-decoration:none; }}
    .brand-mark {{ width:26px; height:26px; border:5px solid var(--cyan); border-right-color:var(--green); border-bottom-color:var(--coral); border-radius:50%; }}
    .nav-links {{ display:flex; align-items:center; gap:20px; }}
    .nav-links a {{ color:var(--muted); font-size:14px; text-decoration:none; }}
    .nav-links a:hover {{ color:var(--ink); }}
    .repo-link {{ padding:7px 10px; border:1px solid var(--line); border-radius:6px; font-weight:700; }}
    .hero {{ min-height:610px; border-bottom:1px solid var(--line); background:#f8fbfc url("assets/open-market-eval-hero.png") center/cover no-repeat; }}
    .hero .shell {{ min-height:610px; display:flex; align-items:center; }}
    .hero-copy {{ width:min(430px, 43%); padding:50px 0 84px; }}
    .eyebrow {{ margin:0 0 10px; color:var(--green); font-size:12px; font-weight:800; text-transform:uppercase; }}
    .live-dot {{ display:inline-block; width:8px; height:8px; margin-right:7px; border-radius:50%; background:var(--green); box-shadow:0 0 0 4px rgba(22,155,98,.13); }}
    h1 {{ margin:0; max-width:430px; font-size:56px; line-height:1.02; letter-spacing:0; }}
    .lede {{ margin:20px 0 24px; color:#3c4d57; font-size:18px; max-width:420px; }}
    .actions {{ display:flex; gap:10px; flex-wrap:wrap; }}
    .button {{ display:inline-flex; align-items:center; justify-content:center; min-height:44px; padding:0 16px; border:1px solid var(--ink); border-radius:6px; color:white; background:var(--ink); text-decoration:none; font-weight:750; }}
    .button.secondary {{ color:var(--ink); background:white; }}
    .hero-proof {{ margin-top:30px; display:flex; gap:18px; color:var(--muted); font-size:12px; flex-wrap:wrap; }}
    .hero-proof strong {{ display:block; color:var(--ink); font-size:18px; }}
    .signal-band {{ border-bottom:1px solid var(--line); background:var(--deep); color:white; }}
    .signals {{ display:grid; grid-template-columns:repeat(4,1fr); }}
    .signal {{ min-height:98px; padding:18px 22px; border-right:1px solid rgba(255,255,255,.14); }}
    .signal:first-child {{ border-left:1px solid rgba(255,255,255,.14); }}
    .signal span {{ display:block; color:#9bb0bb; font-size:12px; }}
    .signal strong {{ display:block; margin-top:3px; font-size:25px; }}
    .signal-cyan strong {{ color:#5bdcff; }} .signal-green strong {{ color:#57d89c; }} .signal-coral strong {{ color:#ff806f; }} .signal-amber strong {{ color:#ffc55f; }}
    section {{ padding:64px 0; border-bottom:1px solid var(--line); }}
    .wash {{ background:var(--wash); }}
    .section-head {{ display:grid; grid-template-columns:minmax(280px,.8fr) minmax(320px,1.2fr); gap:60px; align-items:end; margin-bottom:28px; }}
    h2 {{ margin:0; font-size:34px; line-height:1.15; letter-spacing:0; }}
    .section-head p, .note {{ color:var(--muted); margin:0; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:6px; background:white; }}
    table {{ width:100%; border-collapse:collapse; min-width:790px; }}
    th, td {{ padding:15px 16px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }}
    th {{ color:var(--muted); background:#f7f9fa; font-size:11px; text-transform:uppercase; }}
    tr:last-child td {{ border-bottom:0; }}
    td strong {{ display:block; max-width:560px; }}
    td:nth-child(n+2) {{ white-space:nowrap; }}
    .agency {{ display:block; margin-bottom:3px; color:var(--cyan); font-size:11px; font-weight:800; text-transform:uppercase; }}
    .tags {{ display:flex; gap:6px; margin-top:8px; flex-wrap:wrap; }}
    .tag {{ padding:2px 6px; border:1px solid var(--line); border-radius:4px; color:var(--muted); font-size:11px; }}
    time {{ display:block; font-family:ui-monospace, SFMono-Regular, Consolas, monospace; font-size:12px; }}
    .countdown {{ display:block; margin-top:5px; color:var(--muted); font-size:12px; }}
    .source-link {{ color:var(--cyan); font-size:12px; font-weight:700; text-decoration:none; }}
    .status {{ display:inline-flex; padding:3px 8px; border:1px solid rgba(22,155,98,.28); border-radius:4px; color:var(--green); background:rgba(22,155,98,.08); font-size:11px; font-weight:800; text-transform:uppercase; }}
    .status.closed {{ border-color:rgba(240,82,61,.25); color:var(--coral); background:rgba(240,82,61,.07); }}
    .protocol {{ display:grid; grid-template-columns:repeat(5,1fr); gap:0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .protocol-step {{ position:relative; padding:24px 18px; border-right:1px solid var(--line); }}
    .protocol-step:last-child {{ border-right:0; }}
    .step-no {{ color:var(--cyan); font-family:ui-monospace, SFMono-Regular, Consolas, monospace; font-size:12px; font-weight:800; }}
    .protocol-step:nth-child(2) .step-no {{ color:var(--green); }} .protocol-step:nth-child(3) .step-no {{ color:var(--amber); }} .protocol-step:nth-child(4) .step-no {{ color:var(--coral); }}
    .protocol-step h3 {{ margin:8px 0 6px; font-size:17px; }}
    .protocol-step p {{ margin:0; color:var(--muted); font-size:13px; }}
    .evaluation-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-top:30px; }}
    .eval-layer {{ padding-top:15px; border-top:4px solid var(--cyan); }}
    .eval-layer:nth-child(2) {{ border-color:var(--green); }} .eval-layer:nth-child(3) {{ border-color:var(--coral); }} .eval-layer:nth-child(4) {{ border-color:var(--amber); }}
    .eval-layer h3 {{ margin:0 0 6px; font-size:17px; }} .eval-layer p {{ margin:0; color:var(--muted); font-size:13px; }}
    .layer-state {{ display:inline-block; margin-top:10px; font-size:11px; font-weight:800; text-transform:uppercase; }}
    .state-live {{ color:var(--green); }} .state-next {{ color:var(--amber); }}
    .research-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }}
    .research-card {{ min-height:250px; padding:20px; border:1px solid var(--line); border-top:4px solid var(--cyan); border-radius:6px; background:white; text-decoration:none; transition:transform .18s ease, box-shadow .18s ease; }}
    .research-card:hover {{ transform:translateY(-3px); box-shadow:0 12px 30px rgba(16,25,31,.09); }}
    .research-card.accent-green {{ border-top-color:var(--green); }} .research-card.accent-coral {{ border-top-color:var(--coral); }} .research-card.accent-amber {{ border-top-color:var(--amber); }}
    .research-theme {{ color:var(--cyan); font-size:11px; font-weight:800; text-transform:uppercase; }}
    .accent-green .research-theme {{ color:var(--green); }} .accent-coral .research-theme {{ color:var(--coral); }} .accent-amber .research-theme {{ color:var(--amber); }}
    .research-card h3 {{ margin:14px 0 4px; font-size:18px; line-height:1.25; }}
    .research-meta {{ min-height:38px; margin:0 0 13px !important; color:var(--muted); font-size:12px; }}
    .research-card p {{ margin:0; color:#44545d; font-size:13px; }}
    .research-link {{ display:block; margin-top:16px; color:var(--ink); font-size:12px; font-weight:800; }}
    .disclosure {{ margin-top:18px; color:var(--muted); font-size:12px; }}
    .warning {{ margin:0 0 20px; padding:13px 15px; border-left:4px solid var(--coral); background:#fff5f3; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); border:1px solid var(--line); border-radius:6px; overflow:hidden; background:white; }}
    .metric {{ min-width:0; padding:18px; border-right:1px solid var(--line); border-top:4px solid var(--cyan); }}
    .metric:last-child {{ border-right:0; }} .metric.accent-green {{ border-top-color:var(--green); }} .metric.accent-coral {{ border-top-color:var(--coral); }} .metric.accent-amber {{ border-top-color:var(--amber); }}
    .metric p {{ margin:0; }} .metric-label {{ color:var(--muted); font-size:12px; }} .metric-value {{ margin-top:4px !important; font-size:30px; font-weight:850; }} .metric-note {{ margin-top:3px !important; color:var(--muted); font-size:11px; }}
    .analysis {{ margin-top:24px; display:grid; grid-template-columns:minmax(300px,.8fr) minmax(0,1.2fr); gap:26px; align-items:center; }}
    .chart {{ width:100%; max-height:310px; color:var(--muted); }} .chart text {{ fill:var(--muted); font-size:11px; }} .axis {{ stroke:var(--ink); stroke-width:1.5; }} .ideal {{ stroke:var(--green); stroke-width:2; stroke-dasharray:6 5; }} .point {{ fill:var(--cyan); stroke:white; stroke-width:2; }}
    .submit-band {{ background:var(--deep); color:white; }}
    .submit-layout {{ display:grid; grid-template-columns:.8fr 1.2fr; gap:60px; align-items:center; }}
    .submit-layout h2 {{ max-width:430px; }} .submit-layout p {{ color:#afc0c8; }}
    pre {{ margin:0; padding:20px; overflow:auto; border:1px solid rgba(255,255,255,.18); border-radius:6px; background:#08171f; color:#d9f5ff; font:12px/1.65 ui-monospace, SFMono-Regular, Consolas, monospace; }}
    code {{ font-family:ui-monospace, SFMono-Regular, Consolas, monospace; font-size:12px; }}
    footer {{ padding:34px 0 48px; color:var(--muted); }}
    .footer-layout {{ display:flex; justify-content:space-between; gap:30px; flex-wrap:wrap; }}
    @media (max-width:980px) {{ h1 {{ font-size:50px; }} .hero-copy {{ width:46%; }} .signals, .research-grid {{ grid-template-columns:repeat(2,1fr); }} .signal:nth-child(3) {{ border-left:1px solid rgba(255,255,255,.14); }} .signal:nth-child(-n+2) {{ border-bottom:1px solid rgba(255,255,255,.14); }} .protocol {{ grid-template-columns:repeat(3,1fr); }} .protocol-step:nth-child(3) {{ border-right:0; }} .protocol-step:nth-child(-n+3) {{ border-bottom:1px solid var(--line); }} .evaluation-grid {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:760px) {{ .shell {{ width:min(100% - 28px, 1180px); }} header {{ position:static; }} nav {{ min-height:58px; }} .nav-links a:not(.repo-link) {{ display:none; }} .hero {{ min-height:580px; background-size:auto 580px; background-position:left center; }} .hero .shell {{ min-height:580px; align-items:flex-start; }} .hero-copy {{ width:100%; max-width:470px; padding:38px 0 28px; }} h1 {{ font-size:43px; max-width:390px; }} .lede {{ max-width:420px; font-size:17px; }} .hero-proof {{ max-width:400px; margin-top:22px; }} section {{ padding:48px 0; }} .section-head, .submit-layout {{ grid-template-columns:1fr; gap:18px; align-items:start; }} h2 {{ font-size:29px; }} .analysis {{ grid-template-columns:1fr; }} .metrics {{ grid-template-columns:repeat(2,1fr); }} .metric:nth-child(2) {{ border-right:0; }} .metric:nth-child(-n+2) {{ border-bottom:1px solid var(--line); }} }}
    @media (max-width:520px) {{ .research-grid, .evaluation-grid {{ grid-template-columns:1fr; }} .signals {{ grid-template-columns:repeat(2,1fr); }} .signal {{ min-height:96px; padding:15px 14px; border-bottom:1px solid rgba(255,255,255,.14); }} .signal:nth-child(odd) {{ border-left:1px solid rgba(255,255,255,.14); }} .signal:nth-child(n+3) {{ border-bottom:0; }} .signal strong {{ font-size:20px; }} .protocol {{ grid-template-columns:1fr; }} .protocol-step {{ border-right:0; border-bottom:1px solid var(--line); }} .protocol-step:last-child {{ border-bottom:0; }} .metrics {{ grid-template-columns:1fr; }} .metric {{ border-right:0; border-bottom:1px solid var(--line); }} .metric:last-child {{ border-bottom:0; }} .actions {{ align-items:stretch; flex-direction:column; max-width:290px; }} .button {{ width:100%; }} }}
    @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} .research-card {{ transition:none; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"></span>OpenMarketEval</a><div class="nav-links"><a href="#live">Live round</a><a href="#method">Method</a><a href="#research">Research</a><a class="repo-link" href="https://github.com/Alfonsobang/open-market-eval">GitHub ↗</a></div></nav></header>
  <main id="top">
    <div class="hero"><div class="shell"><div class="hero-copy">
      <p class="eyebrow"><span class="live-dot"></span>Live sealed evaluation · Round 2026-08</p>
      <h1>Forecast the event. Audit the agent.</h1>
      <p class="lede">A time-gated benchmark for market-research agents: public evidence, immutable probabilities, official resolution, and calibration-aware scoring.</p>
      <div class="actions"><a class="button" href="#live">Explore live questions</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval#one-minute-demo">Run the harness ↗</a></div>
      <div class="hero-proof"><span><strong>{len(questions)}</strong>live questions</span><span><strong>L2</strong>pre-event seal</span><span><strong>SHA-256</strong>audit trail</span></div>
    </div></div></div>
    <div class="signal-band"><div class="shell signals">
      <div class="signal signal-cyan"><span>Open now</span><strong id="open-count">{len(questions)} / {len(questions)}</strong></div>
      <div class="signal signal-green"><span>Next close</span><strong id="next-close">Calculating</strong></div>
      <div class="signal signal-coral"><span>Resolution authorities</span><strong>{len(agencies)} official</strong></div>
      <div class="signal signal-amber"><span>Leaderboard policy</span><strong>No deleted misses</strong></div>
    </div></div>
    <section id="live"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Round 2026-08</p><h2>Questions that resolve in the real world</h2></div><p>Each event has a fixed cutoff, objective binary rule, and primary public source. A forecast only qualifies as L2 when its Git commit predates the close time.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Question</th><th>Forecast closes</th><th>Resolution</th><th>Status</th></tr></thead><tbody>{''.join(question_rows)}</tbody></table></div>
    </div></section>
    <section id="method" class="wash"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Evaluation architecture</p><h2>One artifact from evidence to postmortem</h2></div><p>The benchmark separates research quality from portfolio returns. It asks whether an agent assigned a useful probability using only information available at the time.</p></div>
      <div class="protocol">
        <article class="protocol-step"><span class="step-no">01</span><h3>Specify</h3><p>Freeze the event, threshold, deadline, and official resolution rule.</p></article>
        <article class="protocol-step"><span class="step-no">02</span><h3>Research</h3><p>Capture source URLs, publication timestamps, thesis, and falsifiers.</p></article>
        <article class="protocol-step"><span class="step-no">03</span><h3>Seal</h3><p>Hash question and forecast ledgers before the event closes.</p></article>
        <article class="protocol-step"><span class="step-no">04</span><h3>Resolve</h3><p>Use the predeclared primary release and preserve the rationale.</p></article>
        <article class="protocol-step"><span class="step-no">05</span><h3>Score</h3><p>Report Brier, log loss, calibration, baseline skill, and every miss.</p></article>
      </div>
      <div class="evaluation-grid">
        <article class="eval-layer"><h3>Outcome quality</h3><p>Proper scoring rules reward honest probability estimates, not confident storytelling.</p><span class="layer-state state-live">Implemented</span></article>
        <article class="eval-layer"><h3>Temporal integrity</h3><p>Evidence timestamps, close-time validation, immutable files, and public commits limit hindsight.</p><span class="layer-state state-live">Implemented</span></article>
        <article class="eval-layer"><h3>Research process</h3><p>Source diversity, retrieval freshness, tool traces, latency, and cost expose how the answer was produced.</p><span class="layer-state state-next">Next track</span></article>
        <article class="eval-layer"><h3>Robustness</h3><p>Repeated trials, logical consistency, abstention, and bootstrap intervals test reliability beyond one run.</p><span class="layer-state state-next">Next track</span></article>
      </div>
    </div></section>
    <section id="research"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Research compass</p><h2>Built in conversation with the frontier</h2></div><p>These papers and open frameworks inform the roadmap. They are cited as technical lineage, not as endorsements of OpenMarketEval.</p></div>
      <div class="research-grid">{_research_cards()}</div>
      <p class="disclosure">Recent 2026 items are preprints and should be read as emerging methods, not settled consensus. OpenMarketEval currently implements live time-gating, artifact sealing, official resolution, proper scores, and a Harbor task; other techniques above are explicit roadmap directions.</p>
    </div></section>
    <section id="scorecard" class="wash"><div class="shell">
      <div class="section-head"><div><p class="eyebrow">Harness verification</p><h2>Scoring output you can inspect</h2></div><p>The bundled fixture makes CI deterministic and demonstrates the report contract. Live model results will appear only after questions resolve.</p></div>
      <p class="warning"><strong>Synthetic fixture:</strong> these values test software behavior. They are not forecasting performance, a return backtest, or investment evidence.</p>
      <div class="metrics">{metrics}</div>
      <div class="analysis"><div>{_calibration_chart(score)}</div><div class="table-wrap"><table><thead><tr><th>Question</th><th>p</th><th>Outcome</th><th>Brier</th></tr></thead><tbody>{''.join(prediction_rows)}</tbody></table></div></div>
    </div></section>
    <section class="submit-band"><div class="shell submit-layout"><div><p class="eyebrow">Open protocol</p><h2>Bring any model, scaffold, or research agent.</h2><p>Your adapter reads one question from stdin and returns a probability as JSON. The harness skips closed questions, validates timestamps, and writes a PR-ready seal.</p></div><pre><code>python -m open_market_eval prepare-submission \\
  --questions live/rounds/2026-08/questions.jsonl \\
  --command "python path/to/your_agent.py" \\
  --forecaster your-agent-name \\
  --output-dir live/rounds/2026-08/submissions/your-handle</code></pre></div></section>
  </main>
  <footer><div class="shell footer-layout"><span>OpenMarketEval evaluates research processes. Nothing here is investment advice.</span><span><a href="https://github.com/Alfonsobang/open-market-eval/issues/1">Join the live round</a> · <a href="https://github.com/Alfonsobang/open-market-eval/blob/main/CONTRIBUTING.md">Contribute</a></span></div></footer>
  <script>
    const rows = [...document.querySelectorAll('.live-question')];
    const compact = new Intl.DateTimeFormat(undefined, {{ month:'short', day:'numeric', hour:'2-digit', minute:'2-digit', timeZoneName:'short' }});
    function duration(milliseconds) {{
      if (milliseconds <= 0) return 'Forecasting closed';
      const hours = Math.floor(milliseconds / 3600000);
      const days = Math.floor(hours / 24);
      return days ? `${{days}}d ${{hours % 24}}h remaining` : `${{hours}}h remaining`;
    }}
    function refreshDeadlines() {{
      const now = Date.now();
      const open = [];
      for (const row of rows) {{
        const close = Date.parse(row.dataset.close);
        const closed = now >= close;
        const status = row.querySelector('.status');
        status.textContent = closed ? 'Closed' : 'Open';
        status.classList.toggle('closed', closed);
        row.querySelector('.countdown').textContent = duration(close - now);
        const time = row.querySelector('time');
        time.textContent = compact.format(new Date(close));
        if (!closed) open.push(close);
      }}
      document.querySelector('#open-count').textContent = `${{open.length}} / ${{rows.length}}`;
      document.querySelector('#next-close').textContent = open.length ? duration(Math.min(...open) - now).replace(' remaining','') : 'Round closed';
    }}
    refreshDeadlines();
    setInterval(refreshDeadlines, 60000);
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
    shutil.copyfile(image_path, assets / "open-market-eval-hero.png")
    (data / "smoke-scorecard.json").write_text(
        json.dumps(score, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (data / "research-references.json").write_text(
        json.dumps(RESEARCH_REFERENCES, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (data / "live-questions.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for question in questions:
            handle.write(json.dumps(question, sort_keys=True) + "\n")
