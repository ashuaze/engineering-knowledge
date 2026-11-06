# 三条主线的概念覆盖清单

本页逐项记录系统与网络、安全与 API、分布式与数据的当前阅读证据与下一步缺口。截至 2026-10-27，最近一次表内扩展新增信任/威胁、资源/输入与优雅关闭三项，共 53 项（19/17/17）；此前的策略/动态路由、路径 MTU、拥塞算法及 IPv6 源地址/接入四项继续保留。性能与交付六篇在表外说明，其他领域与算法入口见[概念路线图](concept-roadmap.md)。三个方向仍需继续积累，本页是当前优先清单，不是计算机学科全部概念的穷举。

“专题”表示已有正文专门解释该单元的核心问题、机制及失败边界；“关联”表示有相关章节或词汇解释，但尚未独立展开本行完整问题；“待专题”表示仍需系统成文。状态按本行明确范围判断，不把文章数量、术语链接数量或组内某个子概念完成当作整组完成。

概念解释与实测分开验收。下表的专题主要是来源核查和纸面推演；已有局部实验以各篇正文及验证记录为准，不能从“专题”推出真实故障、性能或集成已经验证。本文不计算覆盖百分比。

## 系统与网络

| 概念单元 | 当前阅读证据 | 尚需补充或深入 |
| --- | --- | --- |
| 进程、线程与协程 | 专题：[执行单元与调度边界](../knowledge/systems/process-thread-coroutine.md) | 具体 Runtime 调度、跨平台执行模型与真实资源成本 |
| 上下文切换与调度等待 | 本批专题：[任务切换、就绪与运行](../knowledge/systems/context-switches-run-queues-and-scheduling-delay.md) | 具体内核/策略/亲和性/配额配置、真实调度记录与直接/间接切换成本 |
| 栈堆、布局与对象寿命 | 本批专题：[映射、分配器与寿命](../knowledge/systems/process-memory-layout-stacks-heaps-and-lifetimes.md) | 具体 ABI/优化/allocator、栈保护/耗尽、RSS/碎片与跨线程寿命实测 |
| 地址空间、页与缓存 | 专题：[虚拟内存](../knowledge/systems/virtual-memory-pages-and-faults.md)、[CPU 缓存与局部性](../knowledge/systems/cpu-caches-locality-and-false-sharing.md) | 分配器、NUMA 与真实内存压力/缓存采集 |
| 竞态、锁与条件等待 | 专题：[原子性](../knowledge/systems/races-and-atomicity.md)、[同步原语](../knowledge/systems/locks-and-synchronization.md)、[死锁](../knowledge/systems/deadlocks-and-recovery.md) | 多条件取消、公平性及真实并发历史验证 |
| C++20 内存顺序与发布 | 专题：[内存顺序与原子操作](../knowledge/systems/memory-order-atomics-and-publication.md) | 其他语言模型、具体硬件映射与弱顺序反例验证 |
| 无锁算法与完成进度 | 本批专题：[线性化、整体完成与自身步骤](../knowledge/systems/lock-free-algorithms-linearization-and-progress.md) | 实际算法完整证明、帮助链、依赖进度、并发历史/模型检查及竞争负载实测 |
| ABA 与安全内存回收 | 本批专题：[保护、时代与宽限期](../knowledge/systems/safe-memory-reclamation-aba-hazards-and-epochs.md) | 具体 hazard/epoch/RCU 库与内存顺序、注册退出、逻辑复用、停滞容量及回调恢复实测 |
| 进程间数据交换 | 专题：[IPC、共享内存与所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md) | 具体 IPC 实现、进程故障恢复及跨平台差异验证 |
| 信号、取消与退出 | 专题：[信号与退出责任](../knowledge/systems/signals-cancellation-and-shutdown.md) | 实时信号、真实中断/摘流及期限后处置验证 |
| 内核入口、描述符与就绪 | 专题：[系统调用](../knowledge/systems/syscalls-privilege-and-return-contracts.md)、[描述符](../knowledge/systems/file-descriptors-and-open-file-descriptions.md)、[I/O 多路复用](../knowledge/systems/io-multiplexing-readiness-and-event-loops.md) | 异步 I/O 接口深入、真实关闭/取消和调度证据 |
| DNS、TCP/TLS 与 HTTP 连接 | 专题：[DNS](../knowledge/networking/dns-caching-and-address-selection.md)、[连接状态](../knowledge/networking/tcp-tls-and-connection-states.md)、[连接池](../knowledge/networking/http-reuse-pools-and-timeouts.md)、[流控与拥塞](../knowledge/networking/tcp-flow-control-and-congestion.md)；专题：[UDP 与 QUIC](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md) | 实际 QUIC/HTTP3/回退/迁移、抓包与跨代理切流实测；拥塞与队列见下列独立单元 |
| 网络分层与地址转发 | 专题：[网络分层、IP 与路由](../knowledge/networking/network-layers-ip-subnets-and-routing.md)；专题：[IPv6 与邻居发现](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) | 真实 IPv6 配置、邻居与转发；策略/收敛、MTU/反馈、源选择/接入见下列独立单元 |
| NAT、代理与 L4/L7 负载均衡 | 专题：[NAT、代理与负载均衡](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md) | 具体产品/拓扑的状态恢复、健康/保持/摘流、转发头与真实故障验证 |
| CDN 与 WAF | 专题：[CDN 与 WAF](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md) | 实际缓存键/权限/清除、源站限制、规则可见范围与误报/漏报、产品集成验证 |
| 策略、动态路由与收敛 | 本批专题：[策略与动态路由](../knowledge/networking/policy-routing-control-planes-and-convergence.md) | 具体 IGP/BGP 扩展与政策、设备软硬件下发、双向切流/现存连接实测 |
| 路径 MTU、隧道与大小探测 | 本批专题：[路径 MTU 与隧道](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md) | 具体隧道封装/分片、ICMP 校验过滤、跨路径探测/黑洞恢复及抓包实测 |
| 拥塞算法、队列与反馈 | 本批专题：[拥塞算法与队列管理](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md) | 具体算法版本/队列/ECN 配置、竞争公平性、吞吐与尾延迟对照 |
| IPv6 源地址、隐私与接入信任 | 本批专题：[IPv6 源地址、隐私与接入防护](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md) | 完整主机政策/多宿主、地址刷新、交换机解析/过滤、绑定与合法拓扑实测 |

## 安全与 API

| 概念单元 | 当前阅读证据 | 尚需补充或深入 |
| --- | --- | --- |
| 信任边界、最小权限与威胁分析 | 本批专题：[信任边界与威胁建模](../knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md) | 设备/会话及具体业务威胁、策略落实与有效性验证 |
| 资源、输入与字段写入 | 本批专题：[资源模型与输入边界](../knowledge/api/resource-models-input-validation-and-write-boundaries.md) | 具体资源/长任务协议、字段绑定及并发保存集成 |
| 关闭接纳、连接排空与结果 | 本批专题：[优雅关闭与请求排空](../knowledge/api/graceful-shutdown-draining-and-inflight-outcomes.md) | 真实就绪/端点传播、旧连接/长流、共享期限及超期恢复验证 |
| 身份、会话与联合登录 | 专题：[会话与令牌](../knowledge/security/authentication-sessions-and-tokens.md)、[OAuth/OIDC](../knowledge/security/oauth-oidc-and-pkce.md) | 设备/会话治理与真实身份、联合协议集成；MFA 见下列独立单元 |
| 多因子与认证器管理 | 专题：[MFA](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md) | 真实 OTP/WebAuthn/认证器绑定替换、恢复、升阶会话及并发消费验证 |
| 密码存储与账号恢复 | 专题：[口令派生、恢复与撤销](../knowledge/security/password-storage-and-account-recovery.md) | KDF 容量基准、恢复渠道治理及跨节点撤销验证 |
| 对象权限与租户范围 | 专题：[对象级授权](../knowledge/security/object-level-authorization.md)；专题：[权限模型与策略传播](../knowledge/security/authorization-models-policy-distribution-and-revocation.md) | 策略/事实治理及真实版本传播、缓存/撤销、并发执行和批量对象验证；跨服务委托见独立单元 |
| 同源、CORS 与 CSRF | 专题：[浏览器来源边界](../knowledge/security/origins-cors-and-csrf.md) | 双站点、代理及浏览器配置的集成对照 |
| XSS 与浏览器输出边界 | 专题：[上下文、危险汇与防线](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md) | 具体框架/净化器组合、浏览器支持与部署策略验证 |
| SSRF 与服务端请求边界 | 专题：[URL、解析与出口](../knowledge/security/ssrf-url-resolution-and-egress-boundaries.md) | 所用客户端、代理、DNS 和网络出口的集成验证 |
| Webhook 与消息认证 | 专题：[签名、重放与持久接纳](../knowledge/api/webhook-signatures-replay-and-delivery.md) | 各提供方协议接入、密钥轮换和故障重投对照 |
| HTTP 契约与接纳 | 专题：[契约分页](../knowledge/api/contracts-and-pagination.md)、[条件请求](../knowledge/api/conditional-requests-and-cache-validation.md)、[幂等](../knowledge/api/idempotency.md)、[额度](../knowledge/api/rate-limits-concurrency-and-quotas.md) | 具体资源协议、分布式配额与混合版本验证；资源/字段取舍见上方独立单元 |
| SQL 注入与查询构造 | 专题：[SQL 注入与参数化查询](../knowledge/security/sql-injection-parameters-and-query-structure.md)；输入类型另见[运行时校验](../knowledge/runtime/type-systems-and-runtime-validation.md) | 实际驱动/ORM/数据库组合、动态查询结构与授权/资源边界的集成验证 |
| 密钥与凭证生命周期 | 专题：[密钥与凭证生命周期](../knowledge/security/secrets-credentials-rotation-and-revocation.md) | 具体密钥/凭据服务的发放、轮换撤销、现存会话与恢复副本验证 |
| mTLS 与服务身份 | 专题：[mTLS 与服务身份](../knowledge/security/mtls-service-identities-and-trust-boundaries.md) | 具体 TLS/身份基础设施、策略与终止代理、现存连接及轮换撤销的集成验证 |
| 跨服务委托与调用上下文 | 专题：[跨服务委托](../knowledge/security/service-delegation-token-exchange-and-audience.md) | 具体 STS/profile/权限映射、密钥绑定、保证/撤销传播、缓存和任务恢复集成 |
| API 风格与网关 | 专题：[API 风格与网关](../knowledge/api/api-styles-contracts-and-gateway-boundaries.md) | 所选协议/库/网关的兼容、字段权限与成本、预算取消/重试、错误映射和流式恢复验证 |

## 分布式与数据

| 概念单元 | 当前阅读证据 | 尚需补充或深入 |
| --- | --- | --- |
| 一致性、复制与共识 | 专题：[一致性与复制](../knowledge/distributed/consistency-and-replication.md)、[共识与法定集合](../knowledge/distributed/consensus-leaders-and-quorums.md)；配套 [CAP 与 PACELC](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md)；专题：[共识成员变更与分区恢复](../knowledge/distributed/membership-changes-and-partition-recovery.md) | 实现特定的成员生效点/读写规则、正常等待、真实分区重连/快照恢复和外部执行者隔离验证 |
| 逻辑时间与因果 | 专题：[逻辑时钟与并发](../knowledge/distributed/logical-clocks-causality-and-concurrency.md)；本批专题：[HLC](../knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md) | 时钟界/传播/持久恢复、具体提交时间协议、因果上下文压缩、成员变动及真实传播验证 |
| 并发合并与收敛 | 本批专题：[CRDT](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md) | 其他类型/并发语义、权利分配、因果压缩/清理、成员与备份恢复及真实副本验证 |
| 键放置与节点变化 | 专题：[一致性哈希与再均衡](../knowledge/distributed/consistent-hashing-placement-and-rebalancing.md) | 成员视图、再均衡容量、迁移/接管与故障恢复实作 |
| 分区、分片与路由 | 专题：[分区、分片与数据路由](../knowledge/database/partitioning-sharding-and-data-routing.md) | 具体产品的路由/索引/约束、跨片查询与事务、热点及迁移协议验证 |
| 租约、心跳与执行隔离 | 专题：[租约与 Fencing](../knowledge/distributed/leases-heartbeats-and-fencing.md) | 跨故障域接管、真实旧执行者隔离和资源端验证 |
| 跨边界提交与补偿 | 专题：[2PC/Saga](../knowledge/distributed/two-phase-commit-sagas-and-recovery.md) | 产品资源支持、协调恢复及并发业务集成 |
| 消息、偏移与执行意图 | 专题：[确认](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md)、[偏移](../knowledge/messaging/partitions-consumer-groups-and-offsets.md)、[Outbox](../knowledge/messaging/transactional-outbox.md)；专题：[事件格式演进](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md) | 具体编码器/Registry/历史适配、混合发布/回退与回放副作用、重平衡、偏移事务及 relay 集成 |
| 变更捕获与源端连续性 | 本批专题：[CDC](../knowledge/database/cdc-snapshots-log-positions-and-replay.md) | 实际插件/快照配置、行键/删除/DDL、位点/目标共同恢复、槽保留与来源切换实测 |
| 读写职责、投影与事件历史 | 本批专题：[CQRS](../knowledge/architecture/cqrs-read-write-models-and-projection-lag.md)、[事件溯源](../knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md) | 真实投影延迟/补洞/重建切换、事件存储并发追加、快照、历史演进、隐私删除及副作用恢复验证 |
| 事件时间、窗口与迟到处理 | 本批专题：[事件时间与窗口](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md) | 真实来源水位、空闲分区、状态后端/恢复、迟到分布、会话合并与目标修订协议验证 |
| 数据模型与访问模式 | 专题：[数据模型与访问模式](../knowledge/database/data-models-and-access-patterns.md) | 图与其他模型、更高范式/复杂依赖、真实负载与复制维护的对照验证 |
| 并发、存储与恢复 | 专题：[隔离](../knowledge/database/isolation-and-mvcc.md)、[WAL](../knowledge/database/wal-and-crash-recovery.md)、[备份](../knowledge/database/backups-and-point-in-time-recovery.md)、[迁移](../knowledge/database/schema-migrations-and-compatibility.md) | 跨行历史、恢复链故障、跨故障域及大表回填验证 |
| 缓存读写与容量 | 专题：[Cache-Aside](../knowledge/cache-search/cache-aside-and-invalidation.md)、[淘汰](../knowledge/cache-search/lru-lfu-and-capacity-eviction.md)；专题：[缓存加载合并与惊群控制](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md)；专题：[写穿与异步写回](../knowledge/cache-search/write-through-write-behind-and-durability.md)；专题：[Redis 数据结构](../knowledge/cache-search/redis-data-types-operations-and-atomicity.md) | 实际 Redis 命令/事务/过期/槽位与恢复，待写接纳/版本/删除、共享加载/迟到回填及容量验证 |
| 对象、版本与限时访问 | 专题：[对象存储与预签名访问](../knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md) | 具体产品/SDK 的条件竞争、分段完成/清理、跨系统发布、权限/在途撤销与版本恢复验证 |
| 搜索投影、召回与切换 | 专题：[倒排](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md)、[向量](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md)、[融合重排](../knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md)、[索引重建](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) | 过滤、持续更新、质量标注与真实切换/资源对照 |
| 分布式标识生成 | 专题：[分布式 ID](../knowledge/distributed/distributed-identifiers-time-and-uniqueness.md) | 具体库/生成服务的时钟、身份复用、序列/随机状态、跨地域与恢复验证；数据库索引负载对照 |

## 下一轮怎样验收

本批补齐遗留八组入口：[BFF与前端适配](../knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)、[复制与读副本](../knowledge/distributed/consistency-and-replication.md)、[分布式锁与缓存租约](../knowledge/distributed/leases-heartbeats-and-fencing.md)、[队列、发布订阅与事件流](../knowledge/messaging/queues-pubsub-event-streams-and-retention.md)、[提示词与指令边界](../knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)、[温度、采样与复现](../knowledge/ai/temperature-sampling-and-reproducibility.md)、[MCP与能力协商](../knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)、[微调、蒸馏与评估](../knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md)。BFF、消息模型和AI四篇为六篇新增；复制/读副本及锁/租约复用既有分布式专题并增补，表内原有两项继续计数一次。现有313组词条均有正文关联，三线53项（19/17/17）不变；具体机制和实际验证仍按每行缺口判断。

工程与可靠性另有八个专题入口：[TDD与BDD](../knowledge/engineering/tdd-bdd-examples-and-feedback-loops.md)、[测试金字塔与证据组合](../knowledge/engineering/test-pyramids-risk-portfolios-and-coverage.md)、[设计文档与决策记录](../knowledge/engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md)、[规格驱动与验收追溯](../knowledge/engineering/specifications-contracts-traceability-and-acceptance.md)、[黄金路径与开发者体验](../knowledge/engineering/golden-paths-developer-experience-and-platform-feedback.md)、[RED与USE](../knowledge/reliability/red-use-service-signals-and-resource-evidence.md)、[可用性与可靠性](../knowledge/reliability/availability-reliability-and-observation-windows.md)、[混沌工程与受控故障](../knowledge/reliability/chaos-engineering-hypotheses-stop-conditions-and-recovery.md)。它们解释开发、验证、文档、规格、平台支持与观测/恢复证据，在三线表外说明，不重复增加表内53项（19/17/17）。具体工具、需求/模型对应、多窗口告警、开发体验和受控故障/业务恢复继续保留实现与实测缺口。

性能与交付另有六篇：[批处理与流水线](../knowledge/performance/batching-pipelining-and-amortized-waiting.md)、[热点与资源竞争](../knowledge/performance/hotspots-contention-and-serialized-service.md)、[容量规划与自动扩缩容](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md)、[集群入口与服务发现](../knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md)、[云网络与访问边界](../knowledge/devops/cloud-networks-subnets-routes-and-security-groups.md)、[可信制品与渐进发布](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md)。它们连接三线知识与容量、入口和发布，不另计三线表内项目；三线因新增安全/API三项达到53项（19/17/17）。具体协议/控制器/平台、负载、供应链策略及业务恢复仍待实际验证。

架构已有五个专题入口：[模块化单体与微服务](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)、[设计原则与抽象成本](../knowledge/architecture/design-principles-contracts-and-abstraction-costs.md)、[设计模式与协作契约](../knowledge/architecture/design-patterns-collaboration-and-semantic-boundaries.md)、[渐进替换与写入归属](../knowledge/architecture/strangler-fig-migration-write-authority-and-rollback.md)、[质量属性与架构决策](../knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md)。它们补充风格、抽象、迁移与评估，不另计入上方三线的 53 项；数据线已有的 CQRS/事件溯源仍按原行范围判断。具体模式/上下文映射、服务拆分、写入移交、质量与维护效果继续保留实现和实测缺口。

前端新增五个专题入口：[组件协调与 key](../knowledge/frontend/reconciliation-keys-and-component-identity.md)、[WebSocket/SSE 与断线补读](../knowledge/frontend/websocket-sse-reconnection-and-replay.md)、[Core Web Vitals 与体验证据](../knowledge/frontend/core-web-vitals-field-data-and-diagnostic-boundaries.md)、[Service Worker 与离线更新](../knowledge/frontend/service-workers-offline-caches-and-update-lifecycles.md)、[增量再生成与页面缓存](../knowledge/frontend/incremental-regeneration-revalidation-and-freshness.md)。它们覆盖浏览器与应用界面问题，不计入上方三条主线的 53 项；具体协调算法、真实通道补读、体验采集、离线写入和多层缓存更新仍有实现/验证缺口。

Runtime 已有五个专题入口：[编译、解释与 JIT](../knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md)、[异常传播](../knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md)、[序列化](../knowledge/runtime/serialization-representations-schemas-and-identity.md)、[跨语言调用](../knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md)、[语言虚拟机](../knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md)。它们补充执行和语言边界，不计入上方三条主线的 53 项；编译/退优化、清理/取消、混合编码、原生生命周期与宿主能力均保留实际验证缺口。

先从上表的缺口选择一个可回答问题，核对已有正文能否补章节；需要新文时，明确新增的是哪个机制及其边界。完成后逐行补证据和剩余项，不整行抹去仍未解释的子概念。跨领域学习次序见[概念路线图](concept-roadmap.md)。
