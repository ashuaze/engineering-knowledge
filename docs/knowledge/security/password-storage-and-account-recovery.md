---
id: "kb-security-password-recovery"
title: "密码存储与账号恢复：改了密码，为什么还没夺回账号"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分密码派生、盐和 pepper 的保护范围，沿成本迁移、恢复证明与旧会话撤销解释账号控制权怎样恢复。"
created: "2026-10-22"
updated: "2026-10-23"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-security-sessions-tokens"]
related: ["kb-security-oauth-oidc", "kb-database-isolation-mvcc", "kb-reliability-incident-response", "kb-security-secret-lifecycle", "kb-security-mfa"]
tags: ["passwords", "recovery", "credentials", "revocation"]
---

# 密码存储与账号恢复：改了密码，为什么还没夺回账号

学习入口：数据库中的密码校验值泄露后，团队给它们重新加盐；用户也改了密码，攻击者为什么仍可能控制账号？这里混合了三个问题：怎样提高离线猜测成本、凭什么允许换凭证，以及哪些旧访问能力应失效。三者需要分别闭合。

前置：[认证、会话与令牌](authentication-sessions-and-tokens.md)。本文面向使用本地密码的 Web 账号，解释存储与恢复状态；不提供完整[认证](../../glossary/security.md#security.identity)服务或 [MFA](../../glossary/security.md#security.mfa) 恢复实现。NIST 参考限定为 SP 800-63B-4 的相应机制，不能据本文推定产品满足某个身份保证等级。示例均为教学设计与纸面推演。

## 数据库泄露后，攻击者究竟在算什么

密码验证通常不需要取回原文：服务端使用记录中的算法、成本与盐验证候选密码。攻击者拿到这些记录后，也能离线尝试候选；登录[限流](../../glossary/api.md#api.limits)不再位于其计算路径上。[密码派生](../../glossary/security.md#security.passwords)机制保护的是每次猜测的成本，不能让容易猜的密码凭空增加熵。[NIST §3.1.1.2](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)说明了离线攻击模型与带盐、带成本的密码校验。

| 机制 | 主要增加什么保护 | 不能据此获得什么 |
| --- | --- | --- |
| 适合密码的 KDF / 密码哈希 | 通过计算或内存成本，提高每次候选验证的代价 | 不阻止钓鱼、已知密码登录或活动[会话](../../glossary/security.md#security.sessions)被盗 |
| 每个密码记录的独立随机盐 | 使相同密码的记录不同，限制预计算和跨账号复用猜测结果 | 盐通常与校验值一同保存，不是秘密 |
| [pepper](../../glossary/security.md#security.pepper) | 加入由验证方保密、与密码库分离的秘密，使仅偷到密码库的攻击者还缺一项材料 | 若攻击者同时控制应用或取得秘密，不能继续依赖这层隔离 |

普通快速哈希适合许多完整性用途，却会让低熵密码被快速枚举。加盐不能改变这一速度问题。pepper 则引入秘密的存放、访问与故障恢复责任，不能只把固定字符串写进同一份数据库或代码。以上区分及常见 pepper 组合见 [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#methods-for-enhancing-password-storage)。应使用成熟密码库支持的组合，避免自行设计拼接顺序与编码。

这也解释了“再加一次盐”的局限：攻击者已经持有旧快照，可以继续针对旧记录猜测。修改线上表示不会追回副本；即使切换到更强算法，也不能把已泄露的原文密码变回秘密。

## 成本参数要同时面对离线攻击与在线容量

Argon2id 等内存困难函数让攻击者承担内存与计算代价。其内存量、迭代次数与[并行](../../glossary/systems.md#systems.concurrency)参数共同决定行为；不能仅把某个迭代数字与另一个算法比较。[RFC 9106 §4](https://www.rfc-editor.org/rfc/rfc9106.html#section-4)给出了 Argon2 的参数选择过程，包括每次调用可承担的内存、时间与实际测量。

工程选择应先核对所用算法、库、平台与合规约束的当前指南，再在目标硬件上测量正常和峰值登录负载。需要观察高分位耗时、同时执行的派生数、[进程](../../glossary/systems.md#systems.execution-units)内存、[排队](../../glossary/performance.md#performance.queueing)与拒绝行为；只测一个调用的平均时间无法确定容量。限流和并发接纳也要覆盖密码验证，否则昂贵验证本身会成为耗尽资源的入口。

纸面容量例子：**假设**一次派生需要 64 MiB，允许 32 次同时执行，仅派生区就约需 2 GiB；还未计入进程、连接与分配器开销。这不是推荐配置或实测结果，只说明成本参数与并发上限必须一起决定。提高内存可能提高猜测代价，也可能令登录峰值先触发内存故障。

记录应保存足以选择验证器的算法标识、算法版本、成本、盐与校验值；采用 pepper 时另存秘密版本标识，秘密本身留在独立管理系统。这里的标识不是许可：验证器只接受预先允许的算法和成本范围，不能让不受信任的记录或请求任意要求巨额计算。输入编码、长度上限及历史兼容行为也应固定，防止升级时悄悄改变某些用户的密码含义。

## 版本迁移需要旧验证器，也需要防止旧结果覆盖新凭证

常见迁移方式是在旧算法验证成功、此时仍可取得用户输入的密码后，用新配置生成新记录；没有再次登录的账号不会因此自动升级。[Django 5.2 密码管理](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/#password-upgrading)展示了保留旧验证器并在登录时升级的实现方式。它是一个框架示例，不是本文要求所有系统采用 Django。

教学迁移过程为：读取凭证记录与版本 → 用对应旧验证器验证 → 判断是否需要升级 → 生成新记录 → 仅在旧版本仍匹配时替换。最后一步应有数据库条件更新或等效并发控制：若期间用户已重置密码，旧密码的成功验证不能覆盖刚设的新密码。升级失败应保留可解释的结果，不能把一半字段写成新版本。会话签发也应绑定实际验证过的凭证版本；若凭证已变，应重新验证或拒绝该次登录，不能把旧密码的验证结果直接绑定到重置后的新代次。

如果 pepper 参与的计算需要原密码，拿旧校验值通常不能重新派生到新 pepper；普通参数升级也不应靠“对旧哈希再哈希”冒充重新派生。计划迁移可以在明确期限内支持新旧秘密版本；一旦旧秘密疑似泄露，继续接受它多久就是额外暴露多久，未迁移账号可能需要走受控重置。秘密丢失与泄露的处置不同：前者可能使验证不可用，后者还要求阻断旧能力。秘密轮换、撤销与审计职责见 [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html#27-secret-lifecycle)。

## 恢复证明不能只回答“知道这个账号名吗”

输入邮箱或用户名只是在选择目标账号。恢复流程需要依据预先建立的恢复材料、仍可用的认证器或经约束的身份核验，判断请求者是否有资格替换凭证。邮箱链接证明的是对该链接所达渠道的控制；如果邮箱已经被接管，这项证明也会失去原先意义。

NIST 区分“还有其他认证器可用时更换忘记的密码”与失去所需认证器后的[账号恢复](../../glossary/security.md#security.account-recovery)；后者有独立方法、通知与保证要求。恢复渠道与证据组合应按账号风险决定，不能用一个较弱的找回入口绕过原有强认证。[NIST §4.2](https://pages.nist.gov/800-63-4/sp800-63b/events/)列出保存的恢复码、下发的恢复码、恢复联系人及重新身份核验等方法；这些不是随意互换的同等证明。

疑似接管时，攻击者可能刚换过邮箱或绑定了自己的 MFA。只向“当前账号里最新填写的地址”发送链接，会把控制权交还攻击者；应核对独立、事先建立且仍可信的证据，并审查未经授权的恢复渠道和认证器变更。MFA 的遗失与替换还需自己的恢复策略，见 [OWASP MFA：Resetting MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html#resetting-mfa)。

## 一次性链接是一项有范围、会消耗的权限

重置凭证应不可预测、绑定具体账号与用途、具有到期时间，并安全保存校验材料。它只应授权完成约定的重置步骤，不能顺便获得普通登录或任意修改资料的权限。[OWASP Forgot Password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html#general-security-practices)要求随机、单次、过期等性质；“签名正确的 [JWT](../../glossary/security.md#security.tokens)”若没有消费状态，同样不能自动满足单次使用。

教学状态可以包含 `account_id、purpose、credential_version、expires_at、consumed_at、token_verifier`。在提交新密码时，服务端要原子地判断凭证未消费、未过期、用途与账号匹配，并完成密码记录更新及消费标记；先查“没用过”、再无条件写入会允许两个请求同时通过。计算新密码的昂贵派生可以与短事务分开，但进入事务后仍需重新核对版本和恢复资格。

还需限制两处滥用：申请入口可能枚举账号或轰炸邮箱，兑换入口可能被猜码。登录、恢复的外部文案、状态及明显耗时分支要避免暴露账号是否存在；需要跨账号、来源和整体容量的限速设计，单凭统一一句文案不能证明没有侧信道。[OWASP Authentication：Error Messages](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#authentication-and-error-messages)解释了这种差异因素。

重置地址应由可信配置构建，避免把请求中的任意 Host 当成目标域名；重置页避免把凭证泄露到日志、分析系统或外链引用信息。仅申请重置不应锁定账号或替换密码，否则攻击者只需知道账号名就能制造拒绝服务。具体 URL 与申请处理建议见 [OWASP Forgot Password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html#url-tokens)。

## 换掉密码后，还要关闭哪些入口

密码记录改变，不会自动删除独立的会话、[刷新令牌](../../glossary/security.md#security.token-lifecycle)或 API 凭证。对疑似接管的恢复，本文教学策略是撤销旧会话与刷新能力、使未完成的恢复凭证失效，并核对其他认证器和授权绑定；是否撤销独立 API 密钥还需按泄露范围与产品策略决定。正常的已认证密码修改可以有不同交互，但必须明确保留哪些能力及依据。

可以让密码更新、恢复凭证消费和账号凭证代次推进在同一事务提交；后续请求检查该代次，或撤销该账号的会话记录。若会话系统跨存储，还需可靠传递撤销意图、重试并观测传播，而不能把“消息已发出”当成全部节点已拒绝。纯离线验证的访问令牌、验证缓存和已在执行的业务各有剩余窗口，详见[会话撤销](authentication-sessions-and-tokens.md#session-revocation)。高风险恢复后的重新认证要求可参照 [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#reauthentication-after-risk-events)。

纸面并发例子：账号代次原为 7，恢复链接 R 绑定代次 7。请求甲完成重置，事务把代次改为 8 并消费 R；请求乙即使早已读到“R 未使用”，提交时也应因消费状态或代次冲突失败。旧会话 S 带代次 7，下一次权限敏感请求应按撤销契约拒绝。若甲的成功响应丢失，不能为了重试而重新开放 R；用户应经正常登录或受控状态查询确认，不能从“链接已使用”推断是哪一方完成了重置。这是设计预期，没有执行并发实验。

## 泄露响应应按暴露的能力决定

| 已知暴露材料 | 仍须处理的主要问题 |
| --- | --- |
| 密码校验库 | 评估算法、成本、密码风险与副本范围；控制线上攻击，按风险使受影响密码失效并组织安全重置 |
| pepper 或应用秘密 | 撤销和替换秘密，排查应用访问与其他秘密；不能只改数据库字段 |
| 活动会话或刷新凭证 | 直接撤销相应访问能力，确认各验证方生效时间；只重置密码未必足够 |
| 恢复邮箱、恢复码或 MFA 被改动 | 重新核实控制权，审查关联认证器与恢复设置，防止攻击者再恢复回来 |

此表是按能力划分的处置思路，不是完整事故手册。NIST 对确认受损认证器要求及时停用或失效，也区分有泄露证据时改密与例行周期改密，见 [§4.3](https://pages.nist.gov/800-63-4/sp800-63b/events/) 与 [§3.1.1.2](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)。在线撞库、钓鱼与离线破解不能只靠同一个 KDF 解决；相关在线防护见 [OWASP Credential Stuffing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)。

pepper 和账号恢复之外，服务凭据与加密密钥的分发、轮换、撤销及恢复副本责任，继续见[密钥与凭证生命周期](secrets-credentials-rotation-and-revocation.md)；更换秘密不自动撤回已建立的全部访问能力。

不同因子、抗钓鱼证明与认证器绑定/替换，继续见[MFA](multi-factor-authentication-passkeys-and-recovery.md)。密码恢复与因子恢复可能改变不同能力，不能把一个仍有效的会话或新填邮箱当作无条件移除其他认证器的证明。

## 自检、关联与证据范围

试着独立回答：独立盐为什么不能阻止同一个弱密码被猜中？恢复链接被两个并发请求提交时，哪一步决定只能成功一次？密码重置后，如果资源服务只离线验 JWT，旧访问能力何时才真正消失？设计验证时还应覆盖旧版本迁移与重置竞争、过期和错误用途凭证、撤销缓存陈旧、恢复渠道被改动及响应丢失。

- [OAuth 与 OIDC](oauth-oidc-and-pkce.md)：外部身份绑定也属于账号控制能力；本地密码重置不自动解除外部绑定。
- [事务隔离与 MVCC](../database/isolation-and-mvcc.md)：单次消费和版本迁移需明确并发提交条件，不能靠先查后写。
- [事故响应与复盘](../reliability/incident-response-recovery-and-postmortems.md)：凭证替换之后仍需确认业务恢复、受影响范围与处置闭环。

核查日期：2026-10-22。已核查文中链接的 [OWASP](../../glossary/security.md#security.threats) 指南、NIST SP 800-63B-4、RFC 9106 与 Django 5.2 的对应机制；正文为综合解释与设计推演。未运行 KDF 基准、真实登录、邮件、MFA、恢复或多节点撤销实验，未给出可直接投产的参数配置。密码策略、完整身份核验和具体合规评估仍需结合应用另行完成。
