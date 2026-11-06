<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机系统与操作系统词汇表

本页解释 18 组术语，按[完整术语索引](../glossary.md#systems)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [计算机系统与操作系统文章](../knowledge/systems/index.md)

## 本页术语

- [Process / Thread / Coroutine](#systems.execution-units)
- [Concurrency / Parallelism](#systems.concurrency)
- [Blocking / Non-blocking](#systems.blocking)
- [Context Switch](#systems.context-switch)
- [User Mode / Kernel Mode / Syscall](#systems.privilege)
- [Stack / Heap](#systems.memory-layout)
- [Virtual Memory / Paging](#systems.virtual-memory)
- [Mutex / Semaphore / CAS](#systems.synchronization)
- [Race Condition / Deadlock](#systems.race-deadlock)
- [File Descriptor / Socket](#systems.fd-socket)
- [I/O Multiplexing / epoll](#systems.io-multiplexing)
- [Memory Model / Memory Order / Happens-before](#systems.memory-order)
- [Lock-free / Wait-free / Obstruction-free](#systems.lock-free-progress)
- [Safe Memory Reclamation / Hazard Pointer / EBR / RCU](#systems.memory-reclamation)
- [Atomicity / Invariant](#systems.atomicity)
- [CPU Cache / Cache Line / Locality / False Sharing](#systems.cpu-cache)
- [Linux Signal / Signal Mask / Pending Signal](#systems.signals)
- [Interprocess Communication](#systems.ipc)

<a id="systems.execution-units"></a>

## Process / Thread / Coroutine

**ID：** `systems.execution-units` · **建议优先级：** P0

**别名 / 检索词：** Process、Thread、Coroutine、进程、线程、协程

**简释：** 进程、线程与协程，资源、执行和调度边界。

进程通常拥有独立地址空间和资源边界；线程是操作系统调度的执行流；协程由语言或库保存执行状态并调度。协程数量多不代表能同时使用更多 CPU 核心。

**例子：** 一个服务进程可有多个线程，每个线程又运行多个等待网络的协程。

**深入阅读：** [进程、线程与协程：资源边界和执行调度如何分工](../knowledge/systems/process-thread-coroutine.md) · [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.concurrency"></a>

## Concurrency / Parallelism

**ID：** `systems.concurrency` · **建议优先级：** P0

**别名 / 检索词：** Concurrency、Parallelism、并发、并行

**简释：** 并发推进与并行执行，关注调度和硬件资源。

并发描述多个任务在同一时间段内交错推进；并行描述多个任务在同一时刻实际执行。是否并行取决于可用执行资源和调度，不能只看任务数量。

**例子：** 单核上交替执行两个任务可以并发，两个核心同时执行才是并行。

**深入阅读：** [进程、线程与协程：资源边界和执行调度如何分工](../knowledge/systems/process-thread-coroutine.md)

<a id="systems.blocking"></a>

## Blocking / Non-blocking

**ID：** `systems.blocking` · **建议优先级：** P0

**别名 / 检索词：** Blocking、Non-blocking、阻塞、非阻塞

**简释：** 指定操作会不会让当前执行线程等待。

阻塞调用会在条件未满足时挂起当前线程；非阻塞调用通常立即返回结果或暂不可用状态。同步与异步描述结果交付方式，是另一条判断轴。

**例子：** 非阻塞 socket 读取暂时无数据时返回暂不可用，应用稍后再试。

**深入阅读：** [同步、异步与阻塞：先说清观察边界](../knowledge/runtime/async-and-blocking.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

<a id="systems.context-switch"></a>

## Context Switch

**ID：** `systems.context-switch` · **建议优先级：** P0

**别名 / 检索词：** Context Switch、上下文切换

**简释：** 保存和恢复执行上下文及其开销。

调度器切换执行任务时保存寄存器等上下文，再恢复另一任务。开销还可能来自缓存和地址翻译状态变化；一次系统调用不必然引起任务切换。

**例子：** 线程等待锁后被挂起，调度器让另一个就绪线程继续执行。

**深入阅读：** [上下文切换与调度等待：线程已被唤醒，为什么仍没有运行](../knowledge/systems/context-switches-run-queues-and-scheduling-delay.md)

<a id="systems.privilege"></a>

## User Mode / Kernel Mode / Syscall

**ID：** `systems.privilege` · **建议优先级：** P0

**别名 / 检索词：** User Mode、Kernel Mode、Syscall、系统调用、用户态、内核态、ABI、vDSO、特权级

**简释：** 用户态与内核态的受控入口、调用约定与返回契约，区别于线程调度。

用户态代码通过受控入口请求内核服务，调用约定规定参数、返回值和错误表达。特权级切换与调度到另一个线程是不同事件。

**例子：** 读取文件进入内核检查描述符并读取数据，成功后回到原线程。

**深入阅读：** [系统调用与权限边界：进入内核为什么不等于切换线程](../knowledge/systems/syscalls-privilege-and-return-contracts.md)

<a id="systems.memory-layout"></a>

## Stack / Heap

**ID：** `systems.memory-layout` · **建议优先级：** P0

**别名 / 检索词：** Stack、Heap、调用栈、动态分配

**简释：** 调用栈、动态分配和对象生命周期。

调用栈保存函数调用相关状态，堆用于动态分配；具体对象放在哪里由语言和实现决定。这里的堆是内存管理区域，与优先队列的堆结构不同。

**例子：** 递归过深可能耗尽调用栈；长期持有堆对象可能增加内存占用。

**深入阅读：** [栈、堆与进程内存布局：地址还在，为什么对象已经不能用](../knowledge/systems/process-memory-layout-stacks-heaps-and-lifetimes.md)

<a id="systems.virtual-memory"></a>

## Virtual Memory / Paging

**ID：** `systems.virtual-memory` · **建议优先级：** P0

**别名 / 检索词：** Virtual Memory、Paging、虚拟内存、分页、缺页、Page Fault、TLB、Copy-on-Write、写时复制

**简释：** 虚拟地址到物理页的映射、按需分页、缺页与驻留边界。

虚拟内存用页表将进程地址映射到物理页并实施访问保护；缺页由内核按原因处理。TLB 缓存地址翻译，缺页、TLB 未命中和数据缓存未命中需分别分析。

**例子：** 首次访问按需分配的页面可能触发缺页，即使系统并未读取交换区。

**深入阅读：** [虚拟内存与缺页：地址已经分配，为什么访问仍会等待](../knowledge/systems/virtual-memory-pages-and-faults.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

<a id="systems.synchronization"></a>

## Mutex / Semaphore / CAS

**ID：** `systems.synchronization` · **建议优先级：** P0

**别名 / 检索词：** Mutex、Semaphore、CAS、互斥锁、信号量、比较交换

**简释：** 互斥、资源计数与原子比较交换。

Mutex 保护互斥临界区；Semaphore 维护可获取的许可数量；CAS 按预期旧值执行原子更新。单个 CAS 成功不自动保证多字段业务不变量。

**例子：** 用信号量限制最多十个并发任务，用互斥锁保护共享映射更新。

**深入阅读：** [锁与同步原语：保护范围比加锁动作更重要](../knowledge/systems/locks-and-synchronization.md) · [竞态与原子性：每一步成功，结果为什么仍然错](../knowledge/systems/races-and-atomicity.md) · [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.race-deadlock"></a>

## Race Condition / Deadlock

**ID：** `systems.race-deadlock` · **建议优先级：** P0

**别名 / 检索词：** Race Condition、Deadlock、竞态条件、死锁

**简释：** 时序依赖错误与循环等待。

竞态条件使结果依赖未受约束的执行时序；死锁使参与者互相等待无法推进。修复要围绕状态转换、锁顺序和失败恢复，而非只增加锁数量。

**例子：** 两个线程以相反顺序持有两把锁，可能形成循环等待。

**深入阅读：** [竞态与原子性：每一步成功，结果为什么仍然错](../knowledge/systems/races-and-atomicity.md) · [死锁与失败恢复：等待为什么无法自行结束](../knowledge/systems/deadlocks-and-recovery.md)

<a id="systems.fd-socket"></a>

## File Descriptor / Socket

**ID：** `systems.fd-socket` · **建议优先级：** P0

**别名 / 检索词：** File Descriptor、Socket、文件描述符、打开文件描述、Open File Description、dup、CLOEXEC、套接字

**简释：** 描述符编号引用打开状态及底层对象，需区分偏移共享、关闭与编号复用；Socket 为通信端点。

文件描述符是进程表中的编号，经打开文件描述引用底层对象；复制的描述符可能共享文件偏移。Socket 是通信端点，关闭编号不代表所有引用或远端工作已结束。

**例子：** dup 得到的新描述符可与原描述符共享文件读取偏移。

**深入阅读：** [文件描述符与打开文件描述：关掉一个编号，资源为什么仍在](../knowledge/systems/file-descriptors-and-open-file-descriptions.md) · [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

<a id="systems.io-multiplexing"></a>

## I/O Multiplexing / epoll

**ID：** `systems.io-multiplexing` · **建议优先级：** P0

**别名 / 检索词：** I/O Multiplexing、epoll、I/O 多路复用、就绪通知、Readiness、select、poll、LT、ET、IO 多路复用

**简释：** 监视多个 I/O 就绪条件，应用仍需非阻塞操作、状态保存及公平推进。

多路复用接口报告哪些端点满足就绪条件；就绪不等于完整业务消息已经到达。应用仍需处理部分读写、暂不可用、连接状态和公平调度。

**例子：** epoll 通知可读后，服务端仍需解析长度并等待尚未到达的消息体。

**深入阅读：** [I/O 多路复用与就绪通知：一个线程怎样等待多个连接](../knowledge/systems/io-multiplexing-readiness-and-event-loops.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

<a id="systems.memory-order"></a>

## Memory Model / Memory Order / Happens-before

**ID：** `systems.memory-order` · **建议优先级：** P0

**别名 / 检索词：** Memory Model、Happens-before、内存模型、Memory Order、内存顺序

**简释：** 语言内存模型规定并发访问的合法性、可见性和排序，发布必须满足对应同步关系。

不同语言分别定义数据竞争与同步。原子访问保护指定操作，较弱顺序不自动发布其他字段；release/acquire 等规则还取决于读取来自哪次写入。时间先后、休眠和硬件缓存一致性不能替代语言同步。

**例子：** C++20 的一次性发布中，先写普通载荷再 release 写就绪标志；消费者 acquire 读自该发布后再读载荷，并保证载荷不再被改写且对象仍存活。

**深入阅读：** [竞态与原子性：每一步成功，结果为什么仍然错](../knowledge/systems/races-and-atomicity.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md) · [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

<a id="systems.lock-free-progress"></a>

## Lock-free / Wait-free / Obstruction-free

**ID：** `systems.lock-free-progress` · **建议优先级：** P0

**别名 / 检索词：** Lock-free、Wait-free、Obstruction-free、无锁算法、无等待算法

**简释：** 按独占执行、整体完成与单次自身步骤区分并发算法进度，并与正确性和墙钟时限分别判断。

Obstruction-free 要求足够独占步骤下完成，lock-free 关注整体持续完成，wait-free 要求每次操作在有限自身步骤内完成。原子类型属性不覆盖分配、回调与回收，算法进度也不保证线程及时获得 CPU。

**例子：** 两个参与者反复竞争 CAS，一个持续成功而另一个一直重试，可能符合整体进度，却不能据此证明单个调用不饥饿。

**深入阅读：** [无锁算法与进度保证：系统还在推进，为什么我的操作一直失败](../knowledge/systems/lock-free-algorithms-linearization-and-progress.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.memory-reclamation"></a>

## Safe Memory Reclamation / Hazard Pointer / EBR / RCU

**ID：** `systems.memory-reclamation` · **建议优先级：** P0

**别名 / 检索词：** Safe Memory Reclamation、Hazard Pointer、Epoch-based Reclamation、EBR、RCU、ABA、安全内存回收、危险指针

**简释：** 移除后延迟回收，直到读者保护、静止点或宽限期协议证明旧对象不会再被使用。

Hazard Pointer 登记并验证对象保护，EBR 依赖参与者时代与静止条件，RCU 按相应读取临界区与宽限期协调。地址复用、逻辑 ABA、对象寿命和结构正确性分别证明；基础 EBR 的停滞可能保留大量退役对象。

**例子：** 根从 A 换成 B 后，旧读者仍握着 A；先退役再等待协议允许回收，不能只凭根已更新立即释放。

**深入阅读：** [ABA 与安全内存回收：节点已经移除，什么时候才能真正释放](../knowledge/systems/safe-memory-reclamation-aba-hazards-and-epochs.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.atomicity"></a>

## Atomicity / Invariant

**ID：** `systems.atomicity` · **建议优先级：** P0

**别名 / 检索词：** Atomicity、Invariant、原子性、不变量

**简释：** 点名不可分割的状态转换边界，并检验允许交错下必须保持的业务条件。

原子性必须点名操作边界：一个读改写、一个临界区或一个事务。业务不变量则描述所有允许状态都应满足的条件，局部原子步骤仍可能组合出错误。

**例子：** 余额检查与扣款必须共同维护余额不为负，不能只让单次赋值原子化。

**深入阅读：** [竞态与原子性：每一步成功，结果为什么仍然错](../knowledge/systems/races-and-atomicity.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.cpu-cache"></a>

## CPU Cache / Cache Line / Locality / False Sharing

**ID：** `systems.cpu-cache` · **建议优先级：** P0

**别名 / 检索词：** CPU 缓存、缓存行、局部性、时间局部性、空间局部性、伪共享、Working Set

**简释：** 用缓存行和访问模式解释层级命中与工作集，区分数据缓存、地址翻译、缺页及共享写入的一致性成本。

CPU 缓存通常以缓存行为单位搬运数据；时间和空间局部性影响命中。不同核心写同一缓存行中的不同变量也可能引起一致性流量，称为伪共享。

**例子：** 相邻计数器分属不同线程频繁更新，可能因共享缓存行而互相拖慢。

**深入阅读：** [CPU 缓存与局部性：数据已在内存，访问为什么仍然慢](../knowledge/systems/cpu-caches-locality-and-false-sharing.md) · [内存顺序与原子操作：读到标志之后，怎样才算完成发布](../knowledge/systems/memory-order-atomics-and-publication.md)

<a id="systems.signals"></a>

## Linux Signal / Signal Mask / Pending Signal

**ID：** `systems.signals` · **建议优先级：** P1

**别名 / 检索词：** Linux Signal、POSIX Signal、Linux 信号、POSIX 信号、信号掩码、待决信号

**简释：** 区分进程共享的信号处置、线程独立掩码与待决状态，用受控接收把通知连接到应用停止协议。

进程定向信号可递送给一个未屏蔽线程，标准信号待决期间的同类实例可能合并。处理函数受异步信号安全约束，sigwait/signalfd 可将服务停止通知接到普通执行路径；取消请求仍需安全边界、清理责任和结束确认。

**例子：** 创建工作线程前屏蔽 SIGTERM，由控制线程同步接收后停止接纳并通知工作线程，按总期限汇总完成或结果未知的工作。

**深入阅读：** [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md)

<a id="systems.ipc"></a>

## Interprocess Communication

**ID：** `systems.ipc` · **建议优先级：** P1

**别名 / 检索词：** IPC、Interprocess Communication、Inter-process Communication、进程间通信

**简释：** 在进程边界间传递字节、消息或访问共享存储，需要同时约定边界、容量、结束与所有权。

管道和流 socket 需要应用分帧，消息接口保留记录但仍有大小与容量限制；共享内存将访问布局、同步、初始化、复用和崩溃恢复交给参与者协议。通知、传输结束和业务完成是不同条件。

**例子：** 父进程读子进程管道时必须关闭自己多余的写端，否则子进程退出后仍可能等不到 EOF；改用共享槽位后还要明确发布和归还时机。

**深入阅读：** [进程间通信：选通道之前，先确定边界与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Linux 内核：虚拟内存与页](https://docs.kernel.org/admin-guide/mm/concepts.html)
- [Linux man-pages：信号递送、待决与中断](https://man7.org/linux/man-pages/man7/signal.7.html)
- [Linux man-pages：异步信号安全](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [Linux man-pages：同步接收信号](https://man7.org/linux/man-pages/man3/sigwait.3.html)
- [Linux man-pages：管道与 EOF/写入边界](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [Linux man-pages：Unix 域 socket](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Linux man-pages：POSIX 共享内存](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [C++20 公开草案 N4861：固定版本原子库源文件](https://github.com/cplusplus/draft/blob/n4861/source/atomics.tex)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
