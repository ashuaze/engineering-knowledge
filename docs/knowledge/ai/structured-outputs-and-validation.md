---
id: "kb-ai-structured-output"
title: "结构化输出与校验：合法 JSON 为什么仍不能直接执行"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分解析、Schema、业务条件、授权与结果事实，处理拒绝、不完整输出和格式修复的边界。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-ai-tool-contracts", "kb-ai-tool-security", "kb-ai-tools-lab", "kb-ai-evals", "kb-api-contracts-pagination"]
tags: ["structured-output", "json-schema", "validation", "tool-calling"]
---

# 结构化输出与校验：合法 JSON 为什么仍不能直接执行

学习入口：参数已经能解析，字段也齐全，为什么还要拒绝执行？前置：JSON 对象、类型和[接口契约](../../glossary/api.md#api.contracts)。结构正确回答“长什么样”，业务与[授权](../../glossary/security.md#security.identity)回答“在当前状态下能否这样做”，结果核实回答“究竟发生了什么”。这些判断不能由一个格式保证替代。

## 逐层增加约束，逐层说明证据

| 层次 | 检查示例 | 通过后仍可能失败 |
| --- | --- | --- |
| 输出状态与完整性 | 是完整候选，还是拒绝、截断或中途片段 | 完整候选仍可内容错误 |
| 解析 | 字节能否解析为预期 JSON 值 | 类型、字段与业务含义未确认 |
| Schema / 本地结构 | 字段、类型、枚举与长度 | 对象可能不存在或属于别的租户 |
| 业务条件 | 项目仍开放，版本和数量适用 | 当前用户可能没有写入权 |
| 授权与必要审批 | 当前主体被允许执行这个具体动作 | 远端执行仍可能失败或结果未知 |
| 结果核实 | 状态与记录对应本动作 | 不能顺带证明其他动作或未来状态 |

[OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)区分 JSON 格式保证和按指定 Schema 约束输出，并说明支持的 Schema 范围与拒绝、不完整等例外。这里不把某个产品的成功输出保证扩大为“所有响应必定有可执行参数”，也不把它当作事实或授权保证。

## Schema 应表达什么

以下是教学形状示意，不是完整 API 请求体，也没有提交给模型服务：

```json
{
  "type": "object",
  "properties": {
    "project_id": {"type": "string"},
    "title": {"type": "string", "minLength": 1, "maxLength": 80},
    "priority": {"type": "string", "enum": ["low", "normal"]}
  },
  "required": ["project_id", "title", "priority"],
  "additionalProperties": false
}
```

显式字段与枚举缩小解释空间，additionalProperties=false 可以拒绝模型额外补出的身份或审批字段。但 project_id="p2" 完全可能符合结构，同时属于其他租户；格式校验无法代替权威数据和当前身份。

OpenAI 函数工具的[严格模式说明](https://developers.openai.com/api/docs/guides/function-calling#strict-mode)还要求对象的额外字段规则和 required 字段满足其约束，可空值也需显式建模。其他提供方、接口或模型支持的子集要分别核对，不能把一般 [JSON Schema](../../glossary/ai.md#ai.structured) 和某个服务的 strict 参数视作同一规范。本文不依赖未显式设置时的默认行为。

## 完整、拒绝和不完整要分支处理

流式输出的一个片段不是完整参数。应按协议组合完成并判断终态后，再交给[运行时](../../glossary/runtime.md#runtime.virtual-machine)准入；不能看到半截 `{"project_id":` 就开始写入。发生拒绝、达到输出限制或传输中断时，要保留对应状态，而不是补上括号后当作普通成功候选。

具体服务可能为拒绝和不完整提供不同字段或事件，需按实际接口读取。拒绝不是需要无限修复的“JSON 错误”；网络中断后也不能只靠剩余文本判断工具是否执行过。

## 解析器的宽容也需要约定

数字字符串、布尔值、重复键、非标准数值和额外字段可能在不同解析器中被不同处理。接纳前应明确定义是否转换、怎样报错及大小限制，不要在未知来源输入上默默修正。

[本地实验](tool-execution-boundaries-lab.md)使用限定字段的显式 Python 校验，拒绝重复键、额外身份字段、错误类型和不完整 JSON，并设置输入大小与标题范围。它不是完整 JSON Schema 验证器，也没有测试模型服务的约束生成；手写规则与契约变化仍需要一起维护。

## 校验失败后怎样继续

可修正的候选可以返回明确的字段错误，在总预算内重新生成或由用户补充。修正后参数若改变了对象、动作或其他审批范围，应重新计算绑定并检查授权；不能沿用原来的“已批准”标记。

[重试](../../glossary/api.md#api.retries)和修复还要区分发生在执行前还是执行后。[输入校验](../../glossary/api.md#api.validation)失败且从未调度，可以明确没有本次工具效果；工具返回不符合输出契约时，副作用却可能已经发生，应进入未知结果处理。不能把“输出解析失败”统一解释为“执行没有成功”。

## 格式正确的结果仍需依据

教学反例：工具返回 `status=succeeded, ticket_id=999999`，类型完全正确，但该 ID 不是这次操作创建的工单。应按可信操作标识核对工具支持的权威记录，区分错误关联、旧结果和未完成任务。本地实验验证了这种“错误回执先未知、再查询确认”的路径。

评价时将解析通过、结构通过、业务通过、授权通过、已核实结果分别计数。对输出“看起来规范”的抽样，不能只评分 JSON 格式后声称工具执行可靠，详见[Evals](evals-and-failure-analysis.md)。

自检：additionalProperties=false 为什么不能阻止一个合法字符串携带诱导指令？输入校验失败与执行后回执校验失败，为什么需要不同恢复分支？

核查日期：2026-10-19。结构化生成、严格模式与边界状态依据所链官方文档；分层表、业务反例与解析策略为教学综合。没有调用模型或测量格式成功率，局部校验与效果证据见独立实验页。
