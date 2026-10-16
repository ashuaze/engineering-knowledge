# 学习路径

面向不同方向的技术工程人员，按当前问题和已有基础选择路线，每个单元以可解释或可验证的产出结束。当前四条路线围绕已有正文组织，后续随内容积累扩展；各路线显式区分现有正文和后续计划，不把术语覆盖当作课程已完成。

当前以[核心概念补全](../handbook/concept-roadmap.md)为先。各路线先完成定义、机制、取舍、边界和关联理解，以纸面推演与自检验收；现有实验作为可选配套资料，独立实作按后续阶段推进。

每个单元先提出工程问题，再通过知识索引找到关联概念，结合机制、取舍、实现与失败边界展开理解。用原理解释、设计判断、诊断记录或实验结果检验学习成果。

## A. 请求处理基础：解释一个请求

适合需要理解请求链路的软件开发、测试、运维及其他技术工程人员。

目标：说清请求如何到达服务、如何等待、如何写入，并能验证重复请求的行为。

1. [基础地图](../map.md)：选读系统、网络、Runtime、API、数据库、安全领域，用于定位概念与前置知识。
2. [进程、线程与协程](../knowledge/systems/process-thread-coroutine.md)：区分资源边界、并发与并行。
3. [HTTPS 请求链路](../knowledge/networking/https-request-lifecycle.md)：画出调用方、接入层、应用和数据依赖的边界。
4. [同步与阻塞](../knowledge/runtime/async-and-blocking.md)：画出调用、工作和结果的执行者。
5. [幂等性](../knowledge/api/idempotency.md)：写下 API 重试契约；[幂等性实验](../knowledge/api/idempotency-lab.md)作为配套证据阅读。
6. [库存并发](../knowledge/database/concurrent-inventory.md)：写出业务不变量，解释陈旧读取与条件更新。
7. [对象级授权](../knowledge/security/object-level-authorization.md)：用主体与动作矩阵解释对象权限。

后续实践：PostgreSQL 并发实测、对象授权 HTTP 集成，以及带校验、权限、超时和幂等的本地 API。当前概念验收是解释链路、状态与业务不变量；完整服务实现属于后续阶段。

## B. 生产可靠性：把失败边界画出来

适合关注故障分析、交付质量和系统运行的软件开发、测试、运维、平台及架构人员。

前置：能实现 API 和基本数据库事务。

1. [幂等性](../knowledge/api/idempotency.md)：区分超时和失败。
2. [超时与重试预算](../knowledge/reliability/timeouts-and-retry-budgets.md)：解释总预算、单次上限和停止条件。
3. [Cache-Aside 与失效](../knowledge/cache-search/cache-aside-and-invalidation.md)：排列旧值回填的并发时序。
4. [一致性与复制](../knowledge/distributed/consistency-and-replication.md)：限定写确认与读取可见的保证范围。
5. [Outbox](../knowledge/messaging/transactional-outbox.md)：列出双写与重复窗口。
6. [慢 API 排查](../knowledge/performance/slow-api-investigation.md)：为三个假设分别指定证据。

后续概念：SLI/SLO、延迟与队列。后续实践：连接池压测、缓存故障与恢复演练。当前概念验收是能画出故障窗口、判断读取保证并为排查假设指定证据。

## C. AI Agent 工程：恢复状态与工具副作用

适合参与 AI 应用开发、数据与 AI 平台、工具集成、测试或安全设计的技术工程人员。

前置：了解 API 幂等性、持久化状态和工具调用基本概念。

1. [AI 领域索引](../knowledge/ai/index.md)：定位 RAG、Loop、Harness、Memory 和 Evals 的关系。
2. [幂等性](../knowledge/api/idempotency.md)：为工具动作建立稳定标识。
3. [可恢复 Runtime](../knowledge/ai/recoverable-runtime.md)：设计 unknown 状态与恢复分支。
4. [Outbox](../knowledge/messaging/transactional-outbox.md)：理解本地提交与外部执行边界。
5. [对象级授权](../knowledge/security/object-level-authorization.md)：把工具动作中的身份、租户、对象与权限分开检查。
6. [重试预算](../knowledge/reliability/timeouts-and-retry-budgets.md)：为工具重试设定总时间和停止条件。

后续计划：Checkpoint 故障注入、RAG 召回评测、Memory 写入与失效、Agent 工具授权集成。验收：用测试替身构造工具成功但返回超时，系统能查询或转人工，不盲目重复不可逆动作。

## D. 浏览器交互：解释一次点击为什么迟到

适合前端、测试和关注用户体验的技术工程人员。前置：JavaScript 函数、Promise 与基本浏览器调试。

1. [同步、异步与阻塞](../knowledge/runtime/async-and-blocking.md)：画出调用、工作与完成通知，区分浏览器与 Node.js 宿主。
2. [浏览器长任务](../knowledge/frontend/long-tasks-and-responsiveness.md)：按对照计划分析任务、输入与绘制；浏览器实验待执行。

后续计划：可运行交互页面、真实性能录制、Worker 对照和框架初始化排查。验收：保存一次交互延迟的原始记录，用证据判断问题在输入处理前、处理期间还是绘制阶段，并检查改动后业务结果相同。

## 学习记录

跨路线配套阅读：[复杂度与数据结构](../knowledge/algorithms/complexity-and-data-structures.md)帮助解释工作量与空间；[构建、部署与回滚](../knowledge/devops/build-deploy-rollback.md)和[测试层次与替身](../knowledge/engineering/test-scopes-and-doubles.md)帮助界定变更与证据范围。

给每个单元留下一条证据：代码、复现步骤、解释录音、设计评审或事故复盘。个人掌握等级记录于本地 personal 目录；公开知识库记录可复用的解释与验证。

记录时写明起始问题、关键机制、考虑过的方案、失败假设、实际观察与适用边界，再标出下一步需要验证的部分。
