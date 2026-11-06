---
id: "kb-cache-write-paths"
title: "写穿与异步写回：写入成功究竟确认到了哪里"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "区分同步写穿与延后写回的确认、持久化和恢复边界，解释写入合并、版本顺序、排队容量及数据库可见性。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-cache-search-cache-aside", "kb-database-wal-recovery"]
related: ["kb-cache-load-coalescing", "kb-performance-backpressure", "kb-messaging-delivery-semantics", "kb-messaging-outbox", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-database-backups-pitr"]
tags: ["write-through", "write-behind", "durability", "ordering", "backpressure"]
---

# 写穿与异步写回：写入成功究竟确认到了哪里

学习入口：缓存中的值已经变成 v2，客户端也收到成功，为什么数据库仍是 v1，重启后 v2 甚至消失？[写穿](../../glossary/cache-search.md#cache-search.cache-write)把后端写入纳入同步调用路径；异步写回先接纳待写状态，再由后台推进后端。两者改变等待和失败位置，具体持久性仍取决于成功响应覆盖的阶段、存储配置及恢复协议。

前置：[Cache-Aside 与失效](cache-aside-and-invalidation.md)、[WAL 与崩溃恢复](../database/wal-and-crash-recovery.md)。本文固定参考 Hazelcast 5.6、Ehcache 3.11 和 PostgreSQL 18 官方文档，于 2026-10-23 核查；流程、版本和[队列](../../glossary/algorithms.md#algorithms.queues)数字为教学设计，未部署缓存、数据库或写回工作者。

## 先区分写入由谁组织

| 组织方式 | 谁协调缓存与后端 | 调用方要明确什么 |
| --- | --- | --- |
| Cache-Aside 的常见写路径 | 应用提交权威数据，再更新或失效缓存 | 两步可能部分成功，迟到读者仍可能回填旧值 |
| 应用自行双写 | 应用分别调用缓存和数据库 | 次序、失败修复和事务边界都由应用承担；[并行](../../glossary/systems.md#systems.concurrency)调用不形成共同提交 |
| Write Through，写穿 | 缓存接口调用 writer，在同步写路径更新后端 | 正常成功是否表示 writer 已完成、后端如何确认、缓存何时可见 |
| Write Behind，异步写回 | 缓存写路径接纳待写项，后台稍后调用 writer | 接纳记录放在哪里、会否丢失、后端何时可见、失败怎样继续推进 |

[Ehcache 3.11 的缓存模式说明](https://www.ehcache.org/documentation/3.11/caching-patterns.html)把读写后端的职责放入 loader/writer，并将写回解释为延后后端写入。应用像访问主存储一样使用缓存接口，不等于缓存自动获得数据库的全部事务语义；权威读取、约束及恢复依据仍需明确。

在 [Hazelcast 5.6 MapStore](https://docs.hazelcast.com/hazelcast/5.6/mapstore/working-with-external-data)中，写穿同步调用外部系统，写回则按配置延后。该版本的[配置说明](https://docs.hazelcast.com/hazelcast/5.6/mapstore/configuration-guide)用 `write-delay-seconds=0` 与大于零区分两种模式；把 MapStore 调用卸载到其他[线程](../../glossary/systems.md#systems.execution-units)，又是另一项配置。线程不阻塞分区执行器，不能单独证明业务调用已按写回模式确认。

## 把“成功”写成一条明确的确认链

下图选择一种“先取得后端确认，再发布缓存”的同步契约，用于推理，不代表所有产品的内部次序：

```text
同步教学路径：请求 → writer → 后端按约定提交 → 发布缓存结果 → 返回成功
异步教学路径：请求 → 接纳缓存状态及待写记录 → 返回已接纳
                                      ↓
                    后台 writer → 后端按约定提交 → 标记该项完成
```

异步路径还要保护“状态可见”和“待写意图已接纳”之间的关系。若缓存已显示 v2，队列却因满或异常没有接受对应记录，不能继续声称 v2 已获得完整写回保证；应按契约拒绝、撤销未接纳的发布或进入可恢复的失败状态。具体原子边界由实现提供，图中的箭头本身不构成事务。

| 成功响应覆盖到哪里 | 立即故障后仍缺少的证明 |
| --- | --- |
| 只更新进程内状态或内存队列 | 进程或整个缓存故障后，待写记录是否还存在 |
| 待写意图进入可恢复日志或复制记录 | 持久介质、确认副本、故障模型及重放顺序是否满足要求；后端此时仍可能未更新 |
| writer 返回成功 | writer 是否等到真正提交，是否吞掉错误，数据库采用什么耐久配置 |
| 后端完成其约定的耐久提交 | 其他缓存、副本、搜索投影是否已更新，外部动作是否已完成 |

不能仅因启用了缓存备份、磁盘层或持久队列，就推断所有待写项在任意故障下都能恢复；需核对它们是否覆盖同一条接纳路径及相应状态。[恢复点目标](../../glossary/reliability.md#reliability.recovery) RPO 表示允许丢失的数据范围，不能用固定写[延迟](../../glossary/performance.md#performance.latency-throughput)直接替代。

[PostgreSQL 18 异步提交说明](https://www.postgresql.org/docs/18/wal-async-commit.html)提供了另一层反例：数据库也可以在 [WAL](../../glossary/database.md#database.recovery-log) 真正刷到耐久存储前报告逻辑完成。因而“同步调用数据库”仍需核对数据库的提交与存储配置；这与缓存的异步写回是两种机制。

## 同步返回不自动形成缓存与数据库的共同事务

在前述同步教学路径中，数据库可能已提交，缓存结果发布却失败，或成功响应在返回途中丢失。调用方收到失败或超时，不能据此认定后端没有改变，更不能换一个操作身份无条件再扣一次款。writer 应有[幂等](../../glossary/api.md#api.idempotency)写入或稳定操作标识及结果核对能力，见[幂等性](../api/idempotency.md)与[确认边界](../messaging/delivery-acknowledgements-and-idempotency.md)。

反方向也要查清：产品先把新值暴露给读者、随后后端失败时，会保留、撤回还是标记该值？不能将一种库的内部顺序或异常处理推广给所有写穿实现。多个键分别调用 writer，也不会自动获得跨键原子提交。

教学反例：同一业务要求 A 账户减 10、B 账户加 10。若两个键分别成功写穿，其中一步失败，就可能只完成一半；需要在真正保护余额[不变量](../../glossary/systems.md#systems.atomicity)的权威事务中协调，而不是因为缓存 API 都返回过成功就宣布转账完整。

## 异步窗口里的读者会看到不同进度

以下假定后端初始 v1，缓存接纳 v2 后可返回给本路径读者，后端稍后才更新：

| 时间 | 教学事件 | 可见性与恢复判断 |
| --- | --- | --- |
| t0 | 写回接口接受 v2，缓存读到 v2 | 直接数据库读取仍可得到 v1；成功暂只覆盖接纳边界 |
| t1 | 后台 writer 开始写 v2 | 请求已经发出，不证明后端已提交 |
| t2 | 后端提交 v2，完成标记尚未保存 | 工作重试可能再次写入；必须处理结果未知与重复 |
| t3 | 待写项被确认完成 | 仍不能推出其他读取副本或投影都已应用 |

若在 t0 后、后端提交前整个缓存及未耐久队列丢失，从数据库重新加载可能又得到 v1。若接纳记录已经按约定持久保存，则可依据其恢复规则重放；“有日志”也必须证明已确认写入可在相应故障下从日志恢复。

[缓存淘汰](../../glossary/algorithms.md#algorithms.eviction)、过期或[读穿](../../glossary/cache-search.md#cache-search.cache-read)不能抹掉尚未完成的写入责任。例如 v2 尚未写回，条目被移除后立刻从数据库读到 v1，会让当前缓存状态倒退。实现应明确脏项、待写记录与读取之间的协调；不能假定 [TTL](../../glossary/cache-search.md#cache-search.invalidation) 到期就取消业务写入。

另一路绕过缓存直接把数据库更新成 v3，也可能被队列中的旧 v2 覆盖。需要统一写入入口，或在后端原子核对对象版本及操作身份；单靠“数据库是权威源”这句话不会阻止旧请求真正写入。旧读者回填的类似窗口见[缓存加载合并](cache-load-coalescing-and-stampedes.md)。

## 写入合并保存状态，未必保存每一次动作

批量写入把多项一起调用后端；写入合并则可能只保留同键的最后状态。两者不是同一操作。[Hazelcast 5.6 配置](https://docs.hazelcast.com/hazelcast/5.6/mapstore/configuration-guide)说明，其启用 `write-coalescing` 时在写延迟窗口只存同键最新操作；[Ehcache 3.11 writer 文档](https://www.ehcache.org/documentation/3.11/writers.html)也给出按键、按批保留最后变更的行为。

教学序列：同一个设置键依次取值 `theme=light → dark → light`。若业务只要求最终状态，合并后存最后的 light 可以符合契约；若三条记录表示三次付款、三次计量或审计动作，丢弃中间项就改变业务。不能把会合并状态的写回缓存直接当成无损事件日志，需记录每个独立业务动作的场景可参考 [Transactional Outbox](../messaging/transactional-outbox.md)。

“只保留最新”也要定义最新的依据：应用版本、缓存接纳次序还是时钟时间？一个后台进程按 FIFO 取出，不代表故障重试、多工作者和绕过写入路径仍保持同键提交顺序。应在实际接受写入的位置检查所需版本、去重和并发条件。

删除也属于写入意图。若删除 v3 已生效，迟到的 v2 不能把对象重新创建；需要能跨过重试、缓存移除和恢复的删除版本或删除标记。只在“当前记录存在”时比较版本，记录删除后往往就失去拒绝旧更新的依据。这里是应用接受协议要求，并非声称上述库默认提供完整的跨系统版本或墓碑协议。

## 后端落后时，队列必须有人负责

纸面模型：等待队列容量 10,000 项，初始 2,000 项；稳定接纳 700 项/秒，后台完成 500 项/秒。假设每项都是不同键、无合并、无重试或丢弃、成本相同，且这些速率恒定；Q 只计等待项，不含已取走的在途项。还假定在途项数量稳定，取出速率等于完成速率，均为 500 项/秒；若工作者继续增加在途项，不能直接用完成速率计算等待队列的增速。

```text
净积压 = 700 − 500 = 200 项/秒
剩余空间 = 10,000 − 2,000 = 8,000 项
达到满队列 = 8,000 ÷ 200 = 40 秒
```

模型忽略调度及批次波动，不是实测或容量建议。假设停止所有新接纳、后台持续完成 500 项/秒且无失败，仅这 10,000 个等待项就至少需要理想的 20 秒完成；这个下界尚未计入停止时已有的在途项，实际全部完成还需将它们纳入。后端持续故障时完成速率可能变成零，配置一个写延迟不会保证届时已经写完。实际还要限制字节数、单项大小、在途项、重试缓存及不同租户的占用，见[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。

队列满时，可以让生产调用等待、明确拒绝、转入另一个有容量与耐久约定的存储，或在业务允许时合并状态。已确认接纳的项不能因空间紧张被悄悄舍弃。直接降级为数据库写入时，还要协调先前[排队](../../glossary/performance.md#performance.queueing)的旧项，避免“新值直接提交、旧值随后写回”的倒序。

写回失败不等于库必然自动重试。Ehcache 3.11 的 write-behind wrapper 明确不实现失败重试，应用若需要须在自己的 writer 中处理；这与其他产品的机制不能混为一谈。暂时错误要限定[退避](../../glossary/api.md#api.retries)、次数及总预算；永久格式或权限错误应隔离、告警并有修复责任。所谓死信去向还需说明如何耐久转移、是否保留稳定操作身份，不能把失败项从活动队列移走就当作已经写入后端。

停机需要停止或约束新接纳，等待真正的后端完成，或确认未完成记录已被可靠保存并能恢复。普通关闭、强制终止、宿主机丢失和整个缓存集群丢失不是同一故障；一次正常排空成功不能证明所有崩溃情形。监控应区分已接纳、已写回、失败隔离和结果未知，并同时看最老待写年龄与后端可见进度。

## 五道自检与核查范围

1. 写穿、异步写回、应用双写和 Cache-Aside 的写路径，分别由谁协调？数据库调用返回成功后，还需核对哪些耐久与缓存可见条件？
2. 异步接口在 t0 接受 v2，而数据库仍为 v1：直接读库、缓存淘汰、整个未耐久缓存丢失各会产生什么结果？
3. 后端已提交但完成标记或客户端响应丢失时，重试如何避免重复效果？两个键分别成功为何仍不能证明一次转账共同提交？
4. 按键合并何时允许丢弃中间状态？删除、迟到重试与绕过缓存写入怎样保留拒绝旧值的依据？
5. 700/500 项每秒和 10,000 项上限的模型为何 40 秒后满，20 秒排空又依赖什么？队列满、永久失败与强制终止后，哪些已接纳责任仍必须保留？

核查日期：2026-10-23。本文实际读取以下一手资料；产品版本独立限定，未把术语或库配置推广成通用的持久性、事务、顺序或恢复承诺。接受协议、故障时间线与队列数字是来源机制基础上的教学综合。

| 一手资料与版本 | 实际核查范围 |
| --- | --- |
| [Hazelcast 5.6 MapStore 模式](https://docs.hazelcast.com/hazelcast/5.6/mapstore/working-with-external-data) | read-through、write-through、write-behind 的接口角色与后端更新时机 |
| [Hazelcast 5.6 MapStore 配置](https://docs.hazelcast.com/hazelcast/5.6/mapstore/configuration-guide) | 写延迟、offload 与写入合并的不同控制范围；未核查为全部拓扑提供耐久队列保证 |
| [Hazelcast 5.6 自定义 MapStore](https://docs.hazelcast.com/hazelcast/5.6/mapstore/implement-a-mapstore) | loader/writer、storeAll/deleteAll 批量调用和自定义实现责任；未照搬数据库示例代码 |
| [Ehcache 3.11 Cache Usage Patterns](https://www.ehcache.org/documentation/3.11/caching-patterns.html) | Cache-Aside、缓存接口代为读写后端、同步与延后写入的模式区别 |
| [Ehcache 3.11 Cache Loaders and Writers](https://www.ehcache.org/documentation/3.11/writers.html) | wrapper 不自动重试、队列背压、批次/并发与按键合并；其批写配置不适用于 clustered caches 的提示 |
| [PostgreSQL 18 Asynchronous Commit](https://www.postgresql.org/docs/18/wal-async-commit.html) | 数据库逻辑完成与 WAL 耐久之间的窗口；不等同于缓存异步写回，也未采用性能或丢失时间经验值 |

没有执行缓存/数据库部署、writer API、异步队列、版本或删除协议、重试/顺序/崩溃注入、排空恢复、负载、数据丢失或 RPO 实验。实际选型与实现仍需分别验证成功确认、故障保留范围、读写一致性和可恢复的业务结果。
