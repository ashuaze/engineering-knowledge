---
id: "kb-architecture-refactoring-debt"
title: "技术债与重构：结构变好了，为什么还要核对行为"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "区分技术债、缺陷修复和保持行为的重构，解释特征测试、小步替换、迁移成本与维护优先级。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries", "kb-engineering-test-scopes"]
related: ["kb-engineering-static-analysis", "kb-engineering-code-review", "kb-engineering-dependency-governance", "kb-engineering-contract-compatibility", "kb-database-schema-migrations", "kb-devops-delivery-lifecycle", "kb-architecture-design-principles", "kb-architecture-patterns-collaboration", "kb-architecture-strangler-migration"]
tags: ["technical-debt", "refactoring", "behavior", "characterization", "migration"]
---

# 技术债与重构：结构变好了，为什么还要核对行为

学习入口：拆掉长函数、抽出公共模块或更换旧组件，怎样判断是改善维护，还是悄悄改变了业务？前置：[模块边界](module-boundaries-and-dependencies.md)、[测试范围](../engineering/test-scopes-and-doubles.md)。本文解释维护决策与变更边界；金额、工时及替换过程为教学设计，没有对真实项目[重构](../../glossary/architecture.md#architecture.debt)或测量收益。

抽象与复用的取舍见[设计原则](design-principles-contracts-and-abstraction-costs.md)，接口背后的行为见[设计模式与协作契约](design-patterns-collaboration-and-semantic-boundaries.md)；跨系统渐进替换另见[写入归属与回退](strangler-fig-migration-write-authority-and-rollback.md)，不把数据语义迁移自动当作保持行为的局部重构。

## 重构约束结构调整的行为边界

重构通过一系列小的结构变换改善代码，同时保持约定的可观察行为。不是所有修改旧代码都叫重构：修正金额、增加权限检查、改变错误码、迁移数据语义都可能是必要变更，但需要各自的行为验收。定义与小步方法见 [Martin Fowler 的重构说明](https://refactoring.com/)。

“可观察”不只包含正常返回值，也可能包含异常、数据写入、事件、调用次数、顺序和对外格式。哪些观察属于契约要先说明；性能、时序与[并发](../../glossary/systems.md#systems.concurrency)约束若对调用方有意义，也不能因函数签名相同就忽略。工具完成重命名只说明完成了一种转换，反射字符串、[序列化](../../glossary/runtime.md#runtime.serialization)字段和外部调用者仍需检查。

纸面例：两个商品各 5 分，优惠为 10%，明确采用精确十进制、每次舍入到整数分且半分向上。原规则逐项舍入优惠，各 0.5 分变成 1 分，总优惠 2 分、应付 8 分；若抽出公共函数时改成整单舍入，总优惠变为 1 分、应付 9 分。代码更短，却没有保持原行为。该数字只用于暴露“舍入位置”这一契约差异，不是实际结算结果。

## 技术债描述未来变更的额外代价

技术债是沟通设计取舍与后续成本的比喻。短期省下的工作，可能在之后的理解、修改、验证和交付中不断付出额外成本；也可能是得到新知识后才认识到原设计不合适。Fowler 的[技术债象限](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)区分有意/无意、审慎/鲁莽，不能把所有旧代码都简单归为当初偷懒。

长文件、重复代码和过时组件是调查线索，不是自动排序的债务金额。低频且稳定的模块未必值得立即大改；频繁阻碍需求、跨处同步规则或缺少验证入口的地方，可能更值得处理。代码覆盖率、复杂度或告警数量也不能单独代表维护成本。

一条可讨论的债务记录可写明：当前具体阻碍、影响哪些变化、已知约束、处理办法、暂不处理的代价、责任与重评条件。若只写“重构整个服务”，无法判断何时完成，也无法核对是否解决了原问题。

纸面估计：结构整理需 3 天，兼容与切换需 2 天；预计未来 8 次同类修改各省 0.5 天，仅这一项节省是 4 天，尚未覆盖 5 天投入。不能据此断言永远不做：缺陷风险、知识传播和不确定性也需讨论；同样不能把预计省时写成已实现的收益。这是估算口径练习，不是项目预测公式。

## 先理解当前行为，再决定保留什么

缺少可靠规格时，特征测试（characterization test）可先记录现有系统在选定输入下的实际可观察结果，为结构调整提供比较基线。它描述“现在怎样”，不自动说明“应该怎样”。本篇用此名称指这类现状记录；测试范围仍按[单元、集成与替身](../engineering/test-scopes-and-doubles.md)区分。

若观察到的行为本身有缺陷，应明确决定是先保持并隔离结构，还是在本次变更中修复，再分别声明预期。不要先把错误输出冻结为测试，再以“测试通过”证明业务正确；也不要为让重构通过而静默更新所有快照。时钟、随机性与外部响应要可控，比较时保留有意义的差异，不能把所有异常和顺序都归一化掉。

验证应围绕对外结果与边界，补足更改触及的代表性情况。替身调用不等于真实数据库或远端协议一致；替换状态存储、修改事务边界时，还要回到真实依赖和并发证据。测试通过支持已覆盖范围，不是任意输入下等价的形式证明。

## 小步替换需要兼容阶段和退出条件

可先建立窄的调用边界，让旧实现继续工作，再把调用者逐步移过去，引入新实现并核对差异，最后清理旧路径。这个思路参照 [Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)；抽象是替换工具，不必永久保留，也不保证所有组件都能按调用者逐个切换。

| 阶段 | 纸面替换计划 | 需要核对 |
| --- | --- | --- |
| 建立边界 | 旧实现经适配层调用 | 格式、异常、事务与副作用仍相同 |
| 引入新实现 | 受控输入比较结果 | 差异来自缺陷、语义还是环境 |
| 切换调用者 | 按明确范围启用新路径 | 新旧共存、写入与回退条件 |
| 清理 | 移除旧路径和临时开关 | 已无调用者，兼容与保留窗口结束 |

对纯计算可比较两份结果；对支付、发消息或写入等副作用，不能直接让两份实现都执行一遍。影子比较需隔离写入或采用明确的只读模型，不能因为称为“比较”就重复执行。数据库格式变化与回退仍应接回[迁移兼容](../database/schema-migrations-and-compatibility.md)，不能只切一个函数指针就承诺可回滚。

## 用原问题验收维护结果

验收可以是：同一规则只需改一个维护点、关键行为有明确验证入口、旧依赖已退出、回退窗口和限制已记录。需要实际变更记录才能说明这些结果已经发生；删除行数多、抽象层数多或测试数量多都不能替代它。

评审可配套读[代码评审与小步变更](../engineering/code-review-context-and-change-boundaries.md)，工具告警见[静态分析](../engineering/static-analysis-rules-and-findings.md)，组件替换见[依赖锁定与 SBOM](../engineering/dependency-resolution-lockfiles-and-sbom.md)。它们分别提供维护证据，不会把一个结构修改自动升级为完整业务验证。

自检：哪些观察必须保持？本次包含哪些有意行为变化？基线记录是否把缺陷误认成规格？新旧实现能否安全共存？临时兼容层由谁在什么条件下移除？预期收益有没有实际证据？

2026-10-20 核查 Fowler 的重构、技术债象限与 Branch by Abstraction 资料，状态为 source-checked。舍入、工时、现状记录和替换表为本文教学综合；未修改真实业务、执行特征测试、双路比较、迁移或测量维护收益。
