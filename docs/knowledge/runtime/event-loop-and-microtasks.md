---
id: "kb-runtime-event-loop"
title: "事件循环与微任务：回调为什么还没有执行"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "区分当前执行、任务、微任务和渲染机会，解释 Promise 续体、定时器与宿主差异。"
created: "2026-10-16"
updated: "2026-10-23"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: ["kb-runtime-async-blocking"]
related: ["kb-frontend-long-tasks", "kb-systems-execution-units", "kb-performance-latency-queues", "kb-runtime-gc", "kb-systems-races-atomicity", "kb-runtime-closures", "kb-frontend-reactive-updates", "kb-systems-io-multiplexing", "kb-runtime-exception-propagation"]
tags: ["event-loop", "microtasks", "scheduling"]
---

# 事件循环与微任务：回调为什么还没有执行

等待 [Promise](../../glossary/runtime.md#runtime.async) 的拒绝怎样进入 catch、为什么注册定时器时的 try 捕获不了稍后回调的抛出，继续见[异常传播与异步边界](exceptions-unwinding-cleanup-and-async-boundaries.md)。这里补充阅读关联，原调用顺序与宿主核查范围保持各段声明。

学习入口：[Promise](../../glossary/runtime.md#runtime.async) 已经完成，回调为什么仍在等？用了 await，页面为什么没有画出新状态？前置知识：函数调用、Promise 与[同步/异步](async-and-blocking.md)。本文先讨论浏览器 Window 的常见调度过程，再说明 Node.js 的不同；示例是依据规范的推演，没有进行浏览器性能实测。

## 就绪、排队与执行是三个状态

外部工作完成，只代表结果可以交付；执行回调仍需要调度机会。[事件循环](../../glossary/runtime.md#runtime.event-loop)（Event Loop）协调任务执行等宿主工作，不能把它理解成“轮流取出所有回调的一个[队列](../../glossary/algorithms.md#algorithms.queues)”。

| 对象 | 作用 | 需要保留的边界 |
| --- | --- | --- |
| 当前 JavaScript 执行 | 函数沿[调用栈](../../glossary/systems.md#systems.memory-layout)推进 | 同一执行[线程](../../glossary/systems.md#systems.execution-units)不能同时执行另一个普通回调 |
| [Task](../../glossary/runtime.md#runtime.microtasks)（任务） | 承载脚本、定时器回调、部分输入处理等工作 | 浏览器有多个任务来源，跨来源没有统一的入队先后承诺 |
| Microtask（微任务） | 承载 Promise 反应、queueMicrotask 等工作 | 在微任务检查点处理，不抢占正在执行的同步代码 |
| 渲染机会 | 宿主在合适时机更新界面 | 不保证每个任务后都绘制一次 |

[HTML 标准的事件循环处理模型](https://html.spec.whatwg.org/multipage/webappapis.html#event-loop-processing-model)定义了任务选择、微任务检查点和相关调度步骤。常见的简化路径是“运行任务 → 微任务检查点 → 后续调度”；微任务检查点也会出现在其他规范指定的位置，不能据此画成每轮固定绘制一帧的流水线。

## 按入队时刻推演一次输出

假设下面代码作为浏览器中一个普通脚本任务执行，没有其他代码干预；console 的字母仅用来表示调用顺序。

```javascript
console.log('A');
setTimeout(() => console.log('T'), 0);
Promise.resolve().then(() => {
  console.log('P');
  queueMicrotask(() => console.log('Q'));
});
queueMicrotask(() => console.log('M'));
console.log('B');
```

同步部分先调用 A、B；P 和 M 对应的微任务已经依次入队。到检查点时先执行 P，P 新增的 Q 排到 M 后面，所以微任务部分为 P、M、Q，定时器任务 T 随后才有机会运行。推演的调用顺序为 `A B P M Q T`。

这说明已经兑现的 Promise 也不会让 `.then` 回调插进当前同步语句之间。`setTimeout(..., 0)` 表示请求一个计时器调度，不能当作立即执行或准确耗时保证。不要把这个片段的顺序扩展为所有网络、输入、渲染回调之间的全局顺序。

## await 为什么不保证给绘制让路

await 挂起当前 async 函数，后续继续执行通过 Promise 相关机制调度。如果等待的是已经兑现的 Promise，续体可以在后续微任务中运行；这不等于把控制权交给下一次输入处理或绘制。

```javascript
// 反例示意：处理每项后只让出到微任务，不能据此保证页面流畅。
for (const item of items) {
  processOne(item);
  await Promise.resolve();
}
```

微任务检查点会继续处理队列中新加入的微任务；持续追加工作可能推迟后续任务。[MDN 的微任务指南](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)专门提醒这种饥饿风险。`processOne` 本身如果很重，每次同步执行也仍会占用线程。

需要让界面获得调度机会时，应按目标设计[任务切片](../../glossary/frontend.md#frontend.long-tasks)或把适合的计算交给 Worker，并检查状态在切片间是否仍然有效。`requestAnimationFrame` 适合安排绘制前的更新，其回调中的大量计算仍可能拖延呈现。具体切片与观测方法见[浏览器长任务](../frontend/long-tasks-and-responsiveness.md)。

## Node.js 需要另一张宿主地图

Node.js 没有浏览器页面绘制阶段，它用 timers、poll、check 等阶段协调计时器与 I/O，并有 `process.nextTick` 的额外调度机制。[Node.js 官方说明](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)还记录了 libuv 1.45.0 / Node.js 20 起计时器阶段行为的调整。

因此不要把浏览器图直接用于 Node.js，也不要在未说明顶层执行、I/O 回调、模块类型和版本时，声称 `setTimeout`、`setImmediate`、`nextTick` 与 Promise 有一个永远相同的总顺序。概念上先标出当前执行位置、入队位置与宿主规则，再对具体片段判断。

无论哪种宿主，把 CPU 密集计算移进 `.then` 都不会自动创建[并行](../../glossary/systems.md#systems.concurrency)执行者；增加[排队](../../glossary/performance.md#performance.queueing)回调也不会增加处理容量。长回调和过量微任务是两种不同的[阻塞](../../glossary/systems.md#systems.blocking)调度机会的方式。

## 自检与待验证项

对上面的输出片段，逐步列出同步栈、微任务队列和待运行定时器，再预测把 Q 改成普通函数直接调用后会改变哪一段顺序。解释为什么仅凭这条输出不能证明中间发生过绘制。

若要验证界面响应，应另外录制输入、脚本、微任务与呈现的时间线；若研究 Node.js，记录 Node/libuv 版本、[CommonJS](../../glossary/runtime.md#runtime.modules)/ESM 和代码入口。本文没有执行这些宿主对照与性能实验，输出顺序是指定前提下的规范推演。

回调何时运行与读取哪份数据分别排查，见[闭包与词法绑定](closures-and-lexical-bindings.md)；框架的依赖、更新队列与 [DOM](../../glossary/frontend.md#frontend.render-tree) 提交，见[响应式状态与更新](../frontend/reactive-state-and-update-scheduling.md)。两篇示例为教学推演，不新增本文调度实测。

## 关联阅读与来源

Linux 就绪接口可继续读 [I/O 多路复用](../systems/io-multiplexing-readiness-and-event-loops.md)，区分内核通知、非阻塞操作与应用待处理状态；这只是一个宿主层参照，不把浏览器事件循环等同于 [epoll](../../glossary/systems.md#systems.io-multiplexing)，也没有新增调度实测。

- [竞态与原子性](../systems/races-and-atomicity.md)：同一事件循环在实际挂起点之间也可能发生业务竞态；这不等同于语言[内存模型](../../glossary/systems.md#systems.memory-order)中的数据竞争。
- [可达性与垃圾回收](reachability-and-garbage-collection.md)：检查回调持有路径，另用证据判断内存压力与暂停。
- [同步、异步与阻塞](async-and-blocking.md)：先确定调用契约和工作执行者。
- [浏览器长任务](../frontend/long-tasks-and-responsiveness.md)：把调度机制映射到点击迟到的证据。
- [进程、线程与协程](../systems/process-thread-coroutine.md)：任务队列与并行执行者属于不同层次。
- [延迟、吞吐与排队](../performance/latency-throughput-and-queues.md)：就绪工作仍可能等待稀缺执行资源。

核查日期：2026-10-16。浏览器机制依据当日 HTML Living Standard 与 MDN，Node.js 差异依据官方说明；不保证跨版本片段的全部输出或具体毫秒数。

- [WHATWG HTML：Event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [MDN：Using microtasks in JavaScript](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [Node.js：The Node.js Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
