---
id: "kb-security-sessions-tokens"
title: "认证、会话与令牌：登录状态怎样建立和失效"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分身份认证、Session、Cookie、JWT 与 Bearer，解释凭证验证、过期、刷新和撤销的保证边界。"
created: "2026-10-19"
updated: "2026-10-23"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-security-object-authorization", "kb-networking-https-request", "kb-api-idempotency", "kb-api-contracts-pagination", "kb-security-oauth-oidc", "kb-security-origin-csrf", "kb-security-password-recovery", "kb-security-mfa", "kb-security-service-delegation"]
tags: ["authentication", "sessions", "tokens"]
---

# 认证、会话与令牌：登录状态怎样建立和失效

学习入口：用户已经退出登录，旧令牌为什么仍可能访问 API？前置知识：HTTP 请求、浏览器与服务端、对象权限。本文解释 Web 应用的登录状态及常见令牌模型，使用 [OWASP](../../glossary/security.md#security.threats)、[JWT](../../glossary/security.md#security.tokens) RFC 与 [OIDC](../../glossary/security.md#security.oauth) 的机制说明；不提供可直接投产的登录实现，也不覆盖密码存储、[MFA](../../glossary/security.md#security.mfa)、[账号恢复](../../glossary/security.md#security.account-recovery)及联合登录完整流程。

## 认证的结果怎样进入后续请求

[认证](../../glossary/security.md#security.identity)用于建立请求代表的主体；授权判断主体能否执行当前动作。用户完成登录后，后续请求通常携带[会话](../../glossary/security.md#security.sessions)标识或令牌，服务端根据约定验证它，才构造可信主体。客户端传来的 user_id、界面中显示的用户名、能解码的令牌，都不能单独完成这一过程。[OWASP Authentication 指南](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)说明了身份验证及敏感事件后的重新认证要求。

身份认证也不是永久授权。成员关系、角色和对象状态会变化，需要按策略重新判断，不能把登录时的一份角色清单永远当作当前权限。相关规则见[对象级授权](object-level-authorization.md)。

## Session、Cookie、JWT 与 Bearer 不在同一层

| 概念 | 表达什么 | 不自动保证什么 |
| --- | --- | --- |
| 服务端 Session | 服务端保存会话状态，客户端持有用于查找的标识 | 状态存储[可用性](../../glossary/reliability.md#reliability.availability)、跨节点一致性和撤销传播仍需实现 |
| Cookie | 浏览器保存数据并按规则随请求发送的机制 | 其中的数据不一定是会话 ID，也不自动可信 |
| JWT | 一种承载声明的令牌格式，可签名或加密 | 格式本身不决定传输位置、授权规则或即时撤销 |
| Bearer | 持有凭证即可按其规则使用的访问方式 | 不等于 JWT；不透明字符串也可作为 Bearer 凭证 |

这些选择可以组合：Cookie 可承载不透明会话 ID，也可承载 JWT；Authorization 请求头可传递 Bearer 凭证。不能用“Session 对比 Cookie”或“JWT 对比 [HTTPS](../../glossary/networking.md#networking.tls)”代替完整设计。

Bearer 的持有者使用模型见 [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750.html)。签名 JWT 常使用 JWS 表示，JWK 则是密钥的 JSON 表示；拿到一份 JWK 不等于确认它来自可信签发者，验证方仍需约束密钥来源和使用方式。JWK 格式见 [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html)。

常见的签名 JWT 载荷可以被读取，签名主要用于验证完整性与来源，不提供载荷保密性；JWT 也存在加密表示，不能一概称为明文或加密。格式与声明定义见 [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html)。凭证仍须妥善保护和传输，不能因为“已签名”就随意放入 URL、日志或公开页面。

## 服务端会话的生命周期

不透明会话标识应不可预测，具体生成与管理优先使用成熟框架。服务端保存身份、创建时间、有效期与失效状态等信息；每次受保护请求按会话策略确认状态。登录或权限提升后更新会话标识，可以降低旧标识被固定并继续使用的风险。[OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)说明了会话标识、更新与服务端失效管理。

教学流程如下，不代表已经实现了[并发](../../glossary/systems.md#systems.concurrency)控制或会话存储：

```text
验证登录凭据 → 建立新会话并更新标识 → 客户端保存约定的凭证
受保护请求 → 服务端确认会话有效 → 构造主体 → 执行当前授权
退出或撤销 → 服务端使相应会话失效 → 客户端清除对应凭证
```

只清浏览器 Cookie 不会抹去攻击者保存的副本。服务端若仍接受原标识，它仍可能有效；反过来，服务端失效也要考虑多实例缓存及传播。空闲[超时](../../glossary/api.md#api.retries)限制长期无活动的会话，绝对有效期限制总生命周期，均需由服务端执行。已经开始的操作是否中止，属于另一个并发与业务边界，不能由“已退出”自动推导。

## 接受 JWT 需要验证协议约定

解码只让程序读到字段，不证明令牌来自可信签发者。应用应预先确定可接受的令牌用途、签发者、受众、算法与密钥来源，并按协议验证签名及声明。[RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html)讨论了算法验证、签发者与受众检查，避免不同用途的令牌相互替代。

以一个教学资源 API 为例，其契约要求签名[访问令牌](../../glossary/security.md#security.token-lifecycle)包含预期的 iss、aud、sub 与 exp；还要验证适用的时间约束，如存在的 nbf。这里是应用的接受条件，不是声称 JWT 标准要求所有令牌都携带这些字段。时钟容差应有明确上限，不能把“兼容时钟误差”变成忽略过期。

| 输入或现象 | 为什么不能直接接受 |
| --- | --- |
| 签名有效，但 aud 是另一个 API | 不能证明它是发给当前资源的凭证 |
| 载荷里写着 admin，但未完成验证 | 客户端可以自行构造可解码数据 |
| 未过期，但用户已被停用 | 还需符合账号状态与撤销生效策略 |
| 拿登录用的 ID Token 调资源 API | 令牌用途、接收方与验证规则不同，不能因格式相似混用 |

OAuth 2.0 主要描述委托授权，OIDC 在其上增加身份层；ID Token 用于客户端核实登录相关身份信息，Access Token 用于访问受保护资源。具体用途见 [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)。接入第三方登录还需验证协议流程中的关联与重放防护，本文不把“拿到一个 JWT”当作完成 OIDC。

<a id="session-revocation"></a>

## 到期、刷新与撤销是三件事

到期是凭证在约定时间后不再被接受；刷新是在符合条件时取得新凭证；撤销是主动终止某些凭证或会话的继续使用。三者不能互相替代。仅验证签名和时间的自包含访问令牌，验证方可能在它到期前继续接受它，即使客户端已退出。

缩短访问令牌有效期能缩短部分暴露窗口，但仍需明确窗口是否满足需求。若要求更快撤销，可引入会话状态、版本、拒绝列表或在线检查等机制，同时承担存储、可用性与传播成本。权限缓存的有效期也会影响真实生效时间。

OAuth 中的刷新令牌由授权服务器处理，不是给资源 API 使用的访问令牌。刷新过程自身需要泄露与重放防护；轮换及重用检测有相应协议与并发约束，不能简单地永久复用同一个字符串。[RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.14)说明了相关保护与适用条件。退出时撤销刷新能力，也不自动使已签发的所有访问令牌立即失效。

## Cookie 属性与请求来源的边界

Secure 用于限制 Cookie 经安全传输发送；HttpOnly 限制脚本通过相应接口读取它；SameSite 约束部分跨站请求中的自动携带行为。属性含义见 [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)。还需按应用选择发送范围与过期策略，不能把浏览器保存期限当作唯一服务端有效期。

HttpOnly 不会阻止已执行的恶意同源脚本代表用户发请求。浏览器自动带上 Cookie 的便利，也意味着改变状态的操作需要考虑 [CSRF](../../glossary/security.md#security.web-attacks)；SameSite 应结合实际站点边界、请求方式与其他防护判断，不能一律替代 CSRF Token 或来源校验。详见 [OWASP CSRF 防护指南](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。换成 JWT 格式不会自动消除这些请求机制带来的风险。

口令如何存储、恢复证明如何建立以及泄露后的会话处置，见[密码存储与账号恢复](password-storage-and-account-recovery.md)；恢复入口同样属于身份边界。

多因子、挑战绑定、认证器恢复与升阶，继续见[MFA](multi-factor-authentication-passkeys-and-recovery.md)；向下一跳服务传递主体、执行者和访问范围，见[跨服务委托](service-delegation-token-exchange-and-audience.md)。认证时间、令牌签发时间和当前对象权限分别检查。

## 自检与验证范围

为一个受保护 API 画出：凭证由谁签发、存在哪里、怎样发送、谁验证、什么时候拒绝、撤销多久生效、当前对象权限在哪里检查。再分别构造过期、错误受众、退出后重用、权限撤销和跨站请求，先写预期再做集成验证。

试着解释：Cookie 为什么能装 JWT，却不能替代签名验证？退出后撤销刷新令牌，为什么旧访问令牌可能仍能用？HttpOnly 为什么不能保证 XSS 无法代表用户操作？

核查日期：2026-10-19。本文仅核查 OWASP、IETF、OIDC 与 Cookie 文档中的机制，没有实现认证服务器、签名验证、刷新轮换、CSRF 或多节点撤销实验。既有对象授权实验中的 Principal 仍是[测试替身](../../glossary/engineering.md#engineering.doubles)，不包含这些保证。

- [对象级授权](object-level-authorization.md)：有效身份之后仍要检查动作与对象关系。
- [HTTPS 请求链路](../networking/https-request-lifecycle.md)：安全传输与应用身份验证承担不同职责。
- [幂等性](../api/idempotency.md)：重放业务结果仍需当前身份与授权。
- [HTTP 契约与分页](../api/contracts-and-pagination.md)：把身份、错误和列表范围写入调用契约。

- [OAuth 与 OIDC](oauth-oidc-and-pkce.md)：继续解释授权码、PKCE 与回调交易关联，未实现提供方集成。
- [同源、CORS 与 CSRF](origins-cors-and-csrf.md)：展开[跨源](../../glossary/security.md#security.origin)读取、自动凭证和跨站状态修改的边界。
