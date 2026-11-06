<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 前端与浏览器

建议优先级：P1。目标：具备端到端交付能力，理解渲染、状态和网络边界。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

首屏已出现却不能交互，可能卡在哪个阶段？

## 已有正文

- [BFF 与前端适配：聚合成一次请求，为什么仍需业务边界](backends-for-frontends-projections-and-service-boundaries.md)：区分面向客户端的投影、通用网关与领域规则，说明聚合等待、部分结果、权限和个性化缓存的边界。
- [打包与代码分割：文件变小为什么不一定加载更快](bundling-tree-shaking-and-code-splitting.md)：从模块图到输出资源解释转译、压缩、[Tree Shaking](../../glossary/frontend.md#frontend.bundling) 与代码分割，说明副作用、动态加载、缓存版本和执行成本的边界。
- [Core Web Vitals：怎样把页面体验变成可解释的证据](core-web-vitals-field-data-and-diagnostic-boundaries.md)：分开解释 [LCP](../../glossary/frontend.md#frontend.web-vitals)、INP、CLS 的观察范围与算例，区分单次体验、真实用户分布、实验室结果和业务完成。
- [增量再生成与页面缓存：过了更新间隔为什么仍看到旧内容](incremental-regeneration-revalidation-and-freshness.md)：区分预生成、按请求生成和缓存再验证，用时间线解释 [ISR](../../glossary/frontend.md#frontend.rendering-strategies) 的触发、后台替换、失败保留及多层新鲜度。
- [浏览器长任务：页面已显示为何仍点不动](long-tasks-and-responsiveness.md)：区分内容显示、事件处理和下一次绘制，用[任务切片](../../glossary/frontend.md#frontend.long-tasks)与观测验证交互[阻塞](../../glossary/systems.md#systems.blocking)。
- [实验：比较长任务、微任务与真正让出](long-tasks-lab.md)：以五种调度方式完成相同计算，记录 15 组长任务、输入等待和浏览器时间线。
- [响应式状态与更新：值变了，界面为什么还没变](reactive-state-and-update-scheduling.md)：区分数据修改、依赖追踪、更新调度、[DOM](../../glossary/frontend.md#frontend.render-tree) 提交与浏览器呈现，用 Vue 和 React 例子限定各自机制。
- [组件协调与 key：列表变了，状态应该跟着谁走](reconciliation-keys-and-component-identity.md)：从[组件身份](../../glossary/frontend.md#frontend.component-identity)解释描述、协调与提交，推演索引 key、稳定业务 key 和主动重置的区别，限定 React 与 Vue 的各自语义。
- [渲染与 Hydration：HTML 已显示，页面为什么还没准备好](rendering-and-hydration.md)：区分浏览器呈现、脚本调度与框架接管，解释 CSR、SSR、SSG 和 [Hydration](../../glossary/frontend.md#frontend.hydration) 的成本与一致性边界。
- [前端路由与缓存：导航以后哪些状态仍会保留](routing-state-and-cache-lifecycles.md)：区分历史记录、组件复用、应用数据缓存、HTTP 缓存与页面恢复，解释参数切换、失效和身份边界。
- [Service Worker 与离线更新：新版本下载了为什么还没接管](service-workers-offline-caches-and-update-lifecycles.md)：区分注册、安装、等待、激活与控制，解释 Cache API 策略、资源版本、身份隔离和离线写入的确认边界。
- [WebSocket 与 SSE：连接恢复以后怎样补回消息](websocket-sse-reconnection-and-replay.md)：区分浏览器实时通道、传输与业务确认，说明 [SSE](../../glossary/frontend.md#frontend.realtime) 游标、WebSocket 本地缓冲、补读去重、慢消费及身份变化。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [DOM / CSSOM / Render Tree](../../glossary/frontend.md#frontend.render-tree) | 文档、样式和渲染结构。 |
| [Layout / Paint / Compositing](../../glossary/frontend.md#frontend.render-pipeline) | 布局计算、绘制与图层合成。 |
| [CSR / SSR / SSG / ISR](../../glossary/frontend.md#frontend.rendering-strategies) | 客户端渲染、服务端渲染、预生成与增量再生成。 |
| [Hydration](../../glossary/frontend.md#frontend.hydration) | 让服务端输出的页面连接客户端交互逻辑。 |
| [SPA / Client-side Routing](../../glossary/frontend.md#frontend.spa) | 单页导航与客户端路由状态。 |
| [Reactivity / State Management](../../glossary/frontend.md#frontend.state) | 数据变化、界面更新及状态所有权。 |
| [Virtual DOM / Reconciliation](../../glossary/frontend.md#frontend.vdom) | UI 描述与更新协调策略。 |
| [Bundling / Tree Shaking](../../glossary/frontend.md#frontend.bundling) | 依据模块使用与副作用等信息组织、移除和拆分输出代码；资源粒度、传输成本与[运行时](../../glossary/runtime.md#runtime.virtual-machine)执行需分别分析。 |
| [Browser Cache / Service Worker](../../glossary/frontend.md#frontend.offline) | 响应复用、请求代理和离线能力。 |
| [WebSocket / SSE](../../glossary/frontend.md#frontend.realtime) | 双向连接通信与服务器事件推送。 |
| [Core Web Vitals](../../glossary/frontend.md#frontend.web-vitals) | 衡量加载、交互和布局稳定性的指标集合。 |
| [BFF](../../glossary/frontend.md#frontend.bff) | 为特定客户端提供聚合和适配的后端。 |
| [Long Task / Main-thread Yielding](../../glossary/frontend.md#frontend.long-tasks) | 识别持续占用主[线程](../../glossary/systems.md#systems.execution-units)的任务，分批执行并让出调度机会。 |
| [Hydration Mismatch](../../glossary/frontend.md#frontend.hydration-mismatch) | 预生成 DOM 与客户端首次预期输出不对应，需检查初始数据、结构与环境差异。 |
| [Component Identity / Stable Key](../../glossary/frontend.md#frontend.component-identity) | 更新前后组件或列表项的对应关系，决定局部状态保留与重置。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
