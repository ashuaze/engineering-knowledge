<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 前端与浏览器

建议优先级：P1。目标：具备端到端交付能力，理解渲染、状态和网络边界。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

首屏已出现却不能交互，可能卡在哪个阶段？

## 已有正文

- [浏览器长任务：页面已显示为何仍点不动](long-tasks-and-responsiveness.md)：区分内容显示、事件处理和下一次绘制，用任务切片与观测验证交互阻塞。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| DOM / CSSOM / Render Tree | 文档、样式和渲染结构。 |
| Layout / Paint / Compositing | 布局计算、绘制与图层合成。 |
| CSR / SSR / SSG / ISR | 客户端渲染、服务端渲染、预生成与增量再生成。 |
| Hydration | 让服务端输出的页面连接客户端交互逻辑。 |
| SPA / Client-side Routing | 单页导航与客户端路由状态。 |
| Reactivity / State Management | 数据变化、界面更新及状态所有权。 |
| Virtual DOM / Reconciliation | UI 描述与更新协调策略。 |
| Bundling / Tree Shaking | 模块打包与可证明无用代码的移除。 |
| Browser Cache / Service Worker | 响应复用、请求代理和离线能力。 |
| WebSocket / SSE | 双向连接通信与服务器事件推送。 |
| Core Web Vitals | 衡量加载、交互和布局稳定性的指标集合。 |
| BFF | 为特定客户端提供聚合和适配的后端。 |
| Long Task / Main-thread Yielding | 识别持续占用主线程的任务，分批执行并让出调度机会。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
