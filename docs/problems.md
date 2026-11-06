# 从问题进入

把实际工程问题作为学习入口，领域与术语清单作为知识索引。建议按“现象与约束 → 关联概念 → 机制与取舍 → 实现 → 故障与验证”推进，留下原理解释、设计依据、诊断证据或验证结果。

下表只链接已经存在的正文。后续主题可记录在路线图中，写完后再加入这里。

| 你遇到的问题 | 先读 | 再验证或深入 |
| --- | --- | --- |
| 前端合并一次请求，为什么仍需权限、状态和业务边界？ | [BFF与前端适配](knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md) | 分清客户端投影、领域规则及网关；复算260/110ms的理想条件。 |
| [只读副本](glossary/database.md#database.replication)收到日志，为什么查询仍可能看到旧值？ | [复制与读副本](knowledge/distributed/consistency-and-replication.md) | 区分确认、接收、写盘、回放、新/旧快照及切主恢复。 |
| 锁已释放或过期，为什么旧执行者仍可能写坏缓存？ | [分布式锁与缓存租约](knowledge/distributed/leases-heartbeats-and-fencing.md) | 区分随机持有标识、严格递增代次与回填资格，解释41/42生效点。 |
| 增加消费者，为什么有时分担、有时各得一份？ | [队列、发布订阅与事件流](knowledge/messaging/queues-pubsub-event-streams-and-retention.md) | 按工作池、订阅和历史位置判断八次逻辑处理及103的含义。 |
| 文字写进上下文，为什么不能直接获得执行权？ | [提示词与指令边界](knowledge/ai/prompts-message-roles-and-instruction-boundaries.md) | 区分角色、资料、例子与实际权限；核对接口中的指令继承范围。 |
| [温度](glossary/ai.md#ai.sampling)降低，为什么输出仍可能稳定地答错？ | [温度、采样与复现](knowledge/ai/temperature-sampling-and-reproducibility.md) | 复算T=0.5与top-p=0.7，区分选择分布、事实和复现。 |
| [MCP](glossary/ai.md#ai.mcp)能发现工具，为什么仍不代表本次动作获准？ | [MCP与能力协商](knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md) | 沿宿主/客户端/服务器理解能力、原语、错误与业务完成。 |
| 模型模仿训练例子，为什么仍需独立评估？ | [微调、蒸馏与评估](knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md) | 区分参数适配、软目标和教师文本，解释独立测试及4个百分点。 |
| 先写测试再实现，为什么仍可能做错需求？ | [TDD与BDD](knowledge/engineering/tdd-bdd-examples-and-feedback-loops.md) | 说明红绿[重构](glossary/architecture.md#architecture.debt)、跨角色例子及测试到达目标行为的条件。 |
| 测试多、覆盖率高，为什么真实依赖仍会出错？ | [测试金字塔与证据组合](knowledge/engineering/test-pyramids-risk-portfolios-and-coverage.md) | 按风险选边界，用x=0解释分支覆盖与缺陷发现的区别。 |
| 方案已接受，为什么不能认定实现已经交付？ | [设计文档与决策记录](knowledge/engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md) | 区分设计、讨论与决定历史，连接实现及验证状态。 |
| 规格有测试链接，为什么仍不能宣布要求都满足？ | [规格驱动与验收追溯](knowledge/engineering/specifications-contracts-traceability-and-acceptance.md) | 把目标、规格、实现与证据双向关联，处理不确定付款及版本变化。 |
| 模板生成成功，为什么服务接入和后续升级仍很难？ | [黄金路径与开发者体验](knowledge/engineering/golden-paths-developer-experience-and-platform-feedback.md) | 覆盖创建、运行、升级及退出，复算75%与12.5%的分母。 |
| [服务指标](glossary/reliability.md#reliability.slos)和资源曲线齐全，为什么仍无法归因？ | [RED与USE](knowledge/reliability/red-use-service-signals-and-resource-evidence.md) | 区分接纳/完成/积压、错误速率/比例与可聚合分布。 |
| 在线比例很高，为什么持续执行的任务仍频繁中断？ | [可用性与可靠性](knowledge/reliability/availability-reliability-and-observation-windows.md) | 区分时间/请求比例、连续存活与恢复，声明窗口及故障语义。 |
| 故障注入成功，为什么仍不知道业务是否恢复？ | [混沌工程与受控故障](knowledge/reliability/chaos-engineering-hypotheses-stop-conditions-and-recovery.md) | 区分稳态假设、作用确认、停止条件与业务恢复，保留实验范围。 |
| 来自内网、证书有效的请求，为什么仍可能越权？ | [信任边界与威胁建模](knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md) | 画资产、入口与信任边界，把[最小权限](glossary/security.md#security.trust)和威胁路径连到验证证据。 |
| 字段符合 Schema，为什么仍不能直接保存？ | [资源模型与输入边界](knowledge/api/resource-models-input-validation-and-write-boundaries.md) | 区分资源、表示、动作及逐字段写入权限，检查并发保存条件。 |
| 实例已不就绪，为什么旧连接还会带来请求？ | [优雅关闭与请求排空](knowledge/api/graceful-shutdown-draining-and-inflight-outcomes.md) | 区分停止接纳、连接排空及业务结果；复算30秒总预算。 |
| 减少网络往返，为什么第一项反而等得更久？ | [批处理与流水线](knowledge/performance/batching-pipelining-and-amortized-waiting.md) | 复算18/6ms与7.5ms等待，解释事务、依赖、部分错误和有界窗口。 |
| 整体资源不忙，为什么一个热键已经过载？ | [热点与资源竞争](knowledge/performance/hotspots-contention-and-serialized-service.md) | 复算450>300与500/s上界，用局部分布而非平均值定位竞争。 |
| 副本数提高，为什么实际能力没有立即增加？ | [容量规划与自动扩缩容](knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md) | 复算280/4/5与[HPA](glossary/devops.md#devops.autoscaling)原始15，说明反馈[延迟](glossary/performance.md#performance.latency-throughput)和故障余量。 |
| [DNS](glossary/networking.md#networking.dns) 能解析，为什么入口仍到不了后端？ | [集群入口与服务发现](knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md) | 串起DNS、Service、端点和入口，分别检查绑定与跨空间引用许可。 |
| 私有子网、[安全组](glossary/devops.md#devops.cloud-network)和路由分别保证什么？ | [云网络与访问边界](knowledge/devops/cloud-networks-subnets-routes-and-security-groups.md) | 区分路由、[NAT](glossary/networking.md#networking.nat)、有状态/无状态过滤及业务身份，限定AWS IPv4例子。 |
| 制品签名有效，为什么仍可能发布错误版本或产生回归？ | [可信制品与渐进发布](knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md) | 把摘要、身份及构建期望连到同一产物，再判断暴露、观察和回退。 |
| 服务拆成多个[进程](glossary/systems.md#systems.execution-units)，为何仍要共同发布、共同恢复？ | [模块化单体与微服务](knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md) | [模块边界](knowledge/architecture/module-boundaries-and-dependencies.md)与[跨边界提交](knowledge/distributed/two-phase-commit-sagas-and-recovery.md) |
| 为了遵守 [SOLID](glossary/architecture.md#architecture.principles) 与 DRY 拆了很多接口，为何修改更难？ | [设计原则与抽象成本](knowledge/architecture/design-principles-contracts-and-abstraction-costs.md) | [模块依赖](knowledge/architecture/module-boundaries-and-dependencies.md)与[契约测试](knowledge/engineering/contract-testing-and-compatibility.md) |
| 同样包一层对象，策略、适配器和装饰器各解决什么？ | [设计模式与协作契约](knowledge/architecture/design-patterns-collaboration-and-semantic-boundaries.md) | [设计原则](knowledge/architecture/design-principles-contracts-and-abstraction-costs.md)与[Outbox](knowledge/messaging/transactional-outbox.md) |
| 新系统出错，把流量切回旧系统为什么仍可能丢状态？ | [渐进替换与写入归属](knowledge/architecture/strangler-fig-migration-write-authority-and-rollback.md) | [CDC](knowledge/database/cdc-snapshots-log-positions-and-replay.md)与[迁移兼容](knowledge/database/schema-migrations-and-compatibility.md) |
| 高性能、易维护怎样写成场景？架构决定怎样保留理由与证据？ | [质量属性与架构决策](knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md) | [知识库 ADR](knowledge/architecture/knowledge-base-adr.md)与[基准测试](knowledge/performance/benchmarks-workloads-and-speedup.md) |
| 列表插入、重排以后，草稿为什么跑到另一行？[稳定 key](glossary/frontend.md#frontend.component-identity) 能保证什么？ | [组件协调与 key](knowledge/frontend/reconciliation-keys-and-component-identity.md) | [响应式更新](knowledge/frontend/reactive-state-and-update-scheduling.md)与[路由状态](knowledge/frontend/routing-state-and-cache-lifecycles.md) |
| 实时页面重连成功了，为何仍漏消息或重复通知？ | [WebSocket/SSE 与断线补读](knowledge/frontend/websocket-sse-reconnection-and-replay.md) | [投递与确认](knowledge/messaging/delivery-acknowledgements-and-idempotency.md)与[幂等性](knowledge/api/idempotency.md) |
| 单机跑分很好，用户为何仍觉得页面慢、点击卡、内容跳？ | [Core Web Vitals 与体验证据](knowledge/frontend/core-web-vitals-field-data-and-diagnostic-boundaries.md) | [长任务](knowledge/frontend/long-tasks-and-responsiveness.md)与[基准测试](knowledge/performance/benchmarks-workloads-and-speedup.md) |
| 新 [Service Worker](glossary/frontend.md#frontend.offline) 下载完成为何还没接管？离线保存怎样确认？ | [Service Worker 与离线更新](knowledge/frontend/service-workers-offline-caches-and-update-lifecycles.md) | [分块资源](knowledge/frontend/bundling-tree-shaking-and-code-splitting.md)与[路由缓存](knowledge/frontend/routing-state-and-cache-lifecycles.md) |
| 页面设置 60 秒更新，为何过期后仍能读到旧内容？ | [增量再生成与页面缓存](knowledge/frontend/incremental-regeneration-revalidation-and-freshness.md) | [条件请求](knowledge/api/conditional-requests-and-cache-validation.md)与[边缘缓存](knowledge/networking/cdn-edge-caches-and-waf-boundaries.md) |
| 主[路由表](glossary/networking.md#networking.routing)有更精确路由，为何仍走别的出口？[BGP](glossary/networking.md#networking.policy-routing) 切换为何未恢复业务？ | [策略与动态路由](knowledge/networking/policy-routing-control-planes-and-convergence.md) | [IP 转发基础](knowledge/networking/network-layers-ip-subnets-and-routing.md)与 [NAT 状态](knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md) |
| 小包能通，传大消息却卡住，隧道的长度应怎样计算？ | [路径 MTU 与隧道](knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md) | [UDP 与 QUIC](knowledge/networking/udp-quic-streams-and-delivery-boundaries.md)，实际大小/ICMP 对照待验证 |
| 下载占满带宽后交互变慢，窗口、节奏与[排队等待](glossary/performance.md#performance.queueing)各该检查什么？ | [拥塞算法与队列管理](knowledge/networking/congestion-algorithms-aqm-and-ecn.md) | [TCP 窗口](knowledge/networking/tcp-flow-control-and-congestion.md)与[背压](knowledge/performance/backpressure-and-bounded-queues.md) |
| IPv6 多个源地址怎样选择？地址轮换和 RA 防护能证明什么？ | [IPv6 源地址、隐私与接入防护](knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md) | [IPv6 与邻居发现](knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md)与[服务身份](knowledge/security/mtls-service-identities-and-trust-boundaries.md) |
| I/O 已完成、[线程](glossary/systems.md#systems.execution-units)已唤醒，为什么仍没运行；切换次数能否算出调度[延迟](glossary/performance.md#performance.latency-throughput)？ | [上下文切换](knowledge/systems/context-switches-run-queues-and-scheduling-delay.md) | [相关领域](knowledge/systems/index.md) |
| 地址仍映射为什么对象已失效，free 后 RSS 不降又说明什么？ | [栈堆与内存布局](knowledge/systems/process-memory-layout-stacks-heaps-and-lifetimes.md) | [相关领域](knowledge/systems/index.md) |
| [CAS](glossary/systems.md#systems.synchronization) 是原子的且没有 mutex，为什么单个调用仍可能一直失败？ | [无锁进度](knowledge/systems/lock-free-algorithms-linearization-and-progress.md) | [相关领域](knowledge/systems/index.md) |
| 节点已从根移除，为什么还不能释放；hazard、epoch 与 [RCU](glossary/systems.md#systems.memory-reclamation) 分别等谁？ | [安全内存回收](knowledge/systems/safe-memory-reclamation-aba-hazards-and-epochs.md) | [相关领域](knowledge/systems/index.md) |
| 同一函数为何预热后变快，输入变化后又回退；编译、解释与 [JIT](glossary/runtime.md#runtime.compilation) 各做什么？ | [编译与 JIT](knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md) | [相关领域](knowledge/runtime/index.md) |
| 外层 catch 为什么收不到稍后失败，finally 又为什么可能把失败改成成功？ | [异常传播](knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md) | [相关领域](knowledge/runtime/index.md) |
| 数据能够解析，为何大整数、缺失字段或共享对象仍改变了含义？ | [序列化](knowledge/runtime/serialization-representations-schemas-and-identity.md) | [相关领域](knowledge/runtime/index.md) |
| 跨语言参数相同为何仍崩溃，指针、回调和输出缓冲区由谁持有与释放？ | [跨语言调用](knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md) | [相关领域](knowledge/runtime/index.md) |
| 字节码验证通过为何仍缺依赖、权限或资源保证，[VM](glossary/runtime.md#runtime.virtual-machine) 与宿主怎样分工？ | [语言虚拟机](knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md) | [相关领域](knowledge/runtime/index.md) |
| 命令已成功，查询投影为何仍是旧值；读己之写和投影重建分别需要什么版本依据？ | [CQRS](knowledge/architecture/cqrs-read-write-models-and-projection-lag.md) | [相关领域](knowledge/architecture/index.md) |
| [事件流](glossary/messaging.md#messaging.models)怎样成为权威状态，两个并发命令如何用预期版本避免旧决定同时生效？ | [事件溯源](knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md) | [相关领域](knowledge/architecture/index.md) |
| 迟到事件属于哪个窗口，水位线越过后何时修订、丢弃或旁路？ | [事件时间与窗口](knowledge/messaging/event-time-watermarks-windows-and-late-data.md) | [相关领域](knowledge/messaging/index.md) |
| 消息链如何尊重因果又保留物理时间参照，时间戳何时不能代替提交、期限或读取屏障？ | [HLC](knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md) | [相关领域](knowledge/distributed/index.md) |
| 断联副本怎样合并增加和删除，为什么正确收敛仍可能违反余额或业务约束？ | [CRDT](knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md) | [相关领域](knowledge/distributed/index.md) |
| 全量快照怎样接续变更流，来源位点、事务、删除和目标重放分别怎样验收？ | [CDC](knowledge/database/cdc-snapshots-log-positions-and-replay.md) | [相关领域](knowledge/database/index.md) |
| 怎样证明[分治](glossary/algorithms.md#algorithms.divide-conquer)能组合出正确答案，回溯剪枝又如何保留所有需要的方案并计入总工作与输出？ | [分治与回溯](knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md) | [相关领域](knowledge/algorithms/index.md) |
| 失配后如何安全回退并保留重叠与跨块命中；返回位置怎样与字节、码点和规范化后的文本对齐？ | [字符串匹配](knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md) | [相关领域](knowledge/algorithms/index.md) |
| 不同[认证](glossary/security.md#security.identity)因子、抗钓鱼、认证器绑定/恢复和会话新鲜度怎样共同成立？ | [MFA](knowledge/security/multi-factor-authentication-passkeys-and-recovery.md) | [相关领域](knowledge/security/index.md) |
| 服务替用户调用下一跳时，主体、执行者、受众、权限、认证新鲜度与撤销各需什么依据？ | [跨服务委托](knowledge/security/service-delegation-token-exchange-and-audience.md) | [相关领域](knowledge/security/index.md) |
| 自动配置出 IPv6 地址后，on-link、默认路由器、下一跳映射和邻居可达性各还缺什么依据？ | [IPv6 与邻居发现](knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) | [相关领域](knowledge/networking/index.md) |
| 角色、属性与关系怎样决定访问；权限变化后，策略、事实、缓存和执行边界各需什么证据才能停止旧[授权](glossary/security.md#security.identity)？ | [权限模型与策略传播](knowledge/security/authorization-models-policy-distribution-and-revocation.md) | [相关领域](knowledge/security/index.md) |
| 怎样按整值/字段/成员/排名/消费位置选择 Redis 类型，命令、事务、过期、槽位与耐久各提供什么边界？ | [Redis 数据结构](knowledge/cache-search/redis-data-types-operations-and-atomicity.md) | [相关领域](knowledge/cache-search/index.md) |
| 上传、对象版本与业务发布分别确认什么，条件写和预签名URL怎样限定并发、身份与期限？ | [对象存储与预签名访问](knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md) | [相关领域](knowledge/cache-search/index.md) |
| 缓存写入成功时，后端更新、可恢复接纳、重复与顺序分别确认到哪里；怎样避免[异步写回](glossary/cache-search.md#cache-search.cache-write)在故障和积压中丢掉已接受责任？ | [写穿与异步写回](knowledge/cache-search/write-through-write-behind-and-durability.md) | [相关领域](knowledge/cache-search/index.md) |
| 数据报、可靠流、路径迁移与业务完成各是什么保证，丢包、0-RTT 和回退后还需核对什么？ | [UDP 与 QUIC](knowledge/networking/udp-quic-streams-and-delivery-boundaries.md) | [相关领域](knowledge/networking/index.md) |
| 新老生产者与消费者并存、历史事件回放时，怎样分开验证结构兼容、事实含义、事件身份及业务副作用？ | [事件格式演进](knowledge/messaging/event-contracts-schema-evolution-and-replay.md) | [相关领域](knowledge/messaging/index.md) |
| 边缘命中、[WAF](glossary/networking.md#networking.cdn-waf) 放行与源站访问各证明了什么，缓存身份隔离、撤回及业务[授权](glossary/security.md#security.identity)还需哪些条件？ | [CDN 与 WAF](knowledge/networking/cdn-edge-caches-and-waf-boundaries.md) | [相关领域](knowledge/networking/index.md) |
| 热门键失效后怎样共享一次加载，为什么同键合并仍需权限范围、等待和回源容量、跨实例协调及迟到回填规则？ | [缓存加载合并与惊群控制](knowledge/cache-search/cache-load-coalescing-and-stampedes.md) | [相关领域](knowledge/cache-search/index.md) |
| 成员配置改变时怎样保持新旧决定的安全关系，learner、分区追赶与永久失多数后的重建分别能恢复什么？ | [共识成员变更与分区恢复](knowledge/distributed/membership-changes-and-partition-recovery.md) | [相关领域](knowledge/distributed/index.md) |
| [双向 TLS](glossary/security.md#security.mtls) 分别证明了证书链、预期服务身份和私钥持有的什么；经过代理、证书轮换或代表用户调用时，还缺少哪些[授权](glossary/security.md#security.identity)和失效边界？ | [mTLS 与服务身份](knowledge/security/mtls-service-identities-and-trust-boundaries.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 同一订单需求怎样在资源、远程命令和字段查询之间建模，网关能接管哪些保证，哪些仍必须由执行服务保护？ | [API 风格与网关](knowledge/api/api-styles-contracts-and-gateway-boundaries.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 分区与正常通信时，一次读写怎样在一致性、最终完成与[延迟](glossary/performance.md#performance.latency-throughput)间作出明确承诺，为什么副本数、超时和产品标签都不足以代替操作历史？ | [CAP 与 PACELC](knowledge/distributed/cap-pacelc-and-operation-guarantees.md) | [一致性与复制](knowledge/distributed/consistency-and-replication.md) |
| 怎样界定并维护[分布式 ID](glossary/distributed.md#distributed.ids) 的唯一性，为什么时间可排序的编号仍不证明提交次序、[幂等](glossary/api.md#api.idempotency)结果或访问权限？ | [分布式 ID](knowledge/distributed/distributed-identifiers-time-and-uniqueness.md) | [一致性与复制](knowledge/distributed/consistency-and-replication.md) |
| 怎样从数据事实、读写模式与一致性边界决定关系/键值/文档组织，并正确区分规范化、历史快照和待同步副本？ | [数据模型与访问模式](knowledge/database/data-models-and-access-patterns.md) | [索引与执行计划](knowledge/database/indexes-and-query-plans.md) |
| 数据拆到多个节点后，一次查询到底需要访问哪些数据，为什么仍可能扇出、[热点](glossary/performance.md#performance.contention)、约束失效或迁移未完成？ | [分区、分片与数据路由](knowledge/database/partitioning-sharding-and-data-routing.md) | [索引与执行计划](knowledge/database/indexes-and-query-plans.md) |
| 外部数据怎样保持为 SQL 的值，而不成为查询结构；语法安全之后还缺哪些权限和执行条件？ | [SQL 注入与参数化查询](knowledge/security/sql-injection-parameters-and-query-structure.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 新秘密已经保存和部署，为什么旧凭据、旧会话或旧密文仍然有效，轮换、撤销与销毁应怎样分别完成？ | [密钥与凭证生命周期](knowledge/security/secrets-credentials-rotation-and-revocation.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 已知服务器 [IP](glossary/networking.md#networking.transport) 后，主机怎样确定当前[下一跳](glossary/networking.md#networking.routing)、跨过子网并处理逐跳封装、返回路径与分组大小限制？ | [网络分层、IP 与路由](knowledge/networking/network-layers-ip-subnets-and-routing.md) | [HTTPS 请求链路](knowledge/networking/https-request-lifecycle.md) |
| 请求经过入口后，客户端与后端分别在和谁建立 TCP/[TLS](glossary/networking.md#networking.tls)，地址、流量选择与返回路径怎样改变？ | [NAT、代理与负载均衡](knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md) | [HTTPS 请求链路](knowledge/networking/https-request-lifecycle.md) |
| 地址空间分开后，怎样交换数据并管理生命周期 | [IPC 与共享所有权](knowledge/systems/ipc-channels-shared-memory-and-ownership.md) | [文件描述符](knowledge/systems/file-descriptors-and-open-file-descriptions.md) |
| 原子标志已经更新，为什么其他数据仍不能安全读取 | [内存顺序与原子操作](knowledge/systems/memory-order-atomics-and-publication.md) | [锁与同步](knowledge/systems/locks-and-synchronization.md) |
| 内容已经转义，为什么放进另一个位置仍不安全 | [XSS 与浏览器输出边界](knowledge/security/xss-contexts-sinks-and-browser-defenses.md) | [来源与 CSRF](knowledge/security/origins-cors-and-csrf.md) |
| URL 检查通过，服务端为什么仍可能访问非预期目标 | [SSRF 与服务端请求边界](knowledge/security/ssrf-url-resolution-and-egress-boundaries.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 时间戳更小，为什么不能证明事件先导致了另一个事件 | [逻辑时钟与因果顺序](knowledge/distributed/logical-clocks-causality-and-concurrency.md) | [一致性与复制](knowledge/distributed/consistency-and-replication.md) |
| 新增节点后，哪些键需要移动，[热点](glossary/performance.md#performance.contention)为什么仍然存在 | [一致性哈希与再均衡](knowledge/distributed/consistent-hashing-placement-and-rebalancing.md) | [Cache-Aside](knowledge/cache-search/cache-aside-and-invalidation.md) |
| 收到停止信号后，为什么服务没有安全退出 | [信号、取消与退出](knowledge/systems/signals-cancellation-and-shutdown.md) | [进程、线程与协程](knowledge/systems/process-thread-coroutine.md) |
| 连接已建立，发送速度为什么仍然下降 | [TCP 流量控制与拥塞控制](knowledge/networking/tcp-flow-control-and-congestion.md) | [TCP 与 TLS 连接状态](knowledge/networking/tcp-tls-and-connection-states.md) |
| 密码泄露后，哈希、盐和[账号恢复](glossary/security.md#security.account-recovery)分别保护什么 | [密码存储与账号恢复](knowledge/security/password-storage-and-account-recovery.md) | [认证、会话与令牌](knowledge/security/authentication-sessions-and-tokens.md) |
| 回调签名通过，为什么仍可能重复执行或处理错事件 | [Webhook 签名与防重放](knowledge/api/webhook-signatures-replay-and-delivery.md) | [幂等性](knowledge/api/idempotency.md) |
| 跨服务操作部分成功后，怎样决定提交或补偿 | [2PC、Saga 与补偿恢复](knowledge/distributed/two-phase-commit-sagas-and-recovery.md) | [Outbox](knowledge/messaging/transactional-outbox.md) |
| 新索引已经构建，怎样覆盖期间的新增和删除 | [索引重建与切换](knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) | [向量索引与近似检索](knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md) |
| 单独运行通过，为什么组合或[并行](glossary/systems.md#systems.concurrency)运行偶尔失败 | [测试稳定性与隔离](knowledge/engineering/flaky-tests-isolation-and-evidence.md) | [测试范围与替身](knowledge/engineering/test-scopes-and-doubles.md) |
| 功能还没做完，怎样频繁集成并控制开放 | [主干开发与功能开关](knowledge/engineering/trunk-based-development-and-feature-flags.md) | [交付与回滚](knowledge/devops/build-deploy-rollback.md) |
| 告警恢复了，为什么还不能结束事故处理 | [事故响应与复盘](knowledge/reliability/incident-response-recovery-and-postmortems.md) | [恢复目标](knowledge/reliability/failure-domains-redundancy-and-recovery.md) |
| 配置源码没变，为什么基础设施计划仍有修改 | [IaC 与状态漂移](knowledge/devops/iac-state-drift-and-change-plans.md) | [声明式部署](knowledge/devops/declarative-deployments-and-health-probes.md) |
| 代码结构变好了，怎样确认没有改掉原有行为 | [技术债与重构](knowledge/architecture/technical-debt-refactoring-and-behavior.md) | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) |
| 检查全绿，怎样区分无问题、漏扫与规则未覆盖 | [静态分析与告警](knowledge/engineering/static-analysis-rules-and-findings.md) | [类型系统与运行时校验](knowledge/runtime/type-systems-and-runtime-validation.md) |
| 已有人批准，为什么最终版本仍不能直接发布 | [代码评审与小步变更](knowledge/engineering/code-review-context-and-change-boundaries.md) | [构建、部署与回滚](knowledge/devops/build-deploy-rollback.md) |
| 已锁版本并生成清单，怎样判断内容与来源范围 | [依赖锁定与 SBOM](knowledge/engineering/dependency-resolution-lockfiles-and-sbom.md) | [契约测试与版本兼容](knowledge/engineering/contract-testing-and-compatibility.md) |
| 第一次到达目标，为何仍不是最低成本路线 | [加权最短路与松弛](knowledge/algorithms/weighted-shortest-paths-and-relaxation.md) | [图遍历与依赖顺序](knowledge/algorithms/graphs-traversal-and-dependency-order.md) |
| 每一步都选最好，为何整体仍不是最优 | [贪心选择与交换论证](knowledge/algorithms/greedy-choices-and-exchange-arguments.md) | [动态规划与状态设计](knowledge/algorithms/dynamic-programming-states-and-dependency-order.md) |
| 已经保存子问题结果，为何仍重复使用同一物品 | [动态规划与状态设计](knowledge/algorithms/dynamic-programming-states-and-dependency-order.md) | [属性测试与状态模型](knowledge/engineering/property-testing-and-state-models.md) |
| 总连通成本最低，为何两点间路线仍然更长 | [并查集与最小生成树](knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md) | [加权最短路与松弛](knowledge/algorithms/weighted-shortest-paths-and-relaxation.md) |
| 数据已经在内存，访问为什么仍然慢 | [CPU 缓存与局部性](knowledge/systems/cpu-caches-locality-and-false-sharing.md) | [虚拟内存与缺页](knowledge/systems/virtual-memory-pages-and-faults.md) |
| 主机还有空闲，请求为什么仍得不到 CPU | [CPU 利用率、负载与配额](knowledge/performance/cpu-time-utilization-load-and-quotas.md) | [镜像、容器与资源隔离](knowledge/devops/images-containers-and-resource-isolation.md) |
| [火焰图](glossary/performance.md#performance.profiling)最宽的函数，是否就是[延迟](glossary/performance.md#performance.latency-throughput)根因 | [Profiling 与火焰图](knowledge/performance/profiling-stacks-and-flame-graphs.md) | [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 循环已快四倍，服务为什么没有同样变快 | [基准测试与加速比](knowledge/performance/benchmarks-workloads-and-speedup.md) | [延迟、吞吐与排队](knowledge/performance/latency-throughput-and-queues.md) |
| 正确资料已经入库，为什么向量检索仍漏掉近邻 | [向量索引与近似检索](knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md) | [Evals 与失败分析](knowledge/ai/evals-and-failure-analysis.md) |
| 已经融合两路结果，[重排](glossary/cache-search.md#cache-search.hybrid)为什么仍救不回关键片段 | [混合召回与重排](knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md) | [RAG 与依据](knowledge/ai/rag-retrieval-and-grounding.md) |
| 写入已经返回，为什么后台还在合并并开始停写 | [LSM、SSTable 与压缩合并](knowledge/database/lsm-sstables-and-compaction.md) | [WAL 与恢复](knowledge/database/wal-and-crash-recovery.md) |
| 文档包含全部搜索词，为什么仍不匹配短语或排在前面 | [倒排索引与全文检索](knowledge/cache-search/inverted-indexes-analysis-and-relevance.md) | [RAG 与依据](knowledge/ai/rag-retrieval-and-grounding.md) |
| 索引只有几层，为什么范围查询仍读很多页 | [B/B+ 树与页索引](knowledge/algorithms/b-trees-bplus-trees-and-page-indexes.md) | [索引与执行计划](knowledge/database/indexes-and-query-plans.md) |
| 前缀路径存在，为什么仍不能认定这个键已收录 | [Trie 与前缀检索](knowledge/algorithms/tries-prefix-search-and-key-encoding.md) | [排序与二分](knowledge/algorithms/sorting-binary-search-and-boundaries.md) |
| Bloom 回答可能存在，能否直接跳过重复任务 | [Bloom Filter 与成员判断](knowledge/cache-search/bloom-filters-membership-and-synchronization.md) | [幂等与提交边界](knowledge/api/idempotency.md) |
| 缓存刚访问过，为什么仍被淘汰或继续返回旧值 | [LRU/LFU 与缓存淘汰](knowledge/cache-search/lru-lfu-and-capacity-eviction.md) | [缓存与失效](knowledge/cache-search/cache-aside-and-invalidation.md) |
| 都是保存任务，为什么从队首移除越来越慢 | [线性结构与端点操作](knowledge/algorithms/sequences-stacks-queues-and-deques.md) | [复杂度与结构选择](knowledge/algorithms/complexity-and-data-structures.md) |
| 已用按键映射，为什么仍变慢或覆盖了不该合并的数据 | [哈希表与键契约](knowledge/algorithms/hash-tables-collisions-and-key-contracts.md) | [缓存与失效](knowledge/cache-search/cache-aside-and-invalidation.md) |
| 二分遇到重复值、空序列或边界时为什么答错 | [排序与二分查找](knowledge/algorithms/sorting-binary-search-and-boundaries.md) | [属性测试与状态模型](knowledge/engineering/property-testing-and-state-models.md) |
| 能取最高优先级，为什么还不能按序遍历或查任意任务 | [树、堆与优先队列](knowledge/algorithms/trees-heaps-and-priority-queues.md) | [背压与有界队列](knowledge/performance/backpressure-and-bounded-queues.md) |
| 找到全部可达模块，为什么仍排不出合法启动顺序 | [图遍历与依赖顺序](knowledge/algorithms/graphs-traversal-and-dependency-order.md) | [模块系统与循环依赖](knowledge/runtime/modules-bindings-and-circular-dependencies.md) |
| 已经申请内存，为什么访问仍等待或后来才失败 | [虚拟内存与缺页](knowledge/systems/virtual-memory-pages-and-faults.md) | [可达性与 GC](knowledge/runtime/reachability-and-garbage-collection.md) |
| 一次 read 很慢，怎样区分内核处理、等待与调度 | [系统调用与权限边界](knowledge/systems/syscalls-privilege-and-return-contracts.md) | [同步与阻塞](knowledge/runtime/async-and-blocking.md) |
| 新描述符为何共享读取位置，关闭后资源为何仍在 | [文件描述符与打开文件描述](knowledge/systems/file-descriptors-and-open-file-descriptions.md) | [系统调用与权限边界](knowledge/systems/syscalls-privilege-and-return-contracts.md) |
| 一个[线程](glossary/systems.md#systems.execution-units)怎样等待多个连接，收到事件为何仍读不完整 | [I/O 多路复用与就绪通知](knowledge/systems/io-multiplexing-readiness-and-event-loops.md) | [背压与有界队列](knowledge/performance/backpressure-and-bounded-queues.md) |
| 模块和导出名都存在，为什么初始化仍读不到值 | [模块系统与循环依赖](knowledge/runtime/modules-bindings-and-circular-dependencies.md) | [闭包与词法绑定](knowledge/runtime/closures-and-lexical-bindings.md) |
| 类型检查通过，接口字段为什么仍导致运行失败 | [类型系统与运行时校验](knowledge/runtime/type-systems-and-runtime-validation.md) | [契约测试与版本兼容](knowledge/engineering/contract-testing-and-compatibility.md) |
| 文件变小了，为什么点击仍卡住或导航后白屏 | [打包与代码分割](knowledge/frontend/bundling-tree-shaking-and-code-splitting.md) | [浏览器长任务](knowledge/frontend/long-tasks-and-responsiveness.md) |
| 新部署成功后，旧标签页为什么加载不到按需资源 | [打包与代码分割](knowledge/frontend/bundling-tree-shaking-and-code-splitting.md) | [前端路由与缓存](knowledge/frontend/routing-state-and-cache-lifecycles.md) |
| 多个入口都能改业务数据，同一条规则究竟由谁守住 | [领域模型、聚合与业务不变量](knowledge/architecture/domain-models-aggregates-and-invariants.md) | [模块边界与依赖](knowledge/architecture/module-boundaries-and-dependencies.md) |
| 消费者和提供方各自测试通过，为什么仍接不上 | [契约测试与版本兼容](knowledge/engineering/contract-testing-and-compatibility.md) | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) |
| 新版本组合已通过，旧客户端与回退版本怎么办 | [契约测试与版本兼容](knowledge/engineering/contract-testing-and-compatibility.md) | [构建、部署与回滚](knowledge/devops/build-deploy-rollback.md) |
| 预订和取消单测都通过，连续操作为什么仍破坏库存 | [属性测试与状态模型](knowledge/engineering/property-testing-and-state-models.md) | [库存并发](knowledge/database/concurrent-inventory.md) |
| 使用同一[镜像](glossary/devops.md#devops.containers)，生产为什么仍变慢、缺文件或被终止 | [镜像、容器与资源隔离](knowledge/devops/images-containers-and-resource-isolation.md) | [构建、部署与回滚](knowledge/devops/build-deploy-rollback.md) |
| 部署已接受、进程还活着，为什么仍不能接流量 | [声明式部署与健康探针](knowledge/devops/declarative-deployments-and-health-probes.md) | [SLI/SLO](knowledge/reliability/slis-slos-and-error-budgets.md) |
| 共享依赖变慢，为什么[健康探针](glossary/reliability.md#reliability.probes)让故障继续扩大 | [声明式部署与健康探针](knowledge/devops/declarative-deployments-and-health-probes.md) | [熔断、隔离与降级](knowledge/reliability/circuit-breakers-isolation-and-degradation.md) |
| 已有副本和备份，为什么仍不能按目标恢复业务 | [故障域、冗余与恢复目标](knowledge/reliability/failure-domains-redundancy-and-recovery.md) | [备份与时间点恢复](knowledge/database/backups-and-point-in-time-recovery.md) |
| 已拿到登录 code，为什么还不能确认用户身份 | [OAuth 与 OIDC](knowledge/security/oauth-oidc-and-pkce.md) | [认证、会话与令牌](knowledge/security/authentication-sessions-and-tokens.md) |
| 浏览器报 [CORS](glossary/security.md#security.origin) 错误，服务端修改为什么仍已发生 | [同源、CORS 与 CSRF](knowledge/security/origins-cors-and-csrf.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 已有 [ETag](glossary/api.md#api.conditionals)，怎样既少传正文又避免覆盖别人修改 | [HTTP 条件请求](knowledge/api/conditional-requests-and-cache-validation.md) | [HTTP 契约与分页](knowledge/api/contracts-and-pagination.md) |
| 保存[重试](glossary/api.md#api.retries)收到 412，能否断定第一次没有成功 | [HTTP 条件请求](knowledge/api/conditional-requests-and-cache-validation.md) | [幂等性](knowledge/api/idempotency.md) |
| 值已经改了，旧回调为什么仍读到旧结果 | [闭包与词法绑定](knowledge/runtime/closures-and-lexical-bindings.md) | [响应式状态与更新](knowledge/frontend/reactive-state-and-update-scheduling.md) |
| 状态已经更新，[DOM](glossary/frontend.md#frontend.render-tree) 与屏幕为何还没变 | [响应式状态与更新](knowledge/frontend/reactive-state-and-update-scheduling.md) | [事件循环与微任务](knowledge/runtime/event-loop-and-microtasks.md) |
| URL 已切换，为什么仍显示上一个对象的资料 | [前端路由与缓存](knowledge/frontend/routing-state-and-cache-lifecycles.md) | [闭包与词法绑定](knowledge/runtime/closures-and-lexical-bindings.md) |
| 已设 no-cache，为什么后退仍可能恢复旧页面 | [前端路由与缓存](knowledge/frontend/routing-state-and-cache-lifecycles.md) | [缓存与失效](knowledge/cache-search/cache-aside-and-invalidation.md) |
| 收到多数响应，为何仍不能宣布形成一致决定 | [共识与 Quorum](knowledge/distributed/consensus-leaders-and-quorums.md) | [一致性与复制](knowledge/distributed/consistency-and-replication.md) |
| 锁已经过期，旧进程为何仍能写入 | [租约与 Fencing](knowledge/distributed/leases-heartbeats-and-fencing.md) | [共识与 Quorum](knowledge/distributed/consensus-leaders-and-quorums.md) |
| 消费偏移已提交，业务为什么仍可能遗漏或重复 | [分区、消费组与偏移](knowledge/messaging/partitions-consumer-groups-and-offsets.md) | [消息投递与确认](knowledge/messaging/delivery-acknowledgements-and-idempotency.md) |
| 助手说已转交，原任务就完成了吗 | [路由与交接契约](knowledge/ai/workflow-routing-and-handoff-contracts.md) | [编排状态与检查点](knowledge/ai/workflow-state-and-checkpoints.md) |
| 已有 checkpoint，恢复为何仍可能重复操作 | [编排状态与检查点](knowledge/ai/workflow-state-and-checkpoints.md) | [可恢复 Runtime](knowledge/ai/recoverable-runtime.md) |
| 每个角色都限制三次，流程为何仍不停止 | [持久化预算与失败收敛](knowledge/ai/durable-budgets-and-failure-convergence.md) | [路由与交接契约](knowledge/ai/workflow-routing-and-handoff-contracts.md) |
| 模型推测的偏好可以直接记成事实吗 | [记忆写入与来源](knowledge/ai/memory-writing-and-provenance.md) | [记忆治理实验](knowledge/ai/memory-governance-lab.md) |
| 用户已改偏好，为什么旧摘要又覆盖新值 | [记忆版本与失效](knowledge/ai/memory-versions-conflicts-and-expiry.md) | [记忆治理实验](knowledge/ai/memory-governance-lab.md) |
| 成员已撤权，旧缓存还能返回记忆吗 | [记忆权限与删除](knowledge/ai/memory-access-revocation-and-deletion.md) | [记忆治理实验](knowledge/ai/memory-governance-lab.md) |
| 活动记录已删除，备份为什么仍有原文 | [记忆治理实验](knowledge/ai/memory-governance-lab.md) | [记忆权限与删除](knowledge/ai/memory-access-revocation-and-deletion.md) |
| 模型说已调用工具，为什么还不能显示业务成功 | [工具调用契约](knowledge/ai/tool-calling-and-execution-contracts.md) | [工具执行边界实验](knowledge/ai/tool-execution-boundaries-lab.md) |
| 参数已经是合法 JSON，为何仍不能直接执行 | [结构化输出与校验](knowledge/ai/structured-outputs-and-validation.md) | [工具执行边界实验](knowledge/ai/tool-execution-boundaries-lab.md) |
| 工具返回声称用户已批准，[运行时](glossary/runtime.md#runtime.virtual-machine)应该相信吗 | [工具授权与不可信结果](knowledge/ai/tool-authorization-and-untrusted-results.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 工具已创建对象但结果丢失，如何避免盲目重做 | [工具执行边界实验](knowledge/ai/tool-execution-boundaries-lab.md) | [可恢复 Runtime](knowledge/ai/recoverable-runtime.md) |
| 改了 [DNS](glossary/networking.md#networking.dns)，为什么仍然访问旧地址 | [DNS 缓存与地址选择](knowledge/networking/dns-caching-and-address-selection.md) | [HTTP 复用与连接池](knowledge/networking/http-reuse-pools-and-timeouts.md) |
| 连接建立或收到 reset，能否判断业务已完成 | [TCP 与 TLS 连接状态](knowledge/networking/tcp-tls-and-connection-states.md) | [幂等性](knowledge/api/idempotency.md) |
| 调用已经开始，服务端为何没有请求日志 | [HTTP 复用与连接池](knowledge/networking/http-reuse-pools-and-timeouts.md) | [连接生命周期实验](knowledge/networking/connection-lifecycle-lab.md) |
| 收到响应头或超时通知，为何连接仍被占用 | [连接生命周期实验](knowledge/networking/connection-lifecycle-lab.md) | [超时与重试预算](knowledge/reliability/timeouts-and-retry-budgets.md) |
| 消费者跟不上，异步[队列](glossary/algorithms.md#algorithms.queues)为何仍吃满内存 | [背压与有界队列](knowledge/performance/backpressure-and-bounded-queues.md) | [过载控制实验](knowledge/performance/overload-control-lab.md) |
| 已经限制每秒请求数，[连接池](glossary/api.md#api.pool)为什么仍满 | [限流、并发与配额](knowledge/api/rate-limits-concurrency-and-quotas.md) | [过载控制实验](knowledge/performance/overload-control-lab.md) |
| 一个依赖变慢，为何拖垮其他接口 | [熔断、隔离与降级](knowledge/reliability/circuit-breakers-isolation-and-degradation.md) | [超时与重试预算](knowledge/reliability/timeouts-and-retry-budgets.md) |
| 提交成功后数据页还没写完，重启怎样恢复 | [WAL 与崩溃恢复](knowledge/database/wal-and-crash-recovery.md) | [事务隔离与 MVCC](knowledge/database/isolation-and-mvcc.md) |
| 备份任务成功，怎样证明误删除后能恢复 | [备份与时间点恢复](knowledge/database/backups-and-point-in-time-recovery.md) | [恢复实验](knowledge/database/backup-recovery-lab.md) |
| 改表后回退旧程序，为什么仍不能处理数据 | [数据库迁移兼容](knowledge/database/schema-migrations-and-compatibility.md) | [构建、部署与回滚](knowledge/devops/build-deploy-rollback.md) |
| 每一步都成功，为何[并发](glossary/systems.md#systems.concurrency)后总量仍然错 | [竞态与原子性](knowledge/systems/races-and-atomicity.md) | [库存并发实验](knowledge/database/inventory-concurrency-lab.md) |
| 已经加锁，多实例部署后为何仍有竞争 | [锁与同步原语](knowledge/systems/locks-and-synchronization.md) | [进程、线程与协程](knowledge/systems/process-thread-coroutine.md) |
| 都在等锁，怎样区分[死锁](glossary/systems.md#systems.race-deadlock)与普通[排队](glossary/performance.md#performance.queueing) | [死锁与失败恢复](knowledge/systems/deadlocks-and-recovery.md) | [库存并发实验](knowledge/database/inventory-concurrency-lab.md) · [重试预算](knowledge/reliability/timeouts-and-retry-budgets.md) |
| 聊天记录还在，模型为什么忘了之前的条件 | [Token、上下文与记忆](knowledge/ai/tokens-context-and-memory.md) | [可恢复 Runtime](knowledge/ai/recoverable-runtime.md) |
| 回答有引用，为什么仍用错版本或扩大结论 | [RAG 与依据](knowledge/ai/rag-retrieval-and-grounding.md) | [Evals 与失败分析](knowledge/ai/evals-and-failure-analysis.md) · [对象级授权](knowledge/security/object-level-authorization.md) |
| 改完提示更顺了，怎样判断 AI 应用真的变好 | [Evals 与失败分析](knowledge/ai/evals-and-failure-analysis.md) | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) · [日志、指标与链路](knowledge/reliability/logs-metrics-and-traces.md) |
| HTML 已显示，框架为什么还没准备好处理交互 | [渲染与 Hydration](knowledge/frontend/rendering-and-hydration.md) | [浏览器长任务](knowledge/frontend/long-tasks-and-responsiveness.md) · [事件循环](knowledge/runtime/event-loop-and-microtasks.md) |
| 已退出登录，旧令牌为什么仍能访问 API | [认证、会话与令牌](knowledge/security/authentication-sessions-and-tokens.md) | [对象级授权](knowledge/security/object-level-authorization.md) |
| 列表请求都返回成功，翻页却重复或漏数据 | [HTTP 契约与分页](knowledge/api/contracts-and-pagination.md) | [索引与执行计划](knowledge/database/indexes-and-query-plans.md) · [事务隔离与 MVCC](knowledge/database/isolation-and-mvcc.md) |
| 建了索引，为什么仍然扫描全表 | [索引与执行计划](knowledge/database/indexes-and-query-plans.md) | [事务隔离与 MVCC](knowledge/database/isolation-and-mvcc.md) · [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 对象已经不用了，内存为什么还在增长 | [可达性与垃圾回收](knowledge/runtime/reachability-and-garbage-collection.md) | [事件循环与微任务](knowledge/runtime/event-loop-and-microtasks.md) |
| 指标显示接口变慢，日志却没有报错 | [日志、指标与链路](knowledge/reliability/logs-metrics-and-traces.md) | [慢 API 排查](knowledge/performance/slow-api-investigation.md) · [SLI/SLO](knowledge/reliability/slis-slos-and-error-budgets.md) |
| 改一个业务规则，为何多个模块都要修改 | [模块边界与依赖](knowledge/architecture/module-boundaries-and-dependencies.md) | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) |
| 提高并发后吞吐不升，[P99](glossary/performance.md#performance.percentiles) 却继续变长 | [延迟、吞吐与排队](knowledge/performance/latency-throughput-and-queues.md) | [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 同一事务两次读取，为什么结果不同 | [事务隔离与 MVCC](knowledge/database/isolation-and-mvcc.md) | [库存并发](knowledge/database/concurrent-inventory.md) |
| 已经 await，为什么输入与绘制仍在等待 | [事件循环与微任务](knowledge/runtime/event-loop-and-microtasks.md) | [浏览器长任务](knowledge/frontend/long-tasks-and-responsiveness.md) |
| 消费者处理成功，重启后却再次收到消息 | [消息投递与确认](knowledge/messaging/delivery-acknowledgements-and-idempotency.md) | [Outbox](knowledge/messaging/transactional-outbox.md) |
| 监控全绿，用户仍在投诉，[可靠性](glossary/reliability.md#reliability.availability)该怎样衡量 | [SLI、SLO 与错误预算](knowledge/reliability/slis-slos-and-error-budgets.md) | [延迟与排队](knowledge/performance/latency-throughput-and-queues.md) |
| 创建很多任务，为何计算仍未并行推进 | [进程、线程与协程](knowledge/systems/process-thread-coroutine.md) | [同步与阻塞](knowledge/runtime/async-and-blocking.md) |
| 页面打不开，应先区分解析、连接还是应用失败 | [HTTPS 请求链路](knowledge/networking/https-request-lifecycle.md) | [重试预算](knowledge/reliability/timeouts-and-retry-budgets.md) |
| 数据量增加后，重复查找为何越来越慢 | [复杂度与数据结构](knowledge/algorithms/complexity-and-data-structures.md) | [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 数据库已经改了，缓存为何还返回旧值 | [Cache-Aside 与失效](knowledge/cache-search/cache-aside-and-invalidation.md) | [一致性与复制](knowledge/distributed/consistency-and-replication.md) |
| 写入已成功，换个读取节点却看到旧值 | [一致性与复制](knowledge/distributed/consistency-and-replication.md) | [幂等性](knowledge/api/idempotency.md) |
| 恢复旧程序后，为何数据处理仍失败 | [构建、部署与回滚](knowledge/devops/build-deploy-rollback.md) | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) |
| 本地测试通过，为何真实依赖仍不兼容 | [测试层次与替身](knowledge/engineering/test-scopes-and-doubles.md) | [交付生命周期](knowledge/devops/build-deploy-rollback.md) |
| 写了 async，其他请求仍卡住 | [同步与阻塞](knowledge/runtime/async-and-blocking.md) | [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 客户端超时，不知道订单是否创建 | [幂等性](knowledge/api/idempotency.md) | [幂等实验](knowledge/api/idempotency-lab.md) |
| 业务表写成功，消息却没发出去 | [Outbox](knowledge/messaging/transactional-outbox.md) | [API 幂等性](knowledge/api/idempotency.md) |
| SQL 不慢，整个接口却很慢 | [慢 API 排查](knowledge/performance/slow-api-investigation.md) | [异步与阻塞](knowledge/runtime/async-and-blocking.md) |
| 超时后还该不该重试、最多等多久 | [重试预算](knowledge/reliability/timeouts-and-retry-budgets.md) | [幂等性](knowledge/api/idempotency.md) · [慢 API 排查](knowledge/performance/slow-api-investigation.md) |
| 库存只有一件，两个事务却都下单成功 | [库存并发](knowledge/database/concurrent-inventory.md) | [幂等性](knowledge/api/idempotency.md) · [Outbox](knowledge/messaging/transactional-outbox.md) |
| 用户已登录，修改 ID 却读到别人数据 | [对象级授权](knowledge/security/object-level-authorization.md) | [Agent 工具恢复](knowledge/ai/recoverable-runtime.md) |
| 页面已经显示，点击却迟迟没有反馈 | [浏览器长任务](knowledge/frontend/long-tasks-and-responsiveness.md) | [同步与阻塞](knowledge/runtime/async-and-blocking.md) |
| Agent 重启后不知道工具是否执行成功 | [可恢复 Runtime](knowledge/ai/recoverable-runtime.md) | [幂等性](knowledge/api/idempotency.md) · [Outbox](knowledge/messaging/transactional-outbox.md) |
| 同一内容应该放哪个分类 | [知识库 ADR](knowledge/architecture/knowledge-base-adr.md) | [知识地图](map.md) |

读完后回答四个问题：什么底层机制解释了现象？方案的边界如何设计？哪些证据能支持或推翻故障假设？选择这个方案承担了哪些成本？尚未执行的验证记录为下一步练习。

各领域的下一层待补机制见[概念路线图](handbook/concept-roadmap.md)。[查询计划](knowledge/database/query-plans-lab.md)与[浏览器长任务](knowledge/frontend/long-tasks-lab.md)已有独立实验；[库存并发](knowledge/database/inventory-concurrency-lab.md)也已实测；其他集成实验计划继续保留，实际证据状态以各篇说明为准。
