<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机网络与协议

建议优先级：P0。目标：从[域名解析](../../glossary/networking.md#networking.dns)到应用响应，分层解释连接和传输。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么客户端超时不能证明后端执行失败？

## 已有正文

- [CDN 与 WAF：边缘命中和请求放行分别证明什么](cdn-edge-caches-and-waf-boundaries.md)：沿边缘缓存键、身份范围、失效和源站路径，区分 [CDN](../../glossary/networking.md#networking.cdn-waf) 分发、WAF 检查与应用[授权](../../glossary/security.md#security.identity)的责任。
- [拥塞算法与队列管理：带宽充足为什么仍然延迟很高](congestion-algorithms-aqm-and-ecn.md)：区分 cwnd、[pacing](../../glossary/networking.md#networking.congestion-algorithms)、[带宽时延积](../../glossary/networking.md#networking.queue-management)和[排队](../../glossary/performance.md#performance.queueing)，对照 Reno、CUBIC、BBR 的控制思路及 AQM、调度与 ECN 的职责。
- [连接生命周期实验：复用、池等待与超时后的状态](connection-lifecycle-lab.md)：用真实回环 [HTTP/1.1](../../glossary/networking.md#networking.http-versions) 连接对照七类生命周期场景，保存连接标识、正文摘要和客户端服务端事件。
- [DNS 缓存与地址选择：改了解析为什么还访问旧地址](dns-caching-and-address-selection.md)：区分权威记录、递归与本地缓存、负缓存和候选地址，解释 TTL 为何不是全局切流时钟。
- [HTTP 复用与连接池：请求为什么还没发出去就超时](http-reuse-pools-and-timeouts.md)：区分连接、HTTP 流和池等待，解释响应体释放、空闲回收、代理分段及各类超时的范围。
- [HTTPS 请求链路：从地址输入到响应可用经历了什么](https-request-lifecycle.md)：把解析、连接、安全传输、HTTP、服务端处理与页面呈现分层，建立请求排查的共同语言。
- [IPv6 与邻居发现：有了地址为什么还不一定能发出去](ipv6-addresses-slaac-and-neighbor-discovery.md)：分开解释地址作用范围、SLAAC、链路判断、默认路由和邻居状态，说明自动配置、可达性及安全边界。
- [IPv6 源地址、隐私与接入防护：能发包不等于身份可信](ipv6-source-selection-privacy-and-first-hop-protection.md)：解释源/目的地址选择、稳定与[临时地址](../../glossary/networking.md#networking.ipv6-source-privacy)及寿命，区分 DAD、[RA Guard](../../glossary/networking.md#networking.first-hop-protection)、源地址约束与应用身份授权。
- [NAT、代理与负载均衡：流量经过入口后谁在与谁通信](nat-proxies-and-l4-l7-load-balancing.md)：区分地址转换、连接代理与流量分配，沿元组、[TLS](../../glossary/networking.md#networking.tls)、健康探测、摘流和来源信任链解释入口的能力与失败边界。
- [网络分层、IP 与路由：一个分组怎样跨过子网](network-layers-ip-subnets-and-routing.md)：从逐跳封装与[下一跳](../../glossary/networking.md#networking.routing)出发，解释 [IP](../../glossary/networking.md#networking.transport)、MAC、端口、[IPv4 前缀](../../glossary/networking.md#networking.ip-prefix)和最长前缀匹配，并说明返回路径、跳数限制及 [MTU](../../glossary/networking.md#networking.path-mtu) 的边界。
- [路径 MTU 与隧道：为什么小包能通大包却卡住](path-mtu-icmp-tunnels-and-black-holes.md)：区分链路 MTU、路径 MTU、MSS 与应用大小，用封装预算和探测推演解释 ICMP 反馈、PMTUD 与黑洞边界。
- [策略与动态路由：选路、转发与收敛为什么是三件事](policy-routing-control-planes-and-convergence.md)：区分策略规则、路由信息与转发表，用双出口推演解释跨表选择、[BGP](../../glossary/networking.md#networking.policy-routing) 本地策略、异步收敛及现存连接边界。
- [TCP 流量控制与拥塞控制：发送变慢到底受谁限制](tcp-flow-control-and-congestion.md)：用接收窗口、拥塞窗口和在途数据区分接收端背压与路径限制，解释 RTT、丢包判断、重传和应用排队的边界。
- [TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么](tcp-tls-and-connection-states.md)：区分传输建立、安全协商和业务确认，解释 FIN、RST、TIME_WAIT、保活与连接失效的边界。
- [UDP 与 QUIC：数据报、可靠流与业务完成怎样分开](udp-quic-streams-and-delivery-boundaries.md)：从 UDP 消息边界到 [QUIC](../../glossary/networking.md#networking.quic) 流、丢包恢复、TLS、路径迁移与 HTTP/3，解释传输接受和业务完成的不同保证。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [OSI / TCP-IP Model](../../glossary/networking.md#networking.network-model) | 网络职责分层和封装。 |
| [IP / TCP / UDP](../../glossary/networking.md#networking.transport) | 寻址、字节流可靠传输和数据报。 |
| [DNS / TTL](../../glossary/networking.md#networking.dns) | 域名解析与记录缓存有效期。 |
| [TCP Handshake](../../glossary/networking.md#networking.tcp-handshake) | 连接建立及连接状态。 |
| [Flow Control / Congestion Control](../../glossary/networking.md#networking.transport-control) | 接收方能力约束与网络拥塞调节。 |
| [TLS / HTTPS / PKI](../../glossary/networking.md#networking.tls) | 传输加密、身份校验与证书信任。 |
| [HTTP/1.1 / HTTP/2 / HTTP/3](../../glossary/networking.md#networking.http-versions) | HTTP 传输机制和多路复用差异。 |
| [QUIC](../../glossary/networking.md#networking.quic) | 在UDP上建立安全连接、可靠多流与丢失/资源控制的传输协议。 |
| [Keep-Alive / Connection Reuse](../../glossary/networking.md#networking.keepalive) | 连接复用、空闲管理和连接成本。 |
| [Proxy / Reverse Proxy](../../glossary/networking.md#networking.proxy) | 代理客户端或服务端接收请求。 |
| [Load Balancer / L4 / L7](../../glossary/networking.md#networking.load-balancer) | 按传输层或应用层信息分发流量。 |
| [CDN / WAF](../../glossary/networking.md#networking.cdn-waf) | 在边缘分发并按范围复用响应，以及按应用请求规则执行防护的两类机制。 |
| [CIDR / IP Prefix / Subnet Mask](../../glossary/networking.md#networking.ip-prefix) | 用地址前部的有效位及长度表示地址集合；IPv4 掩码可用于提取这一前缀。 |
| [IP Routing / Next Hop / Longest Prefix Match](../../glossary/networking.md#networking.routing) | 根据转发信息为目的地址选择出接口与下一跳，在已选定表中优先采用更具体的匹配前缀。 |
| [ARP / IPv6 Neighbor Discovery](../../glossary/networking.md#networking.neighbor-discovery) | 在当前链路上取得邻居的链路地址等信息，IPv4 以太网常用 ARP，IPv6 使用 Neighbor Discovery。 |
| [NAT / SNAT / DNAT / NAPT](../../glossary/networking.md#networking.nat) | 在地址域之间改写 IP 地址及适用端口的机制；源/目的转换方向与是否转换端口是不同维度。 |
| [Policy Routing / BGP / RIB / FIB](../../glossary/networking.md#networking.policy-routing) | 按政策选择路由、传播可达性与执行转发的不同层次。 |
| [MTU / PMTU / MSS / PMTUD](../../glossary/networking.md#networking.path-mtu) | 区分链路/路径分组大小、TCP 数据预算与路径大小发现。 |
| [Reno / CUBIC / BBR](../../glossary/networking.md#networking.congestion-algorithms) | 以窗口、发送节奏及拥塞/交付观测调整发送的算法思路。 |
| [AQM / ECN / BDP](../../glossary/networking.md#networking.queue-management) | 区分管道在途量、队列管理、调度与拥塞标记反馈。 |
| [IPv6 Source Address Selection / Temporary Address](../../glossary/networking.md#networking.ipv6-source-privacy) | 根据地址状态、作用范围与政策选择源，并用不同生成方式限制地址关联。 |
| [RA Guard / Source Address Validation](../../glossary/networking.md#networking.first-hop-protection) | 约束本地链路的路由通告与源地址使用，防止部分伪造或误配。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
