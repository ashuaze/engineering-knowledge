<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件架构与设计词汇表

本页解释 19 组术语，按[完整术语索引](../glossary.md#architecture)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [软件架构与设计文章](../knowledge/architecture/index.md)

## 本页术语

- [SOLID / KISS / DRY / YAGNI](#architecture.principles)
- [Cohesion / Coupling](#architecture.coupling)
- [Separation of Concerns](#architecture.concerns)
- [Layered Architecture](#architecture.layering)
- [Modular Monolith](#architecture.modular-monolith)
- [Microservices](#architecture.microservices)
- [DDD / Bounded Context](#architecture.ddd)
- [Entity / Value Object / Aggregate](#architecture.domain-model)
- [Clean / Hexagonal Architecture](#architecture.ports-adapters)
- [Dependency Injection / IoC](#architecture.di)
- [CQRS](#architecture.cqrs)
- [Event Sourcing](#architecture.event-sourcing)
- [Design Pattern / Anti-pattern](#architecture.patterns)
- [ADR](#architecture.adr)
- [Technical Debt / Refactoring](#architecture.debt)
- [Strangler Fig Pattern](#architecture.strangler)
- [Information Hiding](#architecture.information-hiding)
- [Dependency Inversion Principle / DIP](#architecture.dependency-inversion)
- [Quality Attribute Scenario](#architecture.quality-scenario)

<a id="architecture.principles"></a>

## SOLID / KISS / DRY / YAGNI

**ID：** `architecture.principles` · **建议优先级：** P0

**别名 / 检索词：** SOLID、KISS、DRY、YAGNI、设计原则

**简释：** 设计原则和复杂度约束，须结合上下文使用。

SOLID分别讨论职责、扩展、行为替换、接口与源码依赖；KISS、DRY、YAGNI帮助约束复杂度与不必要能力。是否同一知识、契约是否稳定及抽象的现实收益，比类数或重复行数更重要。

**例子：** 两个暂时相似但变化原因不同的流程，可以先保留独立实现。

**深入阅读：** [设计原则与抽象成本：SOLID、DRY 和 YAGNI 怎样一起使用](../knowledge/architecture/design-principles-contracts-and-abstraction-costs.md)

<a id="architecture.coupling"></a>

## Cohesion / Coupling

**ID：** `architecture.coupling` · **建议优先级：** P0

**别名 / 检索词：** Cohesion、Coupling、内聚、耦合

**简释：** 职责聚合程度与组件间依赖。

内聚关注一个模块中的职责是否围绕共同目的，耦合关注模块间需要知道多少彼此细节。边界质量应按变更传播和不变量所有权评估，不能只数类和接口。

**例子：** 支付提供商更换时，只修改支付适配模块，比修改多个业务模块更易维护。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md) · [模块化单体与微服务：代码边界为什么不等于部署边界](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)

<a id="architecture.concerns"></a>

## Separation of Concerns

**ID：** `architecture.concerns` · **建议优先级：** P0

**别名 / 检索词：** Separation of Concerns、关注点分离

**简释：** 按职责隔离不同变化来源。

关注点分离按不同变化来源组织代码，使领域规则、存储、传输和展示可以分别推理。边界仍需清晰协作契约，物理拆目录本身不建立隔离。

**例子：** 把运费规则与 HTTP 参数解析分开，能独立讨论业务与输入协议。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.layering"></a>

## Layered Architecture

**ID：** `architecture.layering` · **建议优先级：** P0

**别名 / 检索词：** Layered Architecture、分层架构

**简释：** 职责分层和依赖方向。

分层把职责放入不同抽象层，并约束依赖方向。运行时调用路径不等于源码依赖方向；跨层捷径和共享数据库仍可能破坏边界。

**例子：** 应用层调用仓储接口，数据库适配层实现该接口并处理存储细节。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.modular-monolith"></a>

## Modular Monolith

**ID：** `architecture.modular-monolith` · **建议优先级：** P0

**别名 / 检索词：** Modular Monolith、模块化单体

**简释：** 在同一部署单元内保持模块边界。

模块化单体在同一部署单元中保持清楚的业务模块及接口。可减少分布式协调成本，但需通过代码与数据访问规则防止模块直接侵入彼此内部。

**例子：** 订单和库存同进程部署，各自拥有规则并通过约定接口协作。

**深入阅读：** [模块化单体与微服务：代码边界为什么不等于部署边界](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)

<a id="architecture.microservices"></a>

## Microservices

**ID：** `architecture.microservices` · **建议优先级：** P0

**别名 / 检索词：** Microservices、微服务

**简释：** 独立演进和部署的服务及其协调成本。

微服务把部分业务能力放入可独立部署的服务，并承担网络调用、状态一致性和运行治理成本。拆分价值应来自独立演进需求，而非只追求服务数量。

**例子：** 高峰扩容支付服务时无需重新发布商品服务，但跨服务流程需处理部分失败。

**深入阅读：** [模块化单体与微服务：代码边界为什么不等于部署边界](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)

<a id="architecture.ddd"></a>

## DDD / Bounded Context

**ID：** `architecture.ddd` · **建议优先级：** P0

**别名 / 检索词：** DDD、Bounded Context、领域驱动设计、限界上下文

**简释：** 领域建模与模型适用范围。

DDD 围绕业务语言建立模型；限界上下文划定术语和规则成立的范围。相同名称跨上下文可以有不同含义，集成时需要明确翻译与契约。

**例子：** 销售中的客户与风控中的客户具有不同属性和规则，不必共享同一模型类。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md) · [领域模型、聚合与业务不变量：规则究竟由谁守住](../knowledge/architecture/domain-models-aggregates-and-invariants.md) · [模块化单体与微服务：代码边界为什么不等于部署边界](../knowledge/architecture/modular-monoliths-microservices-and-service-boundaries.md)

<a id="architecture.domain-model"></a>

## Entity / Value Object / Aggregate

**ID：** `architecture.domain-model` · **建议优先级：** P0

**别名 / 检索词：** Entity、Value Object、Aggregate、Aggregate Root、聚合、业务不变量、数据所有权、实体、值对象、聚合根

**简释：** 标识、值语义与一致性边界。

实体按身份保持连续性，值对象按值表达语义，聚合以根对象维护一组一致性规则。聚合边界不是对象关系图大小，而是需要一起保护的不变量范围。

**例子：** 订单聚合维护订单项与总价规则，外部通过订单根执行修改。

**深入阅读：** [领域模型、聚合与业务不变量：规则究竟由谁守住](../knowledge/architecture/domain-models-aggregates-and-invariants.md)

<a id="architecture.ports-adapters"></a>

## Clean / Hexagonal Architecture

**ID：** `architecture.ports-adapters` · **建议优先级：** P0

**别名 / 检索词：** Clean、Hexagonal Architecture、六边形架构、整洁架构

**简释：** 通过依赖方向和端口隔离核心业务。

端口表达核心需要或提供的能力，适配器连接数据库、网络等外部机制。依赖朝核心约定组织，使业务不必理解具体框架；抽象仍应服务实际变化点。

**例子：** 同一个库存端口可由真实数据库适配器和测试替身分别实现。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.di"></a>

## Dependency Injection / IoC

**ID：** `architecture.di` · **建议优先级：** P0

**别名 / 检索词：** Dependency Injection、IoC、依赖注入、控制反转

**简释：** 外部提供依赖与控制关系反转。

依赖注入由外部组装并传入依赖，是控制反转的一种方式。它改变对象获取依赖的方式；是否依赖抽象仍需从接口归属和源码依赖判断。

**例子：** 构造服务时传入时钟接口，测试可提供固定时间而无需修改全局时钟。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.cqrs"></a>

## CQRS

**ID：** `architecture.cqrs` · **建议优先级：** P0

**别名 / 检索词：** CQRS、命令查询职责分离

**简释：** 分离修改状态与读取状态的模型。

CQRS 为修改状态与读取状态采用不同模型或接口，不强制使用不同数据库或事件溯源。读模型异步更新时需要处理延迟与重建。

**例子：** 提交订单使用业务命令，订单列表由面向查询的投影提供。

**深入阅读：** [CQRS：读写模型分开以后，怎样处理投影延迟与重建](../knowledge/architecture/cqrs-read-write-models-and-projection-lag.md)

<a id="architecture.event-sourcing"></a>

## Event Sourcing

**ID：** `architecture.event-sourcing` · **建议优先级：** P0

**别名 / 检索词：** Event Sourcing、事件溯源

**简释：** 以事件序列记录状态演进。

事件溯源以事件序列作为状态演进的记录，通过回放或投影得到状态。事件版本、顺序、幂等投影和历史数据修订都需设计。

**例子：** 账户余额由入账和出账事件累计得到，重建时不能再次触发真实付款。

**深入阅读：** [事件溯源：事件流怎样成为事实，快照与投影怎样安全重建](../knowledge/architecture/event-sourcing-streams-snapshots-and-projections.md)

<a id="architecture.patterns"></a>

## Design Pattern / Anti-pattern

**ID：** `architecture.patterns` · **建议优先级：** P0

**别名 / 检索词：** Design Pattern、Anti-pattern、设计模式、反模式

**简释：** 可复用设计经验及常见不良结构。

模式按问题和约束描述协作意图；本批分别解释策略、适配器、装饰器和观察者，不穷举目录。语义翻译、组合顺序、错误和资源寿命仍需约定；有模式名不自动获得持久性、事务或性能保证。

**例子：** 纸面折扣D(x)=floor(0.9x)、费用F(x)=x+100；输入1000时F(D(x))=1000，D(F(x))=990，包装顺序会改变结果。

**深入阅读：** [设计模式与协作契约：结构相似为什么行为仍可能不同](../knowledge/architecture/design-patterns-collaboration-and-semantic-boundaries.md)

<a id="architecture.adr"></a>

## ADR

**ID：** `architecture.adr` · **建议优先级：** P0

**别名 / 检索词：** ADR、架构决策记录

**简释：** 记录特定上下文中的决策、备选方案及后果。

ADR保存特定上下文中的重要决定、备选、理由、状态与正负后果；后续记录替代旧决定时保留历史和重评条件。accepted表示决定被接受，不等于实现已经完成或质量目标已验证。

**例子：** 记录为何选单数据库事务，以及跨地域写入需求出现时的重评条件。

**深入阅读：** [质量属性与架构决策：怎样把取舍变成可验证的约束](../knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md) · [ADR-0001：用 Markdown 单一内容源组织工程知识](../knowledge/architecture/knowledge-base-adr.md)

<a id="architecture.debt"></a>

## Technical Debt / Refactoring

**ID：** `architecture.debt` · **建议优先级：** P0

**别名 / 检索词：** Technical Debt、Refactoring、技术债、重构、技术负债、特征测试、Characterization Test

**简释：** 用后续变更的额外成本讨论技术债，通过保持约定行为的结构调整改善维护；现状记录不自动等于正确规格。

技术债是设计取舍与后续演进成本的比喻，也可能随新知识显现。重构调整内部结构而保持约定的可观察行为；有意修复缺陷需另列验收，特征测试只记录选定范围的当前行为。

**例子：** 先补关键回归检查，再拆分职责混杂的模块以降低下次修改成本。

**深入阅读：** [技术债与重构：结构变好了，为什么还要核对行为](../knowledge/architecture/technical-debt-refactoring-and-behavior.md)

<a id="architecture.strangler"></a>

## Strangler Fig Pattern

**ID：** `architecture.strangler` · **建议优先级：** P0

**别名 / 检索词：** Strangler Fig Pattern、绞杀者模式

**简释：** 渐进替换旧系统的迁移方法。

渐进替换逐步转移业务能力，同时管理入口、模型翻译、数据连续性与权威写入。新数据接受写入后，旧系统若未追平或不兼容，单纯切回路由不能安全回退；终点也不必是微服务。

**例子：** 先把只读商品查询切到新服务，确认结果与容量后再迁移写路径。

**深入阅读：** [渐进替换与写入归属：流量切回为什么不等于数据回退](../knowledge/architecture/strangler-fig-migration-write-authority-and-rollback.md)

<a id="architecture.information-hiding"></a>

## Information Hiding

**ID：** `architecture.information-hiding` · **建议优先级：** P1

**别名 / 检索词：** Information Hiding、信息隐藏

**简释：** 把容易变化的设计决定封装在模块内部，以必要接口限制知识传播与变更影响。

信息隐藏把容易变化的实现决定收在模块内部，只公开必要承诺。封装字段并不充分；若调用方仍依赖存储结构和时序，变化仍会扩散。

**例子：** 仓储接口返回领域结果，而非让业务层操作数据库游标与表结构。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.dependency-inversion"></a>

## Dependency Inversion Principle / DIP

**ID：** `architecture.dependency-inversion` · **建议优先级：** P1

**别名 / 检索词：** Dependency Inversion Principle、DIP、依赖反转

**简释：** 围绕核心约定组织源码依赖，使具体适配实现依赖该约定；与运行调用方向及依赖注入分别分析。

依赖反转让高层规则和底层机制依赖核心抽象，具体实现适配核心约定。接口放在哪里、由谁定义，比是否用了依赖注入容器更关键。

**例子：** 订单业务定义支付能力接口，第三方支付 SDK 适配器依赖并实现它。

**深入阅读：** [模块边界与依赖：为什么改一个功能会牵动多个模块](../knowledge/architecture/module-boundaries-and-dependencies.md)

<a id="architecture.quality-scenario"></a>

## Quality Attribute Scenario

**ID：** `architecture.quality-scenario` · **建议优先级：** P1

**别名 / 检索词：** 质量属性场景、质量属性

**简释：** 用刺激源、刺激、环境、受影响对象、响应及度量限定架构目标。

把高性能、可用或易修改等目标连接到具体负载、变化和观察口径，才能比较取舍与组织验证。敏感点和风险分析提示需进一步检查的假设，不替代真实证据；单次预算与分布统计分开判断。

**例子：** 同一次串行请求四段30/80/60/40ms共210ms，但四个组件各自的p95不能直接相加当作端到端p95。

**深入阅读：** [质量属性与架构决策：怎样把取舍变成可验证的约束](../knowledge/architecture/quality-attribute-scenarios-tradeoffs-and-adrs.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Martin Fowler：架构与设计资料](https://martinfowler.com/architecture/)
- [Fowler：重构定义与方法](https://refactoring.com/)
- [Fowler：技术债象限](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Lewis/Fowler：微服务风格](https://martinfowler.com/articles/microservices.html)
- [Robert C. Martin：SOLID Relevance](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html)
- [Liskov/Wing：行为子类型原论文](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [GoF原书：Adapter节选](https://www.informit.com/articles/article.aspx?p=1398600)
- [Fowler：Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [CMU：软件架构与质量场景](https://www.cs.cmu.edu/~schmerl/courses/15-413/02-software-architecture.pdf)
- [SEI：ATAM原报告](https://sei.cmu.edu/documents/629/2000_005_001_13706.pdf)
- [Nygard：Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
