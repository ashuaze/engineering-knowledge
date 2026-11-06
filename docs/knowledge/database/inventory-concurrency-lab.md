---
id: "kb-database-inventory-lab"
title: "实验：验证库存并发、回滚与锁失败"
kind: "lab"
domain: "database"
status: "evolving"
summary: "用两个真实 PostgreSQL 会话与观察会话，执行七类库存、死锁和锁超时场景各三次。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-database-concurrent-inventory"]
related: ["kb-systems-races-atomicity", "kb-systems-synchronization", "kb-systems-deadlocks-recovery", "kb-database-isolation-mvcc", "kb-api-idempotency", "kb-reliability-retry-budgets"]
tags: ["postgresql", "concurrency", "testing"]
---

# 实验：验证库存并发、回滚与锁失败

## 目标与实际边界

本实验完成[库存并发概念](concurrent-inventory.md)中的五类复现，再加入[死锁](../../glossary/systems.md#systems.race-deadlock)与锁等待[超时](../../glossary/api.md#api.retries)对照。两个真实数据库会话分别推进 A、B 的业务，第三个会话查询锁等待与最终状态。目标是验证受控交错中的[不变量](../../glossary/systems.md#systems.atomicity)与错误分支，不测[并发](../../glossary/systems.md#systems.concurrency)吞吐，也不实现完整订单 HTTP 服务。

2026-10-19 在 PostgreSQL **18.0**、Python **3.13.13**、Windows x64 上实际执行七类场景，每类三次，共 **21 组**。111 项场景检查与 3 项汇总检查全部通过。失败方案的“通过”表示成功复现预期错误，不表示该方案满足[业务不变量](../../glossary/architecture.md#architecture.domain-model)。

## 依赖、运行与清理

仅使用 Python 标准库和 PostgreSQL 18 的 psql、initdb、pg_ctl、createdb；无需额外 Python 数据库驱动。准备工具后，在仓库根目录运行，将路径换成自己的 PostgreSQL 工具目录：

```bash
python examples/inventory_concurrency/lab.py --pg-bin /path/to/pgsql/bin --runs 3
# 也可使用 npm run lab:inventory -- --pg-bin /path/to/pgsql/bin
```

本次使用上一轮[查询计划](../../glossary/database.md#database.plans)实验已准备的 PostgreSQL 18.0 Windows 分发工具；没有改动已保存的查询计划记录。运行器见[完整实现](../../../examples/inventory_concurrency/lab.py)，源码及证据摘要见[清单](../../../examples/inventory_concurrency/results/manifest.json)。

运行器只会创建自己的集群，在仓库 `.cache` 内保存数据目录，监听 `127.0.0.1` 临时端口，使用专用 `kb_inventory_lab` 数据库；没有连接已有实例的模式。实验表是可供三个会话共同访问的普通表，整个集群在结束时停止并移除。初始化采用仅适合本机实验的 trust [认证](../../glossary/security.md#security.identity)，Unix 环境应由可运行 PostgreSQL 的普通用户执行。

默认把记录留在 `.cache/inventory-concurrency/`，`--output` 可以指定结果 JSON 路径，三个会话的 psql 输出保存在同一目录。若不能确认集群已停止，运行器保留目录并报错，避免删除仍在使用的数据。

## 状态模型与协调方式

模型只有库存表和预订表：库存以 sku 为主键，remaining 有非负 CHECK；预订以 request_id 为主键，sku 有[外键](../../glossary/database.md#database.constraints)，quantity 必须为正。没有补货和取消时，应满足“剩余库存 + 预订数量 = 初始库存”。两张表的定义及每条执行 SQL 都保留在实现和结果 trace 中。

A、B 每个业务事务显式使用 Read Committed。运行器给每条命令附完成标记并捕获 SQLSTATE；SQL 失败不会被下一条成功命令掩盖。在条件扣减、回滚及死锁场景的第一段等待中，观察会话实际查询 `pg_blocking_pids(B)`，确认[阻塞](../../glossary/systems.md#systems.blocking)者包含 A 且 wait_event_type 为 Lock，再释放 A 或继续构造反向等待。短间隔轮询只用于寻找状态，不以“睡够多久”作为发生锁等待的证据。锁超时场景没有采集阻塞快照，而是保持 A 持锁，以 B 的 55P03 和明确的 lock timeout 错误文本核对结果。

相关函数口径见 [PostgreSQL 系统信息函数](https://www.postgresql.org/docs/18/functions-info.html)。轮询与命令标记用于复现实验，不是生产高频监控方案。结果 trace 的 sequence 按命令完成时追加，包含 SQL、输出和 SQLSTATE；存在异步提交的命令时，它不能当成全局提交请求的精确时间线。

各会话 statement_timeout 为 15 秒、lock_timeout 为 10 秒、deadlock_timeout 为 100 ms；锁超时场景另外对 B 的当前事务设 lock_timeout 为 100 ms。这些是实验保护与加速检测参数，不能据此推荐生产值。

## 七类场景与三次实际结果

下表每行在三个重复中得到同样业务状态。完整结果见[原始 JSON](../../../examples/inventory_concurrency/results/results.json)；表中 remaining、reserved 为各表汇总。

| 场景 | 受控交错 | 实际状态与错误 | 不变量 |
| --- | --- | --- | --- |
| 旧读取后写固定值 | A、B 都读到 1，再各写库存 0 并提交一笔预订 | remaining=0，reserved=2，两笔不同 request_id | 非负成立，总量不守恒；复现超卖 |
| 条件扣减 | A 扣减并插入后持锁；确认 B 等待，再提交 A | B 返回零行；remaining=0，reserved=1，仅 request-a | 守恒 |
| 提交前回滚 | 与上项相同，但 A 回滚 | B 随后成功；remaining=0，reserved=1，仅 request-b | 守恒，A 的修改消失 |
| 库存耗尽后重放 | A 成功后，B 以同一 request_id 再执行分配 | B 返回零行，无唯一冲突；查询仍找到原 request-a | 守恒；零行不表示原请求失败 |
| 还有库存时重复标识 | 初始库存 2，A 成功；B 用相同 request_id | B 得到 23505，再回滚；remaining=1，reserved=1 | 守恒，失败尝试未多扣库存 |
| 反向获取两行锁 | A 持 book，B 持 pen；B 等 book，A 再要 pen | 一方 40P01，另一方语句成功；随后两边均回滚 | book=1、pen=1，无预订 |
| 锁等待超时 | A 持 book，B 等同一行，B 本事务限时 100 ms | B 得到 55P03 后回滚；A 可以提交 | remaining=1，无预订 |

条件分配使用数据修改 CTE，将 `UPDATE ... WHERE remaining >= 1 RETURNING sku` 的结果作为 INSERT 输入；没有扣减到行，就不会新增预订。它只保护这个固定主键、单行模型，不能据此证明跨仓库或跨行额度规则。相关语义见 [Read Committed](https://www.postgresql.org/docs/18/transaction-iso.html) 与 [WITH 查询](https://www.postgresql.org/docs/18/queries-with.html)。

本次条件扣减与回滚对照均观察到 B 等待 A，wait_event 为 transactionid。不要只因出现事务 id 锁就认定没有行级竞争，等待实现需要结合正在执行的语句解释。

## 死锁与超时的原始证据

三次死锁对照均由 B 收到 40P01，A 的第二条 UPDATE 随后成功；检查只要求“恰有一个死锁错误、另一个成功”，不把 B 必然失败写成通用保证。错误 DETAIL 记录两边等待对方事务的关系；本次将幸存事务也回滚，因此没有测量自动重试或恢复后再次提交。

三次锁超时均为 55P03，并明确报告 lock timeout；该场景只有 B 等待 A，没有构造反向依赖。它与数据库报告死锁是不同分支。原始输出分别见 [A 会话](../../../examples/inventory_concurrency/results/a.psql.txt)、[B 会话](../../../examples/inventory_concurrency/results/b.psql.txt)和[观察会话](../../../examples/inventory_concurrency/results/observer.psql.txt)。标记与错误输出保留，预期错误不当作脚本整体失败。

错误码与参数含义分别依据[官方错误码](https://www.postgresql.org/docs/18/errcodes-appendix.html)、[超时参数](https://www.postgresql.org/docs/18/runtime-config-client.html)及[锁与死锁](https://www.postgresql.org/docs/18/explicit-locking.html)说明。

## 检查怎样解释

各场景校验最终库存、预订、业务标识及预期守恒状态；有些还校验两个旧读取、B 的返回值或死锁结果组合。重复标识与锁超时在执行对应命令时严格核对 SQLSTATE，非预期错误会中止运行。汇总检查核对 PostgreSQL 18、场景数量及所有场景检查结果。

结果中的 `actual.conserves_stock=false` 与 `checks.conserves_stock=true` 可以同时出现：前者记录旧读取方案真的不守恒，后者表示它与“应复现不守恒”的预期一致。应把实际业务状态与测试断言是否满足分开阅读。

三次重复增加可复现证据，但不是对所有交错的穷举。脚本没有随机[压力测试](../../glossary/performance.md#performance.load-tests)，没有覆盖 Serializable [写偏斜](../../glossary/database.md#database.write-skew)、[进程](../../glossary/systems.md#systems.execution-units)强杀、断电、网络丢失提交响应、备库、[连接池](../../glossary/api.md#api.pool)或外部支付。耗尽后重放只核对本模型的 request_id、sku、quantity；认证、权限、完整请求指纹和保留期仍属于真实[幂等](../../glossary/api.md#api.idempotency)协议的工作。

## 自检与关联

库存没有负数，却存在两笔预订，为什么仍应判错？零行返回可能表示库存不足还是之前同一请求已成功，调用方怎样区分？记录到 55P03 后，为什么不能直接写“发现死锁”？

来源核查与执行日期：2026-10-19。

- [竞态与原子性](../systems/races-and-atomicity.md)：从允许的交错和业务不变量解释错误。
- [锁与同步原语](../systems/locks-and-synchronization.md)：区分锁对象、参与者和状态范围。
- [死锁与失败恢复](../systems/deadlocks-and-recovery.md)：等待环、错误分类与重试边界。
- [幂等性](../api/idempotency.md)：扣减正确与业务动作去重需要组合设计。
