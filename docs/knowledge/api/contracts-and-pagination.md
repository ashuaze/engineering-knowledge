---
id: "kb-api-contracts-pagination"
title: "HTTP 契约与分页：接口能调用，为什么仍会漏数据"
kind: "concept"
domain: "api"
status: "evolving"
summary: "从方法语义和输入输出契约出发，解释稳定排序、Offset 与游标分页、并发变化及兼容性边界。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-api-idempotency", "kb-security-sessions-tokens", "kb-security-object-authorization", "kb-database-indexes-plans", "kb-database-isolation-mvcc", "kb-engineering-test-scopes", "kb-api-conditional-requests", "kb-engineering-contract-compatibility", "kb-runtime-types-validation", "kb-algorithms-sorting-boundaries", "kb-api-styles-gateway", "kb-api-resource-validation", "kb-api-graceful-shutdown"]
tags: ["http", "contracts", "pagination"]
---

# HTTP 契约与分页：接口能调用，为什么仍会漏数据

学习入口：列表接口每次都返回 200，翻完所有页却出现重复或缺漏，契约少规定了什么？前置知识：HTTP 请求、JSON、基本 SQL 与排序。本文讨论请求式 JSON API；方法与错误参考 HTTP RFC，Schema 参考 [OpenAPI](../../glossary/api.md#api.contracts) 3.1.2，游标示例限定 PostgreSQL 18 的行比较，未执行 SQL 或启动示例服务。

资源、动作及写入许可见[资源模型与输入边界](resource-models-input-validation-and-write-boundaries.md)；服务退出期间的接纳、排空和结果确认见[优雅关闭与请求排空](graceful-shutdown-draining-and-inflight-outcomes.md)。

## 契约包含行为，不只有字段

接口契约约束调用方可以发送什么、服务端如何解释，以及响应提供什么保证。除了字段类型，还应明确身份与对象范围、必填和默认值、时间与单位、资源上限、错误、[重试](../../glossary/api.md#api.retries)，以及版本兼容策略。

[OpenAPI 3.1.2](https://spec.openapis.org/oas/v3.1.2.html)提供路径、操作、参数、请求体、响应和 Schema 等描述结构，可供文档、工具与验证使用。但写了文档不表示[运行时](../../glossary/runtime.md#runtime.virtual-machine)已经校验，也不能仅靠字段 Schema 证明[授权](../../glossary/security.md#security.identity)、事务或分页一致性。

例如 page_size 必须是整数仍不够：是否允许 0、上限是多少、超限拒绝还是截断、缺省取多少，都需要约定。时间字段要说明时区与精度；未知字段与空值如何处理也要明确，避免客户端认为更新成功，服务端却静默忽略关键输入。

## HTTP 方法与错误为调用方提供共同语义

HTTP 的 safe 语义是调用方不请求改变服务端状态，不是服务器完全没有日志等副作用。[幂等性](../../glossary/api.md#api.idempotency)约束重复请求的预期效果，不要求每次响应相同；GET、PUT、DELETE 的标准语义与 POST 不同。不能在 GET 上设计扣款动作，再依靠“客户端只点一次”保护它。方法语义见 [RFC 9110 §9](https://www.rfc-editor.org/rfc/rfc9110.html#section-9)。

POST 可通过额外应用协议提供幂等能力，但键作用域、保留期和冲突规则需要另行说明。超时不证明服务端没有执行，是否重试还需结合该操作的副作用与预算，详见[幂等性](idempotency.md)。

错误也属于契约。调用方需要区分输入不合法、身份或权限不满足、资源冲突和临时不可用，不能把所有失败都包装成 200 后让人猜。采用何种状态及业务错误码应与 HTTP 语义和实际处理一致。

[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html)提供 [Problem Details](../../glossary/api.md#api.problem-details) 结构及 `application/problem+json` 媒体类型。type 用于识别问题类型，detail 面向当前发生的问题，不应要求客户端解析可变的人类说明来判断分支。应用仍要定义稳定的问题类型、扩展字段与重试条件，也不应在错误中泄露凭证或内部敏感信息。

## 分页首先需要稳定且完整的排序规则

“按创建时间倒序”若允许相同时间，多行之间仍可能没有固定次序。可以增加唯一且非空的 id 作为次级排序，并明确方向与空值规则。PostgreSQL 的 [LIMIT/OFFSET 文档](https://www.postgresql.org/docs/18/queries-limit.html)要求约束成可预测的唯一顺序，否则取出的子集可能不稳定。

教学设定：列表按不可变的数值排序键倒序为 A(10)、B(9)、C(8)、D(7)，每页 2 条。

| 时刻 | 数据与请求 | 结果 |
| --- | --- | --- |
| 1 | 原列表，OFFSET 0 LIMIT 2 | A、B |
| 2 | 在最前插入 X(11) | 当前顺序为 X、A、B、C、D |
| 3 | 当前列表，OFFSET 2 LIMIT 2 | B、C，B 重复 |

另一个独立情形：从原列表出发，第一批返回 A、B 后删除 A，当前顺序变为 B、C、D；从 OFFSET 2 继续会取 D，从而漏过 C。排序确定只解决一次查询的次序，不会冻结多次请求之间的数据。Offset 还可能为跳过大量行付出成本，但它支持直观的页码定位，不能只以“是否用了游标”评价全部需求。

## 游标指定位置，仍需限定适用条件

Keyset 分页把上一页最后一个返回项的排序键作为边界。下面只演示已经确认访问范围的后续页查询：id 是唯一且非空的主键，created_at 非空，二者在遍历期间不变，排序统一为倒序。

```sql
SELECT id, created_at, title
FROM documents
WHERE tenant_id = :authorized_tenant
  AND owner_id = :principal_id
  AND (created_at, id) < (:last_created_at, :last_id)
ORDER BY created_at DESC, id DESC
LIMIT :page_size_plus_one;
```

参数以绑定方式传入；principal 与 authorized_tenant 由服务端验证，示例的“仅本人文档”是教学授权策略。第一页没有上一页边界，应走不带该条件的分支。PostgreSQL 的[行比较规则](https://www.postgresql.org/docs/18/functions-comparisons.html#ROW-WISE-COMPARISON)按字段次序比较；如果排序键可空或方向混合，就不能直接套用这个表达式。

为判断是否还有下一页，可在当前可见结果中多取一条：返回前 page_size 条，把额外项仅用于判断 has_more，下一游标取最后一条实际返回项的键。若把那条未返回的额外项当作排他边界，下一次就会跳过它。这是算法设计说明，不是本仓库已执行的分页结果。

客户端可收到不透明游标，由服务端存储状态或采用有完整性保护的编码。游标协议应绑定或验证过滤条件、排序规则与访问范围，并规定失效行为；单纯 Base64 编码不防篡改。即使游标签名有效，每次请求仍要重新检查当前权限，不能把它当成访问许可。

## 游标不是一致快照，兼容性也要检查行为

在上述不可变排序键的前提下，位置边界能避免前方插入导致 Offset 整体位移，但不会把整个结果集固定在某个历史时刻。后方新插入的记录可能进入后续页，删除、过滤字段或权限变化也会改变结果。排序键如果会变动，还可能让同一记录跨过边界，造成重复或缺漏。

需要“某一时刻完整导出”时，应另行设计快照或固定结果集及其生命周期，承担状态保存与版本保留成本。单独加一个 created_at [截止时间](../../glossary/reliability.md#reliability.retry-budget)通常不足以冻结修改、删除和权限。不同请求的读取可见性见[事务隔离与 MVCC](../database/isolation-and-mvcc.md)；total 若另做查询，也要说明是否与当前页共享快照，不能默认两者必然一致。

契约演进同样会影响行为：新增必填参数、改变默认排序、修改空值语义或替换游标格式，都可能使原客户端失败。增加响应字段常有兼容空间，但严格解析器可能拒绝未知字段；给枚举增加值，也可能破坏穷举处理。版本号只是标识，仍需规定旧游标、旧客户端和弃用窗口怎样处理。

资源、命令与类型查询契约的取舍，以及入口治理和业务执行各自承担什么，继续见[API 风格与网关](api-styles-contracts-and-gateway-boundaries.md)。协议或类型定义不会自动补齐分页一致性、对象权限与未知结果处理。

## 自检与后续验证

排序的稳定性、完整次级键与二分边界可配套读[排序与二分查找](../algorithms/sorting-binary-search-and-boundaries.md)。稳定算法保留输入同键顺序，不替代本篇跨页排序与数据一致性的契约；本次仅补概念关联，没有新增分页实验。

为列表接口记录：授权过滤范围、唯一排序、空值规则、默认与最大页长、游标生成和失效、[并发](../../glossary/systems.md#systems.concurrency)变化语义、错误及兼容承诺。再构造同时间多条数据、前方插入、删除、排序键变化、跨租户游标与权限撤销，写出预期后再做集成验证。

试着解释：唯一排序为什么仍不能让 Offset 跨请求稳定？多取一条后应拿哪条记录生成下一游标？完整性保护的游标为什么不是授权？接口 Schema 通过为什么仍可能漏数据？

核查日期：2026-10-19。本文依据 RFC 9110、RFC 9457、OpenAPI 3.1.2 和 PostgreSQL 18 文档；排序历史为纸面推演，SQL 为说明性示例，未验证真实 HTTP 服务、游标保护或数据库并发行为。

- [认证、会话与令牌](../security/authentication-sessions-and-tokens.md)：先建立可信主体，再接受受保护请求。
- [对象级授权](../security/object-level-authorization.md)：列表、统计和后续页都要保持当前访问范围。
- [索引与执行计划](../database/indexes-and-query-plans.md)：验证访问路径与成本，不把游标等同于一定高效。
- [测试层次与替身](../engineering/test-scopes-and-doubles.md)：区分 Schema、契约与真实依赖行为的证据范围。

继续阅读 [HTTP 条件请求](conditional-requests-and-cache-validation.md)，区分[缓存验证](../../glossary/api.md#api.conditionals)的 304、条件保存的 412，以及两者与授权、分页和重试契约的关系；该篇为来源核查与纸面请求。

怎样把接口约定交给消费代码与提供方共同验证，见[契约测试与版本兼容](../engineering/contract-testing-and-compatibility.md)。该篇区分描述、匹配规则与具体版本组合，示例矩阵未运行；本篇的分页与并发边界仍需各自的行为证据。

静态声明怎样与实际输入建立边界，见[类型系统与运行时校验](../runtime/type-systems-and-runtime-validation.md)。[类型断言](../../glossary/runtime.md#runtime.type-system)或[泛型](../../glossary/runtime.md#runtime.generics)返回值不替代运行时字段、权限和业务检查；该篇校验器未执行，也不扩展本篇的接口验证证据。
