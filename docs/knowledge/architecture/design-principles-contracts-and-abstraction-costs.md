---
id: "kb-architecture-design-principles"
title: "设计原则与抽象成本：SOLID、DRY 和 YAGNI 怎样一起使用"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "用变化来源、行为契约和知识所有权解释 SOLID、KISS、DRY、YAGNI，说明拆分、复用与过度抽象的取舍。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries"]
related: ["kb-architecture-patterns-collaboration", "kb-architecture-refactoring-debt", "kb-engineering-contract-compatibility", "kb-architecture-quality-decisions"]
tags: ["solid", "dry", "yagni", "contracts", "abstraction"]
---

# 设计原则与抽象成本：SOLID、DRY 和 YAGNI 怎样一起使用

学习入口：为了遵守原则拆出很多接口，为什么修改功能反而要跳过十几层？两段相似代码一定要合并吗？原则帮助识别变化与约束，不能靠统计类数、接口数或重复行数判断设计质量。

前置：[模块边界与依赖](module-boundaries-and-dependencies.md)。本文参照原则作者说明、行为子类型研究及 Pragmatic Programmer/Fowler 原文，使用教学契约解释取舍；不声称列举全部设计方法或给出形式化替换证明。没有[重构](../../glossary/architecture.md#architecture.debt)真实代码、运行示例或测量维护成本。

## SOLID 是五个不同的问题

| 原则 | 用什么问题检查 | 常见误读 |
| --- | --- | --- |
| SRP，单一职责 | 这些职责是否因为同一类业务原因而改变 | 每个类只能有一个方法 |
| OCP，开放封闭 | 针对已识别变化，能否扩展而少扰动稳定规则 | 从此不能修改旧代码，或预建所有扩展点 |
| LSP，里氏替换 | 替代实现是否仍满足调用方依赖的行为契约 | 只要[编译器](../../glossary/runtime.md#runtime.compilation)接受同一个接口就可替换 |
| ISP，接口隔离 | 使用者是否被迫依赖不需要的能力与变更 | 每个方法都必须有单独接口 |
| [DIP](../../glossary/architecture.md#architecture.dependency-inversion)，依赖反转 | 核心规则是否依赖稳定约定，而非外部实现细节 | 用了注入容器就自动满足原则 |

五项的作者说明见 Robert C. Martin 的 [SOLID Relevance](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html)。表中问题化解释和误读反例为本文教学归纳，不是五条无需上下文的考核清单。

## 职责看变化原因，扩展看真实变化轴

工资规则、持久化格式和对外报表可能由不同需求驱动，即使它们读取同一份数据，也不必成为一个不可分的职责；SRP 的变化原因解释见[原则作者原文](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)。反过来，将一条紧密的业务规则拆成很多互相知道细节的类，不会因为每个类更短就更[内聚](../../glossary/architecture.md#architecture.coupling)。

OCP 的扩展点应围绕已经识别的变化设计。例如多个计价方案都满足同一个金额契约，可把可替换算法放到约定后；如果尚未知道未来方案是否需要外部[授权](../../glossary/security.md#security.identity)或异步报价，就不能靠一个“万能策略接口”宣布所有变化已被封装。

接口也有长期成本：需要命名、理解、组装、版本演进与维护替换约束。DIP 关注源码依赖与约定归属，DI 关注如何提供依赖，两者关系见[模块边界](module-boundaries-and-dependencies.md)。

## 行为替换要守住可观察承诺

Liskov 与 Wing 的[行为子类型原论文](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)要求从上层类型成立的性质能用于子类型；不只是方法名相同。下面只用一个明确契约说明风险，不展开论文的完整不变量与历史约束体系。

教学接口 `load(id)` 承诺：输入为有效 ID；命中返回记录；不存在返回 `Missing`；读取不改变该记录；调用方无需预先命中某个缓存。

| 实现变化 | 是否仍满足本例契约 | 原因 |
| --- | --- | --- |
| 改用另一存储，仍返回相同含义的结果 | 可能满足，仍需验证 | 机制改变不必改变可观察承诺 |
| 只接受缓存中已有的 ID，否则要求调用者先预热 | 不满足 | 增加了原契约没有的调用前提 |
| 找不到时返回一条虚构的默认记录 | 不满足 | 把缺失换成了成功含义 |
| 读取时悄悄更新该记录的业务状态 | 不满足 | 引入被禁止的副作用 |

错误、并发、资源寿命和时序若属于约定，也要一起检查。一个接口若承诺同步返回，不能在保持签名外观时把未完成工作当成完成结果；若不承诺特定[延迟](../../glossary/performance.md#performance.latency-throughput)，也不能把所有性能差异都自动归为 LSP 违反。

## DRY 去掉知识重复，不是消灭一切相似文本

[DRY](../../glossary/architecture.md#architecture.principles) 关注同一知识有清楚的权威表达，见 [Pragmatic Programmer Tip 15](https://pragprog.com/tips/)。同一税额规则若在多个地方独立维护，修改时容易分叉；可让调用者共享规则能力，或从同一来源生成需要的表示。

教学反例：配送备注最多 200 字符，昵称也恰好最多 200 字符。二者来自不同业务约束，未来可能独立改变。只因数字相同就抽出一个通用 `MAX_LENGTH`，会把偶然相似变成错误的共同变化。相反，同一规则在服务校验和界面提示有不同表示，也应说明谁是权威、怎样保持一致，不能简单强求前后端共用同一可执行库。

共享抽象越宽，调用方依赖的共同承诺越多。先判断“是否同一知识”，再判断“如何共享”，比先找重复行更可靠。

## KISS 与 YAGNI 控制今天承担的复杂度

KISS 在本文作为保持方案易于理解的启发式，不以最少代码行或最少模块为定义。简单方案仍需表达错误、权限和恢复，不能把必要边界删掉后称作简单。

YAGNI 克制尚无现实需要的能力，不等于拒绝测试、模块化或让后续修改更容易，见 [Fowler 的 Yagni](https://martinfowler.com/bliki/Yagni.html)。例如暂不实现多租户插件平台，与先把业务规则从某个供应商 SDK 中隔离，是不同决策：前者增加未来产品能力，后者可能正在降低已发生的变更成本。

一个教学选择是先保留两段独立业务流程，记录相似点与实际变化；当同一规则反复一同修改、契约已经稳定时再提取共享能力。它不意味着必须复制三次才允许抽象，也不意味着共享越晚越好。

## 自检

1. SRP 与“每类一个方法”有何区别？OCP 是否禁止修复旧代码？
2. `load(id)` 的缓存前提、默认记录和隐式写入分别破坏了什么承诺？
3. 相同接口但更慢，是否一定违反行为替换？还需知道什么契约？
4. 两处 200 字符限制为何不一定应该合并？同一规则多种表示又该怎样管理？
5. YAGNI 为什么不等于拒绝测试与模块化？抽象时应解释什么现实收益和成本？

## 来源与核查

2026-10-26 核查 Martin 的两篇原则原文、Liskov/Wing 1994 论文、Pragmatic Programmer 官方 tips 与 Fowler Yagni。本文为 source-checked 概念文章；契约、反例与抽象选择为纸面设计，未证明某项目遵守全部原则，也未运行替换、重构或成本实验。
