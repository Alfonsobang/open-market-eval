from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


METHOD_REFERENCES = [
    {
        "name": "ForecastBench",
        "url": "https://arxiv.org/abs/2409.19839",
        "use": "未来问题、动态题库与时间泄漏控制",
    },
    {
        "name": "Pitfalls in Evaluating LM Forecasters",
        "url": "https://arxiv.org/abs/2506.00723",
        "use": "识别时间泄漏和不可外推的评测结论",
    },
    {
        "name": "FinBench (2026 preprint)",
        "url": "https://arxiv.org/abs/2607.16229",
        "use": "金融预测的时间门控、校准和区间评分",
    },
    {
        "name": "Harbor",
        "url": "https://github.com/harbor-framework/harbor",
        "use": "容器化任务、Agent 轨迹和程序化 verifier",
    },
    {
        "name": "Microsoft Qlib",
        "url": "https://github.com/microsoft/qlib",
        "use": "AI 量化研究的数据、模型与工作流基础设施",
    },
    {
        "name": "AKShare",
        "url": "https://github.com/akfamily/akshare",
        "use": "公开财经数据接入和原型交叉验证",
    },
]


STATUS_LABELS = {
    "live": ("运行中", "green"),
    "pilot": ("首批试验", "cyan"),
    "spec": ("规格已发布", "amber"),
    "planned": ("规划中", "gray"),
}


def _status_badge(status: str) -> str:
    label, color = STATUS_LABELS.get(status, (status, "gray"))
    return f'<span class="badge badge-{color}">{html.escape(label)}</span>'


def _track_rows(tracks: list[dict[str, Any]]) -> str:
    rows = []
    for index, track in enumerate(tracks, 1):
        metrics = " / ".join(track["metrics"][:2])
        rows.append(
            f'<tr><td><span class="track-index">0{index}</span></td>'
            f'<td><button class="track-link" data-select-track="{html.escape(track["id"])}">'
            f'<strong>{html.escape(track["name_zh"])}</strong><span>{html.escape(track["name_en"])}</span></button></td>'
            f'<td>{_status_badge(track["status"])}</td>'
            f'<td>{html.escape(metrics)}</td>'
            f'<td><code>{html.escape(track["deliverable"].split("：", 1)[0])}</code></td></tr>'
        )
    return "".join(rows)


def _source_rows(sources: list[dict[str, Any]]) -> str:
    authority = {"primary": "一手来源", "secondary": "二手接口", "tool": "研究工具"}
    rows = []
    for source in sources:
        rows.append(
            f'<tr><td><a href="{html.escape(source["url"])}" target="_blank" rel="noreferrer"><strong>{html.escape(source["name"])}</strong> ↗</a>'
            f'<span class="source-kind">{html.escape(source["kind"])}</span></td>'
            f'<td><span class="authority authority-{html.escape(source["authority"])}">{authority[source["authority"]]}</span></td>'
            f'<td>{html.escape(source["use_for"])}</td>'
            f'<td>{html.escape(source["caution"])}</td></tr>'
        )
    return "".join(rows)


def _method_rows() -> str:
    return "".join(
        f'<tr><td><a href="{html.escape(item["url"])}" target="_blank" rel="noreferrer"><strong>{html.escape(item["name"])}</strong> ↗</a></td><td>{html.escape(item["use"])}</td></tr>'
        for item in METHOD_REFERENCES
    )


def _initial_track(track: dict[str, Any]) -> str:
    return f"""
      <div class="track-detail-head"><div><p class="kicker" id="detail-en">{html.escape(track['name_en'])}</p><h3 id="detail-name">{html.escape(track['name_zh'])}</h3></div><div id="detail-status">{_status_badge(track['status'])}</div></div>
      <p class="detail-question" id="detail-question">{html.escape(track['question'])}</p>
      <div class="detail-grid">
        <div><span class="field-label">帮助用户解决</span><p id="detail-value">{html.escape(track['user_value'])}</p></div>
        <div><span class="field-label">输入</span><p id="detail-input">{html.escape(track['input'])}</p></div>
        <div><span class="field-label">标准交付物</span><p id="detail-deliverable">{html.escape(track['deliverable'])}</p></div>
        <div><span class="field-label">样例任务</span><p id="detail-sample">{html.escape(track['sample_task'])}</p></div>
      </div>
      <div class="detail-bottom"><div><span class="field-label">评分指标</span><div class="chips" id="detail-metrics">{''.join(f'<span>{html.escape(metric)}</span>' for metric in track['metrics'])}</div></div><div><span class="field-label">重点拦截</span><ul id="detail-failures">{''.join(f'<li>{html.escape(item)}</li>' for item in track['failure_modes'])}</ul></div></div>
      <pre><code id="detail-command">python -m open_market_eval show-track --track {html.escape(track['id'])}</code></pre>
    """


def render_dashboard(
    score: dict[str, Any],
    questions: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> str:
    del score
    primary_count = sum(source["authority"] == "primary" for source in sources)
    tracks_json = json.dumps(tracks, ensure_ascii=False).replace("</", "<\\/")
    status_json = json.dumps(STATUS_LABELS, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A股研究 Agent 公共实验场：公告搜索、时点查数、事件预测、回测审计和研究备忘录。">
  <meta name="theme-color" content="#f5f7f8">
  <title>OpenMarketEval · A股研究 Agent 实验场</title>
  <style>
    :root {{ --ink:#172027; --muted:#61707a; --line:#d7dfe3; --paper:#fff; --wash:#f4f7f8; --deep:#12232c; --red:#d94335; --green:#11875d; --cyan:#008fb3; --amber:#b87300; --gray:#75818a; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:14px/1.55 Inter, "PingFang SC", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif; }}
    button, input {{ font:inherit; }}
    a {{ color:inherit; }}
    .shell {{ width:min(1280px, calc(100% - 36px)); margin:0 auto; }}
    header {{ position:sticky; top:0; z-index:20; border-bottom:1px solid var(--line); background:rgba(255,255,255,.96); backdrop-filter:blur(12px); }}
    nav {{ min-height:58px; display:flex; align-items:center; justify-content:space-between; gap:20px; }}
    .brand {{ display:flex; align-items:center; gap:10px; text-decoration:none; font-weight:850; font-size:17px; }}
    .brand-mark {{ width:23px; height:23px; border:5px solid var(--red); border-right-color:var(--green); border-bottom-color:var(--cyan); border-radius:50%; }}
    .brand-sub {{ color:var(--muted); font-weight:600; font-size:12px; }}
    .nav-links {{ display:flex; align-items:center; gap:20px; }}
    .nav-links a {{ color:var(--muted); text-decoration:none; font-size:13px; }}
    .nav-links .github {{ padding:6px 10px; border:1px solid var(--line); border-radius:5px; color:var(--ink); font-weight:750; }}
    .workspace {{ display:grid; grid-template-columns:210px minmax(0,1fr); gap:22px; padding:22px 0 48px; }}
    aside {{ position:sticky; top:80px; align-self:start; }}
    .side-title {{ margin:0 0 10px; color:var(--muted); font-size:11px; font-weight:800; text-transform:uppercase; }}
    .side-nav {{ display:flex; flex-direction:column; border-top:1px solid var(--line); }}
    .side-nav a {{ padding:11px 4px; border-bottom:1px solid var(--line); color:var(--muted); text-decoration:none; }}
    .side-nav a:hover {{ color:var(--ink); }}
    .side-status {{ margin-top:24px; padding:14px 0; border-top:3px solid var(--red); border-bottom:1px solid var(--line); }}
    .side-status strong {{ display:block; margin-bottom:5px; }} .side-status p {{ margin:0; color:var(--muted); font-size:12px; }}
    main {{ min-width:0; }}
    .intro {{ min-height:286px; display:grid; grid-template-columns:minmax(380px,.85fr) minmax(420px,1.15fr); border:1px solid var(--line); background:var(--paper); overflow:hidden; }}
    .intro-copy {{ padding:30px 32px; }}
    .kicker {{ margin:0 0 7px; color:var(--red); font-size:11px; font-weight:850; text-transform:uppercase; }}
    h1 {{ margin:0; font-size:38px; line-height:1.12; letter-spacing:0; }}
    .intro-copy > p:not(.kicker) {{ margin:15px 0 20px; max-width:560px; color:var(--muted); font-size:16px; }}
    .actions {{ display:flex; gap:9px; flex-wrap:wrap; }}
    .button {{ display:inline-flex; min-height:39px; align-items:center; justify-content:center; padding:0 13px; border:1px solid var(--ink); border-radius:5px; color:white; background:var(--ink); text-decoration:none; font-weight:750; }}
    .button.secondary {{ color:var(--ink); background:white; }}
    .intro-visual {{ min-height:286px; background:#fafcfc url("assets/a-share-agent-lab.png") center/cover no-repeat; border-left:1px solid var(--line); }}
    .audience {{ display:grid; grid-template-columns:1fr 1fr; border:1px solid var(--line); border-top:0; background:var(--deep); color:white; }}
    .persona {{ display:grid; grid-template-columns:36px 1fr; gap:12px; padding:17px 22px; }} .persona + .persona {{ border-left:1px solid rgba(255,255,255,.15); }}
    .persona-no {{ color:#ff796c; font:800 18px/1 ui-monospace, monospace; }} .persona:nth-child(2) .persona-no {{ color:#51d3a0; }}
    .persona strong {{ display:block; }} .persona p {{ margin:3px 0 0; color:#abc0ca; font-size:12px; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,1fr); margin-top:16px; border:1px solid var(--line); background:var(--paper); }}
    .summary-item {{ padding:15px 18px; border-right:1px solid var(--line); }} .summary-item:last-child {{ border-right:0; }}
    .summary-item span {{ display:block; color:var(--muted); font-size:11px; }} .summary-item strong {{ display:block; margin-top:2px; font-size:22px; }}
    .summary-item:nth-child(1) strong {{ color:var(--red); }} .summary-item:nth-child(2) strong {{ color:var(--cyan); }} .summary-item:nth-child(3) strong {{ color:var(--green); }} .summary-item:nth-child(4) strong {{ color:var(--amber); }}
    section {{ margin-top:22px; border:1px solid var(--line); background:var(--paper); }}
    .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:24px; padding:20px 22px; border-bottom:1px solid var(--line); }}
    h2 {{ margin:0; font-size:23px; letter-spacing:0; }} .section-head p {{ margin:0; max-width:610px; color:var(--muted); }}
    .table-wrap {{ overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; min-width:820px; }}
    th, td {{ padding:12px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }} tr:last-child td {{ border-bottom:0; }}
    th {{ color:var(--muted); background:#f7f9fa; font-size:11px; font-weight:750; text-transform:uppercase; }}
    .track-index {{ color:#9aa5ab; font:700 12px ui-monospace, monospace; }}
    .track-link {{ padding:0; border:0; background:transparent; color:var(--ink); cursor:pointer; text-align:left; }} .track-link strong, .track-link span {{ display:block; }} .track-link span {{ color:var(--muted); font-size:11px; }} .track-link:hover strong {{ color:var(--red); }}
    .badge {{ display:inline-flex; padding:3px 7px; border:1px solid currentColor; border-radius:4px; font-size:10px; font-weight:800; white-space:nowrap; }}
    .badge-green {{ color:var(--green); background:#eff9f5; }} .badge-cyan {{ color:var(--cyan); background:#eef9fb; }} .badge-amber {{ color:var(--amber); background:#fff8e9; }} .badge-gray {{ color:var(--gray); background:#f3f5f6; }}
    code, pre {{ font-family:ui-monospace, SFMono-Regular, Consolas, monospace; }} code {{ font-size:12px; }}
    .track-tabs {{ display:flex; overflow:auto; border-bottom:1px solid var(--line); background:#fafbfb; }}
    .track-tab {{ min-width:max-content; padding:11px 16px; border:0; border-right:1px solid var(--line); background:transparent; color:var(--muted); cursor:pointer; }} .track-tab.active {{ color:var(--red); background:white; box-shadow:inset 0 -3px var(--red); font-weight:800; }}
    .track-detail {{ padding:22px; }}
    .track-detail-head {{ display:flex; justify-content:space-between; align-items:start; gap:20px; }} .track-detail h3 {{ margin:0; font-size:27px; }}
    .detail-question {{ margin:12px 0 20px; font-size:16px; font-weight:650; max-width:900px; }}
    .detail-grid {{ display:grid; grid-template-columns:repeat(2,1fr); border-top:1px solid var(--line); border-left:1px solid var(--line); }}
    .detail-grid > div {{ min-height:112px; padding:14px 16px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .field-label {{ display:block; margin-bottom:5px; color:var(--muted); font-size:10px; font-weight:800; text-transform:uppercase; }} .detail-grid p {{ margin:0; }}
    .detail-bottom {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-top:20px; }} .detail-bottom ul {{ margin:5px 0 0; padding-left:18px; columns:2; }}
    .chips {{ display:flex; gap:6px; flex-wrap:wrap; }} .chips span {{ padding:4px 7px; border:1px solid var(--line); border-radius:4px; background:var(--wash); font-size:11px; }}
    pre {{ margin:20px 0 0; padding:13px 15px; overflow:auto; border:1px solid #223943; background:var(--deep); color:#d9eef4; }}
    .audit-layout {{ display:grid; grid-template-columns:minmax(0,1.3fr) minmax(260px,.7fr); }}
    .checklist {{ padding:8px 22px 20px; }}
    .check-row {{ display:grid; grid-template-columns:24px 1fr; gap:10px; padding:12px 0; border-bottom:1px solid var(--line); cursor:pointer; }} .check-row:last-child {{ border-bottom:0; }}
    .check-row input {{ width:17px; height:17px; margin-top:2px; accent-color:var(--green); }} .check-row strong {{ display:block; }} .check-row span {{ display:block; color:var(--muted); font-size:12px; }}
    .audit-score {{ display:flex; flex-direction:column; justify-content:center; padding:26px; border-left:1px solid var(--line); background:#f7f9fa; }}
    .score-value {{ font-size:42px; font-weight:850; }} .score-value span {{ color:var(--muted); font-size:16px; }} .score-label {{ color:var(--muted); }}
    .progress {{ height:8px; margin:13px 0; background:#dce3e6; }} .progress span {{ display:block; width:0; height:100%; background:var(--red); transition:width .2s ease, background .2s ease; }}
    .score-message {{ margin:0; font-weight:650; }}
    .source-kind {{ display:block; color:var(--muted); font-size:10px; }} .authority {{ font-size:11px; font-weight:800; white-space:nowrap; }} .authority-primary {{ color:var(--green); }} .authority-secondary {{ color:var(--amber); }} .authority-tool {{ color:var(--cyan); }}
    .method-grid {{ display:grid; grid-template-columns:1fr 1fr; }} .method-grid > div:first-child {{ border-right:1px solid var(--line); }}
    .method-grid h3 {{ margin:0; padding:16px 18px; border-bottom:1px solid var(--line); font-size:16px; }} .method-grid table {{ min-width:0; }}
    .build-status {{ display:grid; grid-template-columns:repeat(4,1fr); }} .build-item {{ padding:17px; border-right:1px solid var(--line); }} .build-item:last-child {{ border-right:0; }} .build-item strong {{ display:block; }} .build-item span {{ color:var(--muted); font-size:11px; }}
    .participate {{ display:grid; grid-template-columns:.9fr 1.1fr; background:var(--deep); color:white; }} .participate-copy {{ padding:26px; }} .participate h2 {{ font-size:26px; }} .participate p {{ color:#afc2cb; }} .participate-actions {{ display:flex; align-items:center; gap:10px; padding:26px; border-left:1px solid rgba(255,255,255,.15); flex-wrap:wrap; }} .participate .button {{ border-color:white; }} .participate .button.secondary {{ color:white; background:transparent; }}
    .disclaimer {{ padding:14px 18px; border-top:1px solid var(--line); color:var(--muted); font-size:11px; }}
    footer {{ padding:24px 0 40px; color:var(--muted); }} .footer-line {{ display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap; }}
    @media (max-width:1000px) {{ .workspace {{ grid-template-columns:1fr; }} aside {{ display:none; }} .intro {{ grid-template-columns:1fr 1fr; }} .summary, .build-status {{ grid-template-columns:repeat(2,1fr); }} .summary-item:nth-child(2), .build-item:nth-child(2) {{ border-right:0; }} .summary-item:nth-child(-n+2), .build-item:nth-child(-n+2) {{ border-bottom:1px solid var(--line); }} }}
    @media (max-width:760px) {{ .shell {{ width:min(100% - 22px,1280px); }} .nav-links a:not(.github) {{ display:none; }} .brand-sub {{ display:none; }} .workspace {{ padding-top:11px; }} .intro {{ grid-template-columns:1fr; }} .intro-copy {{ padding:23px 20px; }} h1 {{ font-size:31px; }} .intro-visual {{ min-height:190px; border-left:0; border-top:1px solid var(--line); background-position:center; }} .audience {{ grid-template-columns:1fr; }} .persona + .persona {{ border-left:0; border-top:1px solid rgba(255,255,255,.15); }} .section-head {{ align-items:start; flex-direction:column; }} .detail-grid, .detail-bottom, .audit-layout, .method-grid, .participate {{ grid-template-columns:1fr; }} .detail-bottom ul {{ columns:1; }} .audit-score, .participate-actions {{ border-left:0; border-top:1px solid var(--line); }} .method-grid > div:first-child {{ border-right:0; border-bottom:1px solid var(--line); }} .track-detail {{ padding:18px 14px; }} .track-detail h3 {{ font-size:23px; }} }}
    @media (max-width:480px) {{ .summary, .build-status {{ grid-template-columns:1fr; }} .summary-item, .build-item {{ border-right:0; border-bottom:1px solid var(--line); }} .summary-item:last-child, .build-item:last-child {{ border-bottom:0; }} .actions, .participate-actions {{ align-items:stretch; flex-direction:column; }} .button {{ width:100%; }} }}
    @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} .progress span {{ transition:none; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"></span>OpenMarketEval <span class="brand-sub">A股研究 Agent 实验场</span></a><div class="nav-links"><a href="#tracks">实验任务</a><a href="#audit">防泄漏自检</a><a href="#sources">数据源</a><a href="#join">参与</a><a class="github" href="https://github.com/Alfonsobang/open-market-eval">GitHub ↗</a></div></nav></header>
  <div class="shell workspace" id="top">
    <aside><p class="side-title">实验导航</p><nav class="side-nav"><a href="#tracks">01 · 五类任务</a><a href="#workbench">02 · 任务工作台</a><a href="#audit">03 · 回测防泄漏</a><a href="#sources">04 · 来源注册表</a><a href="#methods">05 · 技术路线</a><a href="#join">06 · 加入试验</a></nav><div class="side-status"><strong>当前阶段：v0.3 规格期</strong><p>A股任务目录已发布。首个公开数据包和 Agent 对比尚未发布，不展示虚构成绩。</p></div></aside>
    <main>
      <div class="intro"><div class="intro-copy"><p class="kicker">Public A-share agent experiment</p><h1>A股研究 Agent 公共实验场</h1><p>不提供荐股。我们把公告搜索、财务查数、事件预测、回测审计和研究写作拆成可复现、可评分、可复盘的公开任务。</p><div class="actions"><a class="button" href="#workbench">打开任务工作台</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval/tree/main/benchmarks/a-share-lab">查看机器可读规格 ↗</a></div></div><div class="intro-visual" role="img" aria-label="A股研究 Agent 的五轨实验流程示意图"></div></div>
      <div class="audience"><div class="persona"><span class="persona-no">01</span><div><strong>研究基础不完整的 A 股研究者</strong><p>需要一套不会把搜索摘要、错误口径和漂亮回测当成事实的工作规范。</p></div></div><div class="persona"><span class="persona-no">02</span><div><strong>对 AI 投资有兴趣的实践者</strong><p>需要知道 Agent 到底会查、会算、会预测，还是只会生成听起来合理的答案。</p></div></div></div>
      <div class="summary"><div class="summary-item"><span>研究任务轨道</span><strong>{len(tracks)}</strong></div><div class="summary-item"><span>已注册公共来源</span><strong>{len(sources)}</strong></div><div class="summary-item"><span>一手官方来源</span><strong>{primary_count}</strong></div><div class="summary-item"><span>A股公开成绩</span><strong>0</strong><span>等待首批真实试验</span></div></div>

      <section id="tracks"><div class="section-head"><div><p class="kicker">Experiment catalog</p><h2>五类真正可验证的研究任务</h2></div><p>先验证 Agent 完成研究工作的能力，再讨论它能否形成投资判断。每条轨道都有标准输入、交付物、评分指标和失败模式。</p></div><div class="table-wrap"><table><thead><tr><th>#</th><th>任务</th><th>状态</th><th>核心指标</th><th>交付物</th></tr></thead><tbody>{_track_rows(tracks)}</tbody></table></div></section>

      <section id="workbench"><div class="section-head"><div><p class="kicker">Interactive specification</p><h2>任务工作台</h2></div><p>选择一条轨道，直接查看它解决什么问题、需要什么输入、如何评分以及最容易出现什么错误。</p></div><div class="track-tabs">{''.join(f'<button class="track-tab{" active" if index == 0 else ""}" data-track="{html.escape(track["id"])}">{html.escape(track["name_zh"])}</button>' for index, track in enumerate(tracks))}</div><div class="track-detail">{_initial_track(tracks[0])}</div></section>

      <section id="audit"><div class="section-head"><div><p class="kicker">Self-check</p><h2>你的 A 股回测经得起审计吗？</h2></div><p>逐项确认。这个自检不证明策略有效，但任何未通过项都足以让高收益曲线失去可信度。</p></div><div class="audit-layout"><div class="checklist">
        <label class="check-row"><input type="checkbox"><span><strong>声明统一的信息截止时间</strong><span>行情、公告、财务字段和股票池都不能晚于信号时点。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>使用历史时点股票池</strong><span>新上市、退市、ST 和指数调样不能用今天的名单向过去投射。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>信号与成交价格严格分离</strong><span>收盘后生成的信号不能在同一收盘价成交。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>成交使用可交易原始价格</strong><span>前复权序列适合计算收益，不应直接充当跨除权日成交价格。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>建模 T+1、停牌和涨跌停</strong><span>无法买入或卖出的订单不能假设成交。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>计入双边成本与滑点压力</strong><span>至少报告多档成本下结果，而不是只展示零成本曲线。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>财务数据按首次可见版本对齐</strong><span>更正公告和供应商更新不能提前进入历史样本。</span></span></label>
        <label class="check-row"><input type="checkbox"><span><strong>保留全部实验与失败结果</strong><span>调参、失败窗口和不利市场阶段都进入实验账本。</span></span></label>
      </div><div class="audit-score"><span class="field-label">基础可信度检查</span><div class="score-value" id="audit-value">0 <span>/ 8</span></div><div class="progress"><span id="audit-progress"></span></div><p class="score-message" id="audit-message">先完成时点、股票池和成交约束，再看收益率。</p><p class="score-label">该工具只检查研究设计，不评价任何策略或证券。</p></div></div></section>

      <section id="sources"><div class="section-head"><div><p class="kicker">Source registry</p><h2>先找原始来源，再调用便利接口</h2></div><p>来源层级是评测的一部分。官方披露用于事实和结算；开源接口用于接入与交叉验证，不能自动升级为一手证据。</p></div><div class="table-wrap"><table><thead><tr><th>来源</th><th>层级</th><th>适用任务</th><th>使用警告</th></tr></thead><tbody>{_source_rows(sources)}</tbody></table></div></section>

      <section id="methods"><div class="section-head"><div><p class="kicker">Method stack</p><h2>技术路线与建设状态</h2></div><p>借鉴前沿工作，但不把引用当背书。2026 年预印本只代表值得验证的方向，不代表已经形成行业共识。</p></div><div class="method-grid"><div><h3>方法与开源基础</h3><table><tbody>{_method_rows()}</tbody></table></div><div><h3>当前诚实状态</h3><div class="build-status"><div class="build-item"><strong>已完成</strong><span>五轨规格、来源注册表、封存与评分核心</span></div><div class="build-item"><strong>运行中</strong><span>{len(questions)} 个宏观 L2 问题验证基础设施</span></div><div class="build-item"><strong>下一交付</strong><span>10 个公告搜索与时点查数公开任务</span></div><div class="build-item"><strong>尚未声称</strong><span>A股模型排名、超额收益或真实投资能力</span></div></div></div></div><div class="disclaimer">OpenMarketEval 不包含私有公司数据、真实用户数据或专有工作流。所有任务仅用于研究与评测，不构成投资建议。</div></section>

      <section id="join" class="participate"><div class="participate-copy"><p class="kicker">Build in public</p><h2>首批试验需要真实问题，不需要漂亮口号。</h2><p>最有价值的贡献是：一个能明确结算的 A 股研究任务、一个会暴露常见错误的 verifier，或一个可复现的 Agent adapter。</p></div><div class="participate-actions"><a class="button" href="https://github.com/Alfonsobang/open-market-eval/issues">认领首批任务 ↗</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval/blob/main/CONTRIBUTING.md">贡献规范 ↗</a></div></section>
    </main>
  </div>
  <footer><div class="shell footer-line"><span>OpenMarketEval · A股研究 Agent 公共实验场</span><span>公开数据 · 时点安全 · 可复现 · 不构成投资建议</span></div></footer>
  <script>
    const tracks = {tracks_json};
    const statusLabels = {status_json};
    const byId = Object.fromEntries(tracks.map(track => [track.id, track]));
    const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
    function selectTrack(id) {{
      const track = byId[id];
      if (!track) return;
      document.querySelectorAll('.track-tab').forEach(button => button.classList.toggle('active', button.dataset.track === id));
      document.querySelector('#detail-en').textContent = track.name_en;
      document.querySelector('#detail-name').textContent = track.name_zh;
      const [label, color] = statusLabels[track.status] || [track.status, 'gray'];
      document.querySelector('#detail-status').innerHTML = `<span class="badge badge-${{color}}">${{escapeHtml(label)}}</span>`;
      for (const [field, value] of Object.entries({{question:track.question, value:track.user_value, input:track.input, deliverable:track.deliverable, sample:track.sample_task}})) document.querySelector(`#detail-${{field}}`).textContent = value;
      document.querySelector('#detail-metrics').innerHTML = track.metrics.map(item => `<span>${{escapeHtml(item)}}</span>`).join('');
      document.querySelector('#detail-failures').innerHTML = track.failure_modes.map(item => `<li>${{escapeHtml(item)}}</li>`).join('');
      document.querySelector('#detail-command').textContent = `python -m open_market_eval show-track --track ${{track.id}}`;
    }}
    document.querySelectorAll('[data-track]').forEach(button => button.addEventListener('click', () => selectTrack(button.dataset.track)));
    document.querySelectorAll('[data-select-track]').forEach(button => button.addEventListener('click', () => {{ selectTrack(button.dataset.selectTrack); document.querySelector('#workbench').scrollIntoView(); }}));
    const checks = [...document.querySelectorAll('.check-row input')];
    function updateAudit() {{
      const count = checks.filter(input => input.checked).length;
      document.querySelector('#audit-value').innerHTML = `${{count}} <span>/ 8</span>`;
      const progress = document.querySelector('#audit-progress');
      progress.style.width = `${{count / 8 * 100}}%`;
      progress.style.background = count === 8 ? 'var(--green)' : count >= 5 ? 'var(--amber)' : 'var(--red)';
      document.querySelector('#audit-message').textContent = count === 8 ? '基础约束已覆盖，下一步检查数据质量和样本外稳定性。' : count >= 5 ? '仍有关键缺口，暂时不要解释收益曲线。' : '先完成时点、股票池和成交约束，再看收益率。';
    }}
    checks.forEach(input => input.addEventListener('change', updateAudit));
  </script>
</body>
</html>
"""


def build_site(
    score: dict[str, Any],
    questions: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    output: str | Path,
    image_path: str | Path,
) -> None:
    destination = Path(output)
    assets = destination / "assets"
    data = destination / "data"
    assets.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(
        render_dashboard(score, questions, tracks, sources), encoding="utf-8"
    )
    shutil.copyfile(image_path, assets / "a-share-agent-lab.png")
    for name, value in (
        ("smoke-scorecard.json", score),
        ("a-share-tracks.json", tracks),
        ("source-registry.json", sources),
        ("method-references.json", METHOD_REFERENCES),
    ):
        (data / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    with (data / "live-questions.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for question in questions:
            handle.write(json.dumps(question, sort_keys=True) + "\n")
