# 学习路径

面向不同方向的技术工程人员，按当前问题和已有基础选择路线，每个单元以可解释或可验证的产出结束。当前四条路线围绕已有正文组织，后续随内容积累扩展；各路线显式区分现有正文和后续计划，不把术语覆盖当作课程已完成。

当前以[核心概念补全](../handbook/concept-roadmap.md)为先。各路线先完成定义、机制、取舍、边界和关联理解，以纸面推演与自检验收；现有实验作为可选配套资料，独立实作按后续阶段推进。

每个单元先提出工程问题，再通过知识索引找到关联概念，结合机制、取舍、实现与失败边界展开理解。用原理解释、设计判断、诊断记录或实验结果检验学习成果。

## A. 请求处理基础：解释一个请求

适合需要理解请求链路的软件开发、测试、运维及其他技术工程人员。

目标：说清请求如何到达服务、如何等待、如何写入，并能验证重复请求的行为。

1. [基础地图](../map.md)：选读系统、网络、[Runtime](../glossary/runtime.md#runtime.virtual-machine)、API、数据库、安全领域，用于定位概念与前置知识。
2. [进程、线程与协程](../knowledge/systems/process-thread-coroutine.md)：区分资源边界、[并发](../glossary/systems.md#systems.concurrency)与并行。
3. [虚拟内存与缺页](../knowledge/systems/virtual-memory-pages-and-faults.md) → [系统调用与权限边界](../knowledge/systems/syscalls-privilege-and-return-contracts.md) → [文件描述符与打开文件描述](../knowledge/systems/file-descriptors-and-open-file-descriptions.md) → [I/O 多路复用与就绪通知](../knowledge/systems/io-multiplexing-readiness-and-event-loops.md)：解释页面准备、权限转换、共享引用和就绪后的继续处理，区分短读写、EOF、编号复用及 [LT](../glossary/systems.md#systems.io-multiplexing)/ET。
4. [HTTPS 请求链路](../knowledge/networking/https-request-lifecycle.md) → [DNS 缓存与地址选择](../knowledge/networking/dns-caching-and-address-selection.md) → [TCP 与 TLS 状态](../knowledge/networking/tcp-tls-and-connection-states.md) → [HTTP 复用与连接池](../knowledge/networking/http-reuse-pools-and-timeouts.md)：区分名称、连接、安全与业务确认；用[连接生命周期实验](../knowledge/networking/connection-lifecycle-lab.md)核对池等待、正文归还和关闭后的状态。
5. [同步与阻塞](../knowledge/runtime/async-and-blocking.md) → [事件循环与微任务](../knowledge/runtime/event-loop-and-microtasks.md)：画出执行者与回调获得调度机会的时刻。
6. [HTTP 契约与分页](../knowledge/api/contracts-and-pagination.md) → [HTTP 条件请求](../knowledge/api/conditional-requests-and-cache-validation.md) → [幂等性](../knowledge/api/idempotency.md)：说明方法、错误、排序、[缓存验证](../glossary/api.md#api.conditionals)、并发保存与[重试](../glossary/api.md#api.retries)契约；[幂等性实验](../knowledge/api/idempotency-lab.md)作为配套证据阅读。
7. [事务隔离与 MVCC](../knowledge/database/isolation-and-mvcc.md) → [库存并发](../knowledge/database/concurrent-inventory.md)：写出快照与[业务不变量](../glossary/architecture.md#architecture.domain-model)，解释陈旧读取与条件更新；继续读[索引与执行计划](../knowledge/database/indexes-and-query-plans.md)与[查询计划实验](../knowledge/database/query-plans-lab.md)，区分可见性与访问成本。
8. [竞态与原子性](../knowledge/systems/races-and-atomicity.md) → [锁与同步原语](../knowledge/systems/locks-and-synchronization.md) → [死锁与失败恢复](../knowledge/systems/deadlocks-and-recovery.md)：解释共享状态、保护范围与等待；用[库存并发实验](../knowledge/database/inventory-concurrency-lab.md)核对业务不变量、回滚和错误分支。
9. [认证、会话与令牌](../knowledge/security/authentication-sessions-and-tokens.md) → [OAuth 与 OIDC](../knowledge/security/oauth-oidc-and-pkce.md) → [同源、CORS 与 CSRF](../knowledge/security/origins-cors-and-csrf.md) → [对象级授权](../knowledge/security/object-level-authorization.md)：分别解释主体与登录交易、浏览器[跨源](../glossary/security.md#security.origin)读写边界，以及当前动作和对象权限。

10. [模块边界与依赖](../knowledge/architecture/module-boundaries-and-dependencies.md) → [领域模型、聚合与业务不变量](../knowledge/architecture/domain-models-aggregates-and-invariants.md) → [测试层次与替身](../knowledge/engineering/test-scopes-and-doubles.md) → [契约测试与版本兼容](../knowledge/engineering/contract-testing-and-compatibility.md) → [属性测试与状态模型](../knowledge/engineering/property-testing-and-state-models.md)：为规则选择维护者与原子边界，区分跨组件版本验证和状态序列的反例搜索。

系统概念验收：能推演一次触页、共享偏移及 ET 遗留数据，说明[阻塞](../glossary/systems.md#systems.blocking)、调度和业务完成的不同边界。分配/驻留、[系统调用](../glossary/systems.md#systems.privilege)跟踪、描述符关闭与 LT/ET 公平处理对照仍待实测。

已有固定单行库存并发实测；后续实践：跨行[不变量](../glossary/systems.md#systems.atomicity)、分页实测、[OAuth](../glossary/security.md#security.oauth) 回调、CORS/[CSRF](../glossary/security.md#security.web-attacks) 与对象[授权](../glossary/security.md#security.identity) HTTP 集成、缓存验证及原子条件写入，以及带校验、权限、超时和[幂等](../glossary/api.md#api.idempotency)的本地 API。当前概念验收是解释链路、状态、登录交易、来源边界与业务不变量；完整服务实现属于后续阶段。

架构与质量配套实践仍待补：聚合并发持久化、消费者/提供方契约与混合版本矩阵、属性输入生成与收缩、状态机和并发历史对照。当前验收是写出不变量、模型前提、交互契约及测试不能外推的边界。

## B. 生产可靠性：把失败边界画出来

适合关注故障分析、交付质量和系统运行的软件开发、测试、运维、平台及架构人员。

前置：能实现 API 和基本[数据库事务](../glossary/database.md#database.isolation)。

1. [幂等性](../knowledge/api/idempotency.md)：区分超时和失败。
2. [超时与重试预算](../knowledge/reliability/timeouts-and-retry-budgets.md)：解释总预算、单次上限和停止条件。
3. [Cache-Aside 与失效](../knowledge/cache-search/cache-aside-and-invalidation.md)：排列旧值回填的并发时序。
4. [一致性与复制](../knowledge/distributed/consistency-and-replication.md) → [共识与 Quorum](../knowledge/distributed/consensus-leaders-and-quorums.md) → [租约与 Fencing](../knowledge/distributed/leases-heartbeats-and-fencing.md)：限定读写确认范围，说明多数相交为何仍需要协议，以及旧执行者怎样在业务资源处被拒绝。
5. [消息投递与确认](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) → [分区、消费组与偏移](../knowledge/messaging/partitions-consumer-groups-and-offsets.md) → [Outbox](../knowledge/messaging/transactional-outbox.md)：列出发布、分工、业务完成与恢复位置的窗口，推演并行消费不能越过未完成记录的提交边界。
6. [延迟、吞吐与排队](../knowledge/performance/latency-throughput-and-queues.md) → [慢 API 排查](../knowledge/performance/slow-api-investigation.md)：区分平均与尾部，为等待假设分别指定证据。
7. [SLI、SLO 与错误预算](../knowledge/reliability/slis-slos-and-error-budgets.md)：为一个用户操作定义好事件、分母、窗口和预算。
8. [日志、指标与链路](../knowledge/reliability/logs-metrics-and-traces.md)：标出采集边界、传播方式、采样缺口和聚合维度，连接总体异常与请求证据。
9. [WAL 与恢复](../knowledge/database/wal-and-crash-recovery.md) → [备份与时间点恢复](../knowledge/database/backups-and-point-in-time-recovery.md) → [迁移兼容](../knowledge/database/schema-migrations-and-compatibility.md)：区分提交耐久、历史恢复与应用回退；用[恢复实验](../knowledge/database/backup-recovery-lab.md)检查命名点之前保留、之后排除的数据。

10. [背压与有界队列](../knowledge/performance/backpressure-and-bounded-queues.md) → [限流、并发与配额](../knowledge/api/rate-limits-concurrency-and-quotas.md) → [熔断、隔离与降级](../knowledge/reliability/circuit-breakers-isolation-and-degradation.md)：分别写出等待上限、资源边界、拒绝语义和恢复条件；用[过载控制实验](../knowledge/performance/overload-control-lab.md)核对局部接纳和取消清理。

11. [构建、部署与回滚](../knowledge/devops/build-deploy-rollback.md) → [镜像、容器与资源隔离](../knowledge/devops/images-containers-and-resource-isolation.md) → [声明式部署与健康探针](../knowledge/devops/declarative-deployments-and-health-probes.md) → [故障域、冗余与恢复目标](../knowledge/reliability/failure-domains-redundancy-and-recovery.md)：区分制品、运行输入、就绪与业务恢复，写出终止预算、共同故障及 [RTO](../glossary/reliability.md#reliability.recovery)/RPO 的验收边界。

后续深入：自适应容量控制、分布式配额与真实[熔断](../glossary/reliability.md#reliability.isolation)恢复验证。已有本机命名恢复点实验，生产恢复目标仍需端到端演练。后续实践：[容器](../glossary/devops.md#devops.containers)资源与存储对照、滚动替换、探针误判与端点传播、[优雅终止](../glossary/reliability.md#reliability.probes)、跨[故障域](../glossary/reliability.md#reliability.fault-domains)恢复与回切；[共识](../glossary/distributed.md#distributed.consensus)分区、[租约](../glossary/distributed.md#distributed.fencing)与[资源隔离](../glossary/devops.md#devops.isolation)、消费重平衡及偏移事务集成；遥测采集管道与传播验证、跨代理[连接池](../glossary/api.md#api.pool)与真实负载压测、缓存故障与恢复演练。已有回环 [HTTP/1.1](../glossary/networking.md#networking.http-versions) 连接与池等待对照，[DNS](../glossary/networking.md#networking.dns)、[TLS](../glossary/networking.md#networking.tls) 和跨代理排空仍待验证。当前概念验收是能画出故障窗口、判断读取保证、定义服务与恢复目标并为排查假设指定证据。

### 系统性能基础单元

1. [CPU 缓存与局部性](../knowledge/systems/cpu-caches-locality-and-false-sharing.md)：从驻留页面继续区分[缓存行](../glossary/systems.md#systems.cpu-cache)、访问顺序、工作集与伪共享。
2. [CPU 利用率、负载与配额](../knowledge/performance/cpu-time-utilization-load-and-quotas.md)：对齐时间、范围和分母，区分运行、就绪等待、压力及组带宽。
3. [Profiling 与火焰图](../knowledge/performance/profiling-stacks-and-flame-graphs.md)：先确定事件和采集范围，再解释累计/自身成本、执行与等待。
4. [基准测试与加速比](../knowledge/performance/benchmarks-workloads-and-speedup.md)：固定业务契约与负载，推演[预热](../glossary/performance.md#performance.benchmark)、测量偏差及局部加速的整体上限。

当前验收为纸面访问序列、CPU 分母、栈样本和 Amdahl 算例；硬件缓存事件、调度/配额采集、真实程序剖析及工作负载基准继续待实测。

## C. AI 应用与 Agent：从上下文到可恢复执行

适合参与 AI 应用开发、数据与 AI 平台、工具集成、测试或安全设计的技术工程人员。

前置：理解请求与基本 JSON；进入工具执行部分前，先理解 API 幂等性和持久化状态。

1. [Token、上下文与记忆](../knowledge/ai/tokens-context-and-memory.md)：画出会话存储、当前输入与权威业务状态，规划一次请求的输入预算。
2. [RAG 与依据](../knowledge/ai/rag-retrieval-and-grounding.md)：区分入库、召回、[重排](../glossary/cache-search.md#cache-search.hybrid)、上下文组装与生成，核对版本、访问范围和引用支持；配套读[倒排索引与全文检索](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md)，区分词项、布尔条件、短语位置与评分；再读[向量索引](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md)与[混合召回和重排](../knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md)，区分近邻覆盖、候选融合和重排输入。
3. [Evals 与失败分析](../knowledge/ai/evals-and-failure-analysis.md)：为有依据、无依据、越权和工具未知场景设计样本，分别记录失败类型与评价口径。
4. [工具调用契约](../knowledge/ai/tool-calling-and-execution-contracts.md) → [结构化输出与校验](../knowledge/ai/structured-outputs-and-validation.md) → [工具授权与不可信结果](../knowledge/ai/tool-authorization-and-untrusted-results.md)：区分候选、许可、执行与确认；用[工具边界实验](../knowledge/ai/tool-execution-boundaries-lab.md)检查固定输入的局部分支，再用[幂等性](../knowledge/api/idempotency.md)解释稳定动作标识。
5. [记忆写入与来源](../knowledge/ai/memory-writing-and-provenance.md) → [记忆版本与失效](../knowledge/ai/memory-versions-conflicts-and-expiry.md) → [记忆权限与删除](../knowledge/ai/memory-access-revocation-and-deletion.md)：区分来源、版本、[可用性](../glossary/reliability.md#reliability.availability)与删除；结合 [记忆治理实验](../knowledge/ai/memory-governance-lab.md) 核对旧索引、旧缓存和迟到回填。
6. [路由与交接契约](../knowledge/ai/workflow-routing-and-handoff-contracts.md) → [编排状态与检查点](../knowledge/ai/workflow-state-and-checkpoints.md) → [持久化预算与失败收敛](../knowledge/ai/durable-budgets-and-failure-convergence.md)：用纸面时序说明路由、责任交接、恢复边界与共享额度，再用[可恢复 Runtime](../knowledge/ai/recoverable-runtime.md)提案梳理 unknown 和外部效果。
7. [Outbox](../knowledge/messaging/transactional-outbox.md)：理解本地提交与外部执行边界。
8. [对象级授权](../knowledge/security/object-level-authorization.md)：把检索和工具动作中的身份、租户、对象与权限分开检查。
9. [重试预算](../knowledge/reliability/timeouts-and-retry-budgets.md)：为工具重试设定总时间和停止条件。

当前概念验收：能区分近邻覆盖与业务相关性、融合窗口与重排输入、内容未进入上下文、检索未命中、证据被误用、评分器误判和外部结果未知；还能解释交接的接收/完成、检查点的恢复/重放，以及预算的预留/结算，为它们指定不同证据与修正方向。

已有固定候选工具边界的 24 类对照，以及记忆治理的 21 类本地场景；没有调用生成模型或远程工具。后续实践：Token 计数与上下文选择、[RAG](../glossary/ai.md#ai.rag) 召回[评测](../glossary/ai.md#ai.evals)、评分器校准、真实[进程](../glossary/systems.md#systems.execution-units)/SDK Checkpoint 故障注入、持久预算与交接派送、向量更新和备份恢复后的记忆治理，以及模型、身份服务与远程工具集成。

## D. 浏览器交互：解释一次点击为什么迟到

适合前端、测试和关注用户体验的技术工程人员。前置：JavaScript 函数、[Promise](../glossary/runtime.md#runtime.async) 与基本浏览器调试。

1. [渲染与 Hydration](../knowledge/frontend/rendering-and-hydration.md)：区分 HTML 生成、浏览器呈现与客户端接管，定位初始化前后的交互边界。
2. [同步、异步与阻塞](../knowledge/runtime/async-and-blocking.md)：画出调用、工作与完成通知，区分浏览器与 Node.js 宿主。
3. [事件循环与微任务](../knowledge/runtime/event-loop-and-microtasks.md)：推演任务与[微任务](../glossary/runtime.md#runtime.microtasks)的调用顺序，解释 await 不保证发生绘制。
4. [闭包与词法绑定](../knowledge/runtime/closures-and-lexical-bindings.md)：沿定义环境、共享绑定与读取时刻推演回调结果，区分普通变量和渲染快照。
5. [响应式状态与更新](../knowledge/frontend/reactive-state-and-update-scheduling.md) → [前端路由与缓存](../knowledge/frontend/routing-state-and-cache-lifecycles.md)：说明依赖、[队列](../glossary/algorithms.md#algorithms.queues)、[DOM](../glossary/frontend.md#frontend.render-tree) 提交和浏览器呈现，再按组件、查询、HTTP 与整页恢复区分导航状态。
6. [浏览器长任务](../knowledge/frontend/long-tasks-and-responsiveness.md)：结合[长任务实验](../knowledge/frontend/long-tasks-lab.md)的原始记录，分析任务、输入处理等待与 RAF 回调时机。
7. [可达性与垃圾回收](../knowledge/runtime/reachability-and-garbage-collection.md)：画出监听器、[闭包](../glossary/runtime.md#runtime.closure)与缓存的持有路径，区分分配压力与长期保留；Node.js 的内存字段不直接作为浏览器指标使用。

8. [模块系统与循环依赖](../knowledge/runtime/modules-bindings-and-circular-dependencies.md) → [类型系统与运行时校验](../knowledge/runtime/type-systems-and-runtime-validation.md) → [打包与代码分割](../knowledge/frontend/bundling-tree-shaking-and-code-splitting.md)：推演依赖环中的读取、外部数据的信任边界，以及按需资源的请求、求值和跨版本引用。

当前概念验收还包括解释共享绑定与提前计算、DOM 更新与绘制、实例复用与数据失效、模块链接与求值、[静态检查](../glossary/engineering.md#engineering.analysis)与[运行时校验](../glossary/runtime.md#runtime.type-system)，以及移除代码与延后加载。已有合成交互页面与 15 组时间线；后续计划：模块/顶层异步与类型校验对照、[Tree Shaking](../glossary/frontend.md#frontend.bundling)/分割/缓存版本实验，真实业务与设备的完整交互呈现测量、Worker、[响应式](../glossary/frontend.md#frontend.state)框架、路由与多层缓存集成。实践验收：保存一次交互[延迟](../glossary/performance.md#performance.latency-throughput)的原始记录，用证据判断问题在输入处理前、处理期间还是绘制阶段，并检查改动后业务结果相同。

## 遗留八组词条配套单元

前置：API契约、权限、复制/租约、消息确认及AI上下文与评价。按八个问题推进，两篇分布式专题复用并增补，不重复计为新文：

1. [BFF与前端适配](../knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)：分清客户端投影、领域规则及网关；复算260/110ms的理想条件。
2. [复制与读副本](../knowledge/distributed/consistency-and-replication.md)：区分确认、接收、写盘、回放、新/旧快照及切主恢复。
3. [分布式锁与缓存租约](../knowledge/distributed/leases-heartbeats-and-fencing.md)：区分随机持有标识、严格递增代次与回填资格，解释41/42生效点。
4. [队列、发布订阅与事件流](../knowledge/messaging/queues-pubsub-event-streams-and-retention.md)：按工作池、订阅和历史位置判断八次逻辑处理及103的含义。
5. [提示词与指令边界](../knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)：区分角色、资料、例子与实际权限；核对接口中的指令继承范围。
6. [温度、采样与复现](../knowledge/ai/temperature-sampling-and-reproducibility.md)：复算T=0.5与top-p=0.7，区分选择分布、事实和复现。
7. [MCP与能力协商](../knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)：沿宿主/客户端/服务器理解能力、原语、错误与业务完成。
8. [微调、蒸馏与评估](../knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md)：区分参数适配、软目标和教师文本，解释独立测试及4个百分点。

现有313组词条均有阅读入口；验收继续按具体机制、证据和未覆盖范围判断。所有新例子是纸面推演，真实[BFF](../glossary/frontend.md#frontend.bff)/复制/锁/[Broker](../glossary/messaging.md#messaging.roles)/模型/[MCP](../glossary/ai.md#ai.mcp)和训练验证分别积累。

## 工程反馈、验证组合与可靠性证据配套单元

前置：测试范围、API契约、[服务目标](../glossary/reliability.md#reliability.slos)与故障域。按八个问题推进：

1. [TDD与BDD](../knowledge/engineering/tdd-bdd-examples-and-feedback-loops.md)：说明红绿[重构](../glossary/architecture.md#architecture.debt)、跨角色例子及测试到达目标行为的条件。
2. [测试金字塔与证据组合](../knowledge/engineering/test-pyramids-risk-portfolios-and-coverage.md)：按风险选边界，用x=0解释分支覆盖与缺陷发现的区别。
3. [设计文档与决策记录](../knowledge/engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md)：区分设计、讨论与决定历史，连接实现及验证状态。
4. [规格驱动与验收追溯](../knowledge/engineering/specifications-contracts-traceability-and-acceptance.md)：把目标、规格、实现与证据双向关联，处理不确定付款及版本变化。
5. [黄金路径与开发者体验](../knowledge/engineering/golden-paths-developer-experience-and-platform-feedback.md)：覆盖创建、运行、升级及退出，复算75%与12.5%的分母。
6. [RED与USE](../knowledge/reliability/red-use-service-signals-and-resource-evidence.md)：区分接纳/完成/积压、错误速率/比例与可聚合分布。
7. [可用性与可靠性](../knowledge/reliability/availability-reliability-and-observation-windows.md)：区分时间/请求比例、连续存活与恢复，声明窗口及故障语义。
8. [混沌工程与受控故障](../knowledge/reliability/chaos-engineering-hypotheses-stop-conditions-and-recovery.md)：区分稳态假设、作用确认、停止条件与业务恢复，保留实验范围。

验收先解释边界、反例和统计口径；真实开发反馈、需求验收、平台升级、遥测/告警、受控故障及业务恢复分别留证，不把来源核查当作演练结果。

## 安全/API、性能与交付遗漏配套单元

前置：对象权限、HTTP契约、延迟[排队](../glossary/performance.md#performance.queueing)与[声明式部署](../glossary/devops.md#devops.k8s)。按九个问题推进：

1. [信任边界与威胁建模](../knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md)：画资产、入口与信任边界，把[最小权限](../glossary/security.md#security.trust)和威胁路径连到验证证据。
2. [资源模型与输入边界](../knowledge/api/resource-models-input-validation-and-write-boundaries.md)：区分资源、表示、动作及逐字段写入权限，检查并发保存条件。
3. [优雅关闭与请求排空](../knowledge/api/graceful-shutdown-draining-and-inflight-outcomes.md)：区分停止接纳、连接排空及业务结果；复算30秒总预算。
4. [批处理与流水线](../knowledge/performance/batching-pipelining-and-amortized-waiting.md)：复算18/6ms与7.5ms等待，解释事务、依赖、部分错误和有界窗口。
5. [热点与资源竞争](../knowledge/performance/hotspots-contention-and-serialized-service.md)：复算450>300与500/s上界，用局部分布而非平均值定位竞争。
6. [容量规划与自动扩缩容](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md)：复算280/4/5与[HPA](../glossary/devops.md#devops.autoscaling)原始15，说明反馈延迟和故障余量。
7. [集群入口与服务发现](../knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md)：串起DNS、Service、端点和入口，分别检查绑定与跨空间引用许可。
8. [云网络与访问边界](../knowledge/devops/cloud-networks-subnets-routes-and-security-groups.md)：区分路由、[NAT](../glossary/networking.md#networking.nat)、有状态/无状态过滤及业务身份，限定AWS IPv4例子。
9. [可信制品与渐进发布](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md)：把摘要、身份及构建期望连到同一产物，再判断暴露、观察和回退。

验收先解释机制、前提和失败边界；实际认证/写入、关闭/入口传播、云网络、负载与扩缩、制品验证和发布恢复分别保留集成证据，纸面数值不作为配置建议。

## 架构边界、抽象与演进配套单元

前置：模块边界、聚合不变量与基本事务。按五个问题推进：

1. [模块化单体与微服务](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)：分别画出模型、模块、数据与部署边界；推演预留成功但响应丢失。
2. [设计原则与抽象成本](../knowledge/architecture/design-principles-contracts-and-abstraction-costs.md)：按变化来源和行为契约判断拆分，区分同一知识与偶然相似。
3. [设计模式与协作契约](../knowledge/architecture/design-patterns-collaboration-and-semantic-boundaries.md)：说明四类协作的意图，复算费用/折扣顺序并判断通知恢复责任。
4. [渐进替换与写入归属](../knowledge/architecture/strangler-fig-migration-write-authority-and-rollback.md)：标出快照/日志、旧写隔离、权威移交与103之后的回退条件。
5. [质量属性与架构决策](../knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md)：写出质量场景、风险与取舍，区分串行预算、分布统计和ADR状态。

验收以机制解释和纸面反例为主；实际服务拆分、模式实现、写入移交、维护收益与质量目标需独立验证，不把ADR接受状态当作实现已通过。

## 前端身份、实时恢复与新鲜度配套单元

前置：渲染、响应式状态、路由缓存和打包。按问题选读，以下每步以解释机制和反例为验收：

1. [组件协调与 key](../knowledge/frontend/reconciliation-keys-and-component-identity.md)：在同一父级、类型和局部状态前提下，推演索引与稳定 ID 的对应；分开身份重置与外部失效。
2. [WebSocket/SSE 与断线补读](../knowledge/frontend/websocket-sse-reconnection-and-replay.md)：画出连接、接收、连续处理与恢复位置，解释历史缺口、去重和身份变化。
3. [Core Web Vitals 与体验证据](../knowledge/frontend/core-web-vitals-field-data-and-diagnostic-boundaries.md)：复算 [LCP](../glossary/frontend.md#frontend.web-vitals)/交互/CLS 样例，说明单次结果、p75 用户分布及业务完成的区别。
4. [Service Worker 与离线更新](../knowledge/frontend/service-workers-offline-caches-and-update-lifecycles.md)：区分安装、等待、激活与控制，设计旧分块保留、身份缓存与离线待同步状态。
5. [增量再生成与页面缓存](../knowledge/frontend/incremental-regeneration-revalidation-and-freshness.md)：画出过期请求、后台生成、成功替换与失败保留，分别判断多实例和客户端缓存。

以上是来源核查与纸面推演，实际框架、浏览器/代理、真实用户指标、Worker 和多实例缓存的集成验证继续积累。

## 网络选路、大小、拥塞与接入配套单元

前置：[网络分层](../glossary/networking.md#networking.network-model)、[TCP](../glossary/networking.md#networking.transport) 窗口及 IPv6 [邻居发现](../glossary/networking.md#networking.neighbor-discovery)。按四个问题推进：

1. [策略与动态路由](../knowledge/networking/policy-routing-control-planes-and-convergence.md)：给定规则和来源，推演所查表、下一跳及异步切换；分别验收新旧连接。
2. [路径 MTU 与隧道](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md)：逐层计算封装预算，区分有效确认、大小反馈与待验证的黑洞假设。
3. [拥塞算法与队列管理](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md)：复算 [BDP](../glossary/networking.md#networking.queue-management) 和队列等待，区分窗口、[发送节奏](../glossary/networking.md#networking.congestion-algorithms)、调度与拥塞通知。
4. [IPv6 源地址、隐私与接入防护](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md)：按明确前提选择源地址，画出弃用/失效，区分通告权限、源约束与应用授权。

验收为纸面解释和反例；实际路由/隧道/算法/接入设备的配置与故障证据继续积累。

## 系统调度、对象寿命与并发进度配套单元

1. [上下文切换与调度等待](../knowledge/systems/context-switches-run-queues-and-scheduling-delay.md)：沿唤醒、就绪和真正运行拆解时间，区分权限转换、任务切换与迁移。
2. [栈堆与内存布局](../knowledge/systems/process-memory-layout-stacks-heaps-and-lifetimes.md)：分别画虚拟映射、分配器块与对象寿命，解释地址仍在和 free 后 RSS。
3. [无锁算法与进度保证](../knowledge/systems/lock-free-algorithms-linearization-and-progress.md)：先列顺序规格与生效点，再说明整体完成和单次自身步骤各自证明什么。
4. [ABA 与安全内存回收](../knowledge/systems/safe-memory-reclamation-aba-hazards-and-epochs.md)：沿保护、验证、移除、退役和回收判断旧读者与对象复用条件。

概念验收：复算 12 毫秒的三类耗时、四线程的虚拟/驻留栈模型、竞争计数时序和宽限期旧读者时间线。实际调度采集、分配器/碎片、无锁并发历史及 hazard/epoch/[RCU](../glossary/systems.md#systems.memory-reclamation) 停滞与退出仍待验证。

## Runtime 执行与跨边界语义配套单元

1. [编译、解释与 JIT](../knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md)：区分表示、时机与优化，复算预热成本并解释守卫与退优化。
2. [异常传播](../knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md)：沿同步调用、Promise 完成与取消分别追踪失败，明确清理和外部状态责任。
3. [序列化](../knowledge/runtime/serialization-representations-schemas-and-identity.md)：追踪大整数、字段存在性、共享引用和字节身份在交换中保留什么。
4. [跨语言调用](../knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md)：为输入、输出和回调写出 ABI、寿命、线程及错误契约，检查 Wasm 偏移范围。
5. [语言虚拟机](../knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md)：区分装载、验证、实例与宿主，解释可移植和隔离的不同条件。

概念验收：解释 addOne 的类型变化、finally 覆盖、9007199254740993 的表示、65536 字节内存边界与 3+4 的抽象栈。[编译器](../glossary/runtime.md#runtime.compilation)跟踪、故障注入、混合编码器、原生回调与虚拟机宿主权限仍需实际验证。

## 分布式时间、合并与变更流配套单元

1. [HLC](../knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md)：物理分量与逻辑计数、单向因果、偏差/恢复及安全读取边界。
2. [CRDT](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md)：状态/操作传播条件、贡献计数、观察删除、历史清理与业务不变量。
3. [CDC](../knowledge/database/cdc-snapshots-log-positions-and-replay.md)：配对快照、源端事务/位点、删除载荷、重复处理及保留恢复。

## 读写投影、事件历史与流处理时间配套单元

1. [CQRS](../knowledge/architecture/cqrs-read-write-models-and-projection-lag.md)：区分命令接纳、查询可见、投影版本与读己之写，写出一次不暴露半成品的重建切换。
2. [事件溯源](../knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md)：按预期流版本推演并发追加，区分快照、聚合重建、查询投影和外部副作用。
3. [事件时间与窗口](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md)：为准时、迟到和过期记录计算窗口结果，说明水位、触发、累积模式与下游覆盖协议。

当前验收为版本 40/42、账户流版本 3/4 和五分钟窗口的纸面推演；真实投影补洞/切换、事件存储并发与历史升级、流处理状态恢复和目标修订仍待集成验证。

分别回答时间戳证明了哪条边、状态合并保留了哪些更新、快照与日志覆盖了哪个来源边界。读数更大、各副本相同和捕获器已接收，各自还缺少哪些提交、约束或目标完成证据？

## 算法推理与身份委托配套单元

1. [分治与回溯](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md)：子问题契约、递归分层、选择撤销、可行性剪枝与最优上下界。
2. [字符串匹配](../knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md)：精确子串契约、前缀函数/失败链接、线性计数及编码转换边界。
3. [MFA](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)：因子与UP/UV、OTP挑战、注册恢复、升阶与会话保证。
4. [跨服务委托](../knowledge/security/service-delegation-token-exchange-and-audience.md)：主体/执行者/受众、令牌交换、权限收窄与生命周期。

分别复算一棵搜索树、一次失配回退、一段认证状态和一跳权限请求：排除了什么候选，采用哪种位置单位，证明了哪个因子，又由谁在何处接受权限？不要把少走分支当作完整性证据，也不要把新凭据当成新的用户认证或更大权限。

## 地址、权限与存储配套单元

1. [IPv6 与邻居发现](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md)：地址范围与 zone、SLAAC/DAD、A/L/默认路由分工及邻居寿命。
2. [权限模型与策略传播](../knowledge/security/authorization-models-policy-distribution-and-revocation.md)：[RBAC](../glossary/security.md#security.access-control)/ABAC/[ReBAC](../glossary/security.md#security.rebac)、判定与执行、规则/事实传播及撤销窗口。
3. [Redis 数据结构](../knowledge/cache-search/redis-data-types-operations-and-atomicity.md)：操作语义、读写成本、原子执行、过期/槽位与业务恢复。
4. [对象存储与预签名访问](../knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md)：键/版本/校验、单键与发布、分段完成、签名能力与撤销。

画出“获得配置—取得事实—执行操作—发布结果”的不同阶段：有地址还缺哪条路径，规则改动何时影响执行，命令确认与上传完成各证明什么？先说明每项计时与版本的范围，再判断迟到结果、撤销、恢复和在途工作的责任。

## 写入、传输与事件演进配套单元

1. [写穿与异步写回](../knowledge/cache-search/write-through-write-behind-and-durability.md)：写入接纳/后端提交、状态合并、版本删除与有界写回恢复。
2. [UDP 与 QUIC](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md)：数据报/流边界、丢失与资源控制、握手重放、地址与业务身份。
3. [事件格式演进](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)：事件身份、读写版本矩阵、历史适配与回放副作用边界。

自检时沿待写项、传输字节和事件身份分别画时间线：成功前确认了什么，超时后哪些结果未知，旧版本与恢复路径还会接受哪些动作？来源规则、教学模型和实际产品证据分别判断，不用网络确认或格式可解析代替业务提交。

## 边缘、缓存与集群恢复配套单元

1. [CDN 与 WAF](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md)：缓存键与身份范围、边缘失效、[WAF](../glossary/networking.md#networking.cdn-waf) 可见性及受控回源。
2. [缓存加载合并与惊群控制](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md)：同键共享加载、等待/取消、跨实例与总容量、迟到回填。
3. [共识成员变更与分区恢复](../knowledge/distributed/membership-changes-and-partition-recovery.md)：配置交叠、追赶/提升、分区重连与永久失多数恢复。

自检时先标出复用身份和生效范围，再画出失效、共享工作或成员配置的时间线。缓存命中、加载者持有锁、自称领导者和恢复出快照，各自还缺哪些接受与提交证据？真实产品配置、容量和恢复结果需另行验证。

## 服务身份与 API 入口配套单元

1. [mTLS 与服务身份](../knowledge/security/mtls-service-identities-and-trust-boundaries.md)：分别核对证书链、预期身份、私钥持有和权限映射；画清 TLS 终止后的连接对端与可信转发边界。
2. [API 风格与网关](../knowledge/api/api-styles-contracts-and-gateway-boundaries.md)：按同一业务的资源、命令和读取需求比较契约，核对认证接入、路由、额度、预算、重试与业务执行的责任。

自检时画出身份验证路径和业务操作路径：入口确认与最终提交各有什么证据，旧证书、在途请求和未知结果如何处理。[mTLS](../glossary/security.md#security.mtls) 不自动赋予对象权限，网关也不自动维护业务幂等或数据库不变量。

## 分布式取舍与标识配套单元

1. [CAP 与 PACELC](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md)：按一次读写历史区分线性一致、形式可用性与实际期限，说明断联时哪些请求不能继续正常完成，正常复制又需等待什么。
2. [分布式 ID](../knowledge/distributed/distributed-identifiers-time-and-uniqueness.md)：核对编号的唯一范围、时间分辨率、节点身份和序列/随机状态，区分局部排序、因果、提交顺序与业务幂等。

自检时分别画出断联读写历史和生成器状态。不能从多数公式、可排序 ID、非空响应或一次成功生成推导完整系统保证；真实协议、时钟和恢复验证仍需另行积累。

## 数据模型与分片配套单元

1. [数据模型与访问模式](../knowledge/database/data-models-and-access-patterns.md)：区分逻辑事实、完整性约束、访问路径与物理分布；用当前客户资料和订单时点快照判断复制字段的更新责任。
2. [分区、分片与数据路由](../knowledge/database/partitioning-sharding-and-data-routing.md)：从[分片键](../glossary/database.md#database.shard-key)和查询谓词推演定向范围、扇出与[热点](../glossary/performance.md#performance.contention)，核对全局约束和迁移期间的写入归属。

自检时分别画出事实依赖和一次查询经过的数据位置，说明哪些保证由模型、索引、事务或路由协议提供。规范化不保证最优性能，新增分片或改映射也不证明热点与搬迁已经解决。

## 查询构造与凭证生命周期配套单元

1. [SQL 注入与参数化查询](../knowledge/security/sql-injection-parameters-and-query-structure.md)：从可信身份与输入边界出发，解释绑定值、允许结构片段、标识符引用、二次拼接与对象授权的独立责任。
2. [密钥与凭证生命周期](../knowledge/security/secrets-credentials-rotation-and-revocation.md)：区分秘密与公开材料，追踪新旧版本在哪些验证方被接受，解释[动态凭据](../glossary/security.md#security.dynamic-credentials)、加密密钥、在用会话与恢复副本的撤销边界。

自检时画出查询的结构/值来源和凭据的签发/使用/撤销路径；参数安全不证明对象权限，写入新版本也不证明旧能力停止。双向认证与身份映射的概念已接入前文配套单元；所选身份协议和实际服务联动仍需集成验证。

## 网络转发与入口配套单元

1. [网络分层、IP 与路由](../knowledge/networking/network-layers-ip-subnets-and-routing.md)：区分地址、前缀、[下一跳](../glossary/networking.md#networking.routing)和逐跳封装；解释最长前缀的前提及返回路径为何需要独立成立。
2. [NAT、代理与负载均衡](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md)：沿元组、连接和 TLS 终止位置比较 [NAT](../glossary/networking.md#networking.nat)、代理及 [L4](../glossary/networking.md#networking.load-balancer)/L7 分流，解释健康、保持与摘流的有限保证。

自检时画出一条去程和回程，逐段标注可见地址、谁终止连接、谁能读请求，以及未完成工作由谁负责。纸面正确不代表真实路由、NAT 状态、转发头或故障切流已验证。

## 系统共享、安全边界与分布式模型配套单元

1. [IPC 与共享所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md)：字节/消息边界、共享内存、同步、[背压](../glossary/performance.md#performance.queueing)与所有权。
2. [内存顺序与原子操作](../knowledge/systems/memory-order-atomics-and-publication.md)：语言模型、读写顺序、发布条件与 [CAS](../glossary/systems.md#systems.synchronization) 进度边界。
3. [XSS 与浏览器输出边界](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md)：上下文、危险汇、[净化](../glossary/api.md#api.validation)、CSP 与 [Trusted Types](../glossary/security.md#security.trusted-types)。
4. [SSRF 与服务端请求边界](../knowledge/security/ssrf-url-resolution-and-egress-boundaries.md)：解析、DNS、实际连接、重定向及出口控制。
5. [逻辑时钟与因果顺序](../knowledge/distributed/logical-clocks-causality-and-concurrency.md)：happened-before、Lamport、向量比较及并发。
6. [一致性哈希与再均衡](../knowledge/distributed/consistent-hashing-placement-and-rebalancing.md)：环、虚拟节点、成员视图、复制放置与迁移责任。

先看进程和线程怎样交换可用状态，再看浏览器或服务端请求跨越什么信任边界，最后区分因果、放置和全局决策。当前是概念与纸面推演；逐项余项见[覆盖清单](../handbook/concept-coverage.md)。

## 系统网络、安全 API 与分布式数据配套单元

1. [信号、取消与退出](../knowledge/systems/signals-cancellation-and-shutdown.md)：递送、掩码、待决、处理限制与正常退出责任。
2. [TCP 流量控制与拥塞控制](../knowledge/networking/tcp-flow-control-and-congestion.md)：接收窗口、拥塞窗口、在途数据与重传证据。
3. [密码存储与账号恢复](../knowledge/security/password-storage-and-account-recovery.md)：口令派生、成本迁移、恢复证明和[会话撤销](../glossary/security.md#security.revocation)。
4. [Webhook 签名与防重放](../knowledge/api/webhook-signatures-replay-and-delivery.md)：签名覆盖、原始字节、时间窗口、重放与持久接纳。
5. [2PC、Saga 与补偿恢复](../knowledge/distributed/two-phase-commit-sagas-and-recovery.md)：准备与决议、恢复阻塞、本地提交和补偿责任。
6. [索引重建与切换](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md)：快照切点、增量水位、删除版本、发布与回退。

三组可以分别阅读：先核对资源与传输，再核对身份与重复执行，最后核对跨边界状态与数据切换。当前是概念与纸面推演；信号/抓包、身份/回调、协调事务及[索引切换](../glossary/cache-search.md#cache-search.index-cutover)的集成实验仍需另行验证。

## 开发与生产反馈配套单元

1. [测试稳定性与隔离](../knowledge/engineering/flaky-tests-isolation-and-evidence.md)：沿共享状态追查顺序和并行干扰，保留首轮失败、重试与修复的不同证据。
2. [主干开发与功能开关](../knowledge/engineering/trunk-based-development-and-feature-flags.md)：连接小批集成、反馈预算、配置默认值、数据兼容和开关清理。
3. [事故响应与复盘](../knowledge/reliability/incident-response-recovery-and-postmortems.md)：组织止损、交接与业务验收，用时间线区分检测、恢复和响应结束。
4. [IaC 与状态漂移](../knowledge/devops/iac-state-drift-and-change-plans.md)：比较配置、记录和观测，判断漂移意图、变更归属、状态锁和敏感信息边界。

当前验收是能够解释纸面场景的责任与证据，不包含测试套件治理、功能放量、事故演练或云资源变更。

## 工程维护配套单元

1. [技术债与重构](../knowledge/architecture/technical-debt-refactoring-and-behavior.md)：固定可观察行为，区分现状记录与正确规格，再说明小步替换和收益依据。
2. [静态分析与告警](../knowledge/engineering/static-analysis-rules-and-findings.md)：先核对源码、语言、规则和实际覆盖，再判断误报、抑制、风险接受与自动修复。
3. [代码评审与小步变更](../knowledge/engineering/code-review-context-and-change-boundaries.md)：准备完整上下文，说明评审分工、阻断原因和证据对应的最终版本。
4. [依赖锁定与 SBOM](../knowledge/engineering/dependency-resolution-lockfiles-and-sbom.md)：从声明、解析、安装到制品，核对组件身份、[兼容性](../glossary/api.md#api.versioning)、清单和来源证明。

当前验收是解释行为差异、扫描范围、评审依据及依赖图；真实项目[重构](../glossary/architecture.md#architecture.debt)、工具接入、组件升级和制品/来源验证继续待实作。

## 公共基础：按操作与不变量选择算法

适合所有路线配套阅读。先读[复杂度与结构选择](../knowledge/algorithms/complexity-and-data-structures.md)，再按问题推进：

1. [线性结构与端点操作](../knowledge/algorithms/sequences-stacks-queues-and-deques.md)：区分顺序接口、存储表示、定位与修改，以及容量满时的业务责任。
2. [哈希表与键契约](../knowledge/algorithms/hash-tables-collisions-and-key-contracts.md)：解释[碰撞](../glossary/algorithms.md#algorithms.hash-table)、相等、负载和扩容，限定预期与摊还成本。
3. [排序与二分查找](../knowledge/algorithms/sorting-binary-search-and-boundaries.md)：写出排序规则、区间不变量、存在性及重复范围，计入有序维护成本。
4. [树、堆与优先队列](../knowledge/algorithms/trees-heaps-and-priority-queues.md)：比较按键、有序与极值查询，推演堆顶、[Top-K](../glossary/algorithms.md#algorithms.trees)、并列和优先级更新。
5. [图遍历与依赖顺序](../knowledge/algorithms/graphs-traversal-and-dependency-order.md)：区分可达、最少边数、环与拓扑顺序，再说明真实前置完成由谁确认。
6. [B/B+ 树与页索引](../knowledge/algorithms/b-trees-bplus-trees-and-page-indexes.md) → [Trie 与前缀检索](../knowledge/algorithms/tries-prefix-search-and-key-encoding.md) → [Bloom Filter](../knowledge/cache-search/bloom-filters-membership-and-synchronization.md) → [LRU/LFU 与缓存淘汰](../knowledge/cache-search/lru-lfu-and-capacity-eviction.md)：比较有序页访问、共享前缀、概率成员判断与保留策略，明确同步、删除和数据有效性的不同责任。

7. [LSM、SSTable 与压缩合并](../knowledge/database/lsm-sstables-and-compaction.md) → [倒排索引与全文检索](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md)：区分存储写入与后台整理、词项到文档的映射；推演快照、删除、求交、短语和[词频](../glossary/cache-search.md#cache-search.bm25)，注明放大口径与分析配置。

8. [向量索引与近似检索](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md) → [混合召回与重排](../knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md)：先固定空间、距离、过滤与精确基线，再推演 RRF 与候选截断，区分近邻召回、业务相关性和来源支持。

9. [贪心选择与交换论证](../knowledge/algorithms/greedy-choices-and-exchange-arguments.md)：固定目标与区间边界，推演安全交换、局部反例及加权/在线变化。
10. [加权最短路与松弛](../knowledge/algorithms/weighted-shortest-paths-and-relaxation.md)：区分首次发现与确认、非负权与负环影响，并把优先级更新计入实现成本。
11. [动态规划与状态设计](../knowledge/algorithms/dynamic-programming-states-and-dependency-order.md)：定义子问题、初始化与依赖，推演 [0/1 背包](../glossary/algorithms.md#algorithms.dynamic-programming)、一维顺序及伪多项式边界。
12. [并查集与最小生成树](../knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md)：区分分组代表与图边，通过无环与[割性质](../glossary/algorithms.md#algorithms.mst)解释 Kruskal，并与最短路径目标比较。

当前验收为解释模型和纸面反例；容器、碰撞、二分性质、堆更新、图算法、页分裂、前缀更新、Bloom 重建、缓存访问策略、[LSM](../glossary/database.md#database.lsm) 合并、全文/[向量索引](../glossary/cache-search.md#cache-search.vectors)、过滤及融合重排的正确性和性能对照仍待实作。加权路径、背包、集合合并与生成树的实现/穷举对照仍待补；[分治](../glossary/algorithms.md#algorithms.divide-conquer)、回溯剪枝、字符串匹配与其他概率结构继续按路线图深入，不因基础文章有链接就视为全部完成。

## 学习记录

跨路线配套阅读：[复杂度与数据结构](../knowledge/algorithms/complexity-and-data-structures.md)帮助解释工作量与空间；[模块边界与依赖](../knowledge/architecture/module-boundaries-and-dependencies.md)帮助判断变更影响；[构建、部署与回滚](../knowledge/devops/build-deploy-rollback.md)和[测试层次与替身](../knowledge/engineering/test-scopes-and-doubles.md)帮助界定变更与证据范围。

给每个单元留下一条证据：代码、复现步骤、解释录音、设计评审或[事故复盘](../glossary/reliability.md#reliability.incidents)。个人掌握等级记录于本地 personal 目录；公开知识库记录可复用的解释与验证。

记录时写明起始问题、关键机制、考虑过的方案、失败假设、实际观察与适用边界，再标出下一步需要验证的部分。
