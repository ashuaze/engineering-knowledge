---
id: "kb-frontend-reconciliation-identity"
title: "组件协调与 key：列表变了，状态应该跟着谁走"
kind: "concept"
domain: "frontend"
status: "evolving"
summary: "从组件身份解释描述、协调与提交，推演索引 key、稳定业务 key 和主动重置的区别，限定 React 与 Vue 的各自语义。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-frontend-reactive-updates", "kb-frontend-rendering-hydration"]
related: ["kb-frontend-routing-cache", "kb-runtime-closures", "kb-frontend-web-vitals", "kb-frontend-bundling-splitting"]
tags: ["reconciliation", "keys", "component-identity", "rendering"]
---

# 组件协调与 key：列表变了，状态应该跟着谁走

学习入口：列表头部插入一条记录，为什么原本给 B 输入的草稿跑到了 A 的行里？文字已经更新，某行的输入、展开状态或焦点却还像旧数据。需要先判断“哪一个组件实例仍代表原来那条记录”，再讨论减少了多少 [DOM](../../glossary/frontend.md#frontend.render-tree) 操作。

前置：[响应式状态与更新](reactive-state-and-update-scheduling.md)、[渲染与 Hydration](rendering-and-hydration.md)。本文使用 React 官方学习文档和 Vue 3 列表机制说明；两者是各自的公开语义参照，不是所有框架的统一算法规范。表格与片段是纸面设计，没有挂载组件、操作输入框或测量协调成本。

## 重新计算描述不等于重建全部节点

[虚拟 DOM](../../glossary/frontend.md#frontend.vdom) 用对象等结构描述预期 UI；协调更新（reconciliation）确定新旧描述之间的对应与必要变更。框架计算下一份输出、提交真实 DOM，以及浏览器后续布局/绘制，是不同阶段。React 的 [Render and Commit](https://react.dev/learn/render-and-commit)明确区分这些工作，并要求渲染计算保持纯净。

渲染函数再次执行，可能得到与上次相同的输出；提交阶段也可能只改一个属性。反过来，计算结果很小也不能保证浏览器没有布局成本。不要用“render 次数”直接代替 DOM 变更次数、组件重建次数或用户等待时长。

渲染过程中发送订单、修改外部共享对象等副作用，会把“尝试计算一份 UI”错误地变成业务提交点。应按框架约定把交互和外部系统的状态协调放在合适边界；即使移到事件或 effect 中，业务重放安全仍需服务端保证。

## 身份来自树中上下文，不只来自数据相等

在 React 中，状态与渲染树位置关联，组件类型和 key 参与决定保留或重置。key 的身份范围是同一父级下的兄弟项；它不是全应用通用主键，也不是自动传入子组件的普通属性。依据见[状态保留与重置](https://react.dev/learn/preserving-and-resetting-state)及[列表 key 规则](https://react.dev/learn/rendering-lists#rules-of-keys)。

| 变化 | 应检查的身份条件 | 不能直接保证 |
| --- | --- | --- |
| 同一实例收到新数据 | 父级位置、类型、key 是否仍对应 | 内部草稿自动按新数据重置 |
| 同级列表重新排序 | [稳定 key](../../glossary/frontend.md#frontend.component-identity) 是否继续代表相同业务记录 | 不发生任何移动、渲染或布局 |
| key 改变或组件类型改变 | 是否有意丢弃旧实例并创建新实例 | 外部数据缓存和服务端状态同时清空 |
| 相同 key 移到另一父级 | 身份上下文已经改变 | 原组件状态仍会自动迁移 |

若子组件还需要记录 ID，应另传业务属性。`key` 负责协调，`recordId` 负责组件使用的数据语义，二者即使取同一值也承担不同职责。

## 纸面推演：插入记录后草稿归谁

假设同一父组件下有两个同类型 `Row`，每行用自己的组件状态保存草稿。初始顺序是 `[A, B]`，草稿分别为“甲”“乙”；父组件把新记录 X 插入头部。假设除协调身份变化外，不额外移除行或重置状态。

| key 方案 | 更新前的身份 | 更新后 `[X, A, B]` 的对应 | 结果 |
| --- | --- | --- | --- |
| [数组](../../glossary/algorithms.md#algorithms.sequences)索引 | `0→A/甲`，`1→B/乙` | `0→X`，`1→A`，`2→B` | X 继承原位置 0 的“甲”，A 继承位置 1 的“乙”，B 获得新状态 |
| 稳定记录 ID | `A→A/甲`，`B→B/乙` | `X→X`，`A→A`，`B→B` | X 新建，A/B 的草稿继续属于 A/B |
| 每次渲染新生成随机 key | 旧值无法再次匹配 | 每项都成为新的协调身份 | 草稿可能全部丢失，并增加重建成本 |

这个反例的关键是“组件内部有独立草稿”。如果状态完全由父级按记录 ID 管理，结果还取决于外部数据与传参，不能照搬表中的表现。索引在顺序与成员永不变化、输出不依赖实例状态等严格条件下可以适用；应证明这些条件，而非只因为当前看不出问题就认定安全。

说明性 React 片段只展示两类标识，没有完整实现 `Row`：

```jsx
items.map(item => (
  <Row key={item.id} recordId={item.id} label={item.label} />
))
```

ID 应在记录创建时确定并随记录保存。重复 ID 不能提供可靠对应；在每次渲染时重新产生 ID，同样失去了跨更新的身份信息。

## Vue 的就地更新与有 key 更新要分开理解

Vue 3 对无 key 的 `v-for` 列表默认采用就地修补，适合不依赖子组件状态和临时 DOM 状态的输出；提供唯一 key 后，框架可以跟踪节点身份并复用、重排。依据见 [Vue 列表状态与 key](https://vuejs.org/guide/essentials/list.html#maintaining-state-with-key)。这与上面的状态归属问题相关，但不意味着 React 和 Vue 使用相同差分细节或移动策略。

具体实现可能使用编译信息、静态标记及不同列表算法。本文不从 key 规则推出所有更新都是某个固定复杂度，也不声称虚拟 DOM 必然比直接 DOM 操作快；有效比较要包含描述分配、比较、提交与浏览器成本。

## 主动重置也是身份设计

编辑面板从订单 A 切到订单 B 时，可按业务意图选择保留、按 ID 分开保存，或用新的协调身份重置局部状态。重置实例不是清理所有系统状态的总开关：进行中的请求、全局缓存、外部订阅和已提交写入各有责任。

例如 A 的请求在切到 B 后迟到，即使 B 的组件是新建的，未正确隔离的共享数据仍可能被覆盖，见[路由与缓存生命周期](routing-state-and-cache-lifecycles.md)。稳定 key 解决“状态跟谁走”，不替代请求版本、取消、资源释放与[授权](../../glossary/security.md#security.identity)。

## 自检

1. 为什么一次 render 不等于重建全部 DOM，也不等于用户已看到更新？
2. 索引 key 的纸面插入例子里，X、A、B 分别得到哪份草稿？前提是什么？
3. 稳定 key 能否保证同一记录移到另一父级后仍保留实例状态？为什么？
4. 随机 key、重复 key 和按记录 ID 建立的 key，各缺少或保留了什么信息？
5. 切换订单时改变 key，为什么不能证明旧请求和全局缓存已经失效？

## 来源与核查

2026-10-26 核查 React 官方上述三篇学习文档（页面标示 v19.3）与 Vue 3 列表文档，均为滚动资料；引用范围为公开身份与阶段语义，不绑定内部算法。本文为 source-checked 概念文章；未运行 React/Vue、验证 DOM/焦点行为、依赖清理或性能基准。
