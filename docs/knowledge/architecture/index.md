<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件架构与设计

建议优先级：P0。目标：定义模块边界并记录复杂度和演进取舍。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

何时[模块化单体](../../glossary/architecture.md#architecture.modular-monolith)已不足以解决组织和扩展问题？

## 已有正文

- [CQRS：读写模型分开以后，怎样处理投影延迟与重建](cqrs-read-write-models-and-projection-lag.md)：解释命令与查询模型的职责分离、同库与分库存储、投影进度、读己之写和可切换重建边界。
- [设计模式与协作契约：结构相似为什么行为仍可能不同](design-patterns-collaboration-and-semantic-boundaries.md)：用策略、适配器、装饰器与观察者区分变化意图，解释行为翻译、组合顺序、订阅寿命和模式的适用成本。
- [设计原则与抽象成本：SOLID、DRY 和 YAGNI 怎样一起使用](design-principles-contracts-and-abstraction-costs.md)：用变化来源、行为契约和知识所有权解释 [SOLID](../../glossary/architecture.md#architecture.principles)、KISS、DRY、YAGNI，说明拆分、复用与过度抽象的取舍。
- [领域模型、聚合与业务不变量：规则究竟由谁守住](domain-models-aggregates-and-invariants.md)：区分[实体](../../glossary/architecture.md#architecture.domain-model)身份、值语义、聚合一致性边界与[限界上下文](../../glossary/architecture.md#architecture.ddd)，解释数据所有权、并发写入及跨边界流程的验证责任。
- [事件溯源：事件流怎样成为事实，快照与投影怎样安全重建](event-sourcing-streams-snapshots-and-projections.md)：解释权威事件流、预期版本追加、状态重建、快照、投影和历史演进，并区分事件存储、[Broker](../../glossary/messaging.md#messaging.roles)、[Outbox](../../glossary/messaging.md#messaging.outbox) 与审计日志。
- [ADR-0001：用 Markdown 单一内容源组织工程知识](knowledge-base-adr.md)：记录这套知识库选择、备选方案、代价和重评条件。
- [模块化单体与微服务：代码边界为什么不等于部署边界](modular-monoliths-microservices-and-service-boundaries.md)：区分业务模型、代码、数据与部署边界，解释模块化单体与独立服务的收益、部分失败及演进成本。
- [模块边界与依赖：为什么改一个功能会牵动多个模块](module-boundaries-and-dependencies.md)：用[内聚](../../glossary/architecture.md#architecture.coupling)、耦合与[信息隐藏](../../glossary/architecture.md#architecture.information-hiding)分析变更影响，区分源码依赖、运行调用和部署边界。
- [质量属性与架构决策：怎样把取舍变成可验证的约束](quality-attribute-scenarios-tradeoffs-and-adrs.md)：把性能、可用性与可修改性写成[质量属性场景](../../glossary/architecture.md#architecture.quality-scenario)，区分敏感点、权衡、风险、证据与 [ADR](../../glossary/architecture.md#architecture.adr) 的决定状态。
- [渐进替换与写入归属：流量切回为什么不等于数据回退](strangler-fig-migration-write-authority-and-rollback.md)：区分路由切换、模型翻译、历史追平和写入权移交，说明[绞杀者模式](../../glossary/architecture.md#architecture.strangler)、双写窗口、影子比较与回退条件。
- [技术债与重构：结构变好了，为什么还要核对行为](technical-debt-refactoring-and-behavior.md)：区分[技术债](../../glossary/architecture.md#architecture.debt)、缺陷修复和保持行为的重构，解释特征测试、小步替换、迁移成本与维护优先级。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [SOLID / KISS / DRY / YAGNI](../../glossary/architecture.md#architecture.principles) | 设计原则和复杂度约束，须结合上下文使用。 |
| [Cohesion / Coupling](../../glossary/architecture.md#architecture.coupling) | 职责聚合程度与组件间依赖。 |
| [Separation of Concerns](../../glossary/architecture.md#architecture.concerns) | 按职责隔离不同变化来源。 |
| [Layered Architecture](../../glossary/architecture.md#architecture.layering) | 职责分层和依赖方向。 |
| [Modular Monolith](../../glossary/architecture.md#architecture.modular-monolith) | 在同一部署单元内保持模块边界。 |
| [Microservices](../../glossary/architecture.md#architecture.microservices) | 独立演进和部署的服务及其协调成本。 |
| [DDD / Bounded Context](../../glossary/architecture.md#architecture.ddd) | 领域建模与模型适用范围。 |
| [Entity / Value Object / Aggregate](../../glossary/architecture.md#architecture.domain-model) | 标识、值语义与一致性边界。 |
| [Clean / Hexagonal Architecture](../../glossary/architecture.md#architecture.ports-adapters) | 通过依赖方向和端口隔离核心业务。 |
| [Dependency Injection / IoC](../../glossary/architecture.md#architecture.di) | 外部提供依赖与控制关系反转。 |
| [CQRS](../../glossary/architecture.md#architecture.cqrs) | 分离修改状态与读取状态的模型。 |
| [Event Sourcing](../../glossary/architecture.md#architecture.event-sourcing) | 以事件序列记录状态演进。 |
| [Design Pattern / Anti-pattern](../../glossary/architecture.md#architecture.patterns) | 可复用设计经验及常见不良结构。 |
| [ADR](../../glossary/architecture.md#architecture.adr) | 记录特定上下文中的决策、备选方案及后果。 |
| [Technical Debt / Refactoring](../../glossary/architecture.md#architecture.debt) | 用后续变更的额外成本讨论技术债，通过保持约定行为的结构调整改善维护；现状记录不自动等于正确规格。 |
| [Strangler Fig Pattern](../../glossary/architecture.md#architecture.strangler) | 渐进替换旧系统的迁移方法。 |
| [Information Hiding](../../glossary/architecture.md#architecture.information-hiding) | 把容易变化的设计决定封装在模块内部，以必要接口限制知识传播与变更影响。 |
| [Dependency Inversion Principle / DIP](../../glossary/architecture.md#architecture.dependency-inversion) | 围绕核心约定组织源码依赖，使具体适配实现依赖该约定；与运行调用方向及依赖注入分别分析。 |
| [Quality Attribute Scenario](../../glossary/architecture.md#architecture.quality-scenario) | 用刺激源、刺激、环境、受影响对象、响应及度量限定架构目标。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
