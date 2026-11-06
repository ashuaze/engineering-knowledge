---
id: "kb-messaging-models"
title: "队列、发布订阅与事件流：谁会收到消息，谁还能读到历史"
kind: "concept"
domain: "messaging"
status: "evolving"
summary: "按工作分配、独立订阅及保留位置区分消息模型，说明消费组、断线历史、确认、重放和业务效果的关系。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-messaging-delivery-semantics"]
related: ["kb-messaging-partitions-offsets", "kb-messaging-event-evolution", "kb-messaging-outbox", "kb-performance-backpressure"]
tags: ["queue", "pub-sub", "event-streaming", "retention", "replay"]
---

# 队列、发布订阅与事件流：谁会收到消息，谁还能读到历史

学习入口：给服务加了两个[消费者](../../glossary/messaging.md#messaging.roles)，为什么有时共同分担，有时各收到一份？订阅者离线后还能否补读，又取决于什么？应分别说明分发单位、保留策略与确认/位置。

前置：[投递与确认](delivery-acknowledgements-and-idempotency.md)。本文用RabbitMQ官方教程和Kafka4.1模型作参照，不把产品名称与单一模型绑定；事件、数量和恢复过程为纸面设计，没有启动Broker或消费[进程](../../glossary/systems.md#systems.execution-units)。

## 分发方式与保存历史是不同维度

| 视角 | 核心组织方式 | 仍需另行确定 |
| --- | --- | --- |
| 工作[队列](../../glossary/algorithms.md#algorithms.queues) | 将工作分给同一工作池中的消费者 | 确认、重投、并发和顺序 |
| [发布订阅](../../glossary/messaging.md#messaging.models) | 同一发布可送往多个独立订阅范围 | 订阅是否持久、离线如何处理 |
| 可保留事件日志 | 按位置保存记录，读者维护自己的进度 | 保留/压缩、位置失效及重放效果 |

这些维度可以组合。[RabbitMQ Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python)展示多个工作者共享工作；[Publish/Subscribe](https://www.rabbitmq.com/tutorials/tutorial-three-python)则通过交换器与多个队列表达独立接收。一个订阅队列内部仍可有多个消费者分担。

因此“发布订阅”不必然等于没有历史或没有确认，“事件流”也不必然意味着所有消费者都得到逐条广播。要回到所用订阅、[消费组](../../glossary/messaging.md#messaging.groups)和存储配置判断。

## 先定义独立订阅，再计算消费者关系

教学例：有四个事件，账务和通知是两个独立订阅，各自都需要全部四个。忽略重投时，两者一共需要处理八次逻辑投递；账务订阅增加两个工作者，只是在其内部分享四项，不会自动让每个工作者各收到完整四项。

若错误地把账务和通知放在同一个竞争工作池，就可能各拿到部分事件，无法完成双方独立职责。反过来，如果扣款工作被放进两个独立订阅，不能因基础设施“各送了一份”就认定两次扣款都是正确业务效果。

## 位置与保留共同决定能否补读

[Kafka4.1设计说明](https://kafka.apache.org/41/design/design/)描述事件保留、分区及消费进度。读取事件通常不直接删除该事件；不同组可以有不同进度，但仍受保留与日志清理规则约束。

本例日志含位置101至104，提交位置被定义为“下一条待处理位置”。读者处理完102后保存103，重启从103继续；这个约定不是所有系统通用API。如果103已被清理，保存了位置也不能凭空找回记录，需要重建或其他恢复来源。

压缩日志可能按键保留必要状态而非所有历史变化；需要审计完整事件链时，应检查真实保留承诺。消息持久化、订阅持久化与消费者进度持久化也不是同一个配置。

## 确认和重放不自动解决业务重复

消费者写库成功、尚未确认就断开，仍可能再次处理相同消息。多个订阅分别确认，各自的失败也不会自动撤销另一订阅的成功。

事件日志可重读，不表示旧邮件、付款和外部工具应该再次执行。按业务操作身份设计[幂等](../../glossary/api.md#api.idempotency)、投影重建与副作用隔离，见[事件格式演进与回放](event-contracts-schema-evolution-and-replay.md)。

## 顺序与容量也要限定范围

分区内位置顺序不自动成为跨分区全局顺序；工作者并发也可能改变完成先后。需要按业务键串行、接受乱序或重新排序，应在契约中明确，不能只看到“消息按序进入”就推出结果按序提交。

持久存储让积压可见并可恢复，但不是无限容量。离线订阅、重放和慢处理会消耗磁盘、带宽及下游能力；保留期限、[背压](../../glossary/performance.md#performance.queueing)和停止条件需一起规划。

## 自检

1. 工作队列、独立订阅和事件日志分别改变什么？
2. 四事件、两订阅为什么是八次逻辑处理，而不是每个工作者各四次？
3. 本例保存103代表什么？若记录已清理，为什么位置不够？
4. 为什么持久化、确认和重放都不能单独保证外部效果[恰好一次](../../glossary/messaging.md#messaging.exactly-once)？
5. 分区顺序、完成顺序和历史保留分别受哪些条件限制？

## 来源与核查

2026-10-27 核查RabbitMQ工作队列/发布订阅官方教程及Kafka4.1设计与日志清理说明。本文为source-checked；没有运行教程、验证Broker配置、订阅/偏移恢复、消息重放或真实副作用。
