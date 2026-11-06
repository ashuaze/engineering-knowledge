---
id: "kb-security-secret-lifecycle"
title: "密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效"
kind: "concept"
domain: "security"
status: "evolving"
summary: "沿生成、分发、使用、轮换、撤销和销毁区分秘密版本、验证方接受范围与历史数据恢复责任。"
created: "2026-10-22"
updated: "2026-10-23"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-security-sessions-tokens"]
related: ["kb-security-password-recovery", "kb-api-webhook-signatures", "kb-security-object-authorization", "kb-reliability-incident-response", "kb-security-mtls-service-identity", "kb-api-styles-gateway", "kb-security-authorization-models", "kb-cache-object-storage"]
tags: ["secrets", "credentials", "rotation", "revocation", "envelope-encryption"]
---

# 密钥与凭证生命周期：换了秘密，旧访问为什么仍可能有效

学习入口：配置中心已经保存新 API 密钥，所有服务也重新部署了，为什么被盗旧密钥仍能调用接口？“保存了新版本”“消费者开始使用新版本”“验证方停止接受旧版本”是三个状态。密钥与凭证生命周期需要把这三者连接起来，还要说明泄露、控制面故障及恢复时怎样收敛。

前置：[认证、会话与令牌](authentication-sessions-and-tokens.md)。本文讨论应用秘密与加密材料的管理责任，使用官方产品机制作为例子，不提供可直接执行的轮换脚本，也不将一个服务的撤销能力推广到其他系统。所有编号和时间线均为教学假设。

## 先说清楚正在换哪一种材料

| 对象 | 主要用途与保护责任 | 换掉它不自动改变什么 |
| --- | --- | --- |
| 用户密码与密码校验记录 | 用合适的密码派生机制验证候选，不以取回原密码为目标；[pepper](../../glossary/security.md#security.pepper) 是另行保密的材料 | 已有[会话](../../glossary/security.md#security.sessions)、刷新凭证和独立 API 凭证 |
| API key、数据库口令、共享[认证](../../glossary/security.md#security.identity)秘密 | 作为持有能力或认证材料，限制主体、用途、资源和有效期 | 接收端接受列表、已建立连接、被另行签发的令牌 |
| 加密密钥 | 保护数据或包装其他密钥，保存恢复所需的密文与版本关系 | 旧密文的字节、已泄露明文、攻击者已经复制的旧密钥 |
| 私钥与公开证书 | 私钥需要保密；证书承载公开的身份与公钥绑定，分发仍需验证信任和完整性 | 旧证书何时不再被验证方接受、已有连接何时结束 |

表中是责任区分，不是可互换的存储格式。密码校验与 pepper 的迁移条件见[密码存储与账号恢复](password-storage-and-account-recovery.md)，共享 [HMAC](../../glossary/security.md#security.hmac) 秘密的双方信任关系见 [Webhook 签名与重放](../api/webhook-signatures-replay-and-delivery.md)。不能把“证书公开”理解为对应私钥可以公开，也不能把 [KDF](../../glossary/security.md#security.passwords) 当成任意应用秘密的通用加密方案。

## 生命周期记录应能解释每次状态转换

下面是教学责任表；各产品未必使用同一套状态名称：

| 阶段 | 应保存或确认的依据 | 典型失败 |
| --- | --- | --- |
| 生成或取得 | 可信生成路径、负责人、用途、环境、版本、允许主体及期限 | 用可预测字符串作秘密，同一材料跨生产与测试复用 |
| 受限分发 | 谁以什么身份取得哪一版，经什么受保护通道交付 | 把所有秘密注入每个[进程](../../glossary/systems.md#systems.execution-units)，复制到[镜像](../../glossary/devops.md#devops.containers)或调试输出 |
| 使用 | [最小权限](../../glossary/security.md#security.trust)、验证条件、实际使用版本、失败类别 | 取得秘密即获得全部业务权限，日志泄露秘密原文 |
| 轮换 | 新版本生成、目标系统设置、使用验证、消费者切换、旧版退役的分别证据 | 只更新秘密库，忘记数据库或接收端 |
| 撤销与泄露处置 | 哪些能力须停止，哪些验证方已生效，未完成项如何追踪 | 重启应用后宣称被盗副本已失效 |
| 归档、恢复和销毁 | 历史数据依赖、备份位置、恢复授权、撤销记录与最终清理条件 | 新密文可读后就删除仍被旧备份依赖的密钥 |

[OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)的访问控制、审计与生命周期章节支持限制秘密暴露和记录创建、轮换、撤销、过期等事件。审计记录应能关联主体、版本、目标、操作与结果，而不记录秘密值；“谁读过秘密”与“谁使用它完成了业务”也要从不同系统的记录关联。

加密密钥还要区分“停止保护新数据”与“仍允许处理历史数据”。[NIST SP 800-57 Part 1 Rev. 5](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf)的 §5.3 和 §7–8 解释 cryptoperiod、密钥状态与管理阶段；用于加密新数据的期间可以早于允许解密历史数据的期间结束。期限要按用途、使用量、暴露风险和恢复责任确定，不能从某个示例天数推导所有秘密都应同周期轮换；这些说明不构成合规宣告，也不替代疑似泄露时的处置。

## HSM、KMS 和秘密库分别控制什么

| 组件职责 | 提供的主要边界 | 仍需应用和运维承担什么 |
| --- | --- | --- |
| HSM 等密码模块 | 在特定硬件保护边界内保存或使用密码材料 | 调用身份、允许的操作、业务授权及主机被接管后的使用风险 |
| KMS | 管理密码密钥及其使用策略，提供受控密码操作和生命周期接口 | 谁能加解密、何时撤销、历史数据依赖及应用侧明文范围 |
| Secret Manager / 秘密库 | 保存、发放和管理应用秘密版本，可组合轮换流程 | 下游是否真正更新、消费者是否重载、旧凭据何时拒绝 |

这些职责可以组合，不能把名称当成同义词。[AWS KMS 概述](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)说明其密钥由 HSM 保护并经服务接口使用；这不表示应用中所有数据库口令也都留在 HSM 内。秘密库向应用返回一项秘密后，应用内存、错误转储和下游连接仍有自己的暴露面。

## 谁给秘密管理服务提供最初的身份

应用不能凭空访问秘密库：它需要平台授予的角色、[工作负载身份](../../glossary/security.md#security.workload-identity)或其他初始凭据，管理服务也需要在目标系统中执行授权操作的资格。把一把长期“取秘密总钥匙”写回代码，只是移动了问题。应同时限制领取者可以取得的秘密，以及领取后可执行的资源操作；轮换器能修改目标账号，也必须受目标范围约束。

在合适平台上，可让工作负载通过角色或联合身份取得短期凭据，减少分发长期访问密钥。[AWS IAM 临时凭据说明](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html)明确了 STS 生成、有限期限及到期拒绝使用的机制。这依赖事先配置的信任与权限；攻击者若仍控制工作负载或换取凭据的身份，可能继续领取新凭据。短期只限制相应凭据的寿命，不自动证明泄露发现后已经提前撤销。

控制面[可用性](../../glossary/reliability.md#reliability.availability)也是依赖。秘密库或身份服务不可达时，新实例可能无法启动，旧实例也可能无法完成凭据续期。工程策略应明确：哪些仍有效的凭据可在既定期限内继续使用，哪些操作必须拒绝，以及怎样进行受控恢复。不能为了恢复可用性而无限延长缓存或退回更高权限的固定秘密。[OWASP](../../glossary/security.md#security.threats) 的 “Downtime, Break-glass, Backup and Restore” 章节也要求事先准备受保护的恢复路径；恢复入口本身仍需权限、审计和定期验证。

## 信封加密：换包装不等于换数据密钥

[信封加密](../../glossary/security.md#security.envelope-encryption)先用数据加密密钥 DEK 保护数据，再用密钥加密密钥 KEK 包装 DEK。[AWS Encryption SDK 概念](https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html)说明数据密钥、包装密钥及加密数据密钥随消息保存的关系。以下为抽象教学模型，省略库内部的派生、算法套件和封装格式，不能据此自行实现加密：

| 教学记录 | 含义 | 恢复时依赖 |
| --- | --- | --- |
| `C1 = Encrypt(DEK1, 数据1)` | 数据密文 | 正确的 `DEK1`，以及算法要求的 nonce、认证标签和关联数据 |
| `W1 = Wrap(KEK1, DEK1)` | 被包装的 DEK | 对应 KEK 的受控解包能力 |
| `(C1, W1, KEK引用, 格式版本, 相关元数据)` | 应用保存的恢复材料关系 | 元数据与密文匹配；引用本身不能授予解密权限 |

解密方向是“根据受信任策略选择 KEK → 解包 W1 得到 DEK1 → 验证并解密 C1”。新的默认 KEK 不会自动改写这个元组：重新包装 DEK 可以只改变 W1 和相应元数据；真正更换 DEK 保护既有数据，则要按协议重新加密数据并安全发布对应恢复材料。业务数据与其包装元数据若分开更新，崩溃恢复必须避免组合出无法解密的一半新、一半旧记录。

具体到 [AWS KMS 密钥轮换](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)，轮换既有逻辑 KMS key 的材料，会让新加密使用当前材料，并保留解密旧密文所需的材料；它不会自动轮换数据密钥或重加密既有数据。若 `DEK1` 已泄露，仅轮换 KEK 不能弥补；即使重加密了线上副本，也不能追回攻击者已经复制的旧密文与旧密钥。

## 轮换要同时改变保存、使用和接受状态

轮换过程需要可恢复地记录“进行到哪一步”。[AWS Secrets Manager 的四阶段轮换](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html)分别创建待用版本、改变目标服务凭据、测试、再完成版本标签切换。`AWSCURRENT` 是秘密库的版本标签，不是“每个应用已重载且旧连接已关闭”的证明。该流程是产品例子，不是所有系统都能原子接受两把秘密。

下面假定某个 API 协议支持两版共享秘密；各实例有受控的版本接受列表，且可以观测版本使用。数字是教学假设：

| 时间 | 计划轮换动作 | 尚不能推出什么 |
| --- | --- | --- |
| 10:00 | 创建 K2，作为待用版本保存 | 生产者或验证方已开始使用 K2 |
| 10:05 | 核对所有验证方已支持限定集合 `{K1,K2}` | 旧版已失效，或者不可达实例已更新 |
| 10:10 | 生产者切为 K2，确认必要实例和在途处理策略 | 仍持有 K1 的攻击者无法生成有效请求 |
| 10:20 | 结束 K1 接受期，清理相应缓存并核对验证方实际状态 | 未确认或有旁路的验证方也已拒绝 K1 |

若某实例没更新，应记录退役尚未完成，不能只看部署任务成功。双版本窗口降低计划轮换造成的误拒绝，也保留了旧秘密的能力；窗口应有期限、完成条件和失败处置。对于 pepper，迁移可能还需要用户密码；对于数据库，是否支持新旧双凭据要按产品与账号策略另行设计，不能照搬此表。

再假设 10:12 发现 K1 泄露。沿用计划等到 10:20，会继续保留 8 分钟的预定接受窗口；泄露响应应重新决定拒绝时间、可信补发或服务降级。即使 10:13 已提交撤销，若某验证方最后在 10:12 刷新、缓存严格存活 5 分钟且没有主动失效，它仍可能到 10:17 才停止接受 K1。缓存有效期是 5 分钟，本例在提交撤销后还可能接受 4 分钟；这些数字依据明确的缓存假设，不是产品保证。缓存还能续期、节点时钟或旁路不受控时，不能据此给出上界。

撤销何时生效，应从验证方实际拒绝和传播进度确认。已经受理的业务是否取消、旧秘密是否还能换取其他令牌、攻击者能否领取 K2，都要分别处理。继续读[会话撤销](authentication-sessions-and-tokens.md#session-revocation)及[事故响应](../reliability/incident-response-recovery-and-postmortems.md)，不要把“轮换成功”作为泄露调查的结束条件。

## 动态凭据的结束仍要连到目标系统

[Vault 数据库秘密引擎](https://developer.hashicorp.com/vault/docs/secrets/databases)按配置角色动态生成数据库凭据，并用凭据租约管理更新与撤销；独立凭据有助于把数据库用户名关联到调用实例。应限定生成角色的权限，并监控目标数据库撤销是否成功。管理服务的数据库连接资格也属于需要保护和恢复的凭据。

[Vault 的 `lease` 说明](https://developer.hashicorp.com/vault/docs/concepts/lease)要求动态秘密带有凭据租约；续期请求不等于获准所请求的期限，消费者必须看返回结果。普通 KV 秘密不因为响应里出现时长就自动拥有相同撤销语义。凭据租约到期、撤销请求、后端完成角色或权限变更，以及已有数据库会话结束，应分别核查插件、撤销语句和目标接口。

例如 [PostgreSQL 18 角色属性](https://www.postgresql.org/docs/18/role-attributes.html)把密码用于需要密码的建连认证。由此不能把“密码已经替换”当作“已有认证连接已全部关闭”的证据；应用[连接池](../../glossary/api.md#api.pool)、活跃会话与在途事务还需单独处置。类似地，撤销刷新能力不自动清除已签发[访问令牌](../../glossary/security.md#security.token-lifecycle)；资源端缓存与离线验证仍受各自契约限制。

## 删除名称、停用和销毁分别影响什么

| 动作 | 改变的主要状态 | 不能单独证明什么 |
| --- | --- | --- |
| 删除配置名、别名或本地副本 | 某个查找入口或持有位置消失 | 目标系统已撤销，其他副本、内存和备份均消失 |
| 停用、拒绝使用权限 | 受相应验证或服务控制的后续操作被限制 | 应用已丢弃明文密钥，所有派生凭据与已有会话终止 |
| 销毁密钥材料 | 相应密码能力不再可从该材料恢复 | 无备份或其他包装路径；历史明文与被盗副本已消失 |
| 恢复秘密库或业务备份 | 某个过去状态重新出现 | 旧撤销仍生效，新身份、版本与密文依赖仍匹配 |

以 AWS 生成材料的对称客户托管 KMS key 为例，[删除机制](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html)有强制等待期，停用与最终删除也不同；删除后不能恢复该 key。销毁前要盘点仍依赖它的密文和备份，不能只看最近线上写入。另据 [KMS key 不可用对数据密钥的影响](https://docs.aws.amazon.com/kms/latest/developerguide/unusable-kms-keys.html)，限制 KMS 调用不会立即清除已经取出的明文数据密钥；下一次需要 KMS 解包时才可能暴露依赖。

恢复方案应同时核对密文、包装元数据、权限、撤销记录与身份信任。恢复旧秘密库不能无条件重新启用已因泄露撤销的 K1；保留旧解密能力也应限制为约定的历史处理用途。备份需要受限访问和恢复验证，销毁需要覆盖纳入管理的副本及保留策略。若无法确认所有恢复材料与副本，记录剩余风险，而不是把删除一条记录写成“已彻底清除”。

凭据仍有效时，对象关系和策略也可能已变化，见[权限模型与策略传播](authorization-models-policy-distribution-and-revocation.md)。转交给客户端的限时存储请求能力，另见[对象存储与预签名访问](../cache-search/object-storage-versions-uploads-and-presigned-access.md)；停止签发、拒绝新请求和终止在途传输不可互相替代。

## 自检、关联与核查范围

1. 秘密库已把 K2 标为当前版，为什么旧 K1 仍可能认证成功？
2. KEK 材料轮换、DEK 重新包装和数据重新加密，分别改变元组的哪一部分？
3. 10:12 刷新的五分钟验证缓存，在 10:13 提交撤销后能否立刻证明拒绝旧秘密？
4. [动态数据库凭据](../../glossary/security.md#security.dynamic-credentials)到期或被撤销后，应从哪里确认已有连接和在途事务的结果？
5. 为什么恢复旧秘密库、销毁旧 KEK 和保留历史密文必须共同评估？

[对象级授权](object-level-authorization.md)说明凭据有效后仍需核对当前资源范围。本文涉及工作负载取得凭据和证书材料的管理；双向证书校验与身份映射见[mTLS 与服务身份](mtls-service-identities-and-trust-boundaries.md)，不同[接口契约](../../glossary/api.md#api.contracts)与入口职责见[API 风格与网关](../api/api-styles-contracts-and-gateway-boundaries.md)。[MFA](../../glossary/security.md#security.mfa)、完整 [PKI](../../glossary/networking.md#networking.tls) 撤销实现及真实轮换/恢复验证仍需继续积累。

核查日期：2026-10-22。NIST 固定为 SP 800-57 Part 1 Rev. 5，仅用于生命周期、使用期间与 cryptoperiod 概念；PostgreSQL 固定为 18。OWASP、AWS KMS / Encryption SDK / Secrets Manager / IAM 文档为当日读取的滚动资料；Vault 文档为当日标示的 `v2.x (latest)`，具体插件和部署版本仍需复核。正文只核查链接所支持的机制，状态表、信封元组与两种轮换时间线是教学综合。未访问云账户或真实秘密，未运行部署工具、轮换、撤销、数据库连接、密文迁移、销毁、备份恢复或故障实验，不据此证明任何实际系统已完成撤销或满足合规要求。
