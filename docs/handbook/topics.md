# 选题与输出进度

从工程问题确定选题，再定位知识索引。优先考虑跨岗位常见问题、可验证的保证，以及能够与已有正文相互解释的主题。下表是内容进度，个人学习优先级仍可按任务调整。

## 当前阶段：概念正文优先

按跨领域核心概念分批覆盖 17 个领域，已有范围与余项见[概念补全路线图](concept-roadmap.md)。当前共有 201 篇正文，17 个领域均有概念正文；各批交付与验收见[更新计划](../../UPDATE_PLAN.md)。本批用六篇新文和两篇既有增补补齐八组词条，继续按机制深度与真实验证推进。

## 2026-10-27：遗留八组术语闭合

| 词条与正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [BFF与前端适配](../knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)（新增） | 客户端投影、聚合预算、部分结果、对象权限及私有缓存 | Newman/Azure核查；未部署BFF或测量时延 |
| [复制与读副本](../knowledge/distributed/consistency-and-replication.md)（复用增补） | 接收/耐久/回放/快照，读写分离、冲突、切主与备份 | Jepsen/PG18/DynamoDB重新核查；未部署复制或切主 |
| [分布式锁与缓存租约](../knowledge/distributed/leases-heartbeats-and-fencing.md)（复用增补） | 效率/正确性、条件释放持有标识、资源端代次与缓存回填 | etcd3.6/作者/Chubby/Redis重新核查；未运行锁或缓存竞争 |
| [队列、发布订阅与事件流](../knowledge/messaging/queues-pubsub-event-streams-and-retention.md)（新增） | 工作分担、独立订阅、保留/压缩、位置和外部效果 | RabbitMQ教程/Kafka4.1核查；未运行Broker |
| [提示词与指令边界](../knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)（新增） | 任务/资料/示例、角色和接口状态、外部指令及执行权限 | OpenAI Docs/OWASP核查；未调用模型或测试注入 |
| [温度、采样与复现](../knowledge/ai/temperature-sampling-and-reproducibility.md)（新增） | 正温度分布、top-k/top-p、贪心、种子与运行复现 | Transformers/原论文/PyTorch2.14核查；概率为纸面输入 |
| [MCP与能力协商](../knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)（新增） | 宿主/客户端/服务端、协商、原语、授权、错误及业务结果 | MCP2025-11-25核查；未连接服务器/资源/工具 |
| [微调、蒸馏与评估](../knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md)（新增） | 全量/LoRA、软目标/生成序列、数据划分、评估和成本 | Transformers/PEFT/原论文核查；未训练或评价模型 |

新增六篇概念、增补两篇已有分布式专题，累计201篇（188概念）；前端12篇、消息6篇、AI19篇。八组空词条挂接后，313/313组均有正文关联，没有新增术语组；这只是现有目录入口闭合，不是全部学科概念或实现完成。三线53项（19/17/17）不变；两个既有单元补章节，其余六篇表外说明。

## 2026-10-27：工程与可靠性

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [TDD与BDD](../knowledge/engineering/tdd-bdd-examples-and-feedback-loops.md) | 短反馈、行为发现、规则/例子/疑问与独立初始条件 | Beck/Cucumber核查；未运行开发或BDD循环 |
| [测试金字塔与证据组合](../knowledge/engineering/test-pyramids-risk-portfolios-and-coverage.md) | 风险组合、语句/分支、断言、变异及选择性执行范围 | Vocke/Coverage.py7.11.0/PIT核查；未量覆盖或变异 |
| [设计文档与决策记录](../knowledge/engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md) | 背景/取舍、征求意见、决定历史与交付证据 | Ubl/Rust/Nygard核查；未审批或实施方案 |
| [规格驱动与验收追溯](../knowledge/engineering/specifications-contracts-traceability-and-acceptance.md) | 目标/规格/设计、追溯、客户环境与变更验收 | NASA/Cucumber核查；未执行付款/追溯验收 |
| [黄金路径与开发者体验](../knowledge/engineering/golden-paths-developer-experience-and-platform-feedback.md) | 支持路径、模板/既有服务、反馈与任务时间分母 | CNCF/Backstage/GitHub研究核查；未测平台或因果收益 |
| [RED与USE](../knowledge/reliability/red-use-service-signals-and-resource-evidence.md) | 服务/资源、接纳/完成、错误/时长与分布聚合 | RED/Gregg/Prometheus核查；计数及分位数为纸面输入 |
| [可用性与可靠性](../knowledge/reliability/availability-reliability-and-observation-windows.md) | 时间/请求、连续存活、修复与业务正确性 | NIST/SRE核查；未测可用率或估计失效模型 |
| [混沌工程与受控故障](../knowledge/reliability/chaos-engineering-hypotheses-stop-conditions-and-recovery.md) | 稳态/扰动、对照/影响、停止/恢复及可推广范围 | 原则/AWS FIS/SRE核查；未注入故障或运行恢复 |

八组既有空词条挂接正文，没有新增术语组。工程质量已有13篇概念、可靠性9篇概念；共195篇正文、313组术语，305组关联、8组未挂接。八篇在三线表外说明，53项（19/17/17）保持不变；有入口不代表全部子概念和实测完成。后续继续补需求/模型对应、测试工具机制、平台维护、告警及真实故障恢复证据。

## 2026-10-26：安全/API、性能与交付遗漏

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [信任边界与威胁建模](../knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md) | 信任位置/身份/授权、最小权限、资产与威胁路径 | NIST/OWASP核查；未评估实际安全策略 |
| [资源模型与输入边界](../knowledge/api/resource-models-input-validation-and-write-boundaries.md) | 资源/动作/任务、校验、字段许可及写入条件 | AIP/OWASP核查；未运行字段绑定/并发写入 |
| [优雅关闭与请求排空](../knowledge/api/graceful-shutdown-draining-and-inflight-outcomes.md) | 摘流传播、本地接纳、旧连接、共享期限与不确定结果 | Kubernetes v1.36/RFC9113/gRPC核查；未排空真实流量 |
| [批处理与流水线](../knowledge/performance/batching-pipelining-and-amortized-waiting.md) | 合并/重叠/并行/事务、凑批等待、错误与在途上限 | Redis/PG18/SRE核查；18/6/7.5ms为纸面模型 |
| [热点与资源竞争](../knowledge/performance/hotspots-contention-and-serialized-service.md) | 热分区、串行锁、等待/持有、缓存行竞争及证据 | USE/Linux内核核查；分区/锁数值为纸面上界 |
| [容量规划与自动扩缩容](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md) | 请求成本、故障余量、水平/垂直与HPA反馈 | SRE/Kubernetes v1.36核查；未压测或运行HPA |
| [集群入口与服务发现](../knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md) | 普通/无头发现、控制/数据路径、路由绑定与目标许可 | Kubernetes v1.36/Gateway API核查；未部署控制器 |
| [云网络与访问边界](../knowledge/devops/cloud-networks-subnets-routes-and-security-groups.md) | VPC/子网/路由、NAT、SG/ACL和应用身份 | AWS官方资料核查；未创建网络/规则 |
| [可信制品与渐进发布](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md) | 摘要/受信来源、构建期望、渐进暴露/观察及业务回退 | SLSA v1.2/Sigstore/Argo/Kubernetes核查；未验签或发布 |

补十三组既有空入口，新增制品摘要/构建来源一组；安全14篇、API9篇（8概念/1实验）、性能10篇（8概念/1案例/1实验）、交付7篇。三线清单增加信任/威胁、资源/输入与关闭三项，共53项（19/17/17）；性能及交付六篇在表外说明，不据此宣布所有概念或实际验证完成。

## 2026-10-26：架构边界、抽象与演进

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [模块化单体与微服务](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md) | 模型/代码/数据/部署、独立演进、共同事务与部分失败 | Fowler/Lewis 原文核查；未部署或比较运行成本 |
| [设计原则与抽象成本](../knowledge/architecture/design-principles-contracts-and-abstraction-costs.md) | SOLID、KISS/DRY/YAGNI、行为契约与抽象成本 | 作者原文/原始研究核查；未重构或证明完整替换关系 |
| [设计模式与协作契约](../knowledge/architecture/design-patterns-collaboration-and-semantic-boundaries.md) | 策略/适配/装饰/观察、语义映射、组合顺序与订阅寿命 | GoF 节选、Cockburn 与 JDK25核查；未运行模式实现 |
| [渐进替换与写入归属](../knowledge/architecture/strangler-fig-migration-write-authority-and-rollback.md) | 渐进入口、翻译、快照/日志、强制隔离与回退阶段 | 迁移作者与AWS说明核查；移交与回退为教学推演 |
| [质量属性与架构决策](../knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md) | 六部分场景、敏感/权衡/风险、预算/分布与ADR历史 | CMU/SEI及Nygard核查；未执行正式ATAM或实际评估 |

五组原有空词条（设计原则、模块化单体、微服务、模式、渐进替换）挂正文，沿用 ADR 并新增质量属性场景。架构已有 11 篇（10 概念、1 决策记录）。本批五篇在三线清单外说明，50 项统计保持不变；具体算法/模式、复杂上下文映射、迁移/维护收益与真实质量评估继续积累。

## 2026-10-26：前端身份、实时恢复与新鲜度

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [组件协调与 key](../knowledge/frontend/reconciliation-keys-and-component-identity.md) | 描述/协调/提交、父级/类型/key、索引错配与主动重置 | React/Vue 官方公开语义核查；未运行组件或性能测试 |
| [WebSocket/SSE 与断线补读](../knowledge/frontend/websocket-sse-reconnection-and-replay.md) | 通道方向、本地缓冲/SSE 标识、连续补读、快照与授权 | WHATWG/RFC 核查；恢复协议为设计，未连接或注入故障 |
| [Core Web Vitals 与体验证据](../knowledge/frontend/core-web-vitals-field-data-and-diagnostic-boundaries.md) | LCP/INP/CLS、阶段与窗口、真实分布及实验室边界 | web.dev 定义核查；数字为纸面输入，未采集本站指标 |
| [Service Worker 与离线更新](../knowledge/frontend/service-workers-offline-caches-and-update-lifecycles.md) | 注册/安装/等待/激活、Cache API、资源版本与待同步写入 | 固定 SW 草案、开发者与存储标准核查；未注册 Worker |
| [增量再生成与页面缓存](../knowledge/frontend/incremental-regeneration-revalidation-and-freshness.md) | 时间/按需再验证、后台替换/失败保留、缓存层与多实例 | Next.js 未启用 Cache Components 模型核查；未运行再生成 |

三组既有空入口（协调、实时通信、体验指标）挂接专题；沿用离线与渲染策略两组并新增组件身份一组。前端现有 11 篇（10 概念、1 实验）。前端五篇与 Runtime 一样不计入三线的 50 项，具体框架算法、浏览器/代理恢复、真实指标与离线/缓存一致性验证继续保留。

## 2026-10-26：网络选路、大小、拥塞与接入

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [策略与动态路由](../knowledge/networking/policy-routing-control-planes-and-convergence.md) | RPDB、RIB/FIB、BGP 本地策略、收敛阶段与现存连接 | Linux 手册与 RFC 核查；双出口和切换为推演，未运行路由实验 |
| [路径 MTU 与隧道](../knowledge/networking/path-mtu-icmp-tunnels-and-black-holes.md) | 链路/路径 MTU、MSS、隧道首部、ICMP、PLPMTUD 与黑洞 | 固定 RFC 核查；字节预算和探测时序为推演，未发包 |
| [拥塞算法与队列管理](../knowledge/networking/congestion-algorithms-aqm-and-ecn.md) | cwnd/pacing、BDP/队列、Reno/CUBIC/BBR 思路、AQM/调度/ECN | RFC 与开发者资料核查；未对特定算法版本或配置跑分 |
| [IPv6 源地址、隐私与接入防护](../knowledge/networking/ipv6-source-selection-privacy-and-first-hop-protection.md) | 源/目的组合、稳定/临时地址、寿命、DAD、RA Guard 与源验证 | 固定 RFC 核查；未更改主机地址或测试交换机过滤 |

新增六组术语关联正文。[三条主线清单](concept-coverage.md)扩展为 50 项（系统网络 19、安全 API 14、分布式数据 17）。网络领域现有 15 篇正文（14 篇概念、1 篇实验），仍保留具体协议/设备与真实转发、故障和安全验证缺口。

## 2026-10-26：系统调度、对象寿命与并发进度

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [上下文切换与调度等待](../knowledge/systems/context-switches-run-queues-and-scheduling-delay.md) | 运行/就绪/睡眠、权限入口/任务切换/迁移、计数与时长 | Linux/EEVDF/perf 文档核查；时间线为推演，未执行采集 |
| [栈堆与内存布局](../knowledge/systems/process-memory-layout-stacks-heaps-and-lifetimes.md) | 映射/分配器/对象、存储期/寿命、线程栈与 RSS | Linux/glibc 与 C++20 固定草案核查；未执行布局或寿命实验 |
| [无锁算法与进度保证](../knowledge/systems/lock-free-algorithms-linearization-and-progress.md) | 线性化、整体进度、单次步骤、CAS/帮助及完整路径 | 原始论文与 C++20 核查；计数模型非生产实现，未执行并发验证 |
| [ABA 与安全内存回收](../knowledge/systems/safe-memory-reclamation-aba-hazards-and-epochs.md) | 退役/回收、逻辑/地址 ABA、hazard/epoch/RCU、容量与退出 | 原论文/提案与内核文档核查；未执行回收库或故障实验 |

补齐上下文切换、栈堆两组原有空入口，新增进度保证与安全回收两组术语。[三条主线清单](concept-coverage.md)新增四行，共 46 项（系统网络 15、安全 API 14、分布式数据 17）。系统后续可补分配器/碎片、NUMA 与异步 I/O；数据与 Runtime 既有候选继续保留。

## 2026-10-23：Runtime 执行与跨边界语义

| 正文 | 本批覆盖 | 证据状态 |
| --- | --- | --- |
| [编译、解释与 JIT](../knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md) | 表示与时机、分层编译、反馈/守卫/退优化、完整性能成本 | V8 历史设计、CPython 3.13 与 Clang 资料核查；未执行编译或跑分 |
| [异常传播](../knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md) | 调用栈、finally 覆盖、异步拒绝、取消、资源与业务恢复 | ECMAScript 与 Python 3.13 核查；未执行故障注入 |
| [序列化](../knowledge/runtime/serialization-representations-schemas-and-identity.md) | 数值精度、存在性、对象图、字段身份、字节与语义身份 | RFC 8259、Protobuf、WHATWG 与 pickle 文档核查；未执行编解码 |
| [跨语言调用](../knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md) | ABI/布局、借用/转移、回调/线程、展开、Wasm 偏移与视图 | Rust、Node.js 24.16.0 中的 Node-API 与 Wasm JS 资料核查；未执行原生集成 |
| [语言虚拟机](../knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md) | 引擎/Runtime/宿主、帧/装载、模块/实例、能力与隔离 | JVMS 25、Wasm 核心及 Node 24.16.0 核查；未执行 VM/宿主验证 |

五组原有术语均已有专题入口；独立读者核对问题与算例，导航和旧文只扩充关联。Runtime 后续可补对象模型/动态分派、调用帧与协程续体深入，并积累编译、异常、编码与跨语言实际证据。数据线的查询执行/优化与图模型继续列为候选。

## 2026-10-23：读写投影、事件历史与流处理时间

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [CQRS](../knowledge/architecture/cqrs-read-write-models-and-projection-lag.md) | 命令/查询职责、同库/分库存储、投影版本、读己之写与重建切换 | 一手来源核查；版本和流程为纸面推演，未执行真实集成 |
| [事件溯源](../knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md) | 权威事件流、预期版本追加、快照、确定性重放、投影与历史演进 | 一手来源核查；账户流为纸面推演，未执行真实集成 |
| [事件时间与窗口](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md) | 事件/处理时间、窗口、触发、水位、允许迟到及多分区进度 | 一手论文与官方文档核查；时间线为纸面推演，未执行真实作业 |

[覆盖清单](concept-coverage.md)新增读写职责与事件历史、事件时间与窗口两单元；范围、故障与性能仍按各篇证据核对。数据方向后续转向查询执行/优化、图数据模型和相关真实集成；原 Runtime 四项候选已由上方五篇完成概念入口，后续深入对象模型与调用帧/协程续体。

## 2026-10-23：分布式时间、合并与变更流

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [HLC](../knowledge/distributed/hybrid-logical-clocks-and-timestamp-boundaries.md) | 物理分量与逻辑计数、单向因果、偏差/恢复及安全读取边界 | 一手来源核查；例子为纸面推演，未执行真实集成 |
| [CRDT](../knowledge/distributed/crdts-convergence-and-concurrent-merge-semantics.md) | 状态/操作传播条件、贡献计数、观察删除、历史清理与业务不变量 | 一手来源核查；例子为纸面推演，未执行真实集成 |
| [CDC](../knowledge/database/cdc-snapshots-log-positions-and-replay.md) | 配对快照、源端事务/位点、删除载荷、重复处理及保留恢复 | 一手来源核查；例子为纸面推演，未执行真实集成 |

[覆盖清单](concept-coverage.md)扩充 HLC，新增 CRDT 和 CDC 独立单元；范围、故障与性能仍按各篇证据核对。本批后续候选已经由上方读写投影、事件历史与流处理时间单元完成。

## 2026-10-23：算法推理与身份委托

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [分治与回溯](../knowledge/algorithms/divide-and-conquer-backtracking-and-pruning.md) | 子问题契约、递归分层、选择撤销、可行性剪枝与最优上下界 | 一手来源核查；纸面推演，未执行算法/认证/委托集成实验 |
| [字符串匹配](../knowledge/algorithms/string-matching-prefix-functions-and-text-boundaries.md) | 精确子串契约、前缀函数/失败链接、线性计数及编码转换边界 | 一手来源核查；纸面推演，未执行算法/认证/委托集成实验 |
| [MFA](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md) | 因子与UP/UV、OTP挑战、注册恢复、升阶与会话保证 | 一手来源核查；纸面推演，未执行算法/认证/委托集成实验 |
| [跨服务委托](../knowledge/security/service-delegation-token-exchange-and-audience.md) | 主体/执行者/受众、令牌交换、权限收窄与生命周期 | 一手来源核查；纸面推演，未执行算法/认证/委托集成实验 |

路线图扩充分治、回溯与字符串匹配；[三条主线清单](concept-coverage.md)新增 MFA 和跨服务委托单元，保留真实实现与集成缺口。当时提出的 Runtime 候选已由上方五篇补齐概念入口。

## 2026-10-23：地址、权限与存储

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [IPv6 与邻居发现](../knowledge/networking/ipv6-addresses-slaac-and-neighbor-discovery.md) | 地址范围与 zone、SLAAC/DAD、A/L/默认路由分工及邻居寿命 | 一手来源核查；纸面推演，未执行主机/权限/存储集成实验 |
| [权限模型与策略传播](../knowledge/security/authorization-models-policy-distribution-and-revocation.md) | RBAC/ABAC/ReBAC、判定与执行、规则/事实传播及撤销窗口 | 一手来源核查；纸面推演，未执行主机/权限/存储集成实验 |
| [Redis 数据结构](../knowledge/cache-search/redis-data-types-operations-and-atomicity.md) | 操作语义、读写成本、原子执行、过期/槽位与业务恢复 | 一手来源核查；纸面推演，未执行主机/权限/存储集成实验 |
| [对象存储与预签名访问](../knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md) | 键/版本/校验、单键与发布、分段完成、签名能力与撤销 | 一手来源核查；纸面推演，未执行主机/权限/存储集成实验 |

[覆盖清单](concept-coverage.md)扩充对应机制，新增对象/版本/限时访问单元；真实协议、传播、容量、条件竞争及故障恢复仍待分别验证。分治、回溯、字符串匹配、MFA 与跨服务委托的概念已在后续批次补充；真实实现和系统集成仍分别积累。

## 2026-10-23：写入、传输与事件演进

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [写穿与异步写回](../knowledge/cache-search/write-through-write-behind-and-durability.md) | 写入接纳/后端提交、状态合并、版本删除与有界写回恢复 | 一手来源核查；纸面推演，未执行缓存/网络/消息集成实验 |
| [UDP 与 QUIC](../knowledge/networking/udp-quic-streams-and-delivery-boundaries.md) | 数据报/流边界、丢失与资源控制、握手重放、地址与业务身份 | 一手来源核查；纸面推演，未执行缓存/网络/消息集成实验 |
| [事件格式演进](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md) | 事件身份、读写版本矩阵、历史适配与回放副作用边界 | 一手来源核查；纸面推演，未执行缓存/网络/消息集成实验 |

[覆盖清单](concept-coverage.md)补上对应机制，继续保留真实待写接纳与恢复、网络握手/迁移/回退，以及编码器/Registry/历史回放集成。IPv6、权限模型、Redis 数据结构与对象存储的概念已在后续批次补充，真实主机/权限/存储证据继续积累。

## 2026-10-22：边缘、加载与成员恢复

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [CDN 与 WAF](../knowledge/networking/cdn-edge-caches-and-waf-boundaries.md) | 缓存键与身份范围、边缘失效、WAF 可见性及受控回源 | 一手来源核查；纸面推演，未部署或执行产品/负载/集群实验 |
| [缓存加载合并与惊群控制](../knowledge/cache-search/cache-load-coalescing-and-stampedes.md) | 同键共享加载、等待/取消、跨实例与总容量、迟到回填 | 一手来源核查；纸面推演，未部署或执行产品/负载/集群实验 |
| [共识成员变更与分区恢复](../knowledge/distributed/membership-changes-and-partition-recovery.md) | 配置交叠、追赶/提升、分区重连与永久失多数恢复 | 一手来源核查；纸面推演，未部署或执行产品/负载/集群实验 |

[覆盖清单](concept-coverage.md)补上对应机制，写穿/异步写回、UDP/QUIC 的概念已在后续批次补充；IPv6、具体恢复协议和实际产品验证仍保留。

## 2026-10-22：mTLS、服务身份与 API 入口

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [mTLS 与服务身份](../knowledge/security/mtls-service-identities-and-trust-boundaries.md) | 双向证书校验、信任与身份匹配、逐跳调用及轮换接受范围 | 一手资料核查；纸面推演，未执行证书/协议/网关实验 |
| [API 风格与网关](../knowledge/api/api-styles-contracts-and-gateway-boundaries.md) | REST/RPC/GraphQL/gRPC 契约差异、网关治理与执行服务责任 | 一手资料核查；纸面推演，未执行证书/协议/网关实验 |

[覆盖清单](concept-coverage.md)补上两组专题入口，继续保留实际身份基础设施、策略、轮换撤销、协议兼容与调用故障验证。CDN/WAF、缓存加载合并与共识成员变更的概念已在后续批次补充，具体产品与集成证据仍待积累。

## 2026-10-22：CAP/PACELC 与分布式 ID

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [CAP 与 PACELC](../knowledge/distributed/cap-pacelc-and-operation-guarantees.md) | 线性一致、形式可用性、断联历史与正常复制的等待取舍 | 一手资料核查；纸面推演，未执行集群或生成器实验 |
| [分布式 ID](../knowledge/distributed/distributed-identifiers-time-and-uniqueness.md) | 唯一性范围、时间排序、节点/序列状态、UUIDv4/v7 与 ULID | 一手资料核查；纸面推演，未执行集群或生成器实验 |

[覆盖清单](concept-coverage.md)保留成员变更、具体复制/读写策略、时钟与节点身份恢复及跨地域验证；不能由理论边界或编号格式推出整个系统已验证。

## 2026-10-22：数据模型、分区与分片

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [数据模型与访问模式](../knowledge/database/data-models-and-access-patterns.md) | 逻辑模型、约束与访问模式、函数依赖、规范化/复制维护、OLTP/OLAP | 一手资料核查；纸面推演，未执行数据库或集群实验 |
| [分区、分片与数据路由](../knowledge/database/partitioning-sharding-and-data-routing.md) | 范围/哈希/目录、分片键、裁剪与扇出、局部约束和迁移接管 | 一手资料核查；纸面推演，未执行数据库或集群实验 |

[覆盖清单](concept-coverage.md)将模型与分片分别记录，保留更高范式、图模型、CAP/PACELC、标识生成及产品/负载验证等余项；不从词条或文章数推出全域完成。

## 2026-10-22：查询构造与凭证生命周期

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [SQL 注入与参数化查询](../knowledge/security/sql-injection-parameters-and-query-structure.md) | 值/语法分离、标识符与允许映射、驱动/ORM/动态 SQL、授权与计划边界 | 一手资料核查；教学示例，未执行真实服务集成实验 |
| [密钥与凭证生命周期](../knowledge/security/secrets-credentials-rotation-and-revocation.md) | 生成与分发、受限使用、版本轮换、撤销生效、信封加密与动态凭证边界 | 一手资料核查；教学示例，未执行真实服务集成实验 |

SQL 与凭证生命周期建立独立专题；[覆盖清单](concept-coverage.md)将 mTLS/服务身份单列待专题，API 风格、网关和 MFA 继续保留缺口。

## 2026-10-22：网络分组转发与入口边界

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [网络分层、IP 与路由](../knowledge/networking/network-layers-ip-subnets-and-routing.md) | 协议职责、CIDR/子网、下一跳、最长前缀、逐跳封装与返回路径 | 一手资料核查；纸面推演，未执行网络集成实验 |
| [NAT、代理与负载均衡](../knowledge/networking/nat-proxies-and-l4-l7-load-balancing.md) | 地址转换、连接边界、L4/L7、TLS、健康检查、保持与摘流 | 一手资料核查；纸面推演，未执行网络集成实验 |

分层/地址转发和 NAT/代理/负载均衡已有独立专题；[覆盖清单](concept-coverage.md)将 CDN/WAF 单列为待补，不随入口主题一并视为完成。

## 2026-10-22：共享状态、安全边界与分布式模型

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [IPC 与共享所有权](../knowledge/systems/ipc-channels-shared-memory-and-ownership.md) | 字节/消息边界、共享内存、同步、背压与所有权 | 一手资料核查；纸面推演，未执行集成实验 |
| [内存顺序与原子操作](../knowledge/systems/memory-order-atomics-and-publication.md) | 语言模型、读写顺序、发布条件与 CAS 进度边界 | 一手资料核查；纸面推演，未执行集成实验 |
| [XSS 与浏览器输出边界](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md) | 上下文、危险汇、净化、CSP 与 Trusted Types | 一手资料核查；纸面推演，未执行集成实验 |
| [SSRF 与服务端请求边界](../knowledge/security/ssrf-url-resolution-and-egress-boundaries.md) | 解析、DNS、实际连接、重定向及出口控制 | 一手资料核查；纸面推演，未执行集成实验 |
| [逻辑时钟与因果顺序](../knowledge/distributed/logical-clocks-causality-and-concurrency.md) | happened-before、Lamport、向量比较及并发 | 一手资料核查；纸面推演，未执行集成实验 |
| [一致性哈希与再均衡](../knowledge/distributed/consistent-hashing-placement-and-rebalancing.md) | 环、虚拟节点、成员视图、复制放置与迁移责任 | 一手资料核查；纸面推演，未执行集成实验 |

三路并行完成并交叉读审；[覆盖清单](concept-coverage.md)逐项保留尚未展开或实测的边界，不把文章关联数当作学科完成度。

## 2026-10-22：系统网络、安全 API 与分布式数据

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [信号、取消与退出](../knowledge/systems/signals-cancellation-and-shutdown.md) | 递送、掩码、待决、处理限制与正常退出责任 | 一手资料核查；纸面示例，未运行集成实验 |
| [TCP 流量控制与拥塞控制](../knowledge/networking/tcp-flow-control-and-congestion.md) | 接收窗口、拥塞窗口、在途数据与重传证据 | 一手资料核查；纸面示例，未运行集成实验 |
| [密码存储与账号恢复](../knowledge/security/password-storage-and-account-recovery.md) | 口令派生、成本迁移、恢复证明和会话撤销 | 一手资料核查；纸面示例，未运行集成实验 |
| [Webhook 签名与防重放](../knowledge/api/webhook-signatures-replay-and-delivery.md) | 签名覆盖、原始字节、时间窗口、重放与持久接纳 | 一手资料核查；纸面示例，未运行集成实验 |
| [2PC、Saga 与补偿恢复](../knowledge/distributed/two-phase-commit-sagas-and-recovery.md) | 准备与决议、恢复阻塞、本地提交和补偿责任 | 一手资料核查；纸面示例，未运行集成实验 |
| [索引重建与切换](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) | 快照切点、增量水位、删除版本、发布与回退 | 一手资料核查；纸面示例，未运行集成实验 |

三路分别核查一手资料、编写正文并交叉复核，之后统一整合术语和阅读入口。复核、构建与页面检查不扩展为生产机制已实测。

## 2026-10-22：开发与生产反馈概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [测试稳定性与隔离](../knowledge/engineering/flaky-tests-isolation-and-evidence.md) | 共享状态、时间/随机、顺序/并行、重试与首轮证据 | pytest、Playwright 核查；未运行套件治理实验 |
| [主干开发与功能开关](../knowledge/engineering/trunk-based-development-and-feature-flags.md) | 小批集成、反馈、默认值、数据兼容及清理 | DORA、Hodgson、OpenFeature 核查；未发布或分流 |
| [事故响应与复盘](../knowledge/reliability/incident-response-recovery-and-postmortems.md) | 分工/交接、止损/恢复、时间线和效果验证 | Google SRE 核查；未处置真实事故 |
| [IaC 与状态漂移](../knowledge/devops/iac-state-drift-and-change-plans.md) | 配置/状态/观测、计划、锁、归属和敏感数据 | HashiCorp 核查；未运行 Terraform 或云操作 |

本批继续概念优先，区分反馈信号、配置控制、业务验收及变更状态；复查和站点检查仅验证知识库内容。

## 2026-10-20：工程维护概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [技术债与重构](../knowledge/architecture/technical-debt-refactoring-and-behavior.md) | 行为保持、现状记录、收益估计与渐进替换 | Fowler 一手资料核查；金额/工时未实测 |
| [静态分析与告警](../knowledge/engineering/static-analysis-rules-and-findings.md) | 规则、范围、模型、误报/漏报、基线与抑制 | ESLint、TypeScript、CodeQL 核查；未扫描 |
| [代码评审与小步变更](../knowledge/engineering/code-review-context-and-change-boundaries.md) | 上下文、完整单元、分工与版本证据 | Google Engineering Practices 核查；未发送真实评审 |
| [依赖锁定与 SBOM](../knowledge/engineering/dependency-resolution-lockfiles-and-sbom.md) | 解析/安装/交付、身份、清单、来源与兼容 | npm 11、SemVer、CycloneDX、SLSA v1.2 等核查；未安装/升级 |

本批继续概念优先，区分工具与清单声明、实际代码事实、业务行为和交付结果；不用全绿、批准、锁文件或签名文本代替完整验证。

## 2026-10-20：算法进阶概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [加权最短路与松弛](../knowledge/algorithms/weighted-shortest-paths-and-relaxation.md) | DAG/Dijkstra/Bellman-Ford、确认、负环与实现成本 | MIT 6.006 来源核查；边集和距离为推演 |
| [贪心选择与交换论证](../knowledge/algorithms/greedy-choices-and-exchange-arguments.md) | 可行/最优、区间选择、安全交换与契约反例 | MIT 6.046J 来源核查；区间、收益和币种未执行 |
| [动态规划与状态设计](../knowledge/algorithms/dynamic-programming-states-and-dependency-order.md) | 状态、依赖、0/1 背包、压缩/恢复及伪多项式 | MIT 6.006 来源核查；表格与伪代码未执行 |
| [并查集与最小生成树](../knowledge/algorithms/union-find-components-and-minimum-spanning-trees.md) | 代表、压缩、摊还、Kruskal 与割性质 | MIT 6.046J 来源核查；分组和选边为推演 |

本批继续概念优先，先固定优化目标、合法性和计算模型，再解释不变量、正确性与完整成本；没有把抽象最优解当作真实调度或网络的性能保证。

## 2026-10-20：系统性能基础概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [CPU 缓存与局部性](../knowledge/systems/cpu-caches-locality-and-false-sharing.md) | 层级、缓存行、工作集、访问顺序与伪共享 | CMU 与 Linux 来源核查；块访问为推演 |
| [CPU 利用率、负载与配额](../knowledge/performance/cpu-time-utilization-load-and-quotas.md) | 经过/CPU 时间、分母、调度等待、带宽与 PSI | Linux man-pages、内核和利用率分析核查；未采集指标 |
| [Profiling 与火焰图](../knowledge/performance/profiling-stacks-and-flame-graphs.md) | 采样/插桩、累计/自身、执行/等待与观测偏差 | perf 与火焰图作者资料核查；1000 样本为教学设计 |
| [基准测试与加速比](../knowledge/performance/benchmarks-workloads-and-speedup.md) | 相同契约、冷暖/重复、负载与 Amdahl 上限 | Google Benchmark、LLVM、Python 3.13 与 Cornell 核查；未跑基准 |

本批继续概念优先，把定义、分母、模型假设与实际测量区分开；不从未命中次数、CPU 宽度或局部加速直接推出请求延迟收益。

## 2026-10-20：向量索引与混合召回概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [向量索引与近似检索](../knowledge/cache-search/vector-indexes-metrics-and-approximate-search.md) | 空间/距离、精确基线、HNSW/IVF/PQ、过滤与近邻 Recall | Faiss/HNSW、pgvector 0.8.7 核查；坐标与集合未执行 |
| [混合召回与重排](../knowledge/cache-search/hybrid-retrieval-fusion-and-reranking.md) | 身份去重、分数/排名融合、RRF、截断、Cross-Encoder 与评价 | RRF 论文、Elastic、Sentence Transformers、教材核查；排名为推演 |

本批继续概念优先，区分精确近邻、业务相关性和来源支持，分别记录各路深度、融合窗口、重排输入与最终预算；没有实测向量或模型效果。

## 2026-10-20：存储与全文检索概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [LSM、SSTable 与压缩合并](../knowledge/database/lsm-sstables-and-compaction.md) | WAL/内存表/Flush、版本与删除、合并、放大及停写 | LevelDB/RocksDB 文档核查；序列和字节比未执行 |
| [倒排索引与全文检索](../knowledge/cache-search/inverted-indexes-analysis-and-relevance.md) | 词项与倒排表、布尔/短语、分词、TF/DF 与排序 | 信息检索教材及 PostgreSQL 18 核查；倒排表与结果为推演 |

本批继续概念优先，区分存储组织、检索语义、排序及当前访问许可；未将合并完成或词项命中当作完整业务正确性证据。向量索引与混合召回的概念入口见上节，具体索引和模型实测仍待补。

## 2026-10-20：索引与缓存结构概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [B/B+ 树与页索引](../knowledge/algorithms/b-trees-bplus-trees-and-page-indexes.md) | 扇出、叶载荷、范围扫描、分裂及回表边界 | NIST/CMU、PostgreSQL 18 核查；页图未执行 |
| [Trie 与前缀检索](../knowledge/algorithms/tries-prefix-search-and-key-encoding.md) | 终止标记、前缀查询、编码、压缩与删除 | NIST/CMU/Princeton、Unicode 核查；路径未执行 |
| [Bloom Filter 与成员判断](../knowledge/cache-search/bloom-filters-membership-and-synchronization.md) | 共享位、误报、容量、删除及覆盖同步 | CMU、作者综述与 Redis 文档核查；位图和概率为推演 |
| [LRU/LFU 与缓存淘汰](../knowledge/cache-search/lru-lfu-and-capacity-eviction.md) | 新近/频次、维护成本、近似、容量与有效性 | Python 3.13、LFU 论文及 Redis 核查；访问序列未执行 |

本批继续概念优先，区分结构本身的查询规则与数据同步、权限和业务结果；误报目标、低树高或高命中率均不视为完整系统正确性证明。

## 2026-10-20：算法与数据结构概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [线性结构与端点操作](../knowledge/algorithms/sequences-stacks-queues-and-deques.md) | 接口与表示、定位/移动、扩容摊还、FIFO/LIFO 与容量 | MIT、Python 3.13 核查；任务与搬移算例未执行 |
| [哈希表与键契约](../knowledge/algorithms/hash-tables-collisions-and-key-contracts.md) | 哈希与相等、碰撞、负载、扩容与重复键 | MIT、Python 3.13/Java 21 核查；未执行分布或碰撞实验 |
| [排序与二分查找](../knowledge/algorithms/sorting-binary-search-and-boundaries.md) | 稳定性、顺序契约、半开区间、上下界和维护成本 | MIT、Python 3.13 核查；lower_bound 未执行 |
| [树、堆与优先队列](../knowledge/algorithms/trees-heaps-and-priority-queues.md) | 搜索与平衡、局部堆序、Top-K、并列和优先级变更 | MIT、Python 3.13/Java 21 核查；树形与候选为推演 |
| [图遍历与依赖顺序](../knowledge/algorithms/graphs-traversal-and-dependency-order.md) | 表示、BFS/DFS、边数距离、环与拓扑完成 | MIT、Python 3.13 核查；图与执行流程未运行 |

本批继续概念优先，按完整操作、不变量与输出语义分析成本；没有将算法模型等同于真实耗时，也未将图中的计划顺序当作业务已完成。

## 2026-10-20：系统内存与 I/O 概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [虚拟内存与缺页](../knowledge/systems/virtual-memory-pages-and-faults.md) | 地址映射、页表/TLB、驻留、缺页、写时复制与工作集 | Linux 内核及 man-pages 核查；地址和触页时序未执行 |
| [系统调用与权限边界](../knowledge/systems/syscalls-privilege-and-return-contracts.md) | 库与 ABI、权限与调度、返回进度、错误和完成范围 | Linux man-pages 核查；未运行跟踪或短读写实验 |
| [文件描述符与打开文件描述](../knowledge/systems/file-descriptors-and-open-file-descriptions.md) | 资源引用、共享偏移、复用、关闭、继承与额度 | Linux man-pages 核查；未执行 dup/fork 或关闭对照 |
| [I/O 多路复用与就绪通知](../knowledge/systems/io-multiplexing-readiness-and-event-loops.md) | select/poll/epoll、非阻塞、LT/ET、状态与公平推进 | Linux man-pages 核查；未运行事件服务器或性能对比 |

本批继续概念优先，将内存地址、内核入口、资源引用和事件处理串联；系统范围为 Linux，不把具体平台语义推广为所有操作系统的通用算法。

## 2026-10-20：模块、类型与打包概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [模块系统与循环依赖](../knowledge/runtime/modules-bindings-and-circular-dependencies.md) | 解析/链接/求值、活绑定、初始化环、CommonJS 与模块身份 | ECMAScript、MDN、Node.js 24.16.0 核查；片段未执行 |
| [类型系统与运行时校验](../knowledge/runtime/type-systems-and-runtime-validation.md) | 推导、断言、unknown/any、结构兼容、泛型与实际值检查 | TypeScript 官方核查；未运行 tsc 或校验器 |
| [打包与代码分割](../knowledge/frontend/bundling-tree-shaking-and-code-splitting.md) | 模块图、转译/移除/拆分、副作用、加载与资源版本 | webpack、Rollup、MDN/Vite 官方核查；未改配置或测优化收益 |

本批继续概念优先，区分语言、类型检查器、构建工具和宿主执行；找到文件、构建完成和下载完成均不扩展为更高层正确性保证。

## 2026-10-20：架构与工程质量概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [领域模型、聚合与业务不变量](../knowledge/architecture/domain-models-aggregates-and-invariants.md) | 实体与值语义、根与写入路径、并发持久化和跨边界流程 | Evans/Fowler/Microsoft 核查；订单模型为教学设计 |
| [契约测试与版本兼容](../knowledge/engineering/contract-testing-and-compatibility.md) | 消费代码、提供方验证、匹配规则、环境版本矩阵 | Pact、OpenAPI、SemVer 官方核查；未运行 SDK/Broker |
| [属性测试与状态模型](../knowledge/engineering/property-testing-and-state-models.md) | 性质与 oracle、输入域与分布、收缩、命令序列和回归 | Hypothesis 6 与 LLVM 官方核查；没有生成或模糊测试实测 |

本批继续概念优先，区分架构约束与实际提交、跨组件契约与完整业务正确性、顺序模型与并发证据；不把测试工具介绍当作已执行实验。

## 2026-10-20：交付与可靠性概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [镜像、容器与资源隔离](../knowledge/devops/images-containers-and-resource-isolation.md) | 标签与摘要、平台、namespace/cgroup、资源与存储生命周期 | Docker、Linux 和 Kubernetes 文档核查；未运行容器 |
| [声明式部署与健康探针](../knowledge/devops/declarative-deployments-and-health-probes.md) | 控制循环、滚动替换、startup/readiness/liveness、传播与终止 | Kubernetes v1.36 文档核查；未运行集群或探针 |
| [故障域、冗余与恢复目标](../knowledge/reliability/failure-domains-redundancy-and-recovery.md) | 共同故障、容量、切换与历史恢复、业务 RTO/RPO | AWS 一手资料核查；部署表和时间线为教学设计 |

本批继续概念优先，未把确定镜像、控制器更新完成或数据库启动当作完整业务保证；既有本机备份实验也不扩展为容灾目标实测。

## 2026-10-20：安全与 API 的身份、来源和条件请求

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [OAuth 与 OIDC](../knowledge/security/oauth-oidc-and-pkce.md) | 授权码、PKCE、交易关联、令牌用途和外部身份绑定 | OIDC Core、RFC 7636/9700 来源核查；未接入提供方 |
| [同源、CORS 与 CSRF](../knowledge/security/origins-cors-and-csrf.md) | origin/site、预检与响应共享、自动凭证和 CSRF 防护 | HTML、Fetch、MDN/OWASP 来源核查；未运行双站点实验 |
| [HTTP 条件请求](../knowledge/api/conditional-requests-and-cache-validation.md) | ETag、304/412、强弱比较、原子条件保存与缓存身份边界 | HTTP RFC 来源核查；请求与并发时间线为纸面推演 |

本批继续概念优先，未把登录成功、跨源读取许可或标签匹配当作对象授权，也未把既有幂等、库存或对象授权实验扩展为协议集成证据。

## 2026-10-20：闭包、响应式更新与路由缓存

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [闭包与词法绑定](../knowledge/runtime/closures-and-lexical-bindings.md) | 词法环境、共享绑定、提前计算及渲染快照 | ECMAScript/MDN/React 来源核查；片段为推演 |
| [响应式状态与更新](../knowledge/frontend/reactive-state-and-update-scheduling.md) | 依赖追踪、更新队列、DOM 提交与呈现 | Vue 3/React 官方核查；没有挂载或计数实验 |
| [前端路由与缓存](../knowledge/frontend/routing-state-and-cache-lifecycles.md) | 历史记录、组件与缓存层、迟到响应和身份边界 | History、Vue Router、React、RFC/Cache API/bfcache 来源核查；没有缓存集成实测 |

本批继续概念优先；框架机制分别限定，未把语言绑定、状态快照、HTTP 缓存和整页恢复混成统一规则。

## 2026-10-20：分布式协调与消息日志概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [共识与 Quorum](../knowledge/distributed/consensus-leaders-and-quorums.md) | 固定法定集合、任期/日志规则、安全与推进、读路径 | Raft 原论文及 etcd 3.6 官方核查；相交与分区为纸面推演 |
| [租约与 Fencing](../knowledge/distributed/leases-heartbeats-and-fencing.md) | 心跳怀疑、限时资格、资源端原子代次检查及生效点 | etcd、Chubby 论文与 Kleppmann 原始分析核查；未运行锁集群 |
| [分区、消费组与偏移](../knowledge/messaging/partitions-consumer-groups-and-offsets.md) | 普通消费组分工、下一提交位置、完成前沿和重平衡 | Kafka 4.1 官方资料核查；未启动 Broker 或运行消费实验 |

本批只新增概念正文；多数响应、租约到期和偏移提交分别限定保证范围，不扩展为外部业务已验证。

## 2026-10-20：Agent 工作流与编排概念

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [路由与交接契约](../knowledge/ai/workflow-routing-and-handoff-contracts.md) | 规划/路由/委派/交接、最小材料、接收与完成 | 官方框架资料核查；责任契约与故障表为教学设计 |
| [编排状态与检查点](../knowledge/ai/workflow-state-and-checkpoints.md) | 权威范围、保存粒度、恢复/重放、版本与当前许可 | LangGraph 文档核查；未安装或运行该 SDK |
| [持久化预算与失败收敛](../knowledge/ai/durable-budgets-and-failure-convergence.md) | 根预算、原子预留、结算、期限与停止 | AWS/gRPC/Python 来源核查；算例为纸面推演，账本未实现 |

本批不新增实验；原 Runtime 继续保持设计提案，既有工具与记忆实验不扩展为编排集成证据。

## 2026-10-20：AI 记忆治理

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [记忆写入与来源](../knowledge/ai/memory-writing-and-provenance.md) | 声明、观察、推断的准入与来源支持范围 | 官方资料核查；来源适配与自然语言核实未实现 |
| [记忆版本与失效](../knowledge/ai/memory-versions-conflicts-and-expiry.md) | 来源修订、条件更新、派生版本与期限 | SQLite/Redis 资料核查；分布式一致性未实测 |
| [记忆权限与删除](../knowledge/ai/memory-access-revocation-and-deletion.md) | 当前授权、tombstone、派生清理与备份 | OWASP/SQLite 资料核查；物理擦除和恢复治理未实测 |
| [记忆治理实验](../knowledge/ai/memory-governance-lab.md) | 独立权威与派生库、受控交错与逐项读取证据 | 21 类、157 个检查结果通过；没有模型或向量检索 |

## 2026-10-19：AI 工具执行边界

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [模型提出调用以后由谁执行](../knowledge/ai/tool-calling-and-execution-contracts.md) | 调用候选、稳定动作标识、调度与确认 | 官方机制核查；通用链路为教学综合 |
| [合法 JSON 为何仍不能直接执行](../knowledge/ai/structured-outputs-and-validation.md) | 完整性、结构、业务、授权与结果 | 官方资料核查；Schema 示意未提交模型 |
| [外部文字为何不是执行许可](../knowledge/ai/tool-authorization-and-untrusted-results.md) | 可信身份、审批绑定、数据来源与恢复复查 | 官方安全资料核查；不宣称模型注入防护率 |
| [候选到结果的局部验证](../knowledge/ai/tool-execution-boundaries-lab.md) | 固定候选、两库、受控工具与查询恢复 | 24 类、128 个检查结果通过；没有模型或网络 |

## 2026-10-19：网络与连接生命周期

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [改了解析为什么仍访问旧地址](../knowledge/networking/dns-caching-and-address-selection.md) | 权威/缓存、TTL、负缓存、地址尝试和连接存活 | RFC/运行时资料核查；时间线为纸面推演 |
| [建立与关闭分别说明什么](../knowledge/networking/tcp-tls-and-connection-states.md) | TCP 状态、TLS 身份、保活与业务未知 | 一手资料核查；握手包、半关闭和 TLS 未实测 |
| [请求还没发出为何已超时](../knowledge/networking/http-reuse-pools-and-timeouts.md) | 连接/流、池归还、正文消费、空闲关闭与阶段预算 | 协议/Node.js 资料核查；HTTP/2/3 与代理未实测 |
| [连接、等待与超时对照](../knowledge/networking/connection-lifecycle-lab.md) | 真实回环 HTTP/1.1、连接编号、显式释放与本地标记 | 七类各三次，21 组、42 请求、144 个检查结果通过 |

## 2026-10-19：容量控制与过载保护

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [异步队列为何仍积压](../knowledge/performance/backpressure-and-bounded-queues.md) | 有界等待、拒绝与上游反馈、截止时间 | 官方资料核查；反馈协议与业务队列位置为教学说明 |
| [限速以后为何连接池仍满](../knowledge/api/rate-limits-concurrency-and-quotas.md) | 速率、同时占用、累计配额与身份范围 | 一手资料核查；令牌桶与分布式计数未实测 |
| [依赖变慢怎样收敛](../knowledge/reliability/circuit-breakers-isolation-and-degradation.md) | 熔断探测、资源隔离、降级与恢复 | 架构模式核查；状态机、降级业务与真实依赖未实测 |
| [排队、拒绝与取消对照](../knowledge/performance/overload-control-lab.md) | 固定执行槽、开放式到达与原始结果 | 27 组、4,320 次尝试、216 个检查状态（含条件不适用项）、6 次超时探针和 4 项契约测试通过 |

## 2026-10-19：数据恢复与迁移

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [提交后数据页为何还没写完](../knowledge/database/wal-and-crash-recovery.md) | WAL、日志持久化、页写回、检查点与恢复边界 | PostgreSQL 18 来源核查；未做崩溃或断电测试 |
| [备份成功为何还不够](../knowledge/database/backups-and-point-in-time-recovery.md) | 逻辑/物理备份、连续归档、恢复目标与数据验收 | 官方资料核查；目标与验收层次为设计说明 |
| [回退代码为何救不回数据](../knowledge/database/schema-migrations-and-compatibility.md) | 读写契约、扩展回填收缩、权威值和不可逆边界 | 官方 DDL/AWS 资料核查；迁移与混合部署未执行 |
| [恢复到指定命名点](../knowledge/database/backup-recovery-lab.md) | 基础备份、实际归档、重放暂停与目标行集 | PostgreSQL 18.0，13 项恢复检查与 4 项归档契约测试通过 |

## 2026-10-19：并发正确性与同步

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [每一步成功为何仍算错](../knowledge/systems/races-and-atomicity.md) | 共享状态、业务不变量、原子边界与实际挂起点 | Python/Java/PostgreSQL 一手资料核查；内存示例未执行 |
| [加锁为何仍有竞争](../knowledge/systems/locks-and-synchronization.md) | 互斥、计数准入、条件等待与保护范围 | 官方 API 核查；线程、协程与租约实验未执行 |
| [等待为何不能自行结束](../knowledge/systems/deadlocks-and-recovery.md) | 等待环、错误分类、锁顺序与整事务恢复 | PostgreSQL 18 文档核查；自动重试仍为教学协议 |
| [库存、回滚与锁错误实验](../knowledge/database/inventory-concurrency-lab.md) | 两个业务会话与观察会话、相同不变量、SQLSTATE | PostgreSQL 18.0，七类各三次，保存原始记录 |

## 2026-10-19：AI 基础与评价

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [聊天记录还在为何仍忘记条件](../knowledge/ai/tokens-context-and-memory.md) | Token、预算、上下文选择、记忆、压缩与业务状态 | 官方文档核查；Token 预算为纸面计算，未调用模型 |
| [检索到资料为何仍答错](../knowledge/ai/rag-retrieval-and-grounding.md) | 分块、向量、召回、重排、组装、有据性与访问边界 | 官方检索等文档核查；版本资料为教学设计，未构建索引 |
| [怎样判断 AI 应用真的变好](../knowledge/ai/evals-and-failure-analysis.md) | 样本、评分、独立检查、失败分类与系统版本对照 | 官方评价等文档核查；数字与样本未执行模型或评分实验 |

## 2026-10-19：浏览器、身份与接口边界

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [HTML 显示后为什么还未准备好](../knowledge/frontend/rendering-and-hydration.md) | 样式、布局、绘制与合成；脚本调度；SSR/SSG 与水合一致性 | 浏览器与框架官方文档核查；未搭建 SSR 示例或录制性能实验 |
| [退出后旧令牌为何仍可使用](../knowledge/security/authentication-sessions-and-tokens.md) | 身份、会话与传输；令牌验证、到期、刷新、撤销与 Cookie 边界 | OWASP、IETF、OIDC 与 Cookie 文档核查；未实现认证或撤销集成 |
| [列表翻页为什么重复或漏项](../knowledge/api/contracts-and-pagination.md) | HTTP 与 Schema 契约、稳定排序、Offset、Keyset 与快照边界 | RFC/OpenAPI/PostgreSQL 18 文档核查；排序历史为纸面推演，SQL 未执行 |

## 2026-10-19：数据访问、内存与故障证据

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [建了索引为何仍扫描全表](../knowledge/database/indexes-and-query-plans.md) | 访问路径、选择率、行数估计、联合索引与可见性 | PostgreSQL 18 文档核查；另有[六组查询计划实测](../knowledge/database/query-plans-lab.md) |
| [对象不用了为何仍占内存](../knowledge/runtime/reachability-and-garbage-collection.md) | 可达性、引用持有、分代回收与内存观测口径 | MDN、V8、Node.js 文档核查；未运行泄漏复现或快照实验 |
| [日志、指标与链路怎样关联](../knowledge/reliability/logs-metrics-and-traces.md) | 片段边界、上下文传播、标签基数、采样偏差 | OpenTelemetry、Prometheus 文档核查；未部署采集管道 |

## 前一批六个概念选题

| 工程问题 / 正文 | 核心机制 | 证据状态 |
| --- | --- | --- |
| [改一个功能为何牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md) | 内聚、耦合、信息隐藏、依赖方向 | 一手来源核查；支付边界为教学设计 |
| [请求更多为何吞吐不升](../knowledge/performance/latency-throughput-and-queues.md) | 平均量、尾延迟、Little 定律、背压 | 一手来源核查；排队与容量数字为纸面计算 |
| [同一事务到底能看到什么](../knowledge/database/isolation-and-mvcc.md) | 快照、隔离、写偏斜与整事务重试 | PostgreSQL 18 文档核查；并发历史未实测 |
| [回调为什么还没有执行](../knowledge/runtime/event-loop-and-microtasks.md) | 任务、微任务、渲染机会与宿主差异 | 标准与宿主文档核查；顺序为规范推演 |
| [处理成功后为何收到重复消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) | 确认窗口、消费幂等、顺序与重放 | RabbitMQ 4.1 文档核查；集成故障注入待执行 |
| [怎样判断服务足够可靠](../knowledge/reliability/slis-slos-and-error-budgets.md) | SLI/SLO、分母、错误预算与燃烧率 | Google SRE 来源核查；未部署指标和告警 |

## 上一轮四个选题

| 工程问题 / 正文 | 主要读者 | 前置知识 | 本轮产出与证据状态 |
| --- | --- | --- | --- |
| [超时后还该不该重试](../knowledge/reliability/timeouts-and-retry-budgets.md) | 开发、测试、运维、平台 | 请求语义、幂等性 | 七维正文、预算流程、7 项本地策略测试；网络取消待验证 |
| [两个成功事务为何仍可能超卖](../knowledge/database/concurrent-inventory.md) | 开发、数据、测试、架构 | SQL、事务提交 | 概念与 SQL 说明；[两会话实验](../knowledge/database/inventory-concurrency-lab.md)已执行五类库存场景及两类锁错误 |
| [已登录为何仍不能访问这份数据](../knowledge/security/object-level-authorization.md) | 开发、测试、安全、平台 | 请求参数、身份与 SQL | 七维正文、权限规则与 10 项本地策略测试；认证与 HTTP 集成待验证 |
| [页面已显示为何仍点不动](../knowledge/frontend/long-tasks-and-responsiveness.md) | 前端、测试、性能工程 | JavaScript、异步与阻塞 | 概念、任务切片示例及[15 组浏览器实测](../knowledge/frontend/long-tasks-lab.md)；Worker 与真实业务仍待验证 |

四篇均为 `evolving`，已核查正文声明范围的一手来源。策略测试通过只表示相应本地断言成立；库存、查询计划与长任务的独立实验已有局部证据，不扩展为整个领域已验证。

## 后续概念候选

| 工程问题 | 内容类型 | 预期产出 |
| --- | --- | --- |
| 查询执行器与优化器怎样选择并推进计划 | 概念 | 迭代/向量化执行、代价与基数、连接次序及估计失真 |
| 图数据模型怎样表达关系与遍历 | 概念 | 属性图/RDF、身份、路径查询、索引与更新成本 |
| 对象模型与动态分派怎样选择实际方法 | 概念 | 属性查找、继承/委托、接口分派与缓存假设 |
| 调用帧、协程与续体怎样保存执行状态 | 概念 | 栈/堆状态、暂停恢复、任务归属与资源生命周期 |

候选题目尚无正文链接，完成后再加入问题导航。每次选题先检查已有文章能否通过补充章节或实验解决，再决定新增正文。

## 后续实验储备

重构行为与特征基线、静态规则/扫描覆盖及抑制、最终版本评审证据、依赖解析/升级与制品 SBOM/来源验证、缓存访问顺序与伪共享、CPU 时间/调度/配额与 PSI 采集、执行/等待调用栈与符号、冷暖/重复与端到端基准、向量精确/近似基线与量化、过滤/更新和近邻召回、融合/去重/窗口与重排评价、LSM Flush/合并与快照删除、放大口径及停写、分词/倒排求交/位置短语与排序、索引更新与重建切换、页范围/分裂与回表、Trie 终止/压缩及编码、Bloom 误报/覆盖与重建、LRU/LFU 访问轨迹/抽样衰减及字节限制、线性容器操作与扩缩容、哈希碰撞与键变更、排序/二分边界性质、堆和优先级更新、图遍历与环/拓扑判定、加权路径与负环分类、贪心/背包穷举及方案恢复、并查集合并与 MST/最短路径对照、算法正确性及基准对照、内存分配与触页、fork 写时复制、驻留与回收、系统调用跟踪和信号中断、共享偏移与编号复用、跨线程关闭、LT/ET 与公平调度、模块循环/顶层异步与身份缓存、类型编译与输入拒绝、Tree Shaking/分割/预加载及跨版本资源、聚合并发持久化、消费者/提供方契约与混合版本、属性生成与收缩、状态机与并发历史对照、容器资源与挂载、滚动替换与探针误判、端点传播及优雅终止、完整业务恢复与回切、OAuth 回调与令牌验证、CORS/CSRF 双站点对照、HTTP 缓存验证与原子条件写入、归档缺失与时间目标、跨故障域恢复、迁移回填兼容、跨行写偏斜与隔离对照、真实交互与 Worker、响应式/路由/Service Worker 及整页恢复集成、跨代理连接池、DNS/TLS 切流与真实网络故障、分布式限流及熔断恢复、共识分区与租约隔离、消费重平衡和偏移事务集成、Outbox relay、模型/远程工具与审批集成、持久预算账本与交接派送、真实进程或 SDK Checkpoint 故障注入、语义记忆质量、向量更新与备份恢复后的删除策略仍保留为后续实践工作。各篇待验证状态保持可见，概念正文的来源核查不等同于这些实验已经完成。

[写作规范](editorial.md) · [问题导航](../problems.md) · [文章目录](../articles.md)
