---
id: "kb-networking-connection-states"
title: "TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分传输建立、安全协商和业务确认，解释 FIN、RST、TIME_WAIT、保活与连接失效的边界。"
created: "2026-10-19"
updated: "2026-10-22"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-networking-https-request"]
related: ["kb-networking-dns-caching", "kb-networking-http-pools", "kb-networking-connections-lab", "kb-api-idempotency", "kb-security-sessions-tokens", "kb-reliability-retry-budgets", "kb-networking-flow-congestion", "kb-networking-nat-proxy-lb", "kb-security-mtls-service-identity"]
tags: ["tcp", "tls", "connection-state", "keepalive"]
---

# TCP 与 TLS 连接状态：建立、半关闭与失效分别说明什么

学习入口：连接显示 ESTABLISHED，为什么请求仍会[超时](../../glossary/api.md#api.retries)；收到 reset，又能否认定写入没发生？前置：请求、响应和双向通信。传输状态描述端点的协议进度，业务结果需要另外确认。本文限定普通 [TCP](../../glossary/networking.md#networking.transport) 与 [TLS](../../glossary/networking.md#networking.tls) 1.3 的概念路径；没有抓包或运行 TLS、半关闭与内核状态实验。

## 建立连接没有完成业务

对常见 [HTTP/1.1](../../glossary/networking.md#networking.http-versions)、HTTP/2 的 HTTPS 路径，可先区分“TCP 建立 → TLS 协商 → HTTP 与业务”。这不是全部 HTTPS 的固定步骤：[HTTP/3](https://www.rfc-editor.org/rfc/rfc9114.html)运行于 [QUIC](../../glossary/networking.md#networking.quic)，不能套用 TCP 状态机；已有连接被复用时也不会每个请求重新握手。

TCP 的典型建立过程交换 SYN、SYN+ACK 和 ACK，协调初始序号与端点状态。[RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html#name-establishing-a-connection)规定建立与关闭状态机。某端进入 ESTABLISHED 不表示对方应用已处理请求，更不保证未来路径始终可用。TCP 提供有序字节流，应用仍需界定消息边界；一次 send 和一次 read 不必一一对应。

教学时序：客户端把订单请求交给本机发送缓冲区，服务器随后收到并持久化，再尝试返回响应。这是多个事实：写入本机缓冲区不证明对端收到；传输确认不证明业务提交；业务已提交也不证明调用方收到了结果。需要[幂等标识和结果查询](../api/idempotency.md)处理最后一种未知状态。

## TLS 增加了哪些保证

TLS 1.3 协商受保护通信的密钥与参数，并在相应[认证](../../glossary/security.md#security.identity)模式下证明对端持有身份所需的密钥。常见 Web 场景使用证书认证服务器；客户端身份认证不是自动包含的业务登录。[RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html)定义协议，[RFC 9525](https://www.rfc-editor.org/rfc/rfc9525.html)规定客户端期望服务身份与所呈现身份的匹配。

证书链受到信任与证书适用于目标服务是不同检查。连接 IP、用于路由的名称和需要认证的目标名称不应随意互换；跳过名称匹配会破坏“我在和谁通信”的保证。[SNI，RFC 6066](https://www.rfc-editor.org/rfc/rfc6066.html#section-3)在 ClientHello 中提供服务器名称，帮助对端选择配置与证书，不替代身份验证。协议选择也要分清：例如 [ALPN，RFC 7301](https://www.rfc-editor.org/rfc/rfc7301.html)协商应用协议，不能从“TLS 已连上”直接推出使用了 HTTP/2。

复用现有连接和 TLS 会话恢复不是同一件事：前者沿用连接，后者用于建立新的安全连接。TLS 1.3 的 0-RTT 早期数据还有重放风险，不能仅因传输加密就认为副作用只会执行一次。业务重放安全仍需单独设计；本文不提供证书部署或 0-RTT 配置方案。

## 正常关闭有两个方向

| 信号或状态 | 协议层含义 | 排查时还需知道 |
| --- | --- | --- |
| FIN | 发送方在该方向没有更多字节 | 另一方向是否仍在传输，应用协议是否允许半关闭 |
| CLOSE_WAIT | 本端收到对端的关闭方向通知，等待本地关闭流程 | 哪个应用持有 [socket](../../glossary/systems.md#systems.fd-socket)，是否遗漏释放 |
| FIN_WAIT 等 | 本端已开始关闭，正在等待后续协议进度 | 对端状态、未发送数据和关闭策略 |
| TIME_WAIT | 为连接结束后的协议安全保留状态 | 连接创建/关闭速率及端口资源，而非直接判定泄漏 |
| RST / reset | 连接被复位，当前传输不能按原路径继续 | 哪一段、何时失败，业务可能已推进到哪里 |

这是读取状态的入门表，不是全部合法转换。FIN 表达一个方向结束，不规定必须恰好抓到“四个独立报文”；报文组合与同时关闭会改变观察。TIME_WAIT 是协议机制，不应仅凭数量高就关闭保护或认定服务端出错。长期 CLOSE_WAIT 也只是线索，需要与应用释放路径及连接增长关联，不能只靠单个快照下结论。

TLS 还有自己的关闭通知与截断处理，不能把任意 TCP EOF 都当作所有安全层和消息层已完整结束。应用应按具体协议核对消息完整性。本文没有实测 TCP FIN/RST、TLS close_notify 或 TIME_WAIT 的持续时间，操作系统配置值也不作通用推荐。

## “保活”可能指不同层

[RFC 1122 的 TCP keep-alive 说明](https://www.rfc-editor.org/rfc/rfc1122.html#section-4.2.3.6)讨论空闲连接探测。它与 HTTP 在同一连接上发送后续请求、应用[心跳](../../glossary/distributed.md#distributed.fencing)和[负载均衡](../../glossary/networking.md#networking.load-balancer)器的空闲回收是不同机制。探测参数由实际平台与客户端决定，不能把名字里的 [keep-alive](../../glossary/networking.md#networking.keepalive) 当成“永不关闭”。

| 机制 | 主要作用 | 无法单独证明 |
| --- | --- | --- |
| HTTP 持久连接 | 为后续请求复用连接 | 对端永远保留空闲连接 |
| TCP 保活探测 | 在一定空闲条件下探测传输端点可达性 | 业务[线程](../../glossary/systems.md#systems.execution-units)健康、请求按时完成 |
| 应用心跳 | 检查约定的应用响应 | 所有业务依赖和数据均正常 |
| 请求[截止时间](../../glossary/reliability.md#reliability.retry-budget) | 限制本次等待预算 | 远端工作已经撤销 |

路径黑洞或对端失联不一定立即改变本端显示的状态。需要协议重传、探测、显式读写失败或应用预算发现问题；同一连接上的“上次请求成功”也不是本次仍然健康的证明。

## 连接失效后应怎样收敛

先停止把已经确认失效的连接借给新请求，释放本地资源，再按剩余预算与业务语义决定是否重试。错误可能来自客户端到代理，也可能来自代理到服务；不要用单个 reset 名称推断哪端提交过业务。

教学反例：服务端已记录操作后，客户端因为等待响应超时主动断开。传输关闭不会自动撤销服务端的状态变更。[本地连接实验](connection-lifecycle-lab.md)仅验证一条简化路径：客户端显式 destroy 后，服务端进程内的标记仍存在。它没有[数据库事务](../../glossary/database.md#database.isolation)、网络抓包或持久性验证，不能证明真实支付或数据库的取消语义。

连接已建立却不能继续发送时，可连读[TCP 流量控制与拥塞控制](tcp-flow-control-and-congestion.md)，区分接收能力、路径反馈和在途数据限制。

中间节点是否终止 TCP/TLS、返回流量怎样回到映射入口，见[NAT、代理与负载均衡](nat-proxies-and-l4-l7-load-balancing.md)；不能从可见的一段连接推出完整端到端状态。

双向证书认证、预期服务身份与业务权限的区别，继续见[mTLS 与服务身份](../security/mtls-service-identities-and-trust-boundaries.md)。画清每一跳的 TLS 端点，再判断代理后端实际验证的是谁。

## 自检与关联阅读

自检：为什么 ESTABLISHED、收到响应头、完整读取响应体和业务提交是四种证据？收到 reset 后，怎样区分可以重放、需要查原结果和应停止的操作？

- [DNS 与地址选择](dns-caching-and-address-selection.md)：目标地址怎样被找到，旧连接为何不会自动迁移。
- [HTTP 复用与连接池](http-reuse-pools-and-timeouts.md)：连接之外还有流、借用和[排队](../../glossary/performance.md#performance.queueing)边界。
- [超时与重试预算](../reliability/timeouts-and-retry-budgets.md)：阶段等待、清理和额外尝试共享预算。

核查日期：2026-10-19。TCP、TLS、服务身份、ALPN 与保活依据所链 RFC。状态诊断表和业务时序为教学综合；真实故障、协议包与系统参数仍需按部署环境测量。
