---
search: false
---

# 阅读更新

按主题整理的推荐阅读与配套实践。每篇正文分别说明核查范围与仍待验证的部分；整体进度见[概念路线图](handbook/concept-roadmap.md)。

## 建议先读

本批可按 [BFF与前端适配](knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)、[复制与读副本](knowledge/distributed/consistency-and-replication.md)、[分布式锁与缓存租约](knowledge/distributed/leases-heartbeats-and-fencing.md)、[队列、发布订阅与事件流](knowledge/messaging/queues-pubsub-event-streams-and-retention.md)、[提示词与指令边界](knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)、[温度、采样与复现](knowledge/ai/temperature-sampling-and-reproducibility.md)、[MCP与能力协商](knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)、[微调、蒸馏与评估](knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md) 阅读。六篇新文配合两篇既有专题增补，补齐最后八组词条关联；313组现有词条都有正文入口，具体子概念、产品机制和真实验证继续保留缺口。

[Runtime](glossary/runtime.md#runtime.virtual-machine) 可按 [编译、解释与 JIT](knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md) → [异常传播](knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md) → [序列化](knowledge/runtime/serialization-representations-schemas-and-identity.md) → [跨语言调用](knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md) → [语言虚拟机](knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md) 阅读：分别核对执行策略、失败与清理、交换表示、二进制调用和宿主能力；五篇保持来源核查与纸面模型范围。

数据线可按 [CQRS](knowledge/architecture/cqrs-read-write-models-and-projection-lag.md) → [事件溯源](knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md) → [事件时间与窗口](knowledge/messaging/event-time-watermarks-windows-and-late-data.md) 阅读：分别核对写侧接纳与读侧可见、权威历史与重建、事件归窗与迟到修订；真实投影、事件存储与流处理集成仍待验证。

上一批可按 [HLC](knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md)、[CRDT](knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md)、[CDC](knowledge/database/cdc-snapshots-log-positions-and-replay.md) 阅读：先复算带回拨的因果时间线，再检查贡献合并、观察删除及约束反例，最后沿快照、源日志、目标状态和检查点核对连续性与恢复。三篇均为概念解释与纸面推演。

算法与身份可按 [分治与回溯](knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)、[字符串匹配](knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md)、[MFA](knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)、[跨服务委托](knowledge/security/service-delegation-token-exchange-and-audience.md) 阅读：先证明分解和排除分支的条件，再核对匹配单位、回退及返回位置，随后区分[认证](glossary/security.md#security.identity)因子和恢复保证，最后沿调用链检查主体、执行者、目标与权限。模型、示例和协议规则各有范围，未据此宣称实现或真实系统已经验证。

地址与存储可按 [IPv6 与邻居发现](knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md)、[权限模型与策略传播](knowledge/security/authorization-models-policy-distribution-and-revocation.md)、[Redis 数据结构](knowledge/cache-search/redis-data-types-operations-and-atomicity.md)、[对象存储与预签名访问](knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md) 阅读：先拆开地址配置与可达，再检查权限决定依赖的规则和事实，随后按操作语义选择结构，最后核对对象上传、发布与访问能力。例子为教学推演，各产品与实现的真实行为需另行验证。

写入与事件可按 [写穿与异步写回](knowledge/cache-search/write-through-write-behind-and-durability.md)、[UDP 与 QUIC](knowledge/networking/udp-quic-streams-and-delivery-boundaries.md)、[事件格式演进](knowledge/messaging/event-contracts-schema-evolution-and-replay.md) 阅读：先确定写入响应确认到了哪一层，再分清传输可靠性与业务提交，最后核对新旧事件的解析、事实含义与回放副作用。成功、兼容和恢复均需明确适用范围，例子为教学推演。

边缘与恢复可按 [CDN 与 WAF](knowledge/networking/cdn-edge-caches-and-waf-boundaries.md)、[缓存加载合并与惊群控制](knowledge/cache-search/cache-load-coalescing-and-stampedes.md)、[共识成员变更与分区恢复](knowledge/distributed/membership-changes-and-partition-recovery.md) 阅读：先确定边缘响应能否安全复用，再约束重复加载与实际回源，最后核对成员切换、旧执行者和故障恢复的权威边界。产品能力、共享范围和恢复流程均有前提，例子为教学推演。

安全与 API 可按 [mTLS 与服务身份](knowledge/security/mtls-service-identities-and-trust-boundaries.md)、[API 风格与网关](knowledge/api/api-styles-contracts-and-gateway-boundaries.md) 阅读：先确定每跳验证了谁、身份如何映射到权限，再比较资源、调用和查询契约，明确入口网关与执行服务分别承担什么。证书有效、请求通过入口或接口有类型，都不足以单独证明业务访问合法；例子均为纸面推演。

分布式取舍与标识可按 [CAP 与 PACELC](knowledge/distributed/cap-pacelc-and-operation-guarantees.md)、[分布式 ID](knowledge/distributed/distributed-identifiers-time-and-uniqueness.md) 阅读：先明确断联与正常复制时具体操作的保证和等待，再核对标识的唯一性范围、时间字段、节点身份与恢复状态。可排序编号不能代替因果、提交或[授权](glossary/security.md#security.identity)证据；例子均为纸面推演。

数据模型与分片可按 [数据模型与访问模式](knowledge/database/data-models-and-access-patterns.md)、[分区、分片与数据路由](knowledge/database/partitioning-sharding-and-data-routing.md) 阅读：先明确保存哪些事实、哪些约束和读写路径，再选择分区方式与[分片键](glossary/database.md#database.shard-key)，判断查询扇出、[热点](glossary/performance.md#performance.contention)及扩容接管的责任。模型和分布各有适用前提，纸面例子不代表数据库或集群已实测。

安全与 API 可按 [SQL 注入与参数化查询](knowledge/security/sql-injection-parameters-and-query-structure.md)、[密钥与凭证生命周期](knowledge/security/secrets-credentials-rotation-and-revocation.md) 阅读：先区分绑定值、查询结构和业务权限，再沿秘密分发、轮换与撤销判断哪些旧能力仍会被接受。示例为教学设计，具体驱动、数据库与凭据服务仍需集成验证。

系统与网络可按 [网络分层、IP 与路由](knowledge/networking/network-layers-ip-subnets-and-routing.md)、[NAT、代理与负载均衡](knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md) 阅读：先判断分组怎样到达[下一跳](glossary/networking.md#networking.routing)，再区分 [NAT](glossary/networking.md#networking.nat) 改写、代理连接和 [L4](glossary/networking.md#networking.load-balancer)/L7 决策。健康、保持、[TLS](glossary/networking.md#networking.tls) 与摘流分别限定范围；例子为纸面推演，真实网络与产品集成仍待验证。

上一批补充 [IPC 与共享所有权](knowledge/systems/ipc-channels-shared-memory-and-ownership.md)、[内存顺序与原子操作](knowledge/systems/memory-order-atomics-and-publication.md)、[XSS 与浏览器输出边界](knowledge/security/xss-contexts-sinks-and-browser-defenses.md)、[SSRF 与服务端请求边界](knowledge/security/ssrf-url-resolution-and-egress-boundaries.md)、[逻辑时钟与因果顺序](knowledge/distributed/logical-clocks-causality-and-concurrency.md)、[一致性哈希与再均衡](knowledge/distributed/consistent-hashing-placement-and-rebalancing.md)。可用[三条主线覆盖清单](handbook/concept-coverage.md)查看每个概念的阅读证据与剩余边界；有专题不表示组内概念或实测已全部完成。

系统与网络、安全与 API、分布式与数据新增六篇：[信号、取消与退出](knowledge/systems/signals-cancellation-and-shutdown.md)、[TCP 流量控制与拥塞控制](knowledge/networking/tcp-flow-control-and-congestion.md)、[密码存储与账号恢复](knowledge/security/password-storage-and-account-recovery.md)、[Webhook 签名与防重放](knowledge/api/webhook-signatures-replay-and-delivery.md)、[2PC、Saga 与补偿恢复](knowledge/distributed/two-phase-commit-sagas-and-recovery.md)、[索引重建与切换](knowledge/cache-search/index-rebuild-watermarks-and-cutover.md)。可按正在处理的资源、身份或数据问题选读；每篇分别说明保证、失败与核查范围，纸面示例不代表实际环境已验证。

开发与生产反馈可按 [测试稳定性与隔离](knowledge/engineering/flaky-tests-isolation-and-evidence.md) → [主干开发与功能开关](knowledge/engineering/trunk-based-development-and-feature-flags.md) → [事故响应与复盘](knowledge/reliability/incident-response-recovery-and-postmortems.md) → [IaC 与状态漂移](knowledge/devops/iac-state-drift-and-change-plans.md) 阅读，区分首轮失败、再次执行与修复、部署与开放、止损与恢复、声明与观测。资料已核查，时间线与状态例子为教学设计，没有新增真实操作。

工程维护可按 [技术债与重构](knowledge/architecture/technical-debt-refactoring-and-behavior.md) → [静态分析与告警](knowledge/engineering/static-analysis-rules-and-findings.md) → [代码评审与小步变更](knowledge/engineering/code-review-context-and-change-boundaries.md) → [依赖锁定与 SBOM](knowledge/engineering/dependency-resolution-lockfiles-and-sbom.md) 阅读，区分行为与结构、规则与代码事实、批准与最终证据，以及锁定、清单和可信来源。资料已核查，场景为教学设计，没有新增维护工具或项目实测。

算法进阶可按 [贪心选择与交换论证](knowledge/algorithms/greedy-choices-and-exchange-arguments.md) → [加权最短路与松弛](knowledge/algorithms/weighted-shortest-paths-and-relaxation.md) → [动态规划与状态设计](knowledge/algorithms/dynamic-programming-states-and-dependency-order.md) → [并查集与最小生成树](knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md) 阅读，把局部规则的证明、负权边界、状态顺序及连通目标区分开。MIT 资料已核查，图、区间和表格为纸面推演，没有新增算法或性能实测。

系统性能基础可按 [CPU 缓存与局部性](knowledge/systems/cpu-caches-locality-and-false-sharing.md) → [CPU 利用率与配额](knowledge/performance/cpu-time-utilization-load-and-quotas.md) → [Profiling 与火焰图](knowledge/performance/profiling-stacks-and-flame-graphs.md) → [基准测试与加速比](knowledge/performance/benchmarks-workloads-and-speedup.md) 阅读，区分缓存未命中与[缺页](glossary/systems.md#systems.virtual-memory)、[CPU 时间](glossary/performance.md#performance.cpu-metrics)与等待、采样权重与请求耗时，以及局部优化和整体收益。机制已核查，数值为纸面推演，没有新增性能实测。

向量与[混合检索](glossary/cache-search.md#cache-search.hybrid)可按 [向量索引与近似检索](knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md) → [混合召回与重排](knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md) 阅读，区分距离、近邻与业务相关性、候选窗口和重排输入。Faiss、[HNSW](glossary/cache-search.md#cache-search.ann)、pgvector 0.8.7 与融合/重排机制已核查；坐标、集合和 RRF 分数为纸面推演，没有新增索引、模型或效果实测。

存储与[全文检索](glossary/cache-search.md#cache-search.bm25)可读 [LSM、SSTable 与压缩合并](knowledge/database/lsm-sstables-and-compaction.md)和 [倒排索引与全文检索](knowledge/cache-search/inverted-indexes-analysis-and-relevance.md)，分别解释写入与后台合并、词项与文档查询。LevelDB/RocksDB 和信息检索机制已核查，PostgreSQL 对照限定 18 文档；序列、[倒排表](glossary/cache-search.md#cache-search.inverted)与字节比为纸面推演，没有新增存储或检索实测。

索引与缓存结构可按 [B/B+ 树与页索引](knowledge/algorithms/b-trees-bplus-trees-and-page-indexes.md) → [Trie 与前缀检索](knowledge/algorithms/tries-prefix-search-and-key-encoding.md) → [Bloom Filter](knowledge/cache-search/bloom-filters-membership-and-synchronization.md) → [LRU/LFU 与缓存淘汰](knowledge/cache-search/lru-lfu-and-capacity-eviction.md) 阅读，区分有序页、完整键、概率过滤和容量保留。范围、位图及访问序列是纸面推演，没有新增数据库、过滤器或缓存实测。

算法与结构可按 [线性结构](knowledge/algorithms/sequences-stacks-queues-and-deques.md) → [哈希表](knowledge/algorithms/hash-tables-collisions-and-key-contracts.md) → [排序与二分](knowledge/algorithms/sorting-binary-search-and-boundaries.md) → [树、堆与优先队列](knowledge/algorithms/trees-heaps-and-priority-queues.md) → [图遍历与依赖顺序](knowledge/algorithms/graphs-traversal-and-dependency-order.md) 阅读，把访问方式、维护规则与完整成本对应起来。片段参照 Python 3.13，[容器](glossary/devops.md#devops.containers)对照限定 Java 21；算例是纸面推演，没有新增算法或基准实测。

系统资源与 I/O 可按 [虚拟内存与缺页](knowledge/systems/virtual-memory-pages-and-faults.md) → [系统调用与权限边界](knowledge/systems/syscalls-privilege-and-return-contracts.md) → [文件描述符与打开文件描述](knowledge/systems/file-descriptors-and-open-file-descriptions.md) → [I/O 多路复用与就绪通知](knowledge/systems/io-multiplexing-readiness-and-event-loops.md) 阅读，区分地址映射、内核入口、资源引用和后续操作责任。Linux 机制已核查，地址、字节与事件算例为纸面推演，没有新增系统实验。

语言到加载可按 [模块系统与循环依赖](knowledge/runtime/modules-bindings-and-circular-dependencies.md) → [类型系统与运行时校验](knowledge/runtime/type-systems-and-runtime-validation.md) → [打包与代码分割](knowledge/frontend/bundling-tree-shaking-and-code-splitting.md) 阅读，区分绑定初始化、类型与实际数据、输出资源与执行成本。Node 对照限定 24.16.0 文档；代码与部署情形为纸面推演，没有新增编译或优化实测。

架构与工程质量可按 [领域模型、聚合与业务不变量](knowledge/architecture/domain-models-aggregates-and-invariants.md) → [契约测试与版本兼容](knowledge/engineering/contract-testing-and-compatibility.md) → [属性测试与状态模型](knowledge/engineering/property-testing-and-state-models.md) 阅读，分别说明规则归属、版本组合与反例搜索。订单规则、兼容矩阵和状态序列均为教学设计，没有新增建模[重构](glossary/architecture.md#architecture.debt)或测试工具实作。

交付与可靠性可按 [镜像、容器与资源隔离](knowledge/devops/images-containers-and-resource-isolation.md) → [声明式部署与健康探针](knowledge/devops/declarative-deployments-and-health-probes.md) → [故障域、冗余与恢复目标](knowledge/reliability/failure-domains-redundancy-and-recovery.md) 阅读，分别判断运行输入、流量就绪和业务恢复的证据。Kubernetes 机制限定 v1.36 文档，示例为纸面推演，没有新增容器、集群或容灾实测。

安全与 API 可按 [OAuth 与 OIDC](knowledge/security/oauth-oidc-and-pkce.md) → [同源、CORS 与 CSRF](knowledge/security/origins-cors-and-csrf.md) → [HTTP 条件请求](knowledge/api/conditional-requests-and-cache-validation.md) 阅读，区分登录交易、浏览器请求边界，以及[缓存验证](glossary/api.md#api.conditionals)与防止覆盖的不同前提。流程和请求片段为教学推演，没有新增身份提供方、跨站请求或条件更新实测。

浏览器状态可按 [闭包与词法绑定](knowledge/runtime/closures-and-lexical-bindings.md) → [响应式状态与更新](knowledge/frontend/reactive-state-and-update-scheduling.md) → [前端路由与缓存](knowledge/frontend/routing-state-and-cache-lifecycles.md) 阅读，区分回调持有的绑定、框架更新时机和导航中的多层缓存。片段与时序为教学推演，框架、[Service Worker](glossary/frontend.md#frontend.offline) 和整页恢复没有新增实测。

分布式协调与消息日志可按 [共识与 Quorum](knowledge/distributed/consensus-leaders-and-quorums.md) → [租约与 Fencing](knowledge/distributed/leases-heartbeats-and-fencing.md) → [分区、消费组与偏移](knowledge/messaging/partitions-consumer-groups-and-offsets.md) 阅读，分别理解法定集合、执行代次与消费完成边界。本批为来源核查和纸面推演，没有集群或 [Broker](glossary/messaging.md#messaging.roles) 实测。

理解 Agent 流程可按 [路由与交接契约](knowledge/ai/workflow-routing-and-handoff-contracts.md) → [编排状态与检查点](knowledge/ai/workflow-state-and-checkpoints.md) → [持久化预算与失败收敛](knowledge/ai/durable-budgets-and-failure-convergence.md) 阅读，分别判断下一步由谁推进、什么进度可恢复，以及交接和恢复怎样遵守同一预算。本批为来源核查与教学推演。

AI 记忆治理可按 [记忆写入与来源](knowledge/ai/memory-writing-and-provenance.md) → [记忆版本与失效](knowledge/ai/memory-versions-conflicts-and-expiry.md) → [记忆权限与删除](knowledge/ai/memory-access-revocation-and-deletion.md) 阅读，再用 [记忆治理实验](knowledge/ai/memory-governance-lab.md) 核对版本、期限、撤权、迟到回填与备份留存的区别。

AI 工具执行可按[工具调用契约](knowledge/ai/tool-calling-and-execution-contracts.md) → [结构化输出与校验](knowledge/ai/structured-outputs-and-validation.md) → [工具授权与不可信结果](knowledge/ai/tool-authorization-and-untrusted-results.md)阅读，再用[工具执行边界实验](knowledge/ai/tool-execution-boundaries-lab.md)核对拒绝、审批绑定、结果核实与局部恢复。

网络连接可按[DNS 缓存与地址选择](knowledge/networking/dns-caching-and-address-selection.md) → [TCP 与 TLS 连接状态](knowledge/networking/tcp-tls-and-connection-states.md) → [HTTP 复用与连接池](knowledge/networking/http-reuse-pools-and-timeouts.md)阅读，再用[连接生命周期实验](knowledge/networking/connection-lifecycle-lab.md)核对复用、等待、空闲关闭与[超时](glossary/api.md#api.retries)的局部证据。

容量与过载可按[背压与有界队列](knowledge/performance/backpressure-and-bounded-queues.md) → [限流、并发与配额](knowledge/api/rate-limits-concurrency-and-quotas.md) → [熔断、隔离与降级](knowledge/reliability/circuit-breakers-isolation-and-degradation.md)阅读，再用[过载控制实验](knowledge/performance/overload-control-lab.md)核对等待、拒绝和取消的实际边界。

数据恢复可按[WAL 与崩溃恢复](knowledge/database/wal-and-crash-recovery.md) → [备份与时间点恢复](knowledge/database/backups-and-point-in-time-recovery.md) → [数据库迁移兼容](knowledge/database/schema-migrations-and-compatibility.md)阅读；[命名恢复点实验](knowledge/database/backup-recovery-lab.md)提供基础备份加归档 [WAL](glossary/database.md#database.recovery-log) 的实际恢复证据。

[并发](glossary/systems.md#systems.concurrency)正确性可按[竞态与原子性](knowledge/systems/races-and-atomicity.md) → [锁与同步原语](knowledge/systems/locks-and-synchronization.md) → [死锁与失败恢复](knowledge/systems/deadlocks-and-recovery.md)阅读，再结合[库存并发实验](knowledge/database/inventory-concurrency-lab.md)核对局部状态、[不变量](glossary/systems.md#systems.atomicity)、等待与回滚。

理解 AI 应用可从[Token、上下文与记忆](knowledge/ai/tokens-context-and-memory.md) → [RAG 与依据](knowledge/ai/rag-retrieval-and-grounding.md) → [Evals 与失败分析](knowledge/ai/evals-and-failure-analysis.md)进入，再结合可恢复 [Runtime](glossary/runtime.md#runtime.virtual-machine) 理解工具执行与业务证据。

从页面到接口可读[渲染与 Hydration](knowledge/frontend/rendering-and-hydration.md)，区分内容显示和交互准备；再读[认证、会话与令牌](knowledge/security/authentication-sessions-and-tokens.md)与[HTTP 契约与分页](knowledge/api/contracts-and-pagination.md)，理解可信身份、调用约定和数据变化的边界。

排查资源与性能问题可读[索引与执行计划](knowledge/database/indexes-and-query-plans.md)、[可达性与垃圾回收](knowledge/runtime/reachability-and-garbage-collection.md)，再用[日志、指标与链路](knowledge/reliability/logs-metrics-and-traces.md)把总体异常与单次请求的证据联系起来。

理解系统边界可读[模块边界与依赖](knowledge/architecture/module-boundaries-and-dependencies.md)、[事务隔离与 MVCC](knowledge/database/isolation-and-mvcc.md)和[消息投递与确认](knowledge/messaging/delivery-acknowledgements-and-idempotency.md)；理解等待与用户体验可读[事件循环与微任务](knowledge/runtime/event-loop-and-microtasks.md) → [延迟、吞吐与排队](knowledge/performance/latency-throughput-and-queues.md) → [SLI、SLO 与错误预算](knowledge/reliability/slis-slos-and-error-budgets.md)。

补基础概念可先读：[进程、线程与协程](knowledge/systems/process-thread-coroutine.md) → [HTTPS 请求链路](knowledge/networking/https-request-lifecycle.md)；数据与性能方向可从[复杂度与结构选择](knowledge/algorithms/complexity-and-data-structures.md)、[缓存失效](knowledge/cache-search/cache-aside-and-invalidation.md)、[一致性与复制](knowledge/distributed/consistency-and-replication.md)进入。交付与质量方向可读[交付生命周期](knowledge/devops/build-deploy-rollback.md)和[测试层次](knowledge/engineering/test-scopes-and-doubles.md)。

1. 写了 async，其他请求仍卡住 → [同步、异步与阻塞](knowledge/runtime/async-and-blocking.md)。
2. 客户端超时，不知道订单是否创建 → [幂等性](knowledge/api/idempotency.md)。
3. 业务表已提交，消息却没发出去 → [Transactional Outbox](knowledge/messaging/transactional-outbox.md)。
4. Agent 重启后不知道工具是否成功 → [可恢复 Agent Runtime](knowledge/ai/recoverable-runtime.md)。
