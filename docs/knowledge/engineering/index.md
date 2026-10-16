<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 软件质量与研发

建议优先级：P0。目标：用规格、验证和协作方法减少变更风险。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

实现符合自己的理解，却不满足需求，如何提前发现？

## 已有正文

- [测试层次与替身：一项测试究竟证明了什么](test-scopes-and-doubles.md)：按真实依赖与系统边界区分单元、集成和端到端测试，避免把替身行为当成生产保证。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Unit / Integration / E2E Test | 按验证边界划分的测试。 |
| Contract Testing | 验证交互契约的兼容性。 |
| Mock / Stub / Fake | 交互验证、固定行为和简化实现等测试替身。 |
| TDD / BDD | 以测试或可讨论的行为规格推动开发。 |
| Property-based / Fuzz Testing | 自动生成输入验证性质或探测异常。 |
| Regression Testing | 验证原有行为未被意外破坏。 |
| Test Pyramid | 关于不同测试层次成本与数量的经验模型。 |
| Static Analysis / Lint | 静态推断缺陷与检查约定。 |
| Code Review | 共同检查变更并传播上下文。 |
| Trunk-based Development | 短生命周期分支和频繁集成。 |
| Semantic Versioning | 通过版本号表达兼容性意图。 |
| Dependency Management / SBOM | 依赖解析、维护与组件清单。 |
| ADR / RFC / Design Doc | 决策记录、提案和设计说明。 |
| Spec-Driven Development | 以可验证规格约束实现和验收。 |
| Golden Path / Developer Experience | 标准交付路径和研发使用体验。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
