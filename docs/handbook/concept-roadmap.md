# 概念路线图

这份路线图按知识领域展示已有阅读入口和待深入的机制。可根据当前任务、已有基础与文章的前置知识选择阅读顺序，不必从头读完。

目前共有 18 篇正文，17 个领域均有阅读入口，其中 15 个领域已有概念类正文；架构与性能目前分别以决策记录和教学案例作为入口。有入门文章不表示该领域的全部术语都已深入解释，具体覆盖范围与证据状态以正文说明为准。

## 17 个领域的现状与下一层概念

| 领域 | 当前入口与类型 | 下一层待补概念 |
| --- | --- | --- |
| 系统 | [执行单元（概念）](../knowledge/systems/process-thread-coroutine.md) | 虚拟内存、同步原语、竞态与死锁 |
| 网络 | [请求链路（概念）](../knowledge/networking/https-request-lifecycle.md) | DNS 缓存、连接生命周期、流量与拥塞控制 |
| 算法 | [复杂度与结构选择（概念）](../knowledge/algorithms/complexity-and-data-structures.md) | 树、堆、图与概率结构的访问约束 |
| Runtime | [同步与阻塞（对比）](../knowledge/runtime/async-and-blocking.md) | 事件循环与任务队列、内存管理与 GC |
| 前端 | [长任务（概念）](../knowledge/frontend/long-tasks-and-responsiveness.md) | 渲染流水线、Hydration、状态与更新 |
| API | [幂等性（概念）](../knowledge/api/idempotency.md) | HTTP 语义、契约与校验、分页与版本兼容 |
| 架构 | [知识库 ADR（决策）](../knowledge/architecture/knowledge-base-adr.md) | **核心待补：内聚、耦合、模块边界与依赖方向** |
| 安全 | [对象级授权（概念）](../knowledge/security/object-level-authorization.md) | 认证、Session、OAuth/OIDC 与令牌生命周期 |
| 数据库 | [库存并发（概念）](../knowledge/database/concurrent-inventory.md) | ACID、隔离与 MVCC、索引与执行计划 |
| 缓存与检索 | [Cache-Aside（概念）](../knowledge/cache-search/cache-aside-and-invalidation.md) | 淘汰与容量、倒排与向量检索、混合召回 |
| 消息 | [Outbox（模式）](../knowledge/messaging/transactional-outbox.md) | 投递与确认、消费幂等、顺序与重放 |
| 分布式 | [一致性与复制（概念）](../knowledge/distributed/consistency-and-replication.md) | 共识、Quorum、租约与 Fencing |
| 性能 | [慢 API 排查（教学案例）](../knowledge/performance/slow-api-investigation.md) | **核心待补：延迟、吞吐、队列、背压与尾延迟** |
| 交付 | [交付生命周期（概念）](../knowledge/devops/build-deploy-rollback.md) | 镜像与容器、Namespace/cgroups、声明式运行状态 |
| 可靠性 | [重试预算（概念）](../knowledge/reliability/timeouts-and-retry-budgets.md) | Logs/Metrics/Traces、SLI/SLO、错误预算 |
| 工程质量 | [测试层次（概念）](../knowledge/engineering/test-scopes-and-doubles.md) | 契约验证、属性测试、回归与变更风险 |
| AI | [可恢复 Runtime（概念提案）](../knowledge/ai/recoverable-runtime.md) | Token 与上下文、RAG、工具调用、Memory 与 Evals |

## 重点待补主题

| 主题 | 希望解释的问题 |
| --- | --- |
| 模块边界与依赖方向 | 一次变更为什么会波及多个模块，如何判断职责划分是否合理 |
| 延迟、吞吐与排队 | 请求增多时为什么吞吐不再增长，尾延迟却继续升高 |
| 隔离与 MVCC | 并发事务中一次读取能看到什么，哪些业务约束仍需额外保护 |
| 渲染、任务与内存 | 请求完成后，浏览器和 Runtime 还要做哪些工作 |
| 身份、可观测性与消息语义 | 如何确定调用者权限、定位失败并理解重复与顺序 |
| AI 基础与检索评价 | 上下文、RAG、工具调用、Memory 和 Evals 各自解决什么问题 |

这些主题是待补内容，不代表已完成的文章。已有入口可以先用于理解相关问题；需要时结合[学习路径](../paths/index.md)串联前置知识。

## 阅读与实践

阅读时先解释机制和适用边界，再用一个正常情形与一个失败情形检验理解。说明性代码、纸面推演与已执行实验提供不同范围的证据，具体以各篇声明为准。

可运行的配套实验包括[幂等性](../knowledge/api/idempotency-lab.md)、[重试预算](../knowledge/reliability/timeouts-and-retry-budgets.md)和[对象级授权](../knowledge/security/object-level-authorization.md)。库存并发、浏览器长任务、Outbox relay 与 Agent 恢复等独立实验仍有待补充的部分。

[知识地图](../map.md) · [问题导航](../problems.md) · [文章目录](../articles.md)
