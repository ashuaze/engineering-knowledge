<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机系统与操作系统

建议优先级：P0。目标：解释[进程](../../glossary/systems.md#systems.execution-units)、内存、同步与 I/O，定位资源等待。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

一个服务为何 CPU 不高，却不再处理请求？

## 已有正文

- [上下文切换与调度等待：线程已被唤醒，为什么仍没有运行](context-switches-run-queues-and-scheduling-delay.md)：区分运行、就绪与睡眠，解释任务切换、权限入口、CPU 迁移和协程切换的范围，以及切换次数与调度[延迟](../../glossary/performance.md#performance.latency-throughput)的不同证据。
- [CPU 缓存与局部性：数据已在内存，访问为什么仍然慢](cpu-caches-locality-and-false-sharing.md)：解释缓存层级、[缓存行](../../glossary/systems.md#systems.cpu-cache)、工作集与访问顺序，区分未命中、[缺页](../../glossary/systems.md#systems.virtual-memory)、伪共享和程序同步责任。
- [死锁与失败恢复：等待为什么无法自行结束](deadlocks-and-recovery.md)：用等待关系区分[死锁](../../glossary/systems.md#systems.race-deadlock)、竞争与超时，说明锁顺序、数据库回滚和有边界重试的分工。
- [文件描述符与打开文件描述：关掉一个编号，资源为什么仍在](file-descriptors-and-open-file-descriptions.md)：区分描述符编号、[打开文件描述](../../glossary/systems.md#systems.fd-socket)与底层对象，解释 dup/fork 共享、编号复用、关闭和继承的边界。
- [I/O 多路复用与就绪通知：一个线程怎样等待多个连接](io-multiplexing-readiness-and-event-loops.md)：比较 [select](../../glossary/systems.md#systems.io-multiplexing)、poll、epoll 的等待接口，解释就绪与完成、LT/ET、[非阻塞](../../glossary/systems.md#systems.blocking)、部分读写和公平调度。
- [进程间通信：选通道之前，先确定边界与所有权](ipc-channels-shared-memory-and-ownership.md)：比较管道、Unix 域 socket、消息队列和共享内存，说明消息边界、结束、[背压](../../glossary/performance.md#performance.queueing)与共享对象生命周期的责任。
- [无锁算法与进度保证：系统还在推进，为什么我的操作一直失败](lock-free-algorithms-linearization-and-progress.md)：区分线性化正确性、整体进度与单次完成，解释 [lock-free](../../glossary/systems.md#systems.lock-free-progress)、wait-free、[CAS](../../glossary/systems.md#systems.synchronization) 重试、帮助机制和端到端依赖的证明范围。
- [锁与同步原语：保护范围比加锁动作更重要](locks-and-synchronization.md)：区分互斥、计数准入与条件等待，解释线程锁、协程锁和数据库锁各自的保护范围。
- [内存顺序与原子操作：读到标志之后，怎样才算完成发布](memory-order-atomics-and-publication.md)：固定以 C++20 为范围，区分数据竞争、[原子性](../../glossary/systems.md#systems.atomicity)和跨对象排序，推演发布条件、CAS 重试、[ABA](../../glossary/systems.md#systems.memory-reclamation) 与进度保证。
- [栈、堆与进程内存布局：地址还在，为什么对象已经不能用](process-memory-layout-stacks-heaps-and-lifetimes.md)：区分虚拟映射、分配器存储与语言对象寿命，解释线程栈、[动态分配](../../glossary/systems.md#systems.memory-layout)、悬空引用和释放后 RSS，以及布局观测能证明的范围。
- [进程、线程与协程：资源边界和执行调度如何分工](process-thread-coroutine.md)：区分[资源隔离](../../glossary/devops.md#devops.isolation)、执行线程与可挂起任务，解释[并发](../../glossary/systems.md#systems.concurrency)为什么不自动带来并行。
- [竞态与原子性：每一步成功，结果为什么仍然错](races-and-atomicity.md)：从共享状态、操作交错和[业务不变量](../../glossary/architecture.md#architecture.domain-model)出发，区分单步原子、流程正确性与事务保证。
- [ABA 与安全内存回收：节点已经移除，什么时候才能真正释放](safe-memory-reclamation-aba-hazards-and-epochs.md)：区分发布、移除、退役与回收，解释地址复用和逻辑 ABA，比较 Hazard Pointer、Epoch 与 RCU 的读者保护、停滞和容量边界。
- [Linux 信号、取消与退出：收到停止请求后由谁完成清理](signals-cancellation-and-shutdown.md)：区分信号处置、线程掩码、待决与同步接收，把停止通知连接到有期限、可确认的退出责任。
- [系统调用与权限边界：进入内核为什么不等于切换线程](syscalls-privilege-and-return-contracts.md)：区分库函数、[系统调用](../../glossary/systems.md#systems.privilege) ABI、权限切换与线程调度，解释短读写、错误返回和调用成功的边界。
- [虚拟内存与缺页：地址已经分配，为什么访问仍会等待](virtual-memory-pages-and-faults.md)：区分虚拟地址、物理页、页表与驻留内存，解释按需分页、缺页、写时复制和工作集压力。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Process / Thread / Coroutine](../../glossary/systems.md#systems.execution-units) | 进程、线程与协程，资源、执行和调度边界。 |
| [Concurrency / Parallelism](../../glossary/systems.md#systems.concurrency) | 并发推进与并行执行，关注调度和硬件资源。 |
| [Blocking / Non-blocking](../../glossary/systems.md#systems.blocking) | 指定操作会不会让当前执行线程等待。 |
| [Context Switch](../../glossary/systems.md#systems.context-switch) | 保存和恢复执行上下文及其开销。 |
| [User Mode / Kernel Mode / Syscall](../../glossary/systems.md#systems.privilege) | 用户态与内核态的受控入口、调用约定与返回契约，区别于线程调度。 |
| [Stack / Heap](../../glossary/systems.md#systems.memory-layout) | 调用栈、动态分配和对象生命周期。 |
| [Virtual Memory / Paging](../../glossary/systems.md#systems.virtual-memory) | 虚拟地址到物理页的映射、按需分页、缺页与驻留边界。 |
| [Mutex / Semaphore / CAS](../../glossary/systems.md#systems.synchronization) | 互斥、资源计数与原子比较交换。 |
| [Race Condition / Deadlock](../../glossary/systems.md#systems.race-deadlock) | 时序依赖错误与循环等待。 |
| [File Descriptor / Socket](../../glossary/systems.md#systems.fd-socket) | 描述符编号引用打开状态及底层对象，需区分偏移共享、关闭与编号复用；Socket 为通信端点。 |
| [I/O Multiplexing / epoll](../../glossary/systems.md#systems.io-multiplexing) | 监视多个 I/O 就绪条件，应用仍需非阻塞操作、状态保存及公平推进。 |
| [Memory Model / Memory Order / Happens-before](../../glossary/systems.md#systems.memory-order) | 语言内存模型规定并发访问的合法性、可见性和排序，发布必须满足对应同步关系。 |
| [Lock-free / Wait-free / Obstruction-free](../../glossary/systems.md#systems.lock-free-progress) | 按独占执行、整体完成与单次自身步骤区分并发算法进度，并与正确性和墙钟时限分别判断。 |
| [Safe Memory Reclamation / Hazard Pointer / EBR / RCU](../../glossary/systems.md#systems.memory-reclamation) | 移除后延迟回收，直到读者保护、静止点或宽限期协议证明旧对象不会再被使用。 |
| [Atomicity / Invariant](../../glossary/systems.md#systems.atomicity) | 点名不可分割的状态转换边界，并检验允许交错下必须保持的业务条件。 |
| [CPU Cache / Cache Line / Locality / False Sharing](../../glossary/systems.md#systems.cpu-cache) | 用缓存行和访问模式解释层级命中与工作集，区分数据缓存、地址翻译、缺页及共享写入的一致性成本。 |
| [Linux Signal / Signal Mask / Pending Signal](../../glossary/systems.md#systems.signals) | 区分进程共享的信号处置、线程独立掩码与待决状态，用受控接收把通知连接到应用停止协议。 |
| [Interprocess Communication](../../glossary/systems.md#systems.ipc) | 在进程边界间传递字节、消息或访问共享存储，需要同时约定边界、容量、结束与所有权。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
