---
id: "kb-networking-cdn-waf"
title: "CDN 与 WAF：边缘命中和请求放行分别证明什么"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "沿边缘缓存键、身份范围、失效和源站路径，区分 CDN 分发、WAF 检查与应用授权的责任。"
created: "2026-10-22"
updated: "2026-10-23"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-nat-proxy-lb", "kb-api-conditional-requests"]
related: ["kb-security-object-authorization", "kb-security-origin-csrf", "kb-security-xss", "kb-security-sql-injection", "kb-security-mtls-service-identity", "kb-api-styles-gateway", "kb-cache-search-cache-aside", "kb-security-secret-lifecycle", "kb-cache-load-coalescing", "kb-cache-object-storage"]
tags: ["cdn", "waf", "cache-key", "origin", "authorization"]
---

# CDN 与 WAF：边缘命中和请求放行分别证明什么

学习入口：账户页接入边缘缓存后，源站访问量下降，为什么还可能把甲的数据交给乙？请求通过 [WAF](../../glossary/networking.md#networking.cdn-waf)，为什么仍可能读取别人的订单？CDN 负责分发和按规则复用响应，WAF 按可见请求及防护策略采取动作；能否复用、当前是否有权限和业务是否允许执行，必须分别证明。

前置：[代理与连接分段](nat-proxies-and-l4-l7-load-balancing.md)、[HTTP 条件请求](../api/conditional-requests-and-cache-validation.md)。本文为概念和来源核查；拓扑、请求、数字与故障时序是纸面教学设计。AWS、Cloudflare、CRS 资料均为 2026-10-22 读取的滚动文档快照，没有部署 CDN/WAF、修改 [DNS](../../glossary/networking.md#networking.dns) 或发送防护测试流量。

## 先画清边缘、缓存与源站

CDN 是把内容交付能力分布到多个节点的设施，边缘缓存是常见机制；节点选择、回源层次及动态请求处理取决于实际产品和配置，不能假定每次都到地理最近节点、所有内容都能缓存，或所有节点共享一份缓存。WAF 是应用层请求防护机制，可与 CDN、代理或网关组合，但两者不是同义词。

下面只表示一种需要设计和核验的逻辑路径，不是某个产品的固定过滤器顺序：

```text
客户端 → 边缘入口：必要的访问检查、WAF 策略、缓存查找
                     ├─ 可合法复用的命中 → 返回所存表示
                     └─ 未命中或需要验证 → 受控回源路径 → 源站应用
另一路径：客户端 ──直连公开源站──> 源站应用（可能绕过边缘策略）
```

命中且不回源时，源站不会为这次请求重新执行应用检查。因此，受保护内容若允许边缘复用，必须让必要的访问检查也覆盖命中路径，并明确失效时限；否则应选择不共享或绕过相应缓存。仅在源站检查登录，不能保护一份已被错误共享的账户响应。

[CloudFront 缓存策略说明](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)描述了命中时从边缘返回对象、减少回源的机制；[Cloudflare WAF 概览](https://developers.cloudflare.com/waf/)描述按请求属性及规则过滤流量。这里引用具体能力，不推导所有产品具有相同阶段或默认设置。网关与应用职责另见[API 风格与网关](../api/api-styles-contracts-and-gateway-boundaries.md)。

## 缓存键决定谁被当作同一次读取

缓存键把请求归入可复用响应的集合。设计时先问哪些差异会改变表示，再问哪些请求确实允许共享；减少键的维度可能提高命中率，也可能合并本不等价的请求。不能只追求更高命中率。

| 教学请求 | 可能改变结果的条件 | 必须明确的策略 |
| --- | --- | --- |
| 公开的 `/assets/app.v7.js` | 发布版本、编码 | 文件名版本及编码变体与实际存储一致 |
| 公开的 `/catalog?lang=zh` | 语言、币种、查询参数 | 输出受影响的维度进入复用判断；无关跟踪参数能否忽略需验证 |
| `/account` 或按权限裁剪的订单列表 | 用户、租户、当前权限、字段范围 | 默认不按 URL 共享；若设计受控缓存，隔离和每次访问检查都要成立 |
| `POST /orders/o-7/cancellations` | 请求身份、输入、业务状态 | 不能当作一份公开读取表示复用；业务[幂等](../../glossary/api.md#api.idempotency)另有提交协议 |

反例：甲带登录凭据访问 `/account`，源站返回甲的余额；边缘只按路径存储。乙访问同一路径时命中，源站没有机会拒绝这次错误复用。事后加 WAF 的注入规则，也不会让余额重新属于乙。把可伪造的 `tenant` 头直接加入键，同样不能证明请求者拥有该租户权限。

HTTP 的目标 URI、方法和 `Vary`（响应声明哪些请求字段参与变体选择）等规则见 [RFC 9111 §2、§4.1](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.1)。具体 CDN 还要核对缓存策略；CloudFront 的[策略文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html)区分加入键的字段与仅转发给源站的字段。源站已经按某字段生成不同内容，但边缘只转发、不区分它，会留下不等价响应被复用的风险。`Vary` 不能替代产品配置核验。

路径、查询及头字段的解析和规范化也应对齐。若边缘把两个请求当作相同，源站却解释为不同内容，攻击者可能让错误响应进入其他人的复用范围；这是需要防范的缓存污染边界。此处是设计推论，未构造或执行污染载荷。[RFC 9111 §7.1](https://www.rfc-editor.org/rfc/rfc9111.html#section-7.1)另列缓存污染风险。

## 能存、可复用与已经撤回是三件事

不带字段参数的 `private` 限制共享缓存存储；`no-cache` 要求复用前成功验证；`no-store` 施加不存储和不用于其他请求的要求。这些不是加密、[授权](../../glossary/security.md#security.identity)或远程删除已泄露数据的机制。带 `Authorization` 的请求在共享复用上另有明确允许条件；[Cookie](../../glossary/security.md#security.sessions) 本身不自动表达完整的隔离策略。具体 HTTP 边界见 [RFC 9111 §3.5、§5.2.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-3.5)，验证器与 304 继续见[条件请求正文](../api/conditional-requests-and-cache-validation.md)。

还要核对边缘 TTL（缓存有效期限）覆盖规则。CloudFront 的[最小 TTL 说明](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html)明确：配置大于零的最小 TTL 时，即使源站包含 `no-cache`、`no-store` 或 `private`，该产品仍可按最小期限缓存。敏感路径的实际行为不能只凭源站头部推断；这是特定配置风险，不能推广成所有 CDN 忽略 HTTP 指令。

TTL 到期表示需要按相应规则重新判断可用性，不等于全部副本已删除。主动清除边缘对象、发布新文件名、浏览器更新和撤销访问资格也有不同范围。[CloudFront 失效文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html)区分失效与版本化名称，并提醒边缘失效后用户或企业代理仍可能保留旧版本。

撤销访问资格需要让实际执行检查的入口停止接受旧权限或旧凭据；清除内容副本不能替代这一步。若边缘复用授权判断、验证密钥或令牌状态，控制面已撤销到各实例实际拒绝之间仍可能有传播与缓存窗口，需要明确其起点、失效机制和可接受上界。已经通过检查且正在发送的响应也不保证自动中止，应另定在途处理规则；已经下载的字节无法通过撤销追回。相关接受范围见[凭证生命周期](../security/secrets-credentials-rotation-and-revocation.md)。本文未测定撤销窗口或验证中断行为。

教学时间线：t0 发布 `app.v7.js`；t1 发布 `app.v8.js` 并更新入口引用；t2 旧页面仍请求 v7。新文件名帮助新入口选择 v8，不会追溯改写旧页面，也不会收回已经下载的字节。若需删除敏感内容，还要查清所有缓存层、仍指向旧版本的入口及允许访问的路径；单次清除成功不能作为全链路撤回证明。

## 命中率要说明分母，回源要看放大

纸面设定：每秒 1000 次边缘请求，80% 符合缓存条件；这部分中 90% 命中。假定其余请求全部回源、每个未命中只回源一次，没有预刷新、[重试](../../glossary/api.md#api.retries)或其他流量，则：

```text
不可缓存回源 = 1000 × 20% = 200 次/秒
可缓存但未命中 = 1000 × 80% × 10% = 80 次/秒
总回源 = 200 + 80 = 280 次/秒
```

“可缓存请求命中率 90%”在本例不等于整体回源只剩 100 次/秒。多节点冷启动、批量失效、回源重试和派生查询还可能使负载超过上述理想模型。平均命中率也不能证明某个[热点](../../glossary/performance.md#performance.contention)过期瞬间的负载可承受；应另看时间窗口、回源并发、[排队](../../glossary/performance.md#performance.queueing)和依赖容量，参见[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。

[同键加载合并](../../glossary/cache-search.md#cache-search.coalescing)可以减少特定范围的重复加载，但不能把跨边缘节点、跨[进程](../../glossary/systems.md#systems.execution-units)的一切回源自动合成一次，也不替代正确的共享范围与接纳上限。机制细节见[缓存加载合并与惊群控制](../cache-search/cache-load-coalescing-and-stampedes.md)；CDN 策略、应用缓存与数据源需要分别验收。

## WAF 看到了什么，又没有判断什么

WAF 可以按规则检查路径、头字段和可解析的请求内容，匹配后记录、阻断或采取产品支持的其他动作。规则放行只说明当前可见内容和执行过的规则没有产生阻断结果，不能证明无攻击、已获对象权限或业务提交安全。

| 边界 | 教学反例 | 应由谁继续保护 |
| --- | --- | --- |
| 业务权限 | 有效登录者把订单 ID 换成他人的 ID，语法完全正常 | 应用的[对象级授权](../security/object-level-authorization.md) |
| 查询执行 | 请求没有命中已知注入特征，但后端仍拼接 SQL | [参数化查询](../security/sql-injection-parameters-and-query-structure.md)及受控查询结构 |
| 浏览器执行 | 富文本保存请求被放行，后来被页面作为危险 HTML 输出 | [上下文编码、净化与危险汇控制](../security/xss-contexts-sinks-and-browser-defenses.md) |
| 检查可见性 | 请求体超出检查窗口，或未按预期解析 | 明确超限、解析失败策略及应用自己的大小/类型限制 |
| 流量成本 | 单次合法请求要求昂贵计算 | 身份限额、实际成本接纳、并发与依赖保护 |

[AWS WAF 超限处理文档](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html)给出一个具体例子：宿主服务只交付限定范围用于检查，允许继续后送到后端的仍可能是完整请求。Continue、Match、No match 不是同义词；规则动作和整体策略决定最终结果。不能把“产品支持请求体检查”理解为所有字节都被所有规则检查过。

误报是合法请求被判成攻击，漏报是应拦截的请求未被识别。富文本编辑等合法输入可能触发通用规则；调优时需要保留脱敏后的规则 ID、路径、参数和判定依据，再把例外限制到已确认范围。不是看到误报就全局关掉一类防线，也不能把提高灵敏度当作无需代价的修复。[CRS 官方调优说明](https://coreruleset.org/docs/2-how-crs-works/2-3-false-positives-and-tuning/)解释通用规则、误报及细粒度排除；[Cloudflare Managed Rules](https://developers.cloudflare.com/waf/managed-rules/)说明例外、覆盖和规则更新的交互。规则升级后仍需复核例外和合法流量。

## 防护成立还要保证请求经过它

如果源站公开接受同样请求，调用方可能直接连接源站，绕过边缘 WAF、限额或访问检查。应核对源站实际允许哪些入口、是否认证到指定分发路径、其他域名和备用入口是否执行同等要求；仅把公开域名指向 CDN 不会关闭其他入口。

[CloudFront 的源站访问限制文档](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-origin.html)通过让兼容 AWS 源站只接受指定 CloudFront 的认证请求，说明一种具体的来源约束机制。是否支持以及怎样绑定分发身份取决于源站类型；共享出口 [IP](../../glossary/networking.md#networking.transport) 或一个可伪造的请求头，不能自行升级成唯一可信来源。

来源约束证明“请求从允许的基础设施抵达”，仍不证明最终用户拥有订单权限。边缘终止 [TLS](../../glossary/networking.md#networking.tls) 时，回源连接及原调用方上下文也各有信任条件，见[mTLS 与服务身份](../security/mtls-service-identities-and-trust-boundaries.md)。防护日志应区分边缘拒绝、缓存返回、回源与应用拒绝，并控制令牌、Cookie 和敏感正文的采集范围；单看源站没有记录，无法区分合法命中和边缘提前拦截。

源站对象的键/版本、业务发布和客户端限时能力，继续见[对象存储与预签名访问](../cache-search/object-storage-versions-uploads-and-presigned-access.md)。边缘复用、存储接受及业务撤销是不同路径，失效操作不能追回已经下载的字节。

## 五道自检与核查范围

1. 甲乙访问同一个 URL 时，哪些表示差异和访问规则决定响应能否共享？只在源站查权限会遗漏哪条路径？
2. 边缘向源站转发了一个影响响应的请求头，但缓存键忽略它，会发生什么？为什么增加 `Vary` 或 tenant 头不能单独证明安全？
3. 最小 TTL、主动边缘失效、新文件名和访问资格撤销各影响什么？为什么已下载内容不能靠一次清除收回？
4. 在上述 1000 次/秒模型中，280 次/秒怎样得到？哪些预设变化会让实际回源更高？
5. WAF 未匹配、未完整检查、规则例外和直接源站入口分别留下什么边界？应用还须怎样执行权限、输入及容量约束？

核查日期：2026-10-22。RFC 9111 固定为 2022-06 的 HTTP Caching，用于缓存复用、身份请求、指令与污染边界；AWS CloudFront/WAF、Cloudflare 和 CRS 为当日实际读取的滚动说明，不把套餐、当前规则集或宿主服务限制推广成所有实现。没有读取账户配置、部署产品、清除真实缓存、攻击请求、抓包、压测或验证规则误报率。拓扑、账户反例、发布时序和 280 次/秒模型是教学综合；实际效果应以选定产品、配置和端到端证据另行核验。
