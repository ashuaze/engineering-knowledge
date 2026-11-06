---
id: "kb-systems-memory-layout"
title: "栈、堆与进程内存布局：地址还在，为什么对象已经不能用"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分虚拟映射、分配器存储与语言对象寿命，解释线程栈、动态分配、悬空引用和释放后 RSS，以及布局观测能证明的范围。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-systems-virtual-memory", "kb-systems-execution-units"]
related: ["kb-runtime-gc", "kb-runtime-ffi-boundaries", "kb-runtime-virtual-machines", "kb-systems-memory-reclamation", "kb-systems-cpu-caches"]
tags: ["memory-layout", "stack", "heap", "lifetime", "linux"]
---

# 栈、堆与进程内存布局：地址还在，为什么对象已经不能用

学习入口：函数已经返回，原地址上的字节看起来没变，为什么再读仍可能出错；free 了很多对象，RSS 为什么还不降？前置：[虚拟内存](virtual-memory-pages-and-faults.md)、[执行单元](process-thread-coroutine.md)。本文用 Linux/glibc 说明映射和分配，用固定 C++20 草案 N4861 说明存储期与寿命，两种层次分别判断，片段均未执行。

## 一张地址图不能同时代表三个层次

| 层次 | 主要问题 | 观察不到什么 |
| --- | --- | --- |
| 操作系统映射 | 哪段虚拟地址有映射、权限与后备 | 某个语言对象是否还活着、是否属于调用者 |
| 分配器存储 | 哪段空间分配给谁、何时可复用 | 业务是否还持有非法旧引用 |
| 语言对象 | 初始化、访问和销毁是否满足语言规则 | 整个[进程](../../glossary/systems.md#systems.execution-units)已驻留多少物理页 |

Linux 原生进程常见代码/只读数据、可写数据、[动态分配](../../glossary/systems.md#systems.memory-layout)区域、共享库与文件映射、线程栈等区域。它们不是所有语言强制采用的一张固定从低到高分布图；地址随机化、体系结构、加载器与分配器都会影响布局。ELF 的节名也不要求与每条进程映射一一对应。

[/proc/PID/maps](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html)展示区间、权限和文件等信息；`[heap]` 不囊括所有动态分配，`[stack]` 标签也不能代表全部线程栈。旧 `[stack:tid]` 标签在 Linux 4.5 已移除，不能把“没有这个标签”解释为线程没有栈。

## 调用栈和动态存储描述不同的管理方式

调用栈通常保存函数继续执行所需的帧、局部状态与返回信息，动态存储由分配接口和所有者控制寿命。但 C++ 的“自动存储期”不保证对象一定占一块原生栈空间；[编译器](../../glossary/runtime.md#runtime.compilation)可使用寄存器、内联或消除不影响语义的存储。语言规则与机器布局分别核对。

C++20 规定静态、线程、自动和动态存储期；作用域回答名字在哪里可见，存储期回答存储保留范围，寿命回答对象何时可按相应类型使用。三者有关联但不相同。依据见 [N4861 basic.stc / basic.life](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/basic.tex)。

教学片段：

```cpp
int* expired() {
    int local = 7;
    return &local;
}

int* transferred() {
    return new int(7);
}
```

调用者不能用 expired 返回值继续读取已经结束寿命的 local，原字节尚未覆盖也不改变结论。transferred 返回的动态对象可跨过函数返回继续存活，但调用方需明确接管并最终正确释放，不能因为指针变量自己是局部变量就推定所指对象随它结束。实际工程可用明确所有权包装减少遗漏，具体接口仍需核对。

本例只说明寿命，不建议执行悬空访问观察“通常读到几”。对象销毁后存储可能仍保留，相同地址之后也可能承载别的对象；仅凭地址相等，不能证明旧引用可以合法使用，满足语言规定的存储复用条件时须另行判断。

## 每线程一份栈不等于地址空间隔离

[pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html)说明线程拥有各自栈，但共享进程地址空间。如果一个线程把仍存活局部对象的地址交给另一线程，后者并非物理上绝对不可访问；它必须满足寿命、发布同步与[并发](../../glossary/systems.md#systems.concurrency)访问规则。退出作用域前先等使用者结束，和只把指针放进线程安全[队列](../../glossary/algorithms.md#algorithms.queues)，是不同保证。

线程栈还受到大小、保护区域与实现规则限制，递归、较大的自动[数组](../../glossary/algorithms.md#algorithms.sequences)和深调用可能耗尽可用范围。[pthread_attr_setstacksize](https://man7.org/linux/man-pages/man3/pthread_attr_setstacksize.3.html)管理新线程的栈大小属性；不能把一个平台默认值当成每个线程和 [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 的固定物理成本。

自选模型：四个线程各保留 8 MiB 虚拟栈范围，合计 32 MiB；若各自只有 64 KiB 普通页驻留，则这部分合计 256 KiB。这里忽略保护页、页表、共享页与其他内存，数字只用来区分地址范围与驻留量，不是实际默认配置。

## 对象释放、分配器复用和归还系统是不同事件

glibc 的 [malloc(3)](https://man7.org/linux/man-pages/man3/malloc.3.html)说明动态存储可以来自 brk 或匿名 mmap 等路径，多线程 arena 又有自己的管理成本。free 让相应块重新可供分配器使用，不承诺每次调用都撤销映射或立即降低 RSS。碎片、缓存和仍存活对象都影响可归还的页面。

[malloc_trim(3)](https://man7.org/linux/man-pages/man3/malloc_trim.3.html)是尝试归还空闲内存的 glibc 接口，不是强制把所有空闲字节都变成 RSS 降幅的开关。不能将一种 allocator 的回收策略推广到所有语言堆或内存池。

诊断时分别记录活对象/未释放分配、分配器保留量、映射区间及驻留/共享口径。[内核 proc 文档](https://docs.kernel.org/filesystems/proc.html)说明 smaps 的 Size、RSS、PSS 等字段。某个地址区间仍映射，不证明旧对象存活；RSS 较高也不能单独证明泄漏。托管对象保留与 [GC](../../glossary/runtime.md#runtime.gc) 继续见[可达性与回收](../runtime/reachability-and-garbage-collection.md)。

## 自检

1. maps、分配器统计与语言寿命分别能回答什么？
2. expired 与 transferred 的对象在函数返回后有什么不同，责任交给谁？
3. 为什么线程栈独立不表示另一个线程绝对无法访问其中对象？
4. 教学四线程的虚拟栈范围与驻留量各是多少，还忽略哪些开销？
5. free 后 RSS 不降有哪些可能，为什么地址仍映射不能证明旧引用安全？

## 来源与核查

- [C++20 N4861 basic.tex](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/basic.tex)，2026-10-26 核查固定标签的 basic.stc/basic.life；覆盖存储期与对象寿命，不规定唯一机器布局。
- [Linux maps](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html)、[proc 文件系统](https://docs.kernel.org/filesystems/proc.html)，2026-10-26 核查；覆盖映射标签、权限与驻留字段，地址图和数字均为自选示例。
- [pthreads](https://man7.org/linux/man-pages/man7/pthreads.7.html)、[pthread_attr_setstacksize](https://man7.org/linux/man-pages/man3/pthread_attr_setstacksize.3.html)，2026-10-26 核查；覆盖共享地址空间与线程栈边界。
- [glibc malloc](https://man7.org/linux/man-pages/man3/malloc.3.html)、[malloc_trim](https://man7.org/linux/man-pages/man3/malloc_trim.3.html)，2026-10-26 核查；覆盖分配路径与归还条件，不提供本机实测。

本文为 source-checked 概念说明。没有执行地址布局、悬空访问、栈耗尽、allocator/RSS、ASLR 或跨线程寿命实验。
