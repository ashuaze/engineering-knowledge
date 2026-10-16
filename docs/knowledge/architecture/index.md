<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件架构与设计

建议优先级：P0。目标：定义模块边界并记录复杂度和演进取舍。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

何时模块化单体已不足以解决组织和扩展问题？

## 已有正文

- [ADR-0001：用 Markdown 单一内容源组织工程知识](knowledge-base-adr.md)：记录这套知识库选择、备选方案、代价和重评条件。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| SOLID / KISS / DRY / YAGNI | 设计原则和复杂度约束，须结合上下文使用。 |
| Cohesion / Coupling | 职责聚合程度与组件间依赖。 |
| Separation of Concerns | 按职责隔离不同变化来源。 |
| Layered Architecture | 职责分层和依赖方向。 |
| Modular Monolith | 在同一部署单元内保持模块边界。 |
| Microservices | 独立演进和部署的服务及其协调成本。 |
| DDD / Bounded Context | 领域建模与模型适用范围。 |
| Entity / Value Object / Aggregate | 标识、值语义与一致性边界。 |
| Clean / Hexagonal Architecture | 通过依赖方向和端口隔离核心业务。 |
| Dependency Injection / IoC | 外部提供依赖与控制关系反转。 |
| CQRS | 分离修改状态与读取状态的模型。 |
| Event Sourcing | 以事件序列记录状态演进。 |
| Design Pattern / Anti-pattern | 可复用设计经验及常见不良结构。 |
| ADR | 记录特定上下文中的决策、备选方案及后果。 |
| Technical Debt / Refactoring | 演进成本与保持行为的结构调整。 |
| Strangler Fig Pattern | 渐进替换旧系统的迁移方法。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
