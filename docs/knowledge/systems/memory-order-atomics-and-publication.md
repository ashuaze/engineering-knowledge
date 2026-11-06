---
id: "kb-systems-memory-order"
title: "内存顺序与原子操作：读到标志之后，怎样才算完成发布"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "固定以 C++20 为范围，区分数据竞争、原子性和跨对象排序，推演发布条件、CAS 重试、ABA 与进度保证。"
created: "2026-10-22"
updated: "2026-10-26"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-systems-races-atomicity", "kb-systems-synchronization"]
related: ["kb-systems-cpu-caches", "kb-systems-execution-units", "kb-systems-ipc", "kb-systems-deadlocks-recovery", "kb-systems-lock-free-progress", "kb-systems-memory-reclamation"]
tags: ["cpp20", "memory-order", "atomics", "publication"]
---

# 内存顺序与原子操作：读到标志之后，怎样才算完成发布

整体进度与单次完成继续见[无锁算法与进度保证](lock-free-algorithms-linearization-and-progress.md)；发布之后的对象寿命、[ABA](../../glossary/systems.md#systems.memory-reclamation) 与退役回收继续见[安全内存回收](safe-memory-reclamation-aba-hazards-and-epochs.md)。新文扩充概念证明范围，本文仍以原声明的 C++20 来源和纸面模型为依据。

学习入口：生产者先填写对象、再把原子标志设为“就绪”，消费者看到标志后就一定能安全读取对象吗？需要检查标志使用的顺序、这次读取究竟来自哪次写入，以及对象是否还存活。单个原子字段不能自动保护旁边的普通字段或完整业务流程。

前置：[竞态与原子性](races-and-atomicity.md)、[锁与同步原语](locks-and-synchronization.md)。本文固定讨论 **C++20 的[线程](../../glossary/systems.md#systems.execution-units)[内存模型](../../glossary/systems.md#systems.memory-order)**，按公开草案 N4861 的固定标签核查规则。[WG21 编辑报告 N4859](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/n4859.html)说明 N4861 与 C++20 DIS N4860 的正文内容一致，差别为封面等编排项目。下文不使用滚动草案替换这一版本，也不把规则直接推广到 Java、Linux 内核代码或跨进程共享对象。

## 先排除数据竞争，再讨论读到哪个值

在本文普通线程访问的范围内，两个线程对同一内存位置有冲突操作，其中至少一个非原子，且双方没有 happens-before 顺序，就构成数据竞争；C++20 将这种执行归为未定义行为。冲突包含写与读、写与写等关系。不能把结果仅列成“读到旧值或新值”，再据此证明安全。规则见 [N4861 `intro.races`](https://github.com/cplusplus/draft/blob/n4861/source/basic.tex)。

这与业务竞态不同：所有字段都通过原子操作访问，也可能因“检查还有名额”和“占用名额”分开执行而超额。反过来，日志显示写入先发生、插入休眠，或在某款 CPU 上反复跑对，都没有建立语言要求的同步关系。`volatile` 普通变量也不能充当线程间发布协议。

把三个问题分开，有助于检查缺口：

| 问题 | 要求说明的边界 | 仍需另外证明什么 |
| --- | --- | --- |
| [原子性](../../glossary/systems.md#systems.atomicity) | 对某个原子对象的指定操作不可分割 | 多次操作是否共同维护不变量 |
| 可见性 | 某次读取允许来自哪些写入 | 读取对象是否仍然存活、是否有后续写者 |
| 排序 | 哪些操作必须先于另一些操作被观察 | 是否真的建立了跨线程同步边 |

例如统计计数可以只需要独立累计；把计数值同时解释为“前面所有对象都已初始化”，则增加了跨对象发布要求。选择内存顺序应由这个用途决定，不能只看变量类型。

## 四种常用顺序提供什么关系

以下是用于阅读算法的摘要，省略 `consume` 与独立 fence 的完整规则；依据为 [N4861 `atomics.order`](https://github.com/cplusplus/draft/blob/n4861/source/atomics.tex)。每个原子对象各有修改顺序，不能由此得到所有对象的一条共同时间线。

| 顺序 | 在本问题中的作用 | 不能由此推出 |
| --- | --- | --- |
| `relaxed` | 保留该原子操作的原子性及单对象一致性要求 | 自动发布其他普通字段 |
| `release` 写入 | 为此前操作提供可被对应 acquire 接收的发布边界 | 所有读者都已观察到它 |
| `acquire` 读取 | 读到相应 release 或其 release sequence 的写入时建立同步 | 任意一次 acquire 都会获得“最新数据” |
| `seq_cst` | 带有适用的 acquire/release 效果，并参加满足标准约束的单一总序 | 多字段事务，或把所有非 SC 操作一并放入该总序 |

原子读改写还可用 `acq_rel`，同时承担获取和发布的作用；纯 `load` 不能使用 `release`，纯 `store` 不能使用 `acquire`。顺序不是可以任意装到每个操作上的性能档位。

`seq_cst` 通常更便于起步推理，但混合较弱顺序后仍需完整论证。[WG21 P0668R5](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0668r5.html)记录了 C++20 前后修订 SC 约束的背景；这类历史修订也说明，不能仅凭某个处理器的指令直觉定义语言保证。

## 一次性发布的纸面证明

下面是未执行的 C++20 操作模型，不是完整程序。假设 `payload` 是普通整数，`ready` 是原子布尔值，两者均在线程启动前完成初始化；只有一个生产者执行一次发布，`ready` 只从 `false` 变为 `true`，对象一直存活到参与者结束。生产者发布后不再写 `payload`，消费者只在条件成立时读取，也没有其他访问者。

| 生产者 | 消费者 |
| --- | --- |
| A：普通写 `payload = 42` | C：以 `acquire` 读取 `ready` |
| B：以 `release` 写 `ready = true` | D：仅当 C 返回 `true` 时读取 `payload` |

这个受限模型中，返回 `true` 的 C 只能读自 B。于是 A 先于 B，B synchronizes-with C，C 先于 D，形成 A happens-before D；没有其他写者时，D 读取 42。若 C 返回 `false`，消费者不读取载荷，也不能声称发布已经完成。这里证明的是条件成立后的读取，不是循环必定在期限内观察到 `true`。

这种“先写载荷、再发布标志、读到对应标志后读载荷”的推理方式，可对照 [WG21 N2480 的历史解释](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2480.html)理解；其旧版本细节不能替代本文固定的 C++20 规则。

把同一模型中的 B、C 都改成 `relaxed`，即使 C 返回 `true`，也没有这条发布同步边。随后普通读取 `payload` 与 A 缺少所需顺序，构成数据竞争；这不是一个保证只可能打印 0 或 42 的合法实验模型。原子标志自己没有数据竞争，不能替载荷提供保证。

发布也不赋予永久访问权。若生产者在 B 之后再次改写载荷，或消费者读取前对象已销毁，上面的证明前提就失效。需要反复使用缓冲时，必须再设计归还、下一代身份及复用协议；仅把 `ready` 重置成 `false` 不足以证明这一轮读者已经离开。

## “同样的值”不等于“读自对应发布”

一般规则允许 acquire 读取 release sequence 内的写入，从而与序列起点的 release 建立同步。在 C++20 中，该序列从一次 release 开始，后续连续成员是原子读改写；普通 atomic store 即使来自同一线程，也不能按旧版本规则继续这条序列。版本变化及动机见 [P0982R1](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0982r1.html)，固定措辞可核对 N4861 `intro.races`。

纸面反例：P 写完载荷后对 `state` 做 release store 1；Q 再对同一对象做 relaxed store 2；R 的 acquire load 读到 Q 写的 2。Q 的这次普通 store 不会自动转发 P 的发布，所以 R 不能仅靠“2 比 1 大，应该更新”就读取 P 的普通载荷。缺少其他同步时，这个读取仍不合法。若 Q 改用原子读改写，必须进一步核对它是否处于那条 release sequence、R 实际读自哪里；操作名称本身仍不是完整证明。

因此，读取结果与写入来源的关系是证明的一部分。多个写者反复写同一个 `true`、计数器回绕或槽位重复使用时，仅比较值可能无法表达“对应哪一代”。可用锁、显式版本或有严格所有权的状态协议缩小问题，但每一种方案都要另行证明。

## CAS 重试的是判断，不只是那条指令

[CAS](../../glossary/systems.md#systems.synchronization) 将当前值与 `expected` 比较，相符时写入 `desired`；失败时把观察到的值写回 `expected`。C++20 的 `compare_exchange_weak` 允许虚假失败，因而一次失败不能证明必然有另一个业务操作成功。成功是原子读改写，失败按原子读取处理；失败顺序不能是 `release` 或 `acq_rel`。依据见 [N4861 `atomics.types.operations`](https://github.com/cplusplus/draft/blob/n4861/source/atomics.tex)。

用“还剩一个名额才减一”做纸面检查：T1 读到 1 并准备写 0，T2 先把名额改为 0；T1 CAS 失败，得到新的 `expected = 0`。正确的下一步是重新判断是否仍有名额。若继续沿用“曾经看到 1”的结论，再无条件尝试更新，就把保护条件丢掉了。需要重新计算的 `desired` 也不能永久绑定第一次读取的值。

可重试计算还必须控制副作用。若每次尝试前都先发邮件或写外部账本，CAS 失败不会回滚这些动作。对纯数值转换可在每次新状态上重新计算；涉及 I/O、分配、对象解引用和多字段不变量时，应重新评估是否应使用锁或其他事务边界。本文不提供未经编译、执行和算法审阅的“安全无锁栈”。

### ABA 与对象回收是另一个证明义务

教学时序：T1 记下头指针地址 A 后暂停；T2 移除 A，再改变结构，最后让头指针的值重新变成 A。T1 的比较可能成功，但它先前对结构和对象身份的判断已经过期。如果旧对象已回收，T1 甚至可能在比较之前解引用失效对象。把 CAS 改成 `seq_cst` 不会让对象复活，也不会记录未编码的变化历史。

版本标签需要证明不会在观察窗口内回绕；安全回收机制需要证明仍可能使用对象的读者已经被保护或离开。两者处理的缺口不同，不能用一个更宽的整数或一次屏障替代全部证明。[WG21 P0233R2](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0233r2.pdf)讨论了推迟回收与 ABA 的关系；它在本文中是机制资料，不表示其提议的 hazard pointer API 属于 C++20。

## 没写锁，不代表每个调用都能及时完成

`std::atomic<T>` 的具体操作不总是无锁，要核对目标实现与类型的 `is_lock_free` / `is_always_lock_free`。即使底层 CAS 无锁，包围它的算法仍可能分配内存、等待其他线程、调用隐藏锁或无限重试。类型属性不能替整个调用路径背书。

算法文献中的 [lock-free](../../glossary/systems.md#systems.lock-free-progress) 关注整体进度，允许某个参与者长期重试；wait-free 进一步要求每次操作在有限个自身步骤内完成。自身步骤保证也不是线程必被及时调度或墙钟时间上界。区分这些概念及端到端分配约束，可参考 [P0233R2 的进度讨论](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0233r2.pdf)。

还要区分算法声称与语言措辞：N4861 `intro.progress` 对只有一个未[阻塞](../../glossary/systems.md#systems.blocking)线程的 lock-free 执行给出完成要求；多个执行[并发](../../glossary/systems.md#systems.concurrency)时使用“至少一个应完成”的措辞，并讨论异常干扰。不能把它升级成每个 CAS 循环必在固定次数内成功。标准原子属性和线程进度规则见 [N4861 `atomics.lockfree`](https://github.com/cplusplus/draft/blob/n4861/source/atomics.tex)与 [`intro.progress`](https://github.com/cplusplus/draft/blob/n4861/source/basic.tex)。

## 缓存一致性不能代替语言同步

缓存一致性帮助多个核心协调同一存储位置的副本，语言模型则约束程序允许的执行、编译变换和跨对象同步。载荷和标志可能位于不同[缓存行](../../glossary/systems.md#systems.cpu-cache)；硬件能保持各位置一致，也不自动补上上述缺失的发布关系。正确的 C++ 证明先写语言同步关系，再由实现把它映射到目标指令。

Linux 的[内存屏障文档](https://docs.kernel.org/core-api/wrappers/memory-barriers.html)同时讨论[编译器](../../glossary/runtime.md#runtime.compilation)、CPU 排序及缓存影响，但它描述的是内核的访问和屏障规则。不能把 `READ_ONCE`、内核屏障或“刷新到主存”的直觉直接当作[用户态](../../glossary/systems.md#systems.privilege) C++20 的同步 API。屏障也不等于持久化保证；断电恢复是另一套协议。

工程上应先用容易检查的所有权或锁缩小共享状态，再决定是否有理由引入较弱内存顺序。若希望通过降低顺序强度改善性能，应先保留正确性证明和真实瓶颈证据；本文没有执行性能对照，不声称 `relaxed` 在所有平台更快。

## 自检、关联与核查范围

- 一次 acquire 读到 `true` 时，如何确定它读自哪次 release？如果标志可重复使用，哪条前提需要重写？
- 标志是原子的而载荷是普通字段，把发布双方都改为 `relaxed` 后，为什么不能只枚举“旧值/新值”？
- CAS 失败后哪些判断和副作用可以重试？比较值相同是否证明结构未变、对象仍存活、每个调用都能完成？

[CPU 缓存与伪共享](cpu-caches-locality-and-false-sharing.md)解释硬件成本；[锁与同步](locks-and-synchronization.md)说明容易组合的保护边界；[IPC 与共享所有权](ipc-channels-shared-memory-and-ownership.md)进一步加入跨进程初始化、布局和生命周期条件；[死锁与恢复](deadlocks-and-recovery.md)区分安全性和持续推进。本文中的 C++20 线程规则不能单独证明跨进程映射上的对象实现。

2026-10-22 联网核查 `cplusplus/draft` 的固定 `n4861` 源文件、N4859 版本说明、P0668R5/P0982R1 修订说明、N2480 历史解释、P0233R2 回收与进度讨论及 Linux 内核屏障文档。状态为 `source-checked`；各纸面时序、条件推导与选型建议为教学综合。未编译或执行 C++ 原子、发布、CAS、ABA、无锁算法、模型检查、硬件弱内存或性能实验；不以本站构建结果替代这些证据。
