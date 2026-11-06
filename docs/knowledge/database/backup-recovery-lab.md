---
id: "kb-database-recovery-lab"
title: "实验：从基础备份恢复到指定恢复点"
kind: "lab"
domain: "database"
status: "evolving"
summary: "在独立 PostgreSQL 18.0 集群制作基础备份、归档 WAL，并实际重放到命名恢复点核对行集。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-database-wal-recovery", "kb-database-backups-pitr"]
related: ["kb-database-schema-migrations", "kb-devops-delivery-lifecycle", "kb-database-inventory-lab", "kb-api-idempotency"]
tags: ["postgresql", "backups", "recovery"]
---

# 实验：从基础备份恢复到指定恢复点

## 要验证什么

基础备份里只有记录 1。随后源库提交记录 2，创建命名恢复点，再删除记录 2 并提交记录 3。能否从备份加归档 [WAL](../../glossary/database.md#database.recovery-log) 恢复出 1、2，同时排除目标之后的删除与新增？

本实验实际恢复到 PostgreSQL 的命名恢复点，属于指定历史边界的归档恢复。它没有使用 recovery_target_time，也没有模拟[进程](../../glossary/systems.md#systems.execution-units)崩溃、断电、存储损坏、生产切换或数据库迁移。机制先读[WAL 与恢复](wal-and-crash-recovery.md)、[备份与时间点恢复](backups-and-point-in-time-recovery.md)。

## 环境、依赖与运行

2026-10-19 实际环境：Windows x64、PostgreSQL **18.0**、Python **3.13.13**。fsync、synchronous_commit、full_page_writes 均为 on，wal_level=replica，源库 archive_mode=on，WAL 段大小 16 MB。使用前几轮同一份 EDB Windows 二进制分发；包来源与摘要见[证据清单](../../../examples/backup_recovery/results/manifest.json)。

运行要求 Python **3.11+** 标准库，以及 PostgreSQL 18 的 psql、initdb、pg_ctl、createdb、pg_basebackup、pg_verifybackup、pg_waldump。工具齐备后从仓库根目录执行，将目录换成自己的路径：

```bash
python examples/backup_recovery/lab.py --pg-bin /path/to/pgsql/bin
# 或 npm run lab:recovery -- --pg-bin /path/to/pgsql/bin
python -m unittest discover -s examples/backup_recovery -p 'test_*.py' -v
```

运行器见[lab.py](../../../examples/backup_recovery/lab.py)，归档与恢复复制辅助程序见[archive.py](../../../examples/backup_recovery/archive.py)，辅助程序的[契约测试](../../glossary/engineering.md#engineering.contracts)见[test_archive.py](../../../examples/backup_recovery/test_archive.py)。不需要额外数据库驱动。

所有实例、基础备份、归档与恢复副本都放在仓库 `.cache` 内独立的工作目录。只监听回环地址，源库和恢复库使用不同临时端口，没有连接已有实例的入口。采用本机实验用 trust [认证](../../glossary/security.md#security.identity)；Unix 环境应由可运行 PostgreSQL 的普通用户执行。默认文本输出留在 `.cache/backup-recovery/`，可用 `--output` 改变结果 JSON 路径。

结束时先停止所有自建实例，再核对并移除所属工作目录。无法确认停止则保留目录并报错。源库在恢复实例启动前已正常停止，恢复实例在检查后也停止；这不是崩溃恢复测试。二进制备份与归档属于临时实验数据，不作为公共下载产物保留。

## 实际执行步骤

1. 创建独立源集群和普通表 kb_events，提交 `(1, baseline)`；先切换 WAL，并等待文件归档完成状态，确认归档在备份前实际可用。
2. 用 pg_basebackup 制作 plain 格式基础备份，`-Xstream` 收集备份所需 WAL，`-cfast` 用于该小型实验的[检查点](../../glossary/database.md#database.checkpoints)；随后执行 pg_verifybackup。
3. 再次切换 WAL，使后续目标落入基础备份不包含的新日志段；提交 `(2, before-target)`。
4. 调用 `pg_create_restore_point('kb_before_mistake')`，保存返回 LSN 和日志段名。之后在一个事务中删除记录 2、插入 `(3, after-target)` 并提交。
5. 切换 WAL，等待目标所在段的归档 `.done` 状态，保存大小、摘要与归档统计，再正常停止源库。
6. 把基础备份复制到新的恢复目录，配置 archive_mode=off、restore_command、recovery_target_name、recovery_target_action=pause、recovery_target_timeline=current，并创建 recovery.signal。
7. 启动恢复实例，轮询实际恢复暂停状态，读取并比较目标行集，保存日志后停止实例、清理临时数据。

命名标记的含义见 [PostgreSQL 备份控制函数](https://www.postgresql.org/docs/18/functions-admin.html)。名字、LSN 和墙上时间是不同口径；本实验用命名点减少按时间选择目标时的歧义，没有验证时间目标的时区与包含边界。

## 最终记录与检查

修正归档辅助程序的 Windows 重复同步句柄问题后，完整流程重新执行并通过。以下只引用该次最终[结果 JSON](../../../examples/backup_recovery/results/results.json)。

| 阶段 | 实际行集或状态 |
| --- | --- |
| 备份前基线 | `1:baseline` |
| 命名点之前已提交 | `1:baseline`、`2:before-target` |
| 源库后续变更后 | `1:baseline`、`3:after-target` |
| 恢复点暂停后 | `1:baseline`、`2:before-target` |
| 备份验证 | pg_verifybackup 返回 `backup successfully verified` |
| 恢复状态 | in_recovery=true、pause_state=paused、transaction_read_only=on |

运行器的 **13 项恢复检查**全部通过，覆盖版本与持久化设置、备份前归档完成、基础备份验证、目标 WAL 不在基础备份而已归档、三个预期源库行集、恢复暂停与只读状态、恢复行集相等、日志中实际取回目标 WAL，以及端口分离。

其中“目标日志段不在基础备份”和恢复日志中的 helper 输出共同支持：本次恢复确实依赖了备份之后的归档材料，而不是只把基线副本启动起来。目标 LSN、清单 WAL 范围和实际重放位置保存在 JSON；不能用本次固定位置推导其他备份的边界。

原生[基础备份清单](../../../examples/backup_recovery/results/backup_manifest.json)保留文件身份、校验信息和 WAL 范围；[源库日志](../../../examples/backup_recovery/results/source.log.txt)记录归档，[恢复日志](../../../examples/backup_recovery/results/restored.log.txt)记录取回日志段、达到一致状态以及停在命名点。`missing` 某个可选历史文件的消息与最终目标未到达是不同情形；以完整恢复状态和日志解释结果。

## 归档辅助程序的四项契约

独立测试验证：相同文件重复归档可成功；同名但不同内容必须失败并保留原归档；源文件不存在不能假报成功；恢复复制可替换属于恢复过程的临时输出。四项均通过，原始输出见[测试记录](../../../examples/backup_recovery/results/archive-tests.txt)。

这些检查针对本机复制协议。辅助程序对文件执行同步，POSIX 路径还同步目录；它没有实现[对象存储](../../glossary/cache-search.md#cache-search.objects)、加密、远程持久化确认或中途写入失败后的自动修复，也未证明 Windows 文件元数据在断电后的耐久性。不能把它直接当成生产归档代理。

## 能证明与不能外推的范围

本次证据支持该版本、该基础备份和归档链能够到达命名点并返回预期行集。pg_verifybackup 通过并非全部证明；实际恢复和业务行集检查提供了额外范围的证据。参照[工具边界](https://www.postgresql.org/docs/18/app-pgverifybackup.html)理解其分工。

本实验只执行一次完整恢复，使用同一主机与存储[故障域](../../glossary/reliability.md#reliability.fault-domains)，不是跨机容灾。没有测量恢复全过程耗时、数据损失窗口或生产 [RPO](../../glossary/reliability.md#reliability.recovery)/RTO；没有删坏归档的负向数据库恢复实验、[逻辑备份](../../glossary/database.md#database.backups)恢复、时间目标、跨 timeline、增量链、扩展/表空间、promotion 或应用接管。

目标之后本来正确的写入也会被排除在该恢复行集之外。恢复数据库不会撤销外部支付、邮件或消息，接回业务前仍需确认恢复范围和外部状态；本实验无这些外部动作。

## 自检与来源

如果基础备份不包含记录 2，它是怎样出现于恢复结果中的？如果只有“数据库已可读”日志，没有暂停位置与行集检查，能否证明停对目标？为什么本次恢复成功仍不能说明发生断电时不会丢数据？

来源核查与最终执行日期：2026-10-19。

- [PostgreSQL 18：Continuous Archiving and PITR](https://www.postgresql.org/docs/18/continuous-archiving.html)
- [PostgreSQL 18：pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html)
- [PostgreSQL 18：Recovery Target](https://www.postgresql.org/docs/18/runtime-config-wal.html)
- [数据库迁移兼容](schema-migrations-and-compatibility.md)：历史数据库恢复不能替代混合版本兼容验证。
