<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件质量与研发

建议优先级：P0。目标：用规格、验证和协作方法减少变更风险。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

实现符合自己的理解，却不满足需求，如何提前发现？

## 已有正文

- [代码评审与小步变更：有人看过，为什么仍不能保证可发布](code-review-context-and-change-boundaries.md)：解释评审上下文、完整变更单元与风险分工，区分必须修复、建议、最终版本证据和发布兼容责任。
- [契约测试与版本兼容：双方测试通过为什么仍接不上](contract-testing-and-compatibility.md)：区分接口描述、消费者期望和提供方验证，解释版本矩阵、匹配规则、失败交互及契约证据的适用边界。
- [依赖锁定与 SBOM：版本固定了，为什么还不能证明交付可信](dependency-resolution-lockfiles-and-sbom.md)：区分版本约束、解析锁定、安装与交付清单，说明[传递依赖](../../glossary/engineering.md#engineering.supply-chain)、SemVer、摘要、SBOM、来源证明及更新证据的范围。
- [设计文档与决策记录：方案获批，为什么仍不等于已经交付](design-docs-rfcs-adrs-and-decision-lifecycles.md)：区分设计说明、征求意见与决定历史，用证据和变更关系连接需求、取舍、实现、发布及实际结果。
- [测试稳定性与隔离：单独通过，为什么组合运行却失败](flaky-tests-isolation-and-evidence.md)：从共享状态、执行顺序、时间与并发解释间歇失败，区分隔离层次、重试结果、临时隔离与可复查的修复证据。
- [黄金路径与开发者体验：模板生成成功，为什么交付仍然困难](golden-paths-developer-experience-and-platform-feedback.md)：将受支持的默认路径作为持续维护的产品，区分生成、部署、运行和升级，并用任务反馈与上下文评价开发体验。
- [属性测试与状态模型：样例通过为什么仍会漏掉边界](property-testing-and-state-models.md)：区分固定样例、生成输入、性质与测试判断依据，解释收缩、状态机命令和回归反例，以及顺序模型的证据边界。
- [规格驱动与验收追溯：文档完整，为什么仍可能实现了错误目标](specifications-contracts-traceability-and-acceptance.md)：把需求目的、可检查的行为、设计决定及验证结果连接起来，说明例子、契约、假设与变更的不同职责。
- [静态分析与告警：检查全绿，为什么仍可能有缺陷](static-analysis-rules-and-findings.md)：区分 [Lint](../../glossary/engineering.md#engineering.analysis)、类型检查与数据流分析，解释分析范围、规则模型、误报漏报、基线和告警处置的证据边界。
- [TDD 与 BDD：测试写在前面，为什么仍可能做错需求](tdd-bdd-examples-and-feedback-loops.md)：区分小步测试反馈与跨角色行为发现，用库存预留示例说明失败原因、业务结果、替身和[重构](../../glossary/architecture.md#architecture.debt)边界。
- [测试金字塔与证据组合：覆盖率很高，为什么仍会漏掉关键失败](test-pyramids-risk-portfolios-and-coverage.md)：按风险、真实边界和反馈成本组合测试，区分语句/分支覆盖、有效断言、变异测试及未覆盖的产品要求。
- [测试层次与替身：一项测试究竟证明了什么](test-scopes-and-doubles.md)：按真实依赖与系统边界区分单元、集成和[端到端测试](../../glossary/engineering.md#engineering.tests)，避免把替身行为当成生产保证。
- [主干开发与功能开关：代码已合并，为什么功能还不能开放](trunk-based-development-and-feature-flags.md)：连接小批集成、反馈预算与[功能开关](../../glossary/devops.md#devops.flags)，解释部署和开放的区别、配置失败、数据兼容、组合验证及开关清理责任。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Unit / Integration / E2E Test](../../glossary/engineering.md#engineering.tests) | 按验证边界划分的测试。 |
| [Contract Testing](../../glossary/engineering.md#engineering.contracts) | 验证交互契约的兼容性。 |
| [Mock / Stub / Fake](../../glossary/engineering.md#engineering.doubles) | 交互验证、固定行为和简化实现等测试替身。 |
| [TDD / BDD](../../glossary/engineering.md#engineering.tdd) | 以测试或可讨论的行为规格推动开发。 |
| [Property-based / Fuzz Testing](../../glossary/engineering.md#engineering.generative) | 自动生成输入验证性质或探测异常。 |
| [Regression Testing](../../glossary/engineering.md#engineering.regression) | 验证原有行为未被意外破坏。 |
| [Test Pyramid](../../glossary/engineering.md#engineering.pyramid) | 关于不同测试层次成本与数量的经验模型。 |
| [Static Analysis / Lint](../../glossary/engineering.md#engineering.analysis) | 基于代码表示与规则推断性质，先核对分析完成与范围，再区分真实问题、误报、漏报及报告策略。 |
| [Code Review](../../glossary/engineering.md#engineering.review) | 结合意图、上下文与证据判断完整变更单元，明确意见级别、分工、最终版本及发布边界。 |
| [Flaky Tests / Test Isolation](../../glossary/engineering.md#engineering.flaky-tests) | 追查间歇失败的状态依赖，明确测试隔离与重试证据。 |
| [Trunk-based Development](../../glossary/engineering.md#engineering.trunk) | 短生命周期分支和频繁集成。 |
| [Semantic Versioning](../../glossary/engineering.md#engineering.semver) | 通过版本号表达兼容性意图。 |
| [Dependency Management / SBOM](../../glossary/engineering.md#engineering.supply-chain) | 区分依赖声明、解析锁定、安装与交付清单，核对组件身份、兼容性和来源证据。 |
| [ADR / RFC / Design Doc](../../glossary/engineering.md#engineering.design-docs) | 决策记录、提案和设计说明。 |
| [Spec-Driven Development](../../glossary/engineering.md#engineering.sdd) | 以可验证规格约束实现和验收。 |
| [Golden Path / Developer Experience](../../glossary/engineering.md#engineering.dx) | 标准交付路径和研发使用体验。 |
| [Stateful Testing / Model-based Testing](../../glossary/engineering.md#engineering.state-models) | 以简化模型驱动命令序列并检查状态关系，证据受模型、调度与真实依赖范围限制；顺序模型不自动证明并发正确性。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
