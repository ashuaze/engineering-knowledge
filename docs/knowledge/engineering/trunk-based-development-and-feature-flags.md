---
id: "kb-engineering-trunk-flags"
title: "主干开发与功能开关：代码已合并，为什么功能还不能开放"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "连接小批集成、反馈预算与功能开关，解释部署和开放的区别、配置失败、数据兼容、组合验证及开关清理责任。"
created: "2026-10-22"
updated: "2026-10-27"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-engineering-code-review", "kb-devops-delivery-lifecycle"]
related: ["kb-engineering-test-stability", "kb-engineering-contract-compatibility", "kb-database-schema-migrations", "kb-security-object-authorization", "kb-engineering-tdd-bdd", "kb-engineering-design-documents", "kb-engineering-golden-paths-dx"]
tags: ["trunk", "continuous-integration", "feature-flags", "delivery", "compatibility"]
---

# 主干开发与功能开关：代码已合并，为什么功能还不能开放

学习入口：功能还要开发两周，怎样频繁集成而不把半成品开放给用户？前置：[代码评审](code-review-context-and-change-boundaries.md)、[交付生命周期](../devops/build-deploy-rollback.md)。本文说明集成、反馈和行为开放之间的关系；订单场景及检查矩阵为纸面设计，没有修改真实分支策略、接入开关平台或执行发布。

小步集成的行为反馈见[TDD与BDD](tdd-bdd-examples-and-feedback-loops.md)，重大决定的历史与实施范围见[设计文档与决策记录](design-docs-rfcs-adrs-and-decision-lifecycles.md)，默认路径及持续支持见[黄金路径与开发者体验](golden-paths-developer-experience-and-platform-feedback.md)。

## 主干开发缩短共同集成的间隔

[主干开发](../../glossary/engineering.md#engineering.trunk)将工作拆成小批，频繁集成到共同主干，让不一致尽早暴露。仅仅每天从主干拉取，而自己的变更仍数周不合回，并没有完成双向集成。[DORA 的说明](https://dora.dev/capabilities/trunk-based-development/)强调小批和频繁合并；其时间尺度是实践参照，不能用机械的分支数量代替行为判断。

短分支和合并前评审可以服务这个目标。关键是等待、差异规模和共同验证能否支持频繁集成，不需要从概念推出“必须绕过分支保护”。主干可用也不等于每次合并都立即上线；集成策略、制品构建、部署和业务开放各有接受条件。

假设订单页要换一种优惠算法。可以先引入明确接口并保持旧行为，再加入默认不可达的新实现，最后逐步开放新路径。每一步都应可构建、能解释并有必要检查；若未完成代码会在导入时启动任务或在初始化时修改数据，仅隐藏按钮不能隔离这些影响。

## 快速反馈需要分层和故障处理约定

集成检查应对应合并后的实际内容，避免只分别测试两个分支就推定合起来也正确。把成本较低且能阻断常见风险的检查放在较早阶段，成本较高的集成/端到端检查按风险安排，并明确失败后怎样阻断后续开放或恢复主干。后置检查不自动免除问题，只改变发现时间和处理责任。

反馈预算可描述为[排队](../../glossary/performance.md#performance.queueing)、准备、执行和理解结果的总时间。增加[并行](../../glossary/systems.md#systems.concurrency)度可能缓解执行耗时，也可能制造共享资源冲突；频繁[重试](flaky-tests-isolation-and-evidence.md#重试和临时隔离都要留下失败身份)则让反馈更晚且更难解释。预算数值需根据团队和服务实际测量，本篇没有给出通用的“几分钟以内”要求。[测试稳定性与隔离](flaky-tests-isolation-and-evidence.md)讨论这些信号质量问题。

## 开关在某个决策点选择行为

[功能开关](../../glossary/devops.md#devops.flags)让已部署代码按配置和上下文选择路径，分离代码到达环境与功能实际开放。开关的用途不同：[Pete Hodgson 的原文](https://martinfowler.com/articles/feature-toggles.html)区分发布、实验、运维和权限相关开关，也讨论生命周期与维护成本。短期发布开关应有清理条件；长期运维控制则需要持续验证，不应只因为上线完成就一律删除。

对纸面订单系统，决策应说明“使用哪个优惠实现”，调用者不必到处读取同一个配置键。一次业务操作若前后多次读取不同配置版本，可能一半走旧规则、一半走新规则；可以在合适的业务边界固定本次决策，并让下游理解该版本。固定多久取决于业务和紧急控制要求，不能以方便为由永久保留已经过期的配置。

[OpenFeature 的评价接口](https://openfeature.dev/specification/sections/flag-evaluation/)定义类型化返回值及异常时的默认值，但默认值是否符合业务安全需要由应用决定。“统一为 false”不一定恢复可用路径：旧代码可能已移除，或旧路径依赖的数据已经变化。还需知道提供方是否就绪、配置多久未更新及本次决策能否追溯；不要把所有读取异常都静默当成正常关闭。

[评价上下文](https://openfeature.dev/specification/sections/evaluation-context/)可携带标识目标主体的键，供提供方执行定向规则。逐步放量时应明确分配单位是用户、租户还是请求，并控制同一主体在所需范围内的一致性；相同百分比不自动保证同一群体，也不能单凭分桶就宣称形成了有效随机实验。日志和上下文只带必要标识，避免无关个人信息传播。

## 切回旧路径需要旧路径仍然成立

开关关闭能够改变后续路径选择，但不会自动撤销已经写入的数据、发送的消息或完成的外部动作。若新算法开始写旧版本无法理解的价格结构，关闭开关可能让旧读者失败。开放前需明确数据兼容窗口及状态转换，见[迁移与兼容](../database/schema-migrations-and-compatibility.md)。

| 纸面阶段 | 旧路径 | 新路径 | 需要保留的证据 |
| --- | --- | --- | --- |
| 代码合入、开关关闭 | 当前默认，仍可工作 | 有检查但尚未对用户开放 | 关闭时未意外执行新副作用 |
| 小范围开放 | 仍接收其余流量 | 对选定主体生效 | 路径、配置版本、业务结果与停止条件 |
| 全量开放、仍可切回 | 保持兼容及必要容量 | 默认选择 | 切回后读写与在途任务仍成立 |
| 清理旧路径 | 按约定退出 | 唯一实现 | 兼容窗口结束，依赖、配置和告警一并清理 |

这个表是一个可选择的教学方案，不表示所有变更都能无损切回。支付等外部副作用不能为了比较结果直接双执行；需为对照设计无副作用计算或安全的实验边界。

开关也不能代替服务端对象权限检查。隐藏界面后，用户仍可能直接调用接口；可见性条件与主体能否操作某笔订单须分别判断。[对象级访问控制](../security/object-level-authorization.md)负责该边界。谁能改配置、对谁生效、怎样审计和紧急停止，也属于变更治理。

## 组合验证与清理决定长期成本

三个独立二值开关在不加约束时有 2³＝8 种组合。这是纸面状态计数，不表示八种都合法，也不意味着跑完八次就验证了所有数据和版本。应先声明依赖关系和禁止组合，再覆盖默认、计划开放、重要交互、异常降级及仍承诺支持的历史状态；超出支持范围的配置应被明确拒绝。

为短期发布开关记录维护人、用途、默认行为、观测与停止条件、预期清理时间及删除前提。清理时同时考虑代码分支、测试矩阵、配置项、仪表盘和操作手册。长期控制则要周期复查默认值、权限和动作是否仍有效。开关越多，理解每次线上行为所需的上下文也越多。

自检：主干全绿能推出已部署版本可开放吗？不能，还需环境、配置和业务证据。关掉新优惠开关能撤销之前的扣款吗？不能。删除旧路径后还能依靠同一开关切回吗？不能，应重新定义恢复办法。

## 关联阅读与核查范围

- [契约测试与版本兼容](contract-testing-and-compatibility.md)：共享主干之外仍有新旧部署组合。
- [构建、部署与回滚](../devops/build-deploy-rollback.md)：制品、配置、数据和外部副作用的恢复边界。
- [事故响应与复盘](../reliability/incident-response-recovery-and-postmortems.md)：控制失败时的止损、证据和恢复验收。

截至 2026-10-22 核查 DORA、Hodgson 原文及 OpenFeature 在线规范。这里未指定或验证某家提供方的分桶、缓存和传播实现，也没有实际分流、A/B 实验、业务切换或测量集成效率。
