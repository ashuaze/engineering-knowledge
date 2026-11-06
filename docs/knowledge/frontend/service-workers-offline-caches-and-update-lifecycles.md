---
id: "kb-frontend-offline-lifecycle"
title: "Service Worker 与离线更新：新版本下载了为什么还没接管"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分注册、安装、等待、激活与控制，解释 Cache API 策略、资源版本、身份隔离和离线写入的确认边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-frontend-routing-cache", "kb-frontend-bundling-splitting"]
related: ["kb-frontend-incremental-regeneration", "kb-api-idempotency", "kb-security-origin-csrf", "kb-runtime-event-loop", "kb-messaging-outbox"]
tags: ["service-worker", "offline", "cache-storage", "updates", "lifecycle"]
---

# Service Worker 与离线更新：新版本下载了为什么还没接管

学习入口：页面发布了新版，某些用户仍看到旧内容；强制激活以后，旧页面又加载不到分块资源。离线能力让请求与资源生命周期多了一层，需要同时管理 Worker 版本、受控页面和缓存内容。

前置：[路由与缓存生命周期](routing-state-and-cache-lifecycles.md)、[打包与代码分割](bundling-tree-shaking-and-code-splitting.md)。本文依据 Service Workers 2026-09-17 候选推荐草案的基础模型与浏览器开发者文档，草案不代表所有特性已实现。版本、缓存及`待同步`记录为纸面设计；没有注册 Worker、缓存真实响应或修改本站离线行为。

## 注册存在不等于脚本永远运行

[Service Worker](../../glossary/frontend.md#frontend.offline) 是按事件运行的请求处理环境，没有页面 [DOM](../../glossary/frontend.md#frontend.render-tree)。注册记录、脚本执行实例和被控制页面有不同寿命：浏览器可在没有待处理事件，或执行失控、超时等情况下终止实例，后续事件再启动它。关键状态不能只保存在脚本全局变量，见 [Service Workers 生命周期定义](https://www.w3.org/TR/2026/CRD-service-workers-20260917/#service-worker-lifetime)。

`waitUntil()` 让事件关联需要完成的[异步](../../glossary/runtime.md#runtime.async)工作，但不是永久驻留、无限后台运行或断电后保证执行的承诺。注册通常要求安全上下文与同源等条件；`scope` 决定能控制的客户端范围，不能拿一个路径前缀当作整个 origin 内存储或应用[授权](../../glossary/security.md#security.identity)的安全隔离。

## 安装、等待、激活与页面控制逐项判断

| 状态或动作 | 正在发生什么 | 不能直接推出什么 |
| --- | --- | --- |
| 注册/更新检查 | 建立或检查注册及脚本版本 | 当前页已被新 Worker 控制 |
| install | 新 Worker 准备必要资源，报告安装工作结果 | 已替换旧 Worker，或缓存写入都已自动回滚 |
| waiting | 新版本准备好，等待满足接管条件 | 下载失败，或刷新一次就必然接管 |
| activate | 执行激活与必要迁移，进入处理后续事件的阶段 | 所有已打开页面的 JS 都换成新版 |
| 页面受控 | 某客户端请求可交给其控制者处理 | 该页所有资源和数据属于同一发布版本 |

默认更新通常等待旧 Worker 不再控制客户端后才激活，刷新时新旧客户端还可能短暂重叠，所以一次刷新未必足够。更新后的等待用于减少新旧运行环境冲突；`skipWaiting()` 可使新版本更早进入激活，`clients.claim()` 可以接管相应范围中的客户端。两者都不会替旧页面重写已加载的 JavaScript，见[浏览器开发者的生命周期说明](https://web.dev/articles/service-worker-lifecycle)。是否提前接管应由资源/存储兼容性决定，而不是只为消除 waiting 状态。

## Cache API 与 HTTP 缓存各有策略

Cache Storage 中的请求/响应由 Cache API 及应用代码管理，不因一个响应带有 HTTP 新鲜度头就自动按相同规则过期。`fetch()` 自身又可能通过 HTTP 缓存取得响应，所以“network-first”的网络分支也不等于强制穿透所有缓存，见 [Workbox 缓存策略说明](https://developer.chrome.com/docs/workbox/caching-strategies-overview)。

| 常见策略 | 读取顺序 | 主要取舍 |
| --- | --- | --- |
| cache-first | 命中即返回，未命中才获取 | 稳定静态资源更易复用，更新与淘汰需明确 |
| network-first | 先尝试获取，失败或达到设计期限再回缓存 | 新鲜度与离线可用之间取舍，需定义什么算失败 |
| stale-while-revalidate | 有缓存先返回，同时尝试更新 | 当前访问可读旧结果，后台失败需另行处理 |

这些是策略思路，不是一个内置名称便自动完成超时、[状态码](../../glossary/api.md#api.http-semantics)判断和身份隔离。HTTP 500 通常仍是成功取得一个响应，不等于 fetch 网络错误；哪些响应可写入缓存、可否用旧内容降级，要由策略明确。

## 纸面版本切换：新 Worker 不会升级旧页面

假设页面 P1 已加载 release-1，稍后才需要动态分块 `editor.1.js`。新 Worker W2 安装 release-2，资源名为 `editor.2.js`。若提前激活 W2 并立即删除所有 release-1 缓存，而源站也已移除旧资源，P1 仍会请求 `editor.1.js` 并失败。

可选设计是让旧客户端完成后再切换，或让新 Worker 与服务器在过渡期兼容旧资源；也可以在保存草稿后协调刷新。无论采用哪种方式，都应明确哪些页面还引用旧版本，不能把“W2 已激活”当作旧资源已经没人需要的证明。

缓存清理还需按本应用的命名空间与拥有范围执行。相同 origin 下可有多个应用，不能删除所有自己不认识的缓存名。安装失败也不能假定已产生的缓存副作用自动撤销；应能识别并回收不再使用的中间版本。

## 离线可读与离线写入是不同承诺

缓存页面能打开，不意味着写请求已在服务器完成。离线编辑可先把操作 ID、对象版本、身份范围与内容可靠保存到本地[队列](../../glossary/algorithms.md#algorithms.queues)，再显示“`待同步`”。恢复后以同一操作 ID 提交，遇到版本冲突要显式处理；响应丢失时查询或重放同一操作，避免新 ID 造成重复业务效果。

这是一套教学设计，相关耐久接纳/派送职责见 [Outbox](../messaging/transactional-outbox.md)与[幂等性](../api/idempotency.md)，不表示浏览器自动提供了数据库与远端业务之间的事务。后台调度可用性、关闭页面后何时执行，以及失败时怎样让用户知道，均需实现验证。

浏览器本地存储还受配额、持久化模式与用户清除影响，不能视为永久备份，见 [Storage Standard 的配额与管理](https://storage.spec.whatwg.org/#usage-and-quota)。写入失败不能仍显示“已安全保存”。

登出或换租户时，按身份分区的响应与`待同步`操作应分别处理。缓存键中包含用户标识只是命名方案，不是访问控制；稍后重放的操作需按当前服务端授权判断，不能用旧离线状态绕过撤销。

## 自检

1. 注册记录还在，为什么脚本全局变量仍可能丢失？waitUntil 保证什么范围？
2. waiting、activate 和页面受控分别说明什么？提前激活会自动更新页面 JS 吗？
3. 为什么 Cache API 命中不会自动遵守 HTTP 缓存的新鲜度？network-first 是否必到源站？
4. P1/W2 的例子中旧分块为何失败？删旧缓存前还要知道哪些事实？
5. 离线界面显示“`待同步`”与“服务器已提交”有何区别？为何需要操作 ID、版本和身份范围？

## 来源与核查

2026-10-26 核查上述固定 Service Workers 草案、web.dev 生命周期、Workbox 策略与 WHATWG Storage 标准。本文为 source-checked 概念文章，未运行 Service Worker、测试配额/清除、版本接管、离线重放、授权撤销或多标签页集成；不承诺草案全部特性已被浏览器实现。
