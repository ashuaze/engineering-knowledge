---
id: "kb-ai-memory-versioning"
title: "记忆版本、冲突与失效：旧事实怎样被新事实替换"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "用版本条件、来源修订与读取时有效性检查约束旧写入、派生索引、缓存和过期内容。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-ai-memory-provenance"]
related: ["kb-ai-memory-access-deletion", "kb-ai-memory-lab", "kb-cache-search-cache-aside", "kb-systems-races-atomicity", "kb-ai-rag"]
tags: ["memory", "versioning", "conflict", "expiry"]
---

# 记忆版本、冲突与失效：旧事实怎样被新事实替换

学习入口：用户已把偏好改成英文，为什么一个晚完成的摘要任务又写回中文？前置：记忆来源、共享状态与派生缓存。完成时间不等于事实的新鲜度；需要把来源版本、记忆版本和当前可使用条件分开。

## 几种“新”不能混为一谈

| 维度 | 说明什么 | 不能替代什么 |
| --- | --- | --- |
| 来源修订 | 原始材料更新到哪一版 | 本地记忆已经使用了这一版 |
| 记忆版本 | 这条权威记录经历了几次受控修改 | 最新写入一定最真实 |
| 索引或缓存版本 | 派生副本来自哪个记录版本 | 当前仍可[授权](../../glossary/security.md#security.identity)、未过期或未删除 |
| 观察、生效与写入时间 | 事实发生、适用与存储的时刻 | 一个统一的“最后更新时间” |

来源可能迟到，两个陈述也可能各有适用范围。若依据冲突，先保留来源与未决状态，再决定询问、重新查询或按业务规则选择；不能用“最后写入胜出”自动解决真假问题。

## 版本条件可以防止旧写入覆盖新值

教学时序：A、B 都读取记忆 v1，A 根据新来源提交 v2，B 随后尝试基于 v1 更新。无条件写入可能覆盖 A；条件更新则把“我仍在修改读过的版本”作为提交条件：

```sql
UPDATE memories
SET value = :value, version = version + 1
WHERE id = :id AND version = :expected_version AND status = 'active';
```

这是省略了主体、来源与其他字段的机制示意，不能直接充当完整写入接口。[SQLite UPDATE 文档](https://www.sqlite.org/lang_update.html)说明只更新满足 WHERE 的记录，零行匹配也不是 SQL 错误；应用必须检查是否真正修改一行，将旧版本返回为冲突。

冲突后应重新读取，再判断能否合并或重新提议。不能仅把 expected_version 改成最新值就无条件[重试](../../glossary/api.md#api.retries)，否则等于绕过保护。版本条件防止的是特定旧状态覆盖，不证明自然语言内容正确，也不解决跨多条记录的[不变量](../../glossary/systems.md#systems.atomicity)。

## 索引和缓存更新有自己的进度

权威记录已到 v2，向量、关键词索引或结果缓存可能仍为 v1。教学读取策略可以先用索引找候选 ID，再检查当前权威记录的版本、来源、权限和有效期，最后从权威记录组织返回内容。旧候选不合格时，可以暂时漏召回或等待重建，不能默默把旧值当作当前事实。

后台发布也要核对候选的预期版本。捕获 v1 → 保存 v2 → 旧任务发布 v1，是需要明确测试的时序。删除、撤销来源和过期也可能使原先合法的发布失效。

[Redis 客户端缓存文档](https://redis.io/docs/latest/develop/reference/client-side-caching/)展示了变更通知与客户端移除缓存的配合。通知机制能帮助更新，但应用仍需明确断连、遗漏通知和回填竞争时的行为。本文本地实验没有运行 Redis，也不把某个产品的通知协议视作所有记忆存储的保证。

## 过期决策与后台清理是两件事

expires_at 表达记录在某种用途下允许使用到何时；后台清理决定什么时候回收存储。过期记录即使尚未清理，也不应继续进入要求新鲜数据的上下文。TTL 不证明事实仍真，更不能替代权限撤销或删除请求。

[Redis EXPIRE](https://redis.io/docs/latest/commands/expire/)同时使用访问时和后台的过期处理，说明“访问判定”与“清理进度”需要区分。这里只借其机制说明问题，具体存储如何处理持久化、时钟与更新应分别核对。

教学规则规定 `now < expires_at` 才有效，恰好等于期限时排除。真正跨[进程](../../glossary/systems.md#systems.execution-units)系统还需约定时间来源、偏差、更新是否续期，以及任务开始后超过期限怎么办。不能拿单机单调时钟数值直接当作跨服务时间戳。

## 来源修订也可能让记忆失效

记忆 v3 可能仍引用来源 revision=1；来源被更正或撤回时，仅增加记忆的更新时间并不能修复关联。需要重新核对来源版本、当前类型与确认状态，以及支持关系，并追踪受影响的摘要和索引。来源撤回也不表示所有派生内容会立即自行消失。

值未变而权限已变、内容未变而来源撤回，都说明只比较内容哈希不够。应同时检查身份、范围、版本和状态，并为不可用情况设明确的停止或重新核实分支。

## 实验与未覆盖范围

[记忆治理实验](memory-governance-lab.md)用两条实际 SQLite 连接先读同一版本，再按控制顺序提交，观察旧写入冲突；另验证旧缓存、旧索引和迟到发布被排除、来源修订重新关联，以及[逻辑时钟](../../glossary/distributed.md#distributed.clocks)下的期限边界。[SQLite 隔离说明](https://www.sqlite.org/isolation.html)限定了实际数据库行为，不能由这次两连接交错推出所有数据库的[并发](../../glossary/systems.md#systems.concurrency)性质。

实验没有同时运行线程、分布式索引或真实向量更新；发布与读取检查之间仍可能有未测试的并发窗口。生产上的强一致需求，需要把相应检查、快照或写入条件放到权威边界，不能只照搬一段版本判断。

自检：B 收到版本冲突后直接改用 v2 重试，会失去什么保护？记忆未过期但来源被撤回时，为什么仍应排除？旧索引候选被丢弃，会对[可用性](../../glossary/reliability.md#reliability.availability)和召回造成什么代价？

核查日期：2026-10-20。条件更新与隔离依据 SQLite 文档，缓存与过期例子依据 Redis 文档；版本清单、时序和读取策略为教学设计，本地证据限于独立实验页。
