---
id: "kb-security-service-delegation"
title: "跨服务委托：谁在替谁访问哪个资源"
kind: "concept"
domain: "security"
status: "evolving"
summary: "沿服务调用链区分用户、当前执行者与目标受众，解释令牌交换、权限收窄、发送者约束及认证上下文和撤销传播。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-security-oauth-oidc", "kb-security-mtls-service-identity"]
related: ["kb-security-authorization-models", "kb-security-object-authorization", "kb-security-sessions-tokens", "kb-security-mfa", "kb-security-secret-lifecycle", "kb-api-styles-gateway", "kb-api-idempotency", "kb-messaging-outbox"]
tags: ["delegation", "token-exchange", "audience", "oauth", "identity"]
---

# 跨服务委托：谁在替谁访问哪个资源

学习入口：订单服务已经验证了用户令牌，为什么不能把它直接转交给资料服务？服务间 [mTLS](../../glossary/security.md#security.mtls) 证明了当前连接的[工作负载身份](../../glossary/security.md#security.workload-identity)，却没有自动回答“替谁、为哪个动作、在什么范围内访问”。每一跳都需要与目标资源匹配的权限和可核查的执行者上下文。

前置：[OAuth 与 OIDC](oauth-oidc-and-pkce.md)、[mTLS 与服务身份](mtls-service-identities-and-trust-boundaries.md)。本文以 [OAuth](../../glossary/security.md#security.oauth) Token Exchange 和 [JWT](../../glossary/security.md#security.tokens) [Access Token](../../glossary/security.md#security.token-lifecycle) 的标准机制解释服务端委托，不要求所有系统使用 JWT 或同一种身份产品。令牌、集合、时间线和流程均为纸面教学设计，未配置[授权](../../glossary/security.md#security.identity)服务器、交换令牌或调用真实服务。

## 一条调用链至少有三种不同身份

设应用 A 代表用户 Alice 请求订单服务 B，B 再调用资料服务 C 获取当前订单允许使用的地址。

| 要识别的对象 | 在本例中是谁 | 不能替代什么 |
| --- | --- | --- |
| subject | 本次访问所代表的用户 Alice | 发起当前连接的工作负载身份 |
| actor | 当前替 Alice 执行动作的 B | Alice 是否允许此委托及对象权限 |
| audience | 接受下一跳凭据的资源服务 C | “任何内部服务”或任意同名权限 |
| issuer | 签发相关凭据的受信授权方 | 请求者自报的签发者名称或任意 JWK 地址 |
| 请求上下文 | 租户、目标对象、动作及委托目的 | 一段未验证的 X-User-ID 请求头 |

某个 `sub` 字符串也不是跨所有签发者通用的账号 ID，应在约定的身份命名与映射范围解释。客户端 ID、actor 标识与证书身份是否对应同一服务，也须由注册和验证关系决定，不能按字符串相似直接认定。

服务以自己的应用权限执行任务，可以是合理的另一种契约；但不能把它与用户委托混用。[RFC 6749 §4.4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4)的 Client Credentials 依据客户端本身的凭据及预先约定授权，不会因额外加了一个用户头，就变成该用户当前批准的访问。

## 向哪个资源请求与允许做什么分别表达

假设 T_AB 是授权方签发、只面向 B 的访问令牌。B 接受它后，这个令牌的签名和时间即使仍有效，C 也不能忽略受众不匹配而接受它。[RFC 9700 §2.2.1、§4.10](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.2.1)要求资源服务检查凭据是否面向自己及相应资源/动作。

`resource` 或 `audience` 表达目标资源，`scope` 表达约定的访问范围；[RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html)定义请求中的资源指示，并由授权服务器依据自身政策决定是否接受。请求方填写 C 不代表已经获准，也不要求授权方去抓取这个任意 URL。相同 `read` 字符串在两个 API 上可能含义不同，不能不经过权限语义映射就求交或互换。

如果特定部署明确让同一个令牌面向 B、C，仍须说明它为何具有两种受众及各自可用权限；不能以“它是内部签发的”替代每一跳验证。过宽受众还会扩大泄露后的可用范围。

## 令牌交换是受控地取得下一跳凭据

[RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html)定义向授权方请求交换安全令牌的协议，不自动规定所有部署的信任、权限映射或撤销模型。下面是本篇选择显式保留 subject 与当前 actor 的教学配置，不是完整接口实现：

```text
A → B：提交面向 B 的访问凭据，B 验证请求与当前对象动作
B → 授权方：按部署规则证明自己，提交 subject_token 和下一跳请求
授权方：检查输入用途、主体、B 的代行资格、目标和范围
授权方 → B：返回被允许的下一跳访问凭据及有效期等响应信息
B → C：使用新凭据；C 独立验证并执行当前授权
```

`subject_token` 表达请求所代表的主体上下文；若使用 `actor_token`，它表达执行者身份。提交 actor_token 不自动完成请求客户端的认证，也不证明已被允许代行。授权方可拒绝、缩小范围或采用部署约定的其他处理；请求参数本身不是授予结果。

委托通常需要保留“谁替谁”的区别；impersonation 则让接收方在所授予范围内把执行者视为被代表主体。是否采用这种语义必须有明确政策，不能由服务自己改掉 sub 就完成。若协议要求记录执行者，遗漏 actor 还会破坏审计与后续策略判断。

在 RFC 8693 的 JWT 表示中，`act` 描述当前 actor，可嵌套记录历史；访问控制使用顶层声明与最外层当前 actor，嵌套的先前 actor 是历史信息，不能把链上曾出现的管理员当作当前授权。`may_act` 表示某主体有资格成为执行者，与当前“正在代行”的 act 也不同。它们不是任意输入头，只能在可信令牌及其约定语义中使用。

## 权限收窄需要共同的语义与最终接受点

纸面模型先把所有权限映射到同一资源命名空间，用完整的“租户/文档/动作”元组表示，避免把不同 API 的 scope 字符串混为一谈：

| 教学集合 | 包含的动作 |
| --- | --- |
| 用户可委托范围 U | T1/doc7/read、T1/doc8/read |
| B 被允许代行的范围 D | T1/doc7/read |
| 本次请求范围 R | T1/doc7/read、T2/doc9/read |
| C 当前资源政策范围 P | T1/doc7/read、T2/doc9/read |

在本例选定的求交政策下，`U ∩ D ∩ R ∩ P = {T1/doc7/read}`。用户还可读 doc8，并不等于 B 也能代行；C 支持 T2/doc9/read，也不扩大这次委托。这是用于解释[最小权限](../../glossary/security.md#security.trust)的教学模型，不是 RFC 8693 对所有权限系统规定的算法。

签发阶段的判断与 C 执行时的对象状态仍可能不同。C 需要核对真实对象归属、当前关系、动作及服务上下文，不能只相信请求自报的 tenant，也不能把“STS 已发令牌”当作业务检查完成。规则、事实与接受处的时间差继续见[权限模型与策略传播](authorization-models-policy-distribution-and-revocation.md)和[对象级授权](object-level-authorization.md)。

## 令牌用途、发送者与连接认证各自验证

如果部署选择 [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068.html)的 JWT Access Token profile，C 按该 profile 检查类型、受信 issuer、签名、受众和时间等，再使用约定授权上下文；不能把这个检查表推广成任意 JWT 都采用同一布局。ID Token 用于客户端核实身份，不是这一步的通用资源访问凭据。B 也不能靠自行解码新令牌来代替 C 的验证；客户端应按约定处理令牌响应和访问结果。

发送者约束又是另一层。普通 Bearer 被复制后，持有者可能继续使用；证书绑定令牌还要求资源方检查令牌与实际 [TLS](../../glossary/networking.md#networking.tls) 证明的关联。[RFC 8705](https://www.rfc-editor.org/rfc/rfc8705.html)明确区分 mTLS 客户端认证与证书绑定访问令牌，前者成功不自动完成后者配置。

[RFC 9449 的 DPoP](https://www.rfc-editor.org/rfc/rfc9449.html)在应用层提供与密钥及请求相关的持有证明；服务仍需核对令牌绑定、证明与防重放。DPoP 本身不是授权服务器的客户端认证方法，也不负责决定哪个用户能读哪个对象。绑定给 A 的凭据不会因为 B 拿到它，就自动允许 B 用自己的密钥向 C 证明；下一跳的密钥与令牌绑定必须按交换配置重新安排。

## 较新的令牌不等于较新的用户认证

下游可能要求用户近期完成某种认证。`auth_time` 表达用户认证发生时间，`iat` 表达本次令牌签发时间；`acr` 表达约定的认证上下文类别，`amr` 表达所用方法。这些值需要可信来源、明确含义和验证，不是让用户上传一个 `mfa=true`。

[OIDC Core errata set 2](https://openid.net/specs/openid-connect-core-1_0.html#IDToken)规定相关身份声明；RFC 9068 对访问令牌中的这些字段采用可选声明，不能假定每次交换都存在，更不能靠某个库添加字段就证明实际认证。需要它们的下游应通过所用 profile 明确取得与校验方式。

例如用户 12:00 认证，B 在 12:05 换出新令牌，C 在 12:06 执行要求 300 秒内认证的动作；认证年龄为 360 秒，而不是 60 秒，应按教学政策重新取得合格证明。再次交换或刷新只改变凭据，不自动让用户重新使用认证因子。[MFA](../../glossary/security.md#security.mfa)、恢复与升阶的边界见[MFA](multi-factor-authentication-passkeys-and-recovery.md)。

## 交换之后，期限与撤销不会天然连成一根线

教学签发政策：t=120 秒进行交换，输入凭据于 t=350 到期，请求有效期 300 秒，授权方另限制本次输出最多 180 秒；均按同一可靠时钟，且输入此时仍有效。

```text
输入剩余 = 350 − 120 = 230 秒
本次输出寿命 = min(230, 300, 180) = 180 秒
输出到期 = 120 + 180 = t=300
```

这是本篇选择的期限收窄规则，不是令牌交换协议必然使用的公式。RFC 8693 明确交换通常不会使输入立即失效，也不会自动紧密联动输入与输出；输入后续续期、撤销或被替换，不保证输出同步改变。

假设 t=200 撤销输入，但 C 此后只离线检查尚未到期的输出，且没有收到或查询该撤销状态，旧输出可能仍被接受。要更快停止，需要显式的撤销关联、在线状态或版本/事实要求，并核对缓存和传播；不能仅从“上游退出成功”推出整条链已拒绝。已受理的外部业务还需[幂等与结果核对](../api/idempotency.md)，拒绝下一次请求不等于取消前一次提交。

缓存的下一跳凭据也要按可信主体、当前执行者、租户、目标、权限/密钥绑定及期限划定复用范围。只按服务名缓存会让 Alice、Bob 或不同租户共享错误能力；凭据本身不进入普通日志，审计保留受控的身份关联与决策依据。后台任务不能无限延续用户最初的一次登录；应明确持久任务的执行主体、委托寿命与每次恢复后的检查，可恢复意图与权限寿命仍分别管理，见[Outbox](../messaging/transactional-outbox.md)。

## 五道自检与核查范围

1. A→B→C 中 subject、当前 actor、audience 与 issuer 各是谁？Client Credentials、ID Token、用户头和 mTLS 为什么都不能单独构成这次用户委托？
2. Token Exchange 的请求与最终授予有什么区别？subject_token、actor_token、act、嵌套历史与 may_act 分别能用于什么判断？
3. U/D/R/P 的例子为什么只剩 T1/doc7/read？若两个 API 的 read 含义不同，为什么不能直接求交，C 执行时还要核对什么？
4. JWT profile、证书绑定、DPoP 与 auth_time/iat 各提供什么证据？12:00/12:05/12:06 的例子为何不能用新令牌掩盖旧认证？
5. 230/300/180 秒如何得到 t=300 到期？t=200 输入撤销、缓存复用和后台恢复分别还需什么机制，为什么不能推定已执行业务被取消？

核查日期：2026-10-23。实际读取下列固定版本相关部分，流程、权限交集及计时是教学综合；没有核查某个身份产品或跨服务部署。

| 一手资料 | 实际核查部分 |
| --- | --- |
| [RFC 6749，2012-10](https://www.rfc-editor.org/rfc/rfc6749.html) | §4.4 的客户端自身凭据及预先授权范围；不沿用过时流程安全建议替代后续 BCP |
| [RFC 8693，2020-01](https://www.rfc-editor.org/rfc/rfc8693.html) | §1–2 请求/信任范围、委托/模拟、输入输出生命周期与 §4 的 act/may_act；不假设所有输出都有同一 JWT 布局 |
| [RFC 8707，2020-02](https://www.rfc-editor.org/rfc/rfc8707.html) | resource 目标、scope 关系及授权方政策，不把请求指示当已授予能力 |
| [RFC 9068，2021-10](https://www.rfc-editor.org/rfc/rfc9068.html) | JWT Access Token 类型、主体/受众/验证与可选认证上下文，非通用 JWT 接受规则 |
| [RFC 9700，2025-01](https://www.rfc-editor.org/rfc/rfc9700.html) | §2.2.1/4.10 的受众、资源动作与发送者约束，未做泄露或重放实验 |
| [RFC 8705，2020-02](https://www.rfc-editor.org/rfc/rfc8705.html)、[RFC 9449，2023-09](https://www.rfc-editor.org/rfc/rfc9449.html) | mTLS 客户端认证/令牌绑定的区分；DPoP 的应用层证明、客户端认证与资源授权边界 |
| [OIDC Core 1.0 errata set 2，2023-12-15](https://openid.net/specs/openid-connect-core-1_0.html) | auth_time、iat、acr/amr 的含义与新鲜度；未接入外部提供方 |

未执行令牌签发/交换/验证、密钥绑定、DPoP、认证升阶、权限交集、撤销/缓存、[队列](../../glossary/algorithms.md#algorithms.queues)恢复或业务副作用集成实验；未处理真实令牌、证书或用户数据。没有由规范机制推定线上时延、撤销时限或安全效果。
