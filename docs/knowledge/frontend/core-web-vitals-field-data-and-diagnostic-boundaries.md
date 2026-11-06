---
id: "kb-frontend-web-vitals"
title: "Core Web Vitals：怎样把页面体验变成可解释的证据"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "分开解释 LCP、INP、CLS 的观察范围与算例，区分单次体验、真实用户分布、实验室结果和业务完成。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-frontend-rendering-hydration", "kb-frontend-long-tasks"]
related: ["kb-frontend-reconciliation-identity", "kb-frontend-bundling-splitting", "kb-performance-benchmarking", "kb-reliability-slos"]
tags: ["web-vitals", "lcp", "inp", "cls", "measurement"]
---

# Core Web Vitals：怎样把页面体验变成可解释的证据

学习入口：接口平均 100 ms、电脑上跑分很高，用户为什么仍说页面慢、按钮卡、内容乱跳？需要分别观察主要内容呈现、输入后的下一次画面，以及布局稳定性，再用用户与设备分布判断问题范围。

前置：[渲染与 Hydration](rendering-and-hydration.md)、[长任务与响应性](long-tasks-and-responsiveness.md)。本文按 2026-10-26 核查的 web.dev 指标定义解释常规文档访问，不把所有 [SPA](../../glossary/frontend.md#frontend.spa) 软导航、内嵌页面或浏览器实现当作同一测量范围。全部数字为纸面教学数据，没有对本站或业务站点采集 [Core Web Vitals](../../glossary/frontend.md#frontend.web-vitals)、运行 Lighthouse 或上报真实用户数据。

## 三个指标对应三类体验

截至本次核查，Core Web Vitals 包括以下三个指标。推荐用移动与桌面分别统计的第 75 百分位判断，三项都满足相应目标才表示该组体验达到推荐水平，见 [Web Vitals 定义与阈值](https://web.dev/articles/vitals)。

| 指标 | 观察什么 | 推荐“良好”阈值 | 不能代替什么 |
| --- | --- | --- | --- |
| LCP，[Largest Contentful Paint](https://web.dev/articles/lcp) | 视口内符合条件的最大内容元素的呈现时刻 | ≤ 2.5 秒 | 所有资源完成、交互接管完成或业务正确 |
| INP，[Interaction to Next Paint](https://web.dev/articles/inp) | 点击、触控、键盘交互到下一次可呈现画面的响应 | ≤ 200 ms | 后台请求完成、交易成功或所有交互的平均耗时 |
| CLS，[Cumulative Layout Shift](https://web.dev/articles/cls) | 符合计入条件的布局偏移中，最严重会话窗口的累计分数 | ≤ 0.1，无量纲 | 页面所有移动总距离，或对可访问性的完整评价 |

不要把三者相加成“总页面[延迟](../../glossary/performance.md#performance.latency-throughput)”，也不要把测试机上一次满足阈值当作所有用户都达标。定义和门槛可能演进，后续更新应保留核查时间。

## LCP 需要追到具体元素与时间段

LCP 候选会随内容呈现变化，图片或文本块是否符合规则、视口和用户输入等都会影响记录。它不是固定绑定某个 CSS 选择器，也不是只数 HTML 下载，见 [LCP 指标说明](https://web.dev/articles/lcp)。

纸面假设：最终 LCP 候选是一张图片，从本次导航开始计时。首字节到达 300 ms，图片请求再等 200 ms 才开始，下载用 600 ms，下载后再等 400 ms 才呈现；各段连续且无重叠：

```text
LCP = 首字节时间 + 资源加载延迟 + 资源加载时长 + 元素呈现延迟
    = 300 + 200 + 600 + 400 = 1500 ms
```

四段分解依据 [LCP 优化说明](https://web.dev/articles/optimize-lcp)。若图片提早下载结束，但脚本仍到 1500 ms 才允许展示，整体 LCP 未必前移。应查看请求何时被发现、[资源竞争](../../glossary/performance.md#performance.contention)和呈现依赖，而非只更换图片格式或只压缩文件。

这个 1500 ms 只是给定访问的候选结果，不代表用户分布的 p75，也不证明按钮已能处理输入。

## INP 包括处理器开始前和结束后的等待

一次交互可能关联多个事件，响应时长需要从输入发生到下一次可呈现画面观察。假设该交互中决定响应时长的事件，输入等待为 35 ms、处理为 90 ms、处理结束后的呈现等待为 25 ms：

```text
该交互的响应时长 = 35 + 90 + 25 = 150 ms
```

90 ms 的处理器不是完整交互时长；35 ms 可能来自此前工作占用主[线程](../../glossary/systems.md#systems.execution-units)，25 ms 可能包含后续渲染相关等待。具体阶段与交互分组见 [INP 定义](https://web.dev/articles/inp)。页面 INP 从访问期间的相关交互选择代表性的高延迟值；大量交互时按规则排除部分极端项，不能取平均，也不能从上面一次 150 ms 直接宣布整页 INP 为 150 ms。

[异步](../../glossary/runtime.md#runtime.async)请求耗时 2 秒但立即显示合理的等待反馈，下一次画面可以较快出现；这不证明 2 秒的业务等待已解决。相反，接口很快而主线程长期忙碌，输入仍可能等待。应把交互响应与业务完成各自定义，见[长任务](long-tasks-and-responsiveness.md)。

## CLS 按偏移窗口计分

单次布局偏移分数由影响区域比例与移动距离比例相乘得到；会话窗口聚合相邻间隔小于 1 秒、总跨度最多 5 秒的一组偏移，取其中累计分数最大的窗口。与符合规则的近期离散输入相关的偏移可被排除；滚动不是一概排除的理由，见 [CLS 定义](https://web.dev/articles/cls)。

教学假设下面都是需计入的偏移，没有近期输入排除：

| 时刻 | 影响比例 × 距离比例 | 分数 | 窗口 |
| --- | --- | --- | --- |
| 1.0 s | 0.4 × 0.1 | 0.04 | A |
| 1.6 s | 0.3 × 0.2 | 0.06 | A，与上次间隔 0.6 s |
| 4.0 s | 0.4 × 0.2 | 0.08 | B，与上次间隔 2.4 s |

A 累计 0.10，B 累计 0.08，本文完整教学访问的 CLS 为 `max(0.10, 0.08)=0.10`，不是 0.18。这里直接给定了正确的几何比例，没有把移动元素的面积简单当作影响区域，也没有实际读取布局条目。

预留图片与异步区域尺寸可以减少某些偏移；动画是否产生可计量偏移仍要按属性与浏览器规则判断。布局稳定也不自动证明页面内容完整或业务操作安全。

## 单次访问、分布与排查证据分别组织

真实用户测量（field / RUM）反映实际设备、网络、缓存、页面状态与交互，受样本、采集支持和缺失影响。实验室测量可控制条件并重现路径，但一次仅加载页面的测试并未覆盖之后所有交互或布局偏移。两类证据互补，不能把 Lighthouse 某个代理指标直接标成真实 INP。

例如一组相同口径的 100 次访问，按数值排序并明确采用 nearest-rank 教学算法时，p75 是第 `ceil(100×0.75)=75` 个值，而非平均值。若它是 180 ms，可支持这组 INP 样本的 p75 判断；还要独立看 LCP 与 CLS，说明时间窗口、设备分组、路由模板、版本及有无有效交互样本。无交互或无可用测量不能被擅自补成 0 ms。

诊断时应把慢速或不稳定的访问连接到元素、交互目标和工作阶段。发布后比较相近用户条件，并控制业务流量、采样与版本变化；一次数值变好还不足以证明某项改动是唯一原因，见[基准与工作负载](../performance/benchmarks-workloads-and-speedup.md)。

## 自检

1. LCP、INP、CLS 分别观察什么？为什么不能用 API 平均耗时代替？
2. 图片算例的 1500 ms 如何得到？下载提前结束为何可能不改变它？
3. 35/90/25 ms 算例代表什么？能否直接当作整页 INP？
4. 三次偏移为何得到 0.10，而不是 0.18？哪些前提会改变结果？
5. 单机跑分很好为何仍需真实用户分布？没有交互样本能否记作 0 ms？

## 来源与核查

2026-10-26 核查 web.dev 的 Web Vitals、LCP、LCP 优化、INP、CLS 官方说明。本文为 source-checked 概念文章；百分位算法和时长/几何数据明确为教学输入，不是浏览器实测，也不代表本站已获得或达到上述指标。测量实现、库版本与真实分布后续独立验证。
