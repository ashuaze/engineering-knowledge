---
id: "kb-architecture-patterns-collaboration"
title: "设计模式与协作契约：结构相似为什么行为仍可能不同"
kind: "concept"
domain: "architecture"
status: "evolving"
summary: "用策略、适配器、装饰器与观察者区分变化意图，解释行为翻译、组合顺序、订阅寿命和模式的适用成本。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-architecture-module-boundaries", "kb-architecture-design-principles"]
related: ["kb-architecture-refactoring-debt", "kb-architecture-quality-decisions", "kb-engineering-contract-compatibility", "kb-messaging-outbox", "kb-runtime-gc"]
tags: ["design-patterns", "strategy", "adapter", "decorator", "observer"]
---

# 设计模式与协作契约：结构相似为什么行为仍可能不同

学习入口：同样是“包一层对象”，为什么有时叫适配器，有时叫装饰器？用了观察者，消息就不会丢了吗？模式描述特定问题下的协作意图；类图只展示部分结构，还要说明输入、结果、副作用、顺序与寿命。

前置：[模块边界](module-boundaries-and-dependencies.md)、[设计原则与抽象成本](design-principles-contracts-and-abstraction-costs.md)。本文选取四类常见协作，不穷举 GoF 模式、并发变体或各框架实现。JDK 25 API 仅作为具体机制参照；接口、金额和通知均为纸面例子，没有执行代码或接入外部系统。

## 先说希望哪一种变化独立

| 模式 | 希望隔离的问题 | 核心承诺 | 不能仅由模式名得到 |
| --- | --- | --- | --- |
| Strategy，策略 | 同一目标存在不同算法 | 按共同契约选择实现 | 任意新算法都无需改变契约 |
| Adapter，适配器 | 现有接口与调用方期望不一致 | 翻译接口及其语义 | 只改字段名便自动兼容 |
| Decorator，装饰器 | 在原能力周围组合附加行为 | 保持相应接口，明确组合效果 | 包装顺序无关、失败会自动回滚 |
| Observer，观察者 | 对象变化后通知多个订阅者 | 管理订阅与通知关系 | 持久历史、全局顺序或业务[恰好一次](../../glossary/messaging.md#messaging.exactly-once) |

GoF 的[出版社资料与适配器原书节选](https://www.informit.com/articles/article.aspx?p=1398600)用于模式意图的来源入口；本文其余场景与边界为教学设计，不把图形或类名当作完整证明。

## 策略隔离算法，仍需要共同输入与结果含义

例如计价能力接收同一币种的非负整数金额，返回按约定舍入的结果；普通折扣和会员折扣可以是候选策略。若另一实现还要求远程[授权](../../glossary/security.md#security.identity)、可能只返回待处理状态，就需要重新核对调用契约，而不是硬塞进“立即得到最终金额”的接口。

策略也可以由函数、配置驱动计算或对象实现，不要求每个分支都变成继承层次。[JDK 25 Comparator](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html)展示把比较能力传给排序等使用者的机制，同时规定比较关系的契约。可插入一个比较器，不代表可以忽略传递性等条件。

是否提取策略取决于真实变化、测试与维护收益。一个稳定、很短的分支可能比只转发一次的层层对象更清楚。

## 适配器必须翻译能力的真实承诺

供应商接口返回 `accepted`，可能只表示接收了处理请求；领域接口若承诺“扣款已完成”，就不能把它直接映射成 `Completed`。应保留 `Pending`，或改变协议来取得最终结果。币种、单位、错误分类、重放标识及资源寿命同样可能需要翻译。

适配器的意图是让接口不兼容的部分协作，原书节选明确了这一点；端口如何保护应用免于直接理解外部机制，见 [Cockburn 的 Ports and Adapters 原文](https://alistair.cockburn.us/hexagonal-architecture)。一个保持供应商字段形状、让所有调用方继续理解 SDK 细节的包装类，可能只增加了一层转发。

适配器也不能凭空提供底层不存在的[跨资源共同提交](../distributed/two-phase-commit-sagas-and-recovery.md)、撤销或[幂等](../../glossary/api.md#api.idempotency)保证。若差异不能隐藏，应明确暴露限制，而不是把不确定结果伪装成正常成功。

## 装饰器的顺序属于语义

[JDK 25 FilterInputStream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/FilterInputStream.html)展示在已有流周围包装并转发/扩展行为的机制。具体的读、关闭、异常和拥有关系仍依实际类型；不能因为实现同一个接口就断言所有包装可任意交换。

教学模型只计算非负整数金额，单位为分，向下取整：折扣 `D(x)=floor(0.9×x)`，固定附加费用 `F(x)=x+100`。两种组合在输入 1000 时为：

```text
先折扣，再加费用：F(D(1000)) = F(900)  = 1000
先加费用，再折扣：D(F(1000)) = D(1100) = 990
```

差额为 10 分。这不是实际价格建议，而是说明相同构件、不同顺序会改变结果；模式本身不会替业务决定哪一种正确。

类似地，重试与记录、缓存与权限检查的先后，会改变重复效果、可见记录和检查时机。先写出每层负责什么、调用几次、哪些失败传播，再选择组合；不要把每一层都当作独立无副作用的函数。

## 观察者负责通知关系，恢复协议另行设计

[JDK 25 PropertyChangeSupport](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/java/beans/PropertyChangeSupport.html)管理监听器与属性变化通知，是一个具体通知机制参照。一般观察者协作还需要约定同步或异步、监听器出错后的处理、重入、顺序以及何时退订，不能从“有订阅”推断这些保证。

教学反例：订单已提交，但[进程](../../glossary/systems.md#systems.execution-units)在通知监听器之前崩溃；内存订阅关系本身不会自动补发。若必须恢复，应引入可靠记录与派送边界，例如 [Outbox](../messaging/transactional-outbox.md)，并在消费端处理重复。把监听器改成异步任务只改变执行安排，不会自动闭合提交与派送之间的窗口。

订阅者寿命也需管理。短命页面或对象注册到长命发布者后，若仍被引用且没有退订，可能持续接收无关通知或无法释放。资源释放与对象可达性见[可达性与 GC](../runtime/reachability-and-garbage-collection.md)。

## 什么时候模式会变成负担

当变化点尚不清楚时，提前引入多个可替换层，可能让每次修改都要穿透更多契约。[反模式](../../glossary/architecture.md#architecture.patterns)的判断应给出后果：错误成功映射、顺序不明的包装、无寿命的订阅，或所有实现同时修改的“可扩展接口”。仅凭用了继承、出现单例或代码较长，不能完成判断。

选模式前先说明当前问题，使用后再核对契约和成本；需要拆掉不再有价值的抽象时，也应按[保持行为的重构](technical-debt-refactoring-and-behavior.md)逐步处理。

## 自检

1. 策略、适配器、装饰器与观察者分别希望隔离什么变化？为何不能只看类图命名？
2. 供应商 accepted 为什么不能直接映射成业务 Completed？还需翻译哪些语义？
3. 两种费用/折扣组合分别是多少？这说明模式没有替你决定什么？
4. 订单提交后进程崩溃，内存观察者为什么不能保证恢复派送？
5. 一个包装接口的所有实现总是同时修改，应重新检查哪些契约和成本？

## 来源与核查

2026-10-26 核查 GoF 出版社适配器节选、Cockburn 原文及上述 JDK 25 API。本文为 source-checked 概念文章；未把书籍目录当作已阅读全文，也未运行模式实现、订阅/资源回收、重试组合或[契约测试](../../glossary/engineering.md#engineering.contracts)。案例解释机制，不证明某种模式普遍更快或更可靠。
