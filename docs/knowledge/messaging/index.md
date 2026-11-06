<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 消息队列与事件驱动

建议优先级：P1。目标：把投递、消费、业务效果和顺序分开设计。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

消息已确认投递，为什么仍可能重复执行业务？

## 已有正文

- [消息投递与确认：为什么处理成功后还会收到同一条消息](delivery-acknowledgements-and-idempotency.md)：沿生产、[Broker](../../glossary/messaging.md#messaging.roles)、消费与业务提交区分确认边界，解释重复、消费[幂等](../../glossary/api.md#api.idempotency)、顺序和重放。
- [事件格式演进：新旧消费者与历史回放怎样保持同一含义](event-contracts-schema-evolution-and-replay.md)：区分事件身份、载荷结构与业务语义，用读写版本矩阵解释兼容方向、历史适配、分阶段发布和回放副作用。
- [事件时间与窗口：水位线之后的迟到数据怎样修正结果](event-time-watermarks-windows-and-late-data.md)：区分[事件时间](../../glossary/messaging.md#messaging.event-time)与处理时间，解释窗口归属、水位线、触发、累积模式、[允许迟到](../../glossary/messaging.md#messaging.late-data)和多分区进度。
- [分区、消费组与偏移：提交位置为什么不等于处理完成](partitions-consumer-groups-and-offsets.md)：围绕 Kafka 4.1 普通[消费组](../../glossary/messaging.md#messaging.groups)区分日志位置、分区分工、业务完成与偏移提交，解释重复、乱序和重平衡。
- [队列、发布订阅与事件流：谁会收到消息，谁还能读到历史](queues-pubsub-event-streams-and-retention.md)：按工作分配、独立订阅及保留位置区分消息模型，说明消费组、断线历史、确认、重放和业务效果的关系。
- [Transactional Outbox：让业务变化留下可投递的记录](transactional-outbox.md)：用[数据库事务](../../glossary/database.md#database.isolation)保存发布意图，并明确 relay、重复投递与消费去重的责任。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [MQ / Pub-Sub / Event Streaming](../../glossary/messaging.md#messaging.models) | [队列](../../glossary/algorithms.md#algorithms.queues)分发、广播订阅和可重放事件流。 |
| [Producer / Consumer / Broker](../../glossary/messaging.md#messaging.roles) | 消息写入、处理与服务端存储分发角色。 |
| [Topic / Partition / Offset](../../glossary/messaging.md#messaging.positions) | 主题、分区和分区内位置。 |
| [Consumer Group](../../glossary/messaging.md#messaging.groups) | 多个消费者协作分担读取。 |
| [At-most-once / At-least-once](../../glossary/messaging.md#messaging.delivery) | 可能丢失不重投与可能重复的投递保证。 |
| [Exactly-once Semantics](../../glossary/messaging.md#messaging.exactly-once) | 在明确组件和事务范围内限制重复处理效果。 |
| [Idempotent Consumer](../../glossary/messaging.md#messaging.consumer-idempotency) | 重复消费仍保持受约束的业务效果。 |
| [Ordering / Partition Key](../../glossary/messaging.md#messaging.ordering) | 在指定范围内维持顺序。 |
| [Dead Letter Queue / Retry Queue](../../glossary/messaging.md#messaging.retry-dlq) | 隔离持续失败消息与安排[重试](../../glossary/api.md#api.retries)。 |
| [Backpressure](../../glossary/messaging.md#messaging.backpressure) | 下游将容量压力传回上游。 |
| [Transactional Outbox](../../glossary/messaging.md#messaging.outbox) | 同一事务记录业务变化和待发布事件。 |
| [CDC / Asynchronous Processing](../../glossary/messaging.md#messaging.cdc) | 捕获数据变化并解耦后续处理。 |
| [Event Contract / Event Schema Evolution](../../glossary/messaging.md#messaging.event-contract) | 约定事件身份、载荷结构与事实含义，保护新旧读写及历史回放的兼容范围。 |
| [Event Time / Event-time Watermark](../../glossary/messaging.md#messaging.event-time) | 用记录携带的发生时间归类，并用水位线表达事件时间进度；处理时间则来自实际执行时钟。 |
| [Window / Trigger / Pane](../../glossary/messaging.md#messaging.windows) | 窗口决定数据分组范围，触发器决定何时输出，pane 是一次触发产生的结果。 |
| [Late Data / Allowed Lateness](../../glossary/messaging.md#messaging.late-data) | 水位线越过事件所属窗口后到达的数据，以及系统继续保留状态并接受修订的期限。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
