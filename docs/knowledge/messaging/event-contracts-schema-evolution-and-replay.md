---
id: "kb-messaging-event-evolution"
title: "事件格式演进：新旧消费者与历史回放怎样保持同一含义"
kind: "concept"
domain: "messaging"
status: "evolving"
summary: "区分事件身份、载荷结构与业务语义，用读写版本矩阵解释兼容方向、历史适配、分阶段发布和回放副作用。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-messaging-delivery-semantics", "kb-messaging-partitions-offsets"]
related: ["kb-messaging-outbox", "kb-api-contracts-pagination", "kb-engineering-contract-compatibility", "kb-database-schema-migrations", "kb-api-idempotency", "kb-security-object-authorization", "kb-database-cdc", "kb-architecture-event-sourcing", "kb-messaging-event-time-windows", "kb-runtime-serialization"]
tags: ["events", "schema-evolution", "compatibility", "replay", "identity"]
---

# 事件格式演进：新旧消费者与历史回放怎样保持同一含义

字段编号与格式兼容之外，数值精度、缺失/null、共享身份和原始字节还需分别验收，见[序列化与反序列化](../runtime/serialization-representations-schemas-and-identity.md)。新文不表示本文的编码器、Registry 或历史回放已完成集成验证。

学习入口：[生产者](../../glossary/messaging.md#messaging.roles)只增加了一个金额币种字段，在线消费没有报错，为什么重放旧消息后账目却变了？旧消费者仍在线、新消费者还会读取历史数据时，演进需要同时保护事件身份、解析规则、业务含义与副作用；Schema 检查通过只覆盖其中一部分。

前置：[消息确认与幂等](delivery-acknowledgements-and-idempotency.md)、[分区与消费位置](partitions-consumer-groups-and-offsets.md)。本文依据 CloudEvents v1.0.2、Avro 1.12.0 及核查日的官方演进资料；表格、订单字段和发布顺序为纸面教学设计，没有编码消息、配置 Registry、部署新旧客户端或执行回放实验。

## 同一事件、同一订单与同一格式分别是什么

事件信封承载便于路由、识别和解释的上下文，载荷保存业务事实；两者均需要契约。下面以 CloudEvents 为信封参照，并非要求所有消息系统采用它。

| 标识或属性 | 回答的问题 | 不能当作什么 |
| --- | --- | --- |
| `source` 与 `id` | 在来源范围内识别这一次事件；重发的重复事件可保留身份 | 订单 ID、处理成功证明或天然全局顺序 |
| `subject` 或应用的 `order_id` | 这件事与哪个业务对象有关；具体映射由契约约定 | 同一订单所有事件共用的去重 ID |
| `type` | 这是什么业务事件，交给哪种处理逻辑解释 | 所有版本均有相同语义的保证 |
| `dataschema`、产品的 schema ID | 载荷依照哪个结构定义解释 | 事件身份或业务动作标识 |
| 应用的载荷版本、Registry 的 subject/version | 某种载荷契约或注册范围内的演进位置 | CloudEvents `specversion`，也不是对象状态版本 |
| `time`、对象序列、分区位置 | 分别表达发生时间、业务顺序或日志位置 | 可以互相替换的同一全序 |

[CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)把 `source` 与 `id` 的组合用于唯一识别不同事件；`specversion` 表示信封规范，此规范版本的属性值仍为 `1.0`。载荷不兼容变化应以不同的 `dataschema` URI 反映，事件类型的语义及版本约定仍由生产方负责。

同一订单可以先后产生创建、支付、取消事件；用订单 ID 去重会错丢后续事实。重投一个已有事件时随手生成新 ID，又可能绕过去重。若相同事件身份出现非预期的不同内容，应作为冲突核查，不能默认后者覆盖前者。时间戳也不自动给并发事件排出可靠顺序，应另定对象版本和缺口处理，不能只取“时间最大的一条”。

Confluent Schema Registry 的 [subject 说明](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html)区分注册命名范围、版本与结构身份：兼容检查按 subject 进行，版本依附 subject；相同结构在不同 subject 下可以拥有同一 schema ID。主题名、subject 名、CloudEvents `subject` 不是同一个概念。回放还需能找到消息对应的原始结构定义；删除历史定义不因“最新 Schema 还在”就变得安全。

## 兼容方向由谁读谁决定

把写出数据的一侧称为 writer，读入的一侧称为 reader。设 W1、W2 分别按 v1、v2 写出数据，R1、R2 分别按 v1、v2 解释；格式能解码的方向如下：

| Registry 策略名 | 主要检查的关系 | 不自动保证什么 |
| --- | --- | --- |
| BACKWARD | 新读者 R2 能读旧写者 W1 的数据 | 老读者 R1 能读 W2 |
| FORWARD | 老读者 R1 能读新写者 W2 的数据 | 新读者 R2 能读历史 W1 |
| FULL | 上面两个方向都成立 | 单位、权限、默认含义和副作用正确 |
| 带 TRANSITIVE 的相应策略 | 把相应方向扩展到该 subject 的全部先前注册版本 | 未纳入的历史格式、别的 subject、任意消费代码和未来版本 |

这些名称依据 [Confluent 官方兼容说明](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)，属于具体 Registry 的检查政策。非传递模式主要比较最新已有版本；不能靠相邻版本逐次通过推导所有历史都可回放。Avro、[Protobuf](../../glossary/api.md#api.contracts) 和 JSON Schema 的规则各有区别，不能只复制“新增字段兼容”的结论。

## 用 Avro 默认字段复算一个读写矩阵

教学设定：同名同命名空间的 `OrderPaid` record，v1 包含 `order_id: string`、`total_minor: long`；v2 保留这些字段，增加 `currency: string`，其读者默认值为 `"CNY"`。约定历史金额确实全部以人民币分记录；以下只根据 Avro 1.12.0 解析规则推演，不是[序列化](../../glossary/runtime.md#runtime.serialization)测试。

| reader / writer | W1：没有 currency 字段 | W2：含合法 currency 字段 |
| --- | --- | --- |
| R1：只识别 v1 | 原字段可解析 | 忽略读者未定义的 currency |
| R2：识别 v2，提供默认值 | 读者用默认值补出 CNY | 读取写者提供的币种 |

四格在这些结构前提下都可解析，才支持这个变更的双向结构判断。去掉 R2 的默认值后，R2/W1 会因缺失字段而失败，R1/W2 仍可能成立，方向就不再相同。[Avro 1.12.0 的 Records 与 Schema Resolution](https://avro.apache.org/docs/1.12.0/specification/)规定按字段名匹配、忽略读者不认识的写者字段，以及缺失时使用读者默认值的规则。

默认值用于读取缺字段的旧数据，不使 v2 写者可以任意省略编码字段；显式 `null` 也不会自动被替换成 CNY。字段若仅声明 string，null 本身不符合其类型；要允许 null，需按相应格式另行声明，并决定它在业务上代表未知、清空还是无值。

若历史并非全是人民币，填入 CNY 会制造虚假事实；应采用能表达未知的模型，或使用可证明的历史依据转换。保持字段仍为 long，却把 `total_minor` 从分改成元，也可能通过结构检查而改变金额。结构默认、业务默认和数据修复不能混为一项。

相邻兼容不传递的另一条 Avro 纸面反例：其余字段与 record 名不变，v1 有 `memo: string`；v2 删除 memo；v3 增加 `memo: int` 并提供默认 0。R2/W1 忽略 memo，R3/W2 补 0，两个相邻 BACKWARD 关系成立；R3/W1 却遇到 string 与 int 不匹配而失败。三代读者与三代写者共有 `3 × 3 = 9` 个组合，业务未必需要全部支持，但应明确在线、回退和回放会出现哪些格子，而不是只验证最新一格。

## 重命名、未知字段与语义仍要单独检查

Avro 可以通过读者别名参与名称匹配，但需要所用实现支持并验证实际规则；仅把字段改名不证明历史数据仍能正确映射。类型推广也有方向，不能把所有整数、字符串或枚举互换。若改动改变了事件的事实含义，应设计明确的新契约及过渡关系，而非给旧字段换个名字。

Protobuf 的二进制字段号和 JSON 字段表示又是另一套机制。[Proto3 演进指南](https://protobuf.dev/programming-guides/proto3/#updating)区分二进制安全变化、条件兼容及业务代码影响，删除字段后不能复用原编号。其[未知字段说明](https://protobuf.dev/programming-guides/proto3/#unknowns)指出二进制消息可保留未知字段，转成 JSON 或逐字段重建对象却可能丢失它们。旧中继能读取并再次发送，不等于新增信息经过整条链路仍然存在。

因此测试路径需要经过实际序列化、传输、中继、反序列化和消费代码；结构之外再断言金额单位、枚举未知分支、缺失/null、字段权限与错误处理。相关证据范围见[契约测试与版本兼容](../engineering/contract-testing-and-compatibility.md)。格式之间的转换本身也属于待验证边界。

## 历史适配改变读入视图，不应悄悄改写事实

Upcasting 指按明确规则把历史结构适配为当前可处理的结构。[Axon Event Versioning](https://docs.axoniq.io/axon-framework-reference/4.12/events/event-versioning/)说明手写转换链与保留原历史的思路；本篇只取这一机制，不依赖其具体类或部署版本。

本文采用一对一的读入适配：保留原始字节或可追溯原记录、原始事件身份与 writer 定义，另外记录转换器版本及生成的当前视图。不能在每次回放时读取“今天的汇率/客户地区”来猜历史值，否则同一历史会随外部状态改变结果。转换必须说明输入版本、确定的依据、异常路径及输出含义；历史里不存在的信息不能靠默认值证明曾经发生。

若确实需要修正一项错误事实，应另定更正事件或受控数据修复流程，不能把修复静默塞进结构适配。若将适配结果再发布，还须明确它是原事件的另一表示还是新的衍生事件，并保留来源关联；不是所有框架的转换都会一对一，更复杂的拆分需要另定身份和顺序。

当[事件流](../../glossary/messaging.md#messaging.models)本身是权威状态来源时，历史兼容还决定聚合能否重建，见[事件溯源](../architecture/event-sourcing-streams-snapshots-and-projections.md)。当[事件时间](../../glossary/messaging.md#messaging.event-time)字段参与窗口归属时，改变字段含义或重打时间戳会改变历史统计，见[事件时间与窗口](event-time-watermarks-windows-and-late-data.md)。

## 发布、双发与回退都要保护同一个业务动作

下面是在“只保证新读者读旧数据”的情形下设计的过渡次序，不是任意系统的通用部署命令：

| 阶段 | 允许的状态 | 必须留下的证据 |
| --- | --- | --- |
| 准备 | 仍由 W1 发布；验证 R2 读取 W1、W2 及需保留的历史 | 结构、语义、权限和未知值处理均覆盖实际版本组合 |
| 扩展读者 | 部署可读新旧格式的 R2，旧消费者退出对应路径 | 在线、后台、备用恢复和离线任务均纳入清单 |
| 切换写者 | 启用 W2，观测失败、积压与错误隔离 | 真实编码格式、subject/定义获取和路由均匹配 |
| 收缩 | 结束旧发布路径，按约定保留历史读取与回退能力 | 已持久保存的 W2 不会因回退应用而变成 W1 |

若直接采用双发旧、新记录，必须先定义两条记录之间的事实关系。重投已有事件保持其身份；真正新建的衍生事件使用自己的身份并关联原始事件。两路若最终触发同一业务动作，还要保留稳定的业务动作标识，在合流和副作用边界去重；不能让两个新事件 ID 导致扣款两次，也不能只因 payload 字节不同就把已约定的格式转换当作新事实。

双写两次发布还可能只成功一边、先后顺序不同，需持久记录发布意图和补偿/核对进度。[Transactional Outbox](transactional-outbox.md)可把本地业务变化与发送意图放入同一事务，仍不自动实现两路投递或消费的[恰好一次](../../glossary/messaging.md#messaging.exactly-once)；Broker 内事务也不能自动覆盖外部数据库、支付和邮件。格式变化与投递保证应分别验收。

回退代码不能撤回已经发布和持久保存的新格式，类似[数据库迁移兼容](../database/schema-migrations-and-compatibility.md)中的不可逆数据边界。不要为了让回退成功而无约束删除历史定义或消费进度。

## 回放要重新限定结果、权限与副作用

重建查询投影可以使用明确的新投影代次，并把原事件身份与该投影的处理记录关联，避免新旧投影互相污染。恢复同一支付动作则应保留原业务去重范围；删除已处理记录或换一个消费者名称，不代表再次扣款已经合理。保留期须覆盖重复、回退与历史回放窗口，具体[原子性](../../glossary/systems.md#systems.atomicity)见[消息确认与消费幂等](delivery-acknowledgements-and-idempotency.md)。

历史发生过某件事，也不意味着今天任意操作者都有权读它、重新发通知或向外部系统执行动作。回放需要明确执行主体、当前权限、目标数据范围、允许的副作用与可停止条件，见[对象级授权](../security/object-level-authorization.md)。事件时间、对象序列和分区偏移分别处理；不能跨分区仅靠时间排序重建因果，累加型事件也不能统一按最大版本丢弃前项。

未知 schema ID、无法解析、未知业务版本和内容冲突应区分处理。保留受控的原始材料、来源位置、失败原因及尝试记录，使用有容量和权限边界的隔离/死信流程；进入[死信队列](../../glossary/messaging.md#messaging.retry-dlq)不是业务成功，也不证明安全跳过后继续的投影已完整。修复后回放仍需核对原副作用和去重记录，不能让毒消息无限[重试](../../glossary/api.md#api.retries)拖垮正常消费。

从数据库行变化形成输入时，另见[CDC](../database/cdc-snapshots-log-positions-and-replay.md)。源事务、连接器事件身份、删除载荷与空值 tombstone 各有协议；不能直接把捕获行当作完整业务事件或把源 LSN 当作通用 event_id。

## 五道自检与核查范围

1. `source+id`、订单 ID、事件类型、载荷版本、schema ID、Registry subject/version 和 CloudEvents specversion 分别标识什么？重发及衍生事件怎样避免混淆？
2. 在 Avro 订单矩阵中，去掉 currency 的读者默认值后哪一格失败？默认、字段缺失与显式 null 为什么不能互换？
3. memo 的三代反例为什么相邻 BACKWARD 成立，R3/W1 却失败？FULL 与 TRANSITIVE 分别扩大了哪个检查范围，又未证明什么？
4. 旧中继经 JSON 转换、读入 upcast、双发与回退分别怎样丢失字段、改写历史含义或重复动作？应保留哪些身份和版本依据？
5. 重建投影、恢复同一支付与隔离坏消息各需要什么执行和去重范围？为什么保留了历史数据与 Broker 事务仍不自动证明外部业务安全？

核查日期：2026-10-23。上述矩阵、反例、发布与回放责任为教学综合，没有运行编码器、Registry、消费者、中继、[Outbox](../../glossary/messaging.md#messaging.outbox)、upcaster、双发/回退或重建投影，没有执行数据库/支付副作用、权限集成或负载实验。

| 一手资料与范围 | 实际核查部分 |
| --- | --- |
| [CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) | 身份 source/id、specversion、type、dataschema、subject、time；不把信封规范当作业务载荷或权限协议 |
| [Apache Avro 1.12.0 Specification](https://avro.apache.org/docs/1.12.0/specification/) | Records 默认值、别名、writer/reader 解析、字段忽略与缺失、类型匹配/推广；矩阵按这些规则推导，未执行具体库 |
| [Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/) | 更新消息、字段号和二进制/JSON 范围、未知字段保留与丢失路径；2026-10-23 滚动页面，不声明所有语言库版本相同行为 |
| [Confluent Schema Evolution](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) | current 核查日快照；兼容方向、传递范围、subject 检查与升级次序，不引用默认配置代替本系统配置 |
| [Confluent SerDes 与 subject](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html) | current 核查日快照；subject/version、相同结构 ID 及历史定义获取；未假定所有客户端使用同一种线格式 |
| [Axon Event Versioning](https://docs.axoniq.io/axon-framework-reference/4.12/events/event-versioning/) | 读取日返回页的 upcasting/转换链与保留历史概念；请求路径含 4.12，但导航显示 5.4，故只作当日概念资料，不当作固定 4.12 API 或实际产品符合性证据 |
