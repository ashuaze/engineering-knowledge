---
id: "kb-systems-memory-reclamation"
title: "ABA 与安全内存回收：节点已经移除，什么时候才能真正释放"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分发布、移除、退役与回收，解释地址复用和逻辑 ABA，比较 Hazard Pointer、Epoch 与 RCU 的读者保护、停滞和容量边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-systems-memory-order", "kb-systems-memory-layout"]
related: ["kb-systems-lock-free-progress", "kb-systems-ipc", "kb-runtime-gc", "kb-runtime-ffi-boundaries", "kb-systems-signals-shutdown"]
tags: ["reclamation", "aba", "hazard-pointer", "epoch", "rcu"]
---

# ABA 与安全内存回收：节点已经移除，什么时候才能真正释放

学习入口：头指针已经原子换走，为什么删除旧节点仍会让读[线程](../../glossary/systems.md#systems.execution-units)崩溃？前置：[内存顺序](memory-order-atomics-and-publication.md)、[对象寿命与布局](process-memory-layout-stacks-heaps-and-lifetimes.md)。本文用[用户态](../../glossary/systems.md#systems.privilege)原生对象的抽象模型说明回收，并单独引用 Linux 内核 [RCU](../../glossary/systems.md#systems.memory-reclamation)；不把内核 API 或历史 hazard pointer 提案当作 C++20 标准库，时序不是可直接复制的实现。

## 移除只关掉新入口，旧读者还可能握着引用

| 阶段 | 发生了什么 | 尚未证明什么 |
| --- | --- | --- |
| 发布 | 新对象成为可被发现的共享状态 | 未来读取者可以无限期持有它 |
| 移除 | 从指定结构的新查找路径摘下对象 | 所有旧读者已经结束 |
| 退役 retire | 交给回收协议，等待不再被使用的证据 | 现在就能析构、复用或归还存储 |
| 回收 reclaim | 证据满足后销毁/释放，按协议允许复用 | 外部副作用和业务状态也被恢复 |

简单失败时序：R 读到根指针 A 后暂停；W 把根换成 B，立即释放 A；R 恢复并读取 A 的字段。这是可能的释放后使用，不需要等到 R 的下一次 [CAS](../../glossary/systems.md#systems.synchronization)。release/acquire 解决相应发布顺序，也不赋予 A 在未来仍存活的保证。

[Michael 2004](https://www.eecg.utoronto.ca/~amza/ece1747h/papers/hazard_pointers.pdf)从暂停读者持有旧引用的情形引出回收问题；[Linux RCU 概述](https://docs.kernel.org/RCU/whatisRCU.html)也明确把移除与回收分开。每条仍可到达对象的路径都必须纳入同一保护论证，不能只检查一个根。

## ABA 既可能来自地址复用，也可能来自逻辑复用

设抽象栈开始为 A→B→C：T1 记住头 A 和后继 B 后暂停；T2 移除 A、再移除 B，然后把仍存活的 A 重新接到 C 前面，头再次为 A。若 T1 只比较头地址，就可能 CAS 成功并把已不属于当前栈的 B 接回。这段反例假设 A/B 存储都保留且已正确同步，专门展示逻辑历史改变；不包含非法解引用来“证明”结果。

另一种情况是 A 已释放，其地址给了新节点。数值地址相同，代表的对象却不同。版本标签可让比较包含代次，但还需证明标签在观察窗口内不回绕。自选 3 位标签经过 8 次递增会回到原值；“加了版本”也没有自动获得无限历史。

Hazard Pointer 等回收方法可以防止仍受保护对象被释放并以该地址任意重建，但不自动阻止同一个仍存活节点被移除后重新插入的逻辑 ABA。结构更新规则、标签与安全回收各承担一段责任；seq_cst 也不替代这些身份信息。

## Hazard Pointer 保护的是明确对象，发布保护后还要验证

概念流程是先取得候选引用，公开“我可能使用它”的保护记录，再重新验证候选仍满足该结构的访问条件；验证成功后才解引用，需要时重试。使用结束后撤掉保护，移除者则扫描相应域的记录并按协议处理退役集合。

| 相互交错 | 必须达成的结果 |
| --- | --- |
| 移除者在保护公开前已摘下并检查对象 | 读者不能未经重新验证就访问旧候选 |
| 保护已成功建立并持续有效 | 回收者必须遵守保护，读者才可按算法使用该对象 |
| 读者撤销保护后继续缓存裸指针 | 后续使用失去保证；重新进入保护不追认中间访问 |

这只是义务分解，没有给出可运行的 load/store 顺序配方；保护发布、验证、扫描及结构访问需要匹配所选库的完整[内存模型](../../glossary/systems.md#systems.memory-order)。Michael 原论文的保护/验证步骤和 [P0233R2](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0233r2.pdf)说明其依据。引用不表示该历史提案接口属于 C++20，也不将某方法核心操作的进度直接推广到分配、析构和完整遍历。

暂停读者通常只直接保护其已登记的有限对象，但还需计算退役批次、保护记录和扫描成本。不能把“有限个保护槽”直接当成整个程序保留内存的固定上界，相关可达链和对象析构也可能保留更多资源。

## Epoch 与 RCU 保护的是一段读取范围

典型 Epoch-based Reclamation（EBR）让参与者登记进入读取阶段，在退出/静止点表明不再使用这一段取得的旧引用；回收者等待覆盖旧读者的时代推进条件。一个参与者停在活动阶段，可能拖住一大批退役对象，结构操作仍可完成，内存却不断保留。依据见 [Brown 的 EBR 讨论](https://www.cs.toronto.edu/~tabrown/debra/fullpaper.pdf)；不能把基础 EBR 的结论套用所有改进变体。

Linux RCU 用读取临界区、发布/取用原语与宽限期等规则协调。synchronize_rcu 等待的是调用前已经存在的相关读取临界区结束，不要求从此没有新读者；call_rcu 则登记满足相应条件后执行的回调。依据见[RCU 要求说明](https://docs.kernel.org/RCU/Design/Requirements/Requirements.html)。

自选 RCU 时间线：R1 在 t=0 进入；W 在 t=2 摘下 A 并开始等待宽限期；R2 在 t=3 进入且只通过已更新入口取得 B；R1 在 t=5 离开，R2 在 t=9 离开。忽略其他相关读者与实现[延迟](../../glossary/performance.md#performance.latency-throughput)时，A 的这项旧读者条件在 t=5 已满足，不必等 R2 的 t=9；实际回收可晚于 t=5，不能凭这条线宣布 API 必定在 t=5 返回。

如果 A 的引用逃逸到临界区外，或 W 没摘除所有可达入口，上述论证就不成立。RCU 也不自动串行化多个写者，原地修改可见字段仍需对应同步规则。不同 RCU flavor、内核配置和用户态库的允许[阻塞](../../glossary/systems.md#systems.blocking)、注册与退出规则，应按所选实现判断。

## 回收延后也是容量与退出协议

自选稳定退役速率为每秒 2000 个节点，每个 128 字节；回收暂停 30 秒，则新增退役载荷为 60000 个、7680000 字节，约 7.32 MiB。此处忽略分配器/保护元数据和析构持有资源，不是实际容量测试，也不能由平均速率保证峰值上界。

退出时应明确不再接纳新操作、参与者已离开/注销、在途使用结束、退役回调完成与域本身销毁的顺序。不能为赶期限而替仍在运行的线程清掉保护记录；如果它后来恢复，危险引用仍在。超时只能触发既定的隔离或失败策略，不能生成“无人使用”的证据。

## 自检

1. 根已经从 A 换成 B，为什么 A 还不能立即释放？
2. 逻辑 ABA 与地址回收复用各改变什么，Hazard Pointer 为什么不能自动解决全部 ABA？
3. 为什么保护记录公开后还需验证，撤销后缓存的裸指针有何问题？
4. RCU 时间线中旧读者条件何时满足，为什么不要求等待所有未来读者？
5. 退役暂停算例新增多少载荷，为什么超时不能直接清理别人的保护状态？

## 来源与核查

- [Michael：Hazard Pointers（2004）](https://www.eecg.utoronto.ca/~amza/ece1747h/papers/hazard_pointers.pdf)、[WG21 P0233R2（2016）](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0233r2.pdf)，2026-10-26 核查回收、保护/验证与 ABA 范围；未照搬论文硬件现状或性能数据。
- [Brown：Reclaiming Memory for Lock-Free Data Structures](https://www.cs.toronto.edu/~tabrown/debra/fullpaper.pdf)，2026-10-26 核查作者长版中的 EBR/停滞与回收背景；不实现其信号中和扩展。
- [Kernel What is RCU](https://docs.kernel.org/RCU/whatisRCU.html)、[RCU Requirements](https://docs.kernel.org/RCU/Design/Requirements/Requirements.html)，2026-10-26 核查滚动文档；仅按相应内核协议讨论，不转写为用户态 C++ 屏障配方。

本文为 source-checked 概念说明。没有执行 ABA/释放后使用、hazard/epoch/RCU、停滞回收、线程注销或容量实验。
