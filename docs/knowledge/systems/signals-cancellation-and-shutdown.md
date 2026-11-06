---
id: "kb-systems-signals-shutdown"
title: "Linux 信号、取消与退出：收到停止请求后由谁完成清理"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分信号处置、线程掩码、待决与同步接收，把停止通知连接到有期限、可确认的退出责任。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-systems-syscalls"]
related: ["kb-systems-synchronization", "kb-systems-file-descriptors", "kb-systems-io-multiplexing", "kb-reliability-retry-budgets", "kb-devops-declarative-health"]
tags: ["linux", "signals", "cancellation", "shutdown"]
---

# Linux 信号、取消与退出：收到停止请求后由谁完成清理

学习入口：服务收到 SIGTERM 后，为什么有时直接结束，有时卡在退出，甚至在“清理日志”时[死锁](../../glossary/systems.md#systems.race-deadlock)？信号提供控制通知，清理和业务收尾需要应用协议。前置：[进程与线程](process-thread-coroutine.md)、[系统调用返回契约](syscalls-privilege-and-return-contracts.md)。本文以 Linux man-pages 6.19 描述的 POSIX [线程](../../glossary/systems.md#systems.execution-units)接口为参照，讨论普通服务的主动停止；不把内存破坏等崩溃信号当成可安全恢复的停机请求。

## 处置、掩码与待决分别属于谁

[Linux 信号](../../glossary/systems.md#systems.signals)是内核与进程、进程之间传递事件或控制请求的机制。是否结束、忽略或进入处理函数，由该信号的处置方式决定。SIGTERM 默认终止进程；安装处理函数只改变收到它后的动作，不会自动创建排空流程。处置可通过 [sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html)设置，SIGKILL、SIGSTOP 则不能被捕获、忽略或屏蔽。

| 状态 | 所属范围 | 需要避免的混淆 |
| --- | --- | --- |
| 处置方式 disposition | 同一进程的线程共享 | 不能为同一信号给每个线程各装一套独立处置 |
| 信号掩码 mask | 每个线程独立 | 主线程屏蔽，不等于既有工作线程也已屏蔽 |
| 待决 pending | 可针对进程或特定线程 | 尚未递送，不代表已经进入清理逻辑 |

掩码表示当前阻止哪些信号按通常方式递送。多线程程序使用 [pthread_sigmask(3)](https://man7.org/linux/man-pages/man3/pthread_sigmask.3.html)；新线程继承创建者当时的掩码副本，以后修改一个线程的掩码不会同步修改其他线程。待决集可用 [sigpending(2)](https://man7.org/linux/man-pages/man2/sigpending.2.html)观察，但这个快照不是业务取消状态，也不能替代同步协议。

发给进程的信号通常递送给一个未屏蔽它的线程，不保证是主线程。发给特定线程的信号则以该线程为目标。对同一个进程待决集或线程待决集，同一种标准信号待决期间再产生多次，通常仍只有一个待决实例。因此不能用 SIGTERM 的接收次数充当可靠的工作计数；依据见 [signal(7) 的递送与排队语义](https://man7.org/linux/man-pages/man7/signal.7.html)。

由此得到一个工程判断：把“服务需要停止”建模为可重复提交的状态转换，比把每次信号都解释成一项必须执行的清理命令更合适。需要可靠的多条控制消息、顺序或业务确认时，应另选有明确契约的通信通道。

## 异步处理函数为什么应当很小

处理函数可能插入被递送线程的执行路径；此时库内部状态或应用临界区可能只更新到一半。线程安全并不等于异步信号安全：一个可由不同线程调用的函数，仍可能在处理函数重入同一内部锁时卡住。printf 一类 stdio 操作、分配内存和普通[互斥锁](../../glossary/systems.md#systems.synchronization)操作，都不能因“平时线程安全”就直接放入这里。应按 [signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html)核对允许操作，并单独保护被访问的状态。

纸面反例：工作线程持有日志库的锁 → SIGTERM 在该线程触发处理函数 → 处理函数调用日志库 → 再次等待同一把锁。被打断的代码无法先返回释放锁，所谓“退出前记录一下”反而阻断退出。换成另一种日志格式不能修复这个等待关系。

即使采用“只记录停止标志”的处理函数，也要解决共享状态的合法访问和等待者唤醒。只写标志不会自动唤醒正在等 I/O 或条件变量的线程；仅靠 volatile 也不能代替完整的跨线程同步。本文选择下面的同步接收方案解释责任，不给出未经执行的 C 处理函数。

## 同步接收，把停机决策带回普通执行上下文

对由进程接收的 SIGTERM、SIGINT，可以在创建工作线程之前统一屏蔽，再用专门线程调用 [sigwait(3)](https://man7.org/linux/man-pages/man3/sigwait.3.html)。信号到达后，sigwait 消费相应待决实例并返回信号编号；随后是普通线程代码，可以按正常同步规则提交停止状态。等待这些信号时仍保持屏蔽，不是先解除屏蔽再等。

```text
教学架构，非可运行程序：
启动线程屏蔽停止信号 → 创建继承掩码的工作线程
控制线程 sigwait → 提交停止状态并唤醒相关等待者
工作线程到达安全边界 → 清理自己拥有的资源 → 报告结束
退出协调者等待完成或达到总期限 → 决定最终退出方式
```

Linux 的 [signalfd(2)](https://man7.org/linux/man-pages/man2/signalfd.2.html)则把信号读取接到[文件描述符](../../glossary/systems.md#systems.fd-socket)上，可与 [poll](../../glossary/systems.md#systems.io-multiplexing)/epoll 等待组合。相应信号通常仍需屏蔽，避免先走默认处置或处理函数。读取线程能接收发给进程或它自己的信号，不能替其他线程读取定向信号；硬件异常产生的同步信号也不应交给这种服务停止通道。

两种方案都要求整个进程协调掩码与接收者。若某个库预先创建的线程仍未屏蔽 SIGTERM，它可能先成为递送目标；若多个控制线程等待同一集合，也不能假定每个线程都会收到副本。选择前要核对 [Runtime](../../glossary/runtime.md#runtime.virtual-machine)、库与宿主进程是否已经管理这些信号。同步接收解决执行上下文问题，退出顺序仍由应用负责。

## 取消请求和已经停止是两个结果

向特定线程发送信号，不等于只终止那个线程。[pthread_kill(3)](https://man7.org/linux/man-pages/man3/pthread_kill.3.html)明确指出，若处置是终止、停止或继续，影响的是整个进程。用它“杀掉卡住的工作线程”，可能直接结束所有工作。

POSIX 的 [pthread_cancel(3)](https://man7.org/linux/man-pages/man3/pthread_cancel.3.html)是另一套取消接口：响应时机受目标线程的取消状态、类型和取消点约束，请求成功返回不证明目标已结束。应用自行设计的取消令牌、条件变量或控制消息又有各自契约。三者都需要回答：何处观察请求、何时可以离开临界区、由谁释放资源，以及调用方怎样确认结束。

对普通服务，可将合作停止分成以下责任。这是教学设计，不是内核提供的固定流程：

| 阶段 | 责任与完成条件 | 主要失败窗口 |
| --- | --- | --- |
| 停止接纳 | 接入管理者拒绝或转移新工作，标记服务正在排空 | 只改健康状态，已缓存的路由和本地入口仍继续接纳 |
| 处理在途工作 | 每项工作按业务契约完成、取消或转交，并保留结果状态 | 本地停止等待，远端写入却已提交 |
| 归还资源 | 所有者释放锁、租借、描述符及注册项，通知等待者 | 控制线程越权关闭其他线程仍在使用的资源 |
| 汇总结束 | 协调者确认线程或任务结束，在总期限内汇总未完成项 | 无期限 join 或清理回调使停机永久等待 |

停止状态与等待条件应在同一同步协议中检查。否则可能发生“检查尚未停止 → 控制线程通知 → 工作线程才开始等待”的遗漏唤醒；条件变量的谓词与锁配合见[锁与同步原语](locks-and-synchronization.md)。重复的停止请求应能安全收敛；也不能依赖连续收到第二个 SIGTERM 才保证总期限执行。期限由应用协调者检查；若它本身卡住，则需外部宿主发起预先约定的期限后处置，并保留未完成状态。发起强制终止不等于外部业务已经撤销，也不承诺进程在任何内核状态下立即结束。

处理函数打断[阻塞](../../glossary/systems.md#systems.blocking)调用后，接口可能自动重启，也可能返回 EINTR；SA_RESTART 不覆盖所有调用。EINTR 分支仍要先检查停止状态、既有进度和剩余期限，不能无条件重试使取消失效。具体范围见 [signal(7) 的中断说明](https://man7.org/linux/man-pages/man7/signal.7.html)和[系统调用返回契约](syscalls-privilege-and-return-contracts.md)。

## 正常退出也不能替业务完成验收

C 库的 [exit(3)](https://man7.org/linux/man-pages/man3/exit.3.html)执行注册的退出回调并刷新、关闭 stdio 流；这不证明其他线程已经完成，也不等于数据库提交、远端确认或数据耐久性已经验收。清理应在受控的普通执行路径中完成，不能因为 exit 名称里有“正常”就把它当作异步信号处理函数里的安全清理入口。

[_exit(2)](https://man7.org/linux/man-pages/man2/_exit.2.html)不执行这些[用户态](../../glossary/systems.md#systems.privilege)退出回调，也不刷新 stdio 缓冲；不能用它代替需要保留业务结果的排空。强制终止则可能完全没有应用清理机会。退出期限的价值是限制本地资源占用，并明确记录未完成工作；它不能使已经发生的外部副作用回滚。

若服务还创建了子进程，通常需要由父进程通过 [wait/waitpid 等接口](https://man7.org/linux/man-pages/man2/wait.2.html)收集退出状态并回收相应内核记录；收到 SIGCHLD 不等于已经完成回收。在未采用自动回收策略的常见管理方式下，应检查所有可回收子进程，不能把标准信号接收次数当作退出子进程数量。线程等待、子进程回收和业务确认是三种完成条件。

纸面推演：假设服务有 5 秒退出预算，在途 A 已提交远端写入但尚未拿到响应，B 正等待[队列](../../glossary/algorithms.md#algorithms.queues)空位。控制线程首先停止接纳并通知两者；B 观察停止谓词后退出等待，A 根据剩余预算查询或记录结果未知，不能把关闭连接记成“操作未发生”。4 秒时仍未结束，就只剩 1 秒可用于后续清理和汇总，不能再启动一个默认 5 秒的等待。数值是教学假设，没有运行停机或远端调用实验。

## 自检与继续阅读

- 哪些是进程共享处置，哪些是线程自己的掩码？信号可能由哪个线程接收？
- 同一个 SIGTERM 在待决期间产生三次，为什么不能要求执行三次回调？
- 停止请求提交后，等待 I/O、锁和队列空位的任务分别怎样被唤醒并确认结束？
- 总期限结束时，哪些工作是已完成、已取消、已转交或结果未知？证据由谁保留？

[文件描述符生命周期](file-descriptors-and-open-file-descriptions.md)解释跨线程 close 与编号复用为什么不是通用取消；[I/O 多路复用](io-multiplexing-readiness-and-event-loops.md)说明 signalfd 所接入的就绪模型。[超时与重试预算](../reliability/timeouts-and-retry-budgets.md)继续区分本地停止等待与远端副作用，[声明式部署与健康探针](../devops/declarative-deployments-and-health-probes.md)连接实例摘流与进程排空。

## 来源与核查范围

2026-10-22 联网核查所链 Linux man-pages 6.19，覆盖处置/掩码/待决、异步信号安全、sigwait/signalfd、线程定向信号、取消、exit/_exit 及子进程回收的接口边界。状态为 source-checked；状态流程、死锁反例、责任表和五秒预算均为教学综合。未编译或运行信号、线程取消、服务摘流、EINTR、资源回收、崩溃恢复或强制终止实验。
