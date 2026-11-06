---
id: "kb-api-webhook-signatures"
title: "Webhook 签名与重放：验签成功，为什么还不能直接执行业务"
kind: "concept"
domain: "api"
status: "evolving"
summary: "沿签名覆盖字节、密钥轮换与时间窗口区分来源验证和防重放，再用持久接纳、幂等消费及响应丢失解释可靠回调。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-api-idempotency", "kb-security-sessions-tokens"]
related: ["kb-messaging-delivery-semantics", "kb-messaging-outbox", "kb-security-object-authorization", "kb-api-contracts-pagination", "kb-security-secret-lifecycle"]
tags: ["webhooks", "signatures", "replay", "delivery", "idempotency"]
---

# Webhook 签名与重放：验签成功，为什么还不能直接执行业务

学习入口：支付平台的同一事件再次到达，签名和时间检查都通过，接收端能否再发一次货？不能由验签结果决定。签名限制谁能生成被接受的消息；新鲜度限制旧的签名消息何时仍可接受；事件[幂等](../../glossary/api.md#api.idempotency)约束同一业务事实重复到达后产生什么效果。这是三项不同的保证。

前置：[幂等性](idempotency.md)、[认证与令牌](../security/authentication-sessions-and-tokens.md)、HTTP 请求体与[数据库事务](../../glossary/database.md#database.isolation)。本文讨论接收 [Webhook](../../glossary/api.md#api.webhook)，用 GitHub 与 Stripe 官方协议说明差异，并参考 RFC 9421 的 HTTP 消息签名概念。两家协议不是 RFC 9421 的同一种实现，不能互换请求头或计算方法；流程为教学设计，未接入真实平台。

## 先分清传输、消息证明与业务权限

[HTTPS](../../glossary/networking.md#networking.tls) 为一次 TLS 连接提供保护；在通常只[认证](../../glossary/security.md#security.identity)服务器的配置下，任何客户端仍可向公开回调地址发请求。消息签名或 MAC 让接收端按预先建立的信任关系验证指定内容。若前方存在 TLS 终止代理，还需理解连接保护在哪一段结束。[RFC 9421 引言](https://www.rfc-editor.org/rfc/rfc9421.html#section-1)说明了连接保护与消息保护的范围差异。

| 机制 | 可以支持的判断 | 不自动支持的判断 |
| --- | --- | --- |
| [HMAC](../../glossary/security.md#security.hmac) | 在密钥未泄露、算法及验证正确的前提下，内容由共享密钥持有者认证且未被改动 | 不提供保密性；接收方也持有密钥，不能据此向第三方证明只有发送方可能生成它 |
| 非对称数字签名 | 用受信任公钥验证与对应私钥相关的签名 | 任意请求带来的公钥不能自己建立可信来源；签名也不加密载荷 |
| 当前业务校验与授权 | 该来源、事件、租户和对象关系是否允许当前状态转换 | 不能由“某把密钥验过”直接推出任意订单都可以完成 |

HMAC 的共享密钥模型见 [RFC 2104](https://www.rfc-editor.org/rfc/rfc2104.html#section-1)。本文的 HMAC-SHA-256 例子来自所选平台协议，不把该 RFC 的历史算法例举当作今天的算法推荐。签名在许多 Webhook 文档中是统称，实际采用 HMAC 时仍要按 MAC 的信任边界理解。

例如，接收端仍需将事件关联到受信任配置中的商户或安装范围，核对事件类型、对象归属和允许的状态变化。一个真实来源发来的测试事件不应触发生产发货；一份真实事件的对象 ID 也不能用来修改别的租户。继续读[对象级授权](../security/object-level-authorization.md)。

## 验证的是协议规定的字节，不是“看起来一样的 JSON”

JSON 对象在业务上相同，不表示表示它的字节相同：空格、键顺序、换行、转义与字符编码都可能改变。若协议签的是原始请求体，接收端先解析再重新[序列化](../../glossary/runtime.md#runtime.serialization)，通常会丢掉签名所依据的表示。应在 JSON 中间件改变内容前取得协议要求的原始体，并核对代理、解压与编码路径；这里的“原始”指协议定义的表示，不是 [TCP](../../glossary/networking.md#networking.transport) 分段或 HTTP 分块框架。

| 官方协议示例 | 认证计算覆盖什么 | 不能自行附会什么 |
| --- | --- | --- |
| GitHub `X-Hub-Signature-256` | 用 Webhook secret 对 payload 计算 HMAC-SHA-256，按规定十六进制表示及前缀比较 | 不能假定它还认证了任意时间、路径或其他请求头 |
| Stripe `Stripe-Signature` 的 v1 方案 | 对时间戳字符串、点号及原始请求体的连接结果计算 HMAC-SHA-256 | 不能把 JSON 中的事件创建时间替代请求签名时间 |

计算与比较依据分别见 [GitHub：Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) 与 [Stripe：手工验签步骤](https://docs.stripe.com/webhooks?verify=verify-manually#verify-manually)。接入时优先采用对应官方库，同时核实库所接收的是原始体、该端点的签名秘密以及正确的请求头。

另一些协议可以约定规范化表示，HTTP 消息签名也有自己的组件与编码规则。但规范化必须由双方协议明确规定；接收端不能验签失败后随意排序字段、删空白或换编码来“修复”签名。RFC 9421 的组件模型可供自建协议设计参考，不能让第三方平台自动改签更多字段。

## 密钥标识用于选择候选，不用于建立信任

一个服务可能同时接收多个提供方、环境、租户和端点。应先由可信路由与配置确定可接受的来源及密钥集合，再解析协议元数据。若存在 `keyid`，它只是查找已信任候选的标识；未知、已撤销或不属于当前上下文的密钥必须失败，不能临时按请求给出的地址下载任意公钥并信任它。依据见 [RFC 9421 §3.2](https://www.rfc-editor.org/rfc/rfc9421.html#section-3.2)。

协议不一定带密钥 ID。轮换时可在有期限的范围内接受当前与上一版本，或验证协议允许的多个签名；候选数量必须有界。Stripe 允许轮换重叠期内多把端点秘密活动，并为它们生成签名，具体行为见 [Manage webhook endpoints：Roll endpoint signing secrets](https://docs.stripe.com/events/manage-webhook-endpoints#roll-endpoint-signing-secrets-periodically)。这种能力不是所有提供方都有，不能自己要求一个尚不支持的请求头。

普通轮换需要协调发送与接收，使新密钥已部署再结束旧密钥接受期；紧急泄露响应则要决定何时拒绝旧密钥，以及拒绝后如何补收可信事件。无限延长双密钥期会使被盗旧密钥继续有效。日志记录密钥版本和失败类别即可，不记录秘密本身。

解析时限制请求体、头字段、签名数量与长度；只接受配置允许的算法、版本和编码。HMAC 候选值应在规范解码和长度检查后，用成熟库提供的常量时间比较函数核对，避免普通逐字符比较泄露匹配进度；非对称签名使用对应验证 API。GitHub 的验证文档明确建议安全比较。该函数只处理比较环节，不意味着整个端点耗时恒定，也不能补救错误密钥或漏验字段。

## 时间窗口缩短重放期限，不能清除窗口内重复

时间检查只有在时间字段也受认证时才能支撑新鲜度判断；攻击者若能改一个未签名时间头，就能给旧消息附上“现在”。接收策略应明确最大年龄、允许的未来偏差与可信时钟来源。窗口越小，[时钟偏差](../../glossary/distributed.md#distributed.clocks)和网络[延迟](../../glossary/performance.md#performance.latency-throughput)越容易误拒绝；窗口越大，截获消息可被重用的时间越长。

Stripe 把时间戳纳入签名，并在每次重新投递时生成新时间与签名。其库文档描述的默认容差是五分钟，而且容差设为 0 会关闭新鲜度检查；这些是该平台的具体行为，不是通用秒数配方。[Stripe：Preventing replay attacks](https://docs.stripe.com/webhooks#preventing-replay-attacks)。接入时应核对所用 SDK 版本对过去与未来时间的实际接受规则，不能假设一个“容差”参数一定同时限制两侧。

因此，两天前产生的事件可以在今天的合法补发中带着新签名到达；不能只按事件创建时间判断传输重放。反过来，攻击者在有效窗口内重复发送一份截获请求，MAC 和时间仍可能都通过。需要按协议记录受认证的 nonce 或稳定事件身份，结合持久状态限制重复；时间窗口本身没有记录“已经见过”。

GitHub 官方建议使用 `X-GitHub-Delivery` 区分投递，手动重投时该值不变，见[最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks#use-the-x-github-delivery-header)。但结合上面的体 HMAC 公式可以推导：这个头没有因为 payload MAC 而获得密码学认证。记录它能识别按原样重投的请求，不能单独抵御取得有效 payload/MAC 后任意改头的攻击者；GitHub 的这套签名也没有 Stripe 式签名时间。应明确威胁模型，保护请求副本，核对已认证载荷中的业务身份，必要时结合可信提供方查询或业务状态约束，不能为它宣称不存在的完整防重放能力。

## 事件身份、投递尝试与业务动作分别编号

同一事件可能有多次投递尝试；每次尝试的时间或签名可变，事件身份应按协议保持稳定。直接以签名为去重键，会把重新签名的合法[重试](../../glossary/api.md#api.retries)当成新事件。另一方面，不同事件也可能描述同一对象的同一业务结果；事件去重不能代替业务唯一性和状态转换约束。

接收端的事件作用域通常至少包括提供方、环境、可信账号范围及消费者用途；事件 ID 应取自已验证内容或有明确保护与核对规则的协议字段，不能只信一个任意头。相同 ID 携带冲突内容应隔离排查，而非覆盖旧记录。若合法重投会改变包装或新增尝试元数据，冲突判定应比较协议确定的不变字段，不能一律比较整份请求哈希。

Stripe 说明了重复事件 ID，以及不同 Event 对象仍可能反映重复业务结果的情况，见[重复事件处理](https://docs.stripe.com/webhooks#handle-duplicate-events)。但不能普遍规定“对象 ID + 类型永远唯一”：某些事件类型允许同一对象多次发生，仍须按业务语义、版本或动作标识建约束。事件也可能乱序，不能仅凭已认证的旧状态回滚当前业务。

## 把“验过了”“收下了”“处理完了”分成三个阶段

下面是**假定有持久 Inbox 表、本地业务事务与后台消费者**的教学方案，不代表某个提供方 SDK 自动实现了它。方案还要求事件键有可验证的身份依据；没有通用受认证事件 ID 的来源，需按事件类型结合可信载荷、提供方查询或业务状态约束，不能只采用任意投递头就宣称完整防重放：

```text
接收：限制输入 → 按协议验签和新鲜度 → 校验格式及可信账号范围
      → 以唯一事件键持久写入 Inbox（或确认已有相容记录）→ 提交 → 返回成功

消费：领取可恢复的待处理事件
      → 在同一事务中核对去重记录、当前业务前提并更新本地业务
      → 标记已处理；需要后续外部动作时保存 Outbox 意图 → 提交
```

这里成功响应表达的是“按契约持久接纳”，并非“所有业务副作用已经完成”。提供方通常需要快速收到成功响应；GitHub 的[最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks#respond-within-10-seconds)建议异步处理。选择异步接纳之后，系统就承担了任务恢复、积压告警、毒事件隔离与重试责任。

持久接纳不是“放进[进程](../../glossary/systems.md#systems.execution-units)内[队列](../../glossary/algorithms.md#algorithms.queues)”。如果先回成功、再保存，进程崩溃会让发送方认为已送达而接收方没有工作记录。若尚未确认持久提交，不能伪装成功；暂时故障如何响应与补收，要符合提供方实际重试契约。也不能假设每个平台都会无限自动重试，人工补发和对账需有独立入口。

| 故障窗口 | 恢复时应保持的行为 |
| --- | --- |
| 验签通过，Inbox 尚未提交就失败 | 没有宣称接纳成功；允许按提供方契约重投或补收 |
| Inbox 已提交，成功响应丢失 | 再投递经验证后命中已有记录，不再新建同一工作；返回约定成功 |
| 消费者更新业务前失败 | 事务回滚，任务可重新领取，不永久停在无法恢复的“处理中” |
| 本地业务与已处理标记提交，消费者随后崩溃 | 恢复读取已提交结果，不重复修改；两者不能拆成无保护的两次提交 |
| 外部通知或扣款超时 | 结果可能未知；使用外部幂等、查询或对账，不能由本地已处理标记推定未执行 |

[唯一约束](../../glossary/database.md#database.constraints)负责裁决[并发](../../glossary/systems.md#systems.concurrency)重复，而非先查后插。任务领取若有[租约](../../glossary/distributed.md#distributed.fencing)，过期重领仍可能遇到旧执行者，需保证提交条件与业务幂等；不能靠一个永不清除的 `processing=true` 获得恢复能力。概念基础见[投递与确认](../messaging/delivery-acknowledgements-and-idempotency.md)；跨外部副作用继续结合 [Outbox](../messaging/transactional-outbox.md)及外部结果查询。

去重保留期要覆盖实际自动重试、人工补发和恢复窗口，通常远长于一次签名时间窗口。删掉 Inbox 记录后，今天重新签名的旧事件仍可能再次被接受；高价值动作应另有业务唯一约束或长期结果依据。签名窗口到期也不等于已经持久接纳的工作必须删除：后台执行使用已建立的接纳证据和当前业务规则，不应在几小时后把原传输时间检查当作唯一消费资格。

共享验签秘密的版本发布与停止旧版本接受，需要跨发送方、验证方和缓存协调，继续见[密钥与凭证生命周期](../security/secrets-credentials-rotation-and-revocation.md)。

## 纸面推演与自检

教学事件 E 表示订单 O 已满足某项完成条件。首次投递通过验证，Inbox 提交后响应断线；发送方随后以新时间和新签名重投。两次验证都可以成功，Inbox 的唯一事件键使本地只产生一份工作。消费者把 O 的状态变化和已处理标记一同提交，随后崩溃；恢复不能再次产生相同本地效果。若业务还要调用仓库发货 API，这个保证到本地事务就结束，仍须让发货使用稳定动作标识或支持查询恢复。

试着独立回答：相同 JSON 重新序列化后为什么可能验签失败？同一事件在有效时间窗内重复十次，验签和去重各在哪一步发挥作用？Inbox 提交后响应丢失时，为什么既需要允许重投，又不能重复执行业务？进一步验证应覆盖错误密钥、旧密钥退役、改动体字节、改未签字段、未来时间、窗口内并发重复、去重清理、乱序和外部结果未知。

- [HTTP 契约与分页](contracts-and-pagination.md)：事件格式、版本、错误及成功响应含义也需要明确契约。
- [对象级授权](../security/object-level-authorization.md)：来源有效不等于目标对象与当前动作被允许。
- [Transactional Outbox](../messaging/transactional-outbox.md)：在业务事务里保存后续执行意图，投递与外部效果仍需各自恢复。

核查日期：2026-10-22。已核查 GitHub、Stripe 官方页面与 RFC 2104、RFC 9421 支持的签名、覆盖范围、轮换、新鲜度与重投机制；GitHub 未签头的边界是根据已公开公式作出的推导。Inbox、消费者事务与故障表为教学综合，未启动 HTTP 服务、运行 SDK 验签、数据库并发、队列或真实支付回调实验。
