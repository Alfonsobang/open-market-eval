from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


METHOD_REFERENCES = [
    {
        "name": "Harbor",
        "url": "https://github.com/harbor-framework/harbor",
        "use": "容器化任务、Agent 轨迹、重复试验与程序化 verifier",
    },
    {
        "name": "Microsoft Qlib",
        "url": "https://github.com/microsoft/qlib",
        "use": "AI 量化研究、point-in-time 数据与回测基础设施",
    },
    {
        "name": "OpenBB",
        "url": "https://github.com/OpenBB-finance/OpenBB",
        "use": "面向分析师、量化研究者和 AI Agent 的开放数据平台",
    },
    {
        "name": "ForecastBench",
        "url": "https://arxiv.org/abs/2409.19839",
        "use": "动态题库、未来问题和时间泄漏控制",
    },
    {
        "name": "Pitfalls in Evaluating LM Forecasters",
        "url": "https://arxiv.org/abs/2506.00723",
        "use": "识别时间泄漏和不可外推的评测结论",
    },
]


ISSUE_NAMES = {
    "same_close_execution": "同收盘价穿越",
    "current_universe_projection": "当前股票池回放历史",
    "adjusted_price_execution": "复权价虚拟成交",
    "t_plus_one_violation": "T+1 违规",
    "tradability_constraints_ignored": "忽略停牌/涨跌停",
    "transaction_costs_omitted": "遗漏交易成本",
    "revision_leakage": "修订数据提前使用",
    "delisting_survivorship": "退市幸存者偏差",
}


def _case_buttons(cases: list[dict[str, Any]]) -> str:
    return "".join(
        f'<button class="case-tab{" active" if index == 0 else ""}" data-case="{html.escape(case["id"])}">'
        f'<span>{index + 1:02d}</span>{html.escape(case["title"])}</button>'
        for index, case in enumerate(cases)
    )


def _initial_case(case: dict[str, Any]) -> str:
    return f"""
      <p class="eyebrow" id="case-id">{html.escape(case['id'])} · PRACTICE CASE</p>
      <h3 id="case-title">{html.escape(case['title'])}</h3>
      <p class="case-brief" id="case-brief">{html.escape(case['brief'])}</p>
      <div class="setup-list" id="case-setup">{''.join(f'<span>{html.escape(item)}</span>' for item in case['research_setup'])}</div>
      <div class="case-prompt"><span>给 Agent 的任务</span><p id="case-prompt">{html.escape(case['prompt'])}</p></div>
    """


def _track_rows(tracks: list[dict[str, Any]]) -> str:
    status = {"live": "运行中", "pilot": "试验中", "spec": "已定义", "planned": "排队中"}
    return "".join(
        f'<tr><td>Roadmap</td><td><strong>{html.escape(track["name_zh"])}</strong><span>{html.escape(track["name_en"])}</span></td>'
        f'<td>{html.escape(status.get(track["status"], track["status"]))}</td>'
        f'<td>{html.escape(track["deliverable"].split("：", 1)[0])}</td>'
        f'<td>{html.escape(" / ".join(track["metrics"][:2]))}</td></tr>'
        for track in tracks
    )


def _reference_rows() -> str:
    return "".join(
        f'<tr><td><a href="{html.escape(item["url"])}" target="_blank" rel="noreferrer">{html.escape(item["name"])} ↗</a></td>'
        f'<td>{html.escape(item["use"])}</td></tr>'
        for item in METHOD_REFERENCES
    )


def render_dashboard(
    audit_score: dict[str, Any],
    questions: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    cases: list[dict[str, Any]],
) -> str:
    cases_json = json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")
    issue_count = len(ISSUE_NAMES)
    public_agent_count = 0
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A 股研究 Agent 联赛：用可复现任务测试 Agent 能否抓出回测中的未来函数、幸存者偏差与不可成交假设。">
  <meta name="theme-color" content="#f3f5f4">
  <title>A-Share Agent Arena · OpenMarketEval</title>
  <style>
    :root {{ --ink:#172126; --muted:#68757b; --paper:#fff; --wash:#f3f5f4; --line:#d8dedc; --deep:#12272b; --red:#d74434; --teal:#0d8f83; --amber:#bb790e; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:14px/1.58 Inter,"PingFang SC","Microsoft YaHei",ui-sans-serif,system-ui,sans-serif; }}
    button {{ font:inherit; }} a {{ color:inherit; }}
    .shell {{ width:min(1180px,calc(100% - 36px)); margin:0 auto; }}
    header {{ position:sticky; top:0; z-index:30; border-bottom:1px solid var(--line); background:rgba(255,255,255,.96); backdrop-filter:blur(10px); }}
    nav {{ min-height:62px; display:flex; align-items:center; justify-content:space-between; gap:24px; }}
    .brand {{ display:flex; align-items:center; gap:10px; text-decoration:none; font-weight:850; }}
    .brand-mark {{ width:22px; height:22px; border:5px solid var(--red); border-right-color:var(--teal); border-radius:50%; }}
    .brand small {{ padding-left:10px; border-left:1px solid var(--line); color:var(--muted); font-size:11px; letter-spacing:0; }}
    .nav-links {{ display:flex; align-items:center; gap:20px; }} .nav-links a {{ color:var(--muted); text-decoration:none; font-size:13px; }}
    .nav-links .repo {{ padding:7px 11px; border:1px solid var(--line); border-radius:5px; color:var(--ink); font-weight:750; }}
    .hero {{ min-height:508px; display:flex; align-items:center; background:#fff url("assets/a-share-arena-forensics.png") center/cover no-repeat; border-bottom:1px solid var(--line); }}
    .hero-copy {{ width:min(600px,62%); padding:62px 0; }}
    .eyebrow {{ margin:0 0 9px; color:var(--red); font-size:11px; font-weight:850; text-transform:uppercase; }}
    h1 {{ margin:0; max-width:590px; font-size:52px; line-height:1.06; letter-spacing:0; }}
    .hero-lead {{ max-width:555px; margin:20px 0 23px; color:#4f5d62; font-size:18px; }}
    .hero-lead strong {{ color:var(--ink); }}
    .actions {{ display:flex; gap:10px; flex-wrap:wrap; }}
    .button {{ display:inline-flex; min-height:43px; align-items:center; justify-content:center; padding:0 15px; border:1px solid var(--ink); border-radius:5px; color:#fff; background:var(--ink); text-decoration:none; font-weight:800; }}
    .button.secondary {{ color:var(--ink); background:#fff; }}
    .hero-note {{ margin:18px 0 0; color:var(--muted); font-size:11px; }}
    .stats {{ background:var(--deep); color:#fff; }} .stats-grid {{ display:grid; grid-template-columns:repeat(4,1fr); }}
    .stat {{ min-height:92px; padding:17px 20px; border-right:1px solid rgba(255,255,255,.15); }} .stat:last-child {{ border-right:0; }}
    .stat strong {{ display:block; color:#fff; font-size:28px; line-height:1.1; }} .stat span {{ color:#9eb2b5; font-size:11px; }}
    .stat:nth-child(1) strong {{ color:#ff7060; }} .stat:nth-child(2) strong {{ color:#55d2c3; }} .stat:nth-child(3) strong {{ color:#efb64f; }}
    .band {{ border-bottom:1px solid var(--line); background:var(--paper); }} .band.alt {{ background:var(--wash); }} .band.dark {{ background:var(--deep); color:#fff; }}
    .band-inner {{ padding:54px 0; }}
    .section-head {{ display:grid; grid-template-columns:minmax(260px,.72fr) minmax(420px,1.28fr); gap:70px; align-items:end; margin-bottom:28px; }}
    h2 {{ margin:0; font-size:32px; line-height:1.16; letter-spacing:0; }} .section-head > p {{ margin:0; color:var(--muted); font-size:15px; }}
    .challenge-grid {{ display:grid; grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .challenge-copy {{ padding:28px 36px 28px 0; }} .challenge-side {{ padding:28px 0 28px 36px; border-left:1px solid var(--line); }}
    .challenge-title {{ display:flex; justify-content:space-between; gap:20px; align-items:start; }} .challenge-title h3 {{ margin:0; font-size:25px; }}
    .live-badge {{ padding:4px 8px; border:1px solid var(--teal); border-radius:4px; color:var(--teal); background:#effaf7; font-size:10px; font-weight:850; white-space:nowrap; }}
    .challenge-copy > p {{ max-width:700px; color:var(--muted); font-size:15px; }}
    .deliverables {{ display:grid; grid-template-columns:repeat(3,1fr); margin-top:22px; border:1px solid var(--line); }} .deliverables div {{ padding:13px; border-right:1px solid var(--line); }} .deliverables div:last-child {{ border-right:0; }} .deliverables span {{ display:block; color:var(--muted); font-size:10px; }} .deliverables strong {{ font-size:12px; }}
    .runbox {{ position:relative; margin-top:20px; padding:17px 48px 17px 18px; overflow:auto; background:#13252a; color:#dff3f1; }} .runbox code {{ white-space:nowrap; font:13px ui-monospace,SFMono-Regular,Consolas,monospace; }}
    .copy {{ position:absolute; top:9px; right:9px; width:30px; height:30px; border:1px solid #496068; color:#dff3f1; background:transparent; cursor:pointer; }}
    .challenge-side dl {{ margin:0; }} .challenge-side div {{ display:grid; grid-template-columns:95px 1fr; gap:14px; padding:10px 0; border-bottom:1px solid var(--line); }} .challenge-side div:last-child {{ border-bottom:0; }} .challenge-side dt {{ color:var(--muted); font-size:11px; }} .challenge-side dd {{ margin:0; font-weight:700; }}
    .case-workbench {{ display:grid; grid-template-columns:340px minmax(0,1fr); border:1px solid var(--line); background:#fff; }}
    .case-tabs {{ max-height:480px; overflow:auto; border-right:1px solid var(--line); }}
    .case-tab {{ display:grid; grid-template-columns:34px 1fr; width:100%; padding:13px 15px; border:0; border-bottom:1px solid var(--line); color:var(--muted); background:#f8f9f8; text-align:left; cursor:pointer; }} .case-tab span {{ color:#9aa4a5; font:700 11px ui-monospace,monospace; }} .case-tab.active {{ color:var(--ink); background:#fff; box-shadow:inset 3px 0 var(--red); font-weight:800; }}
    .case-detail {{ min-height:480px; padding:34px; }} .case-detail h3 {{ margin:0; font-size:28px; }} .case-brief {{ max-width:720px; margin:14px 0 22px; font-size:17px; font-weight:650; }}
    .setup-list {{ display:grid; grid-template-columns:repeat(3,1fr); border-top:1px solid var(--line); border-left:1px solid var(--line); }} .setup-list span {{ min-height:82px; padding:12px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); color:var(--muted); font-size:12px; }}
    .case-prompt {{ margin-top:24px; padding:18px; border-left:3px solid var(--red); background:var(--wash); }} .case-prompt span {{ color:var(--red); font-size:10px; font-weight:850; }} .case-prompt p {{ margin:5px 0 0; }}
    .score-layout {{ display:grid; grid-template-columns:.8fr 1.2fr; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .score-summary {{ padding:28px 34px 28px 0; }} .score-grid {{ display:grid; grid-template-columns:1fr 1fr; margin-top:19px; border:1px solid var(--line); }} .score-grid div {{ padding:17px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }} .score-grid div:nth-child(2n) {{ border-right:0; }} .score-grid div:nth-last-child(-n+2) {{ border-bottom:0; }} .score-grid strong {{ display:block; font-size:26px; }} .score-grid span {{ color:var(--muted); font-size:10px; }}
    .score-summary p {{ color:var(--muted); }} .score-note {{ padding-top:12px; border-top:1px solid var(--line); font-size:11px; }}
    .score-table {{ min-width:0; max-width:100%; padding:28px 0 28px 34px; border-left:1px solid var(--line); overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; min-width:610px; }} th,td {{ padding:11px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }} th {{ color:var(--muted); font-size:10px; text-transform:uppercase; }} td span {{ display:block; color:var(--muted); font-size:10px; }} tr:last-child td {{ border-bottom:0; }}
    .miss {{ color:var(--red); }} .pass {{ color:var(--teal); }}
    .ops {{ display:grid; grid-template-columns:repeat(4,1fr); border-top:1px solid rgba(255,255,255,.18); }} .op {{ padding:26px 22px; border-right:1px solid rgba(255,255,255,.18); }} .op:last-child {{ border-right:0; }} .op b {{ color:#ff7667; font:800 12px ui-monospace,monospace; }} .op h3 {{ margin:15px 0 7px; font-size:17px; }} .op p {{ margin:0; color:#a8babc; font-size:12px; }}
    .dark .section-head > p {{ color:#a8babc; }}
    .star-contract {{ display:grid; grid-template-columns:repeat(3,1fr); border-top:1px solid var(--line); }} .contract {{ padding:25px 25px 25px 0; border-right:1px solid var(--line); }} .contract + .contract {{ padding-left:25px; }} .contract:last-child {{ border-right:0; }} .contract strong {{ display:block; margin-bottom:7px; font-size:16px; }} .contract p {{ margin:0; color:var(--muted); }}
    .season-table {{ min-width:0; max-width:100%; overflow:auto; }} .season-table td:first-child {{ font-weight:800; }} .season-table .current td {{ background:#f1faf7; }}
    .join {{ display:grid; grid-template-columns:1fr auto; gap:40px; align-items:center; }} .join p {{ max-width:700px; color:#a8babc; }} .join .actions {{ justify-content:flex-end; }} .join .button {{ border-color:#fff; }} .join .button.secondary {{ color:#fff; background:transparent; }}
    .foot {{ padding:24px 0 34px; color:var(--muted); }} .foot-line {{ display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap; }}
    @media (max-width:900px) {{ .hero-copy {{ width:72%; }} .section-head {{ grid-template-columns:1fr; gap:13px; }} .challenge-grid,.score-layout {{ grid-template-columns:1fr; }} .challenge-copy,.score-summary {{ padding-right:0; }} .challenge-side,.score-table {{ padding-left:0; border-left:0; border-top:1px solid var(--line); }} .case-workbench {{ grid-template-columns:260px minmax(0,1fr); }} .ops {{ grid-template-columns:1fr 1fr; }} .op:nth-child(2) {{ border-right:0; }} .op:nth-child(-n+2) {{ border-bottom:1px solid rgba(255,255,255,.18); }} }}
    @media (max-width:680px) {{ .shell {{ width:min(100% - 24px,1180px); }} .nav-links a:not(.repo) {{ display:none; }} .brand small {{ display:none; }} .hero {{ min-height:535px; align-items:start; background-position:58% center; }} .hero-copy {{ width:100%; padding:35px 0; }} h1 {{ max-width:330px; font-size:38px; }} .hero-lead {{ max-width:345px; font-size:16px; }} .hero-copy .actions {{ width:220px; flex-direction:column; }} .stats-grid {{ grid-template-columns:1fr 1fr; }} .stat:nth-child(2) {{ border-right:0; }} .stat:nth-child(-n+2) {{ border-bottom:1px solid rgba(255,255,255,.15); }} .band-inner {{ padding:40px 0; }} h2 {{ font-size:27px; }} .challenge-copy {{ padding-top:22px; }} .challenge-side {{ padding-top:22px; }} .deliverables {{ grid-template-columns:1fr; }} .deliverables div {{ border-right:0; border-bottom:1px solid var(--line); }} .deliverables div:last-child {{ border-bottom:0; }} .case-workbench {{ grid-template-columns:1fr; }} .case-tabs {{ display:flex; max-height:none; overflow:auto; border-right:0; border-bottom:1px solid var(--line); }} .case-tab {{ min-width:170px; }} .case-detail {{ min-height:430px; padding:24px 18px; }} .setup-list {{ grid-template-columns:1fr; }} .setup-list span {{ min-height:0; }} .score-grid {{ grid-template-columns:1fr 1fr; }} .ops,.star-contract {{ grid-template-columns:1fr; }} .op,.op:nth-child(2),.contract,.contract + .contract {{ padding:21px 0; border-right:0; border-bottom:1px solid rgba(255,255,255,.18); }} .star-contract .contract {{ border-bottom-color:var(--line); }} .join {{ grid-template-columns:1fr; }} .join .actions {{ justify-content:flex-start; flex-direction:column; }} .join .button {{ width:100%; }} }}
    @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"></span>OpenMarketEval <small>A-SHARE AGENT ARENA</small></a><div class="nav-links"><a href="#challenge">本期挑战</a><a href="#scoring">评分</a><a href="#season">赛季</a><a href="#operations">运营机制</a><a class="repo" href="https://github.com/Alfonsobang/open-market-eval">GitHub ↗</a></div></nav></header>

  <main id="top">
    <section class="hero"><div class="shell"><div class="hero-copy"><p class="eyebrow">A-SHARE AGENT ARENA · PRESEASON</p><h1>A 股研究 Agent 联赛</h1><p class="hero-lead"><strong>首关：抓出回测里偷看的未来。</strong><br>把任意 Agent 放进同一组 A 股研究陷阱，比较它能否识别未来函数、幸存者偏差和不可能成交。</p><div class="actions"><a class="button" href="#challenge">运行首关</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval/tree/main/benchmarks/a-share-backtest-forensics">查看 10 个案例 ↗</a></div><p class="hero-note">公开开发集 · 无需 API Key · 不含荐股 · 不声称投资收益</p></div></div></section>
    <div class="stats"><div class="shell stats-grid"><div class="stat"><strong>{len(cases)}</strong><span>可运行回测取证案例</span></div><div class="stat"><strong>{issue_count}</strong><span>A 股特有缺陷类别</span></div><div class="stat"><strong>1</strong><span>Harbor 风格确定性任务</span></div><div class="stat"><strong>{public_agent_count}</strong><span>公开参赛 Agent，等待首份外部成绩</span></div></div></div>

    <section class="band" id="challenge"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">CURRENT CHALLENGE</p><h2>Backtest Forensics<br>回测取证开发集</h2></div><p>它不是又一个收益预测 Demo。用户交付的是缺陷证据，评分器同时惩罚漏检和误报；两个干净控制组专门测试 Agent 会不会为了显得专业而乱报问题。</p></div><div class="challenge-grid"><div class="challenge-copy"><div class="challenge-title"><h3>Preseason · 10-case public dev pack</h3><span class="live-badge">SCORER LIVE</span></div><p>覆盖同收盘价成交、当前股票池回放、复权价成交、T+1、停牌与涨跌停、交易成本、财务修订穿越和退市幸存者偏差。</p><div class="deliverables"><div><span>INPUT</span><strong>cases.jsonl</strong></div><div><span>AGENT OUTPUT</span><strong>audit_report.jsonl</strong></div><div><span>VERDICT</span><strong>scorecard.json + .md</strong></div></div><div class="runbox"><code id="run-command">python -m open_market_eval audit-demo</code><button class="copy" id="copy-command" title="复制命令" aria-label="复制运行命令">⧉</button></div></div><div class="challenge-side"><dl><div><dt>安装</dt><dd>零第三方依赖</dd></div><div><dt>评分</dt><dd>Precision / Recall / F1 / Exact</dd></div><div><dt>数据</dt><dd>合成场景，不重分发市场数据</dd></div><div><dt>完整性</dt><dd>公开开发集，不用于隐藏榜排名</dd></div><div><dt>接入</dt><dd>JSONL + Harbor 风格任务</dd></div></dl></div></div></div></section>

    <section class="band alt" id="cases"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">CASE EXPLORER</p><h2>先看一关，再决定你的 Agent 会不会审。</h2></div><p>点击任意案例查看研究设置。正式提交必须给出标准缺陷代码与可定位的证据句，不能只输出“可能存在未来函数”。</p></div><div class="case-workbench"><div class="case-tabs">{_case_buttons(cases)}</div><div class="case-detail">{_initial_case(cases[0])}</div></div></div></section>

    <section class="band" id="scoring"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">REAL SCORECARD</p><h2>成绩不是“看起来挺专业”。</h2></div><p>下方来自仓库内手工编写的格式示例，用来证明评分闭环。它故意漏掉两项，因此召回率和逐案命中不会满分；这不是任何模型成绩。</p></div><div class="score-layout"><div class="score-summary"><p class="eyebrow">FORMAT FIXTURE · NOT A MODEL</p><h3>示例评分输出</h3><div class="score-grid"><div><strong>{audit_score['precision']:.1%}</strong><span>PRECISION</span></div><div><strong>{audit_score['recall']:.1%}</strong><span>RECALL</span></div><div><strong>{audit_score['f1']:.1%}</strong><span>F1</span></div><div><strong>{audit_score['exact_case_accuracy']:.1%}</strong><span>EXACT CASE</span></div></div><p class="score-note">公开 Agent 榜目前为空。第一个外部可复现提交会获得首位记录，但必须公开模型、Agent、运行参数和原始输出。</p></div><div class="score-table"><table><thead><tr><th>案例</th><th>判定</th><th>检出</th><th>漏检</th></tr></thead><tbody>{''.join(f'<tr><td>{html.escape(case["case_id"])}</td><td class="{"pass" if case["exact_match"] else "miss"}">{"完全命中" if case["exact_match"] else "有漏检"}</td><td>{len(case["correct"])}</td><td>{html.escape(", ".join(ISSUE_NAMES.get(code, code) for code in case["missed"]) or "—")}</td></tr>' for case in audit_score['cases'])}</tbody></table></div></div></div></section>

    <section class="band dark" id="operations"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">OPERATING SYSTEM</p><h2>不是发几篇文章，是每月完成一个公开赛季。</h2></div><p>运营内容全部由真实实验自动产生：新任务、参赛轨迹、失败案例和榜单更新。没有新实验，就不制造空洞热点。</p></div><div class="ops"><div class="op"><b>WEEK 01</b><h3>发布挑战</h3><p>释出任务合同、输入包、评分维度和一条可运行命令。</p></div><div class="op"><b>WEEK 02</b><h3>Agent 公开跑</h3><p>征集不同模型与框架，封存配置、成本和完整原始输出。</p></div><div class="op"><b>WEEK 03</b><h3>失败取证</h3><p>拆解最有教育价值的漏检与误报，形成可传播研究笔记。</p></div><div class="op"><b>WEEK 04</b><h3>发布榜单</h3><p>更新可复现成绩、变更日志和下期挑战，不隐藏失败。</p></div></div></div></section>

    <section class="band" id="season"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">SEASON MAP</p><h2>一个旗舰联赛，五条研究能力轨道。</h2></div><p>回测取证负责打开知名度，公告搜索与时点查数负责建立 A 股数据工程深度，事件预测和研究备忘录负责形成长期评测体系。</p></div><div class="season-table"><table><thead><tr><th>阶段</th><th>挑战</th><th>状态</th><th>公开交付物</th><th>主要指标</th></tr></thead><tbody><tr class="current"><td>Preseason</td><td>Backtest Forensics</td><td class="pass">评分器已上线</td><td>10-case dev pack</td><td>Precision / Recall / F1</td></tr>{_track_rows(tracks)}</tbody></table></div></div></section>

    <section class="band alt" id="star"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">WHY FOLLOW</p><h2>关注这个仓库，你会持续得到什么？</h2></div><p>不是每日行情观点，而是一套越来越难、越来越接近真实投研工作的公共 Agent 压力测试。</p></div><div class="star-contract"><div class="contract"><strong>每月一个可运行挑战</strong><p>任务、输入合同、评分器和失败样例一起发布，不只给结论。</p></div><div class="contract"><strong>所有失误进入公开档案</strong><p>榜单之外保留漏检、误报、时间穿越和不可成交假设。</p></div><div class="contract"><strong>连接 Harbor 与量化生态</strong><p>持续输出 Harbor 任务、Qlib 数据边界和通用 Agent adapter。</p></div></div><div class="section-head" style="margin-top:48px"><div><p class="eyebrow">TECHNICAL LINEAGE</p><h2>站在可验证工具之上。</h2></div><p>引用只用于说明方法来源，不代表项目背书或官方合作。</p></div><div class="season-table"><table><tbody>{_reference_rows()}</tbody></table></div></div></section>

    <section class="band dark"><div class="shell band-inner join"><div><p class="eyebrow">ENTER THE ARENA</p><h2>提交第一份外部 Agent 成绩。</h2><p>运行开发集，保留完整输出与参数，然后提交成绩 issue。我们优先接受可复现失败，不接受收益宣传、荐股和无法核验的截图。</p></div><div class="actions"><a class="button" href="https://github.com/Alfonsobang/open-market-eval/issues/new">提交 Agent 成绩 ↗</a><a class="button secondary" href="https://github.com/Alfonsobang/open-market-eval/tree/main/integrations/harbor/a-share-backtest-audit">运行 Harbor 任务 ↗</a></div></div></section>
  </main>

  <footer class="foot"><div class="shell foot-line"><span>OpenMarketEval · A-Share Agent Arena</span><span>{len(sources)} 个来源已注册 · {len(questions)} 个封存事件问题 · 不构成投资建议</span></div></footer>
  <script>
    const cases = {cases_json};
    const byId = Object.fromEntries(cases.map(item => [item.id, item]));
    const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
    function showCase(id) {{
      const item = byId[id]; if (!item) return;
      document.querySelectorAll('[data-case]').forEach(button => button.classList.toggle('active', button.dataset.case === id));
      document.querySelector('#case-id').textContent = `${{item.id}} · PRACTICE CASE`;
      document.querySelector('#case-title').textContent = item.title;
      document.querySelector('#case-brief').textContent = item.brief;
      document.querySelector('#case-setup').innerHTML = item.research_setup.map(value => `<span>${{escapeHtml(value)}}</span>`).join('');
      document.querySelector('#case-prompt').textContent = item.prompt;
    }}
    document.querySelectorAll('[data-case]').forEach(button => button.addEventListener('click', () => showCase(button.dataset.case)));
    document.querySelector('#copy-command').addEventListener('click', async () => {{
      await navigator.clipboard.writeText(document.querySelector('#run-command').textContent);
      const button = document.querySelector('#copy-command'); button.textContent = '✓'; setTimeout(() => button.textContent = '⧉', 1200);
    }});
  </script>
</body>
</html>
"""


def build_site(
    audit_score: dict[str, Any],
    questions: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    output: str | Path,
    image_path: str | Path,
) -> None:
    destination = Path(output)
    assets = destination / "assets"
    data = destination / "data"
    assets.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(
        render_dashboard(audit_score, questions, tracks, sources, cases), encoding="utf-8"
    )
    shutil.copyfile(image_path, assets / "a-share-arena-forensics.png")
    for name, value in (
        ("audit-dev-scorecard.json", audit_score),
        ("a-share-backtest-cases.json", cases),
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
