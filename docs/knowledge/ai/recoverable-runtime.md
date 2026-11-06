---
id: "kb-ai-recoverable-runtime"
title: "可恢复 Agent Runtime：从工具结果未知开始设计"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "围绕工具副作用的故障窗口设计状态、恢复和人工介入。"
created: "2026-10-16"
updated: "2026-10-20"
last_verified: null
verification: "design-proposal"
prerequisites: ["kb-api-idempotency"]
related: ["kb-api-idempotency", "kb-messaging-outbox", "kb-reliability-retry-budgets", "kb-security-object-authorization", "kb-ai-context", "kb-ai-rag", "kb-ai-evals", "kb-ai-tool-contracts", "kb-ai-structured-output", "kb-ai-tool-security", "kb-ai-tools-lab", "kb-ai-workflow-routing", "kb-ai-workflow-state", "kb-ai-workflow-budgets"]
tags: ["agent", "state", "reliability"]
---

# 可恢复 Agent Runtime：从工具结果未知开始设计

学习入口：Agent 重启后，如何判断工具是否已经产生业务效果？前置知识：[API 幂等性](../api/idempotency.md)、持久化状态与[工具调用](../../glossary/ai.md#ai.tools)。下文是待结合实际工具验证的架构[设计提案](../../glossary/engineering.md#engineering.design-docs)。

## 故障起点：工具成功但结果未保存

可恢复 Agent [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 通过持久化动作意图、可核实结果与恢复策略，让中断后的执行能继续、停止或转人工，并明确外部效果无法确认的情况。

Agent 调用了“创建工单”，工具已成功写入业务系统，Runtime 在保存结果前崩溃。重启后仅看到“工具待执行”。再次执行可能创建重复工单；直接当作成功又缺少结果。

本文提出与具体 SDK 无关的架构设计。它不是某个框架功能清单，也没有把模型输出当作已执行的业务事实。

## 状态与恢复决策

### 先区分状态

| 状态 | 可确认的事实 | 合理的下一步 |
| --- | --- | --- |
| planned | 已提出工具动作 | 校验参数、权限、预算和审批 |
| prepared | 已持久化动作意图与 operation_id | 根据执行策略发起调用 |
| confirmed | 已持久化可核实结果 | 将结果提供给模型继续 |
| unknown | 无法确定外部效果 | 查询、对账或人工介入 |
| terminal | 已完成、取消或明确失败 | 停止调度，保留审计 |

这些是本文的示意状态名，实际系统可能还需要 queued、running、waiting-approval 和 compensated。状态机保证首先来自合法流转、持久化和恢复策略，名称本身不产生[可靠性](../../glossary/reliability.md#reliability.availability)。

### 恢复决策

| 工具特征 | 恢复策略 |
| --- | --- |
| 只读且重复调用可接受 | 在预算内重新读取，承认结果可能变化 |
| 支持业务[幂等](../../glossary/api.md#api.idempotency)键 | 复用 operation_id 调用或查询原结果 |
| 可按业务键查询 | 先核对结果，再决定是否执行 |
| 不可查询且有不可逆副作用 | 进入 unknown，交由对账或人工判断 |

将动作意图写入 [checkpoint](../../glossary/ai.md#ai.state)，只能证明系统记录了意图。它不能自动让外部执行和本地状态记录形成同一个事务。

## 执行链路与持久化记录

以下是完整 Runtime 的架构设计；新增[本地工具边界实验](tool-execution-boundaries-lab.md)已实现固定候选下的局部校验、[授权](../../glossary/security.md#security.identity)与查询恢复，未实现模型调度和真实远程工具集成。执行链路为：模型提出动作 → Runtime 校验 → 持久化意图 → 调用工具 → 核实并保存结果 → 继续调度；[超时](../../glossary/api.md#api.retries)或中断后按恢复决策处理。

### 建议的执行记录

每个动作包含 run_id、step_id、稳定 operation_id、工具名和版本、规范化参数指纹、身份与租户作用域、审批依据、尝试编号、状态、结果引用和错误分类。敏感参数应按数据策略存储或脱敏。

重试同一业务动作时保持 operation_id 稳定，attempt_id 则随尝试改变。否则外部工具无法识别两次尝试属于同一动作。

### 决策与执行分开

模型提出动作后，由 Runtime 检查工具白名单、输入、数据访问范围和人工审批。恢复时也要重新确认授权是否仍然有效，避免旧 checkpoint 绕过当前权限。

对于长时间中断的计划，应判断业务前提是否过期，例如工单已由其他人处理。简单重放旧的模型决策可能产生语义错误，即使技术层面没有重复写入。

## 故障窗口、约束与维护成本

| 触发条件 | 后果 | 处理或缓解 |
| --- | --- | --- |
| 工具成功，Runtime 尚未保存结果就中断 | 恢复时可能重复执行 | 进入 unknown，按稳定标识查询、幂等重试或转人工 |
| 同一动作每次重试都更换 operation_id | 工具无法识别重复动作 | 保持 operation_id，单独更新 attempt_id |
| 直接重放旧 checkpoint | 可能使用已失效授权或业务前提 | 恢复时重新检查权限与业务状态 |
| 恢复不断重试且没有预算和终止分支 | 无法收敛到可确认结果 | 设置尝试预算、终止状态与人工介入路径 |

上述为设计分析中的故障窗口，尚未通过 Runtime 集成实验验证。

持久化状态与稳定动作标识为恢复和审计提供依据，也增加执行记录、结果核对、权限复查和人工介入的维护成本。恢复能力受工具契约约束：支持幂等或查询的工具更容易核实；不可查询且有不可逆副作用的工具需要保留 unknown 分支。

## 待执行的恢复验证

以下为完整验证目标，局部已测范围在清单后单独说明：

1. 在动作意图保存前、保存后、工具执行后、结果保存后分别注入中断。
2. 为“工具超时但已成功”设计返回未知的[测试替身](../../glossary/engineering.md#engineering.doubles)。
3. 验证同一 operation_id 不重复产生受控副作用。
4. 验证权限撤销后无法继续执行旧动作。
5. 验证重复恢复、循环恢复和预算耗尽都能终止或转人工。

新增[工具执行边界实验](tool-execution-boundaries-lab.md)使用固定候选、两份 SQLite 文件与受控工具，验证稳定动作重放、结果丢失查询、撤权和一处提交后受控异常窗口。异常后关闭并重开连接，不是实际[进程](../../glossary/systems.md#systems.execution-units)强杀或 SDK Checkpoint 故障注入；步骤预算也没有跨恢复持久化。其他窗口、[并发](../../glossary/systems.md#systems.concurrency)、模型调度与真实工具集成仍待验证；本文继续保持 design-proposal，不将局部实验扩成整套 Runtime 已验证。

自检：给一个有外部副作用的工具写出“可确认成功、可确认失败、结果未知”的判断依据，并为每种情况选择查询、重试或人工处理。

[编排](../../glossary/ai.md#ai.harness)问题已另补[路由与交接契约](workflow-routing-and-handoff-contracts.md)、[状态与检查点](workflow-state-and-checkpoints.md)及[持久化预算](durable-budgets-and-failure-convergence.md)三篇来源核查概念。它们细化责任和边界，没有新增本提案的完整实现或集成验证。

## 关联概念

- [工具调用契约](tool-calling-and-execution-contracts.md)、[结构化校验](structured-outputs-and-validation.md)与[工具授权](tool-authorization-and-untrusted-results.md)：先理解执行前后各自的责任，再设计恢复。

- [Token、上下文与记忆](tokens-context-and-memory.md)：当前输入与摘要不能代替权威执行状态。
- [RAG 与依据](rag-retrieval-and-grounding.md)：恢复时取回的资料仍需当前访问范围、版本和来源支持。
- [Evals 与失败分析](evals-and-failure-analysis.md)：把结果未知、误判成功和评分器误判分别纳入检查。

- [API 幂等性](../api/idempotency.md)：稳定操作标识和结果复用。
- [Transactional Outbox](../messaging/transactional-outbox.md)：本地事务与外部执行的边界。
- [超时与重试预算](../reliability/timeouts-and-retry-budgets.md)：为工具尝试分配剩余时间，并在预算耗尽时保留未知状态。
- [对象级授权](../security/object-level-authorization.md)：执行与恢复阶段都检查主体、租户、对象和动作。

## 设计依据与证据状态

这是基于故障窗口分析的设计提案。引用的基础模式及来源见上述文章；不宣称这里的状态集合是行业标准。
