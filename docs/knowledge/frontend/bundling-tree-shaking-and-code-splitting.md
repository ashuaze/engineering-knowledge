---
id: "kb-frontend-bundling-splitting"
title: "打包与代码分割：文件变小为什么不一定加载更快"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "从模块图到输出资源解释转译、压缩、Tree Shaking 与代码分割，说明副作用、动态加载、缓存版本和执行成本的边界。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-runtime-modules-cycles", "kb-runtime-types-validation", "kb-frontend-routing-cache"]
related: ["kb-frontend-long-tasks", "kb-frontend-rendering-hydration", "kb-api-conditional-requests", "kb-devops-delivery-lifecycle", "kb-architecture-module-boundaries", "kb-frontend-web-vitals", "kb-frontend-offline-lifecycle"]
tags: ["bundling", "tree-shaking", "code-splitting", "cache"]
---

# 打包与代码分割：文件变小为什么不一定加载更快

学习入口：入口文件减小了，为什么导航后仍白屏、点击仍卡住？前置：[模块系统](../runtime/modules-bindings-and-circular-dependencies.md)、[类型与运行时](../runtime/type-systems-and-runtime-validation.md)和[缓存生命周期](routing-state-and-cache-lifecycles.md)。本文以 webpack、Rollup 的官方机制及 Vite 的部署失效说明为参照；依赖图与片段是教学设计，未做[打包](../../glossary/frontend.md#frontend.bundling)配置或性能对照实验。

旧页面引用的分块怎样跨版本保留，继续见[Service Worker 与离线更新](service-workers-offline-caches-and-update-lifecycles.md)；下载、执行与体验分布的联系见[Core Web Vitals](core-web-vitals-field-data-and-diagnostic-boundaries.md)。

## 模块图与输出文件不是一一对应

构建工具从入口解析依赖，并通过相应插件或转换处理源码、资源与引用，最终形成输出文件和加载关系。源码里的一个模块可能进入某个 chunk，一个 chunk 也可能包含多个模块；共享依赖、动态导入和输出格式会影响分组。

```text
源码模块与资源 → 解析依赖、转换、分析引用与副作用
              → 入口、共享部分与按需部分等输出资源
              → 部署地址与缓存 → 下载、解析/编译、求值与调用
```

这是概念链路，不规定所有工具和插件必须按同一顺序运行。[webpack Dependency Graph](https://webpack.js.org/concepts/dependency-graph/)说明了从入口构建依赖图的过程。浏览器原生支持 [ESM](../../glossary/runtime.md#runtime.modules)，也不表示输出分组、压缩和资源管理都失去意义。

开发环境与生产构建可能采用不同的模块提供、优化和缓存策略。开发页面可运行，只能说明该环境的相应路径工作；还要检查生产输出及实际部署地址。

## 转译、压缩、移除和拆分各解决一部分问题

| 操作 | 主要改变什么 | 不能单独保证什么 |
| --- | --- | --- |
| 转译 | 把语法或源格式转换为目标环境接受的形式 | 类型检查通过、目标平台全部 API 都存在 |
| 压缩/最小化 | 减少代码文本及可化简表达 | 业务计算更便宜、运行语义没有风险 |
| Tree Shaking | 根据可达使用和副作用等信息移除不需要的部分 | 任意未使用函数都能被识别、动态行为全部可分析 |
| 代码分割 | 调整哪些代码作为独立资源以及何时加载 | 总下载量更小、没有网络等待或主[线程](../../glossary/systems.md#systems.execution-units)[长任务](../../glossary/frontend.md#frontend.long-tasks) |

HTTP 的 gzip/Brotli 传输压缩又是一层机制，和改写源码的最小化不同。不能把构建文件大小、压缩传输字节、解压后解析成本和执行时间混为一个数。

转译 TypeScript 也不必然执行类型检查。例如 webpack 的 TypeScript 指南明确区分某些 Babel 转换与类型检查工具，见 [webpack TypeScript](https://webpack.js.org/guides/typescript/)。实际质量门禁必须确认哪项任务执行了什么，不能仅凭输出扩展名变成 .js 判断。

## Tree Shaking 需要了解副作用

ESM 的静态导入导出为分析提供了信息，但“某导出未被使用”不说明模块整体都可以删除。模块顶层可能注册插件、修改全局状态、引入样式或执行其他初始化；这些行为即使没有被具名导入，也可能是程序所需。

webpack 的 usedExports 与 sideEffects 承担不同优化职责；声明文件或包没有副作用，会影响工具能否跳过整块模块及相应依赖。错误地标记 sideEffects: false，可能让所需 CSS 或注册行为消失。机制与示例见 [webpack Tree Shaking](https://webpack.js.org/guides/tree-shaking/)。

Rollup 的 treeshake.moduleSideEffects 又有自己的语义。Rollup 核心并不自动把 package.json 的 sideEffects 当作同一开关，包解析插件可以读取并转成相应模块信息。依据见 [Rollup moduleSideEffects](https://rollupjs.org/configuration-options/#treeshake-modulesideeffects)。不能跨工具复制一个布尔值，就认为优化边界完全相同。

动态访问、CommonJS 转换和插件产生的代码会影响分析能力，但不宜笼统断言“CommonJS 永远不能优化”或“ESM 一定全删干净”。需要看实际输出及保留下来的原因；压缩器、副作用标注与源码行为也必须一致。

## import() 建立按需路径，chunk 由构建策略决定

教学片段假定 report.js 提供 renderReport，函数在用户选择打开报表时才调用：

```javascript
async function openReport() {
  const { renderReport } = await import('./report.js');
  renderReport();
}
```

运行到 import() 时请求相应模块；对普通模块，[Promise](../../glossary/runtime.md#runtime.async) 成功兑现表示加载和模块求值已完成，await 后才继续调用 renderReport。已有模块可能复用，不一定重新请求网络；构建工具可能把这条依赖边作为代码分割入口，但不保证“一个 import() 对应一个独立文件”。共享模块、入口策略、输出格式与插件都可能改变资源组合。机制见 [webpack Code Splitting](https://webpack.js.org/guides/code-splitting/)与 [MDN import()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)。

异步导入不等于把模块初始化或 renderReport 放到 Worker。模块求值和调用仍可能在页面主线程产生长任务；await 只是控制后续流程，不能据此证明用户交互不被[阻塞](../../glossary/systems.md#systems.blocking)。执行与让出机制见[浏览器长任务](long-tasks-and-responsiveness.md)。

预取和预加载可能提前取得资源；动态导入若一进入页面就调用，也可能很早开始加载。应分别确认何时请求、何时求值、何时真正使用，而不是只看代码里有没有 import()。

## 拆分有下载、等待和执行之间的取舍

| 教学策略 | 可能收益 | 需要付出的成本 |
| --- | --- | --- |
| 可选报表独立加载 | 没有打开报表的用户少下载一部分初始代码 | 首次打开要等待加载并处理失败 |
| 多页面提取共享库 | 避免多个输出重复包含同一依赖，改善部分缓存复用 | 共享资源可能进入更多页面的依赖与等待路径 |
| 切成很多细小资源 | 提高个别部分的按需粒度 | 请求、元数据、依赖发现和调度开销增加 |

这些是可能性，不是本项目已测收益。[HTTP/2](../../glossary/networking.md#networking.http-versions) 或 HTTP/3 的多路复用也不会消除依赖链、解析/编译和执行成本；不能只按请求数量或单个文件大小选择策略。

评估时先选用户路径，再观察初始和后续加载的传输量、请求瀑布、缓存状态、解析/编译、求值与交互[延迟](../../glossary/performance.md#performance.latency-throughput)。预加载可能把成本提前，压缩可能减少字节却不减少昂贵初始化；需要用同一目标与环境比较。

## 内容摘要帮助版本化，旧引用仍需处理

按内容生成资源名有利于让改变的输出获得新地址，稳定输出继续复用缓存。但引用映射、共享依赖和[运行时](../../glossary/runtime.md#runtime.virtual-machine)代码变化也可能影响其他文件，不能从“源码只改一行”推断只变一个 URL。[webpack Caching](https://webpack.js.org/guides/caching/)说明了 contenthash 及输出关联。

教学故障：旧标签页加载版本 A 的入口，尚未打开报表；部署 B 时清理了 A 的报表 chunk。旧页面稍后仍请求 A 的地址，因文件不存在而失败，新首页是否正常并不能证明这条路径可用。Vite 的[加载错误处理说明](https://vite.dev/guide/build.html#load-error-handling)记录了这类动态导入失效情形。

部署需要让入口与其引用资源一致可用，并依据客户端寿命和保留策略安排旧资源回收；入口文档、内容资源、[CDN](../../glossary/networking.md#networking.cdn-waf)、[Service Worker](../../glossary/frontend.md#frontend.offline) 和应用数据缓存也各有更新责任。不是换一个 hash 或清一个缓存就完成全部版本切换，见[前端路由与缓存](routing-state-and-cache-lifecycles.md)与[条件请求](../api/conditional-requests-and-cache-validation.md)。

加载失败要有可见状态与处理策略，区分网络、资源版本和模块求值错误。刷新可能丢失未保存输入，[重试](../../glossary/api.md#api.retries)也未必修复求值缺陷；不能无限刷新或重试到白屏问题被掩盖。发布与回退继续见[交付生命周期](../devops/build-deploy-rollback.md)。

## 自检与验证范围

先画入口、按需功能和共享依赖的图，再推演首次访问、重复访问、慢网络、模块顶层[异常](../../glossary/runtime.md#runtime.errors)和旧标签页跨版本导航。分别说明哪些代码被移除、哪些只是延后取得，以及失败时用户看到什么。

自检：某模块被保留是因为导出使用还是副作用？构建是否真的执行类型检查？资源下载完成后，初始化是否仍会阻塞主线程？旧入口引用的文件能保留多久，由谁处理过期客户端？

2026-10-20 核查 webpack、Rollup、MDN 与 Vite 官方文档，状态为 source-checked。未更改本站打包配置，未执行 Tree Shaking、chunk 大小/性能、预加载、[缓存失效](../../glossary/cache-search.md#cache-search.invalidation)或跨版本资源对照实验；本站阅读构建不作为这些优化结论的实测证据。
