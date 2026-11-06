---
id: "kb-engineering-property-state-models"
title: "属性测试与状态模型：样例通过为什么仍会漏掉边界"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "区分固定样例、生成输入、性质与测试判断依据，解释收缩、状态机命令和回归反例，以及顺序模型的证据边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-engineering-test-scopes", "kb-architecture-aggregates-invariants"]
related: ["kb-engineering-contract-compatibility", "kb-database-concurrent-inventory", "kb-api-idempotency", "kb-systems-races-atomicity", "kb-algorithms-greedy", "kb-algorithms-dynamic-programming"]
tags: ["property-testing", "state-machine", "oracle", "regression"]
---

# 属性测试与状态模型：样例通过为什么仍会漏掉边界

学习入口：预订、取消分别测试都通过，为什么连续操作后库存却超过初始数量？前置：[测试层次与替身](test-scopes-and-doubles.md)、[业务不变量](../architecture/domain-models-aggregates-and-invariants.md)。本文以 Hypothesis 6 文档解释属性与状态测试，以 libFuzzer 文档区分一种模糊测试机制；性质、模型和操作序列均为纸面设计，没有安装或运行这些工具。

## 自动生成输入之前，先决定怎样判断对错

算法对照可配套读[贪心与交换论证](../algorithms/greedy-choices-and-exchange-arguments.md)及[动态规划与状态设计](../algorithms/dynamic-programming-states-and-dependency-order.md)。小实例穷举可以校验候选实现的输出，抽样未找到反例不能代替整体证明；新文的反例和表格为纸面设计，没有新增本文属性生成或穷举执行结果。

固定样例测试写出具体输入与预期；[属性测试](../../glossary/engineering.md#engineering.generative)为一组适用输入声明应成立的性质，再让工具探索输入。自动生成增加了搜索范围，但不会自动产生正确需求或可信的判断依据。[Hypothesis 入门](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html)展示了这种测试方式。

| 要素 | 在测试中负责什么 |
| --- | --- |
| 输入域 | 哪些值、结构或操作序列属于讨论范围 |
| 生成策略 | 怎样构造和探索这些输入，包括关键边界 |
| Property，性质 | 在声明前提下应成立的关系或[不变量](../../glossary/systems.md#systems.atomicity) |
| Oracle，判断依据 | 根据什么判断结果正确，例如独立模型或业务约束 |
| 重放与隔离 | 让相同条件下的失败能够再次观察和定位 |

教学例子：对普通有限整数列表排序，只验证“再次排序结果不变”不够，永远返回空列表也符合这条关系。还需要结果有序、元素及重复次数保留等约束；性质是否足够，必须用错误实现和反例检查。

同样，“编码后再解码得到原值”可能漏掉编解码两侧共享的错误，还应结合已知格式样例、独立实现或其他约束。把生产实现的分支完整抄进预期计算，容易让测试与实现一起错。

## 输入域与搜索分布不是同一件事

输入域规定哪些值可以出现；分布影响工具先尝试什么、更多探索哪里。Hypothesis 默认并不追求均匀抽样或真实生产流量分布，其目标是有效搜索失败输入。定义见 [Domain and distribution](https://hypothesis.readthedocs.io/en/latest/explanation/domain.html)。因此，“本次生成输入没有失败”不能直接换算成生产缺陷概率。

设计策略时应覆盖空值、边界数值、重复、顺序变化、长度和结构关系，并明确哪些是合法输入、哪些应被拒绝。复杂对象通常适合从其约束出发构造；先生成大量不合法输入再全部过滤，可能使真正被检查的范围很窄。组合与调整策略见 [Hypothesis Adapting strategies](https://hypothesis.readthedocs.io/en/latest/tutorial/adapting-strategies.html)。

过滤也可能把目标缺陷过滤掉。例如测试取消操作时，只允许取消仍活动的预订，就永远不会检查重复取消。应分别设计有效路径、重放路径和非法请求的拒绝行为，而不是让所有“不方便”的情况都变成不执行断言。

## 收缩帮助解释反例，不证明全局最小

发现失败后，工具可以尝试简化数值、结构或命令序列，同时保留失败，帮助定位较小的触发条件。Hypothesis 的相应阶段见 [API：test phases](https://hypothesis.readthedocs.io/en/latest/reference/api.html#hypothesis.Phase)。具体结果受策略、预算、重放稳定性与工具能力影响，不应把输出叫作已证明的全局最小反例。

如果测试共享残留数据、读取真实时钟、依赖未控制的[线程](../../glossary/systems.md#systems.execution-units)时序，简化后的输入可能无法稳定重现失败。每个独立样例或序列需要相应的初始化与清理，不能默认测试框架会替每个生成输入重建所有外部资源。

失败也可能来自测试本身：性质遗漏前提、模型不符合需求、状态准备错误，或者实现确有缺陷。正确处理是核对规则与复现条件，不能直接削弱断言或限制输入直到变绿。

## 状态模型生成的是操作之间的关系

有状态系统的结果取决于历史。[状态机测试](../../glossary/engineering.md#engineering.state-models)维护简化模型，根据模型生成命令，对被测系统执行对应动作，再比较结果及每一步的不变量。规则、前置条件与 invariant 的机制见 [Hypothesis Stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html)。

教学模型只讨论一个 SKU、顺序执行的预订与取消：初始容量为 2，有效预订数量为正整数，测试输入另外包含应被拒绝的非法数量；没有补货、过期或外部副作用。新预订使用尚未出现的标识，库存不足则拒绝；活动预订取消后归还一次库存，已取消者再次取消只重放结果，不再归还。未知标识的取消按本例契约拒绝。

```text
模型状态：初始容量、当前剩余量、活动预订、已取消预订
模型动作：新预订、取消活动预订、重复取消、应被拒绝的请求
每步检查：0 ≤ 剩余量 ≤ 初始容量
          剩余量 + 所有活动预订的预订数量之和 = 初始容量
          拒绝或重放操作不产生额外库存变化
```

模型独立按上述规则计算预期，不能直接把被测系统返回的库存当作正确答案。生成新预订时可以使用模型的剩余量安排合法路径；库存不足、零数量和未知取消等拒绝路径需另外生成并检查状态未被改变。前置条件应表达某条规则何时适用，不应遮蔽需要验证的非法输入。

## 一条短序列怎样暴露单次样例漏掉的问题

下面是教学推演，不是工具实际生成的日志：

| 操作 | 正确模型的剩余量 | 要检查的状态 |
| --- | --- | --- |
| 初始 | 2 | 无预订 |
| 预订 r1，数量 1 | 1 | r1 活动 |
| 取消 r1 | 2 | r1 已取消 |
| 再次取消 r1 | 2 | 重放取消结果，库存不再增加 |

如果实现每次收到取消都加回数量，最后可能得到 3，违反上界与守恒。只测“预订一次”和“取消一次”就可能遗漏它；输入数量再多，若从不生成重复取消，也找不到这条反例。

这个顺序模型不能证明两个[并发](../../glossary/systems.md#systems.concurrency)请求的交错正确，更不能证明数据库隔离、崩溃恢复和远程调用的真实副作用。并发仍需相应调度、真实依赖与历史验证，见[竞态与原子性](../systems/races-and-atomicity.md)和[库存并发](../database/concurrent-inventory.md)。同一预订标识的重复创建、跨租户权限和取消结果持久化也需要扩展模型及[幂等契约](../api/idempotency.md)。

## 属性测试与模糊测试可以相互组合

属性测试强调应成立的关系；模糊测试的一类常见机制是持续生成或变异输入，借助崩溃、检查器、断言等观察异常。它们并非互斥分类，也不简单等于“结构化数据”和“随机字节”。例如 [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html)是进程内、覆盖引导的模糊测试工具，会利用执行反馈探索输入；其他工具的模型可能不同。

二者都需要清楚的测试入口、可复现环境和有意义的观察。高覆盖率不自动说明业务性质完整；没有崩溃也不能说明业务金额、权限或状态转换正确。输入探索与行为断言各自决定能发现哪类问题。

## 把发现保留为回归证据

重现时应保存具体输入或操作序列、性质和模型版本、被测版本、工具版本、配置及必要环境；随机种子可以辅助定位，但不能替代这些材料。Hypothesis 的失败重放和内部表示有版本边界，不能只留一段临时重放数据就假定永久可用。说明见 [Replaying failed tests](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html)。

修复确认后，将关键反例写成明确的回归样例，同时保留生成测试继续搜索其他组合。示例数据库可以帮助重放，但不能代替应长期保存的行为断言；Hypothesis 对显式样例与缓存的说明见 [API Reference](https://hypothesis.readthedocs.io/en/latest/reference/api.html#database)。

自检：性质能否排除一个明显错误实现？生成器是否真会产生目标边界？模型是否复制实现错误？每条序列怎样隔离状态？收缩后怎样确认失败仍来自同一问题？哪些并发与外部协议仍没有证据？跨组件输入输出的版本兼容见[契约测试](contract-testing-and-compatibility.md)。

2026-10-20 核查 Hypothesis 6 与 LLVM 官方文档，状态为 source-checked。库存性质、状态机和取消反例均为纸面设计；未执行属性生成、收缩、模糊测试、并发调度或新增回归实验，也未声称现有实验已经覆盖这些模型。
