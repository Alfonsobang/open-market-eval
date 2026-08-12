# A 股时点查数评测集 v0.1

这是一个小而严格的公开开发集，专门检验金融 Agent 能否在正确版本的定期报告中找到目标数字，保留原始单位，正确换算为人民币元，并定位到准确页面。

[English](README.md)

[打开浏览器实验室](https://alfonsobang.github.io/open-market-eval/filing-qa.html)，无需安装即可尝试全部 10 道任务。

## 包含内容

- 5 家深市上市公司、共 10 个公开任务。
- 每份 2024 年年度报告包含两个字段：营业收入和研发投入金额。
- 5 个巨潮资讯官方 PDF 链接，并记录发布日期、文件字节数和 SHA-256。
- 公开标签覆盖原始数值、披露单位、归一化人民币元数值、期间、口径、PDF 页码和来源 ID。
- 确定性评分器，同时输出逐字段准确率和整题完全匹配率。

这是公开开发集，不是隐藏榜单。它评测查数与证据链协议，不评测投资能力。

## 运行方式

按照 [`submission-template.jsonl`](submission-template.jsonl) 为每道任务填写一行 JSON，然后执行：

```bash
python -m open_market_eval score-fact-qa \
  --submission path/to/fact-answers.jsonl \
  --output runs/fact-qa-scorecard.json
```

单行格式如下：

```json
{
  "task_id": "pit-300750-revenue-2024",
  "value": "362012554",
  "unit": "CNY_THOUSAND",
  "normalized_value_yuan": "362012554000",
  "period": "2024",
  "scope": "listed_company_consolidated",
  "pdf_page": 9,
  "source_id": "cninfo-300750-2024-annual"
}
```

数值使用字符串，避免大型财务数字经过 JSON 数值解析后损失精度。`pdf_page` 指 PDF 文件从 1 开始计数的物理页，不是报告正文中印刷的页码。

## 质量控制

- **版本控制：** 每道任务绑定唯一年报文件，并使用公告日期当天结束时作为信息截止点。
- **文件封存：** 来源清单记录 2026-08-13 获取文件时的 SHA-256 和字节数。
- **单位检查：** `CNY_THOUSAND` 与 `CNY_YUAN` 单独评分，不能只答一个看似正确的大数。
- **来源定位：** 必须返回准确的 PDF 物理页码和来源 ID。
- **数据权利：** 仓库不提交、不再分发年报 PDF，只保存链接、元数据和事实标签。

如果官方文件发生变化，不应静默覆盖哈希或答案；应发布新的评测版本并说明差异。

## 已知边界

- 当前只覆盖 5 家公司、1 个报告期和 2 个字段。
- 截止信息精确到公告日期，不用于日内时点判断。
- 标签公开，因此适合开发与回归测试，不支持对隐藏集泛化能力的宣传。
- 查数正确不代表公司、证券、预测或投资逻辑已经得到验证。

本评测集不构成任何投资建议。
