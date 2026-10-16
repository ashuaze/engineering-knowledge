---
id: "kb-database-concurrent-inventory"
title: "库存并发：两个成功事务为何仍可能超卖"
kind: "concept"
domain: "database"
status: "evolving"
summary: "从陈旧读取和单行条件更新理解事务隔离、数据库约束与业务不变量的分工。"
created: "2026-10-16"
updated: "2026-10-16"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-api-idempotency", "kb-messaging-outbox", "kb-reliability-retry-budgets"]
tags: ["concurrency", "transactions", "constraints"]
---

# 库存并发：两个成功事务为何仍可能超卖

学习入口：库存只有一件，两次请求都检查到有货，并且都下单成功，事务为什么没有防住？前置知识：SELECT、UPDATE 与事务提交。本文按 PostgreSQL 18 的 Read Committed 机制分析；SQL 是可供本地复现的步骤，本轮未运行 PostgreSQL 实验。

## Definition：定义与问题

事务原子性保证一组写入一起提交或回滚；并发下还需选择隔离机制，并把业务不变量落到正确的数据操作上。“用了事务”不能替代对读取、判断和写入之间时序的分析。

本例初始库存为 1，出售一件应使可用库存减少 1，并产生一条数量为 1 的预订。在没有补货、取消和其他写入的前提下，不变量是：`剩余库存 ≥ 0`，且`预订数量之和 + 剩余库存 = 初始库存`。仅检查库存列非负，不能单独证明预订总量正确。

## Principles：工作机制与核心原理

在 PostgreSQL 的 Read Committed 下，普通 SELECT 按语句开始时的已提交快照读取。两个事务先后读取时，都可能看见库存为 1；这个观察不为后续下单保留库存。[官方隔离级别说明](https://www.postgresql.org/docs/18/transaction-iso.html)给出了快照与并发 UPDATE 的规则。

若应用根据旧读取计算出新值 0，再分别执行 `SET remaining = 0`，两个更新都可能成功，最终库存仍是 0，却已有两条预订。这一教学时序没有违背 `CHECK (remaining >= 0)`，暴露的是检查范围与业务不变量不一致。

把判断放入单行更新：`SET remaining = remaining - 1 WHERE remaining >= 1`。在本文固定主键、单行库存的场景中，竞争更新等待前一个事务完成后，会针对更新后的行重新判断条件；库存不足则不更新。此结论限于上述条件，不能推导任意复杂查询或跨多行约束都同样成立。

## Trade-offs：优势、限制与适用边界

| 方案 | 适合的问题 | 成本或边界 |
| --- | --- | --- |
| 条件更新并检查结果 | 单行余额、库存等局部约束 | 热点行仍会竞争；零行更新须作为业务失败处理 |
| SELECT FOR UPDATE 后检查并写入 | 需要在锁定对象上做多步判断 | 持锁期间会阻塞竞争方，须保持短事务与一致锁顺序 |
| UNIQUE、CHECK、外键等约束 | 可以直接表达的数据合法性 | 各自范围不同，不能用单行 CHECK 表达任意跨行统计规则 |
| Serializable 事务 | 需要验证更复杂的并发执行关系 | 可能中止事务，调用方需要有边界地重试整个事务 |

[PostgreSQL 约束说明](https://www.postgresql.org/docs/18/ddl-constraints.html)特别说明了 CHECK 对其他行数据的限制；[显式锁说明](https://www.postgresql.org/docs/18/explicit-locking.html)解释了行锁的阻塞与死锁风险。跨仓库、组合商品、补货和取消均需要扩展模型。

## Implementation：代码或架构实现

以下 SQL 使用 PostgreSQL 18 语法。两轮对照分别在全新的本地练习数据库内准备初始数据，避免把上一轮预订混入结论：

```sql
CREATE TABLE kb_inventory (
  sku text PRIMARY KEY,
  remaining integer NOT NULL CHECK (remaining >= 0)
);
CREATE TABLE kb_reservations (
  request_id text PRIMARY KEY,
  sku text NOT NULL REFERENCES kb_inventory(sku),
  quantity integer NOT NULL CHECK (quantity > 0)
);
INSERT INTO kb_inventory VALUES ('book', 1);
```

错误方案在 A、B 两个会话中先执行 `BEGIN ISOLATION LEVEL READ COMMITTED;`，然后都执行 `SELECT remaining FROM kb_inventory WHERE sku = 'book';`。确认两边均读到 1 后，A 先执行：

```sql
UPDATE kb_inventory SET remaining = 0 WHERE sku = 'book';
INSERT INTO kb_reservations VALUES ('request-a', 'book', 1);
COMMIT;
```

B 再执行相同更新，插入 request-b 并提交。虽然两个事务各自原子提交，预期会留下两笔预订，库存为 0。这是待复现的错误流程。

修正方案用一条语句将“成功分配到库存”与“写预订”关联，A、B 分别使用不同 request_id：

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
WITH allocated AS (
  UPDATE kb_inventory
  SET remaining = remaining - 1
  WHERE sku = 'book' AND remaining >= 1
  RETURNING sku
)
INSERT INTO kb_reservations (request_id, sku, quantity)
SELECT 'request-a', sku, 1 FROM allocated
RETURNING request_id;
COMMIT;
```

没有分配到库存时，allocated 为空，INSERT 也不产生预订。调用方必须检查返回行，不能看到 COMMIT 成功就回复“下单成功”。零行也不能证明同一业务动作此前未成功：前一次请求可能已消耗最后一件库存，重放时根本不会执行 INSERT，更不会触发 request_id 冲突。

若仍有库存，插入则可能因 request_id 冲突失败；此时当前事务须回滚。对重复或结果未知的请求，需要按稳定 request_id 查询并核对原请求参数、权限与结果。这条 SQL 只实现库存分配和预订写入的原子性，完整幂等协议另见关联文章。数据修改 CTE 的语义见 [WITH 文档](https://www.postgresql.org/docs/18/queries-with.html)。

## Failure Modes：常见错误与故障模式

- **先读后写固定值**：旧库存被重复使用；把条件与扣减放到数据库写入中。
- **忽略更新或返回行数**：库存不足仍创建订单或返回成功；把“分配到一行”作为进入后续业务的必要条件。
- **库存与预订分开提交**：一个成功、另一个失败，账目失衡；放入同一事务并测试回滚。
- **事务内等待外部服务**：长时间持锁，竞争方排队；缩短事务，把外部执行边界另行设计。
- **重试创建使用新业务标识**：数据库并发控制没有识别同一次业务意图；另行设计幂等协议。

## Practice：工程案例、测试与验证

本文已核查 PostgreSQL 18 文档，**尚未连接 PostgreSQL 执行上述 SQL**。以下是复现计划，表中数字是预期结果：

| 对照 | 操作 | 应检查的结果 |
| --- | --- | --- |
| 陈旧读取 | A、B 都先读到 1，再分别写固定值和预订 | 两笔预订、库存 0，业务总量不守恒 |
| 条件扣减 | A 成功更新后先不提交，B 发起相同分配，再提交 A | B 等待后无分配；最终一笔预订、库存 0 |
| 提交前回滚 | A 完成扣减和插入但回滚，再让 B 继续 | A 不留预订，库存可以被 B 分配 |
| 耗尽后重放 | 初始库存 1，成功预订后以同一 request_id 重放 | 返回零行；查询并核对原请求，不能据此认定原操作未成功 |
| 有库存时重复标识 | 单独以初始库存 2 建立场景，使用同一 request_id 两次提交 | 第二次插入唯一冲突，回滚后库存仍为 1；查询并核对原结果 |

保留数据库版本、会话隔离级别、语句顺序、返回行及最终两表数据。不要用现有 SQLite 幂等实验替代这里的 PostgreSQL 机制验证。

自检：如果剩余库存从未为负，但预订总量仍超出初始库存，哪条不变量没有被检查？如果扩展到多行总额度，现有单行条件更新还够吗？

## Related Concepts：关联概念

- [幂等性](../api/idempotency.md)：并发扣减与重复业务意图识别需要分别设计。
- [Transactional Outbox](../messaging/transactional-outbox.md)：预订提交后发布事件，可在同一事务内记录待发事件。
- [重试预算](../reliability/timeouts-and-retry-budgets.md)：事务冲突重试也需要次数、时间与安全性边界。

## 来源与核查

核查日期：2026-10-16；适用机制限定为 PostgreSQL 18。快照、条件重判、约束、锁和 CTE 语义依据下列官方文档；库存模型与对照步骤为本知识库的教学设计，所有 SQL 观察结果仍待实测。

- [PostgreSQL 18：Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18：Constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [PostgreSQL 18：Explicit Locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18：WITH Queries](https://www.postgresql.org/docs/18/queries-with.html)
