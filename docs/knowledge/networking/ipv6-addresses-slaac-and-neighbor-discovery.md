---
id: "kb-networking-ipv6-neighbors"
title: "IPv6 与邻居发现：有了地址为什么还不一定能发出去"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "分开解释地址作用范围、SLAAC、链路判断、默认路由和邻居状态，说明自动配置、可达性及安全边界。"
created: "2026-10-23"
updated: "2026-10-26"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-networking-ip-routing"]
related: ["kb-networking-dns-caching", "kb-networking-udp-quic", "kb-networking-nat-proxy-lb", "kb-security-ssrf", "kb-security-mtls-service-identity", "kb-networking-ipv6-source-protection", "kb-networking-path-mtu"]
tags: ["ipv6", "neighbor-discovery", "slaac", "address-scope", "routing"]
---

# IPv6 与邻居发现：有了地址为什么还不一定能发出去

学习入口：主机已经自动生成一个 IPv6 地址，为什么仍访问不了同前缀的设备或外网？先分清五件事：接口拥有什么地址、目标是否在当前链路、经哪个默认路由器、怎样找到[下一跳](../../glossary/networking.md#networking.routing)，以及哪些证据证明邻居仍可达。它们可以来自同一条通告，却有不同的用途与生命周期。

前置：[网络分层、IP 与路由](network-layers-ip-subnets-and-routing.md)。本文以常见以太网上的普通 IPv6 主机为范围，依据固定 RFC 的基础机制与 RFC 5942 的主机模型澄清，不枚举全部后续扩展或主机配置。地址、计时和状态均为纸面教学设计；没有启用 IPv6、发送探测、修改路由或抓包。

多源地址的选择、稳定/[临时地址](../../glossary/networking.md#networking.ipv6-source-privacy)寿命与 RA [接入防护](../../glossary/networking.md#networking.first-hop-protection)，继续见[IPv6 源地址、隐私与接入防护](ipv6-source-selection-privacy-and-first-hop-protection.md)；大小反馈另见[路径 MTU](path-mtu-icmp-tunnels-and-black-holes.md)。

## 地址更长，地址的使用范围仍要分别判断

IPv6 地址为 128 位，以冒号分隔的十六进制组表示；`::` 可压缩一段连续零。地址属于接口，一个接口可以同时具有多个地址。单播、组播与任播有不同的交付含义；IPv6 没有广播，不能将 IPv4 的广播地址与“地址总数减二”规则直接移植，见 [RFC 4291 §2](https://www.rfc-editor.org/rfc/rfc4291.html#section-2)。

| 地址或记法 | 本文中怎样解释 | 不能推出什么 |
| --- | --- | --- |
| `fe80::/10` 范围中的链路本地地址 | 用于当前链路，例如与路由器进行[邻居发现](../../glossary/networking.md#networking.neighbor-discovery) | 路由器会把该源/目的地址转发到另一链路 |
| `::1`、`::` | 分别是回环地址与未指定地址；后者可在某些初始化报文中作为源地址 | 任意远端服务地址，或一个已可正常使用的主机地址 |
| `ff00::/8` 中的组播地址 | 以组和作用范围表达接收对象 | 全网广播或对方应用已经消费 |
| `2001:db8:1200:34::10` | 本文的文档示例地址 | 已被分配给真实主机、公共可达或拥有访问权限 |

链路本地地址不跨链路转发的限制见 [RFC 4291 §2.5.6](https://www.rfc-editor.org/rfc/rfc4291.html#section-2.5.6)。示例前缀 `2001:db8::/32` 专供文档使用，见 [RFC 3849](https://www.rfc-editor.org/rfc/rfc3849.html)；它不是可复制到生产的地址分配。

同一台主机有两张网卡时，两条不同链路都可能有一个 `fe80::1`。`fe80::1%eth0` 这样的本地记法，用 zone 标识区分意图访问哪条链路；具体标识可以是接口名或数字，依主机接口而定。它不是 IPv6 地址新增的第 129 位，也不是一段可在另一台机器上原样解释的全局标识。[RFC 4007 §6、§11](https://www.rfc-editor.org/rfc/rfc4007.html#section-11)规定作用范围与 zone 的关系。处理这类地址的 URL、客户端和出口校验还需各自核对，不能靠字符串前缀覆盖所有地址形式，见 [SSRF 与出口边界](../security/ssrf-url-resolution-and-egress-boundaries.md)。

## 邻居发现不只是在 IPv6 中替代 ARP

Neighbor Discovery（ND）使用 ICMPv6。Router Solicitation / Advertisement 简写为 RS / RA，Neighbor Solicitation / Advertisement 简写为 NS / NA；分别可理解为路由器询问/通告、邻居询问/通告。它们承担的任务见 [RFC 4861 §3](https://www.rfc-editor.org/rfc/rfc4861.html#section-3)。

| 要解决的问题 | 本文涉及的消息或状态 |
| --- | --- |
| 路由器在哪里、有哪些配置信息 | 主机可发 RS，路由器周期性或应询发送 RA |
| 某前缀用于地址配置还是链路判断 | RA 的 Prefix Information Option（前缀信息选项，PIO）及其标志 |
| 已选定的下一跳对应哪个链路地址 | NS / NA 及邻居缓存 |
| 邻居的正向路径是否仍可用 | Neighbor Unreachability Detection（NUD，邻居不可达检测） |
| 候选地址是否检测到链路内重复 | DAD 使用相关 NS / NA 机制，另按地址配置规则处理 |

因此排查要先确定下一跳，再看它的邻居项。远端目的地经过网关时，解析的是当前链路上的网关，而非直接对远端地址求 MAC。RA 也不是一张完整的全网路由表；重定向、具体路由与策略仍有各自规则，不能把“收到 RA”简化为所有配置和所有目的地都已可用。

## 同一 RA 中，A、L 与默认路由器寿命各管什么

PIO 的 A 标志表示前缀可用于无状态地址自动配置，即 SLAAC；L 标志表示前缀可用于 on-link 判断，即把目标视为当前链路上可直接交付的对象。RA 自身的 Router Lifetime 又单独限定发送者作为默认路由器的资格。其独立性见 [RFC 4861 §4.2、§4.6.2](https://www.rfc-editor.org/rfc/rfc4861.html#section-4.6.2)。

| 收到的信息 | 它允许判断的事情 | 它没有单独证明的事情 |
| --- | --- | --- |
| PIO 中 A=1 | 按 SLAAC 规则尝试形成地址 | 该前缀已被声明为 on-link |
| PIO 中 L=1，且相应有效期仍在 | 形成或更新该前缀的 on-link 信息 | 主机一定从它生成了地址 |
| PIO 中 L=0 | 该选项不提供 on-link 判断依据 | 撤销已有 on-link 信息，或明确宣布所有目标 off-link |
| Router Lifetime 非零 | 按主机规则维护发送者的默认路由器项 | 其上游、返回路径或业务健康一定正常 |
| Router Lifetime 为零 | 发送者不作为该通告声明的默认路由器 | PIO 的地址和前缀寿命也全部归零 |

这里最容易错的是从“我获得了这个地址”推导“整个[地址前缀](../../glossary/networking.md#networking.ip-prefix)都在本链路”。[RFC 5942 §3–4](https://www.rfc-editor.org/rfc/rfc5942.html#section-4)明确把地址分配和 on-link 信息分开：SLAAC、DHCPv6 或手动分配地址，都不能隐式补出一个 on-link 前缀；仅收到某个 ND 报文也不能据此新增这类判断。

DHCPv6 可以承担地址、前缀委派或其他配置的交付，参照 [RFC 8415 的术语与范围](https://www.rfc-editor.org/rfc/rfc8415.html#section-4)。但不能把“DHCPv6 已分配地址”当作“已通过 RA 获得默认路由器”。按 [RFC 4861 §4.2](https://www.rfc-editor.org/rfc/rfc4861.html#section-4.2)，RA 的 M=1 表示可通过 DHCPv6 取得地址；O=1 表示可通过 DHCPv6 取得其他配置信息，例如 [DNS](../../glossary/networking.md#networking.dns)。M=1 时 O 是冗余信息，可以忽略，因为 DHCPv6 会返回可用的配置信息。A 则属于每个 PIO；这些标志不是一个统一的开关，也不证明所有操作系统都采用同样的配置策略。

## 用一个反例把地址、直连与出网拆开

纸面设定：普通以太网主机 H 没有该示例全局前缀的 on-link 信息、静态路由、重定向或其他默认路由器；链路本地机制仍按正常规则工作。它在接口 `eth0` 收到源为链路本地地址 `fe80::1` 的有效 RA，内含 `2001:db8:1200:34::/64`，A=1、L=0，Router Lifetime=0；PIO 的地址寿命有效，主机按规则生成不重复的 64 位接口标识并完成 DAD。

```text
128 位地址 = 64 位前缀 + 64 位接口标识
2001:db8:1200:0034 | 0000:0000:0000:0010
→ 示例地址 2001:db8:1200:34::10
```

此时主机可拥有该地址，却没有从这条 PIO 获得 on-link 声明，也没有从该路由器获得默认下一跳。即使目标 `2001:db8:1200:34::20` 看起来与自己“前四组相同”，也不能按这个猜测直接解析目标；没有其他路由依据时，不能发明一条直连或默认路径。

现在只把 Router Lifetime 改为非零且满足相应主机规则，A/L 不变，主机可以通过这个默认路由器处理未判定 on-link 的目标；它解析的是 `fe80::1` 的链路地址。再另外收到 L=1 且有效的对应 PIO，才有该前缀的 on-link 依据。这些步骤假定相关消息均被接收并按规则处理，不是一次真实主机观察；网关是否转发、返回是否可达仍要另行证明。

`/64` 在这里来自“前缀长度 + 本链路接口标识长度 = 128”的 SLAAC 形成条件。若本例接口标识仍为 64 位，收到 `/80` 的 A=1 PIO，`80+64=144` 不满足此条件，不能照样生成地址；见 [RFC 4862 §5.5.3](https://www.rfc-editor.org/rfc/rfc4862.html#section-5.5.3)。这不表示所有 IPv6 路由都必须 `/64`，也不表示该 PIO 不能独立提供有效的 L 标志信息。

## 地址可用、被弃用和检测到重复是不同状态

SLAAC 先形成候选地址。本文按普通 DAD 流程解释：候选处于 tentative，即尚待检测；检测到重复则不能把它正常分配给接口。DAD 针对当前链路的重复，不是全网查询或对某个主体的[认证](../../glossary/security.md#security.identity)，也不能保证未来永不出现冲突。手动或 DHCPv6 地址并非天然免除 DAD；具体例外、禁用和扩展按实现及规范另查，依据见 [RFC 4862 §5.4](https://www.rfc-editor.org/rfc/rfc4862.html#section-5.4)。

Preferred Lifetime 表示地址仍被优先使用的阶段，Valid Lifetime 表示仍有效的阶段。假设一个新生成、DAD 成功的地址在教学时刻 t=0 起剩余优先寿命 600 秒、有效寿命 1800 秒，期间没有更新或其他变化，则 t=600 成为 deprecated（不再优先用于新通信），t=1800 才失效。被弃用仍有效，不等于立刻禁止所有既有通信；实际源地址选择还需结合地址范围、应用约束及其他候选。

该算例描述自然到期，不描述后来 RA 缩短已有地址寿命的处理；后者还有 RFC 4862 §5.5.3 的保护规则，不能把一条“寿命设为零”的未认证通告当作所有地址立即失效的通用操作。地址生命周期见 [RFC 4862 §5.5.3–§5.5.4](https://www.rfc-editor.org/rfc/rfc4862.html#section-5.5.4)。

## 邻居缓存不是一个永久的在线证明

NUD 跟踪从本机向邻居的正向可达性。`INCOMPLETE` 表示仍在解析；`REACHABLE` 表示近期有正向路径确认；`STALE` 表示缺少近期确认，不等于已经判死。使用 STALE 项发送后可进入 DELAY，再视确认情况进入 PROBE；不能把这组状态当成每次都经过的固定倒计时。状态及确认依据见 [RFC 4861 §7.3](https://www.rfc-editor.org/rfc/rfc4861.html#section-7.3)。

例如一次应询 NA 可提供相应的可达性证据，无请求的 RA/NA 不能统一当作同等确认。即便当前网关可响应 NUD，也只说明相应邻居路径，不能证明它的上游、DNS、[TLS](../../glossary/networking.md#networking.tls) 或应用业务都正常。地址选择及连接结果需继续见 [DNS 与地址选择](dns-caching-and-address-selection.md)、[NAT 与代理](nat-proxies-and-l4-l7-load-balancing.md)。

## ICMPv6 必须按职责治理，邻居身份仍要另证

ICMPv6 同时承载 ND 与部分错误反馈。仅因不需要诊断回显就全盘过滤，可能破坏地址配置、邻居交付或[路径 MTU](../../glossary/networking.md#networking.path-mtu) 发现。IPv6 路由器不沿途替源节点分片，经典 PMTU 发现依赖 Packet Too Big 反馈；可能出现握手完成而较大数据停滞的黑洞，见 [RFC 8201 §1、§3](https://www.rfc-editor.org/rfc/rfc8201.html#section-1)。包大小与上层预算继续见 [UDP 与 QUIC](udp-quic-streams-and-delivery-boundaries.md)。

另一方面，允许必要的控制报文不等于信任任意发送者。RA 要求使用链路本地源地址；其他 ND 消息按各自规则校验，不能把这一来源条件统一套给 NS/NA，例如 DAD 的 NS 可以使用未指定源地址。Hop Limit=255 等校验有限制经路由转发的远端伪造的作用，却不替同链路发送者做密码学身份认证；恶意或错误的 RA/NA 仍可能改变转发与缓存。消息校验与威胁范围见 [RFC 4861 §6.1、§7.1、§11](https://www.rfc-editor.org/rfc/rfc4861.html#section-11)。接入治理、受信路由器、特定防护协议与产品配置需要另行验证，应用身份与授权仍独立于地址和邻居映射，见 [mTLS 与服务身份](../security/mtls-service-identities-and-trust-boundaries.md)。

## 五道自检与核查范围

1. 两张网卡都能看见 `fe80::1` 时，为什么只给地址可能不够？zone 与地址范围、应用身份各有什么区别？
2. A、L、Router Lifetime 及 M/O 分别影响什么？DHCPv6 或 SLAAC 配好了地址，为什么不能据此补出 on-link 前缀或默认路由器？
3. A=1/L=0、Router Lifetime=0 的例子中，H 能否直接解析同前缀的 `::20`？只改默认路由器寿命后解析谁？64 位接口标识为何不能按本例接受 `/80` 做 SLAAC？
4. DAD 成功、优先寿命到期、有效寿命到期和邻居 STALE 分别意味着什么？600/1800 秒算例不能用来推断哪一种后来通告处理？
5. 网关 NUD 有响应、ICMPv6 放行与地址可达分别还缺少哪些业务和安全证据？为何“小请求成功”不能排除 PMTU 反馈故障？

核查日期：2026-10-23。实际读取下列固定文本的相关段落，不声明完整标准符合性或任何特定系统行为。上文状态、地址拼接、144 位反例、计时及 RA 场景为教学推演。

| 一手资料 | 实际核查范围 |
| --- | --- |
| [RFC 4291，2006-02](https://www.rfc-editor.org/rfc/rfc4291.html) | §2 的地址/接口、文本、组播与链路本地范围；不沿用已弃用站点本地配置 |
| [RFC 4007，2005-03](https://www.rfc-editor.org/rfc/rfc4007.html) | 作用范围、zone 及 §11 的本地文本表示；不展开 URL 编码或各操作系统 API |
| [RFC 4861，2007-09](https://www.rfc-editor.org/rfc/rfc4861.html) | §3、§4.2/4.6.2、§6/7、§11 的消息、标志、默认路由、邻居状态和威胁；on-link 以 RFC 5942 澄清为准 |
| [RFC 4862，2007-09](https://www.rfc-editor.org/rfc/rfc4862.html) | §5.3–5.5 的地址形成、DAD、前缀长度、优先/有效寿命及短寿命保护；未覆盖所有 DAD 与地址生成扩展 |
| [RFC 5942，2010-07](https://www.rfc-editor.org/rfc/rfc5942.html) | 地址配置与 on-link 独立、默认路由器缺失、旧 ND 定义的修订及错误 `/64` 推断 |
| [RFC 8415，2018-11](https://www.rfc-editor.org/rfc/rfc8415.html) | DHCPv6 的地址、前缀委派与配置范围；不展开客户端状态机、部署策略或全部选项 |
| [RFC 8201，2017-07](https://www.rfc-editor.org/rfc/rfc8201.html) | §1、§3 的路径 MTU、PTB 依赖及阻断后的黑洞边界；不展开分组化层探测算法 |
| [RFC 3849，2004-07](https://www.rfc-editor.org/rfc/rfc3849.html) | `2001:db8::/32` 文档专用范围，不作真实分配或连通性证据 |

未运行 SLAAC、DHCPv6、DAD/NUD、RA/NA 伪造或防护、路由/邻居表变更、ping、抓包、MTU 或性能实验。源选择、隐私地址与 RA 防护的概念已有上文关联专题；多宿主完整政策、具体地址生成、前缀委派部署、SEND 及真实防护/故障恢复仍需深入或集成验证。
