# 工程知识库

**理解原理，解释故障，做出有依据的工程取舍。**

这是一套持续生长的中文工程知识库，面向软件开发、测试、运维与平台、数据、安全、架构及 AI 工程等方向的技术工程人员，也适合正在建立工程基础的学习者。内容从计算机基础延伸至软件系统、数据库、分布式、生产工程和 AI Agent 系统；前置知识与适用范围由各篇正文及学习路径分别说明。

建议先从[实际工程问题](problems.md)进入，再用知识地图和术语索引定位关联概念。学习时重点积累底层原理、系统设计、故障诊断和技术权衡能力，每次留下可解释或可验证的产出。

目前 17 个领域均已有正文入口。各领域的概念深度与待补机制见[概念路线图](handbook/concept-roadmap.md)，可按自己的任务和已有基础选择阅读重点。

| 按你的需要进入 | 你会得到什么 |
| --- | --- |
| [问题导航](problems.md) | 从重复请求、慢接口、状态恢复等问题进入 |
| [学习路径](paths/index.md) | 请求处理、生产可靠性、AI Agent、浏览器交互四条路线 |
| [知识地图](map.md) | 17 个领域的边界、目标与关键问题 |
| [术语索引](glossary.md) | 中英文关键词、简释和已完成正文 |
| [文章目录](articles.md) | 当前可阅读的深入内容 |
| [概念路线图](handbook/concept-roadmap.md) | 17 个领域的概念入口、当前深度与待补机制 |

## 建议先读

补基础概念可先读：[进程、线程与协程](knowledge/systems/process-thread-coroutine.md) → [HTTPS 请求链路](knowledge/networking/https-request-lifecycle.md)；数据与性能方向可从[复杂度与结构选择](knowledge/algorithms/complexity-and-data-structures.md)、[缓存失效](knowledge/cache-search/cache-aside-and-invalidation.md)、[一致性与复制](knowledge/distributed/consistency-and-replication.md)进入。交付与质量方向可读[交付生命周期](knowledge/devops/build-deploy-rollback.md)和[测试层次](knowledge/engineering/test-scopes-and-doubles.md)。

1. 写了 async，其他请求仍卡住 → [同步、异步与阻塞](knowledge/runtime/async-and-blocking.md)。
2. 客户端超时，不知道订单是否创建 → [幂等性](knowledge/api/idempotency.md)。
3. 业务表已提交，消息却没发出去 → [Transactional Outbox](knowledge/messaging/transactional-outbox.md)。
4. Agent 重启后不知道工具是否成功 → [可恢复 Agent Runtime](knowledge/ai/recoverable-runtime.md)。

## 内容的使用方式

[超时与重试预算](knowledge/reliability/timeouts-and-retry-budgets.md)与[对象级授权](knowledge/security/object-level-authorization.md)附本地策略实验；[库存并发](knowledge/database/concurrent-inventory.md)和[浏览器长任务](knowledge/frontend/long-tasks-and-responsiveness.md)中的独立实验仍待执行。概念文章也使用说明性实现、纸面推演与自检，并分别标明证据状态。

每篇正文围绕一个问题，按目的提供必要的机制解释、适用边界或诊断证据。案例会标明是否为教学推演；代码会区分可运行实验和说明性伪代码。当前正文均处于 `evolving`，欢迎通过仓库 Issue 提出可复现的更正。

阅读时可以从定义、原理、取舍、实现、失败、验证和关联概念理解一个问题。对比帮助选择方案，模式解释约束与机制，案例提供诊断过程，实验展示验证方法，决策记录取舍依据；术语简释用于检索与定位。

“有正文”不代表个人已掌握，`evolving` 表示文章仍在完善，不是对所讨论技术成熟度的评价。

## 来源与使用

正文记录更新时间及已核查范围，技术细节优先链接官方文档。部分内容使用 AI 辅助起草；已对关键机制查阅一手资料，并按各篇说明执行随附实验测试。具体证据与局限以正文为准。

原创正文采用 CC BY 4.0，原创代码采用 MIT 许可。转载与改编请保留来源、许可信息并说明修改，详见[使用与转载条件](rights.md)。
