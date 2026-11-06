<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 身份、安全与权限词汇表

本页解释 28 组术语，按[完整术语索引](../glossary.md#security)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [身份、安全与权限文章](../knowledge/security/index.md)

## 本页术语

- [Authentication / Authorization](#security.identity)
- [Session / Cookie](#security.sessions)
- [OAuth 2.0 / OpenID Connect](#security.oauth)
- [JWT / JWS / JWK](#security.tokens)
- [RBAC / ABAC](#security.access-control)
- [Access Token / Refresh Token](#security.token-lifecycle)
- [CORS / Same-Origin Policy](#security.origin)
- [XSS / CSRF / SSRF](#security.web-attacks)
- [SQL Injection / Parameterized Query](#security.sql-injection)
- [Hash / Salt / KDF](#security.passwords)
- [mTLS / Certificate](#security.mtls)
- [Secrets Management](#security.secrets)
- [Least Privilege / Zero Trust](#security.trust)
- [Threat Modeling / OWASP](#security.threats)
- [Tenant Isolation / Object-level Authorization](#security.tenant-isolation)
- [Session / Token Revocation](#security.revocation)
- [Account Recovery](#security.account-recovery)
- [Pepper](#security.pepper)
- [HMAC](#security.hmac)
- [Replay Attack](#security.replay)
- [Contextual Output Encoding](#security.output-encoding)
- [Trusted Types](#security.trusted-types)
- [Envelope Encryption](#security.envelope-encryption)
- [Dynamic Credentials](#security.dynamic-credentials)
- [Workload Identity](#security.workload-identity)
- [Relationship-Based Access Control](#security.rebac)
- [Multi-Factor Authentication](#security.mfa)
- [Service Delegation](#security.service-delegation)

<a id="security.identity"></a>

## Authentication / Authorization

**ID：** `security.identity` · **建议优先级：** P0

**别名 / 检索词：** Authentication、Authorization、认证、授权

**简释：** 证明身份与判断访问权。

认证建立主体身份，授权判断该主体在当前条件下能执行哪些动作。身份有效不代表拥有任意对象权限；每个执行入口都需实施相应授权。

**例子：** 用户登录成功后，仍不能凭其他人的订单 ID 查看详情。

**深入阅读：** [对象级授权：已登录为何仍不能访问这份数据](../knowledge/security/object-level-authorization.md) · [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md) · [MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)

<a id="security.sessions"></a>

## Session / Cookie

**ID：** `security.sessions` · **建议优先级：** P0

**别名 / 检索词：** Session、Cookie、会话

**简释：** 会话状态和浏览器保存、发送的数据。

Session 保存或关联登录状态，Cookie 是浏览器按规则存储并随请求发送数据的机制。Cookie 可保存会话标识，但不是会话本身；作用域与安全属性需单独配置。

**例子：** 服务端撤销会话记录后，旧 Cookie 仍在浏览器中也不应继续获得访问权。

**深入阅读：** [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md) · [XSS：不可信数据何时变成浏览器代码](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md) · [MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)

<a id="security.oauth"></a>

## OAuth 2.0 / OpenID Connect

**ID：** `security.oauth` · **建议优先级：** P0

**别名 / 检索词：** OAuth 2.0、OpenID Connect、OAuth、OIDC、PKCE、Authorization Code、code_verifier、nonce、委托授权

**简释：** 委托授权框架与其上的身份层。

OAuth 规定客户端如何获得访问资源的授权，OIDC 在其上提供身份层。PKCE 绑定授权码交易中的验证材料；仍需校验回调、状态、发行方及适用的令牌声明。

**例子：** 登录客户端校验 ID Token，调用 API 则使用面向该 API 的 Access Token。

**深入阅读：** [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [OAuth 与 OIDC：一次登录怎样绑定授权、身份和回调](../knowledge/security/oauth-oidc-and-pkce.md) · [跨服务委托：谁在替谁访问哪个资源](../knowledge/security/service-delegation-token-exchange-and-audience.md)

<a id="security.tokens"></a>

## JWT / JWS / JWK

**ID：** `security.tokens` · **建议优先级：** P0

**别名 / 检索词：** JWT、JWS、JWK、签名令牌

**简释：** 声明容器、签名格式和密钥表示。

JWT 是声明表示，JWS 是签名封装，JWK 是密钥表示。签名保护完整性而非保密；验证还需限制算法并核对发行方、受众、时间与密钥用途。

**例子：** 可解码 JWT 载荷不代表令牌可信，也不应把敏感秘密放进未加密载荷。

**深入阅读：** [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [跨服务委托：谁在替谁访问哪个资源](../knowledge/security/service-delegation-token-exchange-and-audience.md)

<a id="security.access-control"></a>

## RBAC / ABAC

**ID：** `security.access-control` · **建议优先级：** P0

**别名 / 检索词：** RBAC、ABAC、角色权限、属性权限

**简释：** 通过角色分配或主体、对象、动作与环境属性表达访问规则。

RBAC把权限关联到角色并可使用层级与约束；ABAC对可信属性按规则求值。实际系统可组合角色、属性和对象关系，但模型不替代租户边界、冲突语义、事实来源、新鲜度与执行处检查。

**例子：** 复核员角色允许一种动作，仍需核对其有效租户、目标对象和职责分离；只更新策略版本不代表成员关系已同步。

**深入阅读：** [对象级授权：已登录为何仍不能访问这份数据](../knowledge/security/object-level-authorization.md) · [权限模型与策略传播：规则改了，哪些请求仍可能被允许](../knowledge/security/authorization-models-policy-distribution-and-revocation.md)

<a id="security.token-lifecycle"></a>

## Access Token / Refresh Token

**ID：** `security.token-lifecycle` · **建议优先级：** P0

**别名 / 检索词：** Access Token、Refresh Token、访问令牌、刷新令牌

**简释：** 访问凭据和更新访问凭据的机制。

Access Token 面向资源访问，Refresh Token 用于向授权服务换取新的访问凭据。两者的受众、存储、期限与撤销规则不同，刷新流程也需防重放。

**例子：** 刷新令牌撤销后，已签发访问令牌是否立即失效取决于资源端验证机制。

**深入阅读：** [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md)

<a id="security.origin"></a>

## CORS / Same-Origin Policy

**ID：** `security.origin` · **建议优先级：** P0

**别名 / 检索词：** CORS、Same-Origin Policy、同源策略、跨源

**简释：** 浏览器同源边界与跨源响应访问机制。

同源策略限制浏览器脚本跨源读取或交互；CORS 由服务端声明可被哪些源读取的跨源响应。它不阻止所有请求发出，也不替代服务端认证授权。

**例子：** 浏览器拒绝脚本读取跨源响应，不代表服务端从未收到该请求。

**深入阅读：** [同源、CORS 与 CSRF：请求发得出为什么仍读不到响应](../knowledge/security/origins-cors-and-csrf.md)

<a id="security.web-attacks"></a>

## XSS / CSRF / SSRF

**ID：** `security.web-attacks` · **建议优先级：** P0

**别名 / 检索词：** XSS、CSRF、SSRF、跨站脚本、跨站请求伪造、服务端请求伪造

**简释：** 脚本注入、跨站请求伪造和服务端请求伪造。

XSS 让攻击脚本进入可信页面，CSRF 借浏览器自动携带的凭据触发请求，SSRF 诱导服务端访问非预期目标。三者的信任边界和防护手段不同。

**例子：** 服务端抓取用户 URL 时，需限制目标与重定向，避免访问内部管理接口。

**深入阅读：** [同源、CORS 与 CSRF：请求发得出为什么仍读不到响应](../knowledge/security/origins-cors-and-csrf.md) · [XSS：不可信数据何时变成浏览器代码](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md) · [SSRF：服务端代发请求怎样守住网络出口](../knowledge/security/ssrf-url-resolution-and-egress-boundaries.md)

<a id="security.sql-injection"></a>

## SQL Injection / Parameterized Query

**ID：** `security.sql-injection` · **建议优先级：** P0

**别名 / 检索词：** SQL Injection、Parameterized Query、SQL 注入、参数化查询

**简释：** 查询结构注入与参数绑定防护。

SQL 注入把输入混入查询结构；参数绑定使值与语句结构分离。表名、排序方向等结构项通常不能作为普通值参数，应采用受控映射。

**例子：** 查询用户时绑定用户名参数，排序列则从允许列表选择。

**深入阅读：** [SQL 注入与参数化查询：值怎样与查询结构分开](../knowledge/security/sql-injection-parameters-and-query-structure.md)

<a id="security.passwords"></a>

## Hash / Salt / KDF

**ID：** `security.passwords` · **建议优先级：** P0

**别名 / 检索词：** Hash、Salt、KDF、口令哈希、随机盐

**简释：** 哈希、随机盐和适合口令的派生机制。

口令存储应使用适合口令的派生算法、独立随机盐和合适成本参数。普通快速哈希不适合抵御离线猜测，盐也不承担保密作用。

**例子：** 两名用户使用同一口令，独立盐应使其存储结果不同。

**深入阅读：** [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md)

<a id="security.mtls"></a>

## mTLS / Certificate

**ID：** `security.mtls` · **建议优先级：** P0

**别名 / 检索词：** mTLS、Certificate、双向 TLS

**简释：** TLS 连接双方按约定使用证书及对应私钥证明建立对端身份。

mTLS 需要双方完成证书认证及握手证明。在 CA 证书身份配置中，还要检查信任路径、期限、用途与预期身份；证书链可信不等于业务授权。预注册自签名或证书绑定令牌采用各自协议的接受依据，不能推广为普通服务免检。代理终止 TLS 后须重新划定身份边界，并管理轮换、现存连接和撤销传播。

**例子：** 服务 A 的证书可信并持有对应私钥，仍不能删除租户 T2 的订单；代理 P 终止入站 TLS 后，后端首先认证的是 P 的连接身份。

**深入阅读：** [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md)

<a id="security.secrets"></a>

## Secrets Management

**ID：** `security.secrets` · **建议优先级：** P0

**别名 / 检索词：** Secrets Management、密钥管理、秘密管理

**简释：** 敏感凭据的保存、分发与轮换。

秘密管理覆盖凭据存储、发放、最小访问、轮换与审计。应减少明文传播和日志暴露，优先使用期限与权限受限的凭据。

**例子：** 数据库口令轮换需协调新旧连接与服务更新，不能只改配置中心的值。

**深入阅读：** [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md) · [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md) · [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md) · [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md)

<a id="security.trust"></a>

## Least Privilege / Zero Trust

**ID：** `security.trust` · **建议优先级：** P0

**别名 / 检索词：** Least Privilege、Zero Trust、最小权限、零信任

**简释：** 最小授权和持续验证访问条件。

最小权限只授予完成任务必要的能力；零信任不把网络位置本身当成充分信任依据。访问仍需基于身份、资源和上下文验证，并持续管理凭据。

**例子：** 来自内网的请求也要校验服务身份与具体操作权限。

**深入阅读：** [信任边界与威胁建模：内网请求为什么仍需验证](../knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md)

<a id="security.threats"></a>

## Threat Modeling / OWASP

**ID：** `security.threats` · **建议优先级：** P0

**别名 / 检索词：** Threat Modeling、OWASP、威胁建模

**简释：** 识别攻击面并参考应用安全研究与规范。

威胁建模从资产、入口、信任边界和攻击路径分析风险，并把缓解措施连接到可检查证据；OWASP提供指南与研究，本文不穷举其全部项目。清单不能替代具体业务分析和有效性验证。

**例子：** 上传功能除文件类型外，还需考虑解析器、存储权限和后续访问路径。

**深入阅读：** [信任边界与威胁建模：内网请求为什么仍需验证](../knowledge/security/trust-boundaries-least-privilege-and-threat-modeling.md)

<a id="security.tenant-isolation"></a>

## Tenant Isolation / Object-level Authorization

**ID：** `security.tenant-isolation` · **建议优先级：** P0

**别名 / 检索词：** Tenant Isolation、Object-level Authorization、租户隔离、对象级授权

**简释：** 租户边界与逐对象访问检查。

租户隔离约束数据和操作不能跨租户越界；对象级授权判断当前主体是否有权访问目标对象。身份与租户应来自可信上下文，缓存和后台任务也要保持边界。

**例子：** 查询订单时同时约束对象 ID 与当前主体允许访问的租户范围。

**深入阅读：** [对象级授权：已登录为何仍不能访问这份数据](../knowledge/security/object-level-authorization.md) · [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md) · [权限模型与策略传播：规则改了，哪些请求仍可能被允许](../knowledge/security/authorization-models-policy-distribution-and-revocation.md)

<a id="security.revocation"></a>

## Session / Token Revocation

**ID：** `security.revocation` · **建议优先级：** P1

**别名 / 检索词：** Token Revocation、Session Revocation、会话撤销、令牌撤销

**简释：** 主动终止会话或令牌的继续使用，真实生效范围取决于验证状态与传播策略。

撤销通过改变验证状态使已有凭据停止被接受。生效时间取决于验证缓存、会话存储或令牌自包含策略，删除客户端副本不等于服务端已撤销。

**例子：** 用户退出全部设备后，要核对旧访问令牌在各资源服务上的实际接受期限。

**深入阅读：** [认证、会话与令牌：登录状态怎样建立和失效](../knowledge/security/authentication-sessions-and-tokens.md) · [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md) · [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md) · [权限模型与策略传播：规则改了，哪些请求仍可能被允许](../knowledge/security/authorization-models-policy-distribution-and-revocation.md) · [对象存储与预签名访问：文件上传后怎样成为可用的业务对象](../knowledge/cache-search/object-storage-versions-uploads-and-presigned-access.md) · [跨服务委托：谁在替谁访问哪个资源](../knowledge/security/service-delegation-token-exchange-and-audience.md)

<a id="security.account-recovery"></a>

## Account Recovery

**ID：** `security.account-recovery` · **建议优先级：** P1

**别名 / 检索词：** Account Recovery、账号恢复、账户恢复

**简释：** 丢失所需认证能力后，凭约定证据重新取得账号控制的过程。

账号恢复需要独立判断请求者能否替换认证器，约束恢复材料的用途、有效期与单次消费，并审查被接管的恢复渠道和旧访问能力。知道账号名或完成密码写入，都不等于已经恢复全部控制权。

**例子：** 用户用事先保存的恢复材料重新建立认证能力后，还要撤销攻击者会话并检查被修改的恢复邮箱与 MFA。

**深入阅读：** [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md) · [MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)

<a id="security.pepper"></a>

## Pepper

**ID：** `security.pepper` · **建议优先级：** P1

**别名 / 检索词：** Pepper、口令 pepper

**简释：** 与密码库分离保存、参与密码校验保护的额外秘密。

pepper 通过保密材料增加对仅泄露密码库场景的保护；它不同于通常公开并逐记录独立的盐。秘密的可用性、访问隔离、版本、轮换与泄露处置均需单独设计，不能替代密码 KDF。

**例子：** 攻击者只复制密码校验表时尚未获得秘密服务中的 pepper；若应用及秘密访问权限也被接管，就不能继续依赖这项隔离。

**深入阅读：** [密码存储与账号恢复：改了密码，为什么还没夺回账号](../knowledge/security/password-storage-and-account-recovery.md) · [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md)

<a id="security.hmac"></a>

## HMAC

**ID：** `security.hmac` · **建议优先级：** P1

**别名 / 检索词：** HMAC、基于哈希的消息认证码

**简释：** 使用共享秘密与密码学哈希认证指定消息内容的机制。

HMAC 验证方按同一秘密和协议规定的字节计算认证值并安全比较，以检查消息完整性及共享秘密持有关系。它不加密载荷、不自动限制重放，也不能让共享秘密的接收方证明只有发送方可能生成消息。

**例子：** Webhook 对原始请求体计算 HMAC-SHA-256；把体解析后重新序列化再计算，可能因为字节改变而验证失败。

**深入阅读：** [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md) · [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md)

<a id="security.replay"></a>

## Replay Attack

**ID：** `security.replay` · **建议优先级：** P1

**别名 / 检索词：** Replay Attack、重放攻击

**简释：** 重新提交先前有效的消息或凭证，试图再次获得访问或业务效果。

签名有效只证明被覆盖内容与密钥关系，不证明本次是首次使用。受认证时间可以限制接受期限，nonce 或稳定事件身份需要结合持久消费状态；合法重试与补发仍须按协议得到可恢复且幂等的处理。

**例子：** 攻击者在有效窗口内重复提交同一带签名事件，时间和 MAC 都可能通过，但持久事件键与业务约束应避免再次产生同一效果。

**深入阅读：** [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](../knowledge/api/webhook-signatures-replay-and-delivery.md)

<a id="security.output-encoding"></a>

## Contextual Output Encoding

**ID：** `security.output-encoding` · **建议优先级：** P1

**别名 / 检索词：** Contextual Output Encoding、上下文输出编码

**简释：** 按数据最终进入的 HTML、属性、URL 或脚本语法位置编码，使数据不被误解释成该位置的代码。

上下文输出编码在输出位置执行，与业务输入校验和 HTML 净化职责不同。同一字符串在不同解析器与嵌套上下文中需要不同处理，URL 组件编码也不能替代允许方案与目标检查。优先使用框架文本绑定或不会解析 HTML 的展示 API。

**例子：** 简介需要显示尖括号原文时使用普通展示节点的 textContent；不能把入口处做过一次 HTML 编码的值任意拼入 JavaScript 或 URL。

**深入阅读：** [XSS：不可信数据何时变成浏览器代码](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md)

<a id="security.trusted-types"></a>

## Trusted Types

**ID：** `security.trusted-types` · **建议优先级：** P1

**别名 / 检索词：** Trusted Types、可信类型策略

**简释：** 通过集中策略产生特定可信类型，并按 CSP 约束受管控的 DOM 注入汇接受这些值的浏览器机制。

Trusted Types 把字符串到主动内容的转换集中到可审查策略；它本身不替策略完成净化，原样返回不可信输入会破坏保护。受控汇、策略创建和浏览器支持需按部署核对，不能据此宣称服务端模板或主动恶意第一方代码已被隔离。

**例子：** 应用让受控富文本策略完成净化后产生 TrustedHTML，并检查直接把普通字符串传给相应 DOM 汇的路径。

**深入阅读：** [XSS：不可信数据何时变成浏览器代码](../knowledge/security/xss-contexts-sinks-and-browser-defenses.md)

<a id="security.envelope-encryption"></a>

## Envelope Encryption

**ID：** `security.envelope-encryption` · **建议优先级：** P1

**别名 / 检索词：** Envelope Encryption、信封加密

**简释：** 用数据密钥保护数据，再用包装密钥保护数据密钥，并保存可恢复的密文与版本关系。

信封加密把数据加密与数据密钥的受控保护分层，常用 DEK 表示保护数据的密钥、KEK 表示包装其他密钥的密钥。恢复需要密文、被包装的数据密钥、正确密钥引用和协议元数据。KEK 材料轮换、重新包装 DEK 与用新 DEK 重加密数据是不同动作；已泄露旧材料与副本不能靠改变默认版本追回。具体库还可能包含内部派生和算法套件。

**例子：** C1 由 DEK1 保护，W1 是用 KEK1 包装的 DEK1；只改默认 KEK2，不会自动使 C1 或 W1 的字节改变。

**深入阅读：** [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md)

<a id="security.dynamic-credentials"></a>

## Dynamic Credentials

**ID：** `security.dynamic-credentials` · **建议优先级：** P1

**别名 / 检索词：** Dynamic Credentials、动态凭据、动态数据库凭据

**简释：** 按已授权角色按需生成、期限和权限受限的凭据，并通过目标系统接口完成续期与撤销。

动态凭据减少长期共享秘密的分发，独立身份有助于关联调用者，但仍依赖初始身份、发放权限和后端操作能力。凭据租约到期、撤销请求完成及已有会话结束不是天然同一状态；续期必须检查返回期限，控制面不可达也不能无限延长缓存。普通 KV 秘密不自动具有动态凭据的 lease 语义。

**例子：** Vault 按数据库角色生成独立用户名后，应用仍需管理连接池；不能只见 lease 已到期就宣布所有旧数据库会话已经断开。

**深入阅读：** [密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效](../knowledge/security/secrets-credentials-rotation-and-revocation.md)

<a id="security.workload-identity"></a>

## Workload Identity

**ID：** `security.workload-identity` · **建议优先级：** P1

**别名 / 检索词：** Workload Identity、工作负载身份

**简释：** 标识运行中服务或进程主体、供通信认证与策略映射使用的身份。

身份发放需将工作负载的受控识别证据绑定到可领取的标识，不能由请求者自报身份决定。SPIFFE 是一种具体体系，以信任域及路径构成 SPIFFE ID；X.509-SVID 可在 URI SAN 中承载该 ID，结合信任材料和私钥证明用于认证。工作负载身份、SPIFFE、SVID、SAN 与 PKI 不是同义词，身份到租户、动作和资源的权限映射仍由应用策略执行。

**例子：** 服务端验证 spiffe://prod.example/orders/reader 后，策略只允许它读取 T1 的订单，不能因路径名含 reader 就自动授予所有租户的读权限。

**深入阅读：** [mTLS 与服务身份：双向验证为何仍需授权边界](../knowledge/security/mtls-service-identities-and-trust-boundaries.md) · [跨服务委托：谁在替谁访问哪个资源](../knowledge/security/service-delegation-token-exchange-and-audience.md)

<a id="security.rebac"></a>

## Relationship-Based Access Control

**ID：** `security.rebac` · **建议优先级：** P1

**别名 / 检索词：** ReBAC、Relationship-Based Access Control、基于关系的访问控制

**简释：** 按主体与对象、对象与对象之间的关系及组合规则推导访问资格。

关系模型可表达直接分享、团队成员与父对象继承，并与角色、属性和强制租户限制组合。图上有路径不自动授予权限，实际关系规则、遍历成本与事实新鲜度需分别约定；它不是RBAC角色层级、OpenFGA或PDP的同义词。

**例子：** 团队成员经有读取资格的父文件夹访问文档，仍需满足租户与对象状态；撤销成员关系后，旧事实和允许缓存可能继续影响判断。

**深入阅读：** [权限模型与策略传播：规则改了，哪些请求仍可能被允许](../knowledge/security/authorization-models-policy-distribution-and-revocation.md)

<a id="security.mfa"></a>

## Multi-Factor Authentication

**ID：** `security.mfa` · **建议优先级：** P1

**别名 / 检索词：** MFA、Multi-Factor Authentication、多因子认证

**简释：** 组合不同类别的认证因子，并保持挑战、绑定、会话及恢复路径的保证。

MFA不按设备数或页面步骤计数，密码加安全问题仍通常属于同类因子。OTP短时/单次、WebAuthn的RP和挑战绑定、UP/UV、凭据注册/替换及合格认证的新鲜度需分别检查；MFA完成不代表交易同意或当前对象授权。

**例子：** 12:00完成认证，12:06执行要求300秒内证明的动作，360秒已超范围；换发令牌不会自动重新完成因子认证。

**深入阅读：** [MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度](../knowledge/security/multi-factor-authentication-passkeys-and-recovery.md)

<a id="security.service-delegation"></a>

## Service Delegation

**ID：** `security.service-delegation` · **建议优先级：** P1

**别名 / 检索词：** Service Delegation、跨服务委托

**简释：** 让当前执行者在明确主体、目标资源与权限范围内代为执行操作。

委托需分清subject、当前actor、受众、签发者与对象动作。Token Exchange是一种取得下一跳凭据的协议，不自动赋予权限收窄或撤销联动；ID Token、mTLS、DPoP和客户端自身权限各有不同用途。先前actor历史不等于当前授权，换发时间也不代表新的用户认证。

**例子：** B收到只面向B的用户凭据后，不能直接拿给C；需要取得适合C的能力并由C独立验证当前主体、执行者和对象权限。

**深入阅读：** [跨服务委托：谁在替谁访问哪个资源](../knowledge/security/service-delegation-token-exchange-and-audience.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [OWASP Cheat Sheet Series：Web 安全边界与防护](https://cheatsheetseries.owasp.org/)
- [OWASP：密码存储与 pepper](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP：忘记密码与重置流程](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [NIST SP 800-63B-4：认证器事件与账号恢复](https://pages.nist.gov/800-63-4/sp800-63b/events/)
- [RFC 2104：共享密钥消息认证](https://www.rfc-editor.org/rfc/rfc2104.html)
- [OWASP：XSS 上下文编码与 HTML 净化](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [W3C：Trusted Types 机制与策略边界](https://www.w3.org/TR/trusted-types/)
- [OWASP：SSRF 目的地与网络出口防护](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP：SQL 注入、参数化与允许映射](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Psycopg3：值参数与查询结构](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [PostgreSQL18：动态 SQL 与 USING](https://www.postgresql.org/docs/18/plpgsql-statements.html#PLPGSQL-STATEMENTS-EXECUTING-DYN)
- [OWASP：Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST SP 800-57 Part 1 Rev. 5：Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [AWS Encryption SDK：Envelope Encryption Concepts](https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html)
- [AWS KMS：Rotate Keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [Vault：Database Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [AWS IAM：Temporary Security Credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html)
- [RFC 5280：证书路径、用途约束与撤销](https://www.rfc-editor.org/rfc/rfc5280.html)
- [RFC 9525：TLS 服务端参考身份与名称匹配](https://datatracker.ietf.org/doc/html/rfc9525)
- [RFC 8705：OAuth mTLS 客户端认证与证书绑定令牌](https://www.rfc-editor.org/rfc/rfc8705.html)
- [RFC 9440：Client-Cert 转发字段与代理可信路径](https://www.rfc-editor.org/rfc/rfc9440.html)
- [SPIFFE Identity：身份命名空间、信任域与 SVID](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)
- [SPIFFE X.509-SVID：URI SAN、约束与验证](https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md)
- [SPIFFE Workload API：调用方识别、信任材料与流式更新](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Workload_API.md)
- [NIST RBAC archived project](https://csrc.nist.gov/Projects/Role-Based-Access-Control)
- [NIST SP 800-162: Guide to ABAC](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-162.pdf)
- [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts)
- [OPA Philosophy](https://www.openpolicyagent.org/docs/philosophy)
- [OPA Bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP Authorization Policy and Data Distribution](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Policy_And_Data_Distribution_Cheat_Sheet.html)
- [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/system/files/atc19-pang.pdf)
- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [RFC 6238: TOTP](https://www.rfc-editor.org/rfc/rfc6238.html)
- [WebAuthn Level 2 Recommendation, 2021-04-08](https://www.w3.org/TR/2021/REC-webauthn-2-20210408/)
- [FIDO Alliance Passkeys](https://fidoalliance.org/passkeys/)
- [OWASP Multifactor Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 6749: OAuth2 Client Credentials](https://www.rfc-editor.org/rfc/rfc6749.html)
- [RFC 8693: Token Exchange](https://www.rfc-editor.org/rfc/rfc8693.html)
- [RFC 8707: Resource Indicators](https://www.rfc-editor.org/rfc/rfc8707.html)
- [RFC 9068: JWT Access Token Profile](https://www.rfc-editor.org/rfc/rfc9068.html)
- [RFC 9700: OAuth Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html)
- [RFC 9449: OAuth DPoP](https://www.rfc-editor.org/rfc/rfc9449.html)
- [OpenID Connect Core 1.0 errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [NIST SP 800-207](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)
- [OWASP Threat Modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
