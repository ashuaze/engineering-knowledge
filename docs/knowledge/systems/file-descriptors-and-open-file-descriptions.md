---
id: "kb-systems-file-descriptors"
title: "文件描述符与打开文件描述：关掉一个编号，资源为什么仍在"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "区分描述符编号、打开文件描述与底层对象，解释 dup/fork 共享、编号复用、关闭和继承的边界。"
created: "2026-10-20"
updated: "2026-10-22"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-execution-units", "kb-systems-syscalls"]
related: ["kb-systems-virtual-memory", "kb-systems-io-multiplexing", "kb-networking-http-pools", "kb-systems-synchronization", "kb-systems-ipc"]
tags: ["file-descriptor", "open-file-description", "dup", "resource-lifecycle"]
---

# 文件描述符与打开文件描述：关掉一个编号，资源为什么仍在

学习入口：[dup](../../glossary/systems.md#systems.fd-socket) 得到新编号，为什么读取位置仍会互相影响？close 返回后，为什么另一个[线程](../../glossary/systems.md#systems.execution-units)还可能完成 I/O？前置：[进程与线程](process-thread-coroutine.md)、[系统调用](syscalls-privilege-and-return-contracts.md)。本文依据 Linux man-pages 6.19；资源图和读取顺序为纸面推演，未运行描述符实验。

## 编号、打开状态与对象分属不同层

文件描述符 fd 是非负整数，表示进程描述符表中的一个入口。0 是合法编号，不能用“非零才成功”判断 open。描述符可引用普通文件、socket、管道等不同对象，它们并不具有完全相同的操作语义。

```text
进程中的 fd 表项 → 打开文件描述（open file description）→ 底层对象
       fd 标志        文件位置、文件状态标志等              文件/socket 等
```

[open(2)](https://man7.org/linux/man-pages/man2/open.2.html)说明，每次成功 open 建立新的打开文件描述，描述符引用它。路径是查找入口，不是打开状态本身；以后路径被删除或改指向，不自动使既有引用变成新对象。fd 数字也只在相应表及时间范围内有意义，不是跨进程、永久不变的业务 ID。

## dup 复制引用，不建立独立读取位置

[dup(2)](https://man7.org/linux/man-pages/man2/dup.2.html)取得新的描述符，但它与原描述符引用同一个打开文件描述，因而共享文件偏移和文件状态标志。FD_CLOEXEC 等描述符标志则是另一层；普通 dup 得到的新描述符不自动保留 close-on-exec。

教学假设：普通文件内容为 ABCDEF，均以只读方式打开，所有调用成功，各次 read 均实际返回 2 字节；期间文件内容及路径指向保持不变，无其他读取者或定位操作，按下列顺序执行：

| 操作 | 推演结果 |
| --- | --- |
| open 一次得到 a，再令 b = dup(a) | a 与 b 共享偏移，初始为 0 |
| 从 a 读取 2 字节 | 得到 AB，共享偏移变为 2 |
| 从 b 读取 2 字节 | 得到 [CD](../../glossary/devops.md#devops.cicd)，共享偏移变为 4 |
| 再独立 open 同一路径得到 c，读取 2 字节 | 新打开描述的偏移独立，得到 AB |

另一次 open 的独立偏移不代表文件内容也被复制；底层仍可指向同一文件。同样，dup 也不复制 socket 成另一条独立连接。

fork 后，父子描述符通常仍引用相同打开文件描述，文件偏移及状态标志可以继续共享，见 [fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)。地址空间分开不意味着所有资源状态都分开；同进程普通线程通常还共享描述符表，使用和关闭需要明确所有权。

管道与套接字怎样保留边界和生命周期，共享内存又由谁同步，见[IPC 与共享所有权](ipc-channels-shared-memory-and-ownership.md)。

## 关闭编号不等于取消一切工作

Linux 的 [close(2)](https://man7.org/linux/man-pages/man2/close.2.html)释放描述符编号，使它可被重新使用；其他引用或已开始操作仍可能维持底层状态。例如另一个线程[阻塞](../../glossary/systems.md#systems.blocking)于该打开文件描述的 I/O，Linux 下它可能在 close 之后仍完成操作。不能把跨线程 close 当作通用的即时取消协议。

纸面反例：旧连接使用 fd 7 → 某处关闭它 → 新[连接复用](../../glossary/networking.md#networking.keepalive) fd 7 → [延迟](../../glossary/performance.md#performance.latency-throughput)回调仅凭旧数字操作 → 误作用于新连接。这里假定恰好发生编号复用；防护需要连接对象的生命周期、代次或等效身份检查，不能只检查整数相等。

释放责任也应区分“我拥有的引用”和“全局对象是否消失”。[mmap](virtual-memory-pages-and-faults.md)成功后可在不解除映射的情况下关闭原 fd；映射和描述符分别有归还动作。高层[连接池](../networking/http-reuse-pools-and-timeouts.md)的租借归还又不同于底层 close。

## 继承、错误和额度都属于生命周期

O_CLOEXEC 在打开时设置成功 execve 后关闭的标志，有助于避免资源意外进入新程序映像；它不阻止 fork 时继承，见 [open 的 O_CLOEXEC](https://man7.org/linux/man-pages/man2/open.2.html)。多线程中先 open 再另设标志可能留出竞争窗口，具体创建接口应选择相应原子选项。

Linux close 出错后不能机械地再次关闭同一数字，因为编号可能已经释放并复用；这与某些其他系统的 EINTR 语义不同，不能推广成通用 POSIX 关闭算法。错误仍应记录并按数据策略补救；成功 close 也不单独保证落盘，依据见 [close 的注意事项](https://man7.org/linux/man-pages/man2/close.2.html)。

打开数量受到进程限制和系统资源约束。[getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html)定义 RLIMIT_NOFILE；open 的 EMFILE 与 ENFILE 分别指向进程描述符限制和系统打开文件表限制。提高上限不能修复泄漏，也不会消除连接缓冲、内存与下游容量成本。

自检：独立的是编号、偏移还是底层对象？谁最后归还引用？回调是否仍属于当前连接？资源会不会跨 exec 意外保留？错误来自额度、无效编号还是对象自身？

2026-10-20 核查 open、dup、fork、close、getrlimit 与 mmap 文档，状态为 source-checked。未执行共享偏移、编号复用、跨线程关闭、继承、描述符耗尽或 socket 取消实验。
