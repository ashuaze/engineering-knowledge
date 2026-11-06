---
id: "kb-api-conditional-requests"
title: "HTTP 条件请求：缓存验证与并发更新怎样共用版本依据"
kind: "concept"
domain: "api"
status: "evolving"
summary: "用 ETag、If-None-Match 与 If-Match 区分 304 缓存验证和 412 条件更新，解释强弱验证器、原子比较及身份缓存边界。"
created: "2026-10-20"
updated: "2026-10-22"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-api-contracts-pagination", "kb-security-sessions-tokens"]
related: ["kb-api-idempotency", "kb-security-object-authorization", "kb-security-origin-csrf", "kb-frontend-routing-cache", "kb-database-isolation-mvcc", "kb-networking-cdn-waf"]
tags: ["http", "etag", "cache", "concurrency"]
---

# HTTP 条件请求：缓存验证与并发更新怎样共用版本依据

学习入口：已经拿到一份文档，怎样少传一次正文，又避免保存时覆盖别人刚完成的编辑？前置：[HTTP 契约](contracts-and-pagination.md)、身份与对象[授权](../../glossary/security.md#security.identity)。本文依据 HTTP Semantics 与 HTTP Caching 解释两种不同目的；请求片段和时间线是教学推演，未运行 HTTP 服务或数据库[并发](../../glossary/systems.md#systems.concurrency)更新。

## ETag 标识选定表示，不是对象访问凭证

HTTP [条件请求](../../glossary/api.md#api.conditionals)让服务端在执行动作前检查请求携带的前提。ETag 是[实体](../../glossary/architecture.md#architecture.domain-model)标签，可作为选定表示的验证器；客户端应把引号内的值视为不透明数据，不自行推算后一个版本。它不要求是内容哈希，也不天然具有递增顺序或跨资源可比性。定义见 [RFC 9110 §8.8](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8)。

同一个业务对象可以有不同语言、编码或权限裁剪的表示，不能只凭业务 ID 就认定响应字节相同。服务端生成强验证器时，必须符合相应表示变化的要求；客户端也不能把 A 文档的 ETag 搬到 B 文档，或用它证明当前用户有读取权。

本文把一个教学文档当前表示的标签写作 "v7"，只是为了便于阅读，不暗示 ETag 标准要求数字版本。

## 读取：If-None-Match 让已有正文参与验证

设客户端已经保存了一份可用于当前请求的响应正文和标签：

```http
HTTP/1.1 200 OK
ETag: "v7"
Cache-Control: private, no-cache

（文档的 JSON 正文）
```

下一次需要验证这份缓存时，可以发出：

```http
GET /documents/17 HTTP/1.1
If-None-Match: "v7"
```

在请求本身通过正常检查且条件适用的前提下，当前表示匹配时，GET/HEAD 的条件结果是 304；不匹配时，本例 GET 通常取得包含新正文的 200 响应，HEAD 则仍不返回正文。304 没有正文，用来让缓存根据响应信息更新并复用所存表示，不是“文档内容变成了空”。相关规则见 [RFC 9110 §13.1.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.2)与 [RFC 9111 §4.3](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.3)。

如果应用只保存了标签却丢失正文，304 不会帮它重新获得缺失的数据；需要按契约重新获取完整表示。错误用户、错误语言或已经失效的应用缓存，也不能因为标签相同就随意复用。

## 新鲜度与验证器解决不同问题

新鲜度决定缓存何时可以直接复用；验证器帮助确认所存表示是否仍可使用。带 ETag 不表示每次都要回源，设置 max-age 也不表示响应永远不会改变。

| 机制或指令 | 在此处的含义 |
| --- | --- |
| max-age | 为缓存新鲜度提供期限依据，具体复用还受其他规则约束 |
| 不带字段参数的 no-cache 响应指令 | 再次复用前须成功验证，并不禁止存储 |
| no-store | 对适用的 HTTP 缓存施加不存储要求，不会自动清除所有应用状态 |
| 不带字段参数的 private 响应指令 | 共享缓存不得存储；不是内容加密或用户权限检查 |

这些响应指令的边界见 [RFC 9111 §5.2.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2)。本文的 private, no-cache 示例选择允许私有缓存保存但在复用前验证；是否适合某类敏感数据，需要由应用策略决定，不能照抄为所有接口的默认值。

Vary 指出选择响应时还需考虑哪些请求字段，例如语言或按 Origin 改变的 [CORS](../../glossary/security.md#security.origin) 许可。Authorization 请求的响应在共享缓存中另有严格复用约束；[Cookie](../../glossary/security.md#security.sessions) 本身也不自动表达正确的缓存隔离策略。身份相关表示必须明确可否存储、作用范围及账号切换后的处理，不能把“加了 Vary”当作完成权限设计。规则见 [RFC 9111 §3–4](https://www.rfc-editor.org/rfc/rfc9111.html#section-3)。应用数据缓存与浏览器恢复的区别见[前端路由与缓存](../frontend/routing-state-and-cache-lifecycles.md)。

## 写入：If-Match 把保存前提交给服务端

两个人都读取 "v7"，随后分别修改。单纯依靠“先读后写”，服务端看不出第二次保存是基于旧内容还是有意覆盖。If-Match 可以表达“只在当前表示仍匹配时执行”：

```http
PUT /documents/17 HTTP/1.1
If-Match: "v7"
Content-Type: application/json

（客户端准备保存的新文档）
```

| 时刻 | 教学操作 | 结果 |
| --- | --- | --- |
| 1 | 甲、乙都读到 "v7" | 两人持有相同基础 |
| 2 | 甲携带 If-Match: "v7" 保存 | 原子检查成功，状态变为新版本 "v8" |
| 3 | 乙仍携带 If-Match: "v7" 保存 | 前提不成立，返回 412，不覆盖甲的修改 |
| 4 | 乙重新读取、比较并决定如何合并 | 重新提交需要新的明确前提 |

这里选择冲突时返回 412 的[接口契约](../../glossary/api.md#api.contracts)。HTTP 还规定了服务端能够确认该修改已经成功时的有限成功处理，不能只看旧标签就猜测发生过相同操作。If-Match 的规范见 [RFC 9110 §13.1.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1)。

比较当前版本和提交修改必须在同一个原子边界内完成，例如数据库条件更新或适当事务。先查版本、退出事务、再无条件写入，会在中间留下竞争窗口。所有相关写路径还必须一致维护版本与表示，否则头部语法正确也不能防止丢失更新。这个实现要求是从教学时间线推导的设计约束，本文未验证具体数据库实现。

## 强弱验证器与时间条件不能随意替换

强标签如 "v7"，弱标签带 W/ 前缀，如 W/"v7"。弱验证器允许表示之间不具备相同的强等价保证；If-Match 使用强比较，不能把弱标签原样拿来作为匹配成功的条件。If-None-Match 使用弱比较，适合其缓存验证等用途。比较规则见 [RFC 9110 §8.8.3.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.3.2)。

Last-Modified 和日期条件也可以参与验证，但生成依据与时间精度限制不同，不能默认能区分同一秒内的多次写入。多个条件并存时有规定的优先次序，例如 If-None-Match 优先于 If-Modified-Since；不应在服务端随意挑一个通过的条件。日期验证与次序见 [RFC 9110 §13.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.2)。

## 条件更新不替代授权、幂等性和业务不变量

服务端应先完成正常请求检查，再在执行前评估条件。不能因 If-None-Match 命中就绕过认证返回一个可复用的敏感响应，也不能把持有某个 ETag 当作写权限。HTTP 检查顺序见 [RFC 9110 §13.2.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.2.1)；业务层仍需[对象级授权](../security/object-level-authorization.md)。

教学反例：甲的修改已经提交为 "v8"，但成功响应丢失；甲用旧 "v7" [重试](../../glossary/api.md#api.retries)后收到 412，只能知道旧前提不再满足，不能据此证明第一次没有成功，也不能无条件覆盖。需要结合操作标识、结果查询或[幂等协议](idempotency.md)判断，不能把 If-Match 当作完整的重试去重方案。

条件写入还只保护契约覆盖的表示和原子边界。两条不同资源分别匹配版本，不会自动保证跨资源余额或名额约束；这些仍需事务、隔离和业务设计，见[隔离与 MVCC](../database/isolation-and-mvcc.md)。跨源脚本若要读取 ETag 或发送条件头，还需按 CORS 规则明确暴露响应头和允许相应请求头，详见[同源与跨站请求](../security/origins-cors-and-csrf.md)。

共享边缘的缓存键、产品 TTL 覆盖、清除和身份路径，继续见[CDN 与 WAF](../networking/cdn-edge-caches-and-waf-boundaries.md)。源站头部与验证器不单独证明所有边缘配置或访问路径正确。

## 自检与验证范围

为同一个文档分别写出“缓存仍有效”“缓存需要更新”“别人先保存”“成功响应丢失”四条时间线，区分 200、304、412 各说明什么。再回答：弱 ETag 为什么不能直接用于 If-Match？客户端丢失正文后能否只靠 304 恢复？退出后旧标签为什么不能继续证明访问权？

2026-10-20 核查 RFC 9110、RFC 9111 及关联浏览器规则，状态为 source-checked。本文没有执行真实 HTTP 条件请求、代理缓存、CORS 响应头读取或数据库条件写入实验；未把已有[幂等](../../glossary/api.md#api.idempotency)、库存实验扩展为本协议的实测证据。
