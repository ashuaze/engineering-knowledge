---
id: "kb-networking-dns-caching"
title: "DNS 缓存与地址选择：改了解析为什么还访问旧地址"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分权威记录、递归与本地缓存、负缓存和候选地址，解释 TTL 为何不是全局切流时钟。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-networking-https-request"]
related: ["kb-networking-connection-states", "kb-networking-http-pools", "kb-networking-connections-lab", "kb-cache-search-cache-aside"]
tags: ["dns", "ttl", "negative-cache", "address-selection"]
---

# DNS 缓存与地址选择：改了解析为什么还访问旧地址

学习入口：权威 [DNS](../../glossary/networking.md#networking.dns) 已改成新地址，为什么只有部分客户端切换，另一些还连着旧服务？前置：域名、客户端与服务器。先区分名称查询和现有连接：DNS 更新提供后续查询的候选结果，不会主动迁移已经建立的连接。本文核查机制，时间线为纸面推演，没有修改真实 DNS 或测量解析传播。

## 一次名称查询由谁回答

| 角色 | 保存或处理什么 | 不能自动保证 |
| --- | --- | --- |
| 权威服务器 | 某个区域的记录及委派关系 | 所有客户端立即看到最新版本 |
| 递归解析器 | 代客户端追查答案，并按规则缓存 | 当前应用一定使用这台解析器 |
| 本地解析接口与缓存 | 操作系统、浏览器或应用的名称查询路径 | 每次请求都发出 DNS 网络查询 |
| [连接池](../../glossary/api.md#api.pool) | 已建立、可再次使用的连接 | 连接目标会随 DNS 记录自动改变 |

[RFC 1034](https://www.rfc-editor.org/rfc/rfc1034.html#section-2.4)区分名称空间、名称服务器与解析器。递归解析器可能沿委派查询，也可能用缓存或转发器，不能把“应用每次都从根服务器查起”当作固定路径。记录类型也不同：地址、别名和委派各有职责；跟随别名不等于只管理一个缓存条目。

例如 [Node.js 24.16.0 的 DNS 接口](https://nodejs.org/download/release/v24.16.0/docs/api/dns.html#implementation-considerations)明确区分操作系统名称查询接口与直接发 DNS 查询的接口。读取本机 hosts、系统配置和[运行时](../../glossary/runtime.md#runtime.virtual-machine)缓存的行为需要按实际客户端核对；命令行查到的答案不一定等于应用刚才使用的答案。

## TTL 限制缓存使用时间，不是广播更新

TTL 是资源记录的缓存时间信息。正常的新鲜缓存使用会随经过时间扣减；权威记录变更不会把旧条目剩余时间即时改短。降低 TTL 应提前安排，已经缓存旧 TTL 的解析器仍可能沿用原来的剩余期限。具体约束参见 [RFC 1034 的记录与缓存说明](https://www.rfc-editor.org/rfc/rfc1034.html#section-3.2.1)。

下面只推演一个遵循新鲜度期限、没有提前刷新或过期服务策略的缓存；所有数字都是教学设定：

| 时刻 | 动作 | 这个缓存可见的状态 |
| --- | --- | --- |
| t=0 | 取得旧地址，TTL=300 秒 | 缓存旧地址，正常期限到 t=300 |
| t=60 | 权威改成新地址，新的 TTL=30 秒 | 旧缓存不会被这次写入主动通知 |
| t=100 | 同一缓存回答查询 | 仍可返回旧地址，剩余期限约 200 秒 |
| t=300 之后 | 需要刷新且成功查询权威新值 | 才取得新地址及它的新 TTL |

不同缓存的填充时间不同，切换不会在一个全局时刻完成。还要区分解析器故障时的策略：[RFC 8767](https://www.rfc-editor.org/rfc/rfc8767.html)允许在规定条件下使用过期数据维持服务。因此 TTL 不能单独作为旧地址完全停止被使用的硬性保证。

## 查不到也可能被缓存

NXDOMAIN 表达名称不存在；NODATA 表达名称存在但没有所查询类型的数据。它们与查询[超时](../../glossary/api.md#api.retries)、服务端失败不是同一个结果。[RFC 2308](https://www.rfc-editor.org/rfc/rfc2308.html#section-5)规定相关否定答案的缓存；携带 SOA 的这类负缓存期限取 SOA TTL 与 SOA MINIMUM 的较小值，不能直接照搬某个 A 记录的 TTL。

教学情形：先查询一个尚未创建的名字，得到有期限的否定缓存，随后才发布记录。权威已经有数据，不代表先前的负缓存马上失效。排查时记录问题名称、记录类型、响应码、答案来源和剩余期限；不要把“没有 A 答案”一概写成“域名不存在”。

解析超时、SERVFAIL 等解析失败还有独立的失败缓存规则，见更新 RFC 2308 的 [RFC 9520](https://www.rfc-editor.org/rfc/rfc9520.html#section-3.2)；不能因为它们不是 NXDOMAIN/NODATA，就认定客户端每次都会立即重新向上游查询，也不能套用上述 SOA 期限。本文没有搭建负缓存或失败缓存实验，具体行为仍需核对解析器版本与配置。

## 多个候选地址怎样变成一个连接

查到多个地址后，客户端仍需选择和尝试。列表首项不等于必然使用的地址，某个地址失败也不等于整个名称不可用。[Happy Eyeballs v2，RFC 8305](https://www.rfc-editor.org/rfc/rfc8305.html)协调地址获取和错开的连接尝试，减少单个地址族或路径故障拖延用户的情况；不要将其定时参数视作所有客户端的统一行为。

连接成功后，后续请求可能使用原连接，不再重复查询。DNS 地址、实际 [socket](../../glossary/systems.md#systems.fd-socket) 对端和 [TLS](../../glossary/networking.md#networking.tls) 要验证的服务身份也不同：连接到某个 [IP](../../glossary/networking.md#networking.transport) 不能代替对请求目标身份的校验。详见[TCP 与 TLS 连接状态](tcp-tls-and-connection-states.md)。

## 改地址时还需要管理什么

切流计划应分别安排记录变更、缓存观察、连接池轮换、旧节点停止接纳与在途工作排空。过早移除旧节点，可能使仍使用旧地址或旧连接的客户端失败；无限保留旧连接，又可能延长旧版本服务的使用。连接寿命策略和重连也有成本，不能只把 TTL 调得更短。

排查可先比较：同一名称和类型的权威答案、应用实际解析路径的答案、实际连接对端，以及该连接何时建立。代理场景还要确认由客户端还是代理解析上游名称。名称查询成功只能证明获得了结果，不能证明端口可达、证书正确或应用健康。

[连接生命周期实验](connection-lifecycle-lab.md)使用固定回环 IP，观察复用和关闭后重连；它没有调用 DNS，不是上述传播或切流保证的实测证据。

## 自检与关联阅读

自检：t=60 把 TTL 从 300 改成 30，能否保证 t=90 没人访问旧服务？至少解释旧缓存剩余时间、过期服务策略和现有连接三条路径，再给出各自需要的证据。

- [HTTP 复用与连接池](http-reuse-pools-and-timeouts.md)：名称更新之外的池、流与空闲连接管理。
- [缓存失效](../cache-search/cache-aside-and-invalidation.md)：类比缓存更新时，注意 DNS 有自己的协议与期限。

核查日期：2026-10-19。DNS、否定缓存、过期数据与地址尝试依据上述 RFC；运行时例子限定 Node.js 24.16.0。切流清单和时间线为教学综合，未执行 DNS、双栈或代理实验。
