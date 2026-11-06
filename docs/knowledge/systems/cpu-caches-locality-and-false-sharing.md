---
id: "kb-systems-cpu-caches"
title: "CPU 缓存与局部性：数据已在内存，访问为什么仍然慢"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "解释缓存层级、缓存行、工作集与访问顺序，区分未命中、缺页、伪共享和程序同步责任。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-virtual-memory", "kb-algorithms-linear-structures"]
related: ["kb-systems-races-atomicity", "kb-performance-cpu-metrics", "kb-performance-profiling", "kb-performance-benchmarking", "kb-cache-search-eviction"]
tags: ["cpu-cache", "locality", "cache-line", "false-sharing"]
---

# CPU 缓存与局部性：数据已在内存，访问为什么仍然慢

学习入口：两段程序访问相同数量的元素，为什么执行时间仍可能差很多？前置：[虚拟内存与驻留](virtual-memory-pages-and-faults.md)、[数组与链表](../algorithms/sequences-stacks-queues-and-deques.md)。本文解释常见多级 [CPU 缓存](../../glossary/systems.md#systems.cpu-cache)的概念，参照 CMU 内存层级材料与 Linux 伪共享文档；缓存容量和访问序列为教学假设，没有运行硬件实验。

## 内存驻留不等于缓存命中

CPU 通过容量、[延迟](../../glossary/performance.md#performance.latency-throughput)和共享方式不同的存储层级取得指令与数据。L1、L2、末级缓存与主内存是常见组织，但层数、共享关系、容量和缓存行长度取决于具体处理器，不能把一款机器的周期数作为通用常数。基本机制见 [CMU 内存层级讲义](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m22/www/activities/213_lecture10.pdf)。

数据页已驻留，只能排除某些页面准备工作；访问仍可能在相应 CPU 缓存中未命中。L1 未命中可以由后续缓存层满足，不等于必然访问 DRAM；CPU 缓存未命中也不同于 [TLB](../../glossary/systems.md#systems.virtual-memory) 未命中和操作系统缺页，后两者分别涉及地址翻译缓存与页面映射/准备。TLB 未命中后，若页表已有有效且允许访问的映射，仍可查表完成翻译而不发生缺页，参照[内核页表说明](https://www.kernel.org/doc/html/latest/mm/page_tables.html#mmu-tlb-and-page-faults)。

缓存通常以一段相邻字节为搬运和一致性处理单位，而不是只缓存本次请求的一个变量。时间局部性指近期访问的数据可能再次使用，空间局部性指相邻位置可能很快被访问。缓存只能利用实际访问模式；把对象“放进内存”不保证它一直留在 CPU 缓存。

## 同样访问 32 个元素，未命中可以不同

自设一个只计数据读取的模型：矩阵为 4 行×8 列，每元素 8 字节，按行连续保存，起始地址按 64 字节对齐，因此每行恰好占一个缓存块。缓存最多保留 2 个块，全相联、[LRU](../../glossary/algorithms.md#algorithms.eviction) 替换、初始为空；一次未命中装入整块。忽略预取、其他访问、地址翻译、编译优化及[并行](../../glossary/systems.md#systems.concurrency)执行。

| 访问顺序 | 访问到的行块序列 | 本模型未命中 |
| --- | --- | --- |
| 逐行：一行读完再下一行 | 0 重复 8 次，再 1、2、3 各重复 8 次 | 每行首次一次，共 4 次 |
| 逐列：每列依次读四行 | 0、1、2、3，整体重复 8 轮 | 每次访问的块均已被挤走，共 32 次 |

逐行序列装入一行后复用其中 8 个元素；逐列序列在 4 个行块之间轮转，而缓存只能留 2 块。两者都进行 32 次元素访问，差异来自访问顺序与模型容量，并非算法少处理了数据。这里没有给出真实耗时，也不能据 32/4 推导程序一定快 8 倍。

如果缓存能容纳全部 4 块，本例逐列也可能只在首次访问各块时未命中。实际程序还受组相联映射、预取、数据依赖和其他工作集影响；连续访问常有利于局部性，却不是任意机器与负载下的速度保证。

## 工作集、容量与访问路径一起决定成本

工作集是在某段时间内反复需要的数据，而不是[进程](../../glossary/systems.md#systems.execution-units)全部已分配内存。一次冷启动的首次访问、反复使用的数据超过缓存容量，以及不同地址争用有限映射位置，都可能造成未命中；不能看到相同现象就认定缓存容量不够。

例如[链表](../../glossary/algorithms.md#algorithms.sequences)的下一个地址可能依赖当前节点的读取结果，限制可重叠的内存访问；数组即使元素个数相同，也有不同布局。把数据分块处理、缩小热路径所需字段或减少无用扫描可能改善局部性，但[重排](../../glossary/cache-search.md#cache-search.hybrid)还需保持结果语义，尤其是浮点累加、并发访问和外部可见顺序。

延迟与带宽也不同：一条依赖链可能主要等待一次次访问完成，大量独立读取又可能受到总体传输能力限制。不能仅靠增加线程数或一个缓存命中率判断瓶颈，需要结合工作量和[实际采样](../performance/profiling-stacks-and-flame-graphs.md)提出假设。

## 伪共享：不同变量也会争用同一缓存行

假设两个 CPU 上的线程分别更新自己的计数器 x、y，二者是不同对象、不会互相读写，却位于同一个一致性缓存行内。至少一方写入时，对整行的所有权或有效性处理可能让另一方反复重新取得该行；逻辑上没有共享计数器，硬件上仍共享处理单位。条件与实例见 [Linux False Sharing](https://docs.kernel.org/kernel-hacking/false-sharing.html)。

若双方更新同一个计数器，则还包含真实共享，不能靠把字段挪远来取消必要协调。相邻且只有读取的数据，也不能直接套用“写导致缓存行往返”的解释。是否存在有害伪共享，需要访问频率、布局和一致性事件等证据，不能仅看两个字段挨着就判故障。

按目标平台分开高频写字段、[分片](../../glossary/database.md#database.partitioning)计数或在合适时合并结果，可能降低争用；填充也会增加空间、减少缓存可容纳对象，并不自动优于紧凑布局。Linux 文档介绍的 perf-c2c、布局检查等工具需要在相应硬件与环境下验证，本文没有运行。

缓存一致性也不能替代[语言级同步与 happens-before](races-and-atomicity.md)。原子变量可以保证特定访问规则，却不承诺没有缓存行争用；volatile、填充或“所有 CPU 都有一致缓存”也不自动使存在数据竞争的程序正确。

## 用哪些证据检验局部性假设

先固定相同输入、结果与访问工作量，再观察目标层级的访问/未命中、周期、内存带宽和耗时。PMU 事件的定义与支持取决于处理器及工具，某个通用名称不一定同时覆盖各级读写；未命中计数不能直接当作 DRAM 字节数或缺页数。

微小布局对照还需核对编译输出、对齐、热/冷状态、线程位置和其他竞争，方法见[基准测试与加速比](../performance/benchmarks-workloads-and-speedup.md)。对局部循环的改善仍要回到整个任务，不能据缓存算例承诺业务 [P99](../../glossary/performance.md#performance.percentiles) 收益。

自检：未命中发生在哪一层？工作集是否真的能放下？访问顺序是否保留语义？不同字段是否共享一致性行且至少一方写入？改善的是访问延迟、带宽还是无用工作？

2026-10-20 核查 CMU 内存层级与 Linux 页表、伪共享资料，状态为 source-checked。64 字节、2 块缓存及 4/32 次未命中均为自设模型；未执行缓存/预取/带宽、字段布局、伪共享、PMU 或性能实验。
