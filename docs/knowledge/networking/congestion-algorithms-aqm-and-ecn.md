---
id: "kb-networking-congestion-algorithms"
title: "拥塞算法与队列管理：带宽充足为什么仍然延迟很高"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分 cwnd、pacing、带宽时延积和排队，对照 Reno、CUBIC、BBR 的控制思路及 AQM、调度与 ECN 的职责。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-flow-congestion", "kb-performance-latency-queues"]
related: ["kb-networking-path-mtu", "kb-networking-udp-quic", "kb-performance-backpressure", "kb-performance-benchmarking"]
tags: ["congestion-control", "cubic", "bbr", "aqm", "ecn"]
---

# 拥塞算法与队列管理：带宽充足为什么仍然延迟很高

学习入口：下载几乎占满链路，交互请求却突然变慢。把缓冲区加大以后丢包减少，体验反而更差。问题在于链路吞吐、在途数据、[排队等待](../../glossary/performance.md#performance.queueing)和不同流之间的机会分配属于不同维度。

前置：[TCP 流控与拥塞控制](tcp-flow-control-and-congestion.md)、[延迟、吞吐与排队](../performance/latency-throughput-and-queues.md)。本文介绍固定 RFC 的基础控制思路；[BBR](../../glossary/networking.md#networking.congestion-algorithms) 仅依据开发者资料说明模型方向，不比较其各代实现，也不声称某操作系统默认采用某算法。所有速率、RTT 与队列数字都是纸面假设，没有改内核参数、制造拥塞或进行测速。

## 窗口限制总量，pacing 调整节奏

接收窗口 rwnd 反映接收端承受能力，拥塞窗口 cwnd 约束发送端因网络拥塞而允许的在途量；应用是否持续提供数据、确认到达和连接恢复状态也会限制发送。pacing 将发送安排到时间上，避免把允许发送的量集中为过大的突发。窗口与节奏可以配合使用，不能用“设置了每秒速率”推出拥塞窗口已经无关。

| 控制量 | 主要问题 | 不能单独保证 |
| --- | --- | --- |
| rwnd | 接收端还愿意接纳多少 | 沿途网络没有拥塞 |
| cwnd | 当前允许多少数据在途 | 这些数据均匀发送、没有[排队](../../glossary/performance.md#performance.queueing) |
| pacing rate | 发送机会在时间上怎样展开 | 接收端够快、链路容量无限 |
| 应用供给与发送缓冲 | 当前有没有待发送数据 | 写入返回就代表远端交付 |

窗口基础见 [RFC 5681 §2–3](https://www.rfc-editor.org/rfc/rfc5681.html#section-2)；开发者的 [BBR FAQ](https://raw.githubusercontent.com/google/bbr/master/Documentation/bbr-faq.md)也分别列出 pacing rate、cwnd、带宽和最小 RTT 估计等状态。

## 带宽时延积是管道预算，不是建议填满的队列

假设瓶颈速率为 **100 Mbit/s**，不含排队的往返时延为 **40 ms**，这里采用十进制速率和字节，不扣协议开销：

```text
BDP = 100,000,000 bit/s × 0.040 s
    = 4,000,000 bit = 500,000 byte ≈ 488.3 KiB
```

[BDP](../../glossary/networking.md#networking.queue-management)（Bandwidth-Delay Product，带宽时延积）给出这组理想条件下持续利用管道所需在途量的量级。它既不是瓶颈队列必须预留的长度，也不是任意连接的最佳 cwnd。如果把含大量排队的 RTT 当成基准，算出的“管道”可能把已经堆积的数据也算进去。

同一瓶颈每秒服务 `12,500,000 byte`。假设一个到达分组前方已有 **1,000,000 byte** 排队，期间服务速率固定且不被更高优先级流量打断，则额外等待约为：

```text
1,000,000 / 12,500,000 = 0.080 s = 80 ms
```

这个队列就可能贡献比 40 ms 基础 RTT 更大的等待。这里只计算一个方向、一个队列中已有字节的服务时间，未包含自己的发送、其他排队、传播或接收处理。不能把它直接当作整次请求[延迟](../../glossary/performance.md#performance.latency-throughput)。

## Reno、CUBIC 与 BBR 分别怎样试探

| 思路 | 用什么调整发送 | 阅读时保留的边界 |
| --- | --- | --- |
| Reno 基础模型 | 慢启动后，在拥塞避免阶段较缓地增大窗口，遇拥塞信号回退 | 不同丢包恢复路径和计时器处理不同，不能统一概括为每次丢包都同样减半 |
| CUBIC | 结合距上次拥塞事件的时间，用立方曲线调整窗口，并保留 Reno 友好区域 | 按 RTT 的效果、竞争关系和实现细节仍需验证，曲线本身不保证每条流公平 |
| BBR 的模型方向 | 估计交付速率与传播时延，并配合 pacing、在途量及探测阶段控制发送 | 估计受采样、应用限速和竞争影响，不能视为直接知道真实容量或完全忽略丢包 |

前两行分别依据 [RFC 5681 §3](https://www.rfc-editor.org/rfc/rfc5681.html#section-3) 与 [RFC 9438 §3–4](https://www.rfc-editor.org/rfc/rfc9438.html#section-3)。BBR 的设计动机见作者的 [Google Research 论文页](https://research.google/pubs/bbr-congestion-based-congestion-control/)，状态和探测说明见上述开发者 FAQ。这里不把早期论文或 FAQ 的示例数值移植为当前所有 BBR 版本的参数。

在业务只偶尔发送少量数据时，观测交付速率低可能因为应用没有供给；在接收方很慢时，也可能由 rwnd 限制。只看“速度不高”就更换拥塞算法，可能没有触及真正瓶颈。

## AQM、调度和 ECN 各承担一段控制

AQM（Active Queue Management，主动队列管理）在队列完全塞满之前就按队列状态丢弃或标记部分分组，给端点更早的拥塞反馈，减少长期积压。调度器决定从哪个流或类别的队列取下一个分组，关注机会与隔离。两者可组合：每流排队不自动控制等待，只有 AQM 也不自动保证每个流获得相同份额，见 [RFC 7567 §2.1](https://www.rfc-editor.org/rfc/rfc7567.html#section-2.1)。

ECN（Explicit Congestion Notification，显式拥塞通知）让支持它的路径与端点用标记反馈拥塞，端点仍须降低相应发送压力。以经典 [TCP](../../glossary/networking.md#networking.transport) ECN 为例，需要两端协商，网络设置拥塞标记，接收端反馈，发送端响应；严重拥塞仍可能丢包，见 [RFC 3168 §5–6](https://www.rfc-editor.org/rfc/rfc3168.html#section-5)。本文不展开后续 ECN 扩展，也不认为所有端点对标记的响应相同。

三者都不会创造额外的物理带宽。若持续输入超过可服务量，仍需端点降速、接纳限制或丢弃；若几十条同时传输的流与一条交互流竞争，按流公平也未必等于按用户或业务公平。应用层的[背压](../performance/backpressure-and-bounded-queues.md)还负责把下游压力传回生产者，不能由路由器代替。

## 怎样判断一次调整是否有效

比较应固定内核/协议栈、算法版本、队列管理与调度组合、基础 RTT、容量、缓冲、流数量、传输时长和接收端能力。至少同时查看有效吞吐、空闲/负载下 RTT、[尾延迟](../../glossary/performance.md#performance.percentiles)、丢包/标记、重传与竞争流份额。一次单流长下载的峰值不能证明短请求或多人共享体验改善。

先判断应用受限、接收受限、网络拥塞还是 CPU/加密等处理受限，再解释控制量变化，见[基准测试与工作负载](../performance/benchmarks-workloads-and-speedup.md)。实验还应说明模拟器位置及批量分段/合并设置；开发者 FAQ 特别提醒这些设置可能改变模拟丢包过程。本文没有执行该对照。

## 自检

1. cwnd 和 pacing 分别控制什么？有发送节奏为何仍需要窗口？
2. 100 Mbit/s、40 ms 的 BDP 是多少字节？为什么不是建议的排队长度？
3. 给定队列前方 1,000,000 字节，80 ms 代表哪段时间？还缺哪些延迟？
4. 为什么 AQM、每流调度与 ECN 不能互相替代，也不能消除过载？
5. 应用每秒只提供少量数据，为什么低交付速率不能直接归咎于拥塞算法？

## 来源与核查

2026-10-26 核查 RFC 5681、9438、7567、3168 固定文本及 Google Research/BBR 开发者资料。BBR 页面为设计与观测入口，不是具体部署版本的验证证据。本文为 source-checked 概念文章，未实测算法性能、公平性、队列配置、ECN 协商或故障恢复。
