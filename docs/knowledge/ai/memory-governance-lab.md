---
id: "kb-ai-memory-lab"
title: "记忆治理实验：版本、过期、撤权与删除后的检索"
kind: "lab"
domain: "ai"
status: "evolving"
summary: "用权威记录、派生索引与缓存的独立 SQLite 文件，验证来源准入、版本冲突、过期、撤权和删除边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "tested"
prerequisites: ["kb-ai-memory-provenance", "kb-ai-memory-versioning", "kb-ai-memory-access-deletion"]
related: ["kb-ai-context", "kb-ai-rag", "kb-ai-tools-lab", "kb-cache-search-cache-aside", "kb-database-backups-pitr"]
tags: ["memory", "provenance", "versioning", "deletion", "lab"]
---

# 记忆治理实验：版本、过期、撤权与删除后的检索

问题：[长期记忆](../../glossary/ai.md#ai.memory)更新或删除后，怎样阻止旧缓存、旧索引和迟到任务继续返回旧内容？本实验于 2026-10-20 在 Python 3.13.13 / SQLite 3.50.4 / Windows 11 x64 执行，使用固定的合成内容和可信身份夹具，没有运行模型、向量引擎、Redis 或外部业务服务。

## 装置与可信边界

每类场景建立两份独立 SQLite 文件：authority 保存成员、来源、记忆版本及对象[授权](../../glossary/security.md#security.identity)，derived 保存检索索引与查询缓存。索引按字符串包含关系匹配 language，不是向量或语义检索。发布时清空所有查询缓存，是便于观察的局部策略，不能直接当作大规模缓存方案。

主体 u1 与协作者 u2 属于 t1，u3 属于 t2；身份由夹具提供，实验没有认证服务。来源夹具分别提供用户偏好、工具观察和模型推断；每条来源带租户、拥有者、修订、内容哈希及确认状态。普通哈希只用于比较原样内容是否一致，不能证明陈述真实、摘要蕴含原文或数据已匿名化。

[逻辑时钟](../../glossary/distributed.md#distributed.clocks)初始为 100，默认期限为 120。数字是控制测试顺序的刻度，不是实际等待秒数、跨服务时间戳或生产时钟验证。所有文本均为合成的 language:zh、language:en 等值，公开 JSON 为复核保留历史观察，不能套用为真实个人内容的日志策略。

## 怎样复现与查看证据

在仓库根目录运行，无需第三方依赖：

```bash
python examples/memory_governance/lab.py
python examples/memory_governance/lab.py --check
```

第一条执行全部场景并覆盖本地 JSON；第二条执行同样检查而不覆盖已存 JSON。保留需要的基线后再重跑；保存最终运行输出后，可用 `python examples/memory_governance/lab.py --freeze-manifest` 更新实现和记录的摘要清单。

- [实验实现](../../../examples/memory_governance/lab.py)。
- [原始结果](../../../examples/memory_governance/results/results.json)：环境、逐项检查、读取证据、最终表数据与顺序事件。
- [运行输出](../../../examples/memory_governance/results/run.txt)及[字节数与 SHA256 清单](../../../examples/memory_governance/results/manifest.json)。

每类场景在仓库 .cache/memory-governance 中建立自己的临时目录，解析并检查目录范围，关闭连接后移除数据库；只保留上述文本证据。数据库重开场景先关闭再打开同名文件，没有强杀[进程](../../glossary/systems.md#systems.execution-units)或断电。

## 写入与读取实际做了什么

写入检查当前成员、来源作用域、修订、原样内容哈希、类型和必要确认。用户来源只写 preference，确认过的工具来源只写 observation，模型来源只写 hypothesis。后者保存为 candidate，不进入默认活动检索；把模型推断改标签为偏好，或者提交未经确认的工具观察，均被拒绝。工具确认只是可信夹具标记，本轮没有真实工具核查或人工确认界面。

已有记录的更新要求 expected_version 匹配，数据库条件更新影响一行才成功。新建默认 v1；删除提高版本，清空正文及来源引用，留下 tombstone 和身份等元数据；同 ID 不能重新新建，tombstone 也不能通过普通更新恢复。

检索缓存按租户、主体和查询分键。索引或缓存仅提供内部候选，程序逐项读取当前权威记录，核对当前成员、租户、拥有者或有效授权、活动状态、期限、来源类型、当前确认/活动状态及修订，以及记忆版本。返回的正文和来源字段取自权威记录。内部候选缓存可能包含同租户但无权返回的对象，不能将它直接暴露给用户或模型。

过期、撤权和删除并不要求旧副本先物理消失，读取检查仍会排除它们。权威 v2 配上旧索引 v1 时，本策略返回空结果，等新投影发布后才恢复召回；它选择了拒绝旧值，也承担暂时漏召回的代价。

## 21 类场景的实测结果

| 场景组 | 类数 | 实际观察 |
| --- | --- | --- |
| 用户、工具与模型来源 | 3 | 用户偏好和已确认工具观察返回准确内容与来源；模型推断保留为 candidate 且不发布 |
| 写入准入拒绝 | 4 | 推断冒充偏好、未确认工具、来源内容不匹配、非法期限或无法编码的输入均不建记录 |
| 两连接版本冲突 | 1 | 两条连接先读 v1；A 提交英文 v2 后，B 基于 v1 的中文更新返回 conflict，v2 保留 |
| 旧投影与迟到更新 | 2 | 旧缓存和旧索引均不返回；旧快照发布被拒；发布 v2 后返回准确新值与来源 |
| 期限边界 | 1 | 119 可读，120 排除；索引行仍在，过期快照不能发布 |
| 授权、租户与成员 | 3 | 协作者撤权后旧缓存/索引均不可读；给跨租户主体授对象权限并向其缓存填入外租户候选仍不返回；成员失效返回 denied |
| 删除、清理与重开 | 3 | tombstone 阻止旧副本、迟到回填及同 ID 重建；重开后仍有效；清理活动副本不改变旧备份 |
| 来源撤回与修订 | 2 | 确认被撤、类型改变或来源撤回均拒绝旧副本与发布；来源改版先使旧记忆失效，重新关联新来源后才返回 |
| 权威不可用分支 | 1 | available=false 时返回 unavailable，不从旧缓存降级返回正文 |
| 派生正文被改写 | 1 | 同版本索引和缓存内容被改为 forged，返回正文仍为权威的中文值 |

合计 21 类、157 个检查结果通过。类数表示独立时序，不是模型样本数；检查结果包括共享[不变量](../../glossary/systems.md#systems.atomicity)与临时文件清理。没有返回项的场景，其“所有返回项都合法”检查自然成立，必须同时看该场景明确的拒绝、空结果或状态断言。

检查使用显式异常中止失败，不依赖优化模式可能跳过的 assert。

每次读取还保存当时的逻辑时钟、身份、返回项和相应权威/来源/权限记录。独立断言逐项比较返回字段和当前记录，不直接调用生产路径的 live/can_read 判定函数作为唯一依据；它仍是本实验自带的局部校验，不是生产审计或自然语言事实验证。

## 两连接更新不等于所有并发都已覆盖

版本冲突确实使用两条 SQLite 连接，但按受控顺序先读再提交，没有同时运行线程。[SQLite 的隔离说明](https://www.sqlite.org/isolation.html)描述其写者串行化行为；本例只验证旧版本条件未匹配时拒绝更新。

authority 检查与 derived 发布不在一个跨库事务中，读取多个对象也没有建立统一快照。真实[并发](../../glossary/systems.md#systems.concurrency)可能发生在检查与使用之间，本轮没有验证线性一致、跨服务失效通知或所有回填竞争。需要相应保证时，应在实际权威边界设计原子条件、快照和版本协议，再单独验证。

## 删除、清理和备份分别看证据

删除后，活动记忆的正文和来源引用变为 NULL，但 ID、租户、拥有者、版本、状态及期限等元数据仍在。旧索引与缓存可暂时存在，但不再经本实验读取路径返回；purge 才移除指定索引行并清空缓存。

备份场景实际调用 [SQLite Backup API](https://www.sqlite.org/backup.html)复制删除前的权威数据库。随后在活动库删除并清理派生行，仍能从独立备份直接查询出 language:zh。备份没有连接到活动检索路径，场景结束后随临时目录清理；这不是“恢复后仍自动执行删除策略”的验证。

实验没有安全擦除数据库页、日志或介质，也没有删除来源哈希、审计记录和所有历史文本。依据 [SQLite secure_delete 说明](https://www.sqlite.org/pragma.html#pragma_secure_delete)，底层留存需要单独核对；一次逻辑更新、DELETE 或文件移除不能证明所有副本不可恢复。真实恢复流程如何重新应用删除和撤权记录，仍待独立演练。

## 已测范围与下一步

权威不可用场景只切换受控标志，没有破坏数据库或注入真实 I/O 故障；来源修订和撤回由夹具直接更新，没有实现实际来源适配器。派生内容改写只覆盖可解析候选，没有测试损坏 JSON、数据库损坏或任意存储攻击。

本轮没有测模型记忆抽取、语义冲突解决、检索质量、真实向量更新、分布式缓存、身份平台、并发撤权、跨进程时钟、物理擦除或备份恢复治理。它也不能撤回已经发送的内容或模型已有的上下文。

继续阅读[写入与来源](memory-writing-and-provenance.md)、[版本与失效](memory-versions-conflicts-and-expiry.md)、[权限与删除](memory-access-revocation-and-deletion.md)。自检：为什么“查不到”不能证明“已擦除”？来源修订和记忆版本各自控制什么？暂时拒绝旧索引会牺牲什么？资料核查及执行日期为 2026-10-20。
