---
id: "kb-runtime-exception-propagation"
title: "异常传播与资源清理：失败怎样跨调用栈和异步边界"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "沿调用、清理与异步完成区分异常传播，解释原因链、finally 覆盖、取消和状态恢复，以及捕获与业务回滚的边界。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-runtime-async-blocking", "kb-runtime-event-loop"]
related: ["kb-runtime-ffi-boundaries", "kb-systems-signals-shutdown", "kb-reliability-retry-budgets", "kb-api-idempotency", "kb-runtime-virtual-machines"]
tags: ["exceptions", "cleanup", "async", "cancellation"]
---

# 异常传播与资源清理：失败怎样跨调用栈和异步边界

学习入口：函数外面已经写了 catch，为什么稍后仍出现未处理失败；即使捕获了，为什么订单也没回滚？前置：[同步、异步与阻塞](async-and-blocking.md)、[事件循环](event-loop-and-microtasks.md)。本文用 ECMAScript 与 Python 3.13 区分控制流、资源与业务状态，不把一种语言的[异常](../../glossary/runtime.md#runtime.errors)规则推广到全部 [Runtime](../../glossary/runtime.md#runtime.virtual-machine)；片段和时序未执行。

## 异常把控制权交给能处理它的边界

[同步](../../glossary/runtime.md#runtime.async)调用链 `入口 → service → parse` 中，parse 抛出后，尚未执行的普通语句不会按正常路径继续；相应调用边界寻找匹配处理器，并在传播中运行语言规定的清理。最终入口可能把失败转换成响应，或让任务失败。通常称这段退出过程为栈展开；实际帧、异常表和优化实现不由这个术语唯一规定。

| 表达方式 | 调用方要做什么 | 需要另外确认 |
| --- | --- | --- |
| 抛出异常 | 捕获可处理类型，或继续传播 | 哪些清理会运行，原始原因是否保留 |
| 返回 Result / 错误码 | 检查结果并显式分支 | 调用方是否忽略错误，失败分支是否有效 |
| 异步完成失败 | 等待或订阅失败通道 | 谁拥有任务，何时观测，未处理时宿主如何反应 |

Python 的[错误与异常说明](https://docs.python.org/3.13/tutorial/errors.html)展示异常向调用者传播和 `raise ... from ...` 原因链。包装底层错误时，应保留机器可分辨的类型/代码、原始原因和必要操作上下文；只复制一段 message 容易丢失诊断依据。对外响应与内部日志又有不同的敏感信息边界。

## finally 负责退出路径，不保证恢复业务状态

以下是 JavaScript 反例：

```javascript
function misleading() {
  try {
    throw new Error('write failed');
  } finally {
    return 'ok';
  }
}
```

按 ECMAScript 语义推演，函数返回 `'ok'`，先前异常被 finally 的 return 覆盖。若 finally 自己抛出另一异常，调用者面对的失败也会改变。清理代码因此要约定清理失败的报告方式，避免无意隐藏主要失败。规则见 [ECMAScript try](https://tc39.es/ecma262/multipage/ecmascript-language-statements-and-declarations.html#sec-try-statement)；Python 3.13 的 [finally 规则](https://docs.python.org/3.13/reference/compound_stmts.html#finally-clause)也有相应覆盖行为，具体语言仍应分别查阅。

关闭文件、释放锁与撤销数据库写入不是同一动作。示意时间线 `更新内存 → 远端付款成功 → 本地记录失败 → catch` 中，捕获失败只能处理当前控制流；远端付款不会倒流。需要按业务定义查询提交状态、补偿或幂等重试，继续见[重试预算](../reliability/timeouts-and-retry-budgets.md)与[幂等性](../api/idempotency.md)。

清理设计可以分别检查：资源是否最终释放；对象是否仍满足不变量；失败前状态能否保留。最后一项更强，不能仅凭 finally 推出。[进程](../../glossary/systems.md#systems.execution-units)强杀、断电或 Runtime 致命退出也不承诺运行语言级清理，恢复需要持久记录与下次启动流程。

## 异步失败沿完成关系传播

下面假定 `failLater()` 是 JavaScript async 函数，并返回一个最终 rejected 的 Promise：

```javascript
async function observe() {
  try {
    await failLater();
  } catch (error) {
    // 这里接收所等待 Promise 的拒绝。
  }
}

function detached() {
  try {
    failLater();
  } catch (error) {
    // 这里不会接收稍后的拒绝。
  }
}
```

await 把被等待 Promise 的拒绝恢复为此异步执行上下文中的抛出，因而进入对应 catch。detached 只取得 Promise，没有等待或挂失败处理；稍后失败不在原同步 try 的控制流内。普通函数如果在返回 Promise 之前同步 throw，则又是另一条路径。机制见 [ECMAScript Await](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-await)。

定时回调稍后直接 throw，也不会被注册定时器时的外层 try 接住；应在实际回调或它所连接的异步完成边界处理。逻辑调用链可由异步堆栈帮助展示，但不是一条始终存活的原生[调用栈](../../glossary/systems.md#systems.memory-layout)。未处理拒绝怎样报告或终止属于宿主与配置规则，本文不指定统一策略。

## 取消是协议，清理也可能等待

Python 3.13 asyncio 在任务的下一次可用机会注入 `CancelledError`，它直接继承 BaseException；`except Exception` 通常不会捕获它。完成清理后一般继续传播取消。TaskGroup 等结构会等待所属任务结束并汇总相关异常，具体特殊异常与取消规则见[官方任务文档](https://docs.python.org/3.13/library/asyncio-task.html#task-cancellation)。

自选时间线：t=0 请求取消，t=5 任务抵达可取消等待点，t=5–8 完成清理，t=8 调用方观测任务取消。请求到注入经过 5 个时间单位，清理再用 3 个，请求到观测终态合计 8 个；若任务不让出执行或清理卡住，这个结束时间没有相同上界。取消也不证明已提交的远端操作已停止，系统级信号与退出继续见[信号、取消与退出](../systems/signals-cancellation-and-shutdown.md)。

请求入口应负责响应与关联记录，资源所有者负责释放，任务所有者负责等待和终态观测；在各层只记录自己能说明的范围，避免多层重复日志或把失败改成默认成功。跨原生边界还要约定异常能否展开，见[跨语言调用](ffi-abi-ownership-and-runtime-boundaries.md)。

## 自检

1. 同步异常向外传播时，失败点后面的语句与清理代码分别怎样处理？
2. misleading 为什么返回 ok；finally 再抛错会怎样影响原失败？
3. observe 与 detached 为什么接收失败的能力不同？
4. 取消时间线中哪一步代表任务终态，为什么请求取消不等于远端回滚？
5. 捕获之后要分别检查哪些资源、对象不变量和外部业务状态？

## 来源与核查

- [Python 3.13 错误与异常](https://docs.python.org/3.13/tutorial/errors.html)、[try/finally](https://docs.python.org/3.13/reference/compound_stmts.html#the-try-statement)，2026-10-23 核查；覆盖传播、原因链和清理覆盖。
- [ECMAScript try](https://tc39.es/ecma262/multipage/ecmascript-language-statements-and-declarations.html#sec-try-statement)、[Await](https://tc39.es/ecma262/multipage/control-abstraction-objects.html#sec-await)，2026-10-23 滚动草案核查；只引用已说明的完成与等待机制，不据此宣称全部宿主实现相同。
- [Python 3.13 asyncio 任务与取消](https://docs.python.org/3.13/library/asyncio-task.html)，2026-10-23 核查；覆盖取消异常、清理和任务组范围。

本文为 source-checked 概念说明。没有执行异常注入、Promise 拒绝、任务取消、进程强杀、跨语言展开或业务补偿实验。
