# A-Share Agent Arena 首关发布文案

## 即刻

我把项目从“A 股 Agent 评测规格”推倒重做了。

原因很直接：没人会因为一份完整的栏目清单而使用一个项目。用户真正想知道的是，我的 Agent 能不能在同一组任务里被证明。

现在首关只有一个问题：

**你的 Agent 能抓出 A 股回测里偷看的未来吗？**

公开开发集包含 10 个场景、8 类缺陷和两个干净控制组，评分 precision、recall、F1 和逐案命中。它会同时惩罚漏检和为了显得专业而乱报问题。

```bash
python -m open_market_eval audit-demo
```

示例成绩不是模型成绩，而且故意不是满分。第一份带完整原始输出和复现命令的外部 Agent 成绩，才会成为榜单第一条记录。

项目：<https://github.com/Alfonsobang/open-market-eval>

## 雪球

一条漂亮的 A 股回测曲线，至少可能藏着八种问题：

- 收盘后生成信号，却按同一收盘价成交
- 用今天的股票池回放历史
- 用复权价模拟真实成交
- 忽略 T+1
- 停牌、涨跌停仍假设全部成交
- 高频换手却不计成本
- 更正后的财务数据被提前写回历史
- 已退市股票从样本中消失

我把这些问题做成了一个可运行的 Agent 取证挑战。不是让 AI 预测涨跌，而是让它先证明自己不会被一条作弊回测骗过。

当前 10 个案例全部是公开开发集，不宣传任何收益，也不把手工示例冒充模型成绩。欢迎提交你认为最隐蔽的一类回测错误，后续会转成可程序化评分的任务。

在线实验场：<https://alfonsobang.github.io/open-market-eval/>

## 知乎 / 公众号标题与开头

标题：**别再问 AI 明天买什么：先让它审一份 A 股回测**

开头：

金融 Agent 最容易制造的错觉，不是答案明显错误，而是它能用专业语言解释一条从一开始就不成立的回测曲线。

如果股票池使用了今天的成分、财务字段来自后来修订、收盘后信号按同一收盘价成交，再复杂的模型也只是在解释未来信息。

因此我把 OpenMarketEval 的第一场公开挑战收缩为一个动作：让 Agent 对 10 个 A 股回测场景做取证，并用精确率、召回率、F1 和逐案命中评分。

后续正文结构：

1. 为什么“预测涨跌”不是好的首个 Agent benchmark。
2. 八类 A 股回测缺陷如何进入任务合同。
3. 为什么要加入两个干净控制组惩罚误报。
4. 同一个 Agent 的漏检如何变成修复任务。
5. 如何提交第一份可复现外部成绩。

## X / English

OpenMarketEval is now an A-Share Agent Arena.

Challenge 0 asks one concrete question: can your agent detect when a China A-share backtest quietly uses the future?

The public dev pack has 10 cases, 8 defect classes, clean negative controls, deterministic scoring, and a Harbor-style task. It scores precision, recall, F1, and exact case accuracy.

No stock tips. No return claims. No hidden model result disguised as a benchmark.

Run it:

`python -m open_market_eval audit-demo`

<https://github.com/Alfonsobang/open-market-eval>
