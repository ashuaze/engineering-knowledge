---
id: "kb-runtime-gc"
title: "可达性与垃圾回收：对象不用了，内存为什么还在增长"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "用对象引用图解释 JavaScript 内存持有、GC 与泄漏，区分 Node.js 堆、外部内存和 RSS 的诊断口径。"
created: "2026-10-19"
updated: "2026-10-23"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-runtime-event-loop", "kb-systems-execution-units", "kb-performance-latency-queues", "kb-runtime-closures", "kb-frontend-routing-cache", "kb-systems-virtual-memory", "kb-runtime-ffi-boundaries", "kb-runtime-virtual-machines"]
tags: ["memory", "reachability", "garbage-collection"]
---

# 可达性与垃圾回收：对象不用了，内存为什么还在增长

原生库保存裸指针或回调时，[GC](../../glossary/runtime.md#runtime.gc) [可达性](../../glossary/runtime.md#runtime.reachability)与外部资源生命周期需要额外契约，见[跨语言调用](ffi-abi-ownership-and-runtime-boundaries.md)；堆、帧与宿主能力的抽象边界见[语言虚拟机](virtual-machines-bytecode-hosts-and-isolation.md)。两篇为来源核查和教学推演，不扩大本文内存观测的实验范围。

学习入口：函数已经返回、页面也关闭了，为什么对象仍占内存？前置知识：变量、对象引用、函数与回调。本文解释 JavaScript [可达性](../../glossary/runtime.md#runtime.reachability)与 V8 的基础机制，内存观测字段限定 Node.js 24 文档；不覆盖其他语言的所有收集器，也不把一次堆快照当成完整的[进程](../../glossary/systems.md#systems.execution-units)内存诊断。

## 回收判断看引用路径

程序可以把对象看成节点，把持有关系看成有向边。垃圾收集器从仍需保留的根出发，寻找可以到达的对象；全局对象、活动执行状态等能成为起点。只要对象仍能通过这些路径被访问，就不能仅因业务上“不再使用”而认定可回收。

[JavaScript 内存管理说明](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management)区分了[引用计数](../../glossary/runtime.md#runtime.gc)与基于可达性的收集。两个对象互相引用，但从根已经无法到达，仍可被追踪式收集器回收；循环引用本身不是 JavaScript 泄漏的充分条件。反过来，一个没有循环、却被全局[数组](../../glossary/algorithms.md#algorithms.sequences)永久保存的对象，也可能一直活着。

引用计数记录一个对象被引用的数量，计数归零可触发回收；单纯依靠计数时，不可达的环仍可能相互维持非零计数。这解释了它与追踪式判断的差别，不能把“还有相互引用”直接当成 V8 的回收规则。

“赋值为 null”只删除一条变量持有的边。如果 Map、监听器或另一个[闭包](../../glossary/runtime.md#runtime.closure)仍持有对象，引用路径就没有全部断开。判断生命周期时，应问谁仍持有它、持有多久，以及在哪个业务事件后应该释放。

## 闭包、缓存和监听器怎样延长生命

闭包让函数能够访问其定义时的词法环境中的绑定，而不只看调用位置。回调被保存到更长寿的对象上时，它实际使用的绑定可能让相关对象继续存活；具体优化与保留粒度仍由引擎实现决定。

下面是对象持有关系的教学示意，没有运行内存测量，也不代表引擎必须保留闭包作用域中的全部变量。

```text
全局 Map → 某会话的缓存条目 → 大对象
仍存活的事件源 → 注册的回调 → 回调实际引用的会话对象
运行中的定时器 → 回调 → 待处理批次
```

函数返回不一定让回调引用的对象失去可达性；如果事件源仍保留回调，相关对象可能继续存活。解除监听需要对应的事件、回调和注册方式，重新创建一个“内容相同”的函数通常不能替代原来的函数引用。

设计资源时先配对生命周期：注册与注销、订阅与取消、缓存插入与淘汰、任务启动与结束清理。缓存“以后会过期”也需要具体机制：仅在读取时检查过期，可能长期保留再也不会被访问的条目；TTL 也不能独自限制单位时间内新增数据的峰值。应结合容量上限和清理策略，而不是只等待 GC。

外部连接、文件句柄或订阅还涉及及时释放的业务要求。弱引用与终结回调不能保证清理在某个时间发生，不能把关键资源关闭、付款或提交责任交给垃圾收集时机。关于弱引用和终结时机的限制，同样见 [MDN 的内存管理说明](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management#weakrefs_and_finalizationregistry)。

## GC 在降低回收成本，也消耗执行资源

V8 使用分代思想：许多对象很快死亡，年轻代更频繁处理短命对象，部分存活对象会进入老年代；不同空间与对象有各自的管理细节。[Node.js 的内存介绍](https://nodejs.org/learn/diagnostics/memory/understanding-and-tuning-memory)给出了这一入门模型，不应据此认为每次回收都扫描整个堆，或老年代永远不回收。

收集器可以结合[并行](../../glossary/systems.md#systems.concurrency)、增量和并发工作，仍可能有暂停阶段；不能把“有并发 GC”推导为没有暂停。V8 的 [Orinoco 机制介绍](https://v8.dev/blog/trash-talk)解释了这些工作方式。大量分配会增加回收压力，大量长期存活对象又会让回收后剩余量变大，两者需要分别观测。

请求变慢时，GC 是一个待验证的假设。[事件循环](../../glossary/runtime.md#runtime.event-loop)等待、分配速率、暂停记录与请求时间的关系需要证据，不能仅凭内存曲线上下波动就归因。扩大堆上限可能改变回收节奏，也可能只是延后耗尽；它不会删除仍然可达的泄漏对象。

## 堆、外部内存和 RSS 的口径不同

Node.js 的 `process.memoryUsage()` 给出多个字段。下表依据 [Node.js 24 API](https://nodejs.org/docs/latest-v24.x/api/process.html#processmemoryusage)，没有填入本仓库测量值。

| 字段 | 观察的范围 | 不能直接推导什么 |
| --- | --- | --- |
| heapUsed | V8 堆中正在使用的内存 | 一次升高不证明泄漏，可能尚未回收 |
| heapTotal | V8 已分配的堆容量 | 容量扩大不代表其中全是存活业务对象 |
| external | 与 V8 管理的 JS 对象绑定的 C++ 对象内存 | 不等于所有原生分配的完整清单 |
| arrayBuffers | ArrayBuffer、SharedArrayBuffer 及 Node.js Buffer 的相关内存 | 已包含在 external 中，不能再次相加 |
| rss | 整个进程当前驻留在主存中的空间，包含代码及原生与 JS 对象等 | 不等于 JS 堆使用量，也不是以上字段之和 |

使用 Worker 时，RSS 对应整个进程，其他这些字段对应当前线程，跨线程比较时需要保留这一口径。对象回收后，分配器和[运行时](../../glossary/runtime.md#runtime.virtual-machine)可能保留空间供后续使用，RSS 不必立即下降；某些平台上的分配器碎片也会影响 RSS。仅凭 RSS 上升不能证明 JS 对象泄漏。

## 把增长拆成可检验的假设

先在可比较的负载下观察：请求量、并发数、单次数据规模与缓存容量有没有变化？一次冷启动后的增长与运行数小时后持续增长，不是同一类证据。若相同业务周期后、可比较的回收阶段仍留下越来越多对象，应进一步检查持有关系；若堆稳定但 external 或 RSS 增长，则需要扩大到 Buffer、原生模块及进程层面。

堆快照可帮助比较对象数量和保留路径。Shallow Size 是对象自身占用；Retained Size 关注该对象被回收时，随之可能释放的那部分对象图，字段含义见 [Chrome DevTools 堆快照说明](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots#summary-view)。数值大是调查线索，仍需确认相关持有是否符合业务生命周期。找到一个大对象并不等于找到造成长期增长的错误。

[Node.js 堆快照指南](https://nodejs.org/learn/diagnostics/memory/using-heap-snapshot)提醒，捕获期间会暂停主线程，也可能显著增加内存占用。先选择可承受影响的环境与实例，再比较相同阶段的快照；快照也可能含业务数据。它不是对任意生产进程都无影响的查询。

教学失败情形：删除 Map 条目后内存仍增长，另一路事件监听器还持有同一会话对象。下一步应检查保留路径并补上注销逻辑，再在相同负载周期下比较；只反复手动触发 GC，无法回收仍然可达的对象。

闭包的语言机制继续见[词法绑定](closures-and-lexical-bindings.md)，导航后组件、订阅与缓存怎样保留见[前端路由与缓存](../frontend/routing-state-and-cache-lifecycles.md)。它们提供生命周期解释，没有新增本文内存或 GC 测量。

## 自检、关联阅读与来源

操作系统层的地址范围、驻留、[缺页](../../glossary/systems.md#systems.virtual-memory)与写时复制见[虚拟内存与缺页](../systems/virtual-memory-pages-and-faults.md)。对象可回收、分配器复用和物理页面归还分别有责任；该概念关联不表示已执行堆或驻留实验。

试着解释：不可达的环为什么可以回收？删除一个变量后，为何对象可能继续存活？heapUsed 稳定而 RSS 增长，为什么需要继续区分原生内存与分配器行为？关闭订阅为何不能交给终结回调保证？

- [事件循环与微任务](event-loop-and-microtasks.md)：理解执行机会与暂停影响，不把所有[延迟](../../glossary/performance.md#performance.latency-throughput)都归为调度问题。
- [进程、线程与协程](../systems/process-thread-coroutine.md)：区分进程地址空间与线程观测范围。
- [延迟、吞吐与排队](../performance/latency-throughput-and-queues.md)：把资源成本与[排队](../../glossary/performance.md#performance.queueing)、[尾延迟](../../glossary/performance.md#performance.percentiles)联系起来。

核查日期：2026-10-19。本文依据 MDN、V8 与 Node.js 官方资料解释机制；没有运行泄漏复现、强制 GC 或堆快照实验，也没有报告暂停时长或容量结论。具体来源已在相应段落链接。
