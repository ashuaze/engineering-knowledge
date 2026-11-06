---
id: "kb-networking-ipv6-source-protection"
title: "IPv6 源地址、隐私与接入防护：能发包不等于身份可信"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "解释源/目的地址选择、稳定与临时地址及寿命，区分 DAD、RA Guard、源地址约束与应用身份授权。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-ipv6-neighbors"]
related: ["kb-networking-policy-convergence", "kb-networking-dns-caching", "kb-networking-path-mtu", "kb-security-mtls-service-identity", "kb-security-ssrf"]
tags: ["ipv6", "source-selection", "privacy", "ra-guard", "first-hop"]
---

# IPv6 源地址、隐私与接入防护：能发包不等于身份可信

学习入口：同一网卡有好几个 IPv6 地址，新连接到底用哪一个？[临时地址](../../glossary/networking.md#networking.ipv6-source-privacy)换了，已有连接会不会断？主机收到一个看起来正常的路由通告，又凭什么相信对方是合法路由器？这些问题分别涉及地址选择、寿命和本地链路的信任。

前置：[IPv6 与邻居发现](ipv6-addresses-slaac-and-neighbor-discovery.md)。本文讨论普通 IPv6 主机及受管理接入网络的概念；地址、寿命和端口角色为纸面假设，不穷举移动性、全部地址选择更新或具体交换机配置。没有启用临时地址、发送 RA/ND 或测试[接入防护](../../glossary/networking.md#networking.first-hop-protection)。

## 目的地址候选与源地址选择互相关联

[DNS](../../glossary/networking.md#networking.dns) 可能给出多个目标，主机也可能有多个可用源地址。源地址选择针对给定 IPv6 目的地址，从候选中按有顺序的规则比较；作用范围、是否 deprecated、出口接口、标签和临时地址偏好等会影响结果。应用明确选择与管理员政策也会改变默认行为，见 [RFC 6724 §4–6](https://www.rfc-editor.org/rfc/rfc6724.html#section-5)。

所以“IPv6 优先”“前缀最接近优先”或“临时地址优先”都不足以概括所有情况。目标排序之后的实际建连竞速仍是另一层机制，见 [DNS 与地址选择](dns-caching-and-address-selection.md)。路由规则若又按源地址选出口，就更需要把源/目的组合、接口、策略与时间一起记录，见[策略与动态路由](policy-routing-control-planes-and-convergence.md)。

下面固定同一接口、同一可用出口、同一全局作用范围及标签，无应用绑定或移动性因素，其他较早比较规则均相同：

| 候选 | 当前状态 | 本文给定条件下的用途 |
| --- | --- | --- |
| S，稳定不透明地址 | preferred | 可用于新通信，身份[授权](../../glossary/security.md#security.identity)仍由应用处理 |
| T1，旧临时地址 | deprecated，但仍 valid | 避免用于有合适替代的新通信；旧通信可继续使用 |
| T2，新临时地址 | preferred | 若主机采用默认临时地址偏好，新通信在剩余候选中优先考虑它 |

本例选择 T2：T1 先因 deprecated 落后，S 与 T2 的较早规则平局后再比较临时偏好。这是明确前提下的选择推演，不能把表格用于另一主机的完整排序预测；链路本地源也不能拿来作为任意跨链路通信的源。

## 稳定不透明与临时地址解决不同关联问题

RFC 7217 的稳定不透明接口标识在给定网络上下文和生成参数下保持稳定，减少直接暴露硬件标识及跨网络复用同一标识带来的关联，见 [RFC 7217 §5](https://www.rfc-editor.org/rfc/rfc7217.html#section-5)。参数、密钥或网络改变，结果可以改变；它不是用户账号，也不是“永远固定地址”。

RFC 8981 的临时地址随时间生成，缩短长期使用同一地址的关联窗口；可以与稳定地址并存，见 [RFC 8981 §3](https://www.rfc-editor.org/rfc/rfc8981.html#section-3)。轮换不隐藏网络前缀、登录账号、[Cookie](../../glossary/security.md#security.sessions)、请求特征或观察到的时间关系，也不保证对外匿名。

教学寿命：T1 在 `t=0` 已能使用，preferred lifetime 到 `t=60`，valid lifetime 到 `t=180`；T2 在 `t=50` 已完成配置并可用。假设期间没有通告刷新、删除或管理变更：

1. `t=55`：T1、T2 都 preferred；哪个胜出还需完整选择政策，不能只看新旧编号。
2. `t=70`：T1 已 deprecated，但仍 valid；新通信优先合适的 preferred 候选，绑定 T1 的已有 [TCP](../../glossary/networking.md#networking.transport) 连接不因这次弃用自动换地址或立即断开。
3. `t=181`：T1 已 invalid，不能再作为该接口的有效源/目的地址；需要它的通信不能靠“已经连上”绕过地址失效。

preferred 与 valid 的状态区别依据 [RFC 4862 §2、§5.5.4](https://www.rfc-editor.org/rfc/rfc4862.html#section-5.5.4)。这里的三个时刻是固定教学输入，不是主机默认计时配置。地址仍 valid 也不保证链路、回程、服务或连接状态仍在。

## DAD 与普通 ND 不认证设备身份

DAD 检查链路上的地址冲突，未发现冲突不能证明某地址属于获准用户。普通 ND/RA 也没有自动给通告者建立应用意义上的密码学身份。攻击或错误配置可能让主机学到不合适的默认路由、前缀或邻居信息，基础威胁见 [RFC 4862 §6](https://www.rfc-editor.org/rfc/rfc4862.html#section-6) 与 [RFC 9099 §2.3](https://www.rfc-editor.org/rfc/rfc9099.html#section-2.3)。

例如受管理接入网中，端口 U 接普通终端，端口 R 接获准路由器。若允许 U 随意发送路由通告，终端生成了地址或 DAD 通过都不能证明通告可信。终端看到的地址与路由变化，还可能是接入层问题，不能只[重试](../../glossary/api.md#api.retries)应用请求。

## RA Guard、源地址约束与应用授权各管一层

RA Guard 在二层接入设备检查并过滤路由通告，策略可以规定哪些端口和通告特征被允许，见 [RFC 6105](https://www.rfc-editor.org/rfc/rfc6105.html)。在上述教学网络中，策略可允许 R 的合规 RA，阻止 U 的 RA；多路由器、下挂网络或角色变化时，必须重新核对信任边界。

“设备支持 RA Guard”仍不够：必须理解 IPv6 扩展首部与分片相关的解析和规避问题，见 [RFC 7113](https://www.rfc-editor.org/rfc/rfc7113.html)。不能把只检查固定偏移的过滤器当作完整实现，也不能为阻止 RA 把业务需要的所有 ICMPv6 一起封掉；路径大小反馈见[路径 MTU](path-mtu-icmp-tunnels-and-black-holes.md)。

源地址验证则关注某个接入绑定是否允许使用某个地址或前缀，限制伪造源地址；它与 RA 发送权限不同。部署背景、绑定和局限见 [RFC 9099 §2.3.2](https://www.rfc-editor.org/rfc/rfc9099.html#section-2.3.2)。即使两项检查通过，也不能推出“允许读取所有订单”：服务仍需[服务身份](../security/mtls-service-identities-and-trust-boundaries.md)、对象权限与会话治理。临时地址轮换也不应成为绕过这些控制的账号替代品。

排查时分别记录地址与寿命、选中的源/目的及出口、RA 的进入位置、策略命中与合法通告是否被误挡。把“防伪造”与“合法配置能继续工作”都作为后续实现验证范围。

## 自检

1. 表中为何选 T2？哪些前提改变后，不能沿用这个结论？
2. `t=70` 与 `t=181` 时，T1 的区别是什么？弃用是否会自动迁移 TCP？
3. 稳定不透明地址和临时地址分别减少什么关联？为什么仍不能保证匿名？
4. DAD 通过、RA Guard 允许、源地址验证通过，各能证明什么，不能证明什么？
5. 为什么端口 U/R 的教学规则不能直接复制到允许下挂路由器的所有网络？

## 来源与核查

2026-10-26 核查 RFC 6724、7217、8981、4862、6105、7113、9099 的固定文本，分别用于选择、地址生成/寿命与接入防护的明确范围。本文为 source-checked 概念文章，未验证实际主机选择、生命周期、交换机解析/过滤、绕过防护或应用授权集成。
