---
id: "kb-systems-lock-free-progress"
title: "无锁算法与进度保证：系统还在推进，为什么我的操作一直失败"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分线性化正确性、整体进度与单次完成，解释 lock-free、wait-free、CAS 重试、帮助机制和端到端依赖的证明范围。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-systems-memory-order", "kb-systems-synchronization"]
related: ["kb-systems-memory-reclamation", "kb-systems-context-switch", "kb-systems-races-atomicity", "kb-systems-cpu-caches", "kb-performance-benchmarking"]
tags: ["lock-free", "wait-free", "linearizability", "cas"]
---

# 无锁算法与进度保证：系统还在推进，为什么我的操作一直失败

学习入口：实现没有 [mutex](../../glossary/systems.md#systems.synchronization)，而且 CAS 是原子的，为什么某个调用仍可能长时间重试？前置：[内存顺序](memory-order-atomics-and-publication.md)、[同步原语](locks-and-synchronization.md)。本文按[并发](../../glossary/systems.md#systems.concurrency)算法的抽象步骤讨论进度，并与固定 C++20 原子接口边界对照；数学状态和时序为纸面推演，不提供未经验证的生产无锁结构。

## 正确性和进度回答不同问题

线性化要求并发操作能按符合对象顺序规格、且尊重非重叠操作先后关系的方式解释，仿佛每次在调用与返回之间某点生效。依据见 [Herlihy/Wing 1990](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf)。这里的点是证明工具，不能通过找到一条 CAS 就省略失败、读取和空结果路径的论证。

一个拿着全局锁的正确[队列](../../glossary/algorithms.md#algorithms.queues)可以线性化，却会被暂停的锁持有者阻挡；一个不断返回错误值的实现即使总能立刻结束，也没有实现正确队列。还需分别检查数据竞争、对象寿命和顺序规格。

| 检查维度 | 需要回答 | 不能单独保证 |
| --- | --- | --- |
| 安全性 | 每次结果和状态是否符合规格 | 操作一定能结束 |
| 整体进度 | 持续执行时是否总有某次操作完成 | 某个指定调用不饥饿 |
| 单次步骤界限 | 每次操作是否在有限个自身步骤内完成 | [线程](../../glossary/systems.md#systems.execution-units)及时得到 CPU 或墙钟期限 |
| 实际成本 | 在本次负载下耗时、重试、内存和 CPU 怎样 | 所有交错下的算法证明 |

## lock-free 不要求每个竞争者都获胜

以下用算法文献常见范围表述，假设系统仍有参与者持续执行算法步骤，原语满足所声明模型；不是对无限期停机线程的墙钟承诺。

| 进度类别 | 直观要求 | 仍允许什么 |
| --- | --- | --- |
| [obstruction-free](../../glossary/systems.md#systems.lock-free-progress) | 某操作独占执行足够步骤时能完成 | 持续相互干扰时无人完成 |
| lock-free | 系统持续执行时，总体不断有操作完成 | 特定参与者一直失败或饥饿 |
| wait-free | 每个操作在有限个自身步骤内完成，不依赖其他参与者速度 | 被调度器暂停，或单个步骤实际耗时较长 |

[Herlihy 1991](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)从每次操作的有限步骤定义 wait-free；[Brown 的回收研究](https://www.cs.toronto.edu/~tabrown/debra/fullpaper.pdf)说明 lock-free 的整体完成条件与暂停参与者问题。步骤界限可依赖参与者数或对象大小，不必是固定常数；无等待是术语名称，也不意味着没有缓存访问、总线竞争或[调度等待](../../glossary/performance.md#performance.cpu-metrics)。

“[非阻塞](../../glossary/systems.md#systems.blocking) [socket](../../glossary/systems.md#systems.fd-socket)”描述调用暂不可用时的返回契约，不能直接映射为 wait-free 数据结构；自旋锁也可能没有睡眠[系统调用](../../glossary/systems.md#systems.privilege)，却仍依赖持锁者释放。因此“没调用锁 API”只是实现表象。

## 在一个小模型里定位生效点与饥饿

自选数学计数器 `n` 初始为 0、无上界、没有对象回收。每个 `increment` 读取旧值，尝试强 CAS 将 `n` 改为旧值加一；失败后采用新观察值重新计算，成功后立即返回。原语按原子抽象步骤处理；这不是以有限宽整数直接实现的 C++ 程序。

| 次序 | T1 | T2 | n |
| --- | --- | --- | --- |
| 1 | 读到 0，准备写 1 | | 0 |
| 2 | | CAS 0→1 成功，返回一次 | 1 |
| 3 | CAS 0→1 失败，观察到 1 | | 1 |
| 4 | 准备写 2，再次暂停 | CAS 1→2 成功，返回一次 | 2 |
| 5 | CAS 1→2 失败，观察到 2 | | 2 |
| 6 | 准备写 3 | CAS 2→3 成功，返回一次 | 3 |

成功 CAS 是本模型增量生效的位置，失败尝试不多加一次。可以重复同类交错，使 T2 继续完成而 T1 长期不成功；这说明整体完成与单个调用不饥饿不同。实际计数器有范围与回绕，不能直接借用本模型的无限自然数论证。

如果改用允许虚假失败的 weak CAS，一次失败就不能证明别的操作必然成功；证明要另外处理虚假失败和原语进度。多字段结构里，别的线程改了一个辅助字段也未必代表高层操作已完成，不能照搬本计数器推理。

失败之后还要重新判断业务条件。若算法维护有限名额而不是无限增量，旧值更新为零后必须重新检查能否再减；若每次尝试先做外部付款，失败也不会撤销付款。有关语言顺序与 CAS 接口的细节继续见[内存顺序专题](memory-order-atomics-and-publication.md)。

## 原语无锁和整个接口无锁不是同一个范围

C++20 的 `is_lock_free` / `is_always_lock_free` 用于核对相应原子类型/操作实现，不给周围的分配器、析构、日志、回调、等待和回收算法背书。[N4861 atomics.lockfree / atomics.types.operations](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/atomics.tex)还区分原子等待与普通原子访问；一个原子对象有无锁属性，并不使其 wait 变成无需等待。

标准措辞也要与算法论文分开：[N4861 intro.progress](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/basic.tex)对单个未阻塞线程的 lock-free execution 使用完成要求，对多个并发执行则使用至少一个“应完成”并讨论异常干扰。不能把这些规则增强成每个 CAS 循环都有固定重试次数。

帮助机制是让其他参与者可完成已发布的操作描述，而非一直等原发起者恢复。需要定义谁执行哪一步、如何避免重复效果、描述对象何时可回收，以及帮助链是否有界；无限循环“帮别人”不会自动成为 wait-free。把付款、文件写入等不可随意重复的动作混入帮助阶段，仍有独立协议责任。

## 选型要同时看证明、负载和维护成本

无锁结构可减少对暂停持锁者的依赖，但竞争可能带来大量失败 CAS、[缓存行](../../glossary/systems.md#systems.cpu-cache)传递和待回收节点；短临界区下的锁可能更简单且更快，结论需来自具体负载。wait-free 的额外元数据、帮助与步骤界限也有成本。

评估应列出：顺序规格与生效点；饥饿允许范围；分配/回收和回调依赖；参与者注册/退出；容量满与失败返回；暂停一个参与者后的结果；负载与尾部耗时。有限测试能发现反例，不能凭长时间跑通就证明所有调度下的进度。对象寿命的独立证明见[安全内存回收](safe-memory-reclamation-aba-hazards-and-epochs.md)。

## 自检

1. 一个线性化的锁队列为什么仍可能没有 lock-free 进度？
2. obstruction-free、lock-free、wait-free 各排除哪类等待，哪些仍没排除？
3. 计数模型中 T2 完成三次时 n 是多少，为什么 T1 仍可能继续失败？
4. weak CAS 的一次失败为什么不能照搬强 CAS 模型的归因？
5. atomic 类型无锁之后，还要检查哪些路径，为什么墙钟期限仍不能推出？

## 来源与核查

- [Herlihy/Wing：Linearizability（1990）](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf)、[Herlihy：Wait-Free Synchronization（1991）](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)，2026-10-26 核查定义与证明范围；不引用历史跑分作为本文结果。
- [C++20 N4861 atomics.tex](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/atomics.tex)、[basic.tex](https://raw.githubusercontent.com/cplusplus/draft/n4861/source/basic.tex)，2026-10-26 核查固定标签；覆盖原子属性、CAS、等待与标准进度措辞。
- [Brown：Reclaiming Memory for Lock-Free Data Structures](https://www.cs.toronto.edu/~tabrown/debra/fullpaper.pdf)，2026-10-26 核查作者公开长版的进度与回收背景；不把算法步骤等同实际系统时限。

本文为 source-checked 概念说明。没有执行无锁数据结构、并发历史检查、模型检查、参与者暂停、回收容量或性能实验。
