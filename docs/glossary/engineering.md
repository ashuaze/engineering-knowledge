<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件质量与研发词汇表

本页解释 17 组术语，按[完整术语索引](../glossary.md#engineering)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [软件质量与研发文章](../knowledge/engineering/index.md)

## 本页术语

- [Unit / Integration / E2E Test](#engineering.tests)
- [Contract Testing](#engineering.contracts)
- [Mock / Stub / Fake](#engineering.doubles)
- [TDD / BDD](#engineering.tdd)
- [Property-based / Fuzz Testing](#engineering.generative)
- [Regression Testing](#engineering.regression)
- [Test Pyramid](#engineering.pyramid)
- [Static Analysis / Lint](#engineering.analysis)
- [Code Review](#engineering.review)
- [Flaky Tests / Test Isolation](#engineering.flaky-tests)
- [Trunk-based Development](#engineering.trunk)
- [Semantic Versioning](#engineering.semver)
- [Dependency Management / SBOM](#engineering.supply-chain)
- [ADR / RFC / Design Doc](#engineering.design-docs)
- [Spec-Driven Development](#engineering.sdd)
- [Golden Path / Developer Experience](#engineering.dx)
- [Stateful Testing / Model-based Testing](#engineering.state-models)

<a id="engineering.tests"></a>

## Unit / Integration / E2E Test

**ID：** `engineering.tests` · **建议优先级：** P0

**别名 / 检索词：** Unit、Integration、E2E Test、单元测试、集成测试、端到端测试

**简释：** 按验证边界划分的测试。

单元测试聚焦较小行为边界，集成测试检查组件或真实依赖协作，端到端测试覆盖完整用户路径。边界比工具名称更重要，各层证据互补。

**例子：** 数据库事务回滚行为应由连接真实数据库的集成检查提供证据。

**深入阅读：** [测试层次与替身：一项测试究竟证明了什么](../knowledge/engineering/test-scopes-and-doubles.md)

<a id="engineering.contracts"></a>

## Contract Testing

**ID：** `engineering.contracts` · **建议优先级：** P0

**别名 / 检索词：** Contract Testing、Consumer-driven Contract Testing、Pact、消费者驱动契约、契约测试

**简释：** 验证交互契约的兼容性。

契约测试验证提供方与消费者对消息或接口的交互约定，消费者驱动契约从实际消费需求出发。它不自动证明部署、权限、性能或完整业务流程正确。

**例子：** 提供方改变字段类型时，契约检查可在上线前发现现有消费者不兼容。

**深入阅读：** [测试层次与替身：一项测试究竟证明了什么](../knowledge/engineering/test-scopes-and-doubles.md) · [契约测试与版本兼容：双方测试通过为什么仍接不上](../knowledge/engineering/contract-testing-and-compatibility.md)

<a id="engineering.doubles"></a>

## Mock / Stub / Fake

**ID：** `engineering.doubles` · **建议优先级：** P0

**别名 / 检索词：** Mock、Stub、Fake、测试替身

**简释：** 交互验证、固定行为和简化实现等测试替身。

Stub 提供预设响应，Mock 常用于验证预期交互，Fake 提供简化但可工作的实现。命名因工具而异，关键是说明替身与真实依赖的差异。

**例子：** 内存 Fake 无法替代真实数据库的锁、隔离和崩溃恢复验证。

**深入阅读：** [测试层次与替身：一项测试究竟证明了什么](../knowledge/engineering/test-scopes-and-doubles.md)

<a id="engineering.tdd"></a>

## TDD / BDD

**ID：** `engineering.tdd` · **建议优先级：** P0

**别名 / 检索词：** TDD、BDD、测试驱动开发、行为驱动开发

**简释：** 以测试或可讨论的行为规格推动开发。

TDD按行为场景列表逐项形成可运行检查、实现和重构反馈；BDD通过跨角色发现、表达及自动化澄清行为。先写测试或采用Given/When/Then语法，都不自动证明需求正确、真实依赖或并发行为已验证。

**例子：** 先明确超额购买应被拒绝及其业务结果，再实现库存扣减。

**深入阅读：** [TDD 与 BDD：测试写在前面，为什么仍可能做错需求](../knowledge/engineering/tdd-bdd-examples-and-feedback-loops.md)

<a id="engineering.generative"></a>

## Property-based / Fuzz Testing

**ID：** `engineering.generative` · **建议优先级：** P0

**别名 / 检索词：** Property-based、Fuzz Testing、Property-based Testing、PBT、Shrinking、Test Oracle、属性测试、反例收缩

**简释：** 自动生成输入验证性质或探测异常。

性质测试生成多种输入验证通用性质，失败缩减帮助找到小反例；模糊测试探索异常输入和执行路径。两者都依赖有效的判定依据与输入范围。

**例子：** 对编解码函数检验往返性质，同时对无效输入检查受控失败。

**深入阅读：** [属性测试与状态模型：样例通过为什么仍会漏掉边界](../knowledge/engineering/property-testing-and-state-models.md)

<a id="engineering.regression"></a>

## Regression Testing

**ID：** `engineering.regression` · **建议优先级：** P0

**别名 / 检索词：** Regression Testing、回归测试

**简释：** 验证原有行为未被意外破坏。

回归测试检查已有行为在变更后仍满足契约。有效检查应覆盖曾失败的行为及必要边界，避免只复述当前实现步骤。

**例子：** 修复重复扣款后，保留响应丢失与重试场景来防止问题再次出现。

**深入阅读：** [属性测试与状态模型：样例通过为什么仍会漏掉边界](../knowledge/engineering/property-testing-and-state-models.md)

<a id="engineering.pyramid"></a>

## Test Pyramid

**ID：** `engineering.pyramid` · **建议优先级：** P0

**别名 / 检索词：** Test Pyramid、测试金字塔

**简释：** 关于不同测试层次成本与数量的经验模型。

测试金字塔提示不同粒度的反馈与维护成本，数量比例不是统一规则。风险需对应真实边界；语句/分支覆盖不证明断言有效或要求完整，变异结果也受算子、等价变化和执行范围限制。

**例子：** 保留少量关键用户路径检查，并用更聚焦的检查覆盖细节与错误分支。

**深入阅读：** [测试金字塔与证据组合：覆盖率很高，为什么仍会漏掉关键失败](../knowledge/engineering/test-pyramids-risk-portfolios-and-coverage.md)

<a id="engineering.analysis"></a>

## Static Analysis / Lint

**ID：** `engineering.analysis` · **建议优先级：** P0

**别名 / 检索词：** Static Analysis、Lint、静态分析、代码检查、静态检查、告警基线

**简释：** 基于代码表示与规则推断性质，先核对分析完成与范围，再区分真实问题、误报、漏报及报告策略。

静态分析不靠逐次业务输入执行来观察目标行为，但提取代码可能涉及构建。Lint、类型与数据流模型各有范围；基线和抑制改变报告，不自动消除问题或证明安全。

**例子：** 空值分析可提前发现部分解引用风险，但外部数据仍需运行时校验。

**深入阅读：** [静态分析与告警：检查全绿，为什么仍可能有缺陷](../knowledge/engineering/static-analysis-rules-and-findings.md)

<a id="engineering.review"></a>

## Code Review

**ID：** `engineering.review` · **建议优先级：** P0

**别名 / 检索词：** Code Review、代码审查、代码评审、小步变更

**简释：** 结合意图、上下文与证据判断完整变更单元，明确意见级别、分工、最终版本及发布边界。

代码评审是有限范围内对正确性和维护性的判断。小而完整的变更便于理解，批准和检查需对应最终内容；评审通过不代替兼容、部署及业务验证。

**例子：** 审查重试改动时，重点核对幂等边界与失败后已执行的副作用。

**深入阅读：** [代码评审与小步变更：有人看过，为什么仍不能保证可发布](../knowledge/engineering/code-review-context-and-change-boundaries.md)

<a id="engineering.flaky-tests"></a>

## Flaky Tests / Test Isolation

**ID：** `engineering.flaky-tests` · **建议优先级：** P0

**别名 / 检索词：** Flaky Tests、Flaky Test、测试稳定性、不稳定测试、间歇失败测试

**简释：** 追查间歇失败的状态依赖，明确测试隔离与重试证据。

间歇失败可能来自未控制的输入、共享状态、产品竞态或环境故障。隔离需覆盖实际资源；重试通过并未解释首轮失败，临时移出阻断也需保留缺失覆盖和修复责任。

**例子：** A 修改默认时区后，B 只在 A 之后失败；固定执行顺序会隐藏依赖，显式时区与恢复现场才能针对原因修复。

**深入阅读：** [测试稳定性与隔离：单独通过，为什么组合运行却失败](../knowledge/engineering/flaky-tests-isolation-and-evidence.md)

<a id="engineering.trunk"></a>

## Trunk-based Development

**ID：** `engineering.trunk` · **建议优先级：** P0

**别名 / 检索词：** Trunk-based Development、主干开发

**简释：** 短生命周期分支和频繁集成。

主干开发把工作拆成小批并频繁集成到共同主干，需要及时、可解释的反馈。短分支与评审可以配合，尚未开放的路径可用功能开关控制；频繁合并不自动等于立即发布。

**例子：** 每天集成兼容的小步修改，而非数周后一次性合并大型分支。

**深入阅读：** [主干开发与功能开关：代码已合并，为什么功能还不能开放](../knowledge/engineering/trunk-based-development-and-feature-flags.md)

<a id="engineering.semver"></a>

## Semantic Versioning

**ID：** `engineering.semver` · **建议优先级：** P0

**别名 / 检索词：** Semantic Versioning、语义化版本

**简释：** 通过版本号表达兼容性意图。

语义化版本用 MAJOR.MINOR.PATCH 表达公共 API 的兼容性意图；正式规则对 0.x 和预发布另有约定。实际升级仍需阅读变更与验证使用路径。

**例子：** 1.x 中删除公共接口通常应提升主版本，新增兼容功能提升次版本。

**深入阅读：** [契约测试与版本兼容：双方测试通过为什么仍接不上](../knowledge/engineering/contract-testing-and-compatibility.md)

<a id="engineering.supply-chain"></a>

## Dependency Management / SBOM

**ID：** `engineering.supply-chain` · **建议优先级：** P0

**别名 / 检索词：** Dependency Management、SBOM、依赖管理、软件物料清单、依赖锁定、锁文件、传递依赖、Lockfile

**简释：** 区分依赖声明、解析锁定、安装与交付清单，核对组件身份、兼容性和来源证据。

依赖管理覆盖解析、来源、更新与维护。SBOM 描述声明范围内的组件及关系；锁文件、摘要、签名、来源证明和可复现对照各有可信前提，不能单独证明内容安全。

**例子：** 依赖升级后核对锁文件、来源和受影响行为，并更新组件清单。

**深入阅读：** [依赖锁定与 SBOM：版本固定了，为什么还不能证明交付可信](../knowledge/engineering/dependency-resolution-lockfiles-and-sbom.md)

<a id="engineering.design-docs"></a>

## ADR / RFC / Design Doc

**ID：** `engineering.design-docs` · **建议优先级：** P0

**别名 / 检索词：** ADR、RFC、Design Doc、设计文档、设计提案

**简释：** 决策记录、提案和设计说明。

设计文档解释目标、方案与取舍，工程RFC组织讨论，ADR保存决定理由和替代历史。批准/接受、实现和验证分别留证；当前有效约束与历史应相互链接，这里的RFC是工程提案用法，与IETF文档系列按上下文区分。

**例子：** 先以设计提案比较迁移方案，确定取舍后留下可追溯的决策记录。

**深入阅读：** [设计文档与决策记录：方案获批，为什么仍不等于已经交付](../knowledge/engineering/design-docs-rfcs-adrs-and-decision-lifecycles.md)

<a id="engineering.sdd"></a>

## Spec-Driven Development

**ID：** `engineering.sdd` · **建议优先级：** P0

**别名 / 检索词：** Spec-Driven Development、规格驱动开发

**简释：** 以可验证规格约束实现和验收。

规格驱动以可检查的行为约束实施和验收，具体工作流并无唯一标准。目标、规格、设计、实现与证据应可追溯；有链接不等于已满足，符合规格也需检查规格是否适合客户环境与目标。

**例子：** 规定超时后返回可查询操作 ID，并用失败场景检查实现是否满足该承诺。

**深入阅读：** [规格驱动与验收追溯：文档完整，为什么仍可能实现了错误目标](../knowledge/engineering/specifications-contracts-traceability-and-acceptance.md)

<a id="engineering.dx"></a>

## Golden Path / Developer Experience

**ID：** `engineering.dx` · **建议优先级：** P0

**别名 / 检索词：** Golden Path、Developer Experience、黄金路径、开发者体验

**简释：** 标准交付路径和研发使用体验。

黄金路径为常见任务提供受支持的默认路径，包含创建、交付、运行、升级和退出。模板变更不自动修补旧服务；开发体验需结合任务等待、返工与使用者反馈，不以提交数或采用率直接评价个人生产率。

**例子：** 新服务模板内置健康检查和观测配置，减少团队反复搭建基础能力。

**深入阅读：** [黄金路径与开发者体验：模板生成成功，为什么交付仍然困难](../knowledge/engineering/golden-paths-developer-experience-and-platform-feedback.md)

<a id="engineering.state-models"></a>

## Stateful Testing / Model-based Testing

**ID：** `engineering.state-models` · **建议优先级：** P1

**别名 / 检索词：** Stateful Testing、Model-based Testing、State Model、状态模型、状态机测试

**简释：** 以简化模型驱动命令序列并检查状态关系，证据受模型、调度与真实依赖范围限制；顺序模型不自动证明并发正确性。

状态模型测试生成操作序列，用简化模型核对系统状态和返回结果。模型的假设、外部依赖和调度限制证据范围；顺序操作通过不证明所有并发交错正确。

**例子：** 生成开户、存款、取款序列，并逐步核对余额与拒绝规则。

**深入阅读：** [属性测试与状态模型：样例通过为什么仍会漏掉边界](../knowledge/engineering/property-testing-and-state-models.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Hypothesis：性质与状态模型测试](https://hypothesis.readthedocs.io/en/latest/)
- [Semantic Versioning 2.0.0：兼容性与版本](https://semver.org/)
- [Google：代码评审标准](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [ESLint：规则与核心概念](https://eslint.org/docs/latest/use/core-concepts/)
- [npm 11：锁文件](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json/)
- [CycloneDX：SBOM](https://cyclonedx.org/capabilities/sbom/)
- [pytest：间歇失败与状态隔离](https://docs.pytest.org/en/stable/explanation/flaky.html)
- [DORA：主干开发](https://dora.dev/capabilities/trunk-based-development/)
- [Kent Beck 的 Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd)
- [Cucumber 的 BDD 说明](https://cucumber.io/docs/bdd/)
- [Example Mapping](https://cucumber.io/docs/bdd/example-mapping/)
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Coverage.py 7.11.0](https://coverage.readthedocs.io/en/7.11.0/branch.html)
- [PIT 的机制说明](https://pitest.org/)
- [Malte Ubl 的 Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Rust RFC 流程](https://rust-lang.github.io/rfcs/)
- [Nygard 的 ADR 方法](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [NASA 的需求管理说明](https://www.nasa.gov/reference/6-2-requirements-management/)
- [NASA SWE-055](https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695440/SWE-055%2B-%2BRequirements%2BValidation)
- [Cucumber 的可执行规格说明](https://cucumber.io/docs/)
- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [Backstage Software Templates](https://backstage.io/docs/features/software-templates/)
- [GitHub 的 DevEx 研究报告](https://github.blog/news-insights/research/good-devex-increases-productivity/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
