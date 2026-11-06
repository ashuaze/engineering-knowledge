---
id: "kb-ai-workflow-state"
title: "编排状态与检查点：保存进度后为什么仍可能重做"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分模型上下文、流程状态、检查点与外部效果，解释恢复、重放、版本兼容和当前授权。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-ai-workflow-routing", "kb-api-idempotency"]
related: ["kb-ai-workflow-budgets", "kb-ai-recoverable-runtime", "kb-ai-context", "kb-ai-memory-access-deletion", "kb-messaging-outbox", "kb-ai-tools-lab", "kb-distributed-leases-fencing"]
tags: ["workflow", "state", "checkpoint", "recovery"]
---

# 编排状态与检查点：保存进度后为什么仍可能重做

学习入口：已经保存 [checkpoint](../../glossary/ai.md#ai.state)，重启后为什么仍可能重复创建工单？前置：工具动作、[幂等性](../../glossary/api.md#api.idempotency)和持久化。检查点记录的是选定边界上的流程状态，恢复需要解释这些状态、确认它们仍适用，并处理边界之外的效果。保存成功不代表所有外部动作与检查点一起提交。

## 四种状态各有权威范围

| 材料 | 用来判断什么 | 不能独立证明什么 |
| --- | --- | --- |
| 模型上下文与聊天记录 | 当前模型可以看到什么 | 某次工具已经产生业务效果 |
| [编排](../../glossary/ai.md#ai.harness)状态 | 当前节点、依赖、待办与流程决策 | 外部系统的最终业务事实 |
| 检查点 | 某次保存边界可恢复的流程表示 | 之后没有执行任何动作，或一定能从任意代码行续接 |
| 外部动作记录 | 工具按其契约已受理、完成或失败 | 编排结果已保存，其他动作也已完成 |

[LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)区分按 [thread](../../glossary/systems.md#systems.execution-units) 保存图状态的 checkpointer 与跨 thread 保存应用数据的 store。这是该框架的职责划分；长期偏好、运行进度和工具业务账本不应因都“存到数据库”就混成一个权威来源。记忆的独立生命周期见[权限与删除](memory-access-revocation-and-deletion.md)。

## 检查点边界决定恢复粒度

[LangGraph Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)说明完整检查点位于 super-step 边界，并另有节点级 pending writes 用于失败恢复；其持久化模式也影响何时写入。不能把这些细节简化为所有框架都“每执行一行保存一次”。选型时还需核对实际版本、后端与写入确认契约。

边界较细通常能减少部分重做，也增加写入、[序列化](../../glossary/runtime.md#runtime.serialization)和存储维护；边界较粗则可能重复更多计算。是否重复外部副作用，还取决于工具契约与动作记录。内存保存器适合演示，但进程消失后是否还能恢复，应由实际持久化介质证明，不能凭对象名包含 Saver 判断。

教学上可把保存内容分成：流程/图版本、状态结构版本、任务与父任务标识、节点及依赖、状态版本、已核实结果引用、未决动作标识，以及预算账本引用。必要记录使用受控引用和最少内容；原始凭证、开放文件句柄和进程局部对象不能被当作可移植恢复状态。

## 恢复、重试与历史重放不同

| 动作 | 意图 | 要重新判断的风险 |
| --- | --- | --- |
| 恢复 Resume | 延续尚未结束的流程 | 最新进度、当前权限、未决动作和剩余预算 |
| [重试](../../glossary/api.md#api.retries) Retry | 再尝试一个允许重做的步骤 | 是否同一业务动作、重放是否安全、尝试是否计费 |
| 历史重放 / 分支 | 从旧状态观察或探索另一条轨迹 | 哪些模型或工具会重新调用，是否允许真实副作用 |

上述 Checkpointers 文档的历史重放会重新执行所选检查点之后的节点，包括相关模型和 API 调用；这不等于只播放日志。[LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)也说明恢复中断会重新运行所在节点，因此中断前的副作用要特别处理。具体重做范围按框架核对，不能推导为所有恢复都从头重跑。

即使把写动作放在审批之后，也仍可能出现“外部提交后、检查点保存前”中断。缩小节点或调整中断位置可以减少某些窗口，不能代替稳定动作标识与结果核实。调试分支应明确使用替身、只读能力还是经[授权](../../glossary/security.md#security.identity)的真实动作，不把更换流程分支 ID 自动解释为新的业务意图。

## 用未决动作解释故障缺口

教学时序：

```text
保存动作意图与 operation_id → 调用外部工具 → 外部提交
                        → 本地尚未保存结果时中断
恢复：读取未决意图 → 检查当前许可 → 查询/幂等核实/人工对账
```

仅看到 prepared，不足以判断工具没有执行；仅看到“工具返回了”也不能证明结果已核实。流程状态可单独记录“停止调度”，动作状态仍可保留 unknown，两者不必被压成同一个成功或失败布尔值。

若本地状态、动作意图和待派送事件能放进一个事务，可以约束这段本地变化；外部系统是否提交仍是另一个边界，见 [Outbox](../messaging/transactional-outbox.md)。状态更新的版本条件也只能保护相应记录，不能自动阻止失去执行权的旧工作者写远程系统。

旧工作者能否被业务资源拒绝，继续读[租约与 Fencing](../distributed/leases-heartbeats-and-fencing.md)。它区分持有资格和资源端隔离生效点，属于来源核查与教学设计，没有新增编排[并发](../../glossary/systems.md#systems.concurrency)恢复实测。

## 旧状态恢复前先检查兼容性与当前条件

教学恢复入口可按以下顺序审查：定位正确任务和获准读取的状态 → 校验流程/结构版本及迁移规则 → 协调当前执行权与状态版本 → 恢复当前预算 → 复查授权、审批与业务前提 → 核实未决动作 → 继续允许的调度。

更改了节点名称、状态字段、[路由](../../glossary/ai.md#ai.planning)规则或工具版本后，旧状态可能不再能直接解释。可设计兼容迁移、固定旧版本运行环境或明确拒绝恢复；字段能解析不表示含义仍相同。状态修订也应留来源与版本，避免人工改一个值就无依据地宣布外部动作已成功。

checkpoint 中的旧权限只是历史材料，当前身份已撤销时不能复用旧许可。历史快照中的“剩余 10 次”也不能覆盖权威预算账本已经消耗的次数；回到旧进度不应顺带获得新的资源额度。需要新增预算时，走明确授权并关联原任务。

## 用反例检查恢复设计

| 反例 | 应提出的问题 |
| --- | --- |
| 两个工作者同时恢复同一任务 | 谁能提交下一状态？旧执行者的外部写入怎样被约束？ |
| 状态保存成功但只有内存副本 | 进程退出后还存在什么可恢复证据？ |
| 重放旧节点再次发送通知 | 是复现计算还是允许新的业务动作？怎样防重复？ |
| 流程升级后复用旧 JSON | 状态结构与业务含义都兼容吗？ |
| 工具结果未知却把流程标为失败 | 未决效果是否仍需查询、对账或人工处理？ |

自检：恢复点之前保存过“调用意图”，为什么不能安全地直接创建？为什么“中断后从节点开头再运行”不等于“整个流程必须重跑”？检查点和业务幂等键分别保护哪一段？

核查日期：2026-10-20。框架保存与重放行为依据上述 LangGraph 官方资料；字段清单、恢复顺序及反例为教学设计，没有安装或运行该 SDK，也没有新增进程中断、迁移或并发恢复实验。[既有工具边界实验](tool-execution-boundaries-lab.md)只覆盖本地受控异常后重开数据库的局部查询恢复；[可恢复 Runtime](recoverable-runtime.md)继续保持[设计提案](../../glossary/engineering.md#engineering.design-docs)。预算如何跨恢复约束调度，见[持久化预算与失败收敛](durable-budgets-and-failure-convergence.md)。
