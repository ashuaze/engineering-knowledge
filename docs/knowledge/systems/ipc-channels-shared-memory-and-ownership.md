---
id: "kb-systems-ipc"
title: "进程间通信：选通道之前，先确定边界与所有权"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "比较管道、Unix 域 socket、消息队列和共享内存，说明消息边界、结束、背压与共享对象生命周期的责任。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-systems-file-descriptors"]
related: ["kb-systems-synchronization", "kb-systems-io-multiplexing", "kb-systems-signals-shutdown", "kb-systems-virtual-memory", "kb-systems-memory-order", "kb-performance-backpressure", "kb-messaging-delivery-semantics"]
tags: ["ipc", "linux", "shared-memory", "ownership"]
---

# 进程间通信：选通道之前，先确定边界与所有权

学习入口：子[进程](../../glossary/systems.md#systems.execution-units)已经退出，父进程为什么还等不到管道 EOF？把大对象改放共享内存后，为什么消费者可能读到半成品？[进程间通信](../../glossary/systems.md#systems.ipc)（IPC）既要传递数据，也要约定谁能修改、何时可读、怎样结束。选择通道时应同时回答这几件事。

前置：[进程与线程](process-thread-coroutine.md)、[文件描述符与引用](file-descriptors-and-open-file-descriptions.md)。本文以 Linux man-pages 6.19 所描述的接口为范围；涉及 POSIX 共享原语时点名属性要求。讨论同一主机上协作进程的契约，不提供可直接投产的共享内存[队列](../../glossary/algorithms.md#algorithms.queues)，也不声称某通道普遍更快。

## 先区分传字节、传消息和共同访问状态

| 通道 | 交付给接收方的单位 | 适合从什么需求出发 | 应用仍须负责 |
| --- | --- | --- | --- |
| 管道、命名管道 FIFO | 单向字节流 | 父子进程流水线，或通过路径连接生产者与消费者 | 分帧、关闭多余端点、容量与退出 |
| Unix 域 `SOCK_STREAM` | 双向字节流 | 本机请求/响应、需要独立读写方向的会话 | 分帧、身份与权限、会话状态 |
| Unix 域 `SOCK_DGRAM` / `SOCK_SEQPACKET` | 保留消息边界的记录 | 希望每次接收对应一条消息；后者还提供连接和有序记录 | 最大消息、接收缓冲、截断与业务确认 |
| POSIX 消息队列 | 带优先级的消息 | 需要命名队列、消息大小和队列容量约束 | 优先级策略、删除时机、消费后失败的处理 |
| POSIX 共享内存 | 映射到各进程地址空间的一块存储 | 大块数据需要被多个参与者访问 | 数据布局、同步、初始化、所有权与回收 |

接口依据分别见 [pipe(7)](https://man7.org/linux/man-pages/man7/pipe.7.html)、[unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html)、[mq_overview(7)](https://man7.org/linux/man-pages/man7/mq_overview.7.html)及 [shm_overview(7)](https://man7.org/linux/man-pages/man7/shm_overview.7.html)。Unix 域 [socket](../../glossary/systems.md#systems.fd-socket) 还可传递描述符引用；传递整数编号本身没有这个效果，接收方得到的也不是发送方描述符表中的同一编号。

这里的消息队列是本机内核 IPC 接口。其对象可在进程退出后继续存在，但这种内核持存不等于跨主机消息服务或断电后持久日志。POSIX 队列按高优先级先取，同优先级再取最早的消息，不能默认所有消息都按全局入队顺序消费；见 [mq_receive(3)](https://man7.org/linux/man-pages/man3/mq_receive.3.html)。

选型建议来自上述边界的综合：先用能明确表达协议的通道；只有在数据复制、容量或访问模式确实成为问题时，再评估共享内存。共享存储使双方看见同一份状态，也把原来通过消息交付隔开的修改责任带到双方之间。

## 字节流里的一个写入，不是一条接收消息

管道和流 socket 都需要应用定义消息边界。发送方先写请求 A，再写请求 B，接收方可能一次只拿到 A 的前缀，也可能一次拿到 A 和 B。管道中不超过 `PIPE_BUF` 的一次写入可防止其他写者的数据插入这次写入，但不会使接收端每次读取都返回相同长度；写入原子边界与读取消息边界是两回事。[pipe(7) 的字节流及 `PIPE_BUF` 规则](https://man7.org/linux/man-pages/man7/pipe.7.html)给出了这两个不同保证。

下面是纸面协议，不是已执行实现：每帧使用 4 字节大端长度加消息体，长度上限假设为 64 KiB。本例假定单个有序写入者；多个写者共享字节流时，必须在所有写者之间串行化整帧的发送，包括短写后的续传，或另行设计满足接口约束的记录协议。长度头不能修复已经交错的字节，也不能把管道的 `PIPE_BUF` 保证推广到流 socket。解析器保存未处理后缀，凑齐头部后先校验长度，再等待消息体；完成一帧后继续解析余下字节。上限是教学选择，真实协议还要约定版本、空消息、整数溢出与非法输入的处理。

```text
发送内容： [长度=3][abc][长度=2][de]
读取一次： [长度=3][a]          → 保存半帧
再读一次： [bc][长度=2][de]    → 交付 abc，再交付 de
```

若接收方把第一次读到的 `a` 当作完整请求，或者只取 `abc` 后丢弃后缀，就破坏了自己的协议。EOF 出现在未完成的帧中，也应按协议识别为截断，不能把剩余字节悄悄当成一条完整消息。

有消息边界也不免除长度检查。消息 socket 的接收缓冲不足时可能丢掉消息尾部，应核对返回长度和 `recvmsg` 的 `MSG_TRUNC` 等结果；不能总是假定剩余部分留给下一次读取。POSIX `mq_receive` 则要求缓冲至少达到队列配置的 `mq_msgsize`，不足会报错。两种 API 的失败方式不同，依据见 [recv(2)](https://man7.org/linux/man-pages/man2/recv.2.html)与 [mq_receive(3)](https://man7.org/linux/man-pages/man3/mq_receive.3.html)。

## 没数据、结束、完成业务分别怎样表达

对管道，缓冲数据读完且所有写端引用都关闭后，读取才返回 0 表示 EOF。某个生产者退出，不证明其他继承或复制的写端已关闭。纸面反例：父进程启动子进程后保留了自己不再使用的写端，随后一直读；子进程退出后，这个剩余写端仍使读者等待。修复点是端点所有权和关闭路径，见 [pipe(7) 的 EOF 规则](https://man7.org/linux/man-pages/man7/pipe.7.html)及[描述符生命周期](file-descriptors-and-open-file-descriptions.md)。[非阻塞](../../glossary/systems.md#systems.blocking)读取暂时不可用也不能当作 EOF；所有读端关闭后，写者还需处理 `SIGPIPE` / `EPIPE`。

全双工流 socket 的两个方向可分别结束。`shutdown(fd, SHUT_WR)` 禁止继续发送，仍可保留接收方向；它与释放一个描述符的 `close` 不是同一操作。一个“发送完请求后半关闭，再等响应”的协议，需要继续读取响应直到其完成条件满足。依据见 [shutdown(2)](https://man7.org/linux/man-pages/man2/shutdown.2.html)；流 socket 的有序关闭返回规则见 [recv(2)](https://man7.org/linux/man-pages/man2/recv.2.html)。不要把这个 EOF 判定直接用于允许零长度消息的数据报接口。

结束通道只表达传输状态。发送成功、接收成功和业务提交是三种结果：接收者可能取出消息后尚未处理就崩溃。若发送者必须知道工作是否完成，应在协议中增加请求标识、确认与失败恢复；本机 IPC 没有替应用生成这套保证。可结合[消息投递与确认](../messaging/delivery-acknowledgements-and-idempotency.md)分析重复和结果未知。

## 背压必须延伸到生产者

通道容量有限。写满管道或发满 POSIX 队列时，操作会按接口和标志等待，或以 `EAGAIN` 等结果报告暂不可用；POSIX 队列还提供有期限的发送。依据见 [pipe(7)](https://man7.org/linux/man-pages/man7/pipe.7.html)与 [mq_send(3)](https://man7.org/linux/man-pages/man3/mq_send.3.html)。换成非阻塞调用只改变当前调用如何返回，不会增加消费者的处理能力。

应用应规定满载后是暂停生产、拒绝新工作、在期限内等待，还是按业务允许的策略丢弃。若每次 `EAGAIN` 都把数据塞进另一条无界内存队列，限制只是从内核移到了应用内存。重试也必须保留未发送部分，不能把一条大帧从头重发而重复已接受字节；相关状态机见 [I/O 多路复用](io-multiplexing-readiness-and-event-loops.md)。

纸面推演：假设生产者每秒产生 120 条，消费者每秒处理 100 条；持续一分钟就多出 1200 条等待项。加大缓冲只延后容量耗尽；要维持有界状态，需要降低接纳量或明确舍弃规则。数字是教学假设，没有测量任何 IPC 吞吐。继续阅读[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。

## 共享内存需要四份独立约定

POSIX 共享内存通常经过 `shm_open`、设置对象大小、`mmap` 建立映射。需要共同修改时核对 `MAP_SHARED`，不能把 `MAP_PRIVATE` 的[写时复制](../../glossary/systems.md#systems.virtual-memory)当成共同更新；不同进程的映射基址也未必相同。跨进程布局应表达可校验的偏移、长度与版本，不能直接把一个进程的普通指针值当成另一个进程可解引用的地址。接口机制见 [shm_overview(7)](https://man7.org/linux/man-pages/man7/shm_overview.7.html)和 [mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html)。

| 协议责任 | 必须明确的规则 | 缺失后的失败例 |
| --- | --- | --- |
| 初始化与加入 | 谁创建、何时初始化完成、加入者如何校验版本和容量 | 加入者在头部尚未完成时就解释偏移 |
| 修改与交付 | 谁独占某槽位，何时从“写入中”转为“可读取” | 消费者读到新长度配旧内容 |
| 复用与退出 | 读者何时归还，停止时如何确认无人仍在访问 | 生产者复用仍被消费者引用的槽位 |
| 崩溃与恢复 | 如何识别未完成操作，谁有权重建或放弃这一代对象 | 新进程接着使用上一代的半成品 |

这张表是教学设计检查项，不是 POSIX 自动提供的状态机。即使每个长度字段都用原子变量，多字段组合、对象有效期与恢复责任仍需另行证明。

同步对象也要能跨进程共享。例如 POSIX [mutex](../../glossary/systems.md#systems.synchronization) 默认是 `PTHREAD_PROCESS_PRIVATE`；跨进程使用需初始化为 `PTHREAD_PROCESS_SHARED`，并让参与者访问同一共享存储中的对象。未命名信号量则需要合适的 `pshared` 参数并位于共享内存；不能让每个加入者各自重新初始化正在使用的同步对象。依据见 [pthread_mutexattr_getpshared(3)](https://man7.org/linux/man-pages/man3/pthread_mutexattr_getpshared.3.html)和 [sem_init(3)](https://man7.org/linux/man-pages/man3/sem_init.3.html)。语言对象的构造、布局及跨进程原子操作还需实现支持；不能仅凭“放在共享页上”推导出可移植的 C++ 无锁结构。

`close`、解除映射和删除名称也各有边界：映射建立后可关闭用于建立映射的描述符；`munmap` 撤销当前映射；`shm_unlink` 删除名称，已有映射的使用者不会因此立即失去映射。同名对象若随后被重新创建，会成为不同对象，老进程和新进程可能分属两代。生命周期依据见 [shm_open(3)](https://man7.org/linux/man-pages/man3/shm_open.3.html)。因此清理者必须区分名称、对象这一代身份和仍存活的引用。

若持锁进程崩溃，普通互斥不能代替恢复协议。即使用 robust mutex 收到 `EOWNERDEAD` 并获得锁，应用仍要检查并修复受保护状态，才能按接口标记为一致；不会自动恢复半次写入。见 [POSIX pthread_mutex_lock](https://man7.org/linux/man-pages/man3/pthread_mutex_lock.3p.html)。

## 通知指出需要查看状态，不能替代状态协议

Linux `eventfd` 提供内核计数器与可等待描述符；默认模式一次读取可取得累计值并清零，因而一次唤醒不必对应一条业务消息。其契约见 [eventfd(2)](https://man7.org/linux/man-pages/man2/eventfd.2.html)。实际有多少工作、是否已完整发布，应由受保护的队列或状态记录回答。

纸面协议可以是“生产者在跨进程 mutex 下完成槽位与队列状态更新，释放锁后通知；消费者醒来后取得同一 mutex，再检查队列”。这里同步依据来自共享锁协议，通知负责使等待者重新检查。某些通知原语本身也包含同步语义，必须按具体接口核对；不能仅凭收到了某种事件，就证明任意语言的普通字段访问已经满足同步要求。更不能把“先通知、后填写数据”当作交付顺序。

还需解决检查与休眠之间的窗口：消费者刚检查为空，生产者就发布，随后消费者才睡眠。选择条件等待、计数通知或其他方案时，要说明这个通知如何保留、等待如何注册，以及怎样再次检查谓词。共享内存的访问排序继续见[内存顺序与发布](memory-order-atomics-and-publication.md)，条件谓词与互斥关系见[锁与同步原语](locks-and-synchronization.md)。

## 自检、关联与核查范围

- 一次写入不会被别的写者插入字节，为何接收方仍需要分帧？接收缓冲不足在流和消息接口上分别意味着什么？
- 生产者退出后谁还持有写端？“暂时没数据”“发送方向结束”“业务处理完成”分别由什么证据说明？
- 共享槽位由谁初始化、发布、归还和回收？通知丢失或持锁进程崩溃时，谁能使状态重新收敛？

[虚拟内存](virtual-memory-pages-and-faults.md)解释共同存储与各自地址空间的关系；[信号与退出](signals-cancellation-and-shutdown.md)连接控制通知和资源归还；[内存顺序](memory-order-atomics-and-publication.md)区分原子字段与合法发布。它们共同约束 IPC 的生命周期，不能由某一种通信 API 单独替代。

2026-10-22 联网核查上述 Linux man-pages 6.19，以及页面所引 POSIX mutex [接口契约](../../glossary/api.md#api.contracts)，覆盖通道类型、边界、结束、容量、共享映射与同步对象生命周期。状态为 `source-checked`；选型建议、帧格式、容量数字和所有权表为教学综合。未编译或运行 IPC、消息截断、半关闭、共享内存、robust mutex、崩溃恢复或性能实验。
