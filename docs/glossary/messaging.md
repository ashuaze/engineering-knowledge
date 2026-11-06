<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 消息队列与事件驱动词汇表

本页解释 16 组术语，按[完整术语索引](../glossary.md#messaging)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [消息队列与事件驱动文章](../knowledge/messaging/index.md)

## 本页术语

- [MQ / Pub-Sub / Event Streaming](#messaging.models)
- [Producer / Consumer / Broker](#messaging.roles)
- [Topic / Partition / Offset](#messaging.positions)
- [Consumer Group](#messaging.groups)
- [At-most-once / At-least-once](#messaging.delivery)
- [Exactly-once Semantics](#messaging.exactly-once)
- [Idempotent Consumer](#messaging.consumer-idempotency)
- [Ordering / Partition Key](#messaging.ordering)
- [Dead Letter Queue / Retry Queue](#messaging.retry-dlq)
- [Backpressure](#messaging.backpressure)
- [Transactional Outbox](#messaging.outbox)
- [CDC / Asynchronous Processing](#messaging.cdc)
- [Event Contract / Event Schema Evolution](#messaging.event-contract)
- [Event Time / Event-time Watermark](#messaging.event-time)
- [Window / Trigger / Pane](#messaging.windows)
- [Late Data / Allowed Lateness](#messaging.late-data)

<a id="messaging.models"></a>

## MQ / Pub-Sub / Event Streaming

**ID：** `messaging.models` · **建议优先级：** P1

**别名 / 检索词：** MQ、Pub-Sub、Event Streaming、消息队列、发布订阅、事件流

**简释：** 队列分发、广播订阅和可重放事件流。

工作队列在同一工作池分担，发布订阅提供独立接收范围，事件日志保存位置与历史；这些维度可以组合。断线补读受保留/压缩及进度约束，确认和重放不自动保证外部效果恰好一次。

**例子：** 任务队列让一个工作者处理任务，事件流可让多个独立消费组各自读取。

**深入阅读：** [队列、发布订阅与事件流：谁会收到消息，谁还能读到历史](../knowledge/messaging/queues-pubsub-event-streams-and-retention.md)

<a id="messaging.roles"></a>

## Producer / Consumer / Broker

**ID：** `messaging.roles` · **建议优先级：** P1

**别名 / 检索词：** Producer、Consumer、Broker、生产者、消费者、消息代理

**简释：** 消息写入、处理与服务端存储分发角色。

Producer 写入消息，Broker 接收、存储与分发，Consumer 读取并执行业务处理。每一阶段都有独立确认边界，写入确认不证明消费者已完成业务。

**例子：** 生产者收到 Broker 确认后，通知短信仍可能尚未发送。

**深入阅读：** [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md)

<a id="messaging.positions"></a>

## Topic / Partition / Offset

**ID：** `messaging.positions` · **建议优先级：** P1

**别名 / 检索词：** Topic、Partition、Offset、消息主题、偏移量

**简释：** 主题、分区和分区内位置。

Topic 是消息的逻辑集合，Partition 是其中有序的日志分片，Offset 标识分片内位置。偏移只在对应分区中有意义，不能直接比较不同分区的全局业务顺序。

**例子：** 同一业务键路由到同一分区，才能在该分区提供的顺序上进一步处理。

**深入阅读：** [分区、消费组与偏移：提交位置为什么不等于处理完成](../knowledge/messaging/partitions-consumer-groups-and-offsets.md) · [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md)

<a id="messaging.groups"></a>

## Consumer Group

**ID：** `messaging.groups` · **建议优先级：** P1

**别名 / 检索词：** Consumer Group、消费组

**简释：** 多个消费者协作分担读取。

消费组让多个消费者协作处理分区；具体分配与重平衡规则由 Broker 和客户端协议决定。成员变化可能造成处理重叠，业务完成与提交位置需协调。

**例子：** 一个消费者完成处理但提交前退出，分区转移后消息可能再次被处理。

**深入阅读：** [分区、消费组与偏移：提交位置为什么不等于处理完成](../knowledge/messaging/partitions-consumer-groups-and-offsets.md)

<a id="messaging.delivery"></a>

## At-most-once / At-least-once

**ID：** `messaging.delivery` · **建议优先级：** P1

**别名 / 检索词：** At-most-once、At-least-once、至多一次、至少一次

**简释：** 可能丢失不重投与可能重复的投递保证。

至多一次允许失败时丢失而不重投，至少一次通过重投降低丢失风险但允许重复。保证应说明起止边界、持久化和确认条件。

**例子：** 先确认再执行业务可能丢工作，业务后确认则可能因确认丢失而重复。

**深入阅读：** [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md)

<a id="messaging.exactly-once"></a>

## Exactly-once Semantics

**ID：** `messaging.exactly-once` · **建议优先级：** P1

**别名 / 检索词：** Exactly-once Semantics、恰好一次

**简释：** 在明确组件和事务范围内限制重复处理效果。

Exactly-once 仅在明确的组件、状态和事务范围内有意义。消息系统内的事务不自动覆盖外部数据库、支付或邮件，需要额外协调可观察的业务效果。

**例子：** 日志读写在 Broker 事务内完成，不代表外部扣款也被同一事务保护。

**深入阅读：** [Transactional Outbox：让业务变化留下可投递的记录](../knowledge/messaging/transactional-outbox.md) · [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) · [分区、消费组与偏移：提交位置为什么不等于处理完成](../knowledge/messaging/partitions-consumer-groups-and-offsets.md)

<a id="messaging.consumer-idempotency"></a>

## Idempotent Consumer

**ID：** `messaging.consumer-idempotency` · **建议优先级：** P1

**别名 / 检索词：** Idempotent Consumer、幂等消费者

**简释：** 重复消费仍保持受约束的业务效果。

幂等消费者将消息身份与业务修改关联，使重复投递保持约定效果。去重标识的作用域、保留期和与业务写入的原子关系决定保证。

**例子：** 把事件 ID 去重记录和余额修改放在同一数据库事务中。

**深入阅读：** [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) · [分区、消费组与偏移：提交位置为什么不等于处理完成](../knowledge/messaging/partitions-consumer-groups-and-offsets.md) · [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)

<a id="messaging.ordering"></a>

## Ordering / Partition Key

**ID：** `messaging.ordering` · **建议优先级：** P1

**别名 / 检索词：** Ordering、Partition Key、分区键、消息顺序

**简释：** 在指定范围内维持顺序。

消息顺序需点名业务键、分区或消费执行范围。Broker 有序交付后，应用并行处理、失败重试和跨分区合并仍可能打乱完成顺序。

**例子：** 同一订单的取消不应在创建前生效，可按订单键路由并验证业务版本。

**深入阅读：** [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) · [分区、消费组与偏移：提交位置为什么不等于处理完成](../knowledge/messaging/partitions-consumer-groups-and-offsets.md) · [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)

<a id="messaging.retry-dlq"></a>

## Dead Letter Queue / Retry Queue

**ID：** `messaging.retry-dlq` · **建议优先级：** P1

**别名 / 检索词：** Dead Letter Queue、Retry Queue、死信队列、重试队列

**简释：** 隔离持续失败消息与安排重试。

重试队列安排暂时失败后的再次处理，死信队列隔离持续失败或无法处理的消息。需保留原因、次数与回放方式，并限制重试放大。

**例子：** 修复消息格式后回放死信，仍要防止已成功的副作用再次执行。

**深入阅读：** [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) · [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)

<a id="messaging.backpressure"></a>

## Backpressure

**ID：** `messaging.backpressure` · **建议优先级：** P1

**别名 / 检索词：** Backpressure、消息背压

**简释：** 下游将容量压力传回上游。

消息背压把下游处理能力反馈给生产或拉取端，限制在途与缓存。仅把积压移到 Broker 不代表容量问题消失，仍需检查保留与磁盘上限。

**例子：** 消费者降低拉取并发后，监控积压增长和预计保留窗口。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md) · [消息投递与确认：为什么处理成功后还会收到同一条消息](../knowledge/messaging/delivery-acknowledgements-and-idempotency.md) · [背压与有界队列：把等待放在哪里](../knowledge/performance/backpressure-and-bounded-queues.md)

<a id="messaging.outbox"></a>

## Transactional Outbox

**ID：** `messaging.outbox` · **建议优先级：** P1

**别名 / 检索词：** Transactional Outbox、事务发件箱、Outbox

**简释：** 同一事务记录业务变化和待发布事件。

Outbox 在同一数据库事务中写入业务状态和待发布事件，再由独立发布者发送。它解决提交与记录发送意图的原子性，发布和消费仍可能重复。

**例子：** 订单提交后服务崩溃，发布者恢复后可继续读取 Outbox 并发送事件。

**深入阅读：** [Transactional Outbox：让业务变化留下可投递的记录](../knowledge/messaging/transactional-outbox.md) · [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md)

<a id="messaging.cdc"></a>

## CDC / Asynchronous Processing

**ID：** `messaging.cdc` · **建议优先级：** P1

**别名 / 检索词：** CDC、Asynchronous Processing、异步处理

**简释：** 捕获数据变化并解耦后续处理。

CDC 从日志或变更接口捕获已提交变化，用于异步下游处理。需管理位置、重放、模式变化和断点，变更记录也不一定等于完整业务事件。

**例子：** 同步行更新到搜索索引时，需要保证删除、重放和版本更新不会互相覆盖。

**深入阅读：** [索引重建、增量追赶与切换：怎样覆盖期间的新增和删除](../knowledge/cache-search/index-rebuild-watermarks-and-cutover.md) · [CDC：快照、变更位置与重放怎样接成连续的数据流](../knowledge/database/cdc-snapshots-log-positions-and-replay.md)

<a id="messaging.event-contract"></a>

## Event Contract / Event Schema Evolution

**ID：** `messaging.event-contract` · **建议优先级：** P1

**别名 / 检索词：** Event Contract、Event Schema Evolution、事件契约、事件格式演进

**简释：** 约定事件身份、载荷结构与事实含义，保护新旧读写及历史回放的兼容范围。

事件契约分别定义信封身份、业务对象、格式定位和语义；兼容检查要说明writer/reader方向及历史集合。CloudEvents信封、Avro/Protobuf编码与Schema Registry检查不是同义机制。结构可解析不证明默认值、金额单位、权限与副作用正确，历史适配和双发回放需保留来源及业务去重边界。

**例子：** 新增币种默认CNY只有在历史金额确实按人民币记录时才保留含义；相邻版本通过也不证明新读者能读取全部历史。

**深入阅读：** [事件格式演进：新旧消费者与历史回放怎样保持同一含义](../knowledge/messaging/event-contracts-schema-evolution-and-replay.md) · [事件溯源：事件流怎样成为事实，快照与投影怎样安全重建](../knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md) · [事件时间与窗口：水位线之后的迟到数据怎样修正结果](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md)

<a id="messaging.event-time"></a>

## Event Time / Event-time Watermark

**ID：** `messaging.event-time` · **建议优先级：** P1

**别名 / 检索词：** Event Time、Event-time Watermark、事件时间、事件时间水位线

**简释：** 用记录携带的发生时间归类，并用水位线表达事件时间进度；处理时间则来自实际执行时钟。

事件时间描述业务事实发生的时间，处理时间描述算子实际处理记录的时间；水位线是系统对事件时间进度的声明或估计。水位线越快结果越早但迟到可能越多，越慢则状态和输出延迟增加。它不证明生产者时钟正确，也不等于消息偏移或墙钟截止时间。

**例子：** 10:02发生的交易在10:06到达，事件时间窗口仍可把它归入10:00到10:05；是否接受修订由水位线和迟到策略决定。

**深入阅读：** [事件时间与窗口：水位线之后的迟到数据怎样修正结果](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md)

<a id="messaging.windows"></a>

## Window / Trigger / Pane

**ID：** `messaging.windows` · **建议优先级：** P1

**别名 / 检索词：** Event-time Window、Window Trigger、Result Pane、事件时间窗口、窗口触发、结果分片

**简释：** 窗口决定数据分组范围，触发器决定何时输出，pane 是一次触发产生的结果。

滚动、滑动和会话窗口定义元素属于哪些有限分组；触发器可按水位、处理时间或数据条件提前、按时或迟到输出。多次 pane 还需约定累积、丢弃或撤回语义，下游才能判断是覆盖旧值还是应用增量。

**例子：** 同一五分钟窗口先输出累计和10，迟到事件到达后输出13；累积语义下应覆盖为13，不能再相加得到23。

**深入阅读：** [事件时间与窗口：水位线之后的迟到数据怎样修正结果](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md)

<a id="messaging.late-data"></a>

## Late Data / Allowed Lateness

**ID：** `messaging.late-data` · **建议优先级：** P1

**别名 / 检索词：** Late Data、Allowed Lateness、迟到数据、允许迟到

**简释：** 水位线越过事件所属窗口后到达的数据，以及系统继续保留状态并接受修订的期限。

迟到是相对于水位线与窗口边界定义的，不只看墙钟延迟。Allowed lateness 让窗口在首次按时输出后继续保留到指定的事件时间/水位边界，需要保存状态并明确下游更新协议；它不是首次输出后等待相同墙钟时长。超过边界的数据仍需丢弃、旁路或离线更正策略。

**例子：** 水位线越过10:05后，10:02的事件在允许迟到期内可把窗口结果从10修订为13；状态清理后再到达则进入旁路。

**深入阅读：** [事件时间与窗口：水位线之后的迟到数据怎样修正结果](../knowledge/messaging/event-time-watermarks-windows-and-late-data.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Apache Kafka：分区、复制与投递设计](https://kafka.apache.org/41/design/design/)
- [CloudEvents v1.0.2 specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
- [Apache Avro 1.12.0 Specification](https://avro.apache.org/docs/1.12.0/specification/)
- [Protocol Buffers proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)
- [Confluent Schema Evolution and Compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- [Confluent SerDes and subject name strategy](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html)
- [Axon Event Versioning](https://docs.axoniq.io/axon-framework-reference/4.12/events/event-versioning/)
- [Debezium3.3 PostgreSQL：事件与事务元数据](https://debezium.io/documentation/reference/3.3/connectors/postgresql.html)
- [RabbitMQ Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python)
- [Publish/Subscribe](https://www.rabbitmq.com/tutorials/tutorial-three-python)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
