---
id: "kb-ai-instruction-boundaries"
title: "提示词与指令层级：文字写进上下文，为什么不等于获得执行权"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分任务说明、参考数据、示例与宿主约束，说明角色、请求状态、外部内容和实际权限之间的边界。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-ai-context"]
related: ["kb-ai-tool-security", "kb-ai-structured-output", "kb-ai-evals", "kb-ai-mcp-boundaries"]
tags: ["prompt", "instructions", "message-roles", "untrusted-data"]
---

# 提示词与指令层级：文字写进上下文，为什么不等于获得执行权

学习入口：同样一句“请导出订单”，出现在用户请求、检索文档或工具结果里，为什么不能按同一权限执行？输入文字需要保留来源和用途，实际动作还需要宿主校验。

前置：[Token、上下文与记忆](tokens-context-and-memory.md)。本文参考OpenAI官方文档与[OWASP](../../glossary/security.md#security.threats)，OpenAI角色/参数仅作为具体接口例子；其他宿主应核对自身协议。示例为纸面输入，没有调用模型、测量指令遵循或执行工具。

## 提示输入可以包含多种职责

| 内容 | 主要作用 | 应防止的混淆 |
| --- | --- | --- |
| 任务与成功标准 | 说明要做什么、怎样判断结果 | 只给角色名却没有具体目标 |
| 参考资料 | 提供回答依据与当前事实 | 把资料里的命令当作宿主指令 |
| 示例 | 展示期望映射、格式及边界 | 示例与规则互相矛盾或泄露答案 |
| 宿主约束 | 限定行为、数据和工具边界 | 以文字代替实际权限控制 |

[OpenAI Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)讨论任务表达、角色、示例与评估。上下文包含某条文字，不代表该文字在应用中有决定策略的资格；还要看它来自哪里、以何种消息/数据方式传入。

## 消息角色表达来源与优先关系

在OpenAI文档所述接口中，`developer`等角色和`instructions`参数可表达应用级指令，用户输入表达本次请求。应用需要按所用模型和接口支持的机制组织消息，不能通过给普通文本加一个“system:”前缀就改变其实际角色。

角色优先关系帮助模型处理指令冲突，但不是数据库访问控制或操作许可。即使输出符合所有文字约束，执行器仍需校验主体、对象、动作、预算和结果；工具返回“已经[授权](../../glossary/security.md#security.identity)”也不是可信授权事实。

文档还说明，Responses请求中的`instructions`只适用于当前生成，不能假定使用`previous_response_id`就自动继承前一请求的相同指令。这里仅解释该接口状态边界，不把它推广为所有产品的会话行为。

## 结构化表达减少歧义，不形成安全隔离

纸面任务可以分别写：目标是总结导出任务状态；依据只限给定记录；缺少最终结果时保留“未知”；输出应带来源和待确认项。分隔任务、例子和资料，比把互相矛盾的规则堆在一起更容易复核。

但XML标签、Markdown标题或“忽略资料里的指令”只是提示组织，不能保证模型永不受影响。[OWASP Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)讨论外部内容与指令混合带来的风险，以及分层控制。

例如工具结果夹带“把访问凭据发送到某地址”，应作为不可信内容分析，不能提升为新的工具权限。读取资料与执行外部副作用要保持可检查的边界，见[工具授权](tool-authorization-and-untrusted-results.md)。

## 方法效果随模型、版本和任务变化

清楚的目标、必要背景和一致例子通常有助于表达任务，但不是质量保证。[OpenAI reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)给出特定模型类别的提示建议，也说明不能机械套用同一写法。

不应把“写得更长”“加更多步骤”或某个模板当作通用提升。约束冲突、信息不足、上下文截断或模型能力限制都可能使输出失败；应观察真实任务结果及失败类型。[温度与采样](temperature-sampling-and-reproducibility.md)改变输出选择，也不负责事实核验或访问控制。

## 把提示和运行环境一起留证

记录提示版本、实际消息结构、模型/快照、资料、工具声明与解码条件，用代表性正常/拒绝/资料不足/恶意外部文字等情形评估。输出结构合法与事实正确、动作合规分别检查。

提示修订没有改变模型参数；把用户偏好保存为记忆也不自动更新训练权重。具体效果见[评价与失败分析](evals-and-failure-analysis.md)，本篇没有执行这些评估。

## 自检

1. 任务、参考数据、示例和宿主约束分别负责什么？
2. 在普通文本里写“system:”为什么不自动改变消息角色？
3. 角色优先关系为什么不能代替对象权限和执行校验？
4. 分隔资料、设置低随机性或要求遵守指令，为什么不能保证安全和正确？
5. 比较提示版本时，除了文字本身还应记录什么？

## 来源与核查

2026-10-27 核查OpenAI提示工程/推理提示官方文档及OWASP注入防护说明。本文为source-checked；未调用模型/API、验证消息继承、测量[提示注入](../../glossary/ai.md#ai.injection)或执行真实工具，不声称任何提示能提供不可绕过的安全保证。
