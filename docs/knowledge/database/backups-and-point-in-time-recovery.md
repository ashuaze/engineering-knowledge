---
id: "kb-database-backups-pitr"
title: "备份与时间点恢复：备份成功为何还不够"
kind: "concept"
domain: "database"
status: "evolving"
summary: "区分逻辑与物理备份、归档链和恢复目标，用数据验收说明可恢复性的证据。"
created: "2026-10-19"
updated: "2026-10-23"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-database-wal-recovery"]
related: ["kb-database-recovery-lab", "kb-database-schema-migrations", "kb-devops-delivery-lifecycle", "kb-distributed-consistency", "kb-reliability-slos", "kb-reliability-fault-domains-recovery", "kb-cache-object-storage"]
tags: ["backups", "pitr", "recovery"]
---

# 备份与时间点恢复：备份成功为何还不够

备份任务返回成功，只证明某项制作流程达到了它的成功条件。恢复需要的文件、连续日志、软件与配置是否齐全，恢复出的业务状态是否正确，仍需另行验证。

前置知识：[WAL 与崩溃恢复](wal-and-crash-recovery.md)。本文以 PostgreSQL 18 为参照，讨论备份形式、恢复链和验收方法，不提供企业备份策略或已完成容灾切换的承诺。

## 先定义要恢复的对象和时间

先写明故障模型：误删表、存储丢失、应用写坏数据或整机不可用，所需恢复范围不同。再明确允许丢失的数据时间范围（[RPO](../../glossary/reliability.md#reliability.recovery)）与期望恢复服务的时间（RTO）。这是目标，不能用“每天备份一次”直接代替实测达成情况。

教学例子：某次备份保存于上午，下午发生误删除；如果只拥有上午备份，恢复它可能丢掉中间本来正确的修改。若拥有覆盖所需区间的日志与可用基础备份，则可设计更精细的恢复目标，但仍需核对误操作发生和提交的边界。

## 逻辑备份与物理备份保留什么

| 形式 | 保存与恢复的主要对象 | 需要注意 |
| --- | --- | --- |
| [逻辑备份](../../glossary/database.md#database.backups)，例如 pg_dump | 对象定义与数据的逻辑表示 | 可按工具能力选择对象；角色等集群级信息需另行安排 |
| 物理基础备份，例如 pg_basebackup | 数据库集群的文件及配套恢复材料 | 版本、布局与环境兼容约束更强；不能随意当作单表文件恢复 |
| 基础备份加连续 [WAL](../../glossary/database.md#database.recovery-log) 归档 | 从基础备份向后推进所需的历史 | 目标必须在可到达范围内，缺失中间材料会破坏恢复路径 |

逻辑备份的快照与版本迁移边界见 [SQL Dump](https://www.postgresql.org/docs/18/backup-dump.html)；物理工具的集群范围及 WAL 收集选项见 [pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html)。pg_dump 的输出不能直接作为物理 WAL 重放的起点，二者不是同一格式的不同压缩方式。

复制正在运行的普通数据目录也不能自动获得一致备份。停机复制、一致快照及在线基础备份具有各自前提；跨卷的数据、WAL 和表空间还需保持相应一致性，见[文件系统备份说明](https://www.postgresql.org/docs/18/backup-file.html)。

## 时间点恢复需要连续的恢复链

PITR（Point-in-Time Recovery）利用较早的物理基础备份和后续 WAL，恢复到指定边界。归档必须覆盖备份与恢复目标所需的连续区间；只保留“最新一个日志文件”不足以证明能够到达目标。具体流程见 [PostgreSQL 连续归档与 PITR](https://www.postgresql.org/docs/18/continuous-archiving.html)。

```text
可用基础备份 → 备份一致性所需 WAL → 后续连续 WAL → 选定恢复目标
```

恢复目标可以用时间、事务或命名恢复点等方式表达，具体配置不能混为一谈。按时间恢复时要说明时区和边界是否包含目标事务；按命名点恢复时，要保证名称对应预期历史。目标与到达后的 pause/promote/shutdown 行为见 [Recovery Target 配置](https://www.postgresql.org/docs/18/runtime-config-wal.html)。

恢复后产生的新历史还涉及 timeline。时间相近、文件名看似完整，并不能证明材料来自同一集群和预期时间线。记录基础备份身份、WAL 范围与目标，而不是仅记录一个可读时间戳。

## 校验工具和恢复演练各自证明什么

文件数量、校验和和备份清单可以帮助发现材料损坏或不匹配；pg_verifybackup 根据备份清单执行相应核验，但通过它仍不能替代实际恢复与业务检查。工具自己的[验证边界说明](https://www.postgresql.org/docs/18/app-pgverifybackup.html)也强调这一点。

| 验收层次 | 应留下的证据 |
| --- | --- |
| 制作完成 | 工具版本、退出结果、备份身份与 WAL 收集方式 |
| 材料完整 | 清单与校验结果、归档连续性及访问权限 |
| 数据库可恢复 | 独立目录/实例、实际重放、到达目标的日志与恢复状态 |
| 业务可使用 | 应保留和应排除的数据、关键约束、应用兼容与外部结果核对 |
| 目标可兑现 | 从事件发生到可用状态的全流程计时与数据损失范围 |

只做第三层中的“能启动”，也可能遗漏恢复目标设错、误操作已被重放或应用依赖缺失。校验一行关键数据通常比只看[进程](../../glossary/systems.md#systems.execution-units)存活更接近业务验收，但仍需按真实业务扩大检查范围。

## 保留与恢复需要共同设计

基础备份和 WAL 的保留规则必须共同维护；清理一个仍被恢复链依赖的对象，可能让后续材料单独无用。归档失败也应被发现：本机提交成功不保证归档副本已经可用，归档[延迟](../../glossary/performance.md#performance.latency-throughput)会影响实际恢复能力。

备份含有业务数据，还需要合适的访问控制、加密与密钥恢复安排。把副本、归档和源库都放在同一[故障域](../../glossary/reliability.md#reliability.fault-domains)，不能据此声称已经验证源存储丢失后的恢复。本文的本机实验也明确保留这个限制。

对象版本保留、删除标记与分段上传的恢复边界，继续见[对象存储与预签名访问](../cache-search/object-storage-versions-uploads-and-presigned-access.md)。保存旧版本不自动建立独立备份，也不证明业务记录、访问能力和恢复权限已一起协调。

## 实测入口与自检

配套[恢复实验](backup-recovery-lab.md)在独立 PostgreSQL 18.0 集群制作并验证基础备份，再把后续 WAL 重放到命名恢复点，核对被删数据恢复、目标后的新增数据被排除。它没有按墙上时间设置 recovery_target_time，也未恢复到生产服务、执行 promotion 或测量 RPO/RTO。

自检：一份 pg_dump 能否直接配合物理 WAL 回到下午某时刻？清单校验通过而恢复行集不对，可能是哪层边界出错？为什么“副本跟得很快”不能单独证明误操作前的数据可恢复？

核查日期：2026-10-19。除配套实验明示的本机过程外，策略表和验收层次为设计建议；逻辑备份、跨版本迁移、[对象存储](../../glossary/cache-search.md#cache-search.objects)和[多地域](../../glossary/devops.md#devops.regions)恢复没有新增实测。

服务级的共同故障、依赖恢复与 RTO/RPO 计时见[故障域、冗余与恢复目标](../reliability/failure-domains-redundancy-and-recovery.md)。该篇的时间线为教学推演；本机恢复实验仍仅证明其明示的目标行集，不证明跨故障域或完整业务恢复目标。
