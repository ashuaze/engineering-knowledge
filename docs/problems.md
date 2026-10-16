# 从问题进入

把实际工程问题作为学习入口，领域与术语清单作为知识索引。建议按“现象与约束 → 关联概念 → 机制与取舍 → 实现 → 故障与验证”推进，留下原理解释、设计依据、诊断证据或验证结果。

下表只链接已经存在的正文。后续主题可记录在路线图中，写完后再加入这里。

| 你遇到的问题 | 先读 | 再验证或深入 |
| --- | --- | --- |
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

模块边界、延迟与排队等待补机制见[概念路线图](handbook/concept-roadmap.md)。库存并发与浏览器长任务等已有实验计划继续保留，实际证据状态以各篇说明为准。
