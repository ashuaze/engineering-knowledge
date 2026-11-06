---
id: "kb-security-mfa"
title: "MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分认证因子、OTP、WebAuthn 与会话保证，解释挑战绑定、认证器注册、替换恢复和敏感操作重新认证。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-security-sessions-tokens", "kb-security-password-recovery"]
related: ["kb-security-oauth-oidc", "kb-security-authorization-models", "kb-security-object-authorization", "kb-security-secret-lifecycle", "kb-api-idempotency", "kb-api-admission-controls"]
tags: ["mfa", "totp", "webauthn", "passkeys", "recovery"]
---

# MFA：多因子、抗钓鱼与恢复怎样共同决定认证强度

学习入口：密码之后再输一次验证码，为什么仍可能被实时钓鱼？一个通行密钥只点一次，为何又可能完成[多因子认证](../../glossary/security.md#security.mfa)？判断强度要看证明了哪些因子、证明绑定到哪里，以及注册、[会话](../../glossary/security.md#security.sessions)和恢复是否保住同一保证，不能只数页面步骤。

前置：[认证、会话与令牌](authentication-sessions-and-tokens.md)、[密码存储与账号恢复](password-storage-and-account-recovery.md)。本文核查 NIST SP 800-63B-4、RFC 6238、WebAuthn Level 2 及官方指南的相关机制；不提供认证器或验证码的生产实现。时间、状态和账号流程为纸面教学设计，未注册真实认证器、发短信、执行浏览器[认证](../../glossary/security.md#security.identity)或攻击实验。

## 多因子不是多输几次信息

认证因子通常分为知道什么、持有什么和自身特征。MFA 要求组合不同类别的因子；同一设备可以承载多个类别，也可能把多个秘密暴露在同一个失陷边界。需要判断真实证明和独立性，而非机械要求两台设备。

| 教学组合 | 需要怎样理解 |
| --- | --- |
| 密码加安全问题 | 两者通常都是知识因子，不能只因问了两次就称为 MFA |
| 密码加已绑定 OTP 认证器 | 可以组合知识与持有证明，仍需保护种子、绑定与验证流程 |
| 单独触碰一个安全密钥 | 触碰可表明有人参与，不自动证明已经完成另一类别因子 |
| 私钥认证加认证器本地 PIN/生物验证 | 可在相应协议中构成多因子认证器，服务端仍须验证所需证据 |

[OWASP MFA 指南](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)解释因子组合与实施取舍。生物特征不是可以随意轮换的远程密码；用它在设备内解锁私钥，与把指纹照片发给服务器，是不同的信任关系。

NIST 的 AAL（认证保证等级）评价一套认证器与流程要求，不是按因子数量自动给所有实现评级。[SP 800-63B-4 §2–3](https://pages.nist.gov/800-63-4/sp800-63b.html)还分别要求考虑重放、钓鱼和认证器管理。本文借这些概念解释边界，不由产品名称直接推定等级。

## OTP 的短时有效与抗钓鱼是两项性质

TOTP 利用双方共享秘密与时间步计算一次性密码；验证方必须按约定保护能计算 OTP 的秘密，不能照搬“只存不可逆密码校验值”的全部做法。算法及验证窗口见 [RFC 6238 §4–6](https://www.rfc-editor.org/rfc/rfc6238.html#section-4)。

纸面设定：起始时间 T0=0，时间步 X=30 秒，不计算任何真实验证码，只计算计数器：

```text
T = floor((Unix 时间 − T0) / X)
```

| 教学时间（秒） | T |
| --- | --- |
| 59 | 1 |
| 60 | 2 |
| 89 | 2 |
| 90 | 3 |

若某教学验证策略在 t=60 允许当前步前后一格，它会尝试 T=1、2、3，而非只有 T=2。这是容忍[时钟偏差](../../glossary/distributed.md#distributed.clocks)的一个假设，不是所有系统都应接受三格的配置建议；扩大窗口会扩大候选验证范围。还要限制尝试、记录成功使用，并在并发验证中守住一次使用，不能因“码随时间变”就认为服务器无需状态。

RFC 6238 要求成功使用后的 OTP 不再次被接受。两个节点若都先查未使用、再各自放行，仍可能重复完成认证；消费状态要覆盖相应账号、认证器及有效验证范围，并在实际接受处协调。一次性消费和[业务幂等](../api/idempotency.md)不同，验证码只完成认证步骤，不是付款结果。

然而，尚未使用且仍有效的 OTP 可以被假站点实时转发到真站点。推送批准还可能遇到疲劳诱导；号码控制也不保证渠道永不被接管。短期限、限速与防重复各有用处，却不能把手工转录的验证码变成绑定目标站点的密码学证明。NIST [§3.2.5](https://pages.nist.gov/800-63-4/sp800-63b.html)据此区分抗钓鱼与仅防重放；网络加密也不能替用户识别一个拿到合法证书的假站点。

## WebAuthn 把证明绑定到目标与本次挑战

WebAuthn 让认证器用为 RP（依赖方）注册的公钥凭据证明私钥控制；RP ID 限定凭据的使用范围，服务端还要核对本次实际 origin。依据本文固定使用的 [WebAuthn Level 2，2021-04-08 Recommendation](https://www.w3.org/TR/2021/REC-webauthn-2-20210408/)，认证响应至少涉及下面这些不同检查，具体实现仍应遵循完整规范和成熟库：

| 证据 | 服务端需要确认什么 |
| --- | --- |
| challenge 与交易记录 | 对应自己签发、尚未完成且仍有效的这次认证，绑定预期账号与用途 |
| 类型、origin、RP ID hash | 属于预期的认证操作、受信来源及 RP 范围 |
| credential ID 与公钥 | 是这个账号已绑定、仍允许使用的凭据 |
| 签名与必要认证器数据 | 响应真实覆盖被检查的数据，而非相信客户端自报字段 |
| UP 与按策略要求的 UV | 分别满足用户在场与用户验证要求，不能用 UP 替 UV |

User Presence（UP）表示用户在场；User Verification（UV）表示认证器按其方式验证了本地用户，例如 PIN 或生物识别。UV 位包含在经过验证的签名数据中，RP 才能据此使用；这不是服务器获得了指纹原始数据，也不证明具体哪位自然人操作了一个共享设备。

在正确绑定与验证下，另一个不相关域名不能把同一 RP 凭据作为任意网站可用的 OTP 转交；但合法站点的脚本被控制、认证器被接管或会话被偷，仍是其他边界。WebAuthn 的抗钓鱼性质不能概括成整个账号生命周期不会被接管。

通行密钥（passkey）是相关 FIDO 公钥凭据的使用方式，既可能按产品安排同步，也可能与设备绑定，见 [FIDO Alliance Passkeys](https://fidoalliance.org/passkeys/)。不能仅凭“免密码”推定它完成了 UV、私钥不可导出或满足某个最高等级。同步、备份与同步[账号恢复](../../glossary/security.md#security.account-recovery)还引入自己的信任与恢复责任；上述 Level 2 只用于解释基础仪式，不当作当前全部通行密钥扩展的规范清单。

## 注册、替换与遗失处理也是认证边界

认证器绑定相当于增加一条未来登录路径。若攻击者拿到一个旧会话就能注册自己的新认证器，之后即使原[会话撤销](../../glossary/security.md#security.revocation)，也可能继续登录。绑定需验证当前账号控制权、登记交易、新认证器的持有证明及最终保存的账号/凭据关系，不能把展示了二维码或收到了 credential ID 当作完成绑定。

教学流程可以是：已有强度合适的重新认证 → 建立有期限的注册交易 → 验证新认证器响应 → 在账号状态仍允许时完成绑定 → 通知既有可信渠道并记录变更。并发绑定、取消或账号被停用时，最后一步还应重新核对资格；这是协议设计要求，不是本文已实现的事务。

正常替换已有因子，与所有必需认证器都遗失后的恢复，是两条不同路径。前者可依据仍可信的已登记因子重新验证；后者需要预先建立的恢复材料或受控核验。仅凭当前会话或客服收到的几个个人信息，不自动获得移除 MFA 的权限。更换时通知可信旧渠道、处理可疑变更及遗留认证器的接受状态，见 [OWASP Changing MFA Factors](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html#changing-mfa-factors)。

恢复码若用于一次恢复，需有用途、保存与单次消费责任；它的泄露也会形成一条旁路。不能在主登录上要求抗钓鱼证明，却允许任何人只凭被接管邮箱无约束替换全部因子。若只向账号里刚被攻击者修改的新邮箱发送因子替换确认，就可能把控制权交还攻击者；应核对事先建立且仍可信的恢复证据。具体恢复边界继续见[账号恢复](password-storage-and-account-recovery.md)，本文没有重新执行该篇的任何实验。

## 登录完成、升阶认证和业务授权继续分开

在需要 MFA 的登录路径中，密码成功后可以建立仅能推进认证的 pending 状态，但不能提前授予完整受保护会话。服务端确认其他因子、原交易、账号和凭据状态均仍成立后，才完成转换；前端按钮隐藏或 `mfa=true` 参数不能代替这一接受点。

教学策略：敏感操作要求距一次合格认证不超过 300 秒。若 12:00 已完成，12:06 才操作，相隔 360 秒，应重新认证；12:05 刷新会话或换发新令牌并不代表在 12:05 又使用了因子。300 秒只是假设，真实范围由业务与协议确定，还要分清空闲期限、绝对会话期限和认证新鲜度。

升阶后应更新服务端可信的认证上下文，并按会话机制更新标识、使旧低保证能力不能借新状态继续使用；会话固定与标识更新见 [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#renew-the-session-id-after-any-privilege-level-change)。用户完成了较强认证，仍需当前的租户、对象和动作授权；它不表示已经同意一笔具体交易，也不让被撤销的关系重新有效，见[权限模型与策略传播](authorization-models-policy-distribution-and-revocation.md)。

## 五道自检与核查范围

1. 密码加安全问题、密码加 OTP、仅触碰密钥和私钥加本地 UV 各证明什么？为什么设备数、步骤数和 AAL 不能简单等同？
2. 59/60/89/90 秒的 T 值怎样算出？前后容差、成功消费和并发验证分别影响什么，为什么短时一次性仍不能阻止实时钓鱼？
3. WebAuthn 的 challenge、origin/RP ID、账号凭据、签名及 UP/UV 各检查什么？为什么 passkey、免密码和私钥不可导出不是同义词？
4. 注册新因子、正常替换与全部遗失后的恢复各需要哪些控制权证明？为什么只看现有会话或新填邮箱可能绕过 MFA？
5. pending 登录、12:00/12:06 的升阶例子和当前对象授权各有哪个接受点？为什么[刷新令牌](../../glossary/security.md#security.token-lifecycle)、完成 MFA 或隐藏按钮不能替代它们？

核查日期：2026-10-23。下列为实际读取的相关机制，状态为来源核查；不是某认证器、浏览器、身份提供方或业务部署的符合性结论。

| 一手资料与范围 | 实际核查部分 |
| --- | --- |
| [NIST SP 800-63B-4，2025](https://pages.nist.gov/800-63-4/sp800-63b.html) | 因子/保证等级、OTP/抗钓鱼与同步认证器相关范围，不据此给产品评级 |
| [RFC 6238，2011-05](https://www.rfc-editor.org/rfc/rfc6238.html) | §4–6 的时间步、验证容差与成功后不得重复使用；没有运行密码算法或测试向量 |
| [WebAuthn Level 2，2021-04-08](https://www.w3.org/TR/2021/REC-webauthn-2-20210408/) | RP/挑战、UP/UV、注册与认证响应验证；只解释基础机制，不穷举全部扩展 |
| [FIDO Passkeys](https://fidoalliance.org/passkeys/) | 核查日说明中的公钥凭据、同步/设备绑定形式；不引用营销成功率或推广所有产品行为 |
| [OWASP MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)、[Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) | 核查日滚动指南的因子组合、替换/恢复与会话升阶管理；教学状态/计时不是产品承诺 |

未执行 TOTP/WebAuthn、认证器注册/替换、短信/推送、遗失恢复、会话升阶、并发消费、钓鱼或多节点撤销实验；没有测量认证成功率或给出生产参数。账号、操作和恢复政策仍需结合实际产品另行验证。
