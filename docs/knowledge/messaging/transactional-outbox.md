---
id: "kb-messaging-outbox"
title: "Transactional Outbox：让业务变化留下可投递的记录"
kind: "pattern"
domain: "messaging"
status: "evolving"
summary: "用数据库事务保存发布意图，并明确 relay、重复投递与消费去重的责任。"
created: "2026-10-16"
updated: "2026-10-16"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: ["kb-api-idempotency"]
related: ["kb-api-idempotency", "kb-ai-recoverable-runtime", "kb-database-concurrent-inventory", "kb-distributed-consistency"]
tags: ["messaging", "transactions"]
---

# Transactional Outbox：让业务变化留下可投递的记录

学习入口：业务表写成功，消息为什么没有发出去？前置知识：数据库事务、消息确认与 [API 幂等性](../api/idempotency.md)。本文给出 Outbox 的架构与故障分析，relay/Broker 集成实验尚待实现。

## 双写问题与事务边界

业务要同时完成“写数据库”和“发送消息”。两个独立动作之间存在故障窗口：先写数据库，可能漏发消息；先发消息，可能出现数据库未提交而下游已行动。

Transactional Outbox 将业务更新和待发布事件存入同一数据库事务。独立的投递进程（relay）再将事件发送到消息系统（Broker）。AWS 的模式说明也强调重复消息与幂等消费者的重要性。

## 业务、relay 与消费者如何协作

同一事务中写业务表和 outbox 表。事件至少有稳定 `event_id`、事件类型、聚合标识、有效载荷与创建时间；业务需要顺序时，再定义每个聚合的序列号。

relay 通过轮询或变更数据捕获（CDC）获取待发布事件。成功发布后记录发送进度；失败继续重试。发送进度、业务消费结果和 Broker 的持久化确认必须分别观察。

### 消费端的去重边界

可在消费方数据库中建立 `(consumer_name, event_id)` 唯一约束，将“记录已处理”和“更新本地业务”放在同一事务。重复投递读到已有记录后，不再重复改变本地业务。

如果消费者要发邮件、扣外部余额或调用第三方 API，该事务仍不能覆盖外部副作用。需要继续传递幂等键、查询外部结果或对账。Outbox 也不会自动提供跨所有组件的 Exactly-once。

### 顺序与并发

Outbox 表中的创建时间不等于投递顺序。多个 relay、重试和分区策略都可能改变观察顺序。若订单事件要求有序，先定义“每个订单有序”，再用序列号、分区键与消费校验实现；避免没有必要的全局顺序。

### 串起完整流程

以下是说明性架构流程，尚非已运行的 Broker 集成实现：

```text
业务服务：BEGIN → 写业务表 → 写 outbox(event_id, payload, ...) → COMMIT
relay：轮询或 CDC 读取事件 → 发布到 Broker → 记录发送进度
消费者：接收事件 → 同事务写消费去重记录与本地业务 → 提交 → ACK
```

实现时分别观测发送进度、Broker 持久化确认与消费结果，记录积压最老年龄、未发送数量、重试率和重复消费量。

## 故障窗口与恢复责任

| 故障位置 | 结果 | 需要的处理 |
| --- | --- | --- |
| 业务事务提交前 | 业务与待发记录一起回滚 | 客户端按业务契约重试 |
| 事务提交后、relay 读取前 | 待发记录仍在 | relay 恢复后继续 |
| Broker 已收、relay 未记录成功 | 后续可能重复投递 | 保持 event_id，消费者去重 |
| 消费业务已提交、ACK 丢失 | 消息可能再次被消费 | 消费去重和业务写入在同一事务 |
| 持续失败的事件 | 积压、影响后续处理 | 告警、隔离、人工修复和可审计重放 |

这张矩阵是基于常见数据库与消息系统故障边界的设计分析，具体保证需结合选用组件验证。

## 收益、成本与适用边界

相较于直接分两步写数据库与发消息，Outbox 的收益是在同一事务内保留业务变化与发布意图，提交后可继续投递。它需要接受异步投递、重复处理与额外运维成本。

- 额外写入、清理任务和 relay 运维。
- 事件格式演进和旧消费者兼容。
- 记录清理必须与消费重放、审计保留期协调。

它的保证范围从同一数据库事务开始；外部副作用、跨系统一次性效果和业务顺序仍需各自设计。

## 待执行的故障验证

在 Broker 接收后、relay 标记前主动终止 relay；恢复后验证重复投递不重复改变消费方本地状态。再测试毒消息、Broker 不可用、顺序变化和去重记录过期。

本仓库尚未实现 relay/Broker 集成实验，上述内容是后续验证计划。随附 SQLite API 实验验证的是本地事务与去重，不覆盖消息投递和消费恢复。

自检：画出业务提交、Broker 确认、relay 进度记录和消费提交的边界，逐个指出“已成功但尚未记录”的窗口，以及重试为何可能产生重复。

## 关联模式与概念

- [API 幂等性](../api/idempotency.md)：消费去重和外部调用重试依赖稳定操作标识与结果复用。
- [Agent 工具恢复](../ai/recoverable-runtime.md)：同样需要处理外部已成功、本地尚未记录的故障窗口。
- [库存并发](../database/concurrent-inventory.md)：先在事务内守住库存与预订的不变量，再记录待发布事件。
- [一致性与复制](../distributed/consistency-and-replication.md)：本地事务提交、消息投递和下游可见分别说明保证范围。

## 来源与核查

- [AWS：Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)；核查日期 2026-10-16，覆盖双写问题、事务记录和重复处理边界。
