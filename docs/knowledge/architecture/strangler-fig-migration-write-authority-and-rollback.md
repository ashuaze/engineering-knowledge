---
id: "kb-architecture-strangler-migration"
title: "渐进替换与写入归属：流量切回为什么不等于数据回退"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "区分路由切换、模型翻译、历史追平和写入权移交，说明绞杀者模式、双写窗口、影子比较与回退条件。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries", "kb-database-schema-migrations"]
related: ["kb-architecture-deployment-boundaries", "kb-architecture-quality-decisions", "kb-database-cdc", "kb-distributed-leases-fencing", "kb-messaging-outbox", "kb-architecture-refactoring-debt"]
tags: ["strangler-fig", "migration", "write-authority", "cutover", "rollback"]
---

# 渐进替换与写入归属：流量切回为什么不等于数据回退

学习入口：新服务已接住大部分流量，出了问题把路由切回旧系统就行吗？如果新系统已经接受写入，旧数据是否仍能支撑正确业务？渐进迁移需要同时管理入口、语义、数据与执行者，不能只画一层代理。

前置：[模块边界](module-boundaries-and-dependencies.md)、[迁移与兼容](../database/schema-migrations-and-compatibility.md)。本文解释迁移机制与验收条件，流程是明确假设下的教学设计，不是生产切换手册。没有回填数据、配置路由、移交写入权或执行回退。

## 绞杀者模式逐步替换业务能力

Strangler Fig 通过可控入口逐步把一部分能力交给新实现，保留尚未迁移的旧功能，减少一次性重写的范围。原意与渐进现代化思路见 [Fowler 的 Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)及作者团队的 [Patterns of Legacy Displacement](https://martinfowler.com/articles/patterns-legacy-displacement/)。目标可以是新系统、新模块或新的协作方式，不要求终点必须是[微服务](../../glossary/architecture.md#architecture.microservices)。

切分单位应能说明业务结果和依赖：某租户、某类操作或一项能力，而非只按 URL 数量统计完成率。新系统若仍依赖旧系统内部表和隐含时序，入口换了也可能没有真正解除旧依赖。

## 四条迁移线要对齐

| 迁移线 | 要回答什么 | 常见遗漏 |
| --- | --- | --- |
| 流量入口 | 本次请求送给谁，是否有旁路 | 后台任务、旧连接、消息消费者仍直接调用旧实现 |
| 契约与模型 | 新旧参数、状态和结果如何翻译 | 接收成功被误译成业务完成，缺失/删除语义不一致 |
| 数据连续性 | 哪个快照起点、如何追到当前变化 | 只复制存量，不处理之后的更新、删除和乱序 |
| 写入归属 | 这项状态由谁最终接受和确认修改 | 路由切换后旧执行者仍可以提交 |

[AWS 的模式说明](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html)讨论代理、反腐层和新旧数据同步；本文只引用机制，不采用其具体云产品配置。反腐层负责阻止旧模型语义侵入新模型，不能只靠改字段名完成。

同一[进程](../../glossary/systems.md#systems.execution-units)内部替换库或组件时，也可以先用抽象层包住交互，再逐步切换实现，见 [Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)。它与长期 Git 功能分支不是一回事，也不自动迁移外部数据。

## 双写不是天然一致的过渡方案

教学时序：业务请求先写旧库成功，再写新库；进程在第二次提交前崩溃。两边立即分叉。把两次写入顺序调换，只改变谁可能领先；失败重试还可能产生重复副作用。

迁移期间应明确权威来源，并选择可恢复的变更传播或共同提交协议。若使用源端日志、CDC 或 [Outbox](../../glossary/messaging.md#messaging.outbox)，仍要处理接纳、位点、顺序、去重与目标提交，见 [CDC](../database/cdc-snapshots-log-positions-and-replay.md)与 [Outbox](../messaging/transactional-outbox.md)。队列存在或计数相等不能单独证明所有键、删除和字段语义一致。

## 纸面写入权移交：追平以后还要封住旧入口

假设迁移单位为租户 T，旧系统 O 是唯一权威写入者；快照和变更日志有一致起点，102/103 是同一教学写入历史的连续标号，不表示不同数据库的原生日志位置可以直接比较。采用允许短暂暂停 T 写入的教学方案：

1. 从一致快照复制到新系统 N，并持续应用之后的变更。O 继续写，N 暂不对外接受业务写入。
2. 暂停 T 的新写入，排空或明确处置 O 的在途写操作，确认最终提交位置为 102。
3. N 追平到 102，并核对状态语义；通过可强制执行的写入隔离禁止 O 的后续修改，确认所有旁路和旧执行者也受约束。
4. 在上述条件成立后才允许 N 成为 T 的权威写入者；N 接受新写入 103。

这里的“禁止旧写”需要真实的权限、资源端隔离或所有权协议支持；代理记住一个新版本号本身不够。若仍有旧任务能提交，就未完成移交。旧执行者隔离与租约的边界见 [Fencing](../distributed/leases-heartbeats-and-fencing.md)。本例没有给出所有平台都能照搬的原子移交算法，也不承诺零停顿。

## 回退能力随迁移阶段改变

在 N 尚未接受新写入、O 仍是权威且契约兼容时，撤回部分读取或计算流量可能比较直接。N 提交 103 后，如果 O 只到 102，单纯把路由切回 O 便可能丢失业务可见的新状态，甚至覆盖后续更新。

此时需要判断：新写入能否被旧模型完整表示、旧版本能否理解新状态、是否有可靠反向传播，以及再次移交前怎样暂停/排空 N。在具备兼容、反向传播与校验条件的回退方案中，必须先暂停并排空 N，强制禁止它的后续提交，再让 O 追平到确认的最终位置并校验；之后才可恢复 O 的写入权。若这些条件不成立，应按预先设计的前向修复或恢复策略处理；“代码可回滚”不能替代数据恢复。

恢复备份也不等于撤销已发生的外部行为。已经发送的通知、扣款请求或库存占用可能需要各自核对与补偿，不能通过重放历史再次触发。

## 影子比较与退役需要明确证据

可在不产生重复业务副作用的条件下，把相同输入交给新旧路径并比较。必须说明观察的数据位置、时间、排序和允许差异；“都是只读接口”也不自动证明没有缓存写入或其他副作用。比较结果相同，只支持该输入和条件，不能证明所有历史与故障路径等价。

退役旧系统前还需覆盖定时任务、消息、批量作业、恢复入口和旧凭据，确认无人再依赖旧语义或资源。把迁移代理和翻译层也列为有退出条件的临时负担，避免新旧系统永久双轨。相关目标与重评条件见[质量属性与架构决策](quality-attribute-scenarios-tradeoffs-and-adrs.md)。

## 自检

1. 为什么迁移完成率不能只按新系统承接的 URL 或请求比例判断？
2. 旧库提交后、新库提交前崩溃，双写出现什么窗口？调换顺序能否消除？
3. N 已追到 102，为什么仍不能立刻宣布它是唯一写入者？
4. N 提交 103 后切回只到 102 的 O，会有什么风险？回退还需验证哪些条件？
5. 影子结果一致和线上旧流量为零，各自还不能证明什么退役条件？

## 来源与核查

2026-10-26 核查 Strangler Fig、Patterns of Legacy Displacement、Branch by Abstraction 原文及 AWS 模式说明。本文为 source-checked 概念文章；双写、序号与移交为纸面推演，未执行迁移/追平、强制隔离、影子对比、旧系统退役或数据/业务回退实验。
