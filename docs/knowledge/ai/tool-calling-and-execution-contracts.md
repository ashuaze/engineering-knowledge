---
id: "kb-ai-tool-contracts"
title: "工具调用契约：模型提出动作以后由谁执行"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分调用候选、运行时准入、工具受理和业务确认，说明标识、依赖、预算与未知结果的责任。"
created: "2026-10-19"
updated: "2026-10-27"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: ["kb-api-idempotency"]
related: ["kb-ai-structured-output", "kb-ai-tool-security", "kb-ai-tools-lab", "kb-ai-recoverable-runtime", "kb-reliability-retry-budgets", "kb-ai-workflow-routing", "kb-ai-workflow-state", "kb-ai-workflow-budgets", "kb-ai-mcp-boundaries"]
tags: ["tool-calling", "contracts", "runtime", "side-effects"]
---

# 工具调用契约：模型提出动作以后由谁执行

学习入口：助手输出了“创建工单”，是否意味着工单已经存在？前置：请求响应与[幂等性](../../glossary/api.md#api.idempotency)。模型可以提出工具与参数，实际调用、权限和结果责任需要由执行系统承担。本文核查概念；本库[工具边界实验](tool-execution-boundaries-lab.md)只使用固定候选和受控本地工具，没有调用生成模型。

跨宿主和能力提供方的协商、原语及结果边界继续见[MCP与能力协商](mcp-hosts-capabilities-and-execution-boundaries.md)。

## 提出、准入、执行与确认是不同事实

| 边界 | 已知什么 | 还不能声称什么 |
| --- | --- | --- |
| 生成候选 | 模型提出工具名与参数 | 参数正确、被[授权](../../glossary/security.md#security.identity)或已经执行 |
| [运行时](../../glossary/runtime.md#runtime.virtual-machine)准入 | 通过相应校验与策略 | 外部工具已收到，更不代表提交成功 |
| 工具返回 | 得到数据、受理信息或错误 | “已受理”不等于最终业务完成 |
| 核实与保存 | 找到与本动作关联的可核实结果并保存 | 其他未核实动作也已成功 |

[OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling)说明了一种常见循环：应用提供工具定义，接收调用项，执行相应应用代码，再把结果交回模型。本文主要讨论这种由应用调度的函数工具；托管工具的执行位置和控制接口可能不同，仍需核对实际产品契约。

文本“我已完成”不替代执行记录。模型后续回答也只能基于传回的证据；日志中有调用候选、工具返回 202 或产生一个任务号，都不应自动显示为业务成功。

## 工具定义应约束可执行能力

一个工具契约应说明名称与版本、输入结构、对象范围、读写性质、前提条件、返回状态、错误与[重试](../../glossary/api.md#api.retries)语义，以及能否按稳定标识查询结果。范围窄的“为指定项目创建工单”，比接受任意命令的“执行任何操作”更容易审查和授权，但仍需要可信策略校验。

教学链路如下，阶段可按实现合并，但责任不能消失：

```text
完整调用候选 → 已注册工具与版本 → 参数/业务校验 → 当前身份与授权
             → 必要的动作审批 → 持久化意图 → 执行
             → 校验返回与核对业务记录 → 保存结果 → 继续或停止
```

模型给出的 tenant_id、approved=true 或工具描述中的“安全”字样，都不能创建可信身份或许可。调用适配器应把身份、凭证和权限范围绑定到真实会话，详见[工具授权](tool-authorization-and-untrusted-results.md)。

## 调用标识和业务动作标识承担不同作用

call_id 等协议标识用于把工具结果对应回某个调用项；operation_id 用于在执行、重试、查询和恢复之间标识同一个业务动作。二者不必相同，不能默认模型重新生成的调用 ID 就是可靠的业务幂等键。

教学设计为同一动作保留稳定 operation_id，把工具版本、主体、租户与参数指纹一起关联；每次尝试另记 attempt_id。若同一 operation_id 换成不同参数，应报冲突，不能默默返回另一动作的结果。参数规范化也必须有版本与明确规则，不能为了“看起来相同”就删除有业务意义的字段。

本地实验用运行时提供的 operation_id、独立的调用 ID 与规范化参数摘要验证顺序重放；没有实现上述独立 attempt_id，也没有证明跨租户分布式[并发](../../glossary/systems.md#systems.concurrency)下的 exactly-once。[幂等性](../api/idempotency.md)中的业务边界同样适用工具。

## 多个候选不等于可以任意并发

一次模型输出可能包含零个、一个或多个调用。依赖先前结果的动作需要等待；两个写动作也可能争用同一对象。并行调用选项只影响候选或协议行为，不自动提供业务隔离、事务和正确顺序。

教学例子：先查项目当前状态再创建工单，查询后的状态仍可能在写入前变化。真正约束“项目关闭后不能创建”的规则，应落在权威写入路径的事务或条件检查中；在模型计划中排好顺序不等于消除了竞争。本轮没有测试这种并发时序。

调度还需约束步骤数、在途工具数、总[截止时间](../../glossary/reliability.md#reliability.retry-budget)、重试和费用。工具输出要求“再试直到成功”不能自行增加预算。只限制生成 [Token](../../glossary/ai.md#ai.context)，也不一定限制工具已经[排队](../../glossary/performance.md#performance.queueing)或产生的外部工作。

多个候选怎样成为完整流程，继续读[路由与交接契约](workflow-routing-and-handoff-contracts.md)、[编排状态与检查点](workflow-state-and-checkpoints.md)和[持久化预算](durable-budgets-and-failure-convergence.md)。它们解释跨步骤的控制与责任，不扩大现有工具实验的范围。

## 返回值要表达业务状态与来源

输入 Schema 和输出契约是两回事。输出至少需要让运行时分清：已受理仍处理中、成功且有结果依据、已知失败、以及无法确认效果。返回 JSON 结构正确，仍可能引用错误操作、租户、对象或旧版本。

教学实现对工具返回先校验字段，再按稳定动作标识查询受控工具账本核对结果；工具的说明性 note 保持“不可信数据”来源标签。真实集成未必提供可查询账本，需要按工具能力选择证据，不能凭模型相信了某段文字就确认成功。

## 结果丢失时先保留未知

外部工具可能已经提交，而运行时尚未保存结果。prepared 记录只证明意图已保存，不能证明工具未执行。恢复应先重新确认当前权限，再按支持的查询或幂等协议核实；工具无法查询且副作用不可重放时，保留 unknown，交给对账或人工判断。

[本地实验](tool-execution-boundaries-lab.md)已验证工具侧提交后丢失结果、以及受控异常后重开数据库查询的路径。它没有真实[进程](../../glossary/systems.md#systems.execution-units)强杀、HTTP 工具、SDK、模型调度或跨系统事务，既有[可恢复 Runtime](recoverable-runtime.md)仍是一份更完整的[设计提案](../../glossary/engineering.md#engineering.design-docs)。

自检：模型输出 call_id=c2，但这是同一动作的重试，是否应该换 operation_id？工具返回 accepted，前端能否显示“工单创建成功”？同一操作的查询不可用时，为什么不能统一重试？

核查日期：2026-10-19。[函数调用](../../glossary/ai.md#ai.tools)循环依据上述官方资料；标识设计、阶段表与教学链路为工程综合，具体验证范围由独立实验页承担。
