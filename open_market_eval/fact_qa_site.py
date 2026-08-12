from __future__ import annotations

import html
import json
from typing import Any


def _task_buttons(tasks: list[dict[str, Any]]) -> str:
    return "".join(
        f'<button class="task-tab{" active" if index == 0 else ""}" '
        f'data-task="{html.escape(task["task_id"])}">'
        f"<span>{html.escape(task['security_code'])}</span>"
        f"<strong>{html.escape(task['company_name_zh'])}</strong>"
        f"<small>{'营业收入' if task['field'] == 'operating_revenue' else '研发投入'}</small>"
        "</button>"
        for index, task in enumerate(tasks)
    )


def _source_rows(sources: list[dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td><strong>{html.escape(source['security_code'])}</strong>"
        f"<span>{html.escape(source['company_name_zh'])}</span></td>"
        f"<td>{html.escape(source['published_date'])}</td>"
        f"<td><code>{html.escape(source['sha256'][:12])}...</code>"
        f"<span>{source['bytes']:,} bytes</span></td>"
        f'<td><a href="{html.escape(source["url"])}" target="_blank" '
        'rel="noreferrer">CNINFO PDF</a></td>'
        "</tr>"
        for source in sources
    )


def render_fact_qa_lab(
    tasks: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> str:
    sources = manifest["sources"]
    tasks_json = json.dumps(tasks, ensure_ascii=False).replace("</", "<\\/")
    labels_json = json.dumps(labels, ensure_ascii=False).replace("</", "<\\/")
    sources_json = json.dumps(sources, ensure_ascii=False).replace("</", "<\\/")
    first = tasks[0]
    first_source = next(item for item in sources if item["id"] == first["source_id"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="用五份巨潮资讯官方 A 股年报，测试 Agent 的数值提取、单位归一化、PDF 页码与来源追溯。">
  <meta name="theme-color" content="#f4f6f5">
  <link rel="icon" href="data:,">
  <title>A 股年报时点查数实验室 · OpenMarketEval</title>
  <style>
    :root {{ --ink:#172126; --muted:#68757b; --paper:#fff; --wash:#f4f6f5; --line:#d8dedc; --deep:#12272b; --red:#d74434; --teal:#0d8f83; --amber:#ad7008; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:14px/1.58 Inter,"PingFang SC","Microsoft YaHei",ui-sans-serif,system-ui,sans-serif; }}
    button,input,select {{ font:inherit; }} a {{ color:inherit; }} code {{ font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }}
    .shell {{ width:min(1180px,calc(100% - 36px)); margin:0 auto; }}
    header {{ position:sticky; top:0; z-index:20; border-bottom:1px solid var(--line); background:rgba(255,255,255,.96); }}
    nav {{ min-height:62px; display:flex; align-items:center; justify-content:space-between; gap:24px; }}
    .brand {{ display:flex; align-items:center; gap:10px; text-decoration:none; font-weight:850; }}
    .brand-mark {{ width:22px; height:22px; border:5px solid var(--red); border-right-color:var(--teal); border-radius:50%; }}
    .nav-links {{ display:flex; align-items:center; gap:18px; }} .nav-links a {{ color:var(--muted); text-decoration:none; font-size:13px; }}
    .nav-links .repo {{ padding:7px 11px; border:1px solid var(--line); border-radius:5px; color:var(--ink); font-weight:750; }}
    .intro {{ padding:52px 0 34px; border-bottom:1px solid var(--line); background:#fff; }}
    .eyebrow {{ margin:0 0 8px; color:var(--red); font-size:11px; font-weight:850; text-transform:uppercase; }}
    h1 {{ margin:0; max-width:800px; font-size:42px; line-height:1.1; letter-spacing:0; }}
    .lead {{ max-width:820px; margin:18px 0 0; color:var(--muted); font-size:17px; }}
    .stats {{ display:grid; grid-template-columns:repeat(4,1fr); margin-top:30px; border-top:1px solid var(--line); border-left:1px solid var(--line); }}
    .stat {{ min-height:82px; padding:14px 16px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .stat strong {{ display:block; font-size:25px; }} .stat span {{ color:var(--muted); font-size:11px; }}
    .band {{ border-bottom:1px solid var(--line); background:#fff; }} .band.alt {{ background:var(--wash); }} .band-inner {{ padding:46px 0; }}
    .section-head {{ display:grid; grid-template-columns:minmax(270px,.72fr) minmax(380px,1.28fr); gap:60px; align-items:end; margin-bottom:24px; }}
    h2 {{ margin:0; font-size:29px; line-height:1.2; letter-spacing:0; }} .section-head>p {{ margin:0; color:var(--muted); }}
    .workbench {{ display:grid; grid-template-columns:280px minmax(0,1fr); border:1px solid var(--line); background:#fff; }}
    .task-list {{ max-height:690px; overflow:auto; border-right:1px solid var(--line); }}
    .task-tab {{ display:grid; grid-template-columns:58px 1fr auto; width:100%; min-height:58px; align-items:center; gap:8px; padding:10px 12px; border:0; border-bottom:1px solid var(--line); color:var(--muted); background:#f8f9f8; text-align:left; cursor:pointer; }}
    .task-tab span {{ font:700 11px ui-monospace,monospace; }} .task-tab strong {{ color:var(--ink); font-size:12px; }} .task-tab small {{ font-size:10px; white-space:nowrap; }}
    .task-tab.active {{ background:#fff; box-shadow:inset 3px 0 var(--teal); }}
    .task-main {{ min-width:0; padding:28px 30px; }} .question {{ margin:0 0 18px; font-size:21px; font-weight:760; }}
    .source-line {{ display:flex; flex-wrap:wrap; gap:8px 18px; padding:11px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); color:var(--muted); font-size:11px; }}
    .source-line a {{ color:var(--teal); font-weight:750; }}
    .answer-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px 16px; margin-top:22px; }}
    label span {{ display:block; margin-bottom:5px; color:var(--muted); font-size:10px; font-weight:750; text-transform:uppercase; }}
    input,select {{ width:100%; height:40px; padding:0 10px; border:1px solid var(--line); border-radius:4px; color:var(--ink); background:#fff; }}
    input:focus,select:focus {{ outline:2px solid rgba(13,143,131,.2); border-color:var(--teal); }}
    .actions {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:20px; }}
    .button {{ min-height:41px; padding:0 14px; border:1px solid var(--ink); border-radius:5px; color:#fff; background:var(--ink); cursor:pointer; font-weight:800; }}
    .button.secondary {{ color:var(--ink); background:#fff; }}
    .result {{ margin-top:22px; padding-top:19px; border-top:1px solid var(--line); }} .result h3 {{ margin:0; font-size:18px; }}
    .field-results {{ display:grid; grid-template-columns:repeat(4,1fr); margin-top:12px; border-top:1px solid var(--line); border-left:1px solid var(--line); }}
    .field-result {{ min-height:62px; padding:10px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .field-result strong {{ display:block; font-size:11px; }} .field-result span {{ color:var(--muted); font-size:10px; }} .field-result.pass strong {{ color:var(--teal); }} .field-result.fail strong {{ color:var(--red); }}
    .reference {{ display:none; margin-top:16px; padding:15px; border-left:3px solid var(--amber); background:#fff9ed; }} .reference.visible {{ display:block; }} .reference p {{ margin:0 0 8px; }} .reference code {{ overflow-wrap:anywhere; }}
    .downloads {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:18px; }} .downloads a {{ padding:7px 10px; border:1px solid var(--line); border-radius:4px; background:#fff; text-decoration:none; font-size:12px; font-weight:700; }}
    .table-wrap {{ overflow:auto; border-top:1px solid var(--line); }} table {{ width:100%; min-width:720px; border-collapse:collapse; }} th,td {{ padding:11px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }} th {{ color:var(--muted); font-size:10px; text-transform:uppercase; }} td span {{ display:block; color:var(--muted); font-size:10px; }} td a {{ color:var(--teal); font-weight:750; }}
    .contract-grid {{ display:grid; grid-template-columns:repeat(3,1fr); border-top:1px solid var(--line); }} .contract {{ padding:21px 24px 21px 0; border-right:1px solid var(--line); }} .contract+.contract {{ padding-left:24px; }} .contract:last-child {{ border-right:0; }} .contract strong {{ display:block; margin-bottom:6px; }} .contract p {{ margin:0; color:var(--muted); font-size:12px; }}
    footer {{ padding:24px 0 34px; color:var(--muted); font-size:12px; }}
    @media(max-width:820px) {{ .section-head {{ grid-template-columns:1fr; gap:10px; }} .workbench {{ grid-template-columns:1fr; }} .task-list {{ display:flex; max-height:none; overflow:auto; border-right:0; border-bottom:1px solid var(--line); }} .task-tab {{ min-width:220px; }} .field-results {{ grid-template-columns:repeat(2,1fr); }} }}
    @media(max-width:620px) {{ .shell {{ width:min(100% - 24px,1180px); }} .nav-links a:not(.repo) {{ display:none; }} h1 {{ font-size:34px; }} .intro {{ padding-top:36px; }} .stats,.answer-grid,.contract-grid {{ grid-template-columns:1fr 1fr; }} .contract,.contract+.contract {{ padding:17px 10px; border-bottom:1px solid var(--line); }} .contract:last-child {{ grid-column:1/-1; }} .task-main {{ padding:22px 16px; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span>OpenMarketEval</a><div class="nav-links"><a href="index.html">Agent 联赛</a><a href="research-audit.html">证据审计</a><a class="repo" href="https://github.com/Alfonsobang/open-market-eval">GitHub ↗</a></div></nav></header>
  <main>
    <section class="intro"><div class="shell"><p class="eyebrow">POINT-IN-TIME FILING QA · PUBLIC DEV PACK</p><h1>A 股年报时点查数实验室</h1><p class="lead">用官方年报检验 Agent 能否找到正确数值、保留披露单位、归一化为人民币元，并返回可复核的 PDF 物理页码与来源版本。所有验证在浏览器本地执行。</p><div class="stats"><div class="stat"><strong>{len(tasks)}</strong><span>公开查数任务</span></div><div class="stat"><strong>{len(sources)}</strong><span>巨潮资讯官方年报</span></div><div class="stat"><strong>7</strong><span>逐字段精确评分</span></div><div class="stat"><strong>SHA-256</strong><span>来源内容封存</span></div></div></div></section>
    <section class="band alt"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">LOCAL WORKBENCH</p><h2>选择任务，填写答案，逐字段核验。</h2></div><p>这是公开开发集，不是隐藏榜单。它适合调试金融搜索 Agent、OCR/解析流程和单位归一化逻辑，不代表投资研究或预测能力。</p></div><div class="workbench"><div class="task-list">{_task_buttons(tasks)}</div><div class="task-main"><p class="eyebrow" id="task-id">{html.escape(first["task_id"])}</p><p class="question" id="question">{html.escape(first["question_zh"])}</p><div class="source-line"><span id="company">{html.escape(first["company_name_zh"])} · {html.escape(first["security_code"])}</span><span id="cutoff">截止 {html.escape(first["as_of"])}</span><a id="source-link" href="{html.escape(first_source["url"])}" target="_blank" rel="noreferrer">打开官方年报 ↗</a></div><div class="answer-grid"><label><span>披露原始数值</span><input id="value" inputmode="decimal" autocomplete="off" placeholder="例如 362012554"></label><label><span>披露单位</span><select id="unit"><option value="">请选择</option><option value="CNY_YUAN">CNY_YUAN</option><option value="CNY_THOUSAND">CNY_THOUSAND</option></select></label><label><span>归一化人民币元</span><input id="normalized_value_yuan" inputmode="decimal" autocomplete="off" placeholder="例如 362012554000"></label><label><span>报告期间</span><input id="period" autocomplete="off" placeholder="YYYY"></label><label><span>披露口径</span><select id="scope"><option value="">请选择</option><option value="listed_company_consolidated">listed_company_consolidated</option></select></label><label><span>PDF 物理页码</span><input id="pdf_page" type="number" min="1" step="1" placeholder="从 1 开始"></label><label><span>来源 ID</span><input id="source_id" autocomplete="off" placeholder="cninfo-..."></label></div><div class="actions"><button class="button" id="check-answer">核验答案</button><button class="button secondary" id="show-reference">显示参考标签</button><button class="button secondary" id="clear-answer">清空</button></div><div class="result" aria-live="polite"><h3 id="result-title">等待提交</h3><div class="field-results" id="field-results"></div><div class="reference" id="reference"></div></div></div></div><div class="downloads"><a href="data/fact-qa-tasks.jsonl" download>下载任务 JSONL</a><a href="data/fact-qa-labels.jsonl" download>下载公开标签</a><a href="data/fact-qa-sources.json" download>下载来源清单</a><a href="https://github.com/Alfonsobang/open-market-eval/tree/main/integrations/harbor/a-share-point-in-time-qa">运行 Harbor 任务 ↗</a></div></div></section>
    <section class="band"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">SOURCE REGISTRY</p><h2>五份来源，全部来自官方公告。</h2></div><p>仓库仅保存链接、文件字节数、哈希与事实标签，不重分发 PDF。若官方文件变化，应发布新版本并记录差异，不能静默覆盖。</p></div><div class="table-wrap"><table><thead><tr><th>证券 / 公司</th><th>公告日期</th><th>内容封存</th><th>官方文件</th></tr></thead><tbody>{_source_rows(sources)}</tbody></table></div></div></section>
    <section class="band alt"><div class="shell band-inner"><div class="section-head"><div><p class="eyebrow">EVALUATION CONTRACT</p><h2>查对数字只是第一步。</h2></div><p>真正可复现的金融查数必须同时回答“哪个版本、什么单位、哪个口径、哪一页”。评分器把这些证据字段与数值本身同等对待。</p></div><div class="contract-grid"><div class="contract"><strong>时点与版本</strong><p>任务绑定公告日期、官方 URL、文件长度和 SHA-256，避免事后替换报告。</p></div><div class="contract"><strong>单位与口径</strong><p>原值、原单位和归一化元值分开评分，不能用一个看似正确的大数掩盖缩放错误。</p></div><div class="contract"><strong>证据可定位</strong><p>必须返回从 1 开始计数的 PDF 物理页码与来源 ID，便于人工复核。</p></div></div></div></section>
  </main>
  <footer><div class="shell">OpenMarketEval · Public development data only · 不构成投资建议 · 不含私有公司或真实用户数据</div></footer>
  <script>
    const tasks={tasks_json}, labels={labels_json}, sources={sources_json};
    const taskById=Object.fromEntries(tasks.map(item=>[item.task_id,item]));
    const labelById=Object.fromEntries(labels.map(item=>[item.task_id,item]));
    const sourceById=Object.fromEntries(sources.map(item=>[item.id,item]));
    const fields=['value','unit','normalized_value_yuan','period','scope','pdf_page','source_id'];
    const fieldNames={{value:'原始数值',unit:'披露单位',normalized_value_yuan:'归一化元值',period:'期间',scope:'口径',pdf_page:'PDF 页码',source_id:'来源 ID'}};
    let currentId={json.dumps(first["task_id"])};
    const numeric=value=>String(value??'').replaceAll(',','').trim();
    function matches(field,actual,expected){{ return field==='value'||field==='normalized_value_yuan'?numeric(actual)===numeric(expected):field==='pdf_page'?Number(actual)===expected&&String(actual).trim()!=='':actual===expected; }}
    function clearAnswer(){{ fields.forEach(field=>document.querySelector('#'+field).value=''); document.querySelector('#result-title').textContent='等待提交'; document.querySelector('#field-results').innerHTML=''; document.querySelector('#reference').classList.remove('visible'); }}
    function showTask(id){{ const task=taskById[id],source=sourceById[task.source_id]; currentId=id; document.querySelectorAll('[data-task]').forEach(button=>button.classList.toggle('active',button.dataset.task===id)); document.querySelector('#task-id').textContent=task.task_id; document.querySelector('#question').textContent=task.question_zh; document.querySelector('#company').textContent=`${{task.company_name_zh}} · ${{task.security_code}}`; document.querySelector('#cutoff').textContent=`截止 ${{task.as_of}}`; const link=document.querySelector('#source-link'); link.href=source.url; clearAnswer(); }}
    function checkAnswer(){{ const expected=labelById[currentId],results=fields.map(field=>{{const actual=field==='pdf_page'?document.querySelector('#'+field).value:document.querySelector('#'+field).value.trim();return [field,matches(field,actual,expected[field])];}}),correct=results.filter(([,ok])=>ok).length; document.querySelector('#result-title').textContent=`${{correct}} / ${{fields.length}} 个字段正确`; document.querySelector('#field-results').innerHTML=results.map(([field,ok])=>`<div class="field-result ${{ok?'pass':'fail'}}"><strong>${{ok?'PASS':'CHECK'}}</strong><span>${{fieldNames[field]}}</span></div>`).join(''); }}
    function showReference(){{ const label=labelById[currentId],source=sourceById[label.source_id],box=document.querySelector('#reference'); box.innerHTML=`<p><strong>公开参考标签</strong></p><code>${{JSON.stringify(label)}}</code><p style="margin-top:10px">来源封存：<code>${{source.sha256}}</code> · ${{source.bytes.toLocaleString()}} bytes</p>`; box.classList.add('visible'); }}
    document.querySelectorAll('[data-task]').forEach(button=>button.addEventListener('click',()=>showTask(button.dataset.task)));
    document.querySelector('#check-answer').addEventListener('click',checkAnswer);
    document.querySelector('#show-reference').addEventListener('click',showReference);
    document.querySelector('#clear-answer').addEventListener('click',clearAnswer);
  </script>
</body>
</html>
"""
