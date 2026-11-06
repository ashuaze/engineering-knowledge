---
id: "kb-api-idempotency"
title: "幂等性：给重复请求一个稳定的业务结果"
kind: "concept"
domain: "api"
status: "evolving"
summary: "在明确的作用域、保留期和事务边界内，避免重试产生重复业务效果。"
created: "2026-10-16"
updated: "2026-10-22"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-api-idempotency-lab", "kb-messaging-outbox", "kb-ai-recoverable-runtime", "kb-reliability-retry-budgets", "kb-security-object-authorization", "kb-database-concurrent-inventory", "kb-api-contracts-pagination", "kb-security-sessions-tokens", "kb-api-conditional-requests", "kb-api-webhook-signatures", "kb-distributed-identifiers"]
tags: ["reliability", "transactions"]
---

# 幂等性：给重复请求一个稳定的业务结果

学习入口：客户端[超时](../../glossary/api.md#api.retries)后，如何重试而不重复创建订单？前置知识：HTTP 请求与[数据库事务](../../glossary/database.md#database.isolation)的基本概念。本文讨论应用层[幂等](../../glossary/api.md#api.idempotency)协议，随附实验的保证范围是单个本地数据库。

## Definition：定义与问题

幂等性约束的是重复执行带来的预期业务效果。它不要求每次返回相同 HTTP [状态码](../../glossary/api.md#api.http-semantics)，也不意味着服务器完全没有记录日志等额外动作。RFC 9110 §9.2.2 规定了 HTTP 方法的幂等语义。

对于创建订单等 POST 操作，可以额外设计应用层的幂等协议。本文推荐的键格式、冲突响应和保留期属于应用契约，不宣称是 HTTP 的统一强制规则。

### 从响应丢失开始

客户端提交订单，数据库已经提交，服务端回包途中断线。客户端只知道请求失败，无法判断订单是否存在。如果把重试当成一笔新操作，可能创建第二笔订单。

设计目标是：同一调用方、同一操作、同一幂等键和相同业务输入，在约定保留期内找到原有业务结果。

## Principles：工作机制与核心原理

为同一业务动作提供稳定标识，将它与规范化输入、已提交结果关联。重试时先判断是否为同一动作，再决定复用结果、等待或报告冲突。

| 情况 | 本文建议的处理 |
| --- | --- |
| 首次提交合法键与请求 | 原子执行业务并保存结果 |
| 相同键、相同业务输入 | 返回已保存结果 |
| 相同键、不同业务输入 | 返回明确冲突，如 409；客户端修正调用 |
| 原操作仍在进行 | 等待有限时间或返回可查询状态，不无限占用[线程](../../glossary/systems.md#systems.execution-units) |
| 结果无法确认 | 暴露待核对状态，提供查询或对账路径 |
| 记录已过保留期 | 按公布的契约处理；可能需要业务[唯一约束](../../glossary/database.md#database.constraints)继续防重 |

键的作用域由服务器根据[认证](../../glossary/security.md#security.identity)身份和操作构造。例如 `tenant + principal + operation + key`；不要信任客户端传入的租户字符串。每次重放都重新执行授权检查，避免缓存结果成为越权通道。

请求指纹应基于校验后、规范化的业务输入计算，明确是否包含币种、[API 版本](../../glossary/api.md#api.versioning)或重要请求头。简单地对原始 JSON 字符串哈希，可能把字段顺序差异当作不同业务操作。

## Trade-offs：优势、限制与适用边界

收益是让客户端在响应丢失后仍有安全重试与查询路径。代价是维护稳定操作标识、请求指纹、结果记录和保留期，并处理[并发](../../glossary/systems.md#systems.concurrency)、授权与冲突。

单数据库事务方案适合副作用完全位于同一数据库的操作；SQLite 实验以串行化写入换取简单的并发控制。涉及外部支付、发信或跨数据库写入时，要重新设计外部幂等、查询与对账边界。幂等键只能识别同一动作的重试，业务唯一性仍需独立约束。

## Implementation：代码或架构实现

### 单数据库事务方案

若副作用完全位于一个数据库，可以让业务行、幂等结果和必要的 [Outbox](../../glossary/messaging.md#messaging.outbox) 事件使用同一个事务。

下面是设计流程，实际并发控制须按数据库实现：

```text
认证与授权 → 校验和规范化输入 → 计算 scope 与 fingerprint
BEGIN
  串行化或使用唯一约束竞争 (scope, key)
  已有结果：核对 fingerprint，读取结果
  没有结果：写业务行，写幂等结果，按需写 Outbox
COMMIT
发送响应
```

若进程在提交前失败，事务应整体回滚；提交后回包失败，重试能够读取已保存结果。SQLite 实验使用 `BEGIN IMMEDIATE` [序列化](../../glossary/runtime.md#runtime.serialization)写入，避免把查后写当成并发安全。PostgreSQL 等系统需结合唯一约束、事务隔离与冲突处理实现，不能原样搬用锁策略。

实际代码见 [Python / SQLite 实验](../../../examples/idempotency/lab.py)，运行要求和观察结果见[实验说明](idempotency-lab.md)。

## Failure Modes：常见错误与故障模式

1. **外部支付或发信。** 数据库提交和外部调用不在同一事务；需要外部幂等键、结果查询、Outbox 或对账。这里不提供真实扣款保证。
2. **换键重试。** 两个不同键通常被视为两笔操作。若业务规定一个订单只能支付一次，还需数据库业务约束。
3. **过短的保留期。** 记录清理后到来的旧重试可能再次执行。保留期必须覆盖客户端、[队列](../../glossary/algorithms.md#algorithms.queues)和离线补发的重试窗口。
4. **跨权限重放。** 已保存结果不应绕过当前身份与对象权限检查。

这些问题的排查入口分别是外部结果查询、业务唯一约束、保留期策略和逐次授权检查。

## Practice：工程案例、测试与验证

验证的核心是[不变量](../../glossary/systems.md#systems.atomicity)：“同一 scope + key 最多产生一个本地业务行”，以及“不同指纹不能误领旧结果”。还要验证事务回滚、并发请求、响应丢失和不同作用域。

本仓库的[幂等性实验](idempotency-lab.md)提供可运行的这些用例。实验仅约束本地数据库写入；外部系统、[多地域](../../glossary/devops.md#devops.regions)和保留期清理未覆盖。

自检：解释“提交前失败”与“提交后响应丢失”为何需要不同的恢复判断；再为一个实际 API 写出键作用域、输入指纹、保留期和结果查询契约。

外部事件的来源校验、重放窗口和合法重复投递，见[Webhook 签名与防重放](webhook-signatures-replay-and-delivery.md)；签名通过不自动完成持久接纳和幂等消费。

标识生成策略另见[分布式 ID](../distributed/distributed-identifiers-time-and-uniqueness.md)。每次重试生成新的唯一编号，仍可能把同一业务动作当成多次请求；稳定幂等身份与新记录主键需要分别约定。

## Related Concepts：关联概念

- [HTTP 契约与分页](contracts-and-pagination.md)：把方法、错误、规范化输入和兼容规则写入调用约定。
- [认证、会话与令牌](../security/authentication-sessions-and-tokens.md)：重放之前仍需验证当前身份与凭证有效性。

- [幂等性实验](idempotency-lab.md)：验证本地事务与重复请求的不变量。
- [Transactional Outbox](../messaging/transactional-outbox.md)：组合使用时，在同一事务内保存业务结果与待发布事件。
- [可恢复 Agent Runtime](../ai/recoverable-runtime.md)：把稳定操作标识与结果查询用于[工具调用](../../glossary/ai.md#ai.tools)恢复。
- [超时与重试预算](../reliability/timeouts-and-retry-budgets.md)：决定何时停止尝试，以及结果未知时如何恢复。
- [对象级授权](../security/object-level-authorization.md)：每次重放与查询都要检查当前主体的对象权限。
- [库存并发](../database/concurrent-inventory.md)：把[业务不变量](../../glossary/architecture.md#architecture.domain-model)落实到并发写入，与重试去重分别验证。

## 来源与核查

核查日期：2026-10-16。HTTP 语义依据 RFC；应用协议和失败矩阵是本文设计建议；本地数据库保证另见实验记录。

- [RFC 9110 §9.2.2：Idempotent Methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods)
- [SQLite：Transactions](https://www.sqlite.org/lang_transaction.html)

[HTTP 条件请求](conditional-requests-and-cache-validation.md)中的 [If-Match](../../glossary/api.md#api.conditionals) 可限制基于旧表示的修改，但响应丢失后收到 412 不能证明第一次没有提交。它不替代本篇的稳定操作标识、结果记录与重试契约；条件请求篇没有新增 HTTP 集成实验。
