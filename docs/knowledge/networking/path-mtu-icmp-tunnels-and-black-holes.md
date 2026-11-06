---
id: "kb-networking-path-mtu"
title: "路径 MTU 与隧道：为什么小包能通大包却卡住"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分链路 MTU、路径 MTU、MSS 与应用大小，用封装预算和探测推演解释 ICMP 反馈、PMTUD 与黑洞边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-ip-routing"]
related: ["kb-networking-policy-convergence", "kb-networking-udp-quic", "kb-networking-flow-congestion", "kb-networking-ipv6-neighbors"]
tags: ["mtu", "pmtud", "icmp", "tunnels", "black-hole"]
---

# 路径 MTU 与隧道：为什么小包能通大包却卡住

学习入口：连接建立了，短消息也有响应，传文件或收到较大的 [TLS](../../glossary/networking.md#networking.tls) 报文时却反复超时。一个可能原因是分组大小超出了路径承载能力，反馈又没有抵达发送方。先按层数清字节，再判断证据能否支持这个假设。

前置：[网络分层、IP 与路由](network-layers-ip-subnets-and-routing.md)。本文讨论常见单播路径、ICMP 与分组化层探测；隧道开销和长度均为明确给定的纸面模型，不对应某个 VPN 或云产品。没有改 [MTU](../../glossary/networking.md#networking.path-mtu)、发探测、抓包或复现故障。

## 四种大小回答四个问题

| 名称 | 约束对象 | 容易误判之处 |
| --- | --- | --- |
| 链路 MTU | 某一链路能承载的 [IP](../../glossary/networking.md#networking.transport) 分组大小，按该接口的层次解释 | 只看本机接口便当作全程能力 |
| 路径 MTU（PMTU） | 给定方向和路径上的最小链路 MTU | 认为去回程、不同出口及切流后都相同 |
| TCP MSS | TCP 数据部分的大小上限约束；对端通告限制向它发送的数据段 | 认为包含 IP/TCP 首部，或等于永久不变的 PMTU |
| 应用消息大小 | 应用记录、请求体或对象的长度 | 认为一次 write、一个 TLS 记录与一个 IP 分组一一对应 |

路径 MTU 的定义与用途见 [RFC 1191 §2](https://www.rfc-editor.org/rfc/rfc1191.html#section-2)、[RFC 8201 §2](https://www.rfc-editor.org/rfc/rfc8201.html#section-2)。实际 TCP 分段还要同时遵守对端 MSS、路径与首部预算；TCP 字节流可以拆分一次应用写入，也可以合并多次写入。UDP 保留数据报边界，应用若自行分块还需定义重组与丢失处理，见 [UDP 与 QUIC](udp-quic-streams-and-delivery-boundaries.md)。

## 隧道把内层分组再装入外层分组

假设某条教学隧道的外层路径 MTU 为 **1500 字节**，全部外层封装固定占 **60 字节**，没有额外填充、嵌套封装或外层分片。内层承载 IPv6/TCP，无 IPv6 扩展首部或 TCP 选项，首部分别占 40、20 字节：

```text
内层 IP 分组预算 = 1500 - 60 = 1440 字节
内层 TCP 数据预算 = 1440 - 40 - 20 = 1380 字节
```

1380 是这组条件下每个 TCP 段的数据预算，里面还可能装着 TLS 首部、完整性标签和应用协议元数据，不能直接视为文件净载荷。若内层仍发送 1500 字节 IP 分组，外层总计 1560 字节，便超过给定承载能力。真实隧道应按协议、地址族、加密与填充逐项重算；参考 [RFC 4821 §5](https://www.rfc-editor.org/rfc/rfc4821.html#section-5) 对层次及首部预算的说明。

隧道入口承担一次新的外层发包：它看到的外层路径限制，需要与内层发送者的分组大小衔接。如何传播反馈、调整内层 MTU 或分片属于实现契约。“物理接口是 1500”不能代替这一层分析。

## 大包过不去，需要让发送方知道

IPv4 经典 PMTUD 使用不允许沿途分片的分组；遇到较小出口时，路由器丢弃超限分组并返回需要分片的 ICMP 信息，发送端据此下调估计，见 [RFC 1191 §3–4](https://www.rfc-editor.org/rfc/rfc1191.html#section-3)。若允许 IPv4 分片，还会引入重组与片段丢失成本，不能把它当作所有路径的默认补救。

IPv6 转发路由器不替超限分组分片，使用 ICMPv6 Packet Too Big（PTB）告知发送方。发送端减少后续分组大小；IPv6 的源端分片是另一种机制，见 [RFC 8201 §3–4](https://www.rfc-editor.org/rfc/rfc8201.html#section-3)。一个方向上的反馈不会自动证明反方向也已得到正确估计。

因此，过滤全部 ICMP 可能同时过滤掉正常工作需要的大小反馈。接收方也不能盲信任意 PTB：应校验它是否关联已发送流量及大小信息是否有效，避免错误或伪造反馈造成不必要降速。具体接纳规则、速率限制和防火墙配置需依实现核对。

## 黑洞是一个待验证的解释

教学时序：小握手分组通过；发送方随后发出较大分组；中途因 MTU 限制丢弃；相关 ICMP 又被过滤；发送方没有学到更小的边界，继续等待或重传。发送成功调用只证明本机接纳了数据，不证明对方收到。

这个时序能解释“小包通、大包卡”，但同样现象也可能来自访问策略、丢包、服务器限制或拥塞。小尺寸 ping 成功只证明那次、那个尺寸与协议的往返；Echo 无响应也不能单独判定业务路径断开。比较时需固定目的地、源地址、出口和协议，明确尺寸是否包含各层首部，分别记录正向交付及反馈返回。

路径变更后，曾经成功的大小也可能不再合适。多路径情况下，探测流和业务流还可能走不同路径；不能把一次成功扩展到所有五元组。

## 分组化层探测减少对 ICMP 的单一依赖

PLPMTUD 由 TCP 等分组化层发送受控大小探测，并根据确认区分已证实的可用大小和正在试探的大小，见 [RFC 4821 §7](https://www.rfc-editor.org/rfc/rfc4821.html#section-7)。DPLPMTUD 则给数据报传输提供探测、搜索及黑洞恢复框架，见 [RFC 8899 §4–5](https://www.rfc-editor.org/rfc/rfc8899.html#section-4)。裸 UDP 本身没有确认机制，不能只调用发送接口便声称完成探测。

假设在同一方向与路径上，不分片的探测 IP 分组总长分别为 1200、1400 字节，包含 IP 与传输首部：1200 字节探测收到可靠确认，1400 字节探测未被确认。前者支持“当时该路径能交付这个大小”；后者还可能是普通丢包或确认丢失；若实际路径发生变化，上述路径稳定前提也不再成立。算法需要重复探测、较小基线和连通性判断，不能由一次失败断言“PMTU 就是 1399”。有效 ICMP 可以加快判断，但仍要与探测状态对应。

MSS 调整可影响经过相应处理点的 TCP 分段预算；它不能修复所有 UDP 数据报、错误的隧道封装或每次路径变化。确定实际失败层后再选择处理方式，并重新验证大小、方向与业务交付。

## 自检

1. 给定 1500、60、40、20 字节，1440 与 1380 各约束哪一层？
2. 为什么一次写入 100 KiB 不要求路径 MTU 至少是 100 KiB？
3. IPv6 中途遇到较小链路时，谁通知发送方？路由器会代为分片吗？
4. 小 ping 成功、1400 字节探测一次失败，能否得出精确 PMTU？为什么？
5. 为什么只调整 TCP MSS 不能保证 UDP/[QUIC](../../glossary/networking.md#networking.quic) 与隧道全部恢复？

## 来源与核查

2026-10-26 核查 RFC 1191、8201、4821、8899 的固定文本，范围为经典 PMTUD、分组化探测及首部预算。本文为 source-checked 概念文章，数字均为纸面计算；未验证具体操作系统、隧道、ICMP 规则、黑洞恢复或实际报文尺寸。
