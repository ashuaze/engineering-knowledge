---
id: "kb-systems-virtual-memory"
title: "虚拟内存与缺页：地址已经分配，为什么访问仍会等待"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分虚拟地址、物理页、页表与驻留内存，解释按需分页、缺页、写时复制和工作集压力。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units"]
related: ["kb-systems-syscalls", "kb-systems-file-descriptors", "kb-runtime-gc", "kb-devops-container-boundaries", "kb-performance-slow-api", "kb-systems-cpu-caches", "kb-systems-memory-layout", "kb-systems-memory-reclamation"]
tags: ["virtual-memory", "paging", "page-fault", "copy-on-write"]
---

# 虚拟内存与缺页：地址已经分配，为什么访问仍会等待

映射、分配器存储和语言对象寿命的差别见[栈堆与内存布局](process-memory-layout-stacks-heaps-and-lifetimes.md)；[并发](../../glossary/systems.md#systems.concurrency)读者仍持旧引用时怎样延后释放，见[安全内存回收](safe-memory-reclamation-aba-hazards-and-epochs.md)。地址仍映射与对象仍可合法访问分别判断，新关联不增加本篇内存实测。

学习入口：申请内存成功，为什么第一次访问仍变慢，甚至后来才遇到内存不足？前置：[进程与地址空间](process-thread-coroutine.md)。本文讨论具有 MMU 的 Linux 系统，以内核概念文档及 Linux man-pages 6.19 为参照；地址算例和时序均为纸面推演，没有运行内存或[缺页](../../glossary/systems.md#systems.virtual-memory)实验。

## 程序地址需要经过映射

程序使用的虚拟地址不直接等于内存条上的物理位置。操作系统维护映射与访问权限，CPU 的地址转换机制据此找到物理页及页内位置。不同[进程](../../glossary/systems.md#systems.execution-units)中相同的地址数值，不足以证明访问同一份数据；显式共享映射又允许多个地址关联同一物理页。

| 对象 | 主要含义 | 不等于什么 |
| --- | --- | --- |
| 虚拟地址空间 | 进程可组织的地址范围与映射 | 已经占有同等大小的物理内存 |
| 页表 | 地址转换及相关权限等信息 | 应用对象的引用关系 |
| 物理页 | 物理内存中的存储单位 | 必然只归一个进程使用 |
| TLB | [CPU 缓存](../../glossary/systems.md#systems.cpu-cache)的地址转换信息 | 文件内容缓存或全部页表 |

机制见[内核内存概念](https://docs.kernel.org/admin-guide/mm/concepts.html)。TLB 未命中可能需要查页表，不自动意味着发生缺页或读取磁盘；连续的虚拟地址也不要求对应物理页连续。

教学算例：假定页大小为 4 KiB，虚拟地址 0x12345 可拆成虚拟页号 0x12 和页内偏移 0x345。如果当前映射把该页关联到物理页框 0x9，结果为 0x9345。这里的页大小和映射都是假设，不能把 4 KiB 当作所有系统的唯一页大小。

## 建立范围与取得页面是不同工作

[mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html)可建立映射；匿名映射不由普通文件提供初始内容，文件映射则关联文件范围。映射存在不表示所有页面已经驻留或每次访问都无需等待，实际行为还受映射选项和内存状态影响。

malloc 又是分配器接口：它可能复用已有区域，也可能向系统申请更多空间，并非每次调用都产生一次 mmap 或立即取得全部物理页。Linux 的乐观分配及相关策略也使“返回非空指针”不能推广为未来所有访问均有充足资源，见 [malloc(3)](https://man7.org/linux/man-pages/man3/malloc.3.html)。

应用对象不再使用、分配器可复用空间、映射解除与驻留页减少，是不同事件。托管语言还多一层[可达性与垃圾回收](../runtime/reachability-and-garbage-collection.md)；[GC](../../glossary/runtime.md#runtime.gc) 完成不能直接推出进程驻留量立即下降。

## 缺页可以是正常执行路径

地址访问触发异常后，内核会判断映射是否合法、权限是否允许，以及能否准备相应页面。合法访问可能在处理后继续；非法地址或权限冲突则可能导致信号和程序失败，文件映射等场景还有其他错误，不能把所有失败统称为同一种缺页。

[getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)区分无需 I/O 处理的 minor fault 与需要 I/O 的 major fault。首次建立页面或写时复制可能走无需磁盘读取的路径；缺页计数增多并不单独证明正在频繁交换到磁盘。反过来，即便没有 major fault，内存分配、复制和回收也有成本。

纸面时序：建立一段匿名映射 → 首次写入某页 → 必要时处理缺页、准备可写物理页 → 继续写入。第二次访问同页可能省去该次准备，但不能保证页面以后永远驻留，也不能据此给出固定耗时。

## 写时复制保留隔离，推迟部分复制

Linux 的 fork 通常通过写时复制实现地址空间复制，见 [fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)。对本例普通私有页面，父子进程开始可共享底层页面；一方写入时再建立相应私有内容。父进程不会因为子进程修改了私有变量就自动读到新值。

这不表示 fork 零成本：页表、任务结构及后续写入仍需要资源。显式共享映射也不能套用“写入必然互不可见”的私有页面结论。[mmap 的 MAP_PRIVATE 与 MAP_SHARED](https://man7.org/linux/man-pages/man2/mmap.2.html)规定了不同可见性，应用仍需同步共享访问。

## 工作集与统计口径决定怎样解释压力

页面驻留后的访问成本继续见[CPU 缓存与局部性](cpu-caches-locality-and-false-sharing.md)。地址翻译、操作系统缺页与数据缓存命中分别分析；缓存篇的访问序列为纸面模型，没有新增本文缺页或硬件采集证据。

工作集可用来描述某段时间内实际活跃访问的页面。活跃需求持续超过可用容量时，回收和重新取得页面可能反复发生，等待与[尾延迟](../../glossary/performance.md#performance.percentiles)随之增加；虚拟地址范围较大本身不足以证明这一情况。

Linux 的 size、resident 等统计各有口径；[proc_pid_statm(5)](https://man7.org/linux/man-pages/man5/proc_pid_statm.5.html)还明确说明部分值存在准确性限制。RSS 包含驻留共享页，不能把多个进程的 RSS 简单相加当作互不重叠的物理占用；语言堆指标也不覆盖所有映射、原生分配与内核资源。

诊断时把“对象被长期持有”“分配器保留”“文件映射”“页面回收压力”“[容器](../../glossary/devops.md#devops.containers)额度不足”列为不同假设，再组合映射、驻留、缺页、I/O、限制与应用访问模式判断。容器额度继续见[资源隔离](../devops/images-containers-and-resource-isolation.md)，请求等待分析见[慢 API 排查](../performance/slow-api-investigation.md)。

自检：看到的是地址范围、驻留量还是语言堆？一次缺页是否需要 I/O？父子共享的是私有页面的底层存储还是显式共享状态？减少对象引用后，哪一层负责将空间归还？

2026-10-20 核查上述 Linux 内核与 man-pages 资料，状态为 source-checked。未执行分配/触页、fork 写时复制、页表/TLB、交换回收或容器内存实验；算例不作为实际页面计数、[延迟](../../glossary/performance.md#performance.latency-throughput)或 OOM 结果。
