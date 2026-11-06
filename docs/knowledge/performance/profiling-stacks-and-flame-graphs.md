---
id: "kb-performance-profiling"
title: "Profiling 与火焰图：最宽的函数，为什么未必是延迟根因"
kind: "concept"
domain: "performance"
status: "evolving"
summary: "解释采样、插桩与调用栈聚合，区分包容/自身成本、执行与等待、火焰图与时间线及证据局限。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-performance-cpu-metrics"]
related: ["kb-systems-cpu-caches", "kb-performance-benchmarking", "kb-performance-slow-api", "kb-runtime-async-blocking", "kb-reliability-telemetry"]
tags: ["profiling", "flame-graph", "on-cpu", "off-cpu", "sampling"]
---

# Profiling 与火焰图：最宽的函数，为什么未必是延迟根因

学习入口：[火焰图](../../glossary/performance.md#performance.profiling)里某个函数占了七成宽度，能否断言它消耗七成请求时间，或调用了最多次？前置：[线程与执行](../systems/process-thread-coroutine.md)、[CPU 时间与经过时间](cpu-time-utilization-load-and-quotas.md)。本文解释剖析数据的读法，参照 perf 与火焰图作者资料；[调用栈](../../glossary/systems.md#systems.memory-layout)和样本数为自设例子，没有采集真实程序。

## 先选择需要观察的量

Profiling（性能剖析）把所选资源成本归到代码或执行上下文。按时钟或事件取样，能观察部分瞬间的调用栈；在函数、分配或事件边界插桩，则记录相应进入、退出或事件。两者的覆盖、精度与开销不同，不能只因输出都有函数名就当作同一种测量。

[CPU 时间](../../glossary/performance.md#performance.cpu-metrics)采样、硬件周期、分配字节、锁等待时长都可以按栈聚合，图的宽度究竟代表什么必须由事件和权重说明。Linux [perf 教程](https://perfwiki.github.io/main/tutorial/)区分计数、采样与事件选择；某个默认事件或频率也不是所有平台的统一口径。

确认采集范围是[进程](../../glossary/systems.md#systems.execution-units)、指定线程、CPU 还是整个系统，是否包含内核及后台工作，以及窗口是否覆盖当前问题。只看全部进程总图，可能被后台任务淹没；只采单线程，又可能漏掉真正执行工作的线程池。

## 火焰图表示栈的聚合，不是执行时间线

经典 Flame Graph 把相同调用路径聚合，底部向上表示调用深度；横向宽度表示该路径所占权重，横向位置通常为聚合排序，不是先后时刻。颜色常用于区分相邻帧，并非默认“越红越慢”。定义见 [Brendan Gregg 的火焰图说明](https://www.brendangregg.com/flamegraphs.html)。

图很高只表示栈很深，图很宽才表示相应口径的累计权重大。浏览器等工具中的 Flame Chart 则可把时间放在横轴，矩形宽度通常对应所显示的时间区间；仍需核对它来自事件追踪还是采样重建，颜色也以工具图例为准。外观相似不表示读法相同。聚合图不能直接重建某次请求先执行谁、等待了多久，也不能展示全部[并发](../../glossary/systems.md#systems.concurrency)因果。

## 用三个调用路径理解宽度和自身成本

纸面设定：在同一采集范围中，取得 1000 个有效、等权的 on-CPU 时间样本，且全部样本恰好属于以下三个路径。分号表示从调用者到当前叶帧，不是调用次数记录：

```text
request;parse       200
request;encode      500
background;compact  300
```

| 帧或路径 | 样本解释 |
| --- | --- |
| request | 包含 parse 与 encode 的 700 个样本，占总量 70% |
| parse 叶帧 | 200 个，占 20% |
| encode 叶帧 | 500 个，占 50% |
| background/compact | 300 个，占 30% |

request 的包容成本（inclusive）包含后代，不能再把 70% 与 parse、encode 的比例相加。此例没有停在 request 自身的样本，因此它的自身成本（self）为 0；这只说明所构造的样本，不证明该函数现实中绝无自身工作。

500 个 encode 样本不是 500 次调用，也不是单次调用耗时 500ms。只有在时间采样具有代表性、权重与范围相符等条件下，比例才可帮助估计所选 CPU 时间的分布；它不自动成为所有请求经过时间的分布。CPU 图的采集与解释见 [CPU Flame Graphs](https://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html)。

## CPU 图看不到全部等待

线程等待网络、锁、任务或调度时，可能不在 CPU 上。只采 on-CPU 栈，不能把没有显示的时间归为不存在；若线程忙于自旋，等待又可能表现为 on-CPU [热点](../../glossary/performance.md#performance.contention)。应先判断等待方式，再选择 CPU、调度或[阻塞](../../glossary/systems.md#systems.blocking)证据。

Off-CPU 分析把线程离开 CPU 到再次运行等区间与栈联系起来，可补充部分等待位置；具体采集定义、状态过滤和窗口边界需核对。[Off-CPU Flame Graphs](https://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html)也指出，等待工作的空闲线程可能占据很大比例，栈未必直接告诉你是谁迟迟没有唤醒它。

多个线程的等待区间会重叠，累计等待总量可超过观察窗口。十个线程各等待 1 秒，不表示单个请求[延迟](../../glossary/performance.md#performance.latency-throughput)了 10 秒；一个函数在 off-CPU 图中很宽，也不表示它[运行时](../../glossary/runtime.md#runtime.virtual-machine)消耗很多 CPU。跨线程或远端的关键路径需要结合[请求链路证据](../reliability/logs-metrics-and-traces.md)。

## 采样和解析也有边界

短窗口、很少样本或周期性取样可能遗漏短函数和特定阶段。采样位置还可能偏离触发事件的位置；优化后的内联、栈展开方式、[JIT](../../glossary/runtime.md#runtime.compilation) 符号及丢失事件会影响归因。未知地址、断栈和被过滤的帧不能当作“没有成本”，也不应仅靠一个叶帧名字认定具体源代码行就是原因。

硬件计数器不足时，perf 可分时复用并按运行时间缩放事件；这是估计，工作负载阶段变化会影响代表性，具体见 perf 教程。不同处理器上的同名事件也需核对语义，不能任意比较缓存事件或把周期直接换算成固定请求时长。

采样、插桩和符号处理本身有成本。增加频率或跟踪大量调度事件可能干扰被测对象；“采样”不等于零开销，“插桩”也不等于完整无损记录。应记录工具、事件、权重、版本、过滤、有效/丢失样本和必要的开销对照。

## 从热点形成可证伪的假设

看到宽帧后，先区分它是调用者的包容成本、重复做了太多次、单次工作昂贵，还是在等待其他资源。再提出小范围改动，并检查输出、负载和统计口径相同；热函数可能是必要工作，最宽函数也可能只是汇总入口。

比较前后图时同时保存绝对资源消耗和完成工作数。某路径占比从 20% 变成 40%，可能只是其他路径减少，不能直接推出它慢了一倍。对照方法继续见[基准测试与加速比](benchmarks-workloads-and-speedup.md)，阶段定位可接回[慢 API 排查](slow-api-investigation.md)。

自检：宽度单位是什么？范围和窗口覆盖了谁？父帧与子帧是否重复计量？需要的是 CPU 分布还是请求等待？占比变化是否有绝对值和业务结果支持？

2026-10-20 核查 perf 教程及 Brendan Gregg 的火焰图、CPU/Off-CPU 资料，状态为 source-checked。1000 个样本与三条栈为纸面设计；未运行 perf、采样/插桩、栈展开、调度追踪、火焰图生成或性能对照。
