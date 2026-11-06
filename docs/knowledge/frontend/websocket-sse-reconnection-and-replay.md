---
id: "kb-frontend-realtime-replay"
title: "WebSocket 与 SSE：连接恢复以后怎样补回消息"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分浏览器实时通道、传输与业务确认，说明 SSE 游标、WebSocket 本地缓冲、补读去重、慢消费及身份变化。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-connection-states", "kb-runtime-event-loop"]
related: ["kb-frontend-routing-cache", "kb-performance-backpressure", "kb-api-idempotency", "kb-security-origin-csrf", "kb-messaging-delivery-semantics"]
tags: ["websocket", "sse", "reconnection", "replay", "acknowledgement"]
---

# WebSocket 与 SSE：连接恢复以后怎样补回消息

学习入口：通知页面显示“已连接”，却少了几条更新；重连后有些通知又重复出现。实时连接提供一条当前通道，完整恢复还需要历史、游标和业务处理规则。

前置：[TCP/TLS 与连接状态](../networking/tcp-tls-and-connection-states.md)、[事件循环](../runtime/event-loop-and-microtasks.md)。本文限定浏览器原生 [WebSocket](../../glossary/frontend.md#frontend.realtime) 与 EventSource，协议基础参考固定 RFC 与 WHATWG 滚动标准，不展开第三方实时库。消息编号和恢复流程是教学协议设计，没有创建连接、发送事件或执行故障注入。

## 先按通信方向和恢复职责选通道

| 机制 | 浏览器看到的基本能力 | 应用仍需设计 |
| --- | --- | --- |
| WebSocket | 建立后双向发送文本或二进制消息 | 断线后重建、订阅恢复、历史补读、消息与业务确认 |
| SSE / EventSource | 经 HTTP 事件流接收服务器文本事件，符合规则时自动重连 | 服务器保留历史、解释游标、权限与缺口处理；客户端上行另用请求等通道 |
| 普通请求或轮询 | 每次请求得到对应结果，周期性检查变化 | 轮询间隔、重复与差异、总预算及版本比较 |

WebSocket 基础帧与连接模型见 [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455.html)；浏览器 API 另以 [WHATWG WebSockets](https://websockets.spec.whatwg.org/)为准。SSE 的格式与重连见 [HTML Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)。表中方向是接口能力，不是“WebSocket 必定更快”或“SSE 自动保证不丢”。

## 连通、发送与业务完成是不同事实

`open` 表示当前连接已建立，不证明之前的事件已补齐。WebSocket 的 `send()` 将数据交给本地发送流程；`bufferedAmount` 描述尚未发送到网络的应用数据缓冲量，不是远端确认数。缓冲归零也不能证明对方应用已提交业务，见 [WebSocket API 的 bufferedAmount 与 send](https://websockets.spec.whatwg.org/#dom-websocket-bufferedamount)。

教学反例：客户端发出“确认通知 M”，服务器保存成功，确认响应尚未抵达客户端时断线。客户端看到的结果是不确定，而非已证明失败。再次发送应沿用操作 ID，由服务端识别同一动作；每次生成新 ID 可能把不确定结果变成重复副作用，见[幂等性](../api/idempotency.md)。

连接内消息的传递顺序也不等于异步处理的提交顺序。事件 101 的处理等待数据库，102 的处理先结束时，不能仅把最大已见编号当作连续完成点。

## SSE 的 Last-Event-ID 不是业务完成游标

下面是说明性 SSE 帧，最后包含空行：

```text
id: 102
event: notification
data: {"id":"M102","version":4}

```

EventSource 按格式解析事件，记录 `id`，重建连接时可发送 `Last-Event-ID`。这个标识来自流解析/派发状态，不等待应用[异步](../../glossary/runtime.md#runtime.async)工作持久化；服务器也必须主动把它解释为有效恢复位置。完整规则见 [HTML 的处理模型与解析](https://html.spec.whatwg.org/multipage/server-sent-events.html#the-last-event-id-header)。空 `id` 会清空相应状态，新建 EventSource 对象也不能假定继承旧对象的游标。

因此应明确系统究竟承诺“尽力显示当前通知”，还是“连续处理一段可恢复历史”。前者可能允许重新取快照；后者需要独立的应用确认/恢复协议，不能用浏览器保存的最后事件 ID 偷换已处理位置。

## 用连续位置、去重与快照闭合恢复

假设一个租户下的单条逻辑流按序号连续记录事件。应用已持久化完成到 100；101、102 已到达，但 101 尚未处理完成。接下来发生断线：

1. 如果仅因“已收到 102”就从 103 补读，101 的工作可能永远被跳过。
2. 若以连续完成位置 100 恢复，服务器重发 101、102；已做完的事件要能安全识别，不能重复扣款或重复叠加计数。
3. 应用在效果与去重记录满足一致性要求后推进连续位置；只保存一个最大编号不足以表达中间缺口。
4. 如果服务器当前可补读历史从 111 开始，必须明确报告游标失效；客户端获取与版本 V 对应的快照，并从匹配的 V 之后接续，避免快照与增量之间再漏一段。

要落实从 100 恢复，协议需明确由服务器保存业务确认位置，或通过受校验的参数等方式显式传入应用游标；不能直接沿用可能已到 102 的 Last-Event-ID。

以上是应用协议要求，不是 WebSocket/SSE 原生提供的事务。序号范围、流标识、租户和日志代次都要明确；多个独立分区不能直接拿一个数比较，见[消息投递与确认](../messaging/delivery-acknowledgements-and-idempotency.md)。

## 慢消费和重连风暴仍需边界

主[线程](../../glossary/systems.md#systems.execution-units)忙碌时，数据可能继续进入缓冲，待处理消息也可能持续增长。设置最大消息字节、待处理总量和超时；状态展示可以在语义允许时合并为最新版本，交易事件不能随意丢弃中间项。达到上限后可关闭连接并用明确游标恢复，不能靠无限堆积换取“从未断线”。相关机制见[背压](../performance/backpressure-and-bounded-queues.md)。

重建连接还需[退避](../../glossary/api.md#api.retries)、抖动、[重试预算](../../glossary/reliability.md#reliability.retry-budget)和停止条件。自动重连不意味着任何响应都无限重试，页面退出、用户登出或订阅对象改变时应停止旧订阅。代理缓冲、闲置超时及后台页面调度会影响实际到达时延；应用保活消息只能提供某个时刻的活动证据，不证明任意时段都无消息缺口。

## 身份变化后要重新确定可恢复范围

使用加密连接与正确的服务器身份校验；服务器还要验证调用者、订阅对象和来源策略。WebSocket 的 Origin 机制不等于用户[认证](../../glossary/security.md#security.identity)，也不能把 [CORS](../../glossary/security.md#security.origin) 响应头规则直接当作 WebSocket 授权。SSE 跨源访问遵守其 Fetch/CORS 规则，认证方式还受浏览器接口能力限制，不能假设原生构造器允许任意自定义请求头。

令牌过期、登出或租户切换后，旧连接是否继续被接受需要服务端策略；补读必须按当前权限过滤。事件游标是恢复位置，不能当作访问凭据。前端也应清理旧身份的可见数据，见[浏览器来源边界](../security/origins-cors-and-csrf.md)与[路由缓存](routing-state-and-cache-lifecycles.md)。

## 自检

1. WebSocket 双向与 SSE 单向分别描述什么？SSE 自动重连为何不保证历史完整？
2. `send()` 返回、缓冲归零、收到业务确认，各能证明到哪一步？
3. 已收到 102 但连续完成仅到 100，为何从 103 补读会有风险？
4. 游标早于服务器保留历史时，为什么需要明确快照版本与接续位置？
5. 切换租户后，为什么旧游标、旧连接和旧页面数据都要重新判断？

## 来源与核查

2026-10-26 核查 RFC 6455、WHATWG WebSockets 与 HTML SSE 标准，范围为通道、缓冲、事件标识和重建规则。补读、业务确认、快照与去重流程是本文声明条件下的纸面协议设计。状态为 source-checked；未测试真实浏览器/代理、认证过期、慢消费、历史缺口或可靠交付集成。
