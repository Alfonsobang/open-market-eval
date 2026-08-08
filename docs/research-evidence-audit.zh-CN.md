# A 股研究证据审计

金融搜索 Agent 很容易生成一段看似合理的结论，却没有保留足够的信息来回答一个关键问题：在研究截止时点，当时究竟能看到哪些证据？本门禁先审计证据包，再允许结论进入人工评审。

## 检查范围

| 门禁 | 发现的问题 | 工程价值 |
| --- | --- | --- |
| 截止时点 | 证据发布时间或抓取时间晚于 `as_of` | 防止历史研究或实时决策偷看未来 |
| 时间戳一致性 | 抓取时间早于发布时间 | 识别不可能成立或已损坏的来源链路 |
| 证据去重 | 多个证据 ID 指向同一个规范化 URL | 防止重复搜索结果虚增来源覆盖度 |
| 内容封存 | 缺少合规的 SHA-256 摘要 | 让后续内容变更可以被发现 |
| 一手来源 | 没有公告、交易所、监管或发行人来源 | 区分“搜到线索”和“获得权威支持” |
| 主张引用 | 结论没有引用证据包中的有效 ID | 让每条结论可以追溯到冻结证据 |

审计结果完全由确定性规则产生。它不会判断结论是否真实、来源是否相关，也不会判断某只证券是否值得投资。

## 本地运行

不需要第三方依赖、API Key、行情源或网络访问：

```bash
python -m open_market_eval audit-research-packet \
  --packet examples/research-packets/leaky-packet.json \
  --output runs/research-packet-audit.json
```

命令会同时生成 JSON 报告和 Markdown 评审稿。加入 `--strict` 后，只要存在问题就会返回非零退出码，适合放进 CI。

[浏览器工作台](https://alfonsobang.github.io/open-market-eval/research-audit.html)会在本地执行相同的六类检查，粘贴的内容不会上传。

## 证据包协议

Draft 2020-12 [`research-packet.schema.json`](../schemas/research-packet.schema.json) 定义了最小交换格式：

- 证据包 ID、A 股市场范围、研究问题和带时区的截止时点；
- 证据标题、发布方、URL、发布时间、抓取时间、内容摘要和一手来源标记；
- 每条研究主张及其明确引用的证据 ID。

仓库中的[保守样例](../examples/research-packets/conservative-packet.json)与[风险样例](../examples/research-packets/leaky-packet.json)都是软件测试夹具，使用保留的 `.invalid` 域名，不包含行情数据，也不表达任何投资判断。

通过本门禁只表示证据包没有触发已配置的静态缺陷，下一步仍需独立检查来源相关性和结论真实性。

v0.6 门禁目前处于公开 beta。可以通过[结构化表单](https://github.com/Alfonsobang/open-market-eval/issues/new?template=research-packet-feedback.yml)提交误报、漏报、schema 缺口或经过脱敏的研究包。
