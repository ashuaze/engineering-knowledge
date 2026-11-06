---
id: "kb-database-models-access-patterns"
title: "数据模型与访问模式：先确定怎样读写，再决定怎样存"
kind: "concept"
domain: "database"
status: "evolving"
summary: "以客户与订单为例，区分模型、存储、索引和分布，说明函数依赖、约束、历史快照与复制维护，并从事务和分析访问反推设计。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-database-concurrent-inventory"]
related: ["kb-database-isolation-mvcc", "kb-database-indexes-plans", "kb-architecture-aggregates-invariants", "kb-database-schema-migrations", "kb-database-partitioning-sharding"]
tags: ["data-modeling", "access-patterns", "normalization", "constraints", "workloads"]
---

# 数据模型与访问模式：先确定怎样读写，再决定怎样存

学习入口：订单应该拆成几张表，还是放进一个文档？客户改地址后，为什么有些订单字段必须更新，有些反而不能跟着改？先确定每个字段表达哪个事实、哪些修改必须一起完成，以及调用方怎样读取，再讨论产品与存储结构。

前置：[库存并发与业务不变量](concurrent-inventory.md)。本文用一个简化客户/订单模型展开；产品规则固定参照 PostgreSQL 18、MongoDB 8.0，DynamoDB 与 DuckDB 仅用于说明访问和实现边界。表、结构与查询候选均为未执行的纸面设计，不是数据库选型基准。

## 四个设计轴不要合成一个产品标签

| 设计轴 | 要回答的问题 | 例子 |
| --- | --- | --- |
| 逻辑模型 | 有哪些事实、[实体](../../glossary/architecture.md#architecture.domain-model)、关系和标识？ | 一个订单属于哪个客户，地址是当前值还是历史值 |
| 物理存储与执行 | 如何组织数据和处理读取/更新？ | 行或列的组织、页面与压缩、批量执行 |
| 索引与访问结构 | 怎样缩小一次请求需要检查的数据？ | 按订单号定位，按客户与时间排列 |
| 分布与复制 | 数据放在哪些节点，如何切分和传播？ | 按租户[分片](../../glossary/database.md#database.partitioning)、副本读取与迁移 |

这些轴会互相影响，但不是同义词。关系模型不等于只能保存平坦标量；PostgreSQL 18 可以保存并索引 `jsonb`，见[官方 JSON 类型说明](https://www.postgresql.org/docs/18/datatype-json.html)。一个关系表也可以存在于单机或分布式系统，增加索引也不会自动把它分到更多节点。分区与跨节点的区别继续见[分区、分片与数据路由](partitioning-sharding-and-data-routing.md)。

关系模型把事实组织成关系及其约束，键值模型围绕键定位值，文档模型把相关字段和嵌套结构组织成文档；图模型侧重节点、边和遍历需求，本文不展开图查询。它们是组织和访问数据的方式，不直接给出事务范围、[延迟](../../glossary/performance.md#performance.latency-throughput)或扩展性的保证。`NoSQL` 也不是统一的数据模型或性能指标。

灵活结构同样有模式：哪些字段必须存在、值是什么类型、旧版本怎样解释，都需要契约。MongoDB 8.0 默认允许同集合文档具有不同字段和类型，但可配置 schema [validation](../../glossary/api.md#api.validation)；验证级别及失败时拒绝还是警告也要明确，见[官方模式校验说明](https://www.mongodb.com/docs/v8.0/core/schema-validation/)。把校验从数据库移到应用，不会使数据约束消失。

## 先写访问模式，而不是只写实体名

下面是教学需求，不是已采样的生产流量。每个读取都需补充选择条件、顺序、结果量、时效要求；每个写入都需说明影响哪些事实及并发边界。

| 访问模式 | 明确的需求 | 模型与访问结构的候选 |
| --- | --- | --- |
| 按订单号看详情 | 返回一笔订单及其有限数量明细、下单时地址 | 订单键定位；明细可独立表或有界嵌入 |
| 查看某客户最近 20 笔订单 | 按创建时间和唯一订单号稳定倒序 | 按客户、创建时间、订单号组织的访问结构 |
| 修改客户当前地址 | 修改当前资料，不覆盖已有订单时点事实 | 客户主记录更新；与并发修改协调 |
| 按下单日汇总一个月订单金额 | 扫描相应范围，只读需要的列；先定义状态、币种与撤销口径 | 分析扫描、预聚合或独立投影；明确数据截止时点 |

PostgreSQL 下，第二种需求可以评估 `(customer_id, created_at, order_id)` 等联合索引；它只是候选，不保证优化器选择、结果延迟或写入成本，具体见[索引与执行计划](indexes-and-query-plans.md)。新增“跨全部客户按状态查询”时，应重新评估访问结构，不能把现有索引理解成所有查询的加速器。

DynamoDB 的 `Query` 要求分区键等值，可再约束排序键；过滤表达式不等于为任意字段创建键访问路径，见[官方键条件说明](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.KeyConditionExpressions.html)。因此“按订单号查一项”和“按客户查时间范围”可能需要不同的键或索引设计；不能先随便选键，再假定任意列表查询都能同样处理。[DynamoDB 建模指南](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-modeling-nosql.html)也要求先列清访问模式。

## 用函数依赖找出“同一事实被存了几次”

假设暂时把所有内容放在一张表中，每个订单只有一行，所有示例字段均非空：

| order_id | customer_id | name_current | address_current | created_at |
| --- | --- | --- | --- | --- |
| O101 | C7 | 小林 | 杉路 5 号 | 10-01 |
| O102 | C7 | 小林 | 杉路 5 号 | 10-03 |
| O103 | C9 | 小周 | 柳路 2 号 | 10-03 |

业务约定：一个订单号只标识一笔订单；每个客户在当前状态只有一份当前姓名和当前地址。由此声明：

```text
order_id → customer_id, created_at
customer_id → name_current, address_current
```

`X → Y` 的[函数依赖](../../glossary/database.md#database.functional-dependency)意味着：在每个合法关系状态中，两行若 X 相同，Y 就必须相同。它来自业务语义约束，不是看到这三行刚好相同就发现了一条永久规律；定义见作者官方[《Database System Concepts》第 7 版，第 7 章](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)。同一个客户未来可以改地址，依赖要求的是同一合法状态中的一致性，不是地址永不变化。

这张表会把 C7 的同一份当前资料写两遍：以后再次改址时只更新 O101，会留下互相矛盾的“当前地址”；没有订单时难以单独登记客户；删掉最后一笔订单又可能丢掉客户资料。这些更新、插入、删除异常是组织方式的问题，不是换一种文件格式就会自动消失。

可以把当前事实拆成：

```text
Customers(customer_id, name_current, address_current)
Orders(order_id, customer_id, created_at)
```

让 `customer_id` 在 Customers 唯一，并让每笔订单引用存在的客户。这样修改当前地址只改一处，需要当前资料时再按客户标识连接。对每笔原订单，`customer_id` 在 Customers 中只对应一行；连接不会拼出同一客户的另一份当前资料，也不会改变订单行数。在上述依赖成立、订单客户引用有效的前提下，投影后再按 `customer_id` 连接能还原原来的订单/当前客户组合。不能随意按姓名拆分和连接，因为名字可能相同。

这体现了规范化按依赖减少冗余的作用。以 BCNF 为例，非平凡函数依赖的决定项应是超键；原表的 `customer_id` 不能确定某个 `order_id`，因而不是原表的超键。定义与无损分解要求见 [Berkeley CS186 数据库设计教材](https://cs186berkeley.net/notes/note13/#bcnf-decomposition)。本文只证明这个受限例子的分解，不声称所有拆表都保持信息、所有依赖都能分表单独检查，或[范式](../../glossary/database.md#database.normalization)越高查询就越快。

## 键和外键表达哪些约束，没表达哪些规则

候选键是能唯一确定整行、且不能再删减属性的键；一个模型可以有多个候选键，再选一个作为主要标识。这里的“不能再删减”指包含关系上的最小性，不是必须拥有所有候选键中最少的列数；候选键定义见[教材中的键与依赖](https://cs186berkeley.net/notes/note13/#fds-and-normalization)。声明了 SQL 主键，也不代表数据库替作者证明了其理论最小性。

落到 PostgreSQL 18，本例可采用 `Customers.customer_id` 和 `Orders.order_id` 的主键，以及非空 `Orders.customer_id` 对 Customers 的[外键](../../glossary/database.md#database.constraints)。主键实施唯一且非空；其他业务编号可以另设非空唯一约束。仅有 `UNIQUE` 不总等于候选键：PostgreSQL 默认允许唯一列出现多个 NULL，须明确空值语义。外键维护相应引用的存在性，不保证客户仍处于可下单状态。依据见[PostgreSQL 18 约束文档](https://www.postgresql.org/docs/18/ddl-constraints.html)。

例如“数量必须为正”可以用行内非空与检查约束表达；“支付成功的订单才发货”“某客户全部未结订单不超过授信范围”则涉及状态转换或多记录关系。PostgreSQL 的普通 `CHECK` 不能可靠表达对任意其他行的持续检查，仍要设计适当的约束、事务和并发协议。不要只在应用里先读一次再写入；具体机制见[库存并发](concurrent-inventory.md)与[事务隔离](isolation-and-mvcc.md)。

[数据库事务](../../glossary/database.md#database.isolation)可以把参与的多步写入共同提交或回滚，见 [PostgreSQL 18 事务说明](https://www.postgresql.org/docs/18/tutorial-transactions.html)；但未编码的业务规则、外部支付或邮件不因此加入这次事务。[聚合与业务不变量](../architecture/domain-models-aggregates-and-invariants.md)帮助先确定必须共同维护哪些状态，再落实具体存储边界。

## 订单时点地址与当前地址是不同事实

现在增加需求：订单 O101 必须记录下单时确认的地址。它应有明确命名，例如 `shipping_address_at_order`。假设 C7 在 10-02 把当前地址从松路 8 号改成杉路 5 号，则下面的状态完全合理：

| 位置 | 事实含义 | 值 |
| --- | --- | --- |
| Customers 中 C7 | 现在的客户地址 | 杉路 5 号 |
| O101 的地址快照 | 10-01 下单时确认的地址 | 松路 8 号 |
| O102 的地址快照 | 10-03 下单时确认的地址 | 杉路 5 号 |

这里并不存在 `customer_id → shipping_address_at_order` 这条依赖。把所有订单快照改为客户当前地址，会破坏历史事实；只在读订单时连接 Customers 当前地址，也无法还原过去。历史地址可以存成订单字段、嵌入对象或可追溯版本引用，但必须保证所引用的历史内容不会被普通当前资料更新覆盖。MongoDB 官方也以订单时点地址说明了[时间性数据与重复当前值的区别](https://www.mongodb.com/docs/v8.0/data-modeling/best-practices/#duplicate-data)。

快照在何时生成也要写清：下单页面确认、提交订单，还是仓库受理？本例选择“下单时确认”，不表示永远禁止合法更正。若业务允许改收货地址，应保留订单侧的变更规则和必要历史，而不是后台无条件同步客户资料。

相反，如果订单列表额外缓存 `customer_name_current`，并声称它始终代表客户最新姓名，这才是同一当前事实的复制。需要说明权威来源、哪些写入会触发更新、允许陈旧多久、如何检测漏更与重建。名字、时间戳和字段类型相同，都不足以决定它究竟是历史事实还是待同步副本。

## 嵌入与反规范化把什么成本移到了写入侧

若一笔订单的明细有明确规模上限、经常随订单一起读取和修改，可以评估嵌入；若把客户的全部历史订单持续追加到一个文档，则大小、独立更新、归档和并发都需要重新分析。MongoDB 8.0 的[嵌入与引用建议](https://www.mongodb.com/docs/v8.0/data-modeling/best-practices/#link-related-data)明确把访问相关性、增长和修改方式作为选择条件，不能推出“嵌入一定快”或“引用一定正确”。

引入重复当前值或预计算汇总后，至少回答以下责任。这是设计检查表，不是某个产品自动实施的协议：

| 责任 | 失败窗口 |
| --- | --- |
| 点名权威来源与副本含义 | 不同接口各改一份，无法判断谁正确 |
| 定义共同提交还是异步更新 | 主记录成功后[进程](../../glossary/systems.md#systems.execution-units)退出，投影尚未更新 |
| 规定顺序、重复处理与修复 | 较旧变更覆盖较新值，重放导致重复累计 |
| 规定删除、更正与重建方式 | 源数据已删除，复制内容仍被长期使用 |

单文档[原子性](../../glossary/systems.md#systems.atomicity)也不自动等于整个业务原子性。MongoDB 8.0 的一次单文档操作是原子的，多文档事务则适用于副本集和分片集群，使用时仍需核对读写 concern 与限制；见[事务文档](https://www.mongodb.com/docs/v8.0/core/transactions/)及[部署限制](https://www.mongodb.com/docs/v8.0/core/transactions-production-consideration/)。不能因为数据叫文档就断言没有事务，也不能因为有事务就忽略模型和访问成本。

DynamoDB 也有多项事务 API，但本篇核查的 `TransactWriteItems` 范围是同一账号、同一 Region 中符合限制的项目；事务写入向 GSI 和 stream 的传播不是同步的原子快照。见[官方事务范围说明](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html)。GSI 读取仅提供[最终一致性](../../glossary/distributed.md#distributed.consistency)，不能沿用基础表可选强一致读取的保证，见[读取一致性文档](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)。这说明应该核对具体 API 和读取路径，而非从键值或文档标签推导全部能力。

## OLTP 与 OLAP 描述工作，不是把产品分成两盒

订单创建、状态更新和按标识查询，常属于 [OLTP](../../glossary/database.md#database.workloads) 型负载：操作较短、单次影响数据较少、并发修改与事务边界重要。跨较大范围做筛选、连接和汇总，常属于 OLAP 型负载：需要关心扫描列数、处理行数、批量导入、聚合状态和内存成本。OLAP 也可能更新或追加大量数据，并非只读的同义词。

以 DuckDB 官方定位为例，它是关系型分析数据库，采用列式向量化执行来支持分析负载；见[官方设计说明](https://duckdb.org/why_duckdb#fast)。其 2.0 调优文档也明确主要目标是较大、较少次的查询，而非高并发小查询，见[工作负载边界](https://duckdb.org/docs/2.0/guides/performance/how_to_tune_workloads#prepared-statements)。这说明“支持 SQL”与“针对哪种负载优化”是不同问题，不构成本文对具体产品速度的实测结论。

同一业务完全可能同时需要订单事务与月度分析。若复制到分析投影，要定义处理到哪个源端时点、落后能否接受、退款或更正如何重算；若在同一系统运行，则要核对扫描与更新的资源争用、快照语义及两类负载之间的隔离机制。所谓 HTAP 的混合能力仍需由实际存储、执行和一致性机制实现，名称本身不保证分析实时、事务不受影响或任意混合负载都适合。

## 自检、演进与证据范围

- 当前资料、历史快照和可重建投影分别有哪些字段，谁有权修改？
- 表中目前没有重复值，为什么还不能证明某字段是候选键或永久决定另一个字段？
- 外键、唯一约束和一次事务分别阻止哪些错误，哪些业务转换仍需另行编码？
- 把引用改成嵌入后，读取、更新、增长和失败恢复的责任分别怎样改变？
- 同一批订单用于详情、最近列表和月度汇总时，为什么不能只凭 SQL/[NoSQL](../../glossary/database.md#database.db-models) 或读写比例决定模型？

结构选择改变后，[兼容迁移](schema-migrations-and-compatibility.md)还要覆盖新旧读写、回填与切换；[分区与分片](partitioning-sharding-and-data-routing.md)另行处理数据放置、跨片操作与路由。逻辑模型合理不表示索引已经合适，也不表示分布后能保持原来的约束范围。

2026-10-22 实际联网核查作者官方《Database System Concepts》第 7 版讲义、Berkeley CS186 教材、PostgreSQL 18、MongoDB 8.0、DynamoDB 官方文档及 DuckDB 设计/2.0 工作负载说明。核查覆盖函数依赖与候选键、受限规范化、产品约束/事务/读取范围、嵌入引用及负载定位；状态为 `source-checked`。客户、订单、日期与金额需求均为教学假设，未建表、执行查询、连接数据库、部署或运行性能实验。未覆盖完整范式推导、图模型算法、各产品全部限制、HTAP 实现、分布式约束证明或生产模型迁移验收；文中没有产品性能排名。
