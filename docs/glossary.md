<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 术语索引

当前有 238 组术语条目，覆盖 17 个领域；其中 44 组已连接正文。每组可能包含多个相关缩写，不能当作独立概念数量。

“已收录”表示已有索引简释；“有正文”表示可继续阅读深入文章。简释用于定位，不替代机制、边界和版本说明。P0/P1/P2 为默认学习建议，可按岗位、已有基础和当前任务调整。

术语清单作为知识索引；[实际工程问题](problems.md)作为学习入口。阅读时结合具体约束理解概念，重点积累底层原理、系统设计、故障诊断和技术权衡能力。

[计算机系统与操作系统](#systems) · [计算机网络与协议](#networking) · [数据结构与算法](#algorithms) · [编程语言与 Runtime](#runtime) · [前端与浏览器](#frontend) · [后端 API 与服务](#api) · [软件架构与设计](#architecture) · [身份、安全与权限](#security) · [数据库与存储](#database) · [缓存、检索与对象存储](#cache-search) · [消息队列与事件驱动](#messaging) · [分布式系统](#distributed) · [性能与容量](#performance) · [Linux、云与交付](#devops) · [可观测性与可靠性](#reliability) · [软件质量与研发](#engineering) · [LLM、RAG 与 Agent 工程](#ai)

<a id="systems"></a>

## 计算机系统与操作系统

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `systems.execution-units`<br>Process / Thread / Coroutine | 进程、线程与协程，资源、执行和调度边界。 | P0 | 有正文：[概念](knowledge/systems/process-thread-coroutine.md) |
| `systems.concurrency`<br>Concurrency / Parallelism | 并发推进与并行执行，关注调度和硬件资源。 | P0 | 有正文：[概念](knowledge/systems/process-thread-coroutine.md) |
| `systems.blocking`<br>Blocking / Non-blocking | 指定操作会不会让当前执行线程等待。 | P0 | 有正文：[对比](knowledge/runtime/async-and-blocking.md) |
| `systems.context-switch`<br>Context Switch | 保存和恢复执行上下文及其开销。 | P0 | 已收录 |
| `systems.privilege`<br>User Mode / Kernel Mode / Syscall | 权限边界、系统调用和内核服务。 | P0 | 已收录 |
| `systems.memory-layout`<br>Stack / Heap | 调用栈、动态分配和对象生命周期。 | P0 | 已收录 |
| `systems.virtual-memory`<br>Virtual Memory / Paging | 地址映射、分页和缺页处理。 | P0 | 已收录 |
| `systems.synchronization`<br>Mutex / Semaphore / CAS | 互斥、资源计数与原子比较交换。 | P0 | 已收录 |
| `systems.race-deadlock`<br>Race Condition / Deadlock | 时序依赖错误与循环等待。 | P0 | 已收录 |
| `systems.fd-socket`<br>File Descriptor / Socket | 操作系统资源句柄与通信端点。 | P0 | 已收录 |
| `systems.io-multiplexing`<br>I/O Multiplexing / epoll | 监视多个 I/O 就绪事件，减少逐连接阻塞等待。 | P0 | 已收录 |
| `systems.memory-order`<br>Memory Model / Happens-before | 跨执行单元的可见性、顺序与同步关系。 | P0 | 已收录 |

<a id="networking"></a>

## 计算机网络与协议

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `networking.network-model`<br>OSI / TCP-IP Model | 网络职责分层和封装。 | P0 | 已收录 |
| `networking.transport`<br>IP / TCP / UDP | 寻址、字节流可靠传输和数据报。 | P0 | 已收录 |
| `networking.dns`<br>DNS / TTL | 域名解析与记录缓存有效期。 | P0 | 有正文：[概念](knowledge/networking/https-request-lifecycle.md) |
| `networking.tcp-handshake`<br>TCP Handshake | 连接建立及连接状态。 | P0 | 已收录 |
| `networking.transport-control`<br>Flow Control / Congestion Control | 接收方能力约束与网络拥塞调节。 | P0 | 已收录 |
| `networking.tls`<br>TLS / HTTPS / PKI | 传输加密、身份校验与证书信任。 | P0 | 有正文：[概念](knowledge/networking/https-request-lifecycle.md) |
| `networking.http-versions`<br>HTTP/1.1 / HTTP/2 / HTTP/3 | HTTP 传输机制和多路复用差异。 | P0 | 有正文：[概念](knowledge/networking/https-request-lifecycle.md) |
| `networking.quic`<br>QUIC | 基于 UDP、集成安全机制的传输协议。 | P0 | 已收录 |
| `networking.keepalive`<br>Keep-Alive / Connection Reuse | 连接复用、空闲管理和连接成本。 | P0 | 有正文：[概念](knowledge/networking/https-request-lifecycle.md) |
| `networking.proxy`<br>Proxy / Reverse Proxy | 代理客户端或服务端接收请求。 | P0 | 有正文：[概念](knowledge/networking/https-request-lifecycle.md) |
| `networking.load-balancer`<br>Load Balancer / L4 / L7 | 按传输层或应用层信息分发流量。 | P0 | 已收录 |
| `networking.cdn-waf`<br>CDN / WAF | 内容边缘分发与应用层请求防护。 | P0 | 已收录 |

<a id="algorithms"></a>

## 数据结构与算法

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `algorithms.complexity`<br>Time / Space Complexity | 时间、空间随输入规模增长的趋势。 | P0 | 有正文：[概念](knowledge/algorithms/complexity-and-data-structures.md) |
| `algorithms.sequences`<br>Array / Linked List | 连续或链式存储及访问和修改成本。 | P0 | 有正文：[概念](knowledge/algorithms/complexity-and-data-structures.md) |
| `algorithms.hash-table`<br>Hash Table / Hash Function | 键映射、碰撞处理和负载因子。 | P0 | 有正文：[概念](knowledge/algorithms/complexity-and-data-structures.md) |
| `algorithms.queues`<br>Stack / Queue / Deque | 后进先出、先进先出与双端操作。 | P0 | 已收录 |
| `algorithms.trees`<br>Tree / Heap / Trie | 层级关系、优先级和前缀索引。 | P0 | 已收录 |
| `algorithms.b-tree`<br>B-Tree / B+Tree | 面向页访问的多路平衡树及索引组织。 | P0 | 已收录 |
| `algorithms.sorting-search`<br>Sorting / Binary Search | 排序与有序区间上的查找。 | P0 | 已收录 |
| `algorithms.graph-traversal`<br>Graph / BFS / DFS | 关系建模与图遍历。 | P0 | 已收录 |
| `algorithms.bloom`<br>Bloom Filter | 允许误报的集合成员近似判断。 | P0 | 已收录 |
| `algorithms.eviction`<br>LRU / LFU | 按访问新近程度或频率淘汰缓存。 | P0 | 已收录 |
| `algorithms.amortized`<br>Amortized Analysis | 在一系列操作上分摊成本。 | P0 | 有正文：[概念](knowledge/algorithms/complexity-and-data-structures.md) |
| `algorithms.probabilistic`<br>Probabilistic Data Structure | 用可控误差换取空间或时间效率。 | P0 | 已收录 |

<a id="runtime"></a>

## 编程语言与 Runtime

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `runtime.compilation`<br>Compiler / Interpreter / JIT | 编译、解释与运行期间的编译优化。 | P0 | 已收录 |
| `runtime.virtual-machine`<br>Runtime / VM | 执行语言所需的调度、内存和宿主能力。 | P0 | 已收录 |
| `runtime.event-loop`<br>Event Loop | 协调任务、I/O 完成事件和回调执行。 | P0 | 有正文：[对比](knowledge/runtime/async-and-blocking.md)、[概念](knowledge/frontend/long-tasks-and-responsiveness.md) |
| `runtime.async`<br>Sync / Async / Promise / Async-Await | 调用结果的交付与异步控制流。 | P0 | 有正文：[对比](knowledge/runtime/async-and-blocking.md) |
| `runtime.microtasks`<br>Task / Microtask | 宿主调度任务和微任务，具体规则依 Runtime 而异。 | P0 | 已收录 |
| `runtime.closure`<br>Closure / Scope | 词法作用域和对外部绑定的访问。 | P0 | 已收录 |
| `runtime.gc`<br>GC / Reference Counting | 自动内存回收策略及其代价。 | P0 | 已收录 |
| `runtime.type-system`<br>Type System / Type Inference | 类型约束和自动类型推导。 | P0 | 已收录 |
| `runtime.generics`<br>Generics / Structural Typing | 参数化类型与按结构兼容的类型关系。 | P0 | 已收录 |
| `runtime.serialization`<br>Serialization / Deserialization | 在运行时对象和交换格式间转换。 | P0 | 已收录 |
| `runtime.errors`<br>Exception / Error Propagation | 失败信号、传播边界与资源清理。 | P0 | 已收录 |
| `runtime.modules`<br>Module System / Dependency | 模块加载、依赖解析和初始化。 | P0 | 已收录 |
| `runtime.ffi-wasm`<br>FFI / WebAssembly | 语言边界调用与可移植字节码执行。 | P0 | 已收录 |

<a id="frontend"></a>

## 前端与浏览器

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `frontend.render-tree`<br>DOM / CSSOM / Render Tree | 文档、样式和渲染结构。 | P1 | 已收录 |
| `frontend.render-pipeline`<br>Layout / Paint / Compositing | 布局计算、绘制与图层合成。 | P1 | 已收录 |
| `frontend.rendering-strategies`<br>CSR / SSR / SSG / ISR | 客户端渲染、服务端渲染、预生成与增量再生成。 | P1 | 已收录 |
| `frontend.hydration`<br>Hydration | 让服务端输出的页面连接客户端交互逻辑。 | P1 | 已收录 |
| `frontend.spa`<br>SPA / Client-side Routing | 单页导航与客户端路由状态。 | P1 | 已收录 |
| `frontend.state`<br>Reactivity / State Management | 数据变化、界面更新及状态所有权。 | P1 | 已收录 |
| `frontend.vdom`<br>Virtual DOM / Reconciliation | UI 描述与更新协调策略。 | P1 | 已收录 |
| `frontend.bundling`<br>Bundling / Tree Shaking | 模块打包与可证明无用代码的移除。 | P1 | 已收录 |
| `frontend.offline`<br>Browser Cache / Service Worker | 响应复用、请求代理和离线能力。 | P1 | 已收录 |
| `frontend.realtime`<br>WebSocket / SSE | 双向连接通信与服务器事件推送。 | P1 | 已收录 |
| `frontend.web-vitals`<br>Core Web Vitals | 衡量加载、交互和布局稳定性的指标集合。 | P1 | 已收录 |
| `frontend.bff`<br>BFF | 为特定客户端提供聚合和适配的后端。 | P1 | 已收录 |
| `frontend.long-tasks`<br>Long Task / Main-thread Yielding | 识别持续占用主线程的任务，分批执行并让出调度机会。 | P1 | 有正文：[概念](knowledge/frontend/long-tasks-and-responsiveness.md) |

<a id="api"></a>

## 后端 API 与服务

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `api.styles`<br>REST / RPC / GraphQL / gRPC | API 风格、查询模型与调用协议。 | P0 | 已收录 |
| `api.resource-model`<br>Resource Modeling | 资源标识、状态变化与操作语义。 | P0 | 已收录 |
| `api.http-semantics`<br>HTTP Method / Status Code | 方法意图和响应结果的协议表达。 | P0 | 已收录 |
| `api.idempotency`<br>Idempotency | 同一操作重复执行时约束业务效果。 | P0 | 有正文：[概念](knowledge/api/idempotency.md)、[实验](knowledge/api/idempotency-lab.md) |
| `api.pagination`<br>Pagination / Cursor | 按偏移或位置边界分页。 | P0 | 已收录 |
| `api.versioning`<br>API Versioning / Compatibility | 契约演进与调用方兼容。 | P0 | 已收录 |
| `api.contracts`<br>OpenAPI / Protobuf / JSON Schema | 接口描述与结构约束。 | P0 | 已收录 |
| `api.validation`<br>Validation / Sanitization | 校验输入及按上下文处理危险内容。 | P0 | 已收录 |
| `api.retries`<br>Timeout / Retry / Backoff / Jitter | 截止时间、重试和随机退避。 | P0 | 有正文：[概念](knowledge/reliability/timeouts-and-retry-budgets.md) |
| `api.limits`<br>Rate Limiting / Quota | 速率约束与时间窗口内的用量额度。 | P0 | 已收录 |
| `api.gateway`<br>API Gateway | 统一流量入口和横切治理。 | P0 | 已收录 |
| `api.webhook`<br>Webhook | 基于 HTTP 回调的异步事件通知。 | P0 | 已收录 |
| `api.pool`<br>Connection Pool | 复用有限连接并控制等待。 | P0 | 有正文：[案例](knowledge/performance/slow-api-investigation.md) |
| `api.shutdown`<br>Graceful Shutdown | 停止接流、处理在途任务和释放资源。 | P0 | 已收录 |

<a id="architecture"></a>

## 软件架构与设计

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `architecture.principles`<br>SOLID / KISS / DRY / YAGNI | 设计原则和复杂度约束，须结合上下文使用。 | P0 | 已收录 |
| `architecture.coupling`<br>Cohesion / Coupling | 职责聚合程度与组件间依赖。 | P0 | 已收录 |
| `architecture.concerns`<br>Separation of Concerns | 按职责隔离不同变化来源。 | P0 | 已收录 |
| `architecture.layering`<br>Layered Architecture | 职责分层和依赖方向。 | P0 | 已收录 |
| `architecture.modular-monolith`<br>Modular Monolith | 在同一部署单元内保持模块边界。 | P0 | 已收录 |
| `architecture.microservices`<br>Microservices | 独立演进和部署的服务及其协调成本。 | P0 | 已收录 |
| `architecture.ddd`<br>DDD / Bounded Context | 领域建模与模型适用范围。 | P0 | 已收录 |
| `architecture.domain-model`<br>Entity / Value Object / Aggregate | 标识、值语义与一致性边界。 | P0 | 已收录 |
| `architecture.ports-adapters`<br>Clean / Hexagonal Architecture | 通过依赖方向和端口隔离核心业务。 | P0 | 已收录 |
| `architecture.di`<br>Dependency Injection / IoC | 外部提供依赖与控制关系反转。 | P0 | 已收录 |
| `architecture.cqrs`<br>CQRS | 分离修改状态与读取状态的模型。 | P0 | 已收录 |
| `architecture.event-sourcing`<br>Event Sourcing | 以事件序列记录状态演进。 | P0 | 已收录 |
| `architecture.patterns`<br>Design Pattern / Anti-pattern | 可复用设计经验及常见不良结构。 | P0 | 已收录 |
| `architecture.adr`<br>ADR | 记录特定上下文中的决策、备选方案及后果。 | P0 | 有正文：[决策](knowledge/architecture/knowledge-base-adr.md) |
| `architecture.debt`<br>Technical Debt / Refactoring | 演进成本与保持行为的结构调整。 | P0 | 已收录 |
| `architecture.strangler`<br>Strangler Fig Pattern | 渐进替换旧系统的迁移方法。 | P0 | 已收录 |

<a id="security"></a>

## 身份、安全与权限

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `security.identity`<br>Authentication / Authorization | 证明身份与判断访问权。 | P0 | 有正文：[概念](knowledge/security/object-level-authorization.md) |
| `security.sessions`<br>Session / Cookie | 会话状态和浏览器保存、发送的数据。 | P0 | 已收录 |
| `security.oauth`<br>OAuth 2.0 / OpenID Connect | 委托授权框架与其上的身份层。 | P0 | 已收录 |
| `security.tokens`<br>JWT / JWS / JWK | 声明容器、签名格式和密钥表示。 | P0 | 已收录 |
| `security.access-control`<br>RBAC / ABAC | 按角色或属性判断权限。 | P0 | 有正文：[概念](knowledge/security/object-level-authorization.md) |
| `security.token-lifecycle`<br>Access Token / Refresh Token | 访问凭据和更新访问凭据的机制。 | P0 | 已收录 |
| `security.origin`<br>CORS / Same-Origin Policy | 浏览器同源边界与跨源响应访问机制。 | P0 | 已收录 |
| `security.web-attacks`<br>XSS / CSRF / SSRF | 脚本注入、跨站请求伪造和服务端请求伪造。 | P0 | 已收录 |
| `security.sql-injection`<br>SQL Injection / Parameterized Query | 查询结构注入与参数绑定防护。 | P0 | 已收录 |
| `security.passwords`<br>Hash / Salt / KDF | 哈希、随机盐和适合口令的派生机制。 | P0 | 已收录 |
| `security.mtls`<br>mTLS / Certificate | 连接两端的证书身份校验。 | P0 | 已收录 |
| `security.secrets`<br>Secrets Management | 敏感凭据的保存、分发与轮换。 | P0 | 已收录 |
| `security.trust`<br>Least Privilege / Zero Trust | 最小授权和持续验证访问条件。 | P0 | 已收录 |
| `security.threats`<br>Threat Modeling / OWASP | 识别攻击面并参考应用安全研究与规范。 | P0 | 已收录 |
| `security.tenant-isolation`<br>Tenant Isolation / Object-level Authorization | 租户边界与逐对象访问检查。 | P0 | 有正文：[概念](knowledge/security/object-level-authorization.md) |

<a id="database"></a>

## 数据库与存储

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `database.db-models`<br>RDBMS / NoSQL | 关系模型及多种非关系数据模型。 | P0 | 已收录 |
| `database.workloads`<br>OLTP / OLAP | 在线事务与分析型访问模式。 | P0 | 已收录 |
| `database.acid`<br>ACID | 事务原子性、约束一致性、隔离性和持久性。 | P0 | 已收录 |
| `database.isolation`<br>Transaction / Isolation Level | 事务边界及并发可见性保证。 | P0 | 有正文：[概念](knowledge/database/concurrent-inventory.md) |
| `database.anomalies`<br>Dirty / Non-repeatable / Phantom Read | 读取未提交数据、重复读取变化和结果集变化。 | P0 | 已收录 |
| `database.mvcc`<br>MVCC | 用数据版本协调读写并发。 | P0 | 已收录 |
| `database.locking`<br>Optimistic / Pessimistic Lock | 检测冲突后处理与提前限制竞争。 | P0 | 有正文：[概念](knowledge/database/concurrent-inventory.md) |
| `database.indexes`<br>Index / Covering Index | 缩小访问范围及从索引满足查询。 | P0 | 已收录 |
| `database.plans`<br>Query Plan / EXPLAIN | 数据库执行路径、估算与实际执行信息。 | P0 | 已收录 |
| `database.recovery-log`<br>WAL / Redo / Undo | 预写、重放与回滚相关日志机制，细节因引擎而异。 | P0 | 已收录 |
| `database.normalization`<br>Normalization / Denormalization | 减少冗余与按访问需求引入冗余。 | P0 | 已收录 |
| `database.replication`<br>Replication / Read Replica | 复制状态并提供副本读取。 | P0 | 已收录 |
| `database.partitioning`<br>Partitioning / Sharding | 在逻辑或节点间拆分数据。 | P0 | 已收录 |
| `database.prepared`<br>Prepared Statement | 参数化执行与可能的计划复用，依驱动和数据库而异。 | P0 | 已收录 |
| `database.migration`<br>Schema Migration / CDC | 结构演进与数据变更捕获。 | P0 | 已收录 |
| `database.constraints`<br>Unique Constraint / Foreign Key | 由数据库维护唯一性和引用关系。 | P0 | 有正文：[概念](knowledge/api/idempotency.md)、[概念](knowledge/database/concurrent-inventory.md) |

<a id="cache-search"></a>

## 缓存、检索与对象存储

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `cache-search.cache-read`<br>Cache Aside / Read Through | 应用管理缓存或由缓存层加载数据。 | P0 | 有正文：[概念](knowledge/cache-search/cache-aside-and-invalidation.md) |
| `cache-search.cache-write`<br>Write Through / Write Behind | 写入同步持久化或延后异步写回。 | P0 | 已收录 |
| `cache-search.invalidation`<br>Cache Invalidation / TTL | 主动失效与按时过期。 | P0 | 有正文：[概念](knowledge/cache-search/cache-aside-and-invalidation.md) |
| `cache-search.cache-failures`<br>Penetration / Breakdown / Avalanche | 不存在键回源、热点失效和批量失效问题。 | P0 | 已收录 |
| `cache-search.stampede`<br>Cache Stampede | 并发未命中引发重复加载与回源放大。 | P0 | 有正文：[概念](knowledge/cache-search/cache-aside-and-invalidation.md) |
| `cache-search.redis-types`<br>Redis Data Structures | 按访问语义选择字符串、哈希、集合、有序集合和流。 | P0 | 已收录 |
| `cache-search.lock-lease`<br>Distributed Lock / Lease | 跨节点互斥及有期限的持有权。 | P0 | 已收录 |
| `cache-search.inverted`<br>Inverted Index | 从词项定位包含它的文档。 | P0 | 已收录 |
| `cache-search.bm25`<br>BM25 / Full-text Search | 基于词项统计的相关性排序与全文检索。 | P0 | 已收录 |
| `cache-search.vectors`<br>Embedding / Similarity Search | 向量表示与距离或相似性查找。 | P0 | 已收录 |
| `cache-search.ann`<br>ANN / HNSW | 近似近邻搜索及分层图索引。 | P0 | 已收录 |
| `cache-search.hybrid`<br>Hybrid Search / Reranking | 组合多种召回并重新评分排序。 | P0 | 已收录 |
| `cache-search.objects`<br>Object Storage / Presigned URL | 按对象保存数据与限时签名访问。 | P0 | 已收录 |

<a id="messaging"></a>

## 消息队列与事件驱动

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `messaging.models`<br>MQ / Pub-Sub / Event Streaming | 队列分发、广播订阅和可重放事件流。 | P1 | 已收录 |
| `messaging.roles`<br>Producer / Consumer / Broker | 消息写入、处理与服务端存储分发角色。 | P1 | 已收录 |
| `messaging.positions`<br>Topic / Partition / Offset | 主题、分区和分区内位置。 | P1 | 已收录 |
| `messaging.groups`<br>Consumer Group | 多个消费者协作分担读取。 | P1 | 已收录 |
| `messaging.delivery`<br>At-most-once / At-least-once | 可能丢失不重投与可能重复的投递保证。 | P1 | 已收录 |
| `messaging.exactly-once`<br>Exactly-once Semantics | 在明确组件和事务范围内限制重复处理效果。 | P1 | 有正文：[模式](knowledge/messaging/transactional-outbox.md) |
| `messaging.consumer-idempotency`<br>Idempotent Consumer | 重复消费仍保持受约束的业务效果。 | P1 | 已收录 |
| `messaging.ordering`<br>Ordering / Partition Key | 在指定范围内维持顺序。 | P1 | 已收录 |
| `messaging.retry-dlq`<br>Dead Letter Queue / Retry Queue | 隔离持续失败消息与安排重试。 | P1 | 已收录 |
| `messaging.backpressure`<br>Backpressure | 下游将容量压力传回上游。 | P1 | 已收录 |
| `messaging.outbox`<br>Transactional Outbox | 同一事务记录业务变化和待发布事件。 | P1 | 有正文：[模式](knowledge/messaging/transactional-outbox.md) |
| `messaging.cdc`<br>CDC / Asynchronous Processing | 捕获数据变化并解耦后续处理。 | P1 | 已收录 |

<a id="distributed"></a>

## 分布式系统

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `distributed.cap`<br>CAP / PACELC | 分区下的取舍及正常情况下延迟和一致性的权衡。 | P1 | 已收录 |
| `distributed.consistency`<br>Strong / Eventual Consistency | 不同可见性保证，强一致须进一步说明具体模型。 | P1 | 有正文：[概念](knowledge/distributed/consistency-and-replication.md) |
| `distributed.linear-serial`<br>Linearizability / Serializability | 实时单操作顺序与事务可串行执行的等价性。 | P1 | 有正文：[概念](knowledge/distributed/consistency-and-replication.md) |
| `distributed.consensus`<br>Consensus / Raft | 在故障模型下就日志或状态达成一致。 | P1 | 已收录 |
| `distributed.leadership`<br>Leader Election / Quorum | 选主与按法定集合达成读写条件。 | P1 | 已收录 |
| `distributed.fencing`<br>Heartbeat / Lease / Fencing Token | 存活检测、限时持有与拒绝过期执行者。 | P1 | 已收录 |
| `distributed.lag`<br>Replication Lag | 副本应用变更落后于上游。 | P1 | 有正文：[概念](knowledge/distributed/consistency-and-replication.md) |
| `distributed.split-brain`<br>Split Brain | 多个节点同时认为自己拥有权威。 | P1 | 已收录 |
| `distributed.partition`<br>Network Partition | 节点间通信被切断或严重不可达。 | P1 | 有正文：[概念](knowledge/distributed/consistency-and-replication.md) |
| `distributed.2pc`<br>Distributed Transaction / 2PC | 跨参与者协调提交及其阻塞等成本。 | P1 | 已收录 |
| `distributed.saga`<br>Saga / Compensation | 多步业务通过补偿应对部分成功。 | P1 | 已收录 |
| `distributed.hashing`<br>Consistent Hashing | 减少节点变化时键重新分布的范围。 | P1 | 已收录 |
| `distributed.clocks`<br>Logical Clock / Clock Skew | 因果顺序表示与物理时钟偏差。 | P1 | 已收录 |
| `distributed.ids`<br>Snowflake ID / ULID | 不同的分布式或可排序标识生成方案。 | P1 | 已收录 |

<a id="performance"></a>

## 性能与容量

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `performance.latency-throughput`<br>Latency / Throughput | 完成一次操作的时间与单位时间处理量。 | P0 | 已收录 |
| `performance.rates`<br>QPS / RPS / TPS | 查询、请求和事务速率，须写清计数口径。 | P0 | 已收录 |
| `performance.percentiles`<br>P50 / P95 / P99 | 观测窗口内延迟分布的分位数。 | P0 | 已收录 |
| `performance.bound`<br>CPU-bound / I/O-bound | 瓶颈主要在计算还是 I/O 等待。 | P0 | 已收录 |
| `performance.little`<br>Little’s Law | 稳定系统中平均在途量、到达率和停留时间的关系。 | P0 | 已收录 |
| `performance.profiling`<br>Profiling / Flame Graph | 采样或插桩分析与堆栈聚合展示。 | P0 | 已收录 |
| `performance.load-tests`<br>Load / Stress / Soak Test | 目标负载、极限负载和长时间运行验证。 | P0 | 已收录 |
| `performance.scaling`<br>Horizontal / Vertical Scaling | 增加实例与提升单实例资源。 | P0 | 已收录 |
| `performance.batching`<br>Batching / Pipelining | 合并操作和重叠多个执行阶段。 | P0 | 已收录 |
| `performance.overload`<br>Rate Limiting / Load Shedding | 约束进入速率和过载时拒绝工作。 | P0 | 已收录 |
| `performance.contention`<br>Hotspot / Contention | 局部集中访问与共享资源竞争。 | P0 | 已收录 |
| `performance.queueing`<br>Queueing / Backpressure | 等待队列形成和压力反馈。 | P0 | 有正文：[案例](knowledge/performance/slow-api-investigation.md) |
| `performance.capacity`<br>Capacity Planning | 用工作负载、资源余量和增长预估容量。 | P0 | 已收录 |

<a id="devops"></a>

## Linux、云与交付

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `devops.linux`<br>Linux Process / Signal / Permission | 进程生命周期、信号与访问权限。 | P1 | 已收录 |
| `devops.isolation`<br>Namespace / cgroups | 资源视图隔离和用量限制。 | P1 | 已收录 |
| `devops.containers`<br>Image / Container | 文件系统与配置模板及其运行实例。 | P1 | 已收录 |
| `devops.k8s`<br>Pod / Deployment / Service | 工作单元、声明式副本管理与服务访问。 | P1 | 已收录 |
| `devops.entry`<br>Ingress / Gateway API | 集群入口路由与流量管理接口。 | P1 | 已收录 |
| `devops.discovery`<br>Service Discovery | 查找当前可用服务实例。 | P1 | 已收录 |
| `devops.cloud-network`<br>VPC / Subnet / Security Group | 云网络边界和访问控制。 | P1 | 已收录 |
| `devops.iac`<br>IaC / Terraform | 以版本化声明管理基础设施。 | P1 | 已收录 |
| `devops.cicd`<br>CI / CD | 持续集成、交付或自动部署。 | P1 | 有正文：[概念](knowledge/devops/build-deploy-rollback.md) |
| `devops.rollout`<br>Rolling / Blue-Green / Canary | 不同发布替换和流量迁移策略。 | P1 | 有正文：[概念](knowledge/devops/build-deploy-rollback.md) |
| `devops.flags`<br>Feature Flag | 按条件启用行为并管理开关生命周期。 | P1 | 有正文：[概念](knowledge/devops/build-deploy-rollback.md) |
| `devops.immutable`<br>Immutable Infrastructure | 通过替换实例交付新配置。 | P1 | 已收录 |
| `devops.autoscaling`<br>Autoscaling / HPA | 基于观测信号调整资源或副本数。 | P1 | 已收录 |
| `devops.regions`<br>Multi-AZ / Multi-Region | 跨可用区与跨地域部署。 | P1 | 已收录 |

<a id="reliability"></a>

## 可观测性与可靠性

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `reliability.signals`<br>Logs / Metrics / Traces | 离散事件、聚合数值与请求因果链。 | P0 | 已收录 |
| `reliability.otel`<br>OpenTelemetry | 可观测性 API、SDK、协议及采集生态。 | P0 | 已收录 |
| `reliability.trace`<br>Trace ID / Span / Correlation ID | 链路标识、执行片段和业务关联。 | P0 | 已收录 |
| `reliability.methods`<br>RED / USE | 请求速率错误延迟与资源使用率饱和错误。 | P0 | 已收录 |
| `reliability.slos`<br>SLI / SLO / SLA | 指标、目标和对外服务约定。 | P0 | 已收录 |
| `reliability.budget`<br>Error Budget | 由可靠性目标推导的可接受失败额度。 | P0 | 已收录 |
| `reliability.availability`<br>Availability / Reliability | 可提供服务的程度与持续正确工作的能力。 | P0 | 已收录 |
| `reliability.recovery`<br>RTO / RPO | 恢复耗时目标和可接受数据丢失范围。 | P0 | 已收录 |
| `reliability.isolation`<br>Circuit Breaker / Bulkhead | 熔断失败依赖与隔离资源池。 | P0 | 已收录 |
| `reliability.retry-budget`<br>Timeout / Deadline / Retry Budget | 限制等待时间、传播截止时间并约束重试消耗。 | P0 | 有正文：[概念](knowledge/reliability/timeouts-and-retry-budgets.md) |
| `reliability.probes`<br>Readiness / Liveness | 是否接收流量与是否需要重启的探测。 | P0 | 已收录 |
| `reliability.dr`<br>Disaster Recovery / Failover | 灾难恢复计划与服务切换。 | P0 | 已收录 |
| `reliability.incidents`<br>Incident Response / Postmortem | 止损、诊断、恢复与复盘。 | P0 | 已收录 |
| `reliability.chaos`<br>Chaos Engineering | 通过受控故障验证系统假设。 | P0 | 已收录 |

<a id="engineering"></a>

## 软件质量与研发

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `engineering.tests`<br>Unit / Integration / E2E Test | 按验证边界划分的测试。 | P0 | 有正文：[概念](knowledge/engineering/test-scopes-and-doubles.md) |
| `engineering.contracts`<br>Contract Testing | 验证交互契约的兼容性。 | P0 | 有正文：[概念](knowledge/engineering/test-scopes-and-doubles.md) |
| `engineering.doubles`<br>Mock / Stub / Fake | 交互验证、固定行为和简化实现等测试替身。 | P0 | 有正文：[概念](knowledge/engineering/test-scopes-and-doubles.md) |
| `engineering.tdd`<br>TDD / BDD | 以测试或可讨论的行为规格推动开发。 | P0 | 已收录 |
| `engineering.generative`<br>Property-based / Fuzz Testing | 自动生成输入验证性质或探测异常。 | P0 | 已收录 |
| `engineering.regression`<br>Regression Testing | 验证原有行为未被意外破坏。 | P0 | 已收录 |
| `engineering.pyramid`<br>Test Pyramid | 关于不同测试层次成本与数量的经验模型。 | P0 | 已收录 |
| `engineering.analysis`<br>Static Analysis / Lint | 静态推断缺陷与检查约定。 | P0 | 已收录 |
| `engineering.review`<br>Code Review | 共同检查变更并传播上下文。 | P0 | 已收录 |
| `engineering.trunk`<br>Trunk-based Development | 短生命周期分支和频繁集成。 | P0 | 已收录 |
| `engineering.semver`<br>Semantic Versioning | 通过版本号表达兼容性意图。 | P0 | 已收录 |
| `engineering.supply-chain`<br>Dependency Management / SBOM | 依赖解析、维护与组件清单。 | P0 | 已收录 |
| `engineering.design-docs`<br>ADR / RFC / Design Doc | 决策记录、提案和设计说明。 | P0 | 已收录 |
| `engineering.sdd`<br>Spec-Driven Development | 以可验证规格约束实现和验收。 | P0 | 已收录 |
| `engineering.dx`<br>Golden Path / Developer Experience | 标准交付路径和研发使用体验。 | P0 | 已收录 |

<a id="ai"></a>

## LLM、RAG 与 Agent 工程

| ID / 术语 | 简释 | 优先级 | 覆盖 |
| --- | --- | --- | --- |
| `ai.context`<br>Token / Context Window | 模型处理单元及单次可处理的上下文范围。 | P1 | 已收录 |
| `ai.instructions`<br>Prompt / System Instruction | 任务输入、约束和应用定义的指令边界。 | P1 | 已收录 |
| `ai.sampling`<br>Temperature / Sampling | 生成时的分布变换和采样方法。 | P1 | 已收录 |
| `ai.structured`<br>Structured Output / JSON Schema | 按结构约束生成并校验结果。 | P1 | 已收录 |
| `ai.tools`<br>Tool Calling / Function Calling | 模型提出工具请求，由宿主校验和执行。 | P1 | 已收录 |
| `ai.embeddings`<br>Embedding / Vector Store | 内容向量化与相应检索存储。 | P1 | 已收录 |
| `ai.rag`<br>RAG / Retrieval Pipeline | 获取相关证据并供生成使用的流程。 | P1 | 已收录 |
| `ai.grounding`<br>Chunking / Reranking / Grounding | 文档切分、候选重排和答案证据约束。 | P1 | 已收录 |
| `ai.loop`<br>Agent Loop | 决策、行动、观察与停止控制循环。 | P1 | 有正文：[概念](knowledge/ai/recoverable-runtime.md) |
| `ai.planning`<br>Planning / Routing / Handoff | 任务分解、处理路径选择和控制权移交。 | P1 | 已收录 |
| `ai.harness`<br>Harness / Orchestration | 围绕模型的执行、工具、状态和控制体系。 | P1 | 已收录 |
| `ai.mcp`<br>MCP | 模型应用连接工具和上下文的协议体系。 | P1 | 已收录 |
| `ai.state`<br>Agent State / Checkpoint | 执行状态及可用于恢复的持久化进度。 | P1 | 有正文：[概念](knowledge/ai/recoverable-runtime.md) |
| `ai.memory`<br>Short-term / Long-term Memory | 当前任务上下文和跨任务持久信息。 | P1 | 已收录 |
| `ai.memory-types`<br>Semantic / Episodic Memory | 可复用事实知识和情境经历记录。 | P1 | 已收录 |
| `ai.human`<br>Human-in-the-loop | 在特定决策或执行点引入人工参与。 | P1 | 已收录 |
| `ai.injection`<br>Prompt Injection / Tool Security | 外部内容诱导越权与工具访问控制。 | P1 | 已收录 |
| `ai.evals`<br>Evals / Golden Dataset | 系统化评测任务、数据、指标和判定。 | P1 | 已收录 |
| `ai.cost`<br>Tracing / Token Cost / Latency | 执行可观测性和费用、时延预算。 | P1 | 已收录 |
| `ai.training`<br>Fine-tuning / Distillation | 参数适配和用教师信号训练学生模型。 | P1 | 已收录 |
