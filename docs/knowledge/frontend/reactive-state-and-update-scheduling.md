---
id: "kb-frontend-reactive-updates"
title: "响应式状态与更新：值变了，界面为什么还没变"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "区分数据修改、依赖追踪、更新调度、DOM 提交与浏览器呈现，用 Vue 和 React 例子限定各自机制。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-runtime-closures", "kb-runtime-event-loop"]
related: ["kb-frontend-rendering-hydration", "kb-frontend-routing-cache", "kb-frontend-long-tasks", "kb-runtime-gc", "kb-frontend-reconciliation-identity"]
tags: ["reactivity", "state", "scheduling", "rendering"]
---

# 响应式状态与更新：值变了，界面为什么还没变

学习入口：控制台里的状态已经更新，页面为何仍显示旧内容？前置：对象引用、[闭包](../../glossary/runtime.md#runtime.closure)、[事件循环](../../glossary/runtime.md#runtime.event-loop)与 [DOM](../../glossary/frontend.md#frontend.render-tree)。要分别确认改了哪个状态、框架是否观察到、更新是否获调度、结果是否提交到 DOM，以及浏览器是否已经呈现。不同框架的“[响应式](../../glossary/frontend.md#frontend.state)”不代表同一种检测和调度实现。

状态属于哪个实例、列表重排后怎样保留或重置，继续见[组件协调与 key](reconciliation-keys-and-component-identity.md)。更新调度与[组件身份](../../glossary/frontend.md#frontend.component-identity)要分别判断。

## 从数据到像素有多段边界

| 阶段 | 观察的事实 | 不能直接推出什么 |
| --- | --- | --- |
| 修改状态或提出更新 | 某值变了，或框架接到一次更新请求 | 当前处理器的局部变量已改变 |
| 确定受影响计算 | 找到依赖或需要重新执行的组件 | 所有组件都要重建 |
| 调度与计算输出 | [排队](../../glossary/performance.md#performance.queueing)、合并工作，计算下一份 UI 描述 | DOM 已经提交或浏览器已绘制 |
| 提交 DOM 更新 | 必要 DOM 变更已应用 | 所有节点被替换，或用户已看到新像素 |
| 浏览器呈现 | 根据样式、布局等工作显示结果 | 此前的业务计算没有额外成本 |

这是帮助定位问题的分层，不是所有框架的固定内部流水线。[React Render and Commit](https://react.dev/learn/render-and-commit)明确区分渲染计算、提交与浏览器绘制。重新执行组件函数不等于重新创建全部 DOM；[虚拟 DOM](../../glossary/frontend.md#frontend.vdom) 是组织 UI 描述与协调更新的一种方法，也不是所有响应式系统的必要条件。

## Vue 的属性追踪与普通局部值不同

[Vue 3 的响应式机制](https://vuejs.org/guide/extras/reactivity-in-depth.html)通过代理等方式拦截相应读取与写入，在有效依赖收集上下文中建立关联，再触发订阅更新。不是任意变量赋值都会通知界面；读取是否经过响应式入口、是否被相关计算使用，都影响结果。

下面仅是 Vue 3 模块语境的教学片段，没有创建或挂载组件：

```javascript
import { reactive } from 'vue';

const state = reactive({ count: 0 });
const { count } = state;
state.count = 1;
```

按此片段推演，state.count 为 1，局部 count 仍为 0。对数字属性的这次解构先读取了值，局部绑定不再通过 state.count 访问原代理；它不是一个自动跟随的引用。这个结论不意味着“所有解构都让对象内部失去响应性”，对象属性的后续访问还要看实际引用是否为响应式代理。

[Vue Reactivity Fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)还区分 reactive 对象、ref 与 DOM 更新时间。需要保留响应关系时，应按框架契约选择属性访问、getter 或引用工具；不能只因两个变量初始化时相等，就认定它们以后保持[同步](../../glossary/runtime.md#runtime.async)。

## React 的更新队列不是原地修改当前快照

React 状态 setter 提出后续更新，当前渲染里的局部状态值仍来自该次快照。它与 Vue 代理属性直接修改的模型应分别理解，闭包关系见[词法绑定](../runtime/closures-and-lexical-bindings.md)。

教学设定：一个 React 函[数组](../../glossary/algorithms.md#algorithms.sequences)件的普通点击处理器中，当前 count=0，顺序调用两次 `setCount(count + 1)`。两次都根据同一个局部 0 提议替换为 1，不能把它推演成两次递增到 2；若改为两次纯 updater `setCount(n => n + 1)`，且没有其他更新，则按[队列](../../glossary/algorithms.md#algorithms.queues)前值连续计算，推演结果为 2。

[React 的更新队列说明](https://react.dev/learn/queueing-a-series-of-state-updates)解释了这一差别和[批处理](../../glossary/performance.md#performance.batching)。updater 需要保持纯计算，不能把网络请求或扣款塞进去；也不能把一个事件中的算例扩大成“所有框架、所有异步边界都以相同方式合并”。

## 派生值与副作用要分工

派生值用于从现有状态计算结果，例如从商品与数量计算小计。把每个可计算结果都另外存一份，会增加不同步的状态；但是否缓存派生计算，还要考虑框架的依赖、失效及计算成本。

副作用则与外部世界交互，例如发请求、订阅或写日志。它需要触发条件和清理规则：不应在一次可能重复的 UI 计算中无条件提交业务写入，也不应让派生值更新反过来不断修改自己的输入，形成无进展循环。

[Vue Watchers](https://vuejs.org/guide/essentials/watchers.html)说明依赖变化后旧请求仍可能回调，并提供清理机制。清理可以减少过期工作，但应用仍应检查返回结果是否属于当前任务、对象与身份；取消等待不能证明远端写入已撤销。这里没有实现网络请求或断言某个清理 API 能解决所有竞争。

## DOM 更新完成与绘制完成不能混用

在 Vue 中，`await nextTick()` 用于等待相应 DOM 更新完成，不能因此声称浏览器已经绘制一帧。按上述 Watchers 文档，默认 watcher 在相关父组件更新之后（若有）、所属组件 DOM 更新之前运行；post watcher 在所属组件 DOM 更新之后运行；同步 watcher 同步触发且不进行常规批处理。不能只见到“监听回调已运行”就认定组件 DOM 已是新版本，这些时机也都不等于绘制完成。

React 的渲染/提交和浏览器绘制同样分属不同阶段。无论框架，长时间同步计算或持续[微任务](../../glossary/runtime.md#runtime.microtasks)仍可能推迟用户可见反馈。若目标是解释一次交互[延迟](../../glossary/performance.md#performance.latency-throughput)，应查看[长任务与呈现证据](long-tasks-and-responsiveness.md)，而不是用“响应式更新很快”替代时间线。

## 状态归属决定保留与重置

局部状态、跨组件共享状态、URL 参数与服务端数据有不同生命周期。先确定谁有权修改、谁负责失效，再决定放在哪里；把所有数据移到全局 Store，可能延长过期数据和订阅的生命。

组件 identity、列表 key 或缓存保留策略改变时，状态可能保留或重建。key 用来表达合适的身份，不是修复所有“不更新”的万能开关；强制重建可能掩盖错误引用，同时丢失用户输入并增加工作。具体导航关系见[路由与缓存](routing-state-and-cache-lifecycles.md)。

## 按失败阶段做自检

| 现象 | 应检查的边界 |
| --- | --- |
| 源对象已改，局部值不变 | 是否提前读取了普通值或另一份对象 |
| 框架排了更新，页面仍旧 | 是否仍在执行当前任务，DOM 与绘制各到哪一步 |
| 列表内容对应错行 | 数据身份、组件身份与局部状态是否匹配 |
| 快速切换后旧结果覆盖新结果 | 请求归属、清理与结果应用条件 |
| 一次改动反复触发更新 | 是否重复维护派生状态或副作用循环 |

自检：为什么 state.count 改变不改写已解构的数字 count？连续两次 setter 为什么未必递增两次？nextTick 完成后能否证明用户已经看到结果？

核查日期：2026-10-20。机制依据核查日 Vue 3 与 React 官方在线文档；示例与诊断表为教学推演，没有新增框架挂载、更新次数、网络竞争或性能实验。[既有长任务实验](long-tasks-lab.md)仍只支持原有合成页面的调度范围，不是本篇响应式框架集成验证。
