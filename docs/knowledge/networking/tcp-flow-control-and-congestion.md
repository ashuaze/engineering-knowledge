---
id: "kb-networking-flow-congestion"
title: "TCP 流量控制与拥塞控制：发送变慢到底受谁限制"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "用接收窗口、拥塞窗口和在途数据区分接收端背压与路径限制，解释 RTT、丢包判断、重传和应用排队的边界。"
created: "2026-10-22"
updated: "2026-10-26"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-connection-states", "kb-performance-latency-queues"]
related: ["kb-performance-backpressure", "kb-networking-http-pools", "kb-systems-io-multiplexing", "kb-reliability-retry-budgets", "kb-networking-udp-quic", "kb-networking-congestion-algorithms"]
tags: ["tcp", "flow-control", "congestion-control", "retransmission"]
---

# TCP 流量控制与拥塞控制：发送变慢到底受谁限制

学习入口：连接仍是 ESTABLISHED，发送却越来越慢；把发送缓冲区加大就能恢复吞吐吗？先分清接收端能容纳多少字节、路径上允许多少未确认数据，以及应用自己还有多少待发送工作。前置：[TCP 连接状态](tcp-tls-and-connection-states.md)、[延迟与排队](../performance/latency-throughput-and-queues.md)。本文讨论单条 [TCP](../../glossary/networking.md#networking.transport) 连接的概念模型，不提供某个内核或[拥塞算法](../../glossary/networking.md#networking.congestion-algorithms)的调优参数；没有抓包、测速或故障注入。

Reno、CUBIC、BBR 的控制思路，以及窗口、节奏与[队列](../../glossary/algorithms.md#algorithms.queues)的配合，继续见[拥塞算法与队列管理](congestion-algorithms-aqm-and-ecn.md)。

## 两个窗口约束同一次发送

[流量控制](../../glossary/networking.md#networking.transport-control)保护接收端，避免发送者超过接收方通告的字节范围；拥塞控制调节向网络注入的数据，适应共享路径的反馈。它们都可能让发送变慢，观察对象不同。

| 量 | 从哪里来 | 不能直接代表什么 |
| --- | --- | --- |
| 接收窗口 rwnd | 对端通告的接收空间约束 | 接收应用的业务[并发](../../glossary/systems.md#systems.concurrency)、事务完成量 |
| 拥塞窗口 cwnd | 发送端拥塞控制状态 | 固定链路带宽、接收缓存大小 |
| 在途数据 FlightSize | 已发送但尚未被累计确认的数据量 | 本地所有待发送数据，或当下仍在链路上的精确字节数 |

[RFC 5681 §2](https://www.rfc-editor.org/rfc/rfc5681.html#section-2)定义这些量。在不考虑丢包恢复、窗口收缩等复杂情况的普通发送阶段，可用下面的教学近似理解新增发送额度，所有量先统一为字节：

```text
当前新增发送额度 ≈ max(0, min(rwnd, cwnd) - FlightSize)
```

这里的窗口是允许的范围，在途量是已经占用的额度。发送端即使有很大的 cwnd，也不能绕过小 rwnd。ACK 推进后可释放额度，但若应用没有数据或发送受调度、节奏控制等因素限制，也不一定立刻用满。SACK、恢复期的在途估计及窗口边界处理需要更完整状态，不能把这条近似式直接实现为 TCP 协议栈。

## 接收应用不读，压力怎样传回来

接收窗口通过协议通告发送者，随接收缓冲及消费进度变化。零窗口意味着暂时没有普通新数据的发送空间，不等于连接已经断开。TCP 使用零窗口探测，避免窗口重新打开的通知丢失后永远等待；依据见 [RFC 9293 §3.8.6](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.8.6)。探测只能帮助传递窗口状态，不能让停止消费的应用恢复处理能力。

从此机制推演一条可能的压力链：

```text
接收应用读得慢 → 接收缓冲积压 → 通告窗口限制后续发送
→ 发送端待发数据积压 → 本地写入等待或返回暂不可写
→ 生产者若遵守这个反馈，才会减少继续生产
```

反馈不是瞬时的，中间还存在两端 [socket](../../glossary/systems.md#systems.fd-socket) 缓冲、协议层缓冲和应用[队列](../../glossary/algorithms.md#algorithms.queues)。若发送者一边发现不可写，一边把新工作继续存入无限内存队列，TCP 的限制仍然生效，[进程](../../glossary/systems.md#systems.execution-units)却可能耗尽内存。[Linux send(2)](https://man7.org/linux/man-pages/man2/send.2.html)说明发送缓冲不足时的[阻塞](../../glossary/systems.md#systems.blocking)及非阻塞 EAGAIN/EWOULDBLOCK 行为；应用仍要保留部分发送进度并限制生产。

反方向也可能藏住压力：接收服务迅速把 socket 内容读入无限业务队列，会释放传输接收空间，但数据库消费者仍可能完全跟不上。窗口开放只能表明传输端允许接收相应字节，不能据此给业务请求承诺处理槽位。队列容量、接纳和[截止时间](../../glossary/reliability.md#reliability.retry-budget)仍见[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。

扩大缓冲可吸收突发，也会延后反馈并增加积压的字节与等待时间。先定位限制在哪一层，再决定是否扩大；“写入返回更快”本身不能证明端到端完成吞吐变高。

## 拥塞控制是在反馈中探路

发送者通常不能直接知道所有中间设备当前还有多少空闲容量。经典控制在 ACK 推进时扩张发送范围，遇到拥塞反馈后收缩。慢启动的“慢”不代表始终线性增加：窗口未受其他限制且 ACK 规律合适时，它可以按往返轮次快速增长；进入拥塞避免后则更谨慎。[RFC 5681 §3](https://www.rfc-editor.org/rfc/rfc5681.html#section-3)给出慢启动、拥塞避免和快速重传/恢复的经典规则。

这些规则适合解释反馈关系，不能据此声称所有部署都使用同一个增长曲线或遇到任何丢包都执行完全相同的减窗。比如 [RFC 9438](https://datatracker.ietf.org/doc/html/rfc9438#section-3)描述的 CUBIC 使用与上次拥塞事件后经过时间相关的立方函数调节窗口。具体诊断应记录端点实现、算法、恢复机制和路径条件；本文不声称已核查某台机器的默认配置。

拥塞也不必先表现为丢包。双方和路径支持相应机制时，[RFC 3168 的 ECN](https://www.rfc-editor.org/rfc/rfc3168.html#section-6.1)允许用拥塞标记及反馈请求发送者减速。没有看到重传，不能证明路径没有[排队](../../glossary/performance.md#performance.queueing)或拥塞。

## 丢失检测、重传与减速各自回答一个问题

丢失检测判断哪些字节可能没有送达；重传尝试补齐它们；拥塞控制决定继续发送的强度。它们协作，但“发生了重传”并不是根因已经确定的证据。

累计 ACK 停在某个缺口时，重复 ACK、SACK 等反馈可提供后续数据到达的证据；发送者可在 [RTO](https://www.rfc-editor.org/rfc/rfc6298.html) 到期前推断需要恢复，经典快速重传使用重复 ACK 阈值。这不表示累计确认已经越过缺口。较新的 [RFC 8985 RACK-TLP](https://datatracker.ietf.org/doc/html/rfc8985#section-3.3)结合发送时间和确认关系，并为乱序留出等待窗口；尾部丢失的探测又解决反馈不足的问题。等待太少会误把乱序当丢失，等得太久则[延迟](../../glossary/performance.md#performance.latency-throughput)恢复。这些机制说明，“没收到某一段的确认”需要结合时间与后续证据解释。

RTT 是发送与相应确认往返的时间，不等于应用响应耗时；传播、排队与确认返回路径都会影响观察。RTO 是重传计时期限，也不是 RTT 的固定倍数。[RFC 6298 §2–5](https://www.rfc-editor.org/rfc/rfc6298.html#section-2)用平滑 RTT、变化量和时钟粒度计算 RTO，并在计时器到期重传后[退避](../../glossary/api.md#api.retries)；对重传段取样还需避免无法区分哪次发送引发 ACK 的歧义。应用的请求截止时间则独立约束“还值得等多久”。

丢包可能来自拥塞，也可能来自链路误码等其他原因；协议保守减速并不证明物理原因一定是拥塞。[RFC 3168 §5.2](https://www.rfc-editor.org/rfc/rfc3168.html#section-5.2)明确讨论损坏导致的丢弃；RACK 对乱序的处理则进一步说明重传也可能是误判。诊断应结合路径和两端证据，不能从单端一个重传计数直接推出“交换机带宽满了”。

## 用一组纸面数字区分限制

教学假设：以下是同一发送方向的三个独立瞬间，单位为 KiB；1 KiB = 1024 字节，连接处于普通发送阶段，窗口已按适用缩放换算，无乱序和恢复期特殊规则，发送应用有足够数据。数字不是采样结果。

| 瞬间 | rwnd | cwnd | FlightSize | 可新增量的近似 | 解释 |
| --- | --- | --- | --- | --- | --- |
| A | 64 | 16 | 12 | 4 | 目前由拥塞窗口提供较小上界 |
| B | 8 | 32 | 6 | 2 | 目前由接收窗口提供较小上界 |
| C | 0 | 32 | 0 | 0 | 等待窗口恢复；探测不属于普通大批新数据发送 |

把 A 的 rwnd 从 64 增到 128，不会改变表中的 4 KiB；把 B 的 cwnd 从 32 增到 64，也不会改变 2 KiB。先知道哪个约束生效，才知道修改哪个量可能有用。表格只解释额度，不保证下一瞬间一定发出这些字节。

再作一个理想化估算：若一个窗口受限的稳定连接每 50ms 能推进确认 64 KiB，忽略协议开销、丢失与其他瓶颈，平均数据推进约为 `64 KiB / 0.05s = 1.25 MiB/s`。保持这个窗口而把 RTT 改成 100ms，模型中约为 0.625 MiB/s。这个推导用于说明相同窗口为何不对应固定吞吐，不能据此预测真实 HTTP 下载速度。

同理，若目标数据速率设为 10 MiB/s、无额外排队的 RTT 假设为 50ms，速率与往返时间的乘积为 0.5 MiB。它描述维持该速率所需在途量的理想量级；不表示给 socket 分配 0.5 MiB 就必达目标，也不应把已经被排队放大的 RTT 当作继续堆积缓冲的理由。窗口、物理路径、应用供给和接收消费必须同时允许。

以 UDP 为承载的可靠多流及可选不可靠消息，继续见[UDP 与 QUIC](udp-quic-streams-and-delivery-boundaries.md)。跨流交付减少一类队头等待，流额度、连接额度、拥塞及业务依赖仍需分别判断。

## 排查时先补齐哪类证据

下面是诊断问题清单，没有执行相应采集：

| 观察 | 下一步要区分的原因 | 不能直接下的结论 |
| --- | --- | --- |
| rwnd 长期很小或为零 | 接收端读循环、内存/缓冲策略、应用处理与调度 | 一定是网络带宽不足 |
| cwnd 限制明显且确认推进慢 | 算法和恢复状态、RTT 变化、丢失/[ECN](../../glossary/networking.md#networking.queue-management)、路径条件 | 加大接收缓存必定解决 |
| 两个窗口都有余量却吞吐低 | 应用是否供给不足，本地等待、节奏控制、CPU 或其他协议限制 | TCP 本身一定有故障 |
| 重传上升 | 缺口和乱序时序、两端及路径丢弃证据、观测位置 | 每次重传都对应一次拥塞丢包 |
| 发送暂不可写且应用内存增长 | 本地积压在哪里、上游是否减速、消息字节与期限上限 | 只需扩大 socket 缓冲 |

采集时应说明单连接还是聚合值、哪个方向、时间范围，以及实现是否以段数显示 cwnd；比较前换算单位。抓包位置和协议栈指标也只观察各自边界，不能把一个累计计数当作完整的因果时序。

自检：rwnd 变大而传输不加速，至少还有哪三个解释？ACK 前进但业务队列变长，传输流控保护了谁？为什么 RTT 增大既可能限制窗口周转，也可能是队列积压的结果？

[HTTP 复用与连接池](http-reuse-pools-and-timeouts.md)说明 TCP 连接之外的流、池和排队；[I/O 多路复用](../systems/io-multiplexing-readiness-and-event-loops.md)解释暂不可写后的继续推进；[超时与重试预算](../reliability/timeouts-and-retry-budgets.md)约束应用等待与额外尝试。TCP 自动重传字节，不代替应用对业务重放安全性的判断。

## 来源与核查范围

2026-10-22 联网核查 RFC 9293、5681、6298、3168、8985、9438 及 Linux send(2)，覆盖窗口、经典控制、RTO、ECN、乱序/丢失判断及阻塞发送边界。状态为 source-checked；额度表、压力链、速率与在途量数字为教学推演。未采集 TCP_INFO、内核指标或报文，未运行流控、拥塞、误码、乱序、跨代理背压或性能实验。
