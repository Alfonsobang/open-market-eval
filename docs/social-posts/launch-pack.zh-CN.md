# 首发社媒内容包

所有链接发布时统一指向：<https://alfonsobang.github.io/open-market-eval/>

## 即刻

我把 OpenMarketEval 彻底改成了一个 A 股研究 Agent 公共实验场。

它不回答“明天买什么”，而是先测五件更基础的事：

1. 能不能找到截止时间前的正式公告；
2. 能不能查对财务数字的期间、单位、口径和版本；
3. 能不能在结果前封存概率预测；
4. 能不能识别回测里的未来函数和不可成交假设；
5. 能不能把研究主张连接到证据、反证和失效条件。

页面里有一个可以直接使用的八项回测防泄漏自检。当前 A 股公开成绩是 0，因为第一批真实任务还没有跑完。我宁愿先公开缺口，也不想再做一个带漂亮收益图的 AI Demo。

现在征集的不是 Star，而是首批可验证任务和 Agent adapter。

## 雪球

### 标题

一条 A 股回测曲线，在讨论收益率之前至少要过这 8 关

### 正文

我最近把一个 AI 预测项目推倒重做，原因很简单：大多数用户真正缺的不是新的股票观点，而是判断研究过程是否可信的方法。

新的 A 股研究 Agent 实验场先检查八件事：统一信息截止时间、历史时点股票池、信号与成交价格分离、可交易原始价格、T+1/停牌/涨跌停、双边成本、财务数据首次可见版本、完整实验账本。

任何一项没有处理，高收益曲线都可能只是数据泄漏或不可成交假设。页面提供交互式自检，并把公告搜索、时点查数、事件预测、回测审计和研究备忘录定义成五种公开任务。

这里不提供个股推荐，也暂时没有模型排名。第一阶段目标是把 10 个真实任务和 verifier 做扎实。

## 知乎 / 公众号

### 标题

为什么多数“AI 炒股”项目无法证明自己不是在偷看答案？

### 开头

一个 AI 能写出完整的公司分析，甚至能画出漂亮的回测曲线，并不意味着它完成了可信的投资研究。真正困难的地方通常发生在模型回答之前：它看到的信息是否在当时已经公开？财务数字的期间和口径是否正确？历史股票池是否包含后来退市的公司？收盘后生成的信号是否错误地按同一收盘价成交？

OpenMarketEval 的新路线不再试图做一个“股市预言家”页面，而是把 A 股研究拆成五类可以验证的工作：公告搜索、时点查数、事件预测、回测审计和证据化研究备忘录。

### 文章结构

1. 流畅回答为什么不是研究能力。
2. A 股数据中最常见的四种时点错误。
3. 八项回测防泄漏清单。
4. 五类 Agent 任务如何评分。
5. 为什么第一版公开成绩是 0。
6. 如何贡献一个任务或复现实验。

### 结尾

这个项目不承诺模型能赚钱。它尝试建立更靠前的一层公共基础设施：在谈论投资结果之前，先证明 Agent 能够基于当时可见的公开信息，完成一个定义清楚、可以复核的研究任务。

## X / English

Most “AI investing” demos jump from fluent analysis to a backtest.

We rebuilt OpenMarketEval around the missing layer: verifiable A-share research work.

Five tracks:
- official filing search
- point-in-time financial QA
- sealed event forecasts
- backtest leakage audits
- evidence-linked research memos

The public leaderboard currently has zero A-share results. That is intentional: specifications and anti-leak controls come before model claims.

We are looking for reproducible tasks and agent adapters, not stock picks.

## GitHub Release 摘要

`v0.3.0` turns OpenMarketEval into a public A-Share Agent Lab. It ships a machine-readable five-track task catalog, an eight-source registry, CLI track discovery, a Chinese-first interactive workbench, and a backtest leakage self-check. No A-share model ranking or investment performance is claimed in this release.
