---
id: "kb-cache-redis-data-types"
title: "Redis 数据结构：怎样按操作、容量与原子边界选型"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "从字段更新、去重、排序和消费位置选择 Redis 类型，区分命令原子性、事务错误、过期、集群槽位与恢复责任。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-algorithms-complexity", "kb-cache-search-cache-aside"]
related: ["kb-algorithms-hash-tables", "kb-algorithms-linear-structures", "kb-cache-search-eviction", "kb-cache-write-paths", "kb-messaging-delivery-semantics", "kb-database-partitioning-sharding", "kb-api-idempotency", "kb-performance-backpressure"]
tags: ["redis", "data-types", "atomicity", "expiration", "capacity"]
---

# Redis 数据结构：怎样按操作、容量与原子边界选型

学习入口：同一份用户资料，用一个 JSON 字符串、一个 Hash，或拆成多个键，为什么并发更新、过期和容量问题会不同？Redis 类型定义服务器能直接执行哪些操作；选型还要一起确定键的范围、一次操作修改什么，以及失败后谁负责恢复。

前置：[复杂度与结构选择](../algorithms/complexity-and-data-structures.md)、[Cache-Aside](cache-aside-and-invalidation.md)。本文依据 2026-10-23 实际读取的 Redis 官方 `latest` 文档，只讨论下列常见类型与命令，不把滚动页面当作全部部署版本的能力清单。命令片段和数字为纸面推演，未安装 Redis、执行命令或运行性能、持久化和故障实验。

## 先写操作契约，再选保存形式

键是服务器定位一个值的名称，值具有类型；Hash 的字段、Set 的成员和 Stream 的记录又是值内部不同的定位方式。键名含 `user:` 不会自动建立表、索引或租户权限。编码方式与内部布局也不是同一件事：逻辑类型相同，不保证不同版本、基数和字段长度采用相同内存表示。

| 逻辑类型 | 直接表达的操作需求 | 容易误判的边界 |
| --- | --- | --- |
| String | 一段字节、[序列化](../../glossary/runtime.md#runtime.serialization)结果，或符合命令格式的计数值 | 名字叫字符串不代表只能放文本；整体替换 JSON 不会自动合并字段 |
| Hash | 一个对象的字段到值映射，局部读写字段 | 不是关系表，没有自动二级索引、跨对象约束或任意嵌套查询 |
| List | 按插入顺序组织值，操作两端 | 弹出后[进程](../../glossary/systems.md#systems.execution-units)崩溃不自动恢复任务，[队列](../../glossary/algorithms.md#algorithms.queues)协议仍需设计 |
| Set | 唯一成员与集合运算 | 去重范围只覆盖该键的当前成员；删除或淘汰后不再保留证据 |
| Sorted Set | 唯一成员加分数，按分数或排名读取 | 分数不是业务因果；同分次序也未必是业务想要的顺序 |
| Stream | 带记录 ID 的追加记录、按位置读取及消费组机制 | 消费确认不等于外部业务提交，保留/裁剪与未完成项要协调 |

这些是[官方数据类型概览](https://redis.io/docs/latest/develop/data-types/)中的常见类型；不是所有 Redis 能力的穷举。选择时先问“是否只取整份值”“是否按成员查找”“是否需要排名”“是否需要保留每个动作”，再核对命令、部署版本与数据寿命。[近似成员判断](../../glossary/algorithms.md#algorithms.probabilistic)另见[Bloom Filter](bloom-filters-membership-and-synchronization.md)，不能把它的可能[误报](../../glossary/algorithms.md#algorithms.bloom)等同 Set 的精确成员语义。

## 一个排行榜同时需要顺序、身份和读成本

教学设定：同一租户、同一赛季，成员是稳定用户编号，分数为已定义的积分；只用普通排名查询，不使用 BYSCORE、BYLEX 或 LIMIT。假定已具备支持 REV 的 Redis 版本，纸面命令如下，未执行：

```text
ZADD rank:{T1:S1} 100 u01 100 u02 90 u03
ZRANGE rank:{T1:S1} 0 1 REV WITHSCORES
```

按文档规则，降序时 u02、u01 同为 100，反向字节字典序使 u02 排在 u01 前；范围端点包含在内，因此 0 到 1 返回两个成员。若产品要求“先达到该分数者优先”，不能拿这个同分次序代替时间规则；需要另定可验证的排序表示和更新协议。再次给 u01 设置分数是在更新该成员，不能据此记录两次独立得分事实。

[ZRANGE 文档](https://redis.io/docs/latest/commands/zrange/)列出的排名范围读取复杂度为 `O(log N + M)`，N 是成员数，M 是返回数。读取 100 万成员中的前 10 个，M 为 10；读取全体时 M 成为 100 万。两者不能只因都带“有序集合”就按同一成本估算。文档标明 REV 从 6.2.0 提供，老版本客户端/服务端组合需核对，不照抄选项。

同样，[HGETALL](https://redis.io/docs/latest/commands/hgetall/)随字段数 N 增长，且还要传输全部字段和值。“一个键”不等于“小响应”或“常数成本”。复杂度未包含每个值的字节数、网络、[排队](../../glossary/performance.md#performance.queueing)和客户端解码；不能由大 O 推出[延迟](../../glossary/performance.md#performance.latency-throughput)承诺。应限制成员数、单项大小、返回窗口与任务并发，见[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。

## 单命令原子，不会让整条读改写自动原子

教学设定：计数键初值 10，两个客户端各想加一。

| 时刻 | A | B | 当前值 |
| --- | --- | --- | --- |
| t0 | GET 得到 10 | GET 得到 10 | 10 |
| t1 | 本地算出 11，SET 11 | 尚未写 | 11 |
| t2 | 返回 | 按旧读取 SET 11 | 11，丢掉一次增加 |

改用服务器的 INCR 可以把一次加一放在同一命令内；但若响应丢失后客户端重复 INCR，同一业务动作仍可能加两次。[原子性](../../glossary/systems.md#systems.atomicity)与[业务幂等](../api/idempotency.md)是不同要求；“最后值正确”也不能反向证明每个付款动作都记录过。

把多个命令打包传输的 pipeline 主要减少往返，不构成条件判断或事务。`MULTI/EXEC` 让排队命令在执行阶段不被其他客户端命令插入，但要区分入队错误、执行时错误和乐观冲突。在本文核查的行为中，参数个数等入队错误会使 EXEC 拒绝执行整个队列；这与执行阶段某一命令报错不同。比如一个命令在执行时因类型不符报错，其他已成功命令不会自动回滚。[事务文档](https://redis.io/docs/latest/develop/using-commands/transactions/)明确其错误行为和 WATCH 检查：监视键被改动时，EXEC 可放弃整个待执行队列，应用仍要处理冲突、重试上限和连接状态。

服务器脚本可以把读取、判断和更新组合在一个不被其他命令穿插的执行过程；[Lua 说明](https://redis.io/docs/latest/develop/programmability/eval-intro/)同时指出执行期间会阻塞其他服务器活动。逻辑应有界，先检查输入、类型和业务前提，再修改状态；不能把脚本执行的隔离性解释成业务错误时自动撤销全部已写内容，更不能把外部数据库或支付动作并入这段边界。

## 键、字段与成员的寿命需要分别定义

假设用户资料整体缓存 60 秒，Hash 中保存姓名与展示设置。对键设置 EXPIRE，是限定整个键的寿命，不是自动给每个字段建立独立 60 秒计时器。Hash 字段过期有单独机制：[HEXPIRE](https://redis.io/docs/latest/commands/hexpire/)标明从 7.4.0 提供，不能据此宣称所有旧版 Hash 都支持字段 [TTL](../../glossary/cache-search.md#cache-search.invalidation)，也不能推出 List/Set 的每个元素都有相同接口。

[EXPIRE 说明](https://redis.io/docs/latest/commands/expire/)区分覆盖键与原地修改：普通 SET 覆盖值会清除原有过期，特定保留/设置选项需另行指定；INCR、LPUSH、HSET 等原地修改通常保留键的期限。更新了字段不代表自动续期，覆盖了整值也不代表旧期限自动保留。

教学反例：先 INCR 统计键，再 EXPIRE 60；若进程在两步之间退出，可能留下没有期限的键。把它们放进适当的原子执行范围可以保护这个局部窗口，仍要设计“首次创建才设期限”还是“每次更新续期”。首次创建时起算的固定寿命与每次更新续期的滑动寿命不同；前者也不自动对齐墙上时钟的整分钟[限流](../../glossary/api.md#api.limits)桶，不能只写“缓存一分钟”。删除、过期、[容量淘汰](../../glossary/algorithms.md#algorithms.eviction)与业务失效也不同，见[LRU/LFU 与淘汰](lru-lfu-and-capacity-eviction.md)。

## 槽位、容量与持久化是另外三项条件

Redis Cluster 将键映射到 hash slot；需要共同执行的多键操作要满足其同槽约束，实际命令支持及迁移状态也须核对。`profile:{T1:42}` 与 `quota:{T1:42}` 使用相同 hash tag，可落在同槽；不同 tag 不保证同槽。依据见[Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)。把所有租户强放进一个 tag，又可能把负载集中到一个槽；同槽不保证均衡或跨[数据库事务](../../glossary/database.md#database.isolation)。

一个超大 Hash/Set/List 仍由一个键及所属槽承载；集群不能因值内有许多成员就自动把它均分。拆键可以改变[热点](../../glossary/performance.md#performance.contention)、过期粒度和恢复范围，也增加联合读取、版本协调与跨槽操作的成本，取舍见[分区与数据路由](../database/partitioning-sharding-and-data-routing.md)。

全量遍历也有契约：[SCAN](https://redis.io/docs/latest/commands/scan/)是游标迭代，COUNT 是工作量提示，不保证每次恰好返回该数量；可能返回重复项，中途变化的元素不构成快照。空结果且游标非零仍不能结束。用它做清理或迁移，要允许安全重复并保留进度，不能将一轮扫描当成某个时刻的完整一致导出。

String、Hash 或 Stream 只定义数据和操作，不定义崩溃后必然剩下什么。[持久化文档](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)分别说明 RDB 快照与 AOF 写日志及刷盘策略；Cluster 的异步复制也存在已确认写丢失窗口。恢复目标还需核对配置、存储、故障范围与备份，不能从“用了 Stream”或“单命令完成”推出零丢失。缓存协调后的后端耐久另见[写穿与异步写回](write-through-write-behind-and-durability.md)。

## Stream 的位置和确认仍不能替代业务结果

在消费组中，记录被交给消费者后，可以进入待确认列表 PEL。普通 [XACK](https://redis.io/docs/latest/commands/xack/)移除相应组的待确认记录；它不是执行付款、删除 Stream 原记录或让所有组一起完成的命令。消费者在付款成功后、XACK 前退出，接管或重试可能再次遇到同一业务动作；先 ACK 再执行业务，又可能留下未执行结果。

因此仍需稳定业务身份、外部动作去重或结果核对，见[消息确认与消费幂等](../messaging/delivery-acknowledgements-and-idempotency.md)。记录 ID、PEL、正文保留、裁剪和重建范围分别管理，不能因有消费组就忽略尚未完成的记录。本文不将 Redis Stream 的具体确认方式等同其他 [Broker](../../glossary/messaging.md#messaging.roles) 的偏移提交规则。

## 五道自检与核查范围

1. 整份 JSON、Hash 字段、Set 成员、Sorted Set 分数和 Stream 记录各适合什么操作？何时“最终状态”不能代替“每个动作”？
2. 排行榜示例为什么先返回 u02，为什么只有两名？`O(log N + M)` 的 M、单项字节数和客户端成本分别影响什么？
3. GET/本地加一/SET 为什么得到 11 而不是 12？INCR、pipeline、MULTI/EXEC、WATCH 和脚本分别保护什么，又未保证什么？
4. EXPIRE、SET、HSET 与 7.4.0 起的 HEXPIRE 怎样改变不同层次的寿命？INCR 后再设期限存在什么故障窗口？
5. 同槽、多成员单键、SCAN、RDB/AOF 和 Stream XACK 各不能证明哪种均衡、快照、持久性或业务完成？

核查日期：2026-10-23。实际读取下列官方页面的相关部分，均为 `latest` 核查日快照；只在命令文档明确处引用版本起点，不声明某个客户端或全部部署已支持它。

| 一手资料 | 实际核查部分 |
| --- | --- |
| [Data types](https://redis.io/docs/latest/develop/data-types/) | 常见逻辑类型与字节/字段/顺序/集合需求，不穷举扩展类型或内部编码 |
| [ZRANGE](https://redis.io/docs/latest/commands/zrange/)、[HGETALL](https://redis.io/docs/latest/commands/hgetall/) | 范围、同分与 REV、版本起点、N/M 复杂度及全量返回 |
| [Transactions](https://redis.io/docs/latest/develop/using-commands/transactions/)、[Lua](https://redis.io/docs/latest/develop/programmability/eval-intro/) | 隔离执行、入队/运行错误、无自动回滚、WATCH 及脚本占用执行时间 |
| [EXPIRE](https://redis.io/docs/latest/commands/expire/)、[HEXPIRE](https://redis.io/docs/latest/commands/hexpire/) | 键级期限、原地更新/覆盖差异与字段 TTL 的 7.4.0 起点 |
| [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/) | hash slot/tag、多键与迁移限制、异步复制写丢失窗口 |
| [SCAN](https://redis.io/docs/latest/commands/scan/)、[Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) | 游标/重复/变更/COUNT 提示，RDB 与 AOF 策略的不同责任 |
| [XACK](https://redis.io/docs/latest/commands/xack/) | 消费组 PEL 的确认及返回范围，不把 ACK 当外部副作用提交 |

排行榜、并发计数、键名与过期窗口为教学设计。未执行 Redis 命令、脚本/事务、集群迁移、扫描、内存/时延测量、RDB/AOF 恢复或消费接管；实例配置、错误回滚行为、过期/淘汰和消息保留需结合实际版本另行验证。
