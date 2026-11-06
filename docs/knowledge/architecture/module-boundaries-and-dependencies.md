---
id: "kb-architecture-module-boundaries"
title: "模块边界与依赖：为什么改一个功能会牵动多个模块"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "用内聚、耦合与信息隐藏分析变更影响，区分源码依赖、运行调用和部署边界。"
created: "2026-10-16"
updated: "2026-10-26"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-engineering-test-scopes", "kb-messaging-outbox", "kb-architecture-knowledge-adr", "kb-architecture-aggregates-invariants", "kb-engineering-contract-compatibility", "kb-runtime-modules-cycles", "kb-frontend-bundling-splitting", "kb-algorithms-graphs", "kb-architecture-refactoring-debt", "kb-architecture-deployment-boundaries", "kb-architecture-design-principles", "kb-architecture-patterns-collaboration", "kb-architecture-strangler-migration", "kb-architecture-quality-decisions"]
tags: ["modularity", "coupling", "dependencies"]
---

# 模块边界与依赖：为什么改一个功能会牵动多个模块

学习入口：只改优惠规则，却要同时修改接口、数据库适配和通知代码，模块究竟按什么划分？前置知识：函数、接口和基本业务流程。本文讨论职责与依赖设计，示例是教学方案，没有实现或测量[重构](../../glossary/architecture.md#architecture.debt)收益。

部署边界见[模块化单体与微服务](modular-monoliths-microservices-and-service-boundaries.md)；抽象选择见[设计原则](design-principles-contracts-and-abstraction-costs.md)和[协作模式](design-patterns-collaboration-and-semantic-boundaries.md)，旧系统演进见[渐进替换](strangler-fig-migration-write-authority-and-rollback.md)，目标与证据见[质量属性与决策](quality-attribute-scenarios-tradeoffs-and-adrs.md)。

## 用变更解释内聚与耦合

模块是一组对外提供约定、对内承担职责的代码。[内聚](../../glossary/architecture.md#architecture.coupling)（Cohesion）关注内部元素是否围绕相关职责协作；耦合（Coupling）关注模块之间依赖哪些知识，以及这些知识变化时影响如何传播。文件少、类短或调用少，单独看都不足以判断边界质量。

[信息隐藏](../../glossary/architecture.md#architecture.information-hiding)（Information Hiding）把容易变化的设计决定封装在模块内部，只向使用者暴露必要约定。[Parnas 的原论文](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html)用不同分解方式比较变更影响：按处理步骤切开，与按隐藏的设计决定切开，会形成不同边界。它提供分析依据，不保证每种分解都同时获得最优性能。

以优惠功能为例，优惠资格、叠加规则和金额计算常一起变化，可能形成一个相关职责；邮件模板和数据库驱动有各自变化原因。实际边界还要结合团队、业务规则和调用成本判断，不能仅凭目录名称决定。

## 三种边界分别画

| 观察对象 | 要回答的问题 | 常见误判 |
| --- | --- | --- |
| 源码依赖 | A 编译或加载时需要知道 B 的哪些类型与约定 | 用接口包装了驱动，却把驱动对象放进接口返回值 |
| 运行调用 | 谁调用谁，等待什么，失败如何传播 | 引入事件后认为消费者不再依赖事件结构与含义 |
| 部署边界 | 哪些部分需要共同发布、扩容和回退 | 把多个[进程](../../glossary/systems.md#systems.execution-units)直接视为能够独立演进 |

进程内可以有清楚的模块；跨进程也可能因为共享表结构、同步调用链或版本绑定而紧密耦合。[Microsoft 的架构示例](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)展示了单一部署单元内部的职责分层与[依赖反转](../../glossary/architecture.md#architecture.dependency-inversion)，适合用来区分这些观察对象。

## 依赖方向如何影响替换成本

教学场景：下单规则直接导入某支付厂商 SDK，业务代码需要理解厂商错误码与响应结构。换厂商时，变化便可能穿透整个下单流程。

一种设计是由应用核心定义自己需要的支付能力，适配层负责翻译厂商协议：

```text
源码依赖（箭头表示“需要知道其约定”）：
  下单用例 → 应用核心中的支付端口
  厂商支付适配器 → 应用核心中的支付端口
  厂商支付适配器 → 厂商 SDK
  启动入口 → 下单用例 + 具体适配器，负责组装

运行调用：
  下单用例 → 注入的支付适配器 → 厂商服务
```

核心端口可以表达业务需要的金额、币种、请求标识和结果状态，避免向内暴露 SDK 类型。[依赖注入](../../glossary/architecture.md#architecture.di)（DI）负责把实现交给使用者；依赖反转关心源码依赖指向哪一层。使用 DI [容器](../../glossary/devops.md#devops.containers)不会自动产生合理边界。

这个端口仍需定义[超时](../../glossary/api.md#api.retries)、结果未知、[幂等](../../glossary/api.md#api.idempotency)和错误分类；接口不会消除远端副作用。更换厂商也可能改变业务语义，此时核心约定本身仍需调整。这里的设计推演借鉴上述 Microsoft 文档的依赖反转示例，不要求所有模块都采用同一层数。

## 抽象与拆分的成本

边界增加接口、转换和契约维护成本。只有一个稳定实现、业务逻辑很小的模块，可以先保持直接清楚的结构。为每个类建立同名接口，常常只增加跳转次数，未必隐藏了任何变化。

拆成服务还会增加网络失败、权限、观测、部署与数据协调责任。若规则要求几个数据更新共同提交，应先说明事务边界；跨服务后要另外设计协调或补偿，不能由“低耦合”三个字推导[原子性](../../glossary/systems.md#systems.atomicity)。

[领域分析指南](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)从业务能力和模型语义讨论边界。同一个“客户”在计费与配送中可以有不同模型；[限界上下文](../../glossary/architecture.md#architecture.ddd)用于明确模型含义，不必机械地与一个进程、一个表或一个团队一一对应。

## 一次变更的纸面检查

选一个现有功能，分别推演“更换存储”“增加业务规则”“修改通知格式”三次变化，记录需要修改的模块及原因：

- 若只改存储就要修改核心规则，检查是否泄漏了查询对象、事务对象或表结构。
- 若一项[业务不变量](../../glossary/architecture.md#architecture.domain-model)分散在多个模块，检查谁负责校验、谁能绕过约定直接修改数据。
- 若抽出公共模块后，互不相关的业务总要同步升级，检查是否只因字段相似就合并了语义。
- 若删除一个模块需要逐层绕回自身，检查依赖环；可通过职责重分配、端口或显式协调者重新组织。

这些是诊断线索，需要结合实际变更证据判断。自检产出是一张源码依赖图、一条运行路径，以及一个边界能减少变更影响的具体例子；本文没有执行真实项目重构。

## 关联阅读与来源

结构调整的行为边界继续见[技术债与重构](technical-debt-refactoring-and-behavior.md)：分别声明保留行为、有意变化、替换阶段与清理条件。新文为来源核查和教学设计，没有新增本文真实项目的重构或收益证据。

依赖的表示、遍历、环与拓扑顺序可继续读[图遍历与依赖顺序](../algorithms/graphs-traversal-and-dependency-order.md)。边方向必须先约定；得到一个顺序不证明模块职责合理或运行初始化已完成。本次只增加概念关联，没有新增架构或图工具实作。

- [测试层次与替身](../engineering/test-scopes-and-doubles.md)：端口替身能验证用例，真实适配器仍需契约与集成证据。
- [Transactional Outbox](../messaging/transactional-outbox.md)：异步协作仍承担消息结构、重复与传播[延迟](../../glossary/performance.md#performance.latency-throughput)的约束。
- [知识库 ADR](knowledge-base-adr.md)：记录本仓库的边界选择、代价与重评条件。

核查日期：2026-10-16。来源支持信息隐藏、依赖反转与领域边界的设计依据；支付流程、变更检查和选择建议为本文教学综合，不是已验证的项目结论。

- [Parnas：On the Criteria To Be Used in Decomposing Systems into Modules（1972，全文转录）](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html)
- [Microsoft：Common web application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)
- [Microsoft：Use domain analysis to model microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)

规则维护与写入边界继续见[领域模型、聚合与业务不变量](domain-models-aggregates-and-invariants.md)，跨组件输入输出及版本证据见[契约测试与兼容性](../engineering/contract-testing-and-compatibility.md)。两篇为来源核查与教学设计，不把划分模块、建立聚合或引入测试框架本身当作保证；本篇没有新增重构实验。

语言层的解析、链接和初始化见[模块系统与循环依赖](../runtime/modules-bindings-and-circular-dependencies.md)；源码模块怎样进入输出资源见[打包与代码分割](../frontend/bundling-tree-shaking-and-code-splitting.md)。它们与本篇的业务职责、运行调用和部署边界分别分析，均未新增重构或[打包](../../glossary/frontend.md#frontend.bundling)实验。
