<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机网络与协议词汇表

本页解释 22 组术语，按[完整术语索引](../glossary.md#networking)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [计算机网络与协议文章](../knowledge/networking/index.md)

## 本页术语

- [OSI / TCP-IP Model](#networking.network-model)
- [IP / TCP / UDP](#networking.transport)
- [DNS / TTL](#networking.dns)
- [TCP Handshake](#networking.tcp-handshake)
- [Flow Control / Congestion Control](#networking.transport-control)
- [TLS / HTTPS / PKI](#networking.tls)
- [HTTP/1.1 / HTTP/2 / HTTP/3](#networking.http-versions)
- [QUIC](#networking.quic)
- [Keep-Alive / Connection Reuse](#networking.keepalive)
- [Proxy / Reverse Proxy](#networking.proxy)
- [Load Balancer / L4 / L7](#networking.load-balancer)
- [CDN / WAF](#networking.cdn-waf)
- [CIDR / IP Prefix / Subnet Mask](#networking.ip-prefix)
- [IP Routing / Next Hop / Longest Prefix Match](#networking.routing)
- [ARP / IPv6 Neighbor Discovery](#networking.neighbor-discovery)
- [NAT / SNAT / DNAT / NAPT](#networking.nat)
- [Policy Routing / BGP / RIB / FIB](#networking.policy-routing)
- [MTU / PMTU / MSS / PMTUD](#networking.path-mtu)
- [Reno / CUBIC / BBR](#networking.congestion-algorithms)
- [AQM / ECN / BDP](#networking.queue-management)
- [IPv6 Source Address Selection / Temporary Address](#networking.ipv6-source-privacy)
- [RA Guard / Source Address Validation](#networking.first-hop-protection)

<a id="networking.network-model"></a>

## OSI / TCP-IP Model

**ID：** `networking.network-model` · **建议优先级：** P0

**别名 / 检索词：** OSI、TCP-IP Model、网络分层、封装

**简释：** 网络职责分层和封装。

OSI 是七层参考模型，TCP/IP 模型按互联网协议族组织职责。分层帮助定位封装和接口边界，实际协议与设备并不总能严格一一对应。

**例子：** HTTP 消息经 TLS 保护后由 TCP 承载，再由 IP 路由到目标主机。

**深入阅读：** [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md)

<a id="networking.transport"></a>

## IP / TCP / UDP

**ID：** `networking.transport` · **建议优先级：** P0

**别名 / 检索词：** IP、TCP、UDP、数据报、字节流

**简释：** 寻址、字节流可靠传输和数据报。

IP 提供分组寻址和路由；TCP 在连接内提供可靠、有序字节流；UDP 提供数据报传输。TCP 不保留应用消息边界，UDP 也不替应用保证送达。

**例子：** 一次 TCP 读取可能只得到半条业务消息，需要应用自行分帧。

**深入阅读：** [TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么](../knowledge/networking/tcp-tls-and-connection-states.md) · [TCP 流量控制与拥塞控制：发送变慢到底受谁限制](../knowledge/networking/tcp-flow-control-and-congestion.md) · [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md) · [UDP 与 QUIC：数据报、可靠流与业务完成怎样分开](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md) · [IPv6 与邻居发现：有了地址为什么还不一定能发出去](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md)

<a id="networking.dns"></a>

## DNS / TTL

**ID：** `networking.dns` · **建议优先级：** P0

**别名 / 检索词：** DNS、TTL、域名解析

**简释：** 域名解析与记录缓存有效期。

DNS 将名称查询解析到记录；TTL 限定记录缓存期限。递归解析、应用缓存和连接复用形成不同层次，DNS 变化不等于既有连接立即改向。

**例子：** 域名记录更新后，旧连接仍可继续向原地址发送请求。

**深入阅读：** [HTTPS 请求链路：从地址输入到响应可用经历了什么](../knowledge/networking/https-request-lifecycle.md) · [DNS 缓存与地址选择：改了解析为什么还访问旧地址](../knowledge/networking/dns-caching-and-address-selection.md) · [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md)

<a id="networking.tcp-handshake"></a>

## TCP Handshake

**ID：** `networking.tcp-handshake` · **建议优先级：** P0

**别名 / 检索词：** TCP Handshake、三次握手、TCP 握手

**简释：** 连接建立及连接状态。

TCP 建连通过 SYN、SYN-ACK、ACK 协调序列号及连接状态。连接建立只说明传输层准备就绪，不能证明 TLS 身份校验或业务认证成功。

**例子：** TCP 已连通而 TLS 握手失败时，问题不应归为 DNS 解析失败。

**深入阅读：** [TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么](../knowledge/networking/tcp-tls-and-connection-states.md)

<a id="networking.transport-control"></a>

## Flow Control / Congestion Control

**ID：** `networking.transport-control` · **建议优先级：** P0

**别名 / 检索词：** Flow Control、Congestion Control、流量控制、拥塞控制

**简释：** 接收方能力约束与网络拥塞调节。

流量控制围绕接收方缓冲和处理能力，拥塞控制围绕路径容量与拥塞信号。两者都可能限制发送速率，但观察对象和调节机制不同。

**例子：** 接收窗口收缩可能源于应用读得慢，丢包后的拥塞窗口下降则针对网络路径。

**深入阅读：** [TCP 流量控制与拥塞控制：发送变慢到底受谁限制](../knowledge/networking/tcp-flow-control-and-congestion.md) · [拥塞算法与队列管理：带宽充足为什么仍然延迟很高](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md)

<a id="networking.tls"></a>

## TLS / HTTPS / PKI

**ID：** `networking.tls` · **建议优先级：** P0

**别名 / 检索词：** TLS、HTTPS、PKI、传输加密、证书信任

**简释：** 传输加密、身份校验与证书信任。

TLS 为连接提供机密性、完整性和对端身份校验机制；HTTPS 是在 TLS 上使用 HTTP；PKI 用证书链表达公钥与身份的信任关系。仍需校验名称、用途与有效性。

**例子：** 证书链可信但主机名不匹配时，客户端仍应拒绝该 HTTPS 连接。

**深入阅读：** [HTTPS 请求链路：从地址输入到响应可用经历了什么](../knowledge/networking/https-request-lifecycle.md) · [TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么](../knowledge/networking/tcp-tls-and-connection-states.md) · [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md)

<a id="networking.http-versions"></a>

## HTTP/1.1 / HTTP/2 / HTTP/3

**ID：** `networking.http-versions` · **建议优先级：** P0

**别名 / 检索词：** HTTP/1.1、HTTP/2、HTTP/3、HTTP 多路复用

**简释：** HTTP 传输机制和多路复用差异。

HTTP/1.1 通常通过多个连接扩展并发；HTTP/2 在一条 TCP 连接中复用流；HTTP/3 使用 QUIC。复用减少连接开销，但不消除连接级资源竞争。

**例子：** HTTP/2 的多个流仍共享 TCP 丢包恢复带来的传输等待。

**深入阅读：** [HTTPS 请求链路：从地址输入到响应可用经历了什么](../knowledge/networking/https-request-lifecycle.md) · [HTTP 复用与连接池：请求为什么还没发出去就超时](../knowledge/networking/http-reuse-pools-and-timeouts.md) · [UDP 与 QUIC：数据报、可靠流与业务完成怎样分开](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md)

<a id="networking.quic"></a>

## QUIC

**ID：** `networking.quic` · **建议优先级：** P0

**别名 / 检索词：** QUIC、QUIC v1

**简释：** 在UDP上建立安全连接、可靠多流与丢失/资源控制的传输协议。

QUIC将包传输与各流字节交付分开，减少跨流的传输队头等待，但流仍共享连接额度、拥塞和端点资源。TLS握手、0-RTT重放、路径验证及连接状态各有条件；HTTP/3是上层映射，可选DATAGRAM又有不可靠交付边界。传输确认不等于业务提交。

**例子：** A流缺少中间字节时，独立B流可交付已连续的数据；若连接额度或网络容量耗尽，B仍需等待。

**深入阅读：** [HTTP 复用与连接池：请求为什么还没发出去就超时](../knowledge/networking/http-reuse-pools-and-timeouts.md) · [UDP 与 QUIC：数据报、可靠流与业务完成怎样分开](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md)

<a id="networking.keepalive"></a>

## Keep-Alive / Connection Reuse

**ID：** `networking.keepalive` · **建议优先级：** P0

**别名 / 检索词：** Keep-Alive、Connection Reuse、连接复用、长连接

**简释：** 连接复用、空闲管理和连接成本。

连接复用让多次请求共享已建立连接，减少建连和握手成本。HTTP 持久连接、TCP keepalive 探活及连接池空闲策略是不同机制。

**例子：** 服务端先关闭空闲连接时，连接池需识别失效并在允许范围内重新建连。

**深入阅读：** [HTTPS 请求链路：从地址输入到响应可用经历了什么](../knowledge/networking/https-request-lifecycle.md) · [TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么](../knowledge/networking/tcp-tls-and-connection-states.md) · [HTTP 复用与连接池：请求为什么还没发出去就超时](../knowledge/networking/http-reuse-pools-and-timeouts.md) · [连接生命周期实验：复用、池等待与超时后的状态](../knowledge/networking/connection-lifecycle-lab.md)

<a id="networking.proxy"></a>

## Proxy / Reverse Proxy

**ID：** `networking.proxy` · **建议优先级：** P0

**别名 / 检索词：** Proxy、Reverse Proxy、正向代理、反向代理

**简释：** 代理客户端或服务端接收请求。

正向代理代表客户端访问目标，反向代理代表服务端接收并转发请求。代理可能终止 TLS、缓存或重试，因此会改变可见连接和失败边界。

**例子：** 浏览器经企业代理访问外网；网站经反向代理把请求转到应用实例。

**深入阅读：** [HTTPS 请求链路：从地址输入到响应可用经历了什么](../knowledge/networking/https-request-lifecycle.md) · [NAT、代理与负载均衡：流量经过入口后谁在与谁通信](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md)

<a id="networking.load-balancer"></a>

## Load Balancer / L4 / L7

**ID：** `networking.load-balancer` · **建议优先级：** P0

**别名 / 检索词：** Load Balancer、L4、L7、负载均衡

**简释：** 按传输层或应用层信息分发流量。

L4 负载均衡主要根据传输层连接信息分流，L7 可解析 HTTP 等应用协议。分流算法、健康状态和会话保持共同决定流量去向。

**例子：** L7 入口可按 URL 路径选择服务，再按实例健康状态分配请求。

**深入阅读：** [NAT、代理与负载均衡：流量经过入口后谁在与谁通信](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md)

<a id="networking.cdn-waf"></a>

## CDN / WAF

**ID：** `networking.cdn-waf` · **建议优先级：** P0

**别名 / 检索词：** CDN、WAF、内容分发网络、Web 应用防火墙

**简释：** 在边缘分发并按范围复用响应，以及按应用请求规则执行防护的两类机制。

CDN 的分发与缓存需要正确的键、身份共享范围、新鲜度及撤回策略；WAF 只依据可见内容和实际执行的规则作出防护动作。命中不证明源站刚执行了权限检查，规则放行也不证明业务访问合法。还要约束源站绕过路径和代理信任，产品覆盖与检查窗口按配置核验。

**例子：** 账户响应只按URL共享可能把甲的数据交给乙；WAF规则未命中不补足对象权限，源站也须限制未经过防护的入口。

**深入阅读：** [CDN 与 WAF：边缘命中和请求放行分别证明什么](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md)

<a id="networking.ip-prefix"></a>

## CIDR / IP Prefix / Subnet Mask

**ID：** `networking.ip-prefix` · **建议优先级：** P0

**别名 / 检索词：** CIDR、IP Prefix、IP 前缀、IP前缀、IPv4 前缀、地址前缀、子网掩码、Subnet Mask

**简释：** 用地址前部的有效位及长度表示地址集合；IPv4 掩码可用于提取这一前缀。

CIDR /n 表示最前面 n 个有效位，必须结合地址和长度判断范围。用于路由匹配的前缀不是物理位置或安全边界，IPv6 地址配置也不能自动当成 on-link 信息；云子网和安全组另有平台资源与访问策略。

**例子：** 192.0.2.10/26 的掩码为 255.255.255.192，所属前缀 192.0.2.0/26 共含 64 个地址；192.0.2.70 位于另一个 /26 范围。

**深入阅读：** [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md) · [IPv6 与邻居发现：有了地址为什么还不一定能发出去](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) · [策略与动态路由：选路、转发与收敛为什么是三件事](../knowledge/networking/policy-routing-control-planes-and-convergence.md) · [路径 MTU 与隧道：为什么小包能通大包却卡住](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md)

<a id="networking.routing"></a>

## IP Routing / Next Hop / Longest Prefix Match

**ID：** `networking.routing` · **建议优先级：** P0

**别名 / 检索词：** IP Routing、Routing、IP 路由、IP路由、路由、路由表、下一跳、Next Hop、最长前缀匹配、Longest Prefix Match

**简释：** 根据转发信息为目的地址选择出接口与下一跳，在已选定表中优先采用更具体的匹配前缀。

下一跳是当前这一步要交付的邻居，可以是目标本身或另一路由器。最长前缀匹配的前提是已确定所用转发表；策略路由、同前缀候选和多路径另需处理。存在正向路由不证明下一跳可达、返回可达或业务获准访问。

**例子：** 同一张表内，203.0.113.70 同时匹配 203.0.113.64/26、203.0.113.0/24 与默认 /0 时，采用 /26 的下一跳。

**深入阅读：** [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md) · [IPv6 与邻居发现：有了地址为什么还不一定能发出去](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) · [策略与动态路由：选路、转发与收敛为什么是三件事](../knowledge/networking/policy-routing-control-planes-and-convergence.md) · [路径 MTU 与隧道：为什么小包能通大包却卡住](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md)

<a id="networking.neighbor-discovery"></a>

## ARP / IPv6 Neighbor Discovery

**ID：** `networking.neighbor-discovery` · **建议优先级：** P1

**别名 / 检索词：** ARP、Address Resolution Protocol、Neighbor Discovery、IPv6 ND、邻居发现、邻居地址解析

**简释：** 在当前链路上取得邻居的链路地址等信息，IPv4 以太网常用 ARP，IPv6 使用 Neighbor Discovery。

先由转发信息确定下一跳，再解析当前链路邻居。IPv6 ND还负责路由器/前缀发现与NUD；SLAAC地址形成、PIO的on-link依据和默认路由器寿命需分别判断。地址分配或收到ND消息不能隐式补出on-link前缀，邻居映射/可达也不代替身份认证或全程业务健康。

**例子：** 主机收到A=1、L=0且Router Lifetime=0的RA，可以按条件形成地址，却未由它取得on-link前缀或默认下一跳；STALE邻居也不等于已经判死。

**深入阅读：** [网络分层、IP 与路由：一个分组怎样跨过子网](../knowledge/networking/network-layers-ip-subnets-and-routing.md) · [IPv6 与邻居发现：有了地址为什么还不一定能发出去](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) · [IPv6 源地址、隐私与接入防护：能发包不等于身份可信](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md)

<a id="networking.nat"></a>

## NAT / SNAT / DNAT / NAPT

**ID：** `networking.nat` · **建议优先级：** P0

**别名 / 检索词：** NAT、SNAT、DNAT、NAPT、网络地址转换、源地址转换、目的地址转换、网络地址端口转换

**简释：** 在地址域之间改写 IP 地址及适用端口的机制；源/目的转换方向与是否转换端口是不同维度。

传统 IPv4 NAT 通过转换关联处理往返流量；SNAT 改源字段、DNAT 改目的字段，NAPT 还使用传输端口区分映射。有状态转换的返回路径、映射生命周期和故障切换需协调。NAT 不自动把通信变为两条由代理终止的 TCP 连接，也不证明用户身份或访问许可。

**例子：** 10.0.0.8:51000 与 10.0.0.9:51000 访问同一远端时，纸面 NAPT 分别映射到同一外部 IP 的 40001 与 40002；返回端口决定恢复到哪台内部主机。

**深入阅读：** [NAT、代理与负载均衡：流量经过入口后谁在与谁通信](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md)

<a id="networking.policy-routing"></a>

## Policy Routing / BGP / RIB / FIB

**ID：** `networking.policy-routing` · **建议优先级：** P1

**别名 / 检索词：** 策略路由、动态路由、控制平面、数据平面、RPDB

**简释：** 按政策选择路由、传播可达性与执行转发的不同层次。

RPDB 按规则决定查询上下文；BGP 按本地政策从候选中选择，RIB/FIB 分别表达路由信息和用于转发的状态。候选收到、实际安装、双向业务恢复不是同一完成点。

**例子：** 源匹配规则先在表100找到默认路由时，main中的更长前缀不会自动参与全局比较。

**深入阅读：** [策略与动态路由：选路、转发与收敛为什么是三件事](../knowledge/networking/policy-routing-control-planes-and-convergence.md)

<a id="networking.path-mtu"></a>

## MTU / PMTU / MSS / PMTUD

**ID：** `networking.path-mtu` · **建议优先级：** P1

**别名 / 检索词：** 路径 MTU、链路 MTU、PLPMTUD、DPLPMTUD、Packet Too Big

**简释：** 区分链路/路径分组大小、TCP 数据预算与路径大小发现。

MTU 与 PMTU 约束特定层次和路径的分组大小，MSS 约束 TCP 数据部分。封装占用预算；ICMP 反馈和分组化层探测需关联实际路径与确认，单次失败不能确定精确上限。

**例子：** 外层1500字节、封装60字节时内层预算1440；再扣IPv6/TCP的40/20字节得到1380字节TCP数据预算。

**深入阅读：** [路径 MTU 与隧道：为什么小包能通大包却卡住](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md)

<a id="networking.congestion-algorithms"></a>

## Reno / CUBIC / BBR

**ID：** `networking.congestion-algorithms` · **建议优先级：** P1

**别名 / 检索词：** 拥塞算法、pacing、发送节奏

**简释：** 以窗口、发送节奏及拥塞/交付观测调整发送的算法思路。

Reno、CUBIC 与 BBR 采用不同控制思路；cwnd约束在途量，pacing安排发送时间。算法版本、路径、接收窗口与应用供给共同影响结果，名称不代表统一性能承诺。

**例子：** 应用没有持续供给时，低交付速率不能单独证明拥塞算法失效。

**深入阅读：** [拥塞算法与队列管理：带宽充足为什么仍然延迟很高](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md)

<a id="networking.queue-management"></a>

## AQM / ECN / BDP

**ID：** `networking.queue-management` · **建议优先级：** P1

**别名 / 检索词：** 主动队列管理、显式拥塞通知、带宽时延积

**简释：** 区分管道在途量、队列管理、调度与拥塞标记反馈。

BDP 是速率与基础往返时延的乘积；AQM 用较早丢弃或标记控制积压，调度分配服务机会，ECN 把标记交给端点响应。三者都不创造容量，也不自动保证业务公平。

**例子：** 100Mbit/s乘40ms得到500000字节BDP；1MB排在100Mbit/s瓶颈前约需80ms服务时间，二者不能混作队列目标。

**深入阅读：** [拥塞算法与队列管理：带宽充足为什么仍然延迟很高](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md)

<a id="networking.ipv6-source-privacy"></a>

## IPv6 Source Address Selection / Temporary Address

**ID：** `networking.ipv6-source-privacy` · **建议优先级：** P1

**别名 / 检索词：** IPv6 源地址选择、稳定不透明地址、临时地址

**简释：** 根据地址状态、作用范围与政策选择源，并用不同生成方式限制地址关联。

源/目的选择与路由政策有关；稳定不透明与临时地址解决不同关联问题。preferred到期表示弃用，valid到期表示失效；轮换不隐藏账号与应用特征。

**例子：** 旧临时地址仍valid但已deprecated时，已有TCP不因弃用自动迁移，新通信可选择合适的preferred地址。

**深入阅读：** [IPv6 源地址、隐私与接入防护：能发包不等于身份可信](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md)

<a id="networking.first-hop-protection"></a>

## RA Guard / Source Address Validation

**ID：** `networking.first-hop-protection` · **建议优先级：** P1

**别名 / 检索词：** 接入防护、源地址验证

**简释：** 约束本地链路的路由通告与源地址使用，防止部分伪造或误配。

RA Guard检查允许的通告位置与特征，源地址验证检查地址/前缀与接入绑定。需要处理IPv6解析、合法拓扑和角色变化；DAD或过滤通过都不等于应用身份已认证和授权。

**例子：** 允许路由器端口的合规RA、阻止终端端口的RA，仍不能据此允许该终端访问所有订单。

**深入阅读：** [IPv6 源地址、隐私与接入防护：能发包不等于身份可信](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [RFC 9110：HTTP 语义](https://www.rfc-editor.org/rfc/rfc9110.html)
- [MDN：HTTP 概览](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [RFC 9293：TCP 接收窗口与零窗探测](https://www.rfc-editor.org/rfc/rfc9293.html)
- [RFC 5681：TCP 拥塞控制](https://www.rfc-editor.org/rfc/rfc5681.html)
- [RFC 6298：重传计时器](https://www.rfc-editor.org/rfc/rfc6298.html)
- [RFC 4632：CIDR 前缀与最长匹配](https://www.rfc-editor.org/rfc/rfc4632.html)
- [RFC 1812：IPv4 路由器与逐跳转发](https://www.rfc-editor.org/rfc/rfc1812.html)
- [RFC 4861 与 IPv6 邻居发现](https://www.rfc-editor.org/rfc/rfc4861.html)
- [RFC 5942：IPv6 地址前缀与 on-link 的区别](https://www.rfc-editor.org/rfc/rfc5942.html)
- [RFC 3022：传统 NAT 与地址端口转换](https://www.rfc-editor.org/rfc/rfc3022.html)
- [RFC 9110：HTTP 代理、网关与隧道](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.7)
- [RFC 7239：Forwarded 来源链与完整性](https://www.rfc-editor.org/rfc/rfc7239.html)
- [HAProxy 3.2：TCP/HTTP 模式及服务器状态](https://docs.haproxy.org/3.2/configuration.html)
- [NGINX：HTTP 负载分配与会话保持](https://nginx.org/en/docs/http/load_balancing.html)
- [RFC 8446：TLS 1.3 证书认证、客户端证书请求与恢复边界](https://www.rfc-editor.org/rfc/rfc8446.html)
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [CloudFront cache keys](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [CloudFront cache policy settings](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html)
- [CloudFront invalidation and versioning](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html)
- [CloudFront origin access restriction](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-origin.html)
- [AWS WAF oversize components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)
- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768.html)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085.html)
- [RFC 9000: QUIC v1](https://www.rfc-editor.org/rfc/rfc9000.html)
- [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001.html)
- [RFC 9002: QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002.html)
- [RFC 9114: HTTP/3](https://www.rfc-editor.org/rfc/rfc9114.html)
- [RFC 9221: QUIC DATAGRAM extension](https://www.rfc-editor.org/rfc/rfc9221.html)
- [RFC 4291: IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291.html)
- [RFC 4007: IPv6 Scoped Address Architecture](https://www.rfc-editor.org/rfc/rfc4007.html)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862.html)
- [RFC 8415: DHCP for IPv6](https://www.rfc-editor.org/rfc/rfc8415.html)
- [RFC 8201: IPv6 Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc8201.html)
- [RFC 3849: IPv6 Address Prefix Reserved for Documentation](https://www.rfc-editor.org/rfc/rfc3849.html)
- [Linux ip-rule：策略查询与优先级](https://man7.org/linux/man-pages/man8/ip-rule.8.html)
- [RFC 4271：BGP 路由信息与本地选择](https://www.rfc-editor.org/rfc/rfc4271.html)
- [RFC 8899：数据报分组化层 MTU 发现](https://www.rfc-editor.org/rfc/rfc8899.html)
- [RFC 9438：CUBIC](https://www.rfc-editor.org/rfc/rfc9438.html)
- [RFC 7567：主动队列管理](https://www.rfc-editor.org/rfc/rfc7567.html)
- [RFC 6724：IPv6 默认地址选择](https://www.rfc-editor.org/rfc/rfc6724.html)
- [RFC 8981：IPv6 临时地址](https://www.rfc-editor.org/rfc/rfc8981.html)
- [RFC 7113：RA Guard 实现建议](https://www.rfc-editor.org/rfc/rfc7113.html)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
