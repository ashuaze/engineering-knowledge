<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 前端与浏览器词汇表

本页解释 15 组术语，按[完整术语索引](../glossary.md#frontend)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [前端与浏览器文章](../knowledge/frontend/index.md)

## 本页术语

- [DOM / CSSOM / Render Tree](#frontend.render-tree)
- [Layout / Paint / Compositing](#frontend.render-pipeline)
- [CSR / SSR / SSG / ISR](#frontend.rendering-strategies)
- [Hydration](#frontend.hydration)
- [SPA / Client-side Routing](#frontend.spa)
- [Reactivity / State Management](#frontend.state)
- [Virtual DOM / Reconciliation](#frontend.vdom)
- [Bundling / Tree Shaking](#frontend.bundling)
- [Browser Cache / Service Worker](#frontend.offline)
- [WebSocket / SSE](#frontend.realtime)
- [Core Web Vitals](#frontend.web-vitals)
- [BFF](#frontend.bff)
- [Long Task / Main-thread Yielding](#frontend.long-tasks)
- [Hydration Mismatch](#frontend.hydration-mismatch)
- [Component Identity / Stable Key](#frontend.component-identity)

<a id="frontend.render-tree"></a>

## DOM / CSSOM / Render Tree

**ID：** `frontend.render-tree` · **建议优先级：** P1

**别名 / 检索词：** DOM、CSSOM、Render Tree、渲染树

**简释：** 文档、样式和渲染结构。

DOM 表示文档结构，CSSOM 表示样式规则，渲染结构结合可见内容与计算样式。三者不一一对应，隐藏节点和伪元素等会产生差异。

**例子：** 修改 DOM 或样式后，浏览器可能需要更新渲染结构与布局。

**深入阅读：** [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](../knowledge/frontend/rendering-and-hydration.md)

<a id="frontend.render-pipeline"></a>

## Layout / Paint / Compositing

**ID：** `frontend.render-pipeline` · **建议优先级：** P1

**别名 / 检索词：** Layout、Paint、Compositing、布局、绘制、合成

**简释：** 布局计算、绘制与图层合成。

Layout 计算几何位置，Paint 生成绘制内容，Compositing 组合图层输出画面。一次修改触发哪些阶段取决于属性、图层和实现，不能假定所有动画都只需合成。

**例子：** 改变宽度可能重新布局；变换动画是否避开绘制需用实际轨迹检查。

**深入阅读：** [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](../knowledge/frontend/rendering-and-hydration.md)

<a id="frontend.rendering-strategies"></a>

## CSR / SSR / SSG / ISR

**ID：** `frontend.rendering-strategies` · **建议优先级：** P1

**别名 / 检索词：** CSR、SSR、SSG、ISR、客户端渲染、服务端渲染、静态生成、增量再生成

**简释：** 客户端渲染、服务端渲染、预生成与增量再生成。

CSR 在客户端生成主要界面，SSR 按请求在服务端生成 HTML，SSG 在构建时预生成，ISR 按框架规则更新预生成结果。首屏内容、交互代码和数据新鲜度需分别设计。

**例子：** 商品介绍可预生成，用户购物车仍需根据身份获取实时状态。

**深入阅读：** [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](../knowledge/frontend/rendering-and-hydration.md) · [增量再生成与页面缓存：过了更新间隔为什么仍看到旧内容](../knowledge/frontend/incremental-regeneration-revalidation-and-freshness.md)

<a id="frontend.hydration"></a>

## Hydration

**ID：** `frontend.hydration` · **建议优先级：** P1

**别名 / 检索词：** Hydration、水合

**简释：** 让服务端输出的页面连接客户端交互逻辑。

Hydration 在已有服务端 DOM 上连接客户端组件状态和交互。页面能显示不代表事件已就绪，服务端与客户端初始输出还需满足框架的对应要求。

**例子：** 按钮已经可见，但相关脚本尚未水合时，点击不一定立即得到预期响应。

**深入阅读：** [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](../knowledge/frontend/rendering-and-hydration.md)

<a id="frontend.spa"></a>

## SPA / Client-side Routing

**ID：** `frontend.spa` · **建议优先级：** P1

**别名 / 检索词：** SPA、Client-side Routing、单页应用、客户端路由

**简释：** 单页导航与客户端路由状态。

SPA 在同一文档内更新界面，客户端路由把 URL、页面组件和导航状态联系起来。仍要处理刷新回源、历史记录、权限和页面数据生命周期。

**例子：** 浏览器后退时，应恢复正确路由与状态，而非仅替换地址栏字符串。

**深入阅读：** [前端路由与缓存：导航以后哪些状态仍会保留](../knowledge/frontend/routing-state-and-cache-lifecycles.md)

<a id="frontend.state"></a>

## Reactivity / State Management

**ID：** `frontend.state` · **建议优先级：** P1

**别名 / 检索词：** Reactivity、State Management、响应式、状态管理

**简释：** 数据变化、界面更新及状态所有权。

响应式系统跟踪依赖并在数据变化时安排更新；状态管理明确数据所有者和修改入口。内存赋值、组件更新与屏幕绘制可能发生在不同时点。

**例子：** 更新搜索条件后，旧请求迟到的结果不能覆盖当前条件对应的列表。

**深入阅读：** [响应式状态与更新：值变了，界面为什么还没变](../knowledge/frontend/reactive-state-and-update-scheduling.md) · [前端路由与缓存：导航以后哪些状态仍会保留](../knowledge/frontend/routing-state-and-cache-lifecycles.md)

<a id="frontend.vdom"></a>

## Virtual DOM / Reconciliation

**ID：** `frontend.vdom` · **建议优先级：** P1

**别名 / 检索词：** Virtual DOM、Reconciliation、虚拟 DOM、协调更新

**简释：** UI 描述与更新协调策略。

Virtual DOM描述预期UI，Reconciliation决定对应与变更。公开身份语义依框架而异；React中的父级位置、类型与key影响状态保留，Vue有自身就地修补及有key列表机制。不能从有虚拟结构推出固定差分算法或性能。

**例子：** 列表用稳定业务 key，能减少排序后把旧组件状态误配给另一行的风险。

**深入阅读：** [组件协调与 key：列表变了，状态应该跟着谁走](../knowledge/frontend/reconciliation-keys-and-component-identity.md)

<a id="frontend.bundling"></a>

## Bundling / Tree Shaking

**ID：** `frontend.bundling` · **建议优先级：** P1

**别名 / 检索词：** Bundling、Tree Shaking、Code Splitting、Chunk、代码分割、按需加载、打包、摇树优化

**简释：** 依据模块使用与副作用等信息组织、移除和拆分输出代码；资源粒度、传输成本与运行时执行需分别分析。

Bundling 组织模块为输出资源，Tree Shaking 依据静态使用和副作用信息移除无用代码，Code Splitting 调整按需加载边界。包变小不等于用户等待一定更短。

**例子：** 路由拆包减少初始下载，但跳转时需观察新增请求和代码执行时间。

**深入阅读：** [打包与代码分割：文件变小为什么不一定加载更快](../knowledge/frontend/bundling-tree-shaking-and-code-splitting.md)

<a id="frontend.offline"></a>

## Browser Cache / Service Worker

**ID：** `frontend.offline` · **建议优先级：** P1

**别名 / 检索词：** Browser Cache、Service Worker、浏览器缓存、离线缓存

**简释：** 响应复用、请求代理和离线能力。

浏览器 HTTP 缓存按响应规则复用内容；Service Worker 可代理请求并管理 Cache Storage。两层缓存的键、更新和失效规则不同，离线写入还需同步与冲突处理。

**例子：** 发布新版页面后，旧 Service Worker 缓存可能继续提供旧资源。

**深入阅读：** [前端路由与缓存：导航以后哪些状态仍会保留](../knowledge/frontend/routing-state-and-cache-lifecycles.md) · [Service Worker 与离线更新：新版本下载了为什么还没接管](../knowledge/frontend/service-workers-offline-caches-and-update-lifecycles.md)

<a id="frontend.realtime"></a>

## WebSocket / SSE

**ID：** `frontend.realtime` · **建议优先级：** P1

**别名 / 检索词：** WebSocket、SSE、服务器推送

**简释：** 双向连接通信与服务器事件推送。

WebSocket提供双向消息，SSE提供服务器到浏览器的事件流。连接建立、发送缓冲归零和业务完成各有边界；EventSource标识由解析维护，不是异步业务提交游标。补读、去重、历史缺口和权限由应用协议处理。

**例子：** 已收到102但连续处理只到100时，不能仅按最大已见编号从103继续；还需处理101的缺口与重复效果。

**深入阅读：** [WebSocket 与 SSE：连接恢复以后怎样补回消息](../knowledge/frontend/websocket-sse-reconnection-and-replay.md)

<a id="frontend.web-vitals"></a>

## Core Web Vitals

**ID：** `frontend.web-vitals` · **建议优先级：** P1

**别名 / 检索词：** Core Web Vitals、核心网页指标、LCP、INP、CLS

**简释：** 衡量加载、交互和布局稳定性的指标集合。

本次核查以 LCP、INP、CLS 分别观察主要内容呈现、交互到下一次画面与布局稳定性。推荐按设备分组看真实访问的p75；单次实验室结果不代表用户分布，无交互样本不能补为零，阈值与采集规则需随版本核对。

**例子：** 纸面两段偏移窗口分别累计0.10和0.08，CLS取最大0.10；不是全程相加0.18，也不是本站实测。

**深入阅读：** [Core Web Vitals：怎样把页面体验变成可解释的证据](../knowledge/frontend/core-web-vitals-field-data-and-diagnostic-boundaries.md)

<a id="frontend.bff"></a>

## BFF

**ID：** `frontend.bff` · **建议优先级：** P1

**别名 / 检索词：** BFF、前端后端适配层

**简释：** 为特定客户端提供聚合和适配的后端。

BFF按客户端需要组织字段投影、聚合和交互契约，与通用网关及领域业务规则分工。减少外部请求不自动产生一致快照，也不替代对象授权、预算及个性化缓存失效。

**例子：** 移动端 BFF 把多个服务的数据组合成一次页面请求所需的结果。

**深入阅读：** [BFF 与前端适配：聚合成一次请求，为什么仍需业务边界](../knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)

<a id="frontend.long-tasks"></a>

## Long Task / Main-thread Yielding

**ID：** `frontend.long-tasks` · **建议优先级：** P1

**别名 / 检索词：** Long Task、Main-thread Yielding、scheduler.yield、长任务、任务切片

**简释：** 识别持续占用主线程的任务，分批执行并让出调度机会。

浏览器长任务持续占用主线程，推迟输入和渲染；让出主线程需要产生宿主可调度的边界。仅把循环包装成 async 或连续微任务并不保证响应改善。

**例子：** 将大批数据分段处理，并在段间让出执行机会，再观察输入延迟。

**深入阅读：** [浏览器长任务：页面已显示为何仍点不动](../knowledge/frontend/long-tasks-and-responsiveness.md) · [实验：比较长任务、微任务与真正让出](../knowledge/frontend/long-tasks-lab.md)

<a id="frontend.hydration-mismatch"></a>

## Hydration Mismatch

**ID：** `frontend.hydration-mismatch` · **建议优先级：** P1

**别名 / 检索词：** Hydration Mismatch、水合不匹配

**简释：** 预生成 DOM 与客户端首次预期输出不对应，需检查初始数据、结构与环境差异。

水合不匹配表示预生成 DOM 与客户端首次预期输出不对应。常见原因包括时间、随机值、不同初始数据及无效 HTML；恢复策略依框架而异。

**例子：** 服务端按一个时区输出日期，客户端按另一时区首次渲染，可能出现文本不匹配。

**深入阅读：** [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](../knowledge/frontend/rendering-and-hydration.md)

<a id="frontend.component-identity"></a>

## Component Identity / Stable Key

**ID：** `frontend.component-identity` · **建议优先级：** P1

**别名 / 检索词：** 组件身份、稳定 key、稳定业务 key

**简释：** 更新前后组件或列表项的对应关系，决定局部状态保留与重置。

稳定标识让同级记录跨插入和重排保持对应；身份还受父级和组件类型等框架规则约束。索引可能把状态留在位置，渲染时生成随机标识则丢失对应。重置实例不自动清理外部缓存和迟到请求。

**例子：** 同级A/B分别有甲/乙草稿，头部插入X时，索引key可能把甲/乙交给X/A；稳定记录ID让草稿继续跟随A/B。

**深入阅读：** [组件协调与 key：列表变了，状态应该跟着谁走](../knowledge/frontend/reconciliation-keys-and-component-identity.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [web.dev：Core Web Vitals](https://web.dev/articles/vitals)
- [React：组件状态保留与重置](https://react.dev/learn/preserving-and-resetting-state)
- [Vue：列表状态与key](https://vuejs.org/guide/essentials/list.html#maintaining-state-with-key)
- [WHATWG：浏览器WebSocket](https://websockets.spec.whatwg.org/)
- [HTML：服务器发送事件与恢复标识](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Service Workers：2026-09-17候选推荐草案](https://www.w3.org/TR/2026/CRD-service-workers-20260917/)
- [Next.js：未启用Cache Components的ISR](https://nextjs.org/docs/app/guides/incremental-static-regeneration)
- [Sam Newman 的 BFF 模式](https://samnewman.io/patterns/architectural/bff/)
- [Azure BFF](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)
- [Azure Gateway Aggregation](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
