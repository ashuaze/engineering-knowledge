---
id: "kb-frontend-rendering-hydration"
title: "渲染与 Hydration：HTML 已显示，页面为什么还没准备好"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分浏览器呈现、脚本调度与框架接管，解释 CSR、SSR、SSG 和 Hydration 的成本与一致性边界。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-networking-https-request", "kb-runtime-event-loop", "kb-frontend-long-tasks", "kb-runtime-gc", "kb-frontend-reactive-updates", "kb-frontend-routing-cache", "kb-frontend-reconciliation-identity", "kb-frontend-web-vitals", "kb-frontend-incremental-regeneration"]
tags: ["rendering", "hydration", "browser"]
---

# 渲染与 Hydration：HTML 已显示，页面为什么还没准备好

学习入口：页面很快显示了内容，点按钮却没有预期反馈，是网络、浏览器还是框架的问题？前置知识：HTML、CSS、[DOM](../../glossary/frontend.md#frontend.render-tree) 与事件处理的基本概念。本文使用浏览器通用的简化渲染模型，框架接管参考 React hydrateRoot 与 Vue [SSR](../../glossary/frontend.md#frontend.rendering-strategies) 官方文档；不把某个框架的恢复策略推广到所有实现。

[组件身份](../../glossary/frontend.md#frontend.component-identity)与必要更新继续见[组件协调与 key](reconciliation-keys-and-component-identity.md)；体验证据见[Core Web Vitals](core-web-vitals-field-data-and-diagnostic-boundaries.md)，预生成内容的后续更新见[增量再生成](incremental-regeneration-revalidation-and-freshness.md)。

## 从响应字节到一次呈现

拿到 HTML 后，浏览器还要解析结构、加载关联资源并形成可显示的结果。DOM 表达文档结构，CSSOM 表达样式规则；样式计算确定规则作用后的结果，布局确定几何位置，绘制生成绘制内容，栅格化与合成等工作使结果能够呈现到屏幕。[渲染树、布局与绘制介绍](https://web.dev/articles/critical-rendering-path/render-tree-construction)说明了这些基本职责。

这是一张依赖图，不是每次更新都从头运行的固定流水线。布局、绘制与合成的内部细节因引擎而异；某些改变需要重新布局，某些只影响绘制或合成。不能因为某个动画用了 transform，就承诺它在任意页面都没有其他成本。[web.dev 渲染性能说明](https://web.dev/articles/rendering-performance)展示了不同更新路径与工作量的区别。

脚本读取与修改 DOM，也会影响这些步骤。样式或几何状态失效后，读取布局相关值可能迫使浏览器提前完成[同步](../../glossary/runtime.md#runtime.async)布局；反复交替修改与读取，可能重复付出成本。性能诊断需要查看实际工作，而不能只数 JavaScript 行数或网络请求数。

## 脚本下载完成不等于执行成本消失

脚本可能需要下载、解析和执行。放在解析过程中的普通经典脚本可能[阻塞](../../glossary/systems.md#systems.blocking)后续 HTML 解析；外部经典脚本的 defer 与 async 改变下载、执行及顺序约束，但不会把脚本执行自动搬到 Worker。

| 加载方式 | 入门理解 | 需要保留的边界 |
| --- | --- | --- |
| 普通外部经典脚本 | 解析到相应位置时等待并执行 | 可能阻塞后续解析，还可能受相关样式加载影响 |
| defer 外部经典脚本 | 下载可与解析重叠，解析后按文档顺序执行 | 不等于在后台执行计算；此处不讨论内联 defer |
| async 外部经典脚本 | 可与解析[并行](../../glossary/systems.md#systems.concurrency)下载，资源就绪后安排执行 | 不保证多个脚本的文档顺序，执行仍可能打断解析 |

具体规则和模块脚本差异见 [HTML script 元素说明](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)。模块默认有类似延后执行的行为，依赖图与 async 设置另有规则；不能把上表不加区分地套到所有脚本上。即使 DOM 已完成，随后启动的大量初始化仍可能占用主[线程](../../glossary/systems.md#systems.execution-units)，[延迟](../../glossary/performance.md#performance.latency-throughput)输入处理。

## CSR、SSR、SSG 与 Hydration 分别改变哪里

| 概念 | 谁在什么时候生成主要 HTML | 尚需回答的问题 |
| --- | --- | --- |
| CSR，客户端渲染 | 浏览器运行应用代码后生成界面 | 脚本和数据何时就绪，主线程工作量有多少 |
| SSR，服务端渲染 | 服务端在请求处理中生成 HTML | 服务端成本、缓存、首屏数据与客户端接管怎样协调 |
| SSG，静态生成 | 构建阶段预先生成 HTML | 内容什么时候更新，哪些部分仍需动态数据 |
| [Hydration](../../glossary/frontend.md#frontend.hydration)，水合 | 客户端框架接管预先生成的 HTML | 初始输出能否对应，状态和交互何时建立 |

SSR 与 SSG 描述 HTML 的生成时机，Hydration 描述客户端接管过程，它们不是同一维度的替代选项。静态页面可以完全不需要框架；SSR/SSG 页面也可能只对部分区域执行接管。[Vue SSR 指南](https://vuejs.org/guide/scaling-up/ssr.html)解释了服务端输出、客户端水合与静态生成的区别。

Hydration 不只是“给按钮加几个监听器”：框架需要让组件、状态、事件处理和既有 DOM 建立对应。它可能复用现有节点，仍有下载与执行客户端代码的成本。SSR 有机会让内容较早可见，不能由此推出任意交互已经准备好，或总体工作量一定减少。

## 显示、接管与响应是不同的观察点

教学设定：服务器输出产品名、价格和“加入收藏”按钮，收藏功能由客户端框架处理。以下只描述可能的阶段，没有录制真实时间线，也不代表这些阶段必然严格串行。

```text
服务端生成 HTML → 浏览器解析并显示部分内容
客户端代码和初始数据就绪 → 框架接管相应区域
输入获得处理机会 → 处理逻辑改变状态 → 后续呈现反馈
```

在客户端接管前，产品名可以已显示，但依赖框架的收藏动作未必可用。原生链接或具有有效提交目标的表单可能已有原生行为，不能说所有 HTML 在 Hydration 前都不能交互。部分框架还支持事件重放或选择性接管，具体行为需按框架及边界核查。

接管之后也可能响应慢：事件处理要等待调度，处理逻辑可能很重，状态变化后还有样式、布局和呈现。看到 DOM 改变不能证明用户已经看到新像素，看到首次内容也不能证明未来点击会及时反馈。完整诊断需要把这几个观察点分开，不能只用“首屏快”评价交互。

## 初始输出不一致会造成什么

服务端和客户端的首次输出应能对应。[React hydrateRoot 文档](https://react.dev/reference/react-dom/client/hydrateRoot)要求修复不匹配，并指出不保证自动修补所有属性差异。不能靠“开发环境只有警告”推断生产行为可靠。

常见来源包括：两端分别调用随机数或当前时间；时区与语言环境不同；客户端首次渲染读取了服务端没有的数据；无效 HTML 嵌套被浏览器纠正；接管前已有其他代码修改 DOM。处理时先确定两端使用的初始数据与结构，再决定哪些内容在接管后更新。统一一次初始值和把动态部分放到后续更新，解决的是不同需求。

例如服务端显示“未收藏”，客户端首次就按另一份本地状态显示“已收藏”，不能只把警告隐藏掉；应明确初始状态来源及后续同步策略。框架可能通过重建部分 DOM 恢复，也可能保留某些不匹配，代价与行为取决于实现。

服务端状态还有另一个边界：不能把某位用户的可变请求状态存进所有请求共享的应用单例。SSR 的请求隔离与缓存键需要单独设计；客户端水合成功也不能证明服务端没有跨请求状态污染。相关限制见 [Vue 的 SSR 编写约束](https://vuejs.org/guide/scaling-up/ssr.html#cross-request-state-pollution)。

客户端接管后还要区分[响应式更新](reactive-state-and-update-scheduling.md)中的计算、DOM 提交与绘制，以及[路由与缓存](routing-state-and-cache-lifecycles.md)中的实例复用与恢复。两篇为来源核查与教学推演，没有增加 SSR 或 Hydration 实测。

## 自检与证据边界

面对“显示快、点击慢”，分别检查资源加载、脚本与框架接管、事件是否绑定、主线程等待、处理逻辑及后续呈现；同时排除遮罩和禁用状态。Hydration 是一个待验证的环节，不是所有交互迟到的统一解释。

试着回答：静态链接为什么可能在框架接管前可用？defer 为什么不能保证没有[长任务](../../glossary/frontend.md#frontend.long-tasks)？SSR 为什么仍有客户端执行成本？把不匹配警告关闭，为什么不能替代一致性修复？

核查日期：2026-10-19。本文查阅 web.dev、MDN、React 与 Vue 文档，没有搭建 SSR 示例、运行水合故障注入或录制性能数据；阅读站的页面检查不属于这些技术实验。

- [HTTPS 请求链路](../networking/https-request-lifecycle.md)：先区分响应可用与后续页面处理。
- [事件循环与微任务](../runtime/event-loop-and-microtasks.md)：解释事件与绘制获得机会的边界。
- [浏览器长任务](long-tasks-and-responsiveness.md)：进一步定位执行与输入等待，[配套长任务实验](long-tasks-lab.md)已执行；SSR 与 Hydration 性能仍待单独实测。
- [可达性与垃圾回收](../runtime/reachability-and-garbage-collection.md)：检查组件、监听器和缓存的生命周期。
