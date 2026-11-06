---
id: "kb-systems-io-multiplexing"
title: "I/O 多路复用与就绪通知：一个线程怎样等待多个连接"
kind: "concept"
domain: "systems"
status: "evolving"
summary: "比较 select、poll、epoll 的等待接口，解释就绪与完成、LT/ET、非阻塞、部分读写和公平调度。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-systems-file-descriptors", "kb-runtime-async-blocking"]
related: ["kb-systems-syscalls", "kb-runtime-event-loop", "kb-performance-backpressure", "kb-networking-http-pools", "kb-systems-execution-units"]
tags: ["io-multiplexing", "epoll", "readiness", "event-loop"]
---

# I/O 多路复用与就绪通知：一个线程怎样等待多个连接

学习入口：已有上万条连接，为什么不必给每条连接创建专属等待[线程](../../glossary/systems.md#systems.execution-units)？前置：[文件描述符](file-descriptors-and-open-file-descriptions.md)、[同步与阻塞](../runtime/async-and-blocking.md)。本文讨论 Linux man-pages 6.19 中 [select](../../glossary/systems.md#systems.io-multiplexing)/poll/epoll 的就绪模型，重点是[非阻塞](../../glossary/systems.md#systems.blocking)[字节流](../../glossary/networking.md#networking.transport)；没有实现服务器或执行吞吐实验。

## 把多个等待条件交给同一个接口

应用可以把一组 fd 及关注事件交给内核，等待其中一些出现可处理条件，再分派后续工作。这样避免按固定顺序阻塞读取每条空闲连接，也不必不停遍历并调用 read 试探。

等待接口本身可以阻塞调用线程；“多路复用”不要求永远忙轮询。事件到达或[超时](../../glossary/api.md#api.retries)、信号等条件使调用返回，应用仍需获得 CPU，执行真正的读取和业务逻辑。I/O 通知与回调调度的区别可继续读[事件循环](../runtime/event-loop-and-microtasks.md)。

| 接口 | 应用维护的关注集合 | 需要记住的边界 |
| --- | --- | --- |
| select | 每次传入 fd 集合，返回时集合被修改 | Linux/glibc 常规 fd_set 的 FD_SETSIZE 为 1024；fd 需小于它，即 0～1023，不只是限制连接数量 |
| poll | 每次传入描述符及事件[数组](../../glossary/algorithms.md#algorithms.sequences)，读取返回事件 | 不受该 fd_set 限制，但仍需提交并检查相应数组 |
| epoll | 创建实例，经 ctl 管理关注项，由 wait 取得就绪事件 | Linux 特有；注册、返回事件和应用处理都仍有成本 |

依据见 [select(2)](https://man7.org/linux/man-pages/man2/select.2.html)、[poll(2)](https://man7.org/linux/man-pages/man2/poll.2.html)与 [epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html)。不能把 epoll 简化成任意负载恒定 O(1)、必然更快或无限连接；需要区分总关注数、活跃数、变更频率及每次处理的工作量。

## 就绪不是完成，也不替你保留数据

读就绪说明出现适合尝试读取的条件，也可能因 EOF 或错误返回；写就绪通常表示目前能接受一定输出，不表示任意长度写入都能一次完成，更不证明对端应用已消费。

通知不是对数据的独占预订：另一个读取者可能先消耗数据，就绪条件也可能变化。真正 read 时仍要处理 EAGAIN/EWOULDBLOCK，不能把“收到通知”当作可以安全执行任意阻塞读取的保证。非阻塞 fd 有助于避免这次尝试拖住处理其他连接的线程。

对正长度的字节流读取，返回正数表示该段字节、0 表示读取方向 EOF，-1 则按错误处理。一次 read 的边界也不等于应用消息边界，解析器可能需要累计多段或一次处理多条消息；见 [read(2)](https://man7.org/linux/man-pages/man2/read.2.html)。本文不将这个 EOF 规则推广到数据报。

## LT 与 ET 决定怎样继续推进

epoll 默认使用水平触发 LT：只要相应就绪条件持续满足，后续等待仍可报告。边沿触发 ET 关注状态变化，不能指望每消费一小段都再收到一次提醒。多个变化还可能合并，事件数不等于消息数。

教学时序：非阻塞字节流已有 900 字节 → 收到 ET 通知 → 应用只读取 300 字节 → 剩余 600 字节仍在。如果没有后续变化，也没有应用内部继续处理安排，直接重新等待新通知可能使剩余内容迟迟得不到处理。这是自设数值的纸面反例，机制依据见 [epoll 的 LT/ET 说明](https://man7.org/linux/man-pages/man7/epoll.7.html)。

常见 ET 处理原则是持续推进到 EAGAIN 后才依赖新的通知，同时处理 EOF、错误与中断。若为了公平只处理有限工作量，尚未读空的连接必须留在应用自己的待处理[队列](../../glossary/algorithms.md#algorithms.queues)中，之后主动继续，不能把它遗忘并只等新边沿。

## 等待机制之外，还需要连接状态机

以下为设计步骤，不是可运行的 epoll 服务器：

1. 为连接保存有效身份、输入缓冲、解析进度、输出偏移、关闭状态及期限。
2. 收到事件后先核对生命周期，按具体标志尝试非阻塞操作；分别处理数据、EOF、错误及暂时不能继续。
3. 部分写入后保留未发送后缀，确有待发送数据时安排后续可写处理；避免无事可做却持续响应 LT 可写通知而空转。
4. 达到本轮工作预算时保留待处理状态，轮转其他连接；输出积压达到上限时限制继续生产或接收，保持队列有界。连接管理者需要在容量恢复后重新安排被暂停工作（ET 下不能只等新边沿），或按期限和接纳规则拒绝、终止；具体取舍见[背压与拒绝策略](../performance/backpressure-and-bounded-queues.md)。
5. 终止时安排取消关注、释放拥有的引用，并使已有事件批次与[延迟](../../glossary/performance.md#performance.latency-throughput)回调识别过期连接；不能只用可能复用的 fd 数字证明身份。

错误或挂断事件不能简单解释为“缓冲必然已空”：可能仍有应读取的数据，半关闭也不等于两个方向同时结束。需要依协议决定读完、回写或终止；本批不提供 [TLS](../../glossary/networking.md#networking.tls)、监听接入、重连和完整关闭实现。

## 非阻塞和多路复用不覆盖所有等待

CPU 解析、压缩和用户回调仍可能占满[事件循环](../../glossary/runtime.md#runtime.event-loop)线程。对普通文件，poll 往往立即报告就绪；Linux 的 O_NONBLOCK 不会使普通文件读写免于存储等待，而 epoll_ctl 对普通文件等不支持对象可返回 EPERM。依据见 [open 的 O_NONBLOCK](https://man7.org/linux/man-pages/man2/open.2.html)、[poll](https://man7.org/linux/man-pages/man2/poll.2.html)及 [epoll_ctl(2)](https://man7.org/linux/man-pages/man2/epoll_ctl.2.html)。

因此不能把 [socket](../../glossary/systems.md#systems.fd-socket) 就绪机制推广为所有磁盘 I/O 或 CPU 工作都已异步化。事件循环设计者需为普通文件与耗时 CPU 工作单独安排执行路径；若 [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 使用线程池或其他完成通知接口，还要按其契约分析容量与结果处理。本文不展开 io_uring、IOCP 或跨平台性能比较。

自检：等的是可尝试操作还是已经完成的结果？谁消费了就绪条件？部分消息和未发送后缀在哪里？ET 本轮没处理完时由谁再次推进？忙连接、空转和[背压](../../glossary/performance.md#performance.queueing)分别如何限制？

2026-10-20 核查上述 Linux man-pages 资料，状态为 source-checked。未执行 select/poll/epoll、LT/ET、短读写、半关闭、编号复用、公平调度、普通文件等待或性能对照实验；本站构建仅验收知识库页面。
