from __future__ import annotations

import json
from typing import Any


def render_research_audit_lab(
    safe_packet: dict[str, Any], risky_packet: dict[str, Any]
) -> str:
    safe_json = json.dumps(safe_packet, ensure_ascii=False).replace("</", "<\\/")
    risky_json = json.dumps(risky_packet, ensure_ascii=False).replace("</", "<\\/")
    return rf"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A local-first quality gate for A-share financial-search evidence packets.">
  <meta name="theme-color" content="#12272b">
  <title>A-Share Evidence Audit | OpenMarketEval</title>
  <style>
    :root {{ --ink:#172126; --muted:#66757a; --paper:#fff; --wash:#f2f5f4; --line:#d5dcda; --deep:#12272b; --red:#d74434; --teal:#087f75; --amber:#b56e00; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:14px/1.55 Inter,"PingFang SC","Microsoft YaHei",ui-sans-serif,system-ui,sans-serif; }}
    button,textarea {{ font:inherit; }} a {{ color:inherit; }}
    .shell {{ width:min(1220px,calc(100% - 36px)); margin:0 auto; }}
    header {{ border-bottom:1px solid var(--line); background:#fff; }}
    nav {{ min-height:62px; display:flex; align-items:center; justify-content:space-between; gap:20px; }}
    .brand {{ display:flex; align-items:center; gap:10px; text-decoration:none; font-weight:850; }}
    .mark {{ width:22px; height:22px; border:5px solid var(--red); border-right-color:var(--teal); border-radius:50%; }}
    .nav-actions {{ display:flex; gap:18px; align-items:center; }} .nav-actions a {{ color:var(--muted); text-decoration:none; font-size:12px; }}
    .repo {{ padding:7px 11px; border:1px solid var(--line); border-radius:4px; color:var(--ink)!important; font-weight:750; }}
    .hero {{ color:#fff; background:var(--deep); border-bottom:4px solid var(--red); }}
    .hero-grid {{ display:grid; grid-template-columns:1.25fr .75fr; gap:64px; padding:48px 0 42px; align-items:end; }}
    .eyebrow {{ margin:0 0 8px; color:#69d4c7; font:800 11px ui-monospace,monospace; }}
    h1 {{ margin:0; max-width:720px; font-size:42px; line-height:1.08; letter-spacing:0; }}
    .lead {{ max-width:690px; margin:17px 0 0; color:#b9cbcd; font-size:17px; }}
    .privacy {{ padding:17px 0 0 22px; border-left:2px solid #69d4c7; color:#b9cbcd; }} .privacy strong {{ display:block; color:#fff; }}
    .metrics {{ color:#fff; background:#1c3438; }} .metric-grid {{ display:grid; grid-template-columns:repeat(4,1fr); }}
    .metric {{ padding:15px 18px; border-right:1px solid rgba(255,255,255,.14); }} .metric:last-child {{ border-right:0; }}
    .metric strong {{ display:block; color:#fff; font-size:20px; }} .metric span {{ color:#9fb4b6; font-size:10px; }}
    main {{ padding:34px 0 56px; }}
    .workbench {{ display:grid; grid-template-columns:minmax(0,1.08fr) minmax(390px,.92fr); min-height:650px; border:1px solid var(--line); background:#fff; }}
    .editor {{ min-width:0; padding:26px; border-right:1px solid var(--line); }} .results {{ min-width:0; padding:26px; }}
    .panel-head {{ display:flex; justify-content:space-between; gap:18px; align-items:start; margin-bottom:16px; }}
    .panel-head h2 {{ margin:0; font-size:20px; letter-spacing:0; }} .panel-head p {{ margin:3px 0 0; color:var(--muted); font-size:11px; }}
    .segmented {{ display:flex; border:1px solid var(--line); border-radius:4px; overflow:hidden; }}
    .segmented button {{ min-height:34px; padding:0 11px; border:0; border-right:1px solid var(--line); background:#fff; cursor:pointer; font-size:11px; }} .segmented button:last-child {{ border-right:0; }} .segmented button.active {{ color:#fff; background:var(--deep); }}
    textarea {{ width:100%; height:480px; resize:vertical; padding:16px; border:1px solid var(--line); border-radius:3px; color:#d9edeb; background:#13262a; font:12px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace; tab-size:2; }}
    textarea:focus {{ outline:2px solid #70cfc4; outline-offset:1px; }}
    .actions {{ display:flex; gap:8px; margin-top:13px; }}
    .button {{ min-height:40px; padding:0 14px; border:1px solid var(--ink); border-radius:4px; color:#fff; background:var(--ink); cursor:pointer; font-weight:800; }} .button.secondary {{ color:var(--ink); background:#fff; }}
    .button:disabled {{ opacity:.45; cursor:not-allowed; }}
    .status {{ display:grid; grid-template-columns:1fr auto; gap:20px; align-items:start; padding-bottom:19px; border-bottom:1px solid var(--line); }}
    .status-label {{ color:var(--muted); font-size:10px; font-weight:800; }} .status h2 {{ margin:4px 0 0; font-size:25px; }}
    .count {{ text-align:right; }} .count strong {{ display:block; color:var(--red); font-size:39px; line-height:1; }} .count span {{ color:var(--muted); font-size:10px; }}
    .summary {{ display:grid; grid-template-columns:repeat(3,1fr); margin:18px 0; border:1px solid var(--line); }}
    .summary div {{ padding:11px; border-right:1px solid var(--line); }} .summary div:last-child {{ border-right:0; }} .summary strong {{ display:block; font-size:17px; }} .summary span {{ color:var(--muted); font-size:9px; }}
    .finding-list {{ max-height:395px; overflow:auto; border-top:1px solid var(--line); }}
    .finding {{ display:grid; grid-template-columns:68px 1fr; gap:12px; padding:13px 0; border-bottom:1px solid var(--line); }}
    .finding b {{ color:var(--red); font:800 9px ui-monospace,monospace; overflow-wrap:anywhere; text-transform:uppercase; }} .finding strong {{ display:block; font-size:12px; }} .finding p {{ margin:3px 0 0; color:var(--muted); font-size:11px; }}
    .empty {{ padding:24px 0; color:var(--teal); font-weight:750; }}
    .error {{ margin-top:15px; padding:12px; border-left:3px solid var(--red); color:#8b2b21; background:#fff4f2; }}
    .boundary {{ margin:16px 0 0; padding-top:13px; border-top:1px solid var(--line); color:var(--muted); font-size:10px; }}
    .spec {{ display:grid; grid-template-columns:.82fr 1.18fr; gap:60px; margin-top:34px; padding:30px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
    .spec h2 {{ margin:0; font-size:25px; }} .spec p {{ color:var(--muted); }}
    .gates {{ display:grid; grid-template-columns:1fr 1fr; border-top:1px solid var(--line); border-left:1px solid var(--line); }}
    .gate {{ min-height:86px; padding:13px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }} .gate b {{ color:var(--teal); font:800 10px ui-monospace,monospace; }} .gate strong {{ display:block; margin-top:6px; font-size:12px; }}
    footer {{ padding:25px 0 36px; color:var(--muted); font-size:11px; }} .foot {{ display:flex; justify-content:space-between; gap:20px; flex-wrap:wrap; }}
    @media (max-width:900px) {{ .hero-grid,.workbench,.spec {{ grid-template-columns:1fr; }} .hero-grid {{ gap:24px; }} .privacy {{ padding-top:0; }} .editor {{ border-right:0; border-bottom:1px solid var(--line); }} }}
    @media (max-width:620px) {{ .shell {{ width:calc(100% - 24px); }} .nav-actions a:not(.repo) {{ display:none; }} .hero-grid {{ padding:34px 0; }} h1 {{ font-size:34px; }} .metric-grid {{ grid-template-columns:1fr 1fr; }} .metric:nth-child(2) {{ border-right:0; }} .metric:nth-child(-n+2) {{ border-bottom:1px solid rgba(255,255,255,.14); }} main {{ padding-top:20px; }} .editor,.results {{ padding:18px 14px; }} .panel-head {{ flex-direction:column; }} textarea {{ height:430px; }} .actions {{ flex-direction:column; }} .summary {{ grid-template-columns:1fr 1fr 1fr; }} .gates {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header><nav class="shell"><a class="brand" href="index.html"><span class="mark" aria-hidden="true"></span>OpenMarketEval</a><div class="nav-actions"><a href="index.html">Arena</a><a href="https://github.com/Alfonsobang/open-market-eval/blob/main/schemas/research-packet.schema.json">Schema</a><a class="repo" href="https://github.com/Alfonsobang/open-market-eval">GitHub</a></div></nav></header>
  <section class="hero"><div class="shell hero-grid"><div><p class="eyebrow">A-SHARE RESEARCH QUALITY GATE / FINANCIAL SEARCH</p><h1>Audit the evidence before trusting the answer.</h1><p class="lead">A deterministic preflight for point-in-time financial-search packets: cutoff discipline, claim citations, source freezing, primary evidence, and deduplication.</p></div><div class="privacy"><strong>Local-first by design</strong>Your JSON stays in this browser. No strategy, account, market data, or research packet is uploaded.</div></div></section>
  <section class="metrics"><div class="shell metric-grid"><div class="metric"><strong>6</strong><span>DETERMINISTIC GATES</span></div><div class="metric"><strong>0</strong><span>NETWORK CALLS</span></div><div class="metric"><strong>JSON + MD</strong><span>REVIEW ARTIFACTS</span></div><div class="metric"><strong>CN A</strong><span>MARKET CONTRACT</span></div></div></section>
  <main class="shell">
    <section class="workbench" aria-label="Research evidence workbench">
      <div class="editor"><div class="panel-head"><div><h2>Research packet</h2><p>Paste a sanitized packet or load a synthetic fixture.</p></div><div class="segmented" aria-label="Example packet"><button id="safe-example">Safe fixture</button><button id="risky-example" class="active">Risky fixture</button></div></div><textarea id="packet-input" spellcheck="false" aria-label="Research packet JSON"></textarea><div class="actions"><button class="button" id="audit-button">Run evidence audit</button><button class="button secondary" id="format-button">Format JSON</button></div></div>
      <div class="results"><div class="status"><div><span class="status-label">AUDIT STATUS</span><h2 id="audit-status">REVIEW REQUIRED</h2></div><div class="count"><strong id="finding-count">0</strong><span>FINDINGS</span></div></div><div class="summary"><div><strong id="evidence-count">0</strong><span>EVIDENCE</span></div><div><strong id="claim-count">0</strong><span>CLAIMS</span></div><div><strong id="primary-count">0</strong><span>PRIMARY</span></div></div><div id="error-box" class="error" hidden></div><div id="finding-list" class="finding-list"></div><div class="actions"><button class="button secondary" id="download-json" disabled>Download JSON report</button><button class="button secondary" id="download-md" disabled>Download Markdown</button></div><p class="boundary">Static evidence-integrity audit only. A pass does not verify claim truth, source relevance, model quality, or investment merit.</p></div>
    </section>
    <section class="spec"><div><p class="eyebrow">PACKET CONTRACT 0.1</p><h2>What the gate can prove</h2><p>It detects structural evidence failures that should be resolved before a human or Agent conclusion enters review. Every check is deterministic and produces a repair instruction.</p></div><div class="gates"><div class="gate"><b>01</b><strong>As-of cutoff</strong></div><div class="gate"><b>02</b><strong>Timestamp consistency</strong></div><div class="gate"><b>03</b><strong>Duplicate evidence</strong></div><div class="gate"><b>04</b><strong>SHA-256 source seal</strong></div><div class="gate"><b>05</b><strong>Primary-source presence</strong></div><div class="gate"><b>06</b><strong>Claim-to-evidence links</strong></div></div></section>
  </main>
  <footer><div class="shell foot"><span>OpenMarketEval / A-Share Research Evidence Audit</span><span>No private company data, real user data, or proprietary workflows.</span><span>Not investment advice.</span></div></footer>
  <script>
    const examples = {{ safe: {safe_json}, risky: {risky_json} }};
    const input = document.getElementById('packet-input');
    const list = document.getElementById('finding-list');
    const errorBox = document.getElementById('error-box');
    let lastReport = null;
    const finding = (code, severity, evidence, repair) => ({{code, severity, evidence, repair}});
    const canonical = value => {{ const url = new URL(value); if (!['http:','https:'].includes(url.protocol)) throw new Error('Evidence URLs must use HTTP(S).'); return `${{url.protocol}}//${{url.host.toLowerCase()}}${{url.pathname.replace(/\/$/, '')}}${{url.search}}`; }};
    function audit(packet) {{
      if (packet.schema_version !== '0.1' || packet.market !== 'cn_a_cash') throw new Error('schema_version must be 0.1 and market must be cn_a_cash.');
      if (!packet.packet_id || !packet.query || !packet.as_of) throw new Error('packet_id, query, and as_of are required.');
      if (!Array.isArray(packet.evidence) || !packet.evidence.length || !Array.isArray(packet.claims) || !packet.claims.length) throw new Error('evidence and claims must be non-empty arrays.');
      const cutoff = Date.parse(packet.as_of); if (!Number.isFinite(cutoff) || !/(Z|[+-]\d\d:\d\d)$/.test(packet.as_of)) throw new Error('as_of must be ISO 8601 with a UTC offset.');
      const findings = [], ids = new Set(), urls = new Map(); let primary = 0;
      packet.evidence.forEach((item, index) => {{
        if (!item.id || ids.has(item.id)) throw new Error(`Evidence IDs must be present and unique (index ${{index}}).`); if (!item.title || !item.publisher) throw new Error(`Evidence ${{item.id}} requires title and publisher.`); ids.add(item.id);
        const published = Date.parse(item.published_at), retrieved = Date.parse(item.retrieved_at); if (!Number.isFinite(published) || !Number.isFinite(retrieved) || !/(Z|[+-]\d\d:\d\d)$/.test(item.published_at) || !/(Z|[+-]\d\d:\d\d)$/.test(item.retrieved_at)) throw new Error(`Evidence ${{item.id}} has an invalid or timezone-naive timestamp.`);
        if (published > cutoff || retrieved > cutoff) findings.push(finding('cutoff_violation','critical',`Evidence ${{item.id}} was published or retrieved after the declared as-of time.`,'Exclude the item or move the cutoff forward and rerun the packet.'));
        if (retrieved < published) findings.push(finding('timestamp_inconsistency','high',`Evidence ${{item.id}} was retrieved before publication.`,'Correct the timestamps or remove the item.'));
        const url = canonical(item.url); if (urls.has(url)) findings.push(finding('duplicate_evidence','medium',`Evidence ${{item.id}} duplicates ${{urls.get(url)}}.`,'Deduplicate retrieval results before measuring coverage.')); else urls.set(url,item.id);
        if (!/^[0-9a-f]{{64}}$/.test(item.content_sha256 || '')) findings.push(finding('unsealed_evidence','high',`Evidence ${{item.id}} has no valid SHA-256 digest.`,'Hash the frozen evidence payload and store its digest.'));
        if (typeof item.is_primary !== 'boolean') throw new Error(`Evidence ${{item.id}} requires a boolean is_primary value.`); if (item.is_primary === true) primary += 1;
      }});
      if (!primary) findings.push(finding('primary_source_missing','high','The packet contains no primary source.','Add the relevant filing, exchange notice, regulator release, or issuer disclosure.'));
      const claimIds = new Set(); packet.claims.forEach((claim,index) => {{ if (!claim.id || !claim.text || claimIds.has(claim.id)) throw new Error(`Claim ${{index}} requires a unique id and non-empty text.`); claimIds.add(claim.id); if (!Array.isArray(claim.evidence_ids) || claim.evidence_ids.some(id=>typeof id!=='string')) throw new Error(`Claim ${{claim.id}} evidence_ids must be an array of strings.`); const cited=claim.evidence_ids, unknown=cited.filter(id=>!ids.has(id)); if (!cited.length || unknown.length) findings.push(finding('unsupported_claim','critical',`Claim ${{claim.id}} has no valid evidence link.`,'Attach at least one evidence ID that exists in this packet.')); }});
      const order = {{critical:0,high:1,medium:2,low:3}}; findings.sort((a,b) => order[a.severity]-order[b.severity] || a.code.localeCompare(b.code));
      return {{packet_id:packet.packet_id,market:'cn_a_cash',as_of:packet.as_of,passed:!findings.length,finding_count:findings.length,critical_count:findings.filter(x=>x.severity==='critical').length,evidence_count:packet.evidence.length,claim_count:packet.claims.length,primary_source_count:primary,checks_run:6,findings,claim_boundary:'Static evidence-integrity audit only; it does not verify claim truth or recommend securities.'}};
    }}
    function markdown(report) {{
      const tick=String.fromCharCode(96);
      const rows=report.findings.map(x=>`| ${{x.severity}} | ${{tick}}${{x.code}}${{tick}} | ${{x.evidence}} | ${{x.repair}} |`).join(String.fromCharCode(10));
      const detail=report.findings.length ? `| Severity | Code | Evidence | Repair |
| --- | --- | --- | --- |
${{rows}}` : 'No configured integrity defects were detected. Independent review is still required.';
      return `# A-Share Research Evidence Audit

**${{report.packet_id}}** - **${{report.passed?'PASS':'REVIEW REQUIRED'}}**

- Checks run: **6**
- Evidence items: **${{report.evidence_count}}**
- Claims: **${{report.claim_count}}**
- Findings: **${{report.finding_count}}**
- Critical: **${{report.critical_count}}**

> Static evidence-integrity audit only. This does not verify claim truth or recommend securities.

${{detail}}
`;
    }}
    function render() {{ errorBox.hidden=true; try {{ lastReport=audit(JSON.parse(input.value)); document.getElementById('audit-status').textContent=lastReport.passed?'STATIC CHECKS PASS':'REVIEW REQUIRED'; document.getElementById('finding-count').textContent=lastReport.finding_count; document.getElementById('evidence-count').textContent=lastReport.evidence_count; document.getElementById('claim-count').textContent=lastReport.claim_count; document.getElementById('primary-count').textContent=lastReport.primary_source_count; list.replaceChildren(); if (!lastReport.findings.length) {{ const node=document.createElement('div'); node.className='empty'; node.textContent='No configured integrity defects detected. Independent review is still required.'; list.append(node); }} else lastReport.findings.forEach(item=>{{ const row=document.createElement('div'); row.className='finding'; const sev=document.createElement('b'); sev.textContent=item.severity; const body=document.createElement('div'); const title=document.createElement('strong'); title.textContent=item.code; const copy=document.createElement('p'); copy.textContent=item.evidence+' Repair: '+item.repair; body.append(title,copy); row.append(sev,body); list.append(row); }}); document.getElementById('download-json').disabled=false; document.getElementById('download-md').disabled=false; }} catch(error) {{ lastReport=null; errorBox.textContent=error.message; errorBox.hidden=false; document.getElementById('audit-status').textContent='INVALID PACKET'; document.getElementById('download-json').disabled=true; document.getElementById('download-md').disabled=true; }} }}
    function loadExample(name) {{ input.value=JSON.stringify(examples[name],null,2); document.querySelectorAll('.segmented button').forEach(node=>node.classList.toggle('active',node.id.startsWith(name))); render(); }}
    function download(name,content,type) {{ const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([content],{{type}})); link.download=name; link.click(); setTimeout(()=>URL.revokeObjectURL(link.href),0); }}
    document.getElementById('safe-example').addEventListener('click',()=>loadExample('safe')); document.getElementById('risky-example').addEventListener('click',()=>loadExample('risky')); document.getElementById('audit-button').addEventListener('click',render); document.getElementById('format-button').addEventListener('click',()=>{{ try {{ input.value=JSON.stringify(JSON.parse(input.value),null,2); errorBox.hidden=true; }} catch(error) {{ errorBox.textContent=error.message; errorBox.hidden=false; }} }}); document.getElementById('download-json').addEventListener('click',()=>download('research-evidence-audit.json',JSON.stringify(lastReport,null,2)+String.fromCharCode(10),'application/json')); document.getElementById('download-md').addEventListener('click',()=>download('research-evidence-audit.md',markdown(lastReport),'text/markdown'));
    loadExample('risky');
  </script>
</body>
</html>
"""
