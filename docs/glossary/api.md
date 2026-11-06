<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 后端 API 与服务词汇表

本页解释 16 组术语，按[完整术语索引](../glossary.md#api)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [后端 API 与服务文章](../knowledge/api/index.md)

## 本页术语

- [REST / RPC / GraphQL / gRPC](#api.styles)
- [Resource Modeling](#api.resource-model)
- [HTTP Method / Status Code](#api.http-semantics)
- [Idempotency](#api.idempotency)
- [Pagination / Cursor](#api.pagination)
- [API Versioning / Compatibility](#api.versioning)
- [OpenAPI / Protobuf / JSON Schema](#api.contracts)
- [Validation / Sanitization](#api.validation)
- [Timeout / Retry / Backoff / Jitter](#api.retries)
- [Rate Limiting / Quota](#api.limits)
- [API Gateway](#api.gateway)
- [Webhook](#api.webhook)
- [Connection Pool](#api.pool)
- [Graceful Shutdown](#api.shutdown)
- [Problem Details](#api.problem-details)
- [ETag / Conditional Request](#api.conditionals)

<a id="api.styles"></a>

## REST / RPC / GraphQL / gRPC

**ID：** `api.styles` · **建议优先级：** P0

**别名 / 检索词：** REST、RPC、GraphQL、gRPC、接口风格

**简释：** API 架构约束、调用模型、查询规范与框架的对照组。

REST 是包含统一接口等约束的架构风格；RPC 将交互建模为远程操作；GraphQL 规定类型、查询和执行；gRPC 提供围绕服务定义的 RPC 框架及协议生态。四者处于不同抽象层，可以组合，不能用 JSON、HTTP/2 或 Protobuf 分别代替其定义。

**例子：** 订单读取可使用资源式 HTTP，聚合页面可增加受控的 GraphQL 查询层，内部命令可采用 gRPC；每层仍需契约、授权和成本边界。

**深入阅读：** [API 风格与网关：接口形状怎样连接契约与执行边界](../knowledge/api/api-styles-contracts-and-gateway-boundaries.md)

<a id="api.resource-model"></a>

## Resource Modeling

**ID：** `api.resource-model` · **建议优先级：** P0

**别名 / 检索词：** Resource Modeling、资源建模

**简释：** 资源标识、状态变化与操作语义。

资源建模给业务对象稳定身份，并约定其表示、状态转换和操作语义。URL 形式只是外观，还需明确权限、并发条件和生命周期。

**例子：** 订单取消应检查当前状态和调用者权限，不能只把任意记录状态改成 cancelled。

**深入阅读：** [资源模型与输入边界：字段合法为什么仍不能保存](../knowledge/api/resource-models-input-validation-and-write-boundaries.md)

<a id="api.http-semantics"></a>

## HTTP Method / Status Code

**ID：** `api.http-semantics` · **建议优先级：** P0

**别名 / 检索词：** HTTP Method、Status Code、状态码、HTTP 方法

**简释：** 方法意图和响应结果的协议表达。

HTTP 方法表达请求意图，状态码表达协议层结果。安全性、幂等性和缓存语义各有定义，业务错误还需稳定的机器可读契约。

**例子：** GET 不应被设计成扣款操作；创建成功可返回相应状态与资源定位信息。

**深入阅读：** [HTTP 契约与分页：接口能调用，为什么仍会漏数据](../knowledge/api/contracts-and-pagination.md) · [HTTP 条件请求：缓存验证与并发更新怎样共用版本依据](../knowledge/api/conditional-requests-and-cache-validation.md)

<a id="api.idempotency"></a>

## Idempotency

**ID：** `api.idempotency` · **建议优先级：** P0

**别名 / 检索词：** Idempotency、幂等性、幂等

**简释：** 同一操作重复执行时约束业务效果。

幂等性要求同一操作重复执行时保持约定的业务效果。工程实现需定义动作标识、输入一致性、作用域、保留期和原子提交边界，响应内容未必每次相同。

**例子：** 订单已提交但响应丢失后，用原幂等键重试并查询已有结果。

**深入阅读：** [幂等性：给重复请求一个稳定的业务结果](../knowledge/api/idempotency.md) · [实验：验证本地订单写入的幂等性](../knowledge/api/idempotency-lab.md) · [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md)

<a id="api.pagination"></a>

## Pagination / Cursor

**ID：** `api.pagination` · **建议优先级：** P0

**别名 / 检索词：** Pagination、Cursor、游标分页、偏移分页

**简释：** 按偏移或位置边界分页。

偏移分页按跳过数量定位，游标分页按排序边界继续读取。稳定排序通常需要唯一的决胜字段；游标不自动提供固定快照或授权保证。

**例子：** 按创建时间和 ID 共同排序，避免同一时间戳的记录跨页重复或遗漏。

**深入阅读：** [HTTP 契约与分页：接口能调用，为什么仍会漏数据](../knowledge/api/contracts-and-pagination.md)

<a id="api.versioning"></a>

## API Versioning / Compatibility

**ID：** `api.versioning` · **建议优先级：** P0

**别名 / 检索词：** API Versioning、Compatibility、API 版本、兼容性

**简释：** 契约演进与调用方兼容。

兼容性要从调用方观察的字段、默认行为、错误和时序判断。版本号只是标识，演进还需弃用计划、迁移窗口和消费者验证。

**例子：** 把可选字段变成必填，即使 URL 未变化，也可能破坏已有调用方。

**深入阅读：** [HTTP 契约与分页：接口能调用，为什么仍会漏数据](../knowledge/api/contracts-and-pagination.md)

<a id="api.contracts"></a>

## OpenAPI / Protobuf / JSON Schema

**ID：** `api.contracts` · **建议优先级：** P0

**别名 / 检索词：** OpenAPI、Protobuf、JSON Schema、接口契约

**简释：** 接口描述与结构约束。

OpenAPI 描述 HTTP API，Protobuf 定义消息和服务，JSON Schema 约束 JSON 结构。结构合法不等于权限、业务状态或跨字段规则都成立。

**例子：** 请求通过 Schema 后，还需确认订单属于当前租户且状态允许修改。

**深入阅读：** [HTTP 契约与分页：接口能调用，为什么仍会漏数据](../knowledge/api/contracts-and-pagination.md) · [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)

<a id="api.validation"></a>

## Validation / Sanitization

**ID：** `api.validation` · **建议优先级：** P0

**别名 / 检索词：** Validation、Sanitization、输入校验、净化

**简释：** 校验输入及按上下文处理危险内容。

校验检查结构、类型、取值和语义；净化按明确规则处理允许的内容。两者不替代字段授权、SQL参数绑定或对应输出上下文的编码，也不自动解决并发保存。

**例子：** SQL 参数绑定保护值边界；HTML 文本输出仍需使用对应转义规则。

**深入阅读：** [资源模型与输入边界：字段合法为什么仍不能保存](../knowledge/api/resource-models-input-validation-and-write-boundaries.md)

<a id="api.retries"></a>

## Timeout / Retry / Backoff / Jitter

**ID：** `api.retries` · **建议优先级：** P0

**别名 / 检索词：** Timeout、Retry、Backoff、Jitter、超时、重试、退避、抖动

**简释：** 截止时间、重试和随机退避。

超时限制一次等待，退避拉开重试间隔，抖动分散集中重试。是否可重试取决于错误和副作用状态，总次数与总时间还应受共同预算限制。

**例子：** 大量客户端遇到 503 时使用带抖动的退避，避免同步重试形成下一轮尖峰。

**深入阅读：** [超时与重试预算：一次请求最多值得等多久](../knowledge/reliability/timeouts-and-retry-budgets.md) · [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md)

<a id="api.limits"></a>

## Rate Limiting / Quota

**ID：** `api.limits` · **建议优先级：** P0

**别名 / 检索词：** Rate Limiting、Quota、限流、配额

**简释：** 速率约束与时间窗口内的用量额度。

限流约束进入速率，配额约束某主体在周期内的用量；并发上限约束同时占用的工作量。键、窗口、突发容量和拒绝反馈都应成为契约。

**例子：** 每分钟请求配额未耗尽，也可能因并发连接已满而被拒绝。

**深入阅读：** [限流、并发限制与配额：分别在限制什么](../knowledge/api/rate-limits-concurrency-and-quotas.md)

<a id="api.gateway"></a>

## API Gateway

**ID：** `api.gateway` · **建议优先级：** P0

**别名 / 检索词：** API Gateway、API 网关

**简释：** 在边界统一承接路由、凭证验证和流量治理的入口层。

API Gateway 可按具体实现承担路由、TLS 或令牌验证、边界配额及协议适配。执行服务仍需保护对象与字段权限、业务接纳、幂等提交和数据库不变量；身份转发、错误映射、总预算和多层重试必须显式约定。

**例子：** 网关验证订单调用的令牌并限制入口流量，订单服务继续核对当前对象权限、是否允许取消以及重复提交结果。

**深入阅读：** [API 风格与网关：接口形状怎样连接契约与执行边界](../knowledge/api/api-styles-contracts-and-gateway-boundaries.md)

<a id="api.webhook"></a>

## Webhook

**ID：** `api.webhook` · **建议优先级：** P0

**别名 / 检索词：** Webhook

**简释：** 基于 HTTP 回调的异步事件通知。

Webhook 由事件提供方主动发起 HTTP 回调通知。接收方需验证签名、防重放并记录处理状态，双方需约定重试、重复、乱序和补偿查询。

**例子：** 同一支付事件可能重复到达，接收端按事件 ID 去重并核对业务状态。

**深入阅读：** [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md)

<a id="api.pool"></a>

## Connection Pool

**ID：** `api.pool` · **建议优先级：** P0

**别名 / 检索词：** Connection Pool、连接池

**简释：** 复用有限连接并控制等待。

连接池复用有限连接，并在池满时安排等待或拒绝。容量、获取超时、连接健康与释放规则共同决定行为；连接数过大也可能压垮下游。

**例子：** 请求总超时中应计入等待数据库连接的时间，而不仅是 SQL 执行时间。

**深入阅读：** [慢 API 排查：把执行时间与排队时间分开](../knowledge/performance/slow-api-investigation.md)

<a id="api.shutdown"></a>

## Graceful Shutdown

**ID：** `api.shutdown` · **建议优先级：** P0

**别名 / 检索词：** Graceful Shutdown、优雅关闭

**简释：** 停止接流、处理在途任务和释放资源。

优雅关闭协调发现/就绪传播、本地停止接纳、连接排空与业务结果；传播有延迟，旧连接可能继续送来新请求。预停与清理需共享期限，断开不证明业务回滚，超期需明确恢复策略。

**例子：** 部署替换实例时先退出就绪状态，再等待已接受请求完成。

**深入阅读：** [优雅关闭与请求排空：停止接流为什么仍有请求进来](../knowledge/api/graceful-shutdown-draining-and-inflight-outcomes.md)

<a id="api.problem-details"></a>

## Problem Details

**ID：** `api.problem-details` · **建议优先级：** P1

**别名 / 检索词：** Problem Details、RFC 9457、问题详情

**简释：** HTTP API 的结构化问题详情表示，以稳定的问题类型关联机器处理与人类说明。

Problem Details 用标准化问题文档表达 HTTP API 错误，稳定的问题类型可关联处理规则和文档。响应应避免泄露内部堆栈、密钥或不应暴露的对象信息。

**例子：** 客户端依据问题类型识别额度不足，界面再显示适合用户的说明。

**深入阅读：** [HTTP 契约与分页：接口能调用，为什么仍会漏数据](../knowledge/api/contracts-and-pagination.md)

<a id="api.conditionals"></a>

## ETag / Conditional Request

**ID：** `api.conditionals` · **建议优先级：** P1

**别名 / 检索词：** ETag、Conditional Request、If-Match、If-None-Match、条件请求、缓存验证

**简释：** 以表示验证器表达读取或修改的前提，区分缓存验证与条件保存；不替代授权、幂等协议或跨资源不变量。

条件请求用 ETag 等验证器表达前提。If-None-Match 常用于验证缓存，If-Match 可限制基于旧表示的修改；比较与写入仍需在服务端正确联结。

**例子：** 编辑时带上读取版本的 ETag，版本已变化则拒绝覆盖并要求重新处理。

**深入阅读：** [HTTP 条件请求：缓存验证与并发更新怎样共用版本依据](../knowledge/api/conditional-requests-and-cache-validation.md) · [CDN 与 WAF：边缘命中和请求放行分别证明什么](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [RFC 9110：HTTP 方法、状态码与条件请求](https://www.rfc-editor.org/rfc/rfc9110.html)
- [GitHub：Webhook 验签](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [Stripe：Webhook 签名、重投与事件处理](https://docs.stripe.com/webhooks)
- [RFC 9421：HTTP 消息签名](https://www.rfc-editor.org/rfc/rfc9421.html)
- [Fielding Dissertation, Chapter 5: Representational State Transfer (REST)](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [gRPC Core concepts, architecture and lifecycle](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [GraphQL September 2025 Edition](https://spec.graphql.org/September2025/)
- [GraphQL Authorization](https://graphql.org/learn/authorization/)
- [Envoy Router](https://www.envoyproxy.io/docs/envoy/v1.35.0/configuration/http/http_filters/router_filter)
- [AIP-121](https://google.aip.dev/121)
- [AIP-151](https://google.aip.dev/151)
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP Mass Assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [普通 Pod 终止流程](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [GOAWAY，RFC 9113 §6.8](https://www.rfc-editor.org/rfc/rfc9113.html#section-6.8)
- [gRPC 的优雅关闭](https://grpc.io/docs/guides/server-graceful-stop/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
