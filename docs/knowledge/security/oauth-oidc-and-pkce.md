---
id: "kb-security-oauth-oidc"
title: "OAuth 与 OIDC：一次登录怎样绑定授权、身份和回调"
kind: "concept"
domain: "security"
status: "evolving"
summary: "沿授权码与 PKCE 流程区分客户端、授权服务器和资源 API，解释 state、nonce、令牌用途与账号绑定的边界。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-security-sessions-tokens", "kb-networking-https-request"]
related: ["kb-security-origin-csrf", "kb-security-object-authorization", "kb-api-contracts-pagination", "kb-security-service-delegation"]
tags: ["oauth", "oidc", "pkce", "identity"]
---

# OAuth 与 OIDC：一次登录怎样绑定授权、身份和回调

学习入口：浏览器已经带回 code，为什么仍不能直接认定用户登录成功？前置：[认证、会话与令牌](authentication-sessions-and-tokens.md)、HTTP 重定向和服务端请求。本文沿浏览器参与的[授权](../../glossary/security.md#security.identity)码流程解释关联关系，采用 [OIDC](../../glossary/security.md#security.oauth) Core 1.0 errata set 2、PKCE 和 OAuth 安全最佳实践；流程图与反例是教学推演，未接入真实身份提供方。

## 先确定谁在向谁证明什么

OAuth 2.0 提供委托授权框架，OIDC 在其上增加身份层。获取可访问某个资源的凭证，与确认客户端正在登录哪个用户，是相关但不同的任务。[OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html#Introduction)定义了这一身份层及 ID Token。

| 参与方 | 在教学流程中的责任 |
| --- | --- |
| 用户及浏览器 | 参与交互并传递重定向；浏览器带回的参数仍需验证 |
| 客户端 Client / RP | 发起登录、保存本次交易上下文、验证回调和身份结果，建立自己的[会话](../../glossary/security.md#security.sessions) |
| 授权服务器 / OIDC Provider | 按协议认证用户、处理授权并签发相应结果 |
| 资源服务器 / API | 按[访问令牌](../../glossary/security.md#security.token-lifecycle)的接受规则建立主体，再检查资源和动作权限 |

客户端可以有服务端，也可以是运行在浏览器中的公共客户端。能够保守凭证的服务端客户端，可能需要在令牌端点认证自己；浏览器代码中嵌入的共享字符串不能因此成为保密的 client secret。PKCE 也不替代适用的客户端认证。

## 授权码流程把前端回调与令牌兑换分开

下面选用 Authorization Code + PKCE S256，并同时展示 state 和 nonce 的职责。这是教学组合，不是声称所有 OAuth/OIDC 配置都强制同时使用三者。新接入应按所选协议配置与成熟库实现；[RFC 9700 §2.1.1](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1.1)给出了授权码和 PKCE 的安全要求及建议。

```text
客户端：建立一次登录交易，绑定浏览器上下文和预期提供方
  → 浏览器去授权端点：client_id、redirect_uri、scope=openid …
                        state、nonce、code_challenge、S256
提供方：按协议处理认证与授权
  → 浏览器回到已注册回调：code、state（或错误）
客户端：先匹配交易与预期提供方，再向其令牌端点兑换 code
  → 令牌请求包含 code_verifier，以及该客户端适用的其他参数/认证
客户端：验证令牌响应及 ID Token，随后建立本地登录会话
资源 API：单独验证 Access Token 与当前对象权限
```

交易上下文应包含所选提供方、预期回调、请求参数及有效期，按交易区分，避免两个标签页互相覆盖。回调失败、过期或不属于当前浏览器交易时，应按契约结束该交易；不能把所有回调都交给“最近一次登录”。成功后也要防止再次消费旧交易。

授权码经浏览器返回，令牌请求则发往预期的令牌端点。服务端客户端可在服务端完成兑换；公共客户端的部署约束不同，不能照搬“把 secret 放进前端”的做法。本文不选择具体 [SPA](../../glossary/frontend.md#frontend.spa)、[BFF](../../glossary/frontend.md#frontend.bff) 或服务端会话架构。

## state、nonce 与 PKCE 各绑定一段关系

| 机制 | 关联什么 | 不能据此推导什么 |
| --- | --- | --- |
| state | 将回调关联到发起请求及浏览器交易上下文，并承载受保护的应用状态 | 随便回传同一个常量不能证明关联成立 |
| nonce | 为交易生成足够不可预测的值，将验证后的 ID Token 关联到发起的身份请求；发送后须核对返回声明 | nonce 相同不能替代签发者、受众和令牌完整性验证 |
| PKCE | 授权请求中的 challenge 与兑换时的 verifier 绑定，限制仅凭截获 code 兑换 | 不证明用户是谁，也不使资源 API 自动接受该客户端 |

PKCE 为每次交易生成高熵 code_verifier；S256 将其经 SHA-256 与规定的 Base64url 编码得到 code_challenge。授权服务器绑定 challenge 与授权码，兑换时验证 verifier。算法与编码规则见 [RFC 7636 §4](https://www.rfc-editor.org/rfc/rfc7636.html#section-4)，不能用普通 Base64 或自行发明的可逆编码替代。

这些机制的保护有交集。RFC 9700 允许在满足条件时依赖 PKCE 或 OIDC nonce 提供相应 [CSRF](../../glossary/security.md#security.web-attacks) 防护；不能把它简化成“有 PKCE 就永远不用检查交易”。还需确认服务端支持并正确执行 PKCE，防止降级，并保护应用 state 的完整性与浏览器关联。详见 [RFC 9700 §4.7–4.8](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.7)。nonce 的返回验证见 [OIDC ID Token Validation](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)。

## 回调地址、提供方和令牌用途不能靠猜

注册回调限制结果被送往哪里；请求关联限制结果属于哪次交易；提供方验证限制结果来自谁。三者不能只做其中一个。以 Web 客户端为例，应按协议对已注册 redirect_uri 精确匹配，避免字符串前缀判断；原生应用回环地址等有专门例外，不应自行放宽。依据见 [RFC 9700 §4.1.3](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.1.3)。

同时接入多个提供方时，客户端需绑定预期签发者和端点，并采用协议规定的混淆攻击防护，例如按所选协议验证授权响应的签发者标识，或采用符合要求的不同回调地址。仅保存预期 issuer 并不能鉴别实际响应；也不能因回调参数或未验证令牌写了某个 issuer，就临时向该地址取密钥并接受它。相关机制见 [RFC 9700 §4.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.4)。

ID Token 面向客户端的身份验证。客户端需要按所选流程核对签发者、受众、有效期、nonce（若发送）及适用的完整性和其他声明要求；使用受信任配置和合适的库，不能只解码 [JWT](../../glossary/security.md#security.tokens)。Access Token 面向受保护资源，可能是不透明字符串，资源 API 有自己的验证契约。ID Token 的受众必须包含当前客户端，并满足适用的其他受众声明检查；这不说明它可作为任意 API 的访问凭证。验证规则见 [OIDC Core §3.1.3](https://openid.net/specs/openid-connect-core-1_0.html#TokenEndpoint)。

## 外部身份怎样映射到本地账号

OIDC 中，验证后的 issuer 与 sub 组合提供身份标识；sub 的作用域和 pairwise 规则需要纳入设计。email 等展示或联系信息不能自动当作跨提供方的稳定账号主键。稳定标识说明见 [OIDC Core §5.7](https://openid.net/specs/openid-connect-core-1_0.html#ClaimStability)。

教学反例：本地账号以“提供方 A + sub 17”绑定。提供方 B 返回相同 email，不足以自动把它绑定到该账号；否则账号合并策略可能越过原有身份验证。安全的账号绑定与合并需要单独的证明和交互策略，本文未实现这套策略。

建立本地会话后，失效、刷新、退出和对象授权仍需各自执行。第三方登录成功不会赋予本地管理员权限，也不证明某项资源操作当前被允许。继续阅读[会话生命周期](authentication-sessions-and-tokens.md)与[对象级授权](object-level-authorization.md)。

## 用失败情形检查流程是否闭合

| 教学输入 | 应解释的拒绝或处理依据 |
| --- | --- |
| 交易甲收到交易乙的 code/state | 按交易与浏览器关联检查，不能交换登录结果 |
| code 被截获，但缺少对应 verifier | 正确执行的 PKCE 应阻止单凭该 code 兑换 |
| 签名可验，但 issuer 或 aud 不符合本次契约 | 完整性有效不等于当前客户端可以接受 |
| 同一个回调再次到达 | 不能再次消费已完成交易；还需授权码的单次使用约束 |
| 登录失败携带一个任意 return_url | 错误处理与登录后跳转仍需约束，不能形成开放重定向 |

这些是预期行为，不是测试输出。回调使用浏览器时，还要分别理解[同源、CORS 与 CSRF](origins-cors-and-csrf.md)：重定向、[跨源](../../glossary/security.md#security.origin)读取和自动携带 Cookie 不是同一种权限。

从已建立的用户访问继续调用另一资源，见[跨服务委托](service-delegation-token-exchange-and-audience.md)。授权码交易、ID Token、下一跳访问凭据与令牌交换有不同用途，受众、执行者和权限不能在转发时被省略。

## 自检与验证范围

画出谁保存 verifier、谁验证 nonce、哪个配置决定 issuer 和密钥来源，以及 ID Token 与 Access Token 分别交给谁。再解释：两个标签页怎样区分交易？PKCE 为什么不替代客户端认证？email 相同为什么不足以自动合并账号？

2026-10-20 核查上述规范与安全最佳实践，状态为 source-checked。本文未启动授权服务器，未执行 SDK、签名校验、真实回调、令牌重放、账号合并或退出集成实验；纸面流程不能作为接入安全性证明。[密码存储与账号恢复](password-storage-and-account-recovery.md)、[MFA](multi-factor-authentication-passkeys-and-recovery.md)已有独立概念篇；完整凭证存储、原生应用流程及真实联合登录集成仍需继续补充。
