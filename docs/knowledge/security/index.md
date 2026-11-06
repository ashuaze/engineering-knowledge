<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 身份、安全与权限

建议优先级：P0。目标：以信任边界、身份和[最小权限](../../glossary/security.md#security.trust)设计系统。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

已登录用户为何仍不能直接访问任意租户数据？

## 已有正文

- [认证、会话与令牌：登录状态怎样建立和失效](authentication-sessions-and-tokens.md)：区分身份[认证](../../glossary/security.md#security.identity)、Session、[Cookie](../../glossary/security.md#security.sessions)、[JWT](../../glossary/security.md#security.tokens) 与 Bearer，解释凭证验证、过期、刷新和撤销的保证边界。
- [权限模型与策略传播：规则改了，哪些请求仍可能被允许](authorization-models-policy-distribution-and-revocation.md)：区分角色、属性与关系模型，沿策略、事实、缓存和执行边界解释授权决定及撤销何时真正生效。
- [mTLS 与服务身份：双向验证为何仍需授权边界](mtls-service-identities-and-trust-boundaries.md)：区分证书链、预期身份与私钥证明，解释工作负载授权、代理逐跳和证书轮换的信任边界。
- [MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度](multi-factor-authentication-passkeys-and-recovery.md)：区分认证因子、OTP、WebAuthn 与会话保证，解释挑战绑定、认证器注册、替换恢复和敏感操作重新认证。
- [OAuth 与 OIDC：一次登录怎样绑定授权、身份和回调](oauth-oidc-and-pkce.md)：沿授权码与 [PKCE](../../glossary/security.md#security.oauth) 流程区分客户端、授权服务器和资源 API，解释 state、nonce、令牌用途与账号绑定的边界。
- [对象级授权：已登录为何仍不能访问这份数据](object-level-authorization.md)：将主体、动作、对象和租户关系写成可验证的访问规则，覆盖详情、列表和写入。
- [同源、CORS 与 CSRF：请求发得出为什么仍读不到响应](origins-cors-and-csrf.md)：区分 origin 与 site、[跨源](../../glossary/security.md#security.origin)读取与发送、CORS 预检和自动凭证，说明 [CSRF](../../glossary/security.md#security.web-attacks) 与 Cookie 属性的防护边界。
- [密码存储与账号恢复：改了密码，为什么还没夺回账号](password-storage-and-account-recovery.md)：区分密码派生、盐和 [pepper](../../glossary/security.md#security.pepper) 的保护范围，沿成本迁移、恢复证明与旧[会话撤销](../../glossary/security.md#security.revocation)解释账号控制权怎样恢复。
- [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](secrets-credentials-rotation-and-revocation.md)：沿生成、分发、使用、轮换、撤销和销毁区分秘密版本、验证方接受范围与历史数据恢复责任。
- [跨服务委托：谁在替谁访问哪个资源](service-delegation-token-exchange-and-audience.md)：沿服务调用链区分用户、当前执行者与目标受众，解释令牌交换、权限收窄、发送者约束及认证上下文和撤销传播。
- [SQL 注入与参数化查询：值怎样与查询结构分开](sql-injection-parameters-and-query-structure.md)：区分绑定值、受控查询结构与对象权限，用 Psycopg 教学例解释动态排序、模式与列表语义、二次注入，以及预处理和计划复用的范围。
- [SSRF：服务端代发请求怎样守住网络出口](ssrf-url-resolution-and-egress-boundaries.md)：沿 URL 解析、[DNS](../../glossary/networking.md#networking.dns) 候选地址、实际连接、重定向与代理出口解释 SSRF，说明允许列表、凭据隔离、元数据保护和响应限额的边界。
- [信任边界与威胁建模：内网请求为什么仍需验证](trust-boundaries-least-privilege-and-threat-modeling.md)：区分资产、身份、信任假设与执行点，用威胁场景说明最小权限、零信任、缓解措施和验证证据。
- [XSS：不可信数据何时变成浏览器代码](xss-contexts-sinks-and-browser-defenses.md)：沿数据源、危险汇与解析上下文解释 XSS，区分输出编码、HTML [净化](../../glossary/api.md#api.validation)、安全 [DOM](../../glossary/frontend.md#frontend.render-tree) API、[Trusted Types](../../glossary/security.md#security.trusted-types) 和 CSP 的防护职责。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Authentication / Authorization](../../glossary/security.md#security.identity) | 证明身份与判断访问权。 |
| [Session / Cookie](../../glossary/security.md#security.sessions) | 会话状态和浏览器保存、发送的数据。 |
| [OAuth 2.0 / OpenID Connect](../../glossary/security.md#security.oauth) | 委托授权框架与其上的身份层。 |
| [JWT / JWS / JWK](../../glossary/security.md#security.tokens) | 声明容器、签名格式和密钥表示。 |
| [RBAC / ABAC](../../glossary/security.md#security.access-control) | 通过角色分配或主体、对象、动作与环境属性表达访问规则。 |
| [Access Token / Refresh Token](../../glossary/security.md#security.token-lifecycle) | 访问凭据和更新访问凭据的机制。 |
| [CORS / Same-Origin Policy](../../glossary/security.md#security.origin) | 浏览器同源边界与跨源响应访问机制。 |
| [XSS / CSRF / SSRF](../../glossary/security.md#security.web-attacks) | 脚本注入、跨站请求伪造和服务端请求伪造。 |
| [SQL Injection / Parameterized Query](../../glossary/security.md#security.sql-injection) | 查询结构注入与参数绑定防护。 |
| [Hash / Salt / KDF](../../glossary/security.md#security.passwords) | 哈希、随机盐和适合口令的派生机制。 |
| [mTLS / Certificate](../../glossary/security.md#security.mtls) | [TLS](../../glossary/networking.md#networking.tls) 连接双方按约定使用证书及对应私钥证明建立对端身份。 |
| [Secrets Management](../../glossary/security.md#security.secrets) | 敏感凭据的保存、分发与轮换。 |
| [Least Privilege / Zero Trust](../../glossary/security.md#security.trust) | 最小授权和持续验证访问条件。 |
| [Threat Modeling / OWASP](../../glossary/security.md#security.threats) | 识别攻击面并参考应用安全研究与规范。 |
| [Tenant Isolation / Object-level Authorization](../../glossary/security.md#security.tenant-isolation) | 租户边界与逐对象访问检查。 |
| [Session / Token Revocation](../../glossary/security.md#security.revocation) | 主动终止会话或令牌的继续使用，真实生效范围取决于验证状态与传播策略。 |
| [Account Recovery](../../glossary/security.md#security.account-recovery) | 丢失所需认证能力后，凭约定证据重新取得账号控制的过程。 |
| [Pepper](../../glossary/security.md#security.pepper) | 与密码库分离保存、参与密码校验保护的额外秘密。 |
| [HMAC](../../glossary/security.md#security.hmac) | 使用共享秘密与密码学哈希认证指定消息内容的机制。 |
| [Replay Attack](../../glossary/security.md#security.replay) | 重新提交先前有效的消息或凭证，试图再次获得访问或业务效果。 |
| [Contextual Output Encoding](../../glossary/security.md#security.output-encoding) | 按数据最终进入的 HTML、属性、URL 或脚本语法位置编码，使数据不被误解释成该位置的代码。 |
| [Trusted Types](../../glossary/security.md#security.trusted-types) | 通过集中策略产生特定可信类型，并按 CSP 约束受管控的 DOM 注入汇接受这些值的浏览器机制。 |
| [Envelope Encryption](../../glossary/security.md#security.envelope-encryption) | 用数据密钥保护数据，再用包装密钥保护数据密钥，并保存可恢复的密文与版本关系。 |
| [Dynamic Credentials](../../glossary/security.md#security.dynamic-credentials) | 按已授权角色按需生成、期限和权限受限的凭据，并通过目标系统接口完成续期与撤销。 |
| [Workload Identity](../../glossary/security.md#security.workload-identity) | 标识运行中服务或[进程](../../glossary/systems.md#systems.execution-units)主体、供通信认证与策略映射使用的身份。 |
| [Relationship-Based Access Control](../../glossary/security.md#security.rebac) | 按主体与对象、对象与对象之间的关系及组合规则推导访问资格。 |
| [Multi-Factor Authentication](../../glossary/security.md#security.mfa) | 组合不同类别的认证因子，并保持挑战、绑定、会话及恢复路径的保证。 |
| [Service Delegation](../../glossary/security.md#security.service-delegation) | 让当前执行者在明确主体、目标资源与权限范围内代为执行操作。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
