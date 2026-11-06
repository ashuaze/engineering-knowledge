---
id: "kb-api-styles-gateway"
title: "API 风格与网关：接口形状怎样连接契约与执行边界"
kind: "concept"
domain: "api"
status: "evolving"
summary: "以订单需求区分 REST、RPC、gRPC 与 GraphQL 的抽象层，说明契约、查询成本、流式调用及网关和业务服务的责任边界。"
created: "2026-10-22"
updated: "2026-10-27"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-api-contracts-pagination", "kb-security-object-authorization"]
related: ["kb-api-idempotency", "kb-api-conditional-requests", "kb-api-admission-controls", "kb-security-sessions-tokens", "kb-security-origin-csrf", "kb-networking-http-pools", "kb-networking-nat-proxy-lb", "kb-reliability-retry-budgets", "kb-engineering-contract-compatibility", "kb-security-mtls-service-identity", "kb-frontend-bff"]
tags: ["api-styles", "gateway", "contracts", "grpc", "graphql"]
---

# API 风格与网关：接口形状怎样连接契约与执行边界

学习入口：订单页要组合详情、商品和配送进度，运营端要分页导出，内部服务要取消订单并持续接收状态变化。应该怎样表达这些需求，哪些保证能放在网关，哪些必须留在执行服务？先确定访问形状与失败契约，再选择实现；协议和入口设施不能替业务作出权限、提交或容量承诺。

前置：[HTTP 契约与分页](contracts-and-pagination.md)、[对象级授权](../security/object-level-authorization.md)。本文是概念与来源核查，订单接口、数字和调用链均为纸面教学设计；没有启动服务、执行查询、部署网关或测量性能。[GraphQL](../../glossary/api.md#api.styles) 语言与执行语义固定使用 September 2025 正式规范；实现指南按 2026-10-22 读取快照，Envoy 例子固定 v1.35.0，不表示选型或版本推荐。

通用网关与客户端专用适配的职责继续见[BFF与前端适配](../frontend/backends-for-frontends-projections-and-service-boundaries.md)。

## 先分开架构约束、调用模型与具体框架

REST、RPC、GraphQL 与 gRPC 经常出现在同一张选型表，却没有处在同一抽象层。

| 概念 | 它主要规定什么 | 不能由名称直接推出什么 |
| --- | --- | --- |
| REST | 分布式超媒体系统的一组架构约束 | 路径像名词或响应是 JSON，就已符合全部约束 |
| RPC | 将交互建模为调用远程操作及其参数、结果 | 特定编码、传输协议、性能或[重试](../../glossary/api.md#api.retries)安全性 |
| gRPC | 围绕服务定义、生成代码和调用生命周期的一套 RPC 框架及协议生态 | [HTTP/2](../../glossary/networking.md#networking.http-versions) 或 [Protobuf](../../glossary/api.md#api.contracts) 单独就等于 gRPC |
| GraphQL | [类型系统](../../glossary/runtime.md#runtime.type-system)、查询语言、校验与执行、响应规则 | 自动生成高效数据库查询，或已经规定 HTTP、[认证](../../glossary/security.md#security.identity)和部署拓扑 |

Fielding 原论文第 5 章将 REST 组合为客户端与服务端分离、无状态交互、缓存、统一接口、分层系统，以及可选的按需代码。统一接口还包含资源标识、通过表示操作资源、自描述消息和超媒体驱动应用状态；“统一”不只是统一 URL 前缀。无状态约束要求请求具有理解本次交互所需的信息，并不禁止保存订单等资源状态。采用部分约束的资源式 HTTP API 很常见，但应说明采用了什么，不能仅凭 JSON 和动词命名宣称完整 REST。[来源：Fielding §5.1](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)

gRPC 默认使用 Protobuf 描述接口和消息，但两者不是同义词；Protobuf 还能用于存储或其他通信，HTTP/2 也能承载普通 HTTP API。GraphQL 执行层可以调用 RPC 服务，也能访问数据库；资源式 HTTP 入口也可转发到 gRPC 服务。因此，同一系统可以组合这些机制，组合后仍需检查每一跳的契约。[来源：gRPC Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)、[GraphQL September 2025](https://spec.graphql.org/September2025/)

## 用同一订单需求检查接口形状

教学设定：已认证用户只能读自己租户内获准访问的订单；只允许取消尚未发货的订单；运营列表按稳定顺序分页；客户端需要在响应丢失后查询取消结果。以下只是三种表达草图，未提供完整 Schema 或可运行服务。

| 需求 | 资源式 HTTP 表达 | 远程操作表达，可用 gRPC 实现 | GraphQL 表达 |
| --- | --- | --- | --- |
| 读订单与配送 | `GET /orders/o-42`，按契约返回表示或链接 | `GetOrder(order_id)`，必要时调用配送服务 | `order(id: "o-42") { id status shipment { eta } }` |
| 请求取消 | `POST /orders/o-42/cancellations`，创建可查询的取消申请 | `CancelOrder(order_id, operation_id)`，返回受理或最终结果 | `mutation { cancelOrder(input: ...) { operationId status } }` |
| 分页列表 | `GET /orders?after=...&limit=20` | `ListOrders(page_token, page_size)` | `orders(first: 20, after: ...) { edges { cursor node { id } } }` |
| 跟踪变化 | 另定事件订阅或轮询契约 | `WatchOrder(...) returns (stream OrderEvent)` | `subscription { orderChanged(id: ...) { status } }`，另定传输与恢复协议 |

资源式表达把“订单”和“取消申请”作为可定位对象，便于查询处理中和最终结果；RPC 将业务命令及返回值直接放入服务定义；GraphQL 允许客户端选择所需字段和关系。表中的 URI、方法名与分页形状均为设计选择，并非各规范要求订单必须这样建模，也不证明上述 HTTP 草图已满足全部 REST 约束。

GraphQL 的 `mutation` 可以表达命令。规范对一次 mutation 的顶层字段采用串行执行，但这不等于[数据库事务](../../glossary/database.md#database.isolation)、跨服务[原子性](../../glossary/systems.md#systems.atomicity)或多次请求之间互斥；取消条件与副作用仍由业务实现保护。`subscription` 定义响应流，却不规定传输、确认、重发和其他服务质量保证，断流后从哪里续接需另定。[来源：正式规范 §6.2](https://spec.graphql.org/September2025/#sec-Executing-Operations)

三种接口都必须保证同一业务规则：租户与对象授权、取消前的当前状态检查，以及取消申请和结果的提交边界。将 `CancelOrder` 改名为 `POST` 或 `mutation`，都不会自动建立这些保证。

## 契约要同时覆盖字段、错误与演进

[HTTP 方法](../../glossary/api.md#api.http-semantics)的安全性描述客户端不请求改变服务端状态；[幂等性](../../glossary/api.md#api.idempotency)描述相同请求重复执行的预期效果与一次相同，不要求响应逐次一致。GET 不能设计成取消订单；PUT、DELETE 和安全方法有标准幂等语义，创建取消申请的 POST 则需要额外的[业务幂等协议](idempotency.md)。方法是否允许缓存、响应是否可存储与复用也要分别判断：RFC 9110 为 GET、HEAD 和特定条件下的 POST 定义缓存语义，常见缓存主要支持前两者，不能推成“GET 一定缓存、POST 一律不缓存”。[来源：RFC 9110 §9.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2)

| 接口边界 | 需要公开的契约 | 演进时容易遗漏的行为 |
| --- | --- | --- |
| 资源式 HTTP | 方法、路径、表示、输入输出、状态码、机器可读错误、条件更新和重试规则 | 默认排序、错误类型、空值、分页令牌、缓存键与身份范围改变 |
| RPC / gRPC | 服务和方法、消息、状态、metadata、时限、流的完成与错误规则 | 字段能解码，不代表旧客户端理解新语义；改变方法或流模式影响生成代码与调用流程 |
| GraphQL | Schema、参数、可空性、可选择字段、执行结果与业务错误表示 | 删除字段、增加无默认值的必填参数、改变字段含义，都可能破坏现有操作；弃用标记不是安全删除证据 |

gRPC 有自己的状态体系，应区分 `UNAUTHENTICATED`、`PERMISSION_DENIED`、`RESOURCE_EXHAUSTED` 和 `UNAVAILABLE` 等原因，不能把 HTTP 成功响应当成 RPC 业务成功。官方状态说明也明确：`DEADLINE_EXCEEDED` 可能发生在写操作已经成功之后，`UNAVAILABLE` 不保证非幂等操作能安全重试。[来源：gRPC Status Codes](https://grpc.io/docs/guides/status-codes/)

Protobuf 的二进制演进规则应与业务兼容分开：不要复用删除字段的编号，不能随意改现有字段编号；某个改动在线格式上安全，也可能破坏生成代码的穷举分支。JSON 转码另有兼容限制，不能把二进制线格式保证原样转移过去。[来源：Proto3 Updating A Message Type](https://protobuf.dev/programming-guides/proto3/#updating)

GraphQL 要区分执行前请求错误与执行时字段错误，后者可能与部分 `data` 一起返回；非空字段错误还可能向上影响更大范围的数据。客户端必须按返回契约判断可用数据与错误。语言规范并未统一规定 HTTP 状态码和传输认证：官方 HTTP 指南与尚在制定中的 GraphQL-over-HTTP 规范是另一层约定。该指南支持 POST 承载 query/mutation，也允许 GET 承载 query；不能概括为“GraphQL 只能 POST”或“所有错误必须 HTTP 200”。具体状态处理还与媒体类型和实现有关。[来源：正式规范 §7](https://spec.graphql.org/September2025/#sec-Response)、[Serving over HTTP](https://graphql.org/learn/serving-over-http/)

契约版本不能只看 URL 的 v1、服务 package 或 Schema 版本号。应记录仍在使用的客户端和操作，验证新旧组合的输入、输出及错误行为，另见[契约测试与版本兼容](../engineering/contract-testing-and-compatibility.md)。

## 分页、流式、缓存和浏览器各有独立前提

| 工程目标 | 要落实的机制 | 不能省略的边界 |
| --- | --- | --- |
| 完整分页与导出 | 稳定完整排序、页长上限、令牌范围；必要时固定快照或结果集 | REST、RPC、GraphQL 均不自动保证跨页快照；GraphQL 的 connection 形状也是应用约定 |
| 连续状态推送 | 流的顺序、结束、[背压](../../glossary/performance.md#performance.queueing)、最大寿命，以及事件身份和恢复位置 | 同一流中的有序消息不代表断线后不丢不重，也不提供持久投递保证 |
| 公共读取缓存 | 可复用表示、缓存键、新鲜度、验证器与失效策略 | 用户、租户、权限和字段选择可能改变结果；一个 endpoint 不等于一个可共享的响应 |
| 浏览器消费 | 浏览器可用客户端、[CORS](../../glossary/security.md#security.origin)、凭证及 [CSRF](../../glossary/security.md#security.web-attacks) 策略，所需流能力 | 浏览器能使用 HTTP/2，不等于能直接调用原生 gRPC；代理适配也可能缩小流能力 |

gRPC 明确区分 unary（一请求一响应）、服务端流（一请求多响应）、客户端流（多请求一响应）和双向流（两侧独立发送）。同一次调用内，每个方向的消息顺序保持；双向流的两个方向独立，不自动产生跨方向的全序。[来源：gRPC 四类方法](https://grpc.io/docs/what-is-grpc/core-concepts/)

接收者变慢时，流控约束发送进度，框架按容量反馈安排缓冲与发送，写调用也可能等待；应用仍需限制自身排队，不能据此假定可无限缓冲。向流写入后返回，只表示消息交给框架，不证明已经发上网络，更不证明对端业务已经消费或提交；持久恢复也需另定。[来源：gRPC Flow Control](https://grpc.io/docs/guides/flow-control/)

浏览器集成需核对所选适配器。2026-10-22 读取的官方 gRPC-Web README 描述 unary 和特定模式下的服务端流，不支持客户端流及双向流；不能将该实现的范围泛化为所有浏览器方案，也不能承诺代理支持原生 gRPC 的全部模式。[来源：grpc/grpc-web Streaming Support](https://github.com/grpc/grpc-web#streaming-support)

GraphQL 查询可以通过受支持的 GET 或持久化文档标识接入 HTTP 缓存，但缓存键仍需区分操作、变量及响应所依赖的身份范围；客户端的对象缓存又有自己的标识和失效规则。把查询全部放入 POST，并不自动提供通用共享缓存；只有一个 URL 也不自动消除缓存可能性。资源式 API 的 [ETag](../../glossary/api.md#api.conditionals) 与授权边界见[HTTP 条件请求](conditional-requests-and-cache-validation.md)，所有浏览器入口继续遵守[同源、CORS 与 CSRF](../security/origins-cors-and-csrf.md)。

## GraphQL 把查询选择交给客户端，也要接住相应成本

身份认证后，业务逻辑仍要检查对象、关系与字段权限。例如用户可以读订单状态，不表示可以读 `internalRiskNote`；从 `order(id)`、订单列表、客户的反向订单关系和批量读取进入，都要落在同一授权规则上。隐藏 Schema 字段或只在顶层 resolver 检查一次，不能保护其他路径。按官方建议，resolver 调用可复用的业务授权逻辑，读取与输出时保持当前租户及字段范围，避免不同入口各写一套策略。[来源：GraphQL Authorization](https://graphql.org/learn/authorization/)

单个 HTTP 请求也可能要求大量工作：`orders(first: 100)` 下每单再选商品、配送记录和多层关联。应组合页长上限、深度与列表嵌套限制、字段别名及批量上限、成本估计和实际执行预算；仅限请求数或仅限深度均不足。浅层昂贵聚合也可能超预算，成本权重需结合数据源与真实观测修正。对受控客户端可评估经过审查的操作允许列表，但可信操作的变量仍需限额，保存了文档也不等于已受信任。[来源：GraphQL Security 的 Demand control](https://graphql.org/learn/security/#demand-control)

N+1 是另一类成本：先查 20 张订单，再在每个商品 resolver 各访问一次数据源，会放大调用。GraphQL.js 不自动合并独立 resolver；DataLoader 能在可合批的数据访问模式下合并查找并复用请求内结果，前提包括数据源有批量访问能力、结果与输入键正确对齐，以及 loader 的缓存范围不跨越不兼容的用户或权限上下文。它不能替代授权、索引、分页或总成本上限，也不能保证每种任意嵌套查询只访问一次数据库。[来源：GraphQL.js DataLoader 指南](https://www.graphql-js.org/docs/n1-dataloader/)

## gRPC 的截止时间、取消与重试不是同一种保证

客户端要显式设置合理 [deadline](../../glossary/reliability.md#reliability.retry-budget)；gRPC 默认不替所有调用设置一个有限时限。服务继续调用下游时，应传播已扣除耗时的剩余预算；有的语言默认传播，有的需要显式启用，必须按所用实现核对。收到 deadline 或取消通知后，应用仍需协作停止派生任务和释放资源，库一般不能强行中断业务处理，更不能撤销已提交事务或已发生的外部副作用。[来源：gRPC Deadlines](https://grpc.io/docs/guides/deadlines/)、[Cancellation](https://grpc.io/docs/guides/cancellation/)

gRPC 的重试会建立新的调用并重放保存的调用历史。透明重试只适用于库能判断尚未进入应用处理等特定失败窗口；扩大到应用错误的重试，需要配置次数、退避和可重试状态。收到响应头后不再继续该机制的重试，是框架调用的提交边界，不是数据库提交证明。能保存并重放消息只说明技术上可重放，不说明 `CancelOrder` 或付款动作的业务效果幂等。[来源：gRPC Retry](https://grpc.io/docs/guides/retry/)

订单取消应保留同一个业务操作标识，服务端在当前授权和原子提交规则下识别重复；超时后结果未知时走状态查询或核对路径。流已交付的部分消息、发送缓冲范围和断线续接也需单独约定，不能把 unary 的重试想象成任意长流的无缝恢复。相关提交机制见[幂等性](idempotency.md)，总时间和尝试上限见[超时与重试预算](../reliability/timeouts-and-retry-budgets.md)。

## 网关控制入口，执行服务保护业务事实

[API 网关](../../glossary/api.md#api.gateway)常在受控入口组合路由和流量治理，也可能做 [TLS](../../glossary/networking.md#networking.tls) 终止、凭证验证和协议转换。它与[反向代理](../../glossary/networking.md#networking.proxy)、[负载均衡](../../glossary/networking.md#networking.load-balancer)职责有交集，具体能力由产品、版本、过滤器和部署方式决定；不是所有入口都理解 GraphQL 文档或支持所有 gRPC 流模式。[代理与连接分段](../networking/nat-proxies-and-l4-l7-load-balancing.md)另有展开。

```text
浏览器或服务调用方
  → 网关：验证入口凭证与来源边界、选路、边界限额、传播剩余预算
  → 订单服务：当前对象/字段授权、业务接纳、状态检查、幂等与提交
  → 数据库或依赖服务：约束、并发控制、依赖调用与结果核对
```

| 责任 | 网关可承担的工作 | 执行服务仍要保护什么 |
| --- | --- | --- |
| 路由与边界认证 | 匹配路由；按配置验证客户端证书或令牌；传递受保护的身份上下文 | 验证其可信来源与用途；检查当前动作、租户、对象和字段权限 |
| 边界[配额](../../glossary/api.md#api.limits)与流量治理 | 按可信身份限速、约束请求大小或并发、拒绝明显超预算流量 | 按实际业务成本接纳；保护执行槽、数据库和下游；按契约结算用量 |
| 重试与协议适配 | 对被明确允许的操作控制尝试；执行指定的消息映射 | 保持稳定业务身份，保证提交、去重、不变量和结果查询 |
| 可观测性 | 记录入口拒绝、路由、耗时和代理尝试 | 记录业务接纳、执行和提交；用[关联标识](../../glossary/reliability.md#reliability.trace)连接证据 |

Envoy v1.35.0 提供具体而有限的例子：[Router](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_filters/router_filter)执行路由、转发和重试；[JWT Authentication](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_filters/jwt_authn_filter)按配置验证签名、发行方、受众和时间，并可把结果交给上游继续授权；[Rate limit](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_filters/rate_limit_filter)向限流服务发送描述符并处理超限或服务错误。配置这些能力仍需明确身份来源、失效时拒绝还是有界放行，以及计数范围；单实例限额和分布式业务配额也不能互换，见[限流、并发限制与配额](rate-limits-concurrency-and-quotas.md)。

若 TLS 在网关终止，网关到上游是另一个安全通道。后端连接认证到的通常是这一跳对端；声称“原调用方是谁”的转发字段，需要可信代理清洗、重写和受保护的传输，后端还应限制可提交此类上下文的调用方。不得直接信任外部传入的 `user_id`、租户头或证书转发头。Envoy 的 [XFCC 文档](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_conn_man/headers#x-forwarded-client-cert)明确存在清洗、追加和转发选择；有一个头字段不等于获得证书验证证据。服务身份与信任域继续见[mTLS 与服务身份](../security/mtls-service-identities-and-trust-boundaries.md)，凭证接受规则见[认证、会话与令牌](../security/authentication-sessions-and-tokens.md)。

### 总预算和重试责任必须跨入口定义

教学推演：入口总预算 2 秒，鉴权与排队已用 0.4 秒，保留返回与清理 0.1 秒，则下一跳至多可使用 1.5 秒；不是网关、订单服务、库存服务各重新获得 2 秒。各段[连接池与超时](../networking/http-reuse-pools-and-timeouts.md)都要核对覆盖范围，上传、排队、退避、转码和返回阶段是否计入不能靠同名配置猜测。

Envoy v1.35.0 Router 的路由超时包含其内部重试，这只是该边界的计时语义，不证明整条用户操作已经共用预算。调用方、网关、服务若各允许两次总尝试，在可触发全部重试的教学路径上，底层最多面对 `2 × 2 × 2 = 8` 次尝试；应确定主要重试责任层，协调尝试和流量预算，并禁止对不允许重放的写操作自动重试。记录原始请求、代理尝试和业务操作三个身份，才能区分负载放大与重复提交。

### 协议转换也需要错误和流的契约

Envoy v1.35.0 的 [gRPC-JSON transcoder](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_filters/grpc_json_transcoder_filter)需要服务描述符和明确的 HTTP 映射；转换后的路径、方法和流消息形状有具体规则。这是特定过滤器的能力，不能推导任意 GraphQL、JSON API 与 gRPC 都能互转。

转换边界应逐项定义：身份及 metadata 的映射、输入可空性与默认值、状态与业务错误、流终止及部分数据、超时取消和请求大小。还要区分网关在转发前拒绝、上游执行后失败、以及提交结果未知。例如，若把内部 RPC 的认证失败映射为 HTTP 401，外部挑战与错误体也需符合对外契约；不能机械把所有 RPC 错误压成 502，或因 HTTP 为 200 就丢弃 GraphQL 的字段错误。这些是本文的适配设计检查项，不是某个网关的默认行为声明。

## 按具体目标做决定

下表是基于上述机制的工程建议，不是框架性能排名。先写要保护的交互与保证，再用本系统的[延迟](../../glossary/performance.md#performance.latency-throughput)、成本和兼容证据验证选择。

| 当前目标 | 优先评估的接口组织 | 决策前要证明的条件 |
| --- | --- | --- |
| 向多类客户端提供可链接的资源读取，并利用通用 HTTP 缓存 | 明确资源和表示，采用标准方法、缓存与条件请求语义 | 身份缓存隔离、表示变体、分页和失效规则完整；若宣称 REST，要检查其余约束 |
| 内部业务命令清晰，需要多语言客户端与服务定义 | RPC；可评估 gRPC 的生成工具和调用模型 | 契约演进、调用链 deadline、业务幂等、协议和运维环境匹配 |
| 多端页面字段组合差异大，需聚合已有服务 | GraphQL 查询层可调用既有领域服务 | 对象与字段授权、可控查询成本、批量访问和[缓存失效](../../glossary/cache-search.md#cache-search.invalidation)能被维护 |
| 需要长时双向交互 | 先明确流和恢复语义，再评估原生 gRPC 或其他合适传输 | 实际客户端、代理和协议转换均支持所需模式；背压、取消、重连与事件恢复有契约 |
| 统一入口认证、限额和路由，内部逐步迁移 | 网关配合领域服务，必要时采用显式适配层 | 服务仍保护业务接纳和不变量；身份转发、错误映射、重试责任及预算不因迁移丢失 |

## 五道自检与核查范围

1. 订单接口采用名词路径、JSON 和 HTTP/2，就能分别证明完整 REST 与 gRPC 吗？还缺哪些定义或约束证据？
2. 同一 GraphQL 请求读取订单状态和内部风控备注时，认证、对象授权、字段授权和成本限制分别在哪里执行？从反向关系进入时怎样保持一致？
3. `CancelOrder` 返回 `DEADLINE_EXCEEDED` 后，为什么仍需查询结果？调用历史能重放、服务支持取消和业务幂等分别保证什么？
4. 网关已验令牌且限流通过，订单服务还必须拒绝哪些请求？若外部调用方伪造身份转发头，哪一跳负责清洗，后端依据什么信任它？
5. 将资源式 HTTP 入口转码到 gRPC，并让 SDK、网关、服务同时重试时，需要怎样定义总预算、错误映射和尝试身份，才能解释部分响应与提交结果未知？

核查日期：2026-10-22。实际联网读取 Fielding 第 5 章的 REST 约束与统一接口，RFC 9110 §9 的方法、安全、幂等及缓存语义；gRPC 官方核心概念、状态、deadline、取消、重试与流控指南；GraphQL 版本入口、September 2025 正式规范的类型、执行与响应相关章节，以及 GraphQL/GraphQL.js 官方 HTTP、授权、安全和 DataLoader 指南。读取了 gRPC-Web 官方 README 的流支持范围和 Proto3 消息演进规则。前述滚动指南仅代表核查日读取内容，不宣称所有语言、服务器或客户端版本行为相同。

网关实现依据固定为 Envoy v1.35.0 的 Router、[JWT](../../glossary/security.md#security.tokens) Authentication、Rate limit、HTTP header manipulation 和 gRPC-JSON transcoder 文档；仅用来证明所述具体代理能力与配置边界，没有执行配置或宣称其生产效果。GraphQL-over-HTTP 在核查时仍为制定中的规范，未将其当作 September 2025 语言规范的强制 HTTP 条款。订单形状、预算数字、责任表和决策表为教学设计及来源综合；未执行端到端、授权、重试、流式恢复、性能、缓存或协议转换实验，也未进行网关和 SDK 跨版本验证。
