---
id: "kb-runtime-closures"
title: "闭包与词法绑定：回调为什么读到旧值"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "沿定义位置、环境实例和读取时刻解释闭包，区分共享绑定、提前计算的值与框架渲染快照。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: []
related: ["kb-runtime-event-loop", "kb-runtime-gc", "kb-frontend-reactive-updates", "kb-frontend-routing-cache", "kb-systems-races-atomicity", "kb-runtime-modules-cycles"]
tags: ["closure", "scope", "binding", "javascript"]
---

# 闭包与词法绑定：回调为什么读到旧值

学习入口：值已经改了，稍后运行的回调为什么仍显示旧结果？前置：JavaScript 函数、变量声明与对象引用。先找回调访问的是哪一次执行创建的绑定，再看值在哪里、何时被读取或计算。[闭包](../../glossary/runtime.md#runtime.closure)既不自动冻结全部值，也不自动改读所有地方的“最新同名变量”。

## 函数沿定义环境寻找名字

闭包可以理解为函数及其能够访问的外层词法环境。词法作用域按代码的定义位置建立名字关系；把函数交给另一个调用者，不会让外层变量自动变成调用者的同名局部变量。[ECMAScript 的环境记录与名字解析](https://tc39.es/ecma262/multipage/executable-code-and-execution-contexts.html#sec-environment-records)用环境链描述这类查找关系。

要区分三个对象：源码中的变量名、一次执行创建的绑定，以及绑定当前指向的值。相同名字可以出现在不同环境中；同一个绑定也可能在后续被赋予新值。环境记录是规范模型，不表示引擎必须按同一种堆内存布局实现。

## 共享绑定与提前计算的值不同

下面是独立 JavaScript 片段的教学推演，没有运行计时器或框架：

```javascript
function makeReading() {
  let value = 0;
  const saved = value;
  return {
    advance: () => { value += 1; },
    current: () => value,
    atCreation: () => saved,
  };
}

const first = makeReading();
const second = makeReading();
first.advance();
```

| 随后调用 | 推演值 | 原因 |
| --- | --- | --- |
| first.current() | 1 | 与 first.advance 访问同一次执行的 value 绑定 |
| first.atCreation() | 0 | saved 初始化时已经读取数字 0，不会因 value 改变而重算 |
| second.current() | 0 | 第二次调用 makeReading 创建另一组绑定 |

“回调取得旧值”可能是提前计算留下了旧结果，也可能是它属于另一组环境。[MDN 闭包指南](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)解释了共享环境与不同函数调用产生环境的区别。判断时不要只对照两个变量名是否拼写相同。

这里 saved 保存的是数字值；若保存的是对象引用，后来仍可能观察到同一对象的修改。const 限制绑定重新赋值，不等于深度冻结对象，更不等于自动复制出独立快照。

## 循环回调为什么可能全读到最后一个数

教学片段：先把函数收进[数组](../../glossary/algorithms.md#algorithms.sequences)，所有循环结束后才调用它们；没有其他代码修改这些变量。

```javascript
function makeReaders() {
  const shared = [];
  const separate = [];
  for (var i = 0; i < 3; i++) shared.push(() => i);
  for (let j = 0; j < 3; j++) separate.push(() => j);
  return { shared, separate };
}
```

按上述前提，shared 中三个回调都读到 3；separate 中依次读到 0、1、2。前者使用同一个函数作用域内的 i 绑定，后者的 for-let 循环为迭代提供不同绑定。这是闭包与声明语义的组合，不是某个回调执行得慢，也不需要定时器才能出现。

若后来继续修改某个共享绑定，读取结果还会随之改变；若循环内本就提前生成字符串，修正变量声明也不会让已经生成的字符串自动重算。先辨别“保留了绑定”与“保留了计算结果”，再决定改哪里。

## 框架快照不是另一套闭包规则

[React 的状态快照说明](https://react.dev/learn/state-as-a-snapshot)中，函数组件某次渲染生成的处理器会使用该次渲染的状态。设置 state 请求后续渲染，不会修改已经运行的这次函数中那个局部状态值；新渲染会建立新的处理器与绑定关系。

因此，旧处理器保留旧渲染环境，并不反驳“闭包可以观察共享绑定的后续修改”。两种情形里访问的绑定并不相同。不要把 React 的渲染快照套到所有普通 JavaScript 变量，也不要把 Vue [响应式](../../glossary/frontend.md#frontend.state)对象的属性读取套成所有框架都一样。

要先决定业务需要哪种语义：保存“用户发起这次动作时的对象和条件”，还是在回调执行时重新读取“当前有效对象和条件”。盲目追求最新值可能把旧请求的结果写进新的页面对象。跨请求的归属检查见[前端路由与缓存](../frontend/routing-state-and-cache-lifecycles.md)。

## 调度时刻与数据来源分别排查

闭包说明函数能访问什么，[事件循环](../../glossary/runtime.md#runtime.event-loop)说明它何时有机会执行。把函数放进 [Promise](../../glossary/runtime.md#runtime.async)、计时器或事件监听，不会因此自动复制它读取的数据；一个同步调用也可能读取另一环境的旧绑定，见[事件循环与微任务](event-loop-and-microtasks.md)。

| 现象 | 优先追问 |
| --- | --- |
| 所有循环回调结果相同 | 是否共享同一个循环绑定，调用发生在什么时候 |
| 某回调始终返回初始字符串 | 字符串是否在建立回调前就计算完成 |
| 新界面有新值，旧处理器仍用旧值 | 处理器属于哪次渲染，是否仍注册着旧函数 |
| 异步结果覆盖另一对象 | 回调身份、请求条件和当前目标是否仍一致 |

修复应针对需要的语义：建立独立环境、延后读取、重算派生值、更新订阅，或者拒绝过期回调。单纯[延迟](../../glossary/performance.md#performance.latency-throughput)执行或加一次 await，通常不能修复错误的数据归属。

## 保留环境也带来生命周期成本

闭包可以封装私有状态、参数化行为和清理函数，也可能因长寿命监听器、定时器或缓存引用而延长对象[可达性](../../glossary/runtime.md#runtime.reachability)。函数返回不代表相关对象一定回收；但闭包存在也不等于内存泄漏，更不能断言引擎保留了整个作用域的全部变量。

注册与注销、启动与取消应配对，清理需要同一函数身份等相应条件。内存保留路径与 [GC](../../glossary/runtime.md#runtime.gc) 的判断继续见[可达性与垃圾回收](reachability-and-garbage-collection.md)，不要仅凭函数嵌套层数推导性能或内存数量。

自检：first.current 和 first.atCreation 为什么不同？如果 saved 改为对象引用，又能否称作独立快照？循环回调的执行顺序相同，为什么 var 与 let 仍可能读到不同结果？

核查日期：2026-10-20。词法绑定依据 ECMAScript 规范与 MDN，渲染快照例子依据 React 官方资料。片段输出与诊断表为指定前提下的教学推演，没有新增脚本执行、框架对照、内存快照或性能实验。继续读[响应式状态与更新](../frontend/reactive-state-and-update-scheduling.md)，区分读取绑定与框架更新界面。

[模块系统与循环依赖](modules-bindings-and-circular-dependencies.md)继续区分 [ESM](../../glossary/runtime.md#runtime.modules) 活绑定、读取后保存的值与初始化时刻；这些语言片段仍为纸面推演，没有新增模块执行实验。
