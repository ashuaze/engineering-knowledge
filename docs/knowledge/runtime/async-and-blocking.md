---
id: "kb-runtime-async-blocking"
title: "同步、异步与阻塞：先说清观察边界"
kind: "comparison"
domain: "runtime"
status: "evolving"
summary: "分清结果交付、线程等待和 CPU 工作，解释为什么 async 仍可能阻塞。"
created: "2026-10-16"
updated: "2026-10-16"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-api-idempotency", "kb-performance-slow-api", "kb-frontend-long-tasks", "kb-systems-execution-units"]
tags: ["concurrency", "runtime"]
---

# 同步、异步与阻塞：先说清观察边界

学习入口：写了 async，其他请求为什么仍然卡住？前置知识：JavaScript 函数调用、Promise 与线程的基本概念。本文比较调用契约和线程等待两个维度，示例未作为自动实验执行。

## 比较基准：调用契约、线程等待与实际工作

分析一个调用时，先说清“哪个调用、哪个线程、哪个时间段”。同步/异步主要讨论调用与完成结果的协调方式；阻塞/非阻塞讨论指定操作是否让当前执行线程等待。两组词描述不同维度，不能只凭函数名判断吞吐或执行成本。

本文以 JavaScript / Node.js 的应用开发视角讨论，不试图用一张四象限表统一所有操作系统异步 I/O API。

| 观察点 | 要问的问题 | 示例 |
| --- | --- | --- |
| 调用契约 | 结果在调用返回时提供，还是稍后交付？ | 返回结果对象，或返回 Promise |
| 当前线程 | 指定操作等待期间，线程能否执行其他任务？ | 阻塞读、就绪通知 |
| 实际工作 | 谁在计算或等待外部资源？ | JS 主线程、内核、线程池、远端服务 |
| 容量 | 工作多了以后在哪里排队？ | 事件循环、工作线程池、连接池、服务端队列 |

这些问题可以独立回答。Promise 是异步结果的抽象，不能据此推出工作已经转移到另一个线程。

## Node.js 的执行位置与等待

Node.js 的事件循环协调回调与 I/O 通知；部分操作由操作系统处理，部分由 libuv 工作线程池承担。应用中的 JavaScript 回调仍可能长时间占用执行线程。不能用“所有异步调用都在后台线程运行”解释它。来源：Node.js 的 Event Loop 与 Don't Block 文档。

实际排查时，可把“主线程忙”“工作线程池排队”“外部依赖等待”当作三个待验证的假设。观察事件循环延迟、CPU profile、任务类别与依赖耗时，避免只看到 CPU 不高便断定系统没有瓶颈。

## 反例：async 不会自动迁移计算

下面是说明性代码，未作为本仓库自动实验执行：

```javascript
async function calculate() {
  let sum = 0;
  for (let i = 0; i < 1_000_000_000; i++) sum += i;
  return sum;
}
```

调用后，函数体会在遇到第一个挂起点之前同步执行。这里没有 await，循环仍占用执行它的 JavaScript 线程；返回 Promise 不会自动把循环放入工作线程。来源：MDN 的 async function 说明。

把循环放入 `Promise.resolve().then(...)` 也只改变其调度时机。是否需要迁移执行位置，应结合实际工作量和迁移成本判断。

## 按工作类型和容量选择方案

- Promise 便于表达稍后完成的结果；选择它时仍要核算工作实际占用的线程与资源。
- 异步 I/O 的并发受线程池、连接池与下游容量约束，增加请求数量时要观察排队。
- 需要并行 CPU 计算时，应另行设计 worker、独立进程或任务服务，并核算传输、调度和结果合并成本。

比较方案时明确相同负载、运行环境与观察指标，避免只凭 async 关键字做性能判断。

### 排查常见误判

- 将同步大文件读取放进请求处理，其他请求可能一起等待。
- 把大型 JSON 转换、压缩或循环塞进 Promise，以为获得了并行。
- 用无限并发的异步请求压满连接池，下游开始排队。
- 用大量微任务延迟其他任务的执行机会；具体调度规则需按宿主验证。

这些是排查方向，是否发生需要观测证据。增加异步调用数量本身不能证明系统吞吐提高。

## 对照验证与自检

工程案例入口是[慢 API 排查](../performance/slow-api-investigation.md)，其中的教学推演用于拆分执行时间与排队时间。

验证计划：在相同负载下观察 CPU 循环与 I/O 等待时的事件循环延迟、CPU profile 和依赖耗时，检查“主线程忙”与“外部等待”是否具有不同证据。本文未执行此对照实验；具体结果需要在选定 Node.js 版本与环境中记录。

面对一个“异步接口”，画出调用返回、工作执行、完成通知三个时刻，并注明执行者。然后回答：若任务数量翻十倍，谁会先排队？如果无法回答，还需要补齐宿主和依赖的调度机制。

## 关联阅读

- [API 幂等性](../api/idempotency.md)：异步完成与重试也会带来结果未知。
- [慢 API 排查](../performance/slow-api-investigation.md)：把等待时间拆开。
- [浏览器长任务](../frontend/long-tasks-and-responsiveness.md)：在浏览器宿主中分析输入、任务与绘制，并设计让出策略。
- [进程、线程与协程](../systems/process-thread-coroutine.md)：解释资源边界与调度位置，区分并发与并行。

## 来源与核查

核查日期：2026-10-16；核查范围为 async 执行边界、事件循环与线程池的基本机制，未执行上述 JavaScript 片段。

- [MDN：async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [Node.js：The Event Loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Node.js：Don't Block the Event Loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop)
