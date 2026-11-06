---
id: "kb-reliability-fault-domains-recovery"
title: "故障域、冗余与恢复目标：有副本为什么仍可能恢复不了"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "从共同故障与业务依赖解释冗余、故障切换和灾难恢复，区分 RTO/RPO 目标、实际恢复时间与可恢复数据边界。"
created: "2026-10-20"
updated: "2026-10-27"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-reliability-slos", "kb-database-backups-pitr"]
related: ["kb-devops-declarative-health", "kb-devops-delivery-lifecycle", "kb-distributed-consistency", "kb-distributed-leases-fencing", "kb-database-recovery-lab", "kb-reliability-failure-isolation", "kb-reliability-incident-response", "kb-reliability-availability-models", "kb-reliability-chaos-experiments"]
tags: ["failure-domain", "redundancy", "recovery", "rto", "rpo"]
---

# 故障域、冗余与恢复目标：有副本为什么仍可能恢复不了

学习入口：已经有三个副本和定期备份，为什么一次故障仍让服务长时间不可用？前置：[SLI/SLO](slis-slos-and-error-budgets.md)与[备份、恢复链](../database/backups-and-point-in-time-recovery.md)。本文讨论服务层面的故障假设、依赖和恢复目标；时间线是教学推演，没有执行跨节点、可用区或地域切换。

在线比例、连续工作与正确恢复的区别见[可用性与可靠性](availability-reliability-and-observation-windows.md)；怎样把故障假设变成受控验证见[混沌工程与受控故障](chaos-engineering-hypotheses-stop-conditions-and-recovery.md)。

## 副本数量之外，还要画出共同故障

[故障域](../../glossary/reliability.md#reliability.fault-domains)是分析某类故障会同时影响哪些组件的边界。物理主机、机架、可用区和地域可以构成不同范围，但共同配置、权限、软件版本与依赖也会造成关联失败。隔离设计要明确针对哪种故障，而不是只统计实例数量。[AWS 故障隔离说明](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/use-fault-isolation-to-protect-your-workload.html)讨论了用边界限制影响范围。

| 教学部署 | 能减少的某类影响 | 仍共享的风险 |
| --- | --- | --- |
| 同一节点运行三个实例 | 部分单[进程](../../glossary/systems.md#systems.execution-units)退出的影响 | 节点内核、供电和本地存储 |
| 多节点、同一可用区 | 单节点失效 | 可用区范围的设施或网络故障 |
| 跨可用区 | 某一可用区失效 | 区域服务、共同控制依赖、全量错误配置 |
| 跨地域并保留恢复材料 | 某些区域级故障 | 身份与密钥、共同软件缺陷、误操作传播，以及恢复流程自身 |

表格是分析框架，不是任何云平台的[可用性](../../glossary/reliability.md#reliability.availability)承诺。物理边界与逻辑依赖会交叉：应用分散部署，但仍只依赖一处数据库、[镜像](../../glossary/devops.md#devops.containers)仓库或解密服务，恢复时就可能一起受阻。不能在未验证独立性时，把单实例故障概率简单相乘来声称整体可靠性。

冗余还需要剩余容量。三个副本刚好共同承担全部峰值，失去一个之后，其余实例可能过载，再触发更多[超时](../../glossary/api.md#api.retries)或退出流量。除了放在哪里，还要问失去一个故障域后，剩余实例与下游资源是否能承担约定业务。

## 高可用、切换和灾难恢复分别安排什么

高可用设计减少服务中断的发生或持续时间；[故障切换](../../glossary/reliability.md#reliability.dr)把服务角色或流量转移给另一组可用资源；灾难恢复则准备在选定严重故障后重建可用业务。它们有交集，不能只以“是否自动”或“是否跨地域”区分。恢复策略及成本取舍可参考 [AWS 灾难恢复策略](https://aws.amazon.com/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-i-strategies-for-recovery-in-the-cloud/)。

副本通常追随当前状态，也可能复制误删与错误写入；历史备份提供另一种恢复路径，但不自动拥有可用算力、密钥、路由或应用配置。恢复速度、允许丢失范围、资源成本和运行复杂度，需要一起比较。

故障切换还需要确定谁可以写。旧主机失联不等于停止执行；如果新旧两边同时产生不能合并的写入，恢复出的结果可能互相冲突。安全的主角色交接需按系统协议落实隔离、代次或其他写入资格约束，见[租约与 Fencing](../distributed/leases-heartbeats-and-fencing.md)。切换不是简单把一个地址改到新机器。

## RTO 与 RPO 先规定可以接受什么

[RTO](../../glossary/reliability.md#reliability.recovery)（Recovery Time Objective）规定服务中断到恢复之间可接受的最长时间；RPO（Recovery Point Objective）规定可接受的数据恢复点相对事故或约定数据丢失事件时刻的落后范围，常用时间表达能容忍的数据丢失程度。它们是面向业务与故障情形的目标，需要匹配依赖系统的能力，不能用一份配置证明已经达成。定义和目标制定依据见 [AWS REL13-BP01](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_for_recovery_objective_defined_recovery.html)。

| 需写清的约定 | 为什么影响判断 |
| --- | --- |
| 业务范围与故障情形 | 订单查询恢复不等于支付与履约都恢复；误写与存储失效也有不同路径 |
| 中断起点与恢复条件 | 不能等运维开始操作才计时，也不能数据库启动就停止业务恢复计时 |
| 可接受的数据边界 | 哪些已确认写入允许丢失，哪些结果必须重新核对 |
| 依赖、身份与配置 | 缺少必需依赖时，应用进程运行仍可能无法服务 |
| 验证方法与负责人 | 明确谁确认关键结果、如何留证据、目标失效时怎样处理 |

RPO 的分钟数不直接给出丢了多少订单或多少钱；业务量与关键程度仍需另行评估。RTO 也不等于平均修复耗时或一个恢复命令的执行时长。[SLO](../../glossary/reliability.md#reliability.slos) 衡量约定窗口的用户结果，RTO/RPO 关注某类恢复的目标，不能直接互相换算。

## 用完整时间线区分目标与观察值

教学设定：订单查询业务目标为 RTO ≤20 分钟、RPO ≤5 分钟；事故前已明确恢复需要正确数据、可用身份和完整查询路径。假设所有数据边界均已通过一致性核验，才使用下表判断：

| 时间 | 教学事件 | 计时或数据含义 |
| --- | --- | --- |
| 09:58 | 最后可确认、可一致恢复的业务数据边界 | 不是仅凭备份文件名推定 |
| 10:00 | 业务中断 | 本情形的恢复计时起点 |
| 10:03 | 发现并确认事故 | 已经消耗 3 分钟 |
| 10:12 | 数据库与必要实例启动 | 尚未完成全部业务验收 |
| 10:17 | 身份、路由、数据和查询能力符合预设恢复条件 | 本情形实际恢复时间为 17 分钟 |

在这些假设下，恢复时间 17 分钟满足本次 20 分钟目标；恢复点落后事故 2 分钟，满足本次 5 分钟目标。2 分钟依据事故时刻与可恢复边界比较，不是用 10:17 减去 09:58；具体损失的已确认写入仍需核对。

若直到 10:26 才拿到解密密钥并完成同样验收，就不能因数据库在 10:12 启动而声称达成 RTO。若实际只能恢复到 09:50，即使 10:10 就恢复服务，数据目标仍未满足。两个目标需要分别验收，也只证明这次设定覆盖的情形。

误写恢复还可能要求回到错误发生之前，同时补回其后正确的操作。这与单纯恢复最新副本不同；旧数据上的重放、消息重复和外部支付结果需要共同核对，不能把“回到某个时间”当作所有业务都已一致。

## 恢复顺序由依赖和安全边界决定

恢复计划应列出数据源、日志、软件制品、配置、密钥、身份、网络、域名和第三方依赖，并标出哪些恢复步骤自己依赖已失效的环境。跨地域留了备份，但只有故障地域的身份系统能[授权](../../glossary/security.md#security.identity)取回密钥，就是一条需要提前验证的[循环依赖](../../glossary/runtime.md#runtime.modules)。

以下为教学检查顺序，不是平台自动执行的事务：

```text
确认影响范围与恢复路径，按策略约束旧写入者
→ 确认可用恢复材料、身份和依赖
→ 恢复一致数据与兼容的应用/配置，准备所需容量
→ 验证关键约束、外部结果和真实访问路径
→ 按计划切流并持续观察，记录时间与数据边界
```

重新开放写入与切流需有明确条件；恢复后的回切也可能再次产生数据分叉或容量问题，应单独规划。[DNS](../../glossary/networking.md#networking.dns)、代理和旧连接不会因为控制台显示“已切换”而同步完成，见[连接池与生命周期](../networking/http-reuse-pools-and-timeouts.md)。

恢复过程中的分工、交接、止损和结束条件见[事故响应与复盘](incident-response-recovery-and-postmortems.md)，其中用独立时间线区分业务恢复与集中响应结束。

## 演练应证明哪些范围

从低风险的材料检查与桌面推演开始，再按授权和环境开展实际恢复。演练应记录故障模型、受影响依赖、起止条件、关键数据和计时，而不只记录“任务成功”。恢复策略需要周期验证，相关实践见 [AWS 灾难恢复规划](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)。

已有[本机备份恢复实验](../database/backup-recovery-lab.md)验证了独立 PostgreSQL 集群到命名恢复点的目标行集；源库与材料仍在本机，且未恢复完整业务或测量 RTO/RPO。它不能证明跨故障域灾难恢复目标已达成。容器的[健康探针与替换](../devops/declarative-deployments-and-health-probes.md)同样只覆盖其中一部分运行机制。

自检：三个副本共同依赖什么？副本是否会复制这次错误？恢复出的不同存储能否组成一致业务状态？密钥服务不可用时还能否取回数据？实际恢复时间包含哪些等待？哪些故障仍没有证据？

2026-10-20 核查 AWS 故障隔离、灾难恢复与 RTO/RPO 资料，并结合已有数据库与分布式概念界定范围。状态为 source-checked；部署表、时间线和恢复顺序为教学设计，未执行故障切换、旧主隔离、跨地域恢复、回切或业务恢复目标实验，未对本知识库承诺任何 RTO/RPO 数值。
