---
id: "kb-security-trust-threat-models"
title: "信任边界与威胁建模：内网请求为什么仍需验证"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分资产、身份、信任假设与执行点，用威胁场景说明最小权限、零信任、缓解措施和验证证据。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-security-object-authorization", "kb-security-mtls-service-identity"]
related: ["kb-security-authorization-models", "kb-api-resource-validation", "kb-devops-cloud-network", "kb-devops-trusted-progressive-delivery"]
tags: ["trust-boundary", "least-privilege", "zero-trust", "threat-modeling"]
---

# 信任边界与威胁建模：内网请求为什么仍需验证

学习入口：请求来自公司网络、服务证书也有效，为什么仍不能允许它读取任意订单？需要把网络位置、调用身份、当前动作和资源权限分别证明，再检查这些证明在哪里被执行。

前置：[对象级授权](object-level-authorization.md)、[mTLS 与服务身份](mtls-service-identities-and-trust-boundaries.md)。本文参考 NIST SP 800-207 与 [OWASP](../../glossary/security.md#security.threats) 官方方法，限定概念分析；教学系统、威胁和措施均未部署或攻击验证，不声称完成一次组织级安全评估。

## 信任边界是需要重新核对假设的地方

资产不只有秘密，也包括订单完整性、可用容量、凭证与审计证据。边界可能位于浏览器到 API、服务到数据库、构建系统到制品库，也可能存在于同一网络甚至同一[进程](../../glossary/systems.md#systems.execution-units)内的不同权限主体之间。

| 现有事实 | 支持的判断 | 仍需判断 |
| --- | --- | --- |
| 来源属于内部地址段 | 请求来自某条网络路径 | 实际主体及其当前权限 |
| [mTLS](../../glossary/security.md#security.mtls) 校验通过 | 对端满足所用证书与身份验证条件 | 能否执行当前对象动作 |
| 网关已检查登录 | 入口做过某项校验 | 是否存在旁路，下游能否可信绑定该身份 |
| 已通过一次[授权](../../glossary/security.md#security.identity) | 当时的条件允许该动作 | 后续条件变化、撤销与不同资源的权限 |

[NIST SP 800-207](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)强调不因网络位置或资产归属就授予隐含信任。[零信任](../../glossary/security.md#security.trust)不是一个产品名称，也不意味着每个字节都重新要求用户登录；它要求明确资源访问条件、验证与执行位置，并处理条件变化。

## 最小权限需要动作、对象、范围和期限

最小权限不是“给一个只读角色”便结束。只读全部租户仍可能超出目的；能够写一张表，也可能绕过业务状态转换。应按主体需要限定对象集合、允许动作、字段/数据范围以及持续时间；默认拒绝和每次请求检查的原则见 [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)。

教学例：报表任务只需读取租户 T 的已结算订单。它不应因拥有服务身份就获得退款、修改支付信息或读取其他租户的能力。执行点应使用可信身份与资源事实，不能直接把客户端给出的 `tenant_id=T` 当作权限证明。

分发策略和缓存事实可能带来撤销[延迟](../../glossary/performance.md#performance.latency-throughput)。决定点说“拒绝”之后，旧连接、旧令牌或旧结果是否仍可用要分别处理，见[权限传播](authorization-models-policy-distribution-and-revocation.md)。

## 威胁模型从系统与目标出发

[OWASP Threat Modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)围绕系统模型、可能出错的情形、缓解与复核组织分析。数据流图、STRIDE 等方法用于提出问题，不是填满分类表就证明没有遗漏。

以下是自拟的报表下载场景：

| 要素 | 本例记录 |
| --- | --- |
| 资产与预期行为 | T 的报表仅对当前有权限的主体可见 |
| 数据流与边界 | 浏览器提交任务 → API 保存范围 → 后台生成 → [对象存储](../../glossary/cache-search.md#cache-search.objects)下载 |
| 威胁路径 | 调用者更改对象标识；后台丢失租户范围；下载凭据在撤权后继续有效 |
| 缓解假设 | 服务端绑定主体范围、后台继承可信上下文、下载访问有明确权限和寿命 |
| 待验证证据 | 跨租户请求、后台恢复、凭据到期/撤销及旁路请求的实际结果 |

同一个威胁可以需要多层措施；一个措施也可能引入新的故障，例如授权依赖不可用时如何收敛。应写出条件、影响、负责人和待补证据，而不是只写“加密”“上 [WAF](../../glossary/networking.md#networking.cdn-waf)”或“使用零信任”。

## 控制存在、部署生效与覆盖场景分开验收

代码有鉴权函数，不证明所有入口都调用；策略配置已提交，不证明所有副本已生效；某次越权被拒绝，不证明所有对象类型、后台任务和恢复路径都安全。

复核应连接具体威胁与证据：检查什么输入、以什么主体执行、预期在哪个边界被拒绝、错误时是否泄露数据。用结构化记录保留剩余风险和假设；系统增加数据流、身份提供方、缓存或供应链入口后，应重评相关部分。本文没有执行这些检查。

## 自检

1. 内网地址、有效服务证书和对象权限分别证明什么？
2. 报表任务的最小权限为何不能只写“只读”？
3. 威胁路径、缓解措施和验证证据有何区别？
4. 网关已鉴权，为什么仍要检查后台任务、旁路与身份上下文？
5. 配置中存在某项防护，为何不等于所有部署和恢复路径均受保护？

## 来源与核查

2026-10-26 核查 NIST SP 800-207 的信任与访问原则，以及 OWASP 的授权和威胁建模说明。本文为 source-checked 概念文章；未验证网络/身份策略、实施渗透测试或证明完整威胁覆盖，设备[会话](../../glossary/security.md#security.sessions)和具体执行系统仍需独立深入。
