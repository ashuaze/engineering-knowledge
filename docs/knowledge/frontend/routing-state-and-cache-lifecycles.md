---
id: "kb-frontend-routing-cache"
title: "前端路由与缓存：导航以后哪些状态仍会保留"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分历史记录、组件复用、应用数据缓存、HTTP 缓存与页面恢复，解释参数切换、失效和身份边界。"
created: "2026-10-20"
updated: "2026-10-27"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-frontend-rendering-hydration", "kb-frontend-reactive-updates"]
related: ["kb-runtime-closures", "kb-runtime-gc", "kb-cache-search-cache-aside", "kb-security-object-authorization", "kb-networking-https-request", "kb-api-conditional-requests", "kb-security-origin-csrf", "kb-frontend-bundling-splitting", "kb-frontend-reconciliation-identity", "kb-frontend-realtime-replay", "kb-frontend-offline-lifecycle", "kb-frontend-incremental-regeneration", "kb-frontend-bff"]
tags: ["routing", "cache", "lifecycle", "frontend"]
---

# 前端路由与缓存：导航以后哪些状态仍会保留

学习入口：从用户 A 切到用户 B，URL 已变，为什么页面仍显示 A 的资料或表单？前置：浏览器文档、组件状态与数据请求。导航可以改变地址和历史，而组件、数据与缓存各有身份和生命周期。先确定哪个层次被复用，才能判断该保留、重置还是重新验证。

组件重置见[协调与 key](reconciliation-keys-and-component-identity.md)；订阅恢复见[WebSocket/SSE](websocket-sse-reconnection-and-replay.md)；请求代理与资源接管见[离线更新](service-workers-offline-caches-and-update-lifecycles.md)，服务器输出更新见[增量再生成](incremental-regeneration-revalidation-and-freshness.md)。

客户端适配与个性化聚合的权限/缓存边界见[BFF与前端适配](backends-for-frontends-projections-and-service-boundaries.md)。

## URL 变化不等于整个文档重载

[History.pushState](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState)可以更新同源 URL 并增加历史记录，本身不会请求加载新地址，更不会自动渲染相应组件。[客户端路由](../../glossary/frontend.md#frontend.spa)器还需匹配路径、更新视图、管理数据加载和错误状态。

浏览器后退/前进可能通过[popstate](https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event)通知同文档历史变化；直接调用 pushState 或 replaceState 不会自行触发该事件。框架路由提供的导航方法可能另外执行更新，不能用它们的表现倒推原生 History API 包办了所有工作。

直接输入深层地址或刷新通常会走文档请求路径。采用 HTML5 history 的 SPA 需要服务器正确处理入口回退，同时保留 API、静态资源与真正不存在页面的处理边界；只在客户端点开过并不能证明刷新可用，相关部署问题见 [Vue Router 的 History 模式说明](https://router.vuejs.org/guide/essentials/history-mode.html)。

## 组件身份与路由参数分别判断

[Vue Router 的参数路由说明](https://router.vuejs.org/guide/essentials/dynamic-matching.html)中，从一个用户参数切到另一个用户参数，可以复用同一组件实例，因此某些创建生命周期不会再次执行。只在初始化时加载数据，可能留下旧用户内容；应按实际框架规则响应参数变化。

[React 的状态保留说明](https://react.dev/learn/preserving-and-resetting-state)则从树中位置、组件类型与 key 等身份条件解释保留和重置。URL 不是所有框架的自动重置开关，重新请求数据也不自动清空未提交表单。

教学决策应分别写清：[实体](../../glossary/architecture.md#architecture.domain-model)切换后草稿是否仍属于原实体、错误和 loading 是否重置、滚动位置如何恢复、共享状态是否跨页面保留。若保留草稿，按实体明确保存；若重建组件，评估用户输入与订阅会怎样结束，不为强制刷新盲目更换随机 key。

## “缓存”要点名保存在哪一层

| 层次 | 保存什么 | 失效或恢复需要检查什么 |
| --- | --- | --- |
| 组件实例保留 | 局部状态与相关实例 | 是否仍属于当前实体，激活/停用时处理什么 |
| 应用数据缓存 | 查询结果、资源状态等应用数据 | 键、版本、身份范围、有效期及重新验证策略 |
| HTTP 缓存 | 按协议复用响应 | 新鲜度、验证器、Cache-Control 与响应变体 |
| Cache API / [Service Worker](../../glossary/frontend.md#frontend.offline) | 程序管理的请求响应条目，可参与离线策略 | 写入、匹配、淘汰与版本更新由谁管理 |
| bfcache | 浏览器对整个页面执行状态的内存保留 | 是否符合资格，恢复时数据和身份是否仍有效 |

这些层可以同时存在。清掉查询结果不代表组件草稿已重置，卸载组件也不代表 HTTP 缓存已删除；一次网络面板显示“没有请求”，需要进一步区分究竟是哪一层复用。

例如 [Vue KeepAlive](https://vuejs.org/guide/built-ins/keep-alive.html)缓存组件实例，切出时进入停用而不只是普通卸载流程。保留实例不等于所有外部订阅自动结束；需按激活、停用、淘汰和卸载语义管理资源。它不是 API 数据永远新鲜的保证。

## HTTP 指令不能替所有缓存决定生命周期

[RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)中，不带字段参数的响应 no-cache 要求后续复用前成功验证，不能解释为“一律不保存”；no-store 则约束相应 HTTP 缓存存储行为。它们不是应用内状态、历史页面或所有持久材料的统一清除命令。

[Cache API](https://developer.mozilla.org/en-US/docs/Web/API/Cache)由程序显式管理，不能假定它自动遵守 HTTP 缓存头或自动淘汰过期条目。服务端改了缓存指令，也仍需核查已有应用缓存与 Service Worker 的实际策略；这里不提供一套可直接复制的离线更新实现。

[bfcache 说明](https://web.dev/articles/bfcache)区分整页内存恢复与 HTTP 响应复用。跨文档后退可能恢复已有页面状态，不应统一称为重新加载；但是否命中取决于浏览器与页面资格，不能承诺每次后退都保留页面。恢复事件可作为重新检查数据与身份的入口，不应等同于完整安全保证。

## 迟到响应不能决定当前页面是谁

教学时序：打开 /users/A [并发](../../glossary/systems.md#systems.concurrency)起请求 A → 切到 /users/B 发起请求 B → B 先返回 → A 后返回。如果回调不检查归属，最后完成的 A 就可能覆盖 B 的页面，尽管两个响应都正确。

一种教学策略是为当前数据目标保留查询键与请求代次，应用结果前同时核对目标、代次及当前身份上下文。展示代次只保护当前展示；若旧响应要写回自己目标的缓存，还需核对该缓存键的更新版本、身份及失效代次，防止覆盖同键的新结果，或在退出清理后重新建回旧条目。允许暂时显示旧数据时，也需明确标识其目标与加载状态。

清理或取消请求有助于减少过期工作，仍不能代替应用结果时的有效性判断，更不证明远端写入没有发生。回调保留了哪个目标还取决于[闭包与读取时刻](../runtime/closures-and-lexical-bindings.md)，不能用“总读最新 URL”把旧业务动作悄悄换成新对象。

## 共享、失效与身份切换需要一起设计

应用查询键至少要能区分实际影响结果的条件，例如资源、参数、租户、主体范围和数据版本；哪些字段需要进入键，由可信会话和业务契约决定。键里写 user_id 不等于完成[授权](../../glossary/security.md#security.identity)，服务端及实际数据路径仍需检查[对象权限](../security/object-level-authorization.md)。

修改成功后，应按契约更新相关查询或标记失效，再重新验证需要的新鲜数据。一次本地失效不证明其他标签页、Service Worker、组件缓存和整页恢复都已[同步](../../glossary/runtime.md#runtime.async)；离线、失效通知遗漏与旧回填也需要明确行为，见[缓存与失效](../cache-search/cache-aside-and-invalidation.md)。

退出、切换身份或权限撤销时，要同时考虑已展示内容、内存缓存、持久条目、在途响应和恢复页面。先前已交付的数据不能自动收回；前端隐藏内容也不能替代服务端权限。这里的清单是设计范围，没有实现跨标签页一致失效或完整清除保证。

## 按生命周期组合做自检

| 教学情形 | 应确认的证据 |
| --- | --- |
| 同组件切换参数 | 实例是否复用，数据与草稿分别属于谁 |
| 深层 URL 直接刷新 | 文档请求、入口回退与真实 404 是否正确 |
| 后退/前进 | 同文档路由变化还是整页恢复，哪些状态仍有效 |
| 修改后再访问 | 哪个缓存键已更新，哪些派生结果仍待验证 |
| 退出后旧请求返回 | 当前身份已变，旧数据是否还能写入展示或共享缓存 |

自检：pushState 之后为什么可能只有地址变化？KeepAlive 与 HTTP 缓存各保留什么？no-cache 为何不等于删除全部缓存？取消 A 的等待，为什么仍要判断结果归属？

核查日期：2026-10-20。原生历史与缓存接口依据 MDN、HTTP 依据 RFC 9111，组件例子依据 Vue/Vue Router 与 React 官方资料，整页恢复依据 web.dev。查询代次、缓存键与身份清单为教学设计；没有新增路由挂载、Service Worker、bfcache、跨标签页或认证集成实验，也没有验证所有浏览器的恢复行为。

HTTP 层的标签、304 与条件保存见 [HTTP 条件请求](../api/conditional-requests-and-cache-validation.md)；[跨源](../../glossary/security.md#security.origin)请求与自动凭证见[同源、CORS 与 CSRF](../security/origins-cors-and-csrf.md)。这些概念不扩展为本篇已执行了缓存或身份集成实验。

[打包与代码分割](bundling-tree-shaking-and-code-splitting.md)继续说明按需资源、共享代码和旧页面跨版本引用的生命周期；哈希命名、下载缓存与模块求值各有边界，没有新增旧标签页、预加载或资源回收实验。
