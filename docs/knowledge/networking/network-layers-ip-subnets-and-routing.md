---
id: "kb-networking-ip-routing"
title: "网络分层、IP 与路由：一个分组怎样跨过子网"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "从逐跳封装与下一跳出发，解释 IP、MAC、端口、IPv4 前缀和最长前缀匹配，并说明返回路径、跳数限制及 MTU 的边界。"
created: "2026-10-22"
updated: "2026-10-26"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-https-request"]
related: ["kb-networking-dns-caching", "kb-networking-connection-states", "kb-networking-flow-congestion", "kb-networking-nat-proxy-lb", "kb-security-ssrf", "kb-networking-udp-quic", "kb-networking-ipv6-neighbors", "kb-networking-policy-convergence", "kb-networking-path-mtu"]
tags: ["ip", "cidr", "routing", "neighbor-discovery", "mtu"]
---

# 网络分层、IP 与路由：一个分组怎样跨过子网

学习入口：客户端已经知道服务器的 [IP](../../glossary/networking.md#networking.transport) 地址，为什么还需要网关和 MAC 地址？同样是“网络通了”，为何小消息能走、大消息却可能卡住？需要把最终目的地、当前[下一跳](../../glossary/networking.md#networking.routing)和每层的交付单位分开。

前置：[HTTPS 请求链路](https-request-lifecycle.md)。本文限定常见以太网承载 IP 的单播教学路径，重点是 [IPv4 前缀](../../glossary/networking.md#networking.ip-prefix)与逐跳转发，并对照 IPv6 的[邻居发现](../../glossary/networking.md#networking.neighbor-discovery)、`Hop Limit` 和分片差异。不展开[动态路由](../../glossary/networking.md#networking.policy-routing)协议、隧道和云网络配置；所有拓扑、地址、端口与长度均为纸面假设，没有发送分组或更改路由。

策略规则、路由信息与实际转发的区别继续见[策略与动态路由](policy-routing-control-planes-and-convergence.md)；分组长度与隧道预算见[路径 MTU](path-mtu-icmp-tunnels-and-black-holes.md)。

## 分层说明职责，封装说明谁装着谁

本文按互联网协议族区分四类职责，不强求每个协议与 [OSI](../../glossary/networking.md#networking.network-model) 七层逐项对应。互联网分层依据见 [RFC 1122 §1.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-1.1.3)。

| 职责 | 本文例子 | 交付或判断的对象 |
| --- | --- | --- |
| 应用 | HTTP | 请求、响应与业务含义 |
| 传输 | TCP / UDP | 传输端点及数据交付方式 |
| 网际 | IPv4 / IPv6 | 用 IP 地址与转发信息把分组送向目的地 |
| 链路 | 以太网 | 在当前链路上传送帧 |

IP 提供尽力而为的分组交付，不单独保证送达、顺序或不重复；需要的恢复机制由相应上层协议承担，见 [RFC 1122 §1.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-1.1.3)。

例如 TCP 上的应用数据可以被 [TLS](../../glossary/networking.md#networking.tls) 保护，再由 IP 与链路承载。下图只表示一次发送的逻辑包裹，不表示一条 HTTP 消息、TLS 记录和 TCP 分段恰好对齐：

```text
以太网帧：[链路头 | IP 头 | TCP 头 | 一段 TCP 字节 | 链路尾]
```

以太网承载 IPv4 时，帧的数据区域包含 IP 头与 IP 数据；见 [RFC 894](https://www.rfc-editor.org/rfc/rfc894.html)。经过路由器转到另一条以太网链路时，新的帧承载继续转发的 IP 分组。普通 IP 转发不要求路由器拼好整条 HTTP 消息，也不自动建立一条新的 TCP 连接。

同一以太网链路可以经过交换设备延伸，并非必须共用一根网线。下面讲的“逐跳换帧”，指跨路由边界的链路封装；不能据此声称经过每台二层交换机都会更换 IP 源地址或消耗一次 IP 跳数。

## IP 地址、MAC 地址和端口回答不同问题

| 标识 | 在本文范围内回答什么 | 不能直接证明什么 |
| --- | --- | --- |
| IP 源/目的地址 | 分组来自哪里、发往哪个 IP 目的地 | 用户身份、物理位置或访问权限 |
| 以太网源/目的 MAC | 当前帧在这条链路上由谁发送、交给谁 | 跨多个路由器后的最终服务器身份 |
| TCP/UDP 源/目的端口 | 在相应传输协议和 IP 端点下如何区分通信端点 | 某个端口必然运行特定服务，或已经获得[授权](../../glossary/security.md#security.identity) |

TCP 与 UDP 各有端口字段，端口号要与协议和地址一起解释；TCP 443 和 UDP 443 不是同一个传输端点。字段依据见 [RFC 9293 §3.1](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.1)和 [RFC 768](https://www.rfc-editor.org/rfc/rfc768.html)。IP 头的协议指示信息帮助接收端继续分派上层处理。

若目标不在当前直连范围，主机通常把帧交给网关的 MAC，但 IP 目的地址仍写最终目标。下一跳路由器负责继续转发，不会因为收到帧就成为本次 TCP 通信的应用服务器；本地/远端与下一跳的区分见 [RFC 1122 §3.3.1](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.3.1)。涉及地址转换或代理时，需另看[网络中介的边界](nat-proxies-and-l4-l7-load-balancing.md)。

## IPv4 前缀怎样界定地址集合

CIDR 用 `/n` 表示 IPv4 地址最前面的 n 个有效前缀位。地址不是只看前三个十进制数是否相同；前缀长度必须一起给出。记法依据见 [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1)。

纸面算例：A 配置为 `192.0.2.10/26`，对应掩码 `255.255.255.192`。最后一个八位组的计算是：

```text
10：  00001010
192： 11000000
按位与 00000000 → 前缀 192.0.2.0/26
剩余位数：32 - 26 = 6；地址数：2^6 = 64
范围：192.0.2.0 至 192.0.2.63
```

因此 `192.0.2.20` 在这个集合里，`192.0.2.70` 不在；后者属于 `192.0.2.64/26` 的范围。在这个普通 IPv4 广播子网的假设下，首地址为网络地址、末地址为子网广播地址，不能把这 64 个数都当作普通主机地址；特殊地址规则见 [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.2.1.3)。也不能把“总数减二”推广到每个前缀：点到点 `/31` 有明确例外，见 [RFC 3021 §2.1](https://www.rfc-editor.org/rfc/rfc3021.html#section-2.1)；主机路由 `/32` 等用途另需区分，本文不展开配置。

本例地址来自 [RFC 5737 的文档保留网段](https://www.rfc-editor.org/rfc/rfc5737.html#section-3)，只为说明位运算与路径，不是部署建议。一个前缀表示地址集合或转发匹配范围，不证明设备位于同一机房，也不单独形成可信网络或安全边界。云 [VPC](../../glossary/devops.md#devops.cloud-network)、云子网和安全组还包含平台资源与访问策略，不能由这次前缀计算推导完成。

## 路由先给下一跳，再解析它的链路地址

转发信息告诉节点：目的地址匹配哪个前缀，应从哪个接口发送，下一跳是直连目标还是另一个路由器。**下一跳只解决接下来交给谁，不承诺全程可达。** 路由来源及动态协议如何形成这些信息，不在本文范围。

在已选定的转发表中，通常按目的地址选择最长匹配前缀：匹配的有效位越多，范围越具体。依据见 [RFC 4632 §5.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-5.1)。同前缀的多个候选、路由优先级和等价多路径还需按实现处理；策略路由也可能先按源地址或其他条件选择表。Linux 的这一额外边界见 [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html)，不能把不同策略表中的前缀混在一起做一次最长匹配。

以下是 R1 **同一张已选表**的教学条目；假设两个上联及各下一跳均已配置可达，没有额外策略和过滤：

| 目的前缀 | 接口 / 下一跳 |
| --- | --- |
| `192.0.2.0/26` | A 所在链路，直连 |
| `198.51.100.0/30` | 上联 1，直连；R1 地址为 `.1` |
| `198.51.100.4/30` | 上联 2，直连；R1 地址为 `.5` |
| `203.0.113.0/24` | 上联 1，经 `198.51.100.2`，即 R2 |
| `203.0.113.64/26` | 上联 2，经 `198.51.100.6`，即 R3 |
| `0.0.0.0/0` | 默认经 R2 |

目的 `203.0.113.70` 同时匹配 `/26`、`/24` 和 `/0`，选 `/26` 经 R3。不能因为默认路由在表中排得更早，或宽前缀看起来“距离更短”，就先选它。`/0` 匹配所有 IPv4 地址，在没有更具体适用条目时才承担兜底作用；没有匹配项也没有默认项时，不能凭空知道下一跳。

选定上联 2 之后，R1 需要的是 R3 在该链路的地址，而非远端 B 的 MAC。IPv4 在以太网上可通过 ARP 建立邻居 IP 与链路地址的映射；映射可缓存，不必每个数据分组都重新广播查询。ARP 的目标是当前链路上的地址解析，不是为远程目标寻找整条路径，见 [RFC 826](https://www.rfc-editor.org/rfc/rfc826.html)。

IPv6 使用基于 ICMPv6 的 Neighbor Discovery，包含链路地址解析、路由器发现与邻居可达性维护，见 [RFC 4861 §3](https://www.rfc-editor.org/rfc/rfc4861.html#section-3)。也不要仅凭自己地址的前缀就推定另一 IPv6 地址必在链路上：IPv6 的地址配置与 on-link 信息有区别，需结合实际前缀/路由信息判断，澄清见 [RFC 5942](https://www.rfc-editor.org/rfc/rfc5942.html)。ARP/ND 得到映射不等于完成对应用身份的认证。

## 把一次转发和返回路径画完整

继续使用上述教学配置，假设 A 的默认网关为 `192.0.2.1`，B 是 `203.0.113.70/26`，R3 面向 B 的地址为 `203.0.113.65`。所有链路均为以太网，不使用 [NAT](../../glossary/networking.md#networking.nat)、代理、隧道或分片；省略交换机：

```text
A 192.0.2.10
  → R1 192.0.2.1 | 198.51.100.5
  → R3 198.51.100.6 | 203.0.113.65
  → B 203.0.113.70

R2 位于另一条上联，本次没有被最长前缀匹配选中。
```

| 发送位置 | 当前以太网帧的源 → 目的 | 帧内 IPv4 源 → 目的 |
| --- | --- | --- |
| A 发出 | A 的 MAC → R1 面向 A 的 MAC | `192.0.2.10` → `203.0.113.70` |
| R1 转发 | R1 上联 2 的 MAC → R3 上联的 MAC | 同上 |
| R3 转发 | R3 面向 B 的 MAC → B 的 MAC | 同上 |

R1、R3 各自从收到的链路封装中取得 IP 分组，再用相应出接口的封装继续发送；IPv4 头中的跳数限制等字段会变化，不能说整个 IP 头逐字节不变。该处理边界见 [RFC 1812 §5.2.1](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.1)。在本例的限制下，TCP 源/目的端口也不会因普通路由转发而更换。

返回报文以 A 为目的地址，B 与沿途路由器重新查自己的转发信息，不携带“沿刚才路径原路返回”的一般保证。本例还需假设 B 经 R3 返回，且 R3 有 `192.0.2.0/26` 经 `198.51.100.5` 的路由；只有正向表是不够的。真实网络中返回路径可以不对称；这不自动构成协议错误，但可能与有状态中介的部署约束发生冲突。

失败时逐层问：选了哪张表和哪条前缀？下一跳是否真的在所选链路可达？邻居映射是否可用？下一跳能否继续转发？返回方向是否也有路径？“路由条目存在”与“收到了业务响应”之间还有这些条件。

## 跳数限制与 MTU 处理两种不同风险

IPv4 的 `TTL` 限制分组存活，路由转发时至少减一，降到零就丢弃；实际常表现为跳数上限。它不能证明多久收到响应，更不是 [DNS](../../glossary/networking.md#networking.dns) 记录缓存期限。依据见 [RFC 1812 §5.3.1](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.3.1)。若上述路径初始 `TTL=64`，并假设每次转发只减一，R1 发出为 63，R3 发出为 62。IPv6 的 `Hop Limit` 则明确定义每个转发节点减一，见 [RFC 8200 §3](https://www.rfc-editor.org/rfc/rfc8200.html#section-3)。纯二层交换不属于这些 IP 转发跳。

[MTU](../../glossary/networking.md#networking.path-mtu) 限制链路能承载的 IP 分组大小；IP 层 MTU 不等于应用正文长度或带全部链路头尾的帧长。路径 MTU 是该方向路径各链路 MTU 的最小值。教学假设三段分别为 1500、1400、1500 字节，则路径 MTU 为 1400；若 IPv4 头与 TCP 头都假设为 20 字节、无选项及额外封装，单个这样的 IP 分组最多放 `1400 - 20 - 20 = 1360` 字节 TCP 数据。这不是所有机器通用的 MSS 或应用消息上限。

IPv4 分组超过出口 MTU 时，是否允许路由器分片受 `DF` 等条件约束；`DF` 置位而无法转发时，会丢弃并按规则产生“需要分片”的 ICMP 错误，经典路径 MTU 发现据此调整发送大小。基本机制见 [RFC 1191 §2–4](https://www.rfc-editor.org/rfc/rfc1191.html#section-2)。IPv6 路由器不沿途分片，由源节点处理必要的分片；过大的分组通常需要 ICMPv6 Packet Too Big 反馈，见 [RFC 8200 §4.5](https://www.rfc-editor.org/rfc/rfc8200.html#section-4.5)和 [RFC 8201 §3](https://www.rfc-editor.org/rfc/rfc8201.html#section-3)。

ICMP 不只是诊断工具的回显报文，还承担网络错误反馈；收到反馈也不等于应用动作已取消或目标服务健康。若过滤使关键反馈到不了发送端，可能出现小报文正常、较大传输停滞的路径 MTU 黑洞，见 [RFC 8201 §1](https://www.rfc-editor.org/rfc/rfc8201.html#section-1)。这是一个排查方向，不是看到大请求慢就能下的唯一结论；现代传输也可使用分组化层的探测机制，本文不展开算法。

路径大小、UDP 数据报与可靠多流的衔接，继续见[UDP 与 QUIC](udp-quic-streams-and-delivery-boundaries.md)。IP/UDP 头、[QUIC](../../glossary/networking.md#networking.quic) 包与应用数据各占空间，路径迁移也不能绕过新路径验证及拥塞责任。

IPv6 的地址范围、自动配置、on-link 与默认路由独立关系，继续见[IPv6 与邻居发现](ipv6-addresses-slaac-and-neighbor-discovery.md)。有地址、DAD 成功和邻居可达，各不代表整条业务路径已经成立。

## 自检、关联与核查范围

- A 访问不在本地直连范围的 B 时，第一帧的目的 MAC 和 IP 目的地址分别属于谁？
- `192.0.2.70` 是否属于 `192.0.2.0/26`？怎样从二进制和地址范围各验证一次？
- 本例目的地址为何经 R3 而非默认 R2？如果系统先选了另一张策略表，哪些推论需要重做？
- 一次正向发送成功，为什么不能直接推导返回可达？跨路由器时哪些头部标识变化、哪些在本例保持？
- 大小为 1500 字节的 IPv4 分组遇到 1400 字节链路且 `DF` 置位时，为什么不能总指望路由器替它切开？

[DNS 与地址选择](dns-caching-and-address-selection.md)解释名称怎样给出候选地址，DNS 的 `TTL` 与本篇 IP 字段承担不同职责；[TCP/TLS 状态](tcp-tls-and-connection-states.md)继续说明传输和身份建立；[流量与拥塞控制](tcp-flow-control-and-congestion.md)处理端点能力与网络负载；[NAT、代理和负载均衡](nat-proxies-and-l4-l7-load-balancing.md)解释本例排除的中介如何改变地址、连接和信任边界。[SSRF 防护](../security/ssrf-url-resolution-and-egress-boundaries.md)还要求对实际目的地址和出口权限做授权，不能把“有路由”当成“允许访问”。

2026-10-22 实际联网核查上述 RFC 与 iproute2 的 `ip-rule` 文档，覆盖互联网分层、以太网承载、端口字段、CIDR/最长前缀、ARP、IPv6 ND/on-link、逐跳转发、跳数限制及经典路径 MTU 反馈。地址、拓扑、表项、位运算和长度均为教学推演，状态为 `source-checked`。未执行 ping、抓包、邻居表/路由变更、MTU 或性能实验；未验证真实主机配置。IPv6 自动配置、策略查询/收敛与路径大小/隧道探测的概念已在关联专题展开；具体路由协议与设备规则、交换环路、VLAN、安全邻居发现、分片重组、隧道实现和真实故障仍需深入或实测。
