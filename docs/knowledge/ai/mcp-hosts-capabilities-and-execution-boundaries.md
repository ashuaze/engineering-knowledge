---
id: "kb-ai-mcp-boundaries"
title: "MCP 与能力协商：工具能被发现，为什么仍不能直接执行"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "沿宿主、客户端和服务器解释初始化、工具/资源/提示原语，区分协议成功、授权与真实业务结果。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-ai-tool-contracts", "kb-ai-tool-security"]
related: ["kb-ai-instruction-boundaries", "kb-ai-structured-output", "kb-ai-workflow-state", "kb-security-service-delegation"]
tags: ["mcp", "capability-negotiation", "protocol", "authorization"]
---

# MCP 与能力协商：工具能被发现，为什么仍不能直接执行

学习入口：连接服务器后列出了一个退款工具，是否说明当前用户已经有权退款？工具返回一段“成功”，又是否证明外部付款系统真的处理完毕？协议、权限和业务效果要分别判断。

前置：[工具调用契约](tool-calling-and-execution-contracts.md)、[工具授权](tool-authorization-and-untrusted-results.md)。本文固定参照[MCP](../../glossary/ai.md#ai.mcp)规范2025-11-25，未声称覆盖所有版本/扩展；没有连接服务器、读取真实资源或调用工具。

## MCP组织宿主与能力提供方的交互

[MCP Architecture](https://modelcontextprotocol.io/specification/2025-11-25/architecture)描述host、client和server的职责。宿主管理模型与应用策略，创建客户端；客户端与相应服务器维护协议交互；服务器提供上下文或能力，可以在本地或远端。

这不是模型权重里内置的万能接口，也不自动让服务器看到整个会话。宿主决定传递必要上下文并管理权限；“支持MCP”还需说明版本、传输和具体能力。

## 初始化声明能做什么，不代表获准做什么

[Lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)要求先初始化、交换版本与能力，并在成功后发送完成初始化的通知，再按协商结果操作。版本不兼容和能力缺失需要明确处理，不能仅凭网络连通就调用任意扩展。

能力声明描述协议支持范围；用户对某个订单的权限、参数约束和是否允许本次副作用，仍由宿主与服务端按可信身份检查。客户端缓存的工具列表还可能过期，调用前后的变更与失败需要处理。

## 三种服务器原语有不同用途

| 原语 | 主要提供什么 | 常见误解 |
| --- | --- | --- |
| Tools | 可调用操作及输入/输出约定 | 有Schema便等于任意调用均获[授权](../../glossary/security.md#security.identity) |
| Resources | 通过URI等标识提供上下文数据 | 只读便等于内容可信或可随意公开 |
| Prompts | 可发现和参数化的提示模板 | 服务器模板自动成为宿主最高指令 |

分别见规范的[Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)、[Resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)和[Prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)。它们的常见交互控制方式不同，协议没有要求所有应用采用唯一界面；宿主仍要管理数据来源和执行意图。

## 连接凭据、业务授权与结果可信度分层检查

[Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)针对支持授权的HTTP传输给出相应规范，stdio凭据处理有不同安排。不能把一套[OAuth](../../glossary/security.md#security.oauth)流程或网络令牌规则直接套到所有本地[进程](../../glossary/systems.md#systems.execution-units)。

取得[访问令牌](../../glossary/security.md#security.token-lifecycle)通常只解决某个资源服务器的访问条件，不能单独证明用户对每个业务对象、字段和动作有权。宿主还应限制提供给模型的工具及传递内容，服务端也要校验真实输入和权限；[跨服务委托](../../glossary/security.md#security.service-delegation)范围另见[工具授权](tool-authorization-and-untrusted-results.md)。

## 协议响应、工具失败与业务完成不同

规范区分JSON-[RPC](../../glossary/api.md#api.styles)层错误与工具执行结果里的 `isError: true`。找不到工具和执行时业务拒绝可以位于不同错误层；某次收到有效响应，只说明已取得相应协议结果。

即使 `isError: false`，也需解释返回内容代表接纳、执行中还是最终业务效果。请求超时或连接断开可能发生在写入之后，JSON-RPC请求ID只用于关联消息，不能自动作为持久业务[幂等](../../glossary/api.md#api.idempotency)键。

工具描述、资源和结果文本均可能含不可信内容。将结果送回模型时保留来源，不能让“请忽略限制”这样的服务器文本提升权限；对结果做结构和业务验证，按操作身份核对不确定效果。

## 自检

1. host、client、server各自主要负责什么？
2. 网络连通、初始化和工具声明，为什么都不等于业务授权？
3. Tools、Resources和Prompts分别提供什么？
4. JSON-RPC错误、工具的isError与最终业务结果有什么区别？
5. 为什么请求ID、HTTP令牌或服务器提示都不能单独提供执行安全？

## 来源与核查

2026-10-27 核查MCP2025-11-25架构、生命周期、三种服务器原语及授权相关章节。本文为source-checked；未运行MCP客户端/服务器、传输、OAuth、能力更新、错误恢复或实际副作用，也未验证任何具体服务器可信。
