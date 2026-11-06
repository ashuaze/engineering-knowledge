---
id: "kb-security-authorization-models"
title: "权限模型与策略传播：规则改了，哪些请求仍可能被允许"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分角色、属性与关系模型，沿策略、事实、缓存和执行边界解释授权决定及撤销何时真正生效。"
created: "2026-10-23"
updated: "2026-10-26"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-security-object-authorization", "kb-security-sessions-tokens"]
related: ["kb-security-secret-lifecycle", "kb-security-mtls-service-identity", "kb-cache-search-cache-aside", "kb-database-isolation-mvcc", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-security-mfa", "kb-security-service-delegation", "kb-security-trust-threat-models", "kb-api-resource-validation"]
tags: ["authorization", "rbac", "abac", "rebac", "policy-distribution"]
---

# 权限模型与策略传播：规则改了，哪些请求仍可能被允许

学习入口：管理员移除了用户的团队成员关系，为什么某个服务仍允许他下载文档？规则没有更新、关系副本落后、旧允许结果仍有效，以及请求早已进入执行，都会造成相似现象。权限模型表达判断依据；安全地实施变更还要约束事实来源、传播、缓存和实际执行。

前置：[对象级授权](object-level-authorization.md)、[认证、会话与令牌](authentication-sessions-and-tokens.md)。本文解释常见服务端[授权](../../glossary/security.md#security.identity)机制；规则、关系图、时间线和数字均为纸面教学设计，未部署策略引擎、修改真实权限或执行撤销实验。NIST 资料用于概念，不作为本系统的合规结论。

信任位置、身份与权限的区别见[信任边界与威胁建模](trust-boundaries-least-privilege-and-threat-modeling.md)；结构合法与字段可写的区别见[资源模型与输入边界](../api/resource-models-input-validation-and-write-boundaries.md)。

## 角色、属性与关系分别表达什么

授权至少涉及主体、目标对象、动作以及判断所需上下文。主体可以是用户或服务；[访问令牌](../../glossary/security.md#security.token-lifecycle)能被验证，不代表其中旧角色仍满足当前访问条件。

| 模型 | 主要表达方式 | 教学例子 | 需要额外说明的边界 |
| --- | --- | --- | --- |
| [RBAC](../../glossary/security.md#security.access-control)，基于角色的访问控制 | 将权限分配给角色，再把主体分配到角色；还可有角色层级和约束 | 账务复核员可以复核付款 | 角色在哪个租户有效，是否允许自审，能处理哪些对象 |
| ABAC，基于属性的访问控制 | 按主体、对象、动作和环境属性求值 | 同租户且密级许可覆盖文档，才允许读取 | 属性由谁提供、是否可信、何时更新，未知值怎样处理 |
| [ReBAC](../../glossary/security.md#security.rebac)，基于关系的访问控制 | 用主体与对象、对象与对象之间的关系及组合规则推导访问 | 团队成员可读团队拥有的文件夹中的文档 | 哪些关系可继承，交集/排除怎样定义，遍历与一致性范围 |

[NIST RBAC 归档概念页](https://csrc.nist.gov/Projects/Role-Based-Access-Control)说明角色、权限、层级和约束；归档页面不提供当前产品保证。[NIST SP 800-162](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-162.pdf)定义 ABAC 的判断输入。[OpenFGA 的 ReBAC 概念](https://openfga.dev/docs/authorization-concepts)则以对象关系及父对象权限说明关系模型。这里对照表达方式，不把它们视为三个互斥技术栈。

例如给“每个团队的每个文档”分别建一个角色，可能让角色数量和授予关系难以维护；把团队关系与对象继承分开通常更容易解释。但 ReBAC 不等于 RBAC 的角色层级：它还可以表示文件夹归属、直接分享、群组成员等关系；关系是否授予权限由规则决定，不是图上有一条路径就允许。

下面是一份教学关系事实和组合规则，语法不属于具体引擎：

```text
Alice 是 Team-A 的成员
Folder-7 属于 Team-A
Document-9 的父对象是 Folder-7

允许读取 = 身份有效 AND 主体与对象处于允许的租户范围
         AND（直接获准读取 OR 属于有读取资格的父对象团队）
         AND 对象未被禁止访问
```

这里同时使用身份、租户/状态属性与对象关系。直接分享不能绕过强制租户限制；加入 deny 规则后，还需明确它与 allow 的组合优先级、继承和缺失值语义。不同引擎不会自动替业务选择同一套冲突处理。

## 判定、执行、规则与事实不是同一职责

PDP（策略决策点）计算访问决定，PEP（策略执行点）在读取或修改资源的路径落实决定。规则由管理入口维护；成员、归属和状态等事实则有各自权威来源。[SP 800-162 §2.3.2](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-162.pdf)分别说明 PDP、PEP、PIP（策略信息点）和 PAP（策略管理点），这些是职责划分，不要求部署为四个独立服务。

| 要确认的对象 | 本例的可信依据 | 不能据此推出什么 |
| --- | --- | --- |
| 当前主体 | 服务端已验证的身份与委托上下文 | 请求里自报的 user_id/角色已可信 |
| 对象与动作 | 实际读取/修改的对象、租户与具体操作 | 检查过文档读取就允许下载所有附件或修改文档 |
| 策略版本 | 该 PDP 实际激活的规则及适用范围 | 管理端显示发布成功，所有节点就已更新 |
| 属性与关系事实 | 对应权威服务、数据版本或可接受快照 | 用了新规则就自然得到新成员关系 |
| 执行约束 | 资源端采用的决定、条件与失败处理 | PDP 返回 allow，内容就已安全地输出 |

网络 API 上的 PEP 也要认证并限定其可查询的范围；PEP 传来的租户、对象归属不能仅复制用户参数。[进程](../../glossary/systems.md#systems.execution-units)内 PDP 与应用共享相应信任边界。服务连接已通过 [mTLS](mtls-service-identities-and-trust-boundaries.md)，仍需判断服务能代表谁、操作哪些资源。

## 集中规则管理，不等于集中或实时的每次判断

| 组织方式 | 主要收益 | 需要承担的成本 |
| --- | --- | --- |
| 远程集中 PDP | 共用判断逻辑和观测入口 | 请求[延迟](../../glossary/performance.md#performance.latency-throughput)、依赖故障、事实存储/副本仍可能陈旧 |
| 本地 PDP，分发规则与数据 | 减少远程判定依赖 | 各节点激活进度、版本组合及撤销传播 |
| 本地规则，判断时查询事实 | 规则执行靠近业务，按需取得输入 | 事实查询的期限、权限和一致性，不因“查询”就保证最新 |

[OPA Philosophy](https://www.openpolicyagent.org/docs/philosophy)将策略决定与业务服务解耦，应用仍负责执行查询结果；[OPA Bundles](https://www.openpolicyagent.org/docs/management-bundles)提供策略和数据的下载/激活机制，并明确分发属于最终一致。其 revision、[ETag](../../glossary/api.md#api.conditionals) 等用于识别相应内容或下载状态，不能单独证明所有实例都已经使用最新事实。

规则和事实可能以不同渠道变化：`P12` 仍写着“团队成员可读”，撤销的只是关系事实从 `R6` 变为 `R7`。只发布策略版本，或只观察策略没有变化，都不会完成此次撤销。若分开发规则与输入结构，还要约束相容组合，不能让新规则在旧字段缺失时意外放行。

分发通道需限制谁能改规则、谁能写关系；制品来源验证与激活审查用于防止未经授权或错误版本进入节点。签名正确也不证明规则含义正确或足够新。这里的职责取舍参考 [OWASP 策略与数据分发指南](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Policy_And_Data_Distribution_Cheat_Sheet.html)，不假设任意引擎都支持同一传播方式。

## 缓存允许结果，必须保留它所依赖的输入范围

只用 `user_id + object_id` 当缓存键，会混淆租户、读写动作、委托、对象版本或环境条件。教学设计可把主体/委托、租户、对象与动作、策略版本、相关事实版本和必要上下文纳入决定的适用范围，并为结果保留原始失效期限。

但“键里包含版本”只区分已知版本：如果节点始终只知道 `R6`，它仍可能继续查到 `R6` 的旧允许结果。系统还需要可信的更新进度、可验证的最低版本要求，或符合新鲜度要求的权威查询。读取旧副本后给结果加上今天的生成时间，也不能把旧事实变新。

策略输入里的时间、设备状态、对象归属和组成员关系都可能影响结果；任一关键输入超出允许范围，就不能只因缓存未满或命中率高而继续使用。拒绝结果也可能过期，影响新授予权限的可用性。[Cache-Aside 与失效](../cache-search/cache-aside-and-invalidation.md)解释迟到回填；授权缓存更要防止旧判断在失效后重新进入有效集合。

## 用明确假设复算撤销窗口

设 t=0 时，权威关系库已提交“移除 Alice”，规则 P12 不变。只讨论此后的新访问接纳，教学模型作如下强假设：全部相关节点均受控；该变更至多 4 秒发布，发布后至多 5 秒被所有 PDP 激活；此后所有新取得的事实快照均已反映这次撤销，没有其他陈旧输入或倒退。一次允许结果的 30 秒期限锚定其所用事实快照的取得时刻，不从返回、缓存回填或命中时重新计时；PEP 每次使用都检查原期限，无过期续用与旁路，计时可靠。

```text
全部 PDP 停止取得撤销前事实：4 + 5 = 9 秒以内
最后一份旧允许结果的失效上界：9 + 30 = 39 秒
```

| 时间 | 教学状态 | 判断 |
| --- | --- | --- |
| t=0 | R7 已提交，N2 仍使用 R6 | 管理端完成不表示 N2 已拒绝 Alice |
| t=8.9 | N2 最后一次取得旧快照并生成允许结果 | 原期限为 t=38.9，晚返回也不能顺延 |
| t=9 | 所有 PDP 已激活 R7 | 不再取得 R6 快照；已有结果与在途求值仍保留原失效期限 |
| t≥39 | 旧结果都已过期 | 按上述前提，不再以这些旧结果接纳新访问 |

39 秒是这套教学协议的保守上界，不是 OPA、OpenFGA 或网络的保证。若每次命中滑动续期、事实来源仍可回旧值、后台重试没有期限，或分区使传播无法满足上限，就不能从“缓存 [TTL](../../glossary/cache-search.md#cache-search.invalidation)=30 秒”推出撤销上界。必须先定义超出新鲜度时哪些受影响动作停止接纳，再验证真正的 PEP 行为。

这个上界也不取消 t=2 已被允许的下载、事务或外部操作；已经发出的内容无法追回。权限撤销与 [会话/凭据撤销](secrets-credentials-rotation-and-revocation.md)可能需要同时处理，但撤销登录状态不等同撤销所有对象关系，反之亦然。

## 新内容、旧决定与执行时变化怎样衔接

另一个纸面失败时序是：先移除 Bob 的文档权限，再写入新内容，读取服务却用移除前的允许结果返回新内容。只检查“缓存还在有效期内”无法满足“新内容必须尊重此前权限变化”的要求。[Zanzibar 2019 论文 §2.2](https://www.usenix.org/system/files/atc19-pang.pdf)专门讨论这类次序问题，并以一致性令牌约束检查快照与内容版本之间的关系；这属于论文所设计的协议，不是任意策略版本字符串都能提供的能力。

即使重新请求 PDP，也存在“判断允许 → 权限变化 → 业务写入”的检查与使用间隙。若要求撤销与修改有明确先后关系，需要让资源端以事务、受控条件或经过设计的版本协议协调最终接受点；把检查挪到执行前仍不自动形成跨服务原子提交，见[事务隔离与 MVCC](../database/isolation-and-mvcc.md)。外部支付、邮件等动作还需保留业务身份、结果查询和 [幂等规则](../api/idempotency.md)，不能靠权限拒绝推断已受理动作没有发生。

后台作业、分批导出和批量对象访问需要定义执行主体、每批/每项检查与停止条件；开始时的 allow 不是永久能力。列表过滤须与实际对象/字段规则一致，并明确分页和总数暴露的范围。图关系过深、查询超限或输入缺失应进入明确的拒绝/错误分支，不能截断遍历后当作允许。记录实际策略、事实依据和拒绝原因，有助于区分错配与传播落后；审计不应复制敏感原始属性。

不可达、未初始化、未知字段和求值异常也不是 allow。[OWASP 授权指南](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)强调默认拒绝和逐请求检查。保留已验证旧版本可能帮助服务继续判断，但只有策略、事实和结果均仍在明确新鲜度范围内才可使用；网络 [超时与重试](../reliability/timeouts-and-retry-budgets.md)必须服从该范围，不能无限延长旧权限。

认证因子和合格认证的新鲜度见[MFA](multi-factor-authentication-passkeys-and-recovery.md)，委托主体、执行者及下一跳范围见[跨服务委托](service-delegation-token-exchange-and-audience.md)。规则/事实版本、认证时间和凭据期限相互关联，但交换凭据或完成 [MFA](../../glossary/security.md#security.mfa) 都不会自动刷新全部权限与撤销状态。

## 五道自检与核查范围

1. 角色、属性与关系分别表达什么？团队文件夹的例子为什么可以组合模型，又为什么不能仅凭图上可达或某个角色就跨租户放行？
2. PDP、PEP、规则管理和事实来源各负责什么？集中 PDP、[mTLS](../../glossary/security.md#security.mtls) 或发布任务成功，为什么都不单独证明最终执行已使用当前权限？
3. 规则 P12 不变、关系 R6→R7 时，授权缓存应区分哪些输入？为什么键里有版本仍不足以发现撤销，旧判断晚回填又该怎样处理？
4. 4 秒、5 秒和 30 秒的假设怎样得出 39 秒上界？滑动续期、旧事实、传播中断与已接纳下载分别使哪条结论失效？
5. 新内容读取、业务写入和后台导出各如何面对旧决定或检查后变化？为什么重新查询、[幂等](../../glossary/api.md#api.idempotency)重试与拒绝返回也不证明跨服务撤销原子生效？

核查日期：2026-10-23。本文只核查下列资料所支持的概念，不声称任何真实部署符合该协议或达到了撤销时限。

| 一手资料与版本范围 | 实际核查部分 |
| --- | --- |
| [NIST RBAC 项目归档页](https://csrc.nist.gov/Projects/Role-Based-Access-Control) | 角色/权限分配、层级与约束；页面已归档，仅作概念背景，不引用历史市场/成本数字 |
| [NIST SP 800-162，2014，含 2019-08-02 更新](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-162.pdf) | ABAC 主体/对象/动作/环境输入、属性来源及 §2.3.2 的 PDP/PEP/PIP/PAP 职责；不作法规适用判断 |
| [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts) | 核查日滚动页面的 ReBAC 对象关系解释；不据此声明具体服务器/SDK 的一致性或遍历限制 |
| [OPA Philosophy](https://www.openpolicyagent.org/docs/philosophy)、[Bundles](https://www.openpolicyagent.org/docs/management-bundles) | 滚动页面的决定/执行解耦、动态规则/数据、最终一致分发，以及 revision/ETag 的内容识别；未执行命令或核查某部署配置 |
| [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | 核查日滚动指南的[最小权限](../../glossary/security.md#security.trust)、默认拒绝、逐请求校验和模型取舍；未采用其历史 ASVS 链接推定当前版本 |
| [OWASP Policy and Data Distribution](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Policy_And_Data_Distribution_Cheat_Sheet.html) | 核查日滚动指南的权威输入、新鲜度、分发/请求传入、激活进度与故障；上文时间和缓存协议为独立教学设计 |
| [Zanzibar，USENIX ATC 2019](https://www.usenix.org/system/files/atc19-pang.pdf) | §2.2 的 ACL/内容因果次序和一致性令牌约束；未推广论文生产规模、延迟或可用性指标 |

未执行策略引擎、身份/关系服务、缓存/失效、并发撤销、[网络分区](../../glossary/distributed.md#distributed.partition)、混合版本、后台导出或外部副作用实验；没有新增或重跑已有[对象级授权](../../glossary/security.md#security.tenant-isolation)实验。来源规则、纸面机制和真实执行证据应分别验收。
