<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 消息队列与事件驱动

建议优先级：P1。目标：把投递、消费、业务效果和顺序分开设计。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

消息已确认投递，为什么仍可能重复执行业务？

## 已有正文

- [Transactional Outbox：让业务变化留下可投递的记录](transactional-outbox.md)：用数据库事务保存发布意图，并明确 relay、重复投递与消费去重的责任。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| MQ / Pub-Sub / Event Streaming | 队列分发、广播订阅和可重放事件流。 |
| Producer / Consumer / Broker | 消息写入、处理与服务端存储分发角色。 |
| Topic / Partition / Offset | 主题、分区和分区内位置。 |
| Consumer Group | 多个消费者协作分担读取。 |
| At-most-once / At-least-once | 可能丢失不重投与可能重复的投递保证。 |
| Exactly-once Semantics | 在明确组件和事务范围内限制重复处理效果。 |
| Idempotent Consumer | 重复消费仍保持受约束的业务效果。 |
| Ordering / Partition Key | 在指定范围内维持顺序。 |
| Dead Letter Queue / Retry Queue | 隔离持续失败消息与安排重试。 |
| Backpressure | 下游将容量压力传回上游。 |
| Transactional Outbox | 同一事务记录业务变化和待发布事件。 |
| CDC / Asynchronous Processing | 捕获数据变化并解耦后续处理。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
