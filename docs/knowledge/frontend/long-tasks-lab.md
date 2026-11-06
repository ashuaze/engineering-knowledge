---
id: "kb-frontend-long-tasks-lab"
title: "实验：比较长任务、微任务与真正让出"
kind: "lab"
domain: "frontend"
status: "evolving"
summary: "以五种调度方式完成相同计算，记录 15 组长任务、输入等待和浏览器时间线。"
created: "2026-10-19"
updated: "2026-10-26"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-frontend-long-tasks", "kb-runtime-async-blocking"]
related: ["kb-frontend-long-tasks", "kb-runtime-event-loop", "kb-frontend-rendering-hydration"]
tags: ["browser", "scheduling", "testing"]
---

# 实验：比较长任务、微任务与真正让出

## 要验证什么

把计算函数写成 [async](../../glossary/runtime.md#runtime.async)，或者不断 `await Promise.resolve()`，页面就能及时处理输入吗？本实验让五种实现完成相同算术工作，比较[长任务](../../glossary/frontend.md#frontend.long-tasks)、输入处理等待、定时器与 requestAnimationFrame 回调获得执行机会的时刻。机制先读[浏览器长任务](long-tasks-and-responsiveness.md)与[事件循环](../runtime/event-loop-and-microtasks.md)。

本次采集的是自动注入 pointerdown 到其处理函数开始的等待，**不是 [INP](../../glossary/frontend.md#frontend.web-vitals)**。它没有包含真实人群交互、完整交互处理与最终呈现[延迟](../../glossary/performance.md#performance.latency-throughput)，也没有测试 [SSR](../../glossary/frontend.md#frontend.rendering-strategies)、[Hydration](../../glossary/frontend.md#frontend.hydration)、Worker 或移动设备。

## 环境与复现

2026-10-19 实际环境：Windows x64、8 个逻辑 CPU、Chrome **155.0.8059.40**、Node.js **24.16.0**、Playwright **1.62.1**。浏览器以 headless 模式运行，1100 × 850 视口，没有配置 CPU 降速；Long Tasks 与 scheduler.yield 能力检测均通过。源码与记录摘要见[证据清单](../../../examples/browser_long_tasks/results/manifest.json)。

从仓库根目录安装锁定依赖并准备 Chromium：

```bash
npm ci
npx playwright install chromium
npm run lab:browser
```

已有 Chrome 可传入实际路径，替代上面的浏览器下载与默认运行命令。本次使用：

```powershell
npm run lab:browser -- --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe" --runs 3
```

运行器启动仅监听回环地址的临时页面服务，执行后关闭浏览器与服务。默认在 `.cache/browser-long-tasks/` 保存结果、每次的时间线和页面截图；`--output` 可换目录。需要手动观察时，用目标浏览器打开[实验页面源码](../../../examples/browser_long_tasks/lab.html)对应的本地 HTML 文件，选一种模式点击开始，再在计算期间点击探针按钮。

实现见[自动运行器](../../../examples/browser_long_tasks/run.mjs)。不支持 scheduler.yield 时跳过该原生模式，仍执行定时器回退对照；缺少 Long Tasks 观测能力时运行器明确报错，不能把“不支持”当成“没有长任务”。

## 相同工作与测量方法

先用三次短计算校准一次，本次固定为 80 个 job、每个 1,481,481 次整数运算；随后所有模式复用同样参数和总运算顺序。每轮调整模式先后次序，共 3 轮、15 次。8 ms 是每个 job 完成后的检查阈值，无法抢占正在执行的 job。

| 模式 | 工作安排 |
| --- | --- |
| sync | 一个同步循环执行全部 job |
| [microtask](../../glossary/runtime.md#runtime.microtasks) | 每个 job 后 await 已完成的 Promise |
| yield | 累计到检查阈值后 await scheduler.yield() |
| timer | 累计到检查阈值后 await setTimeout(0) 包装的 Promise |
| heavy | 把同样的总工作合并成一个不可拆 job，再检查阈值 |

真实浏览器按钮事件启动计算；运行器收到“已开始”信号约 40 ms 后，通过浏览器协议向探针坐标注入鼠标按下。使用直接坐标注入，避免自动化操作的可点击检查等到主[线程](../../glossary/systems.md#systems.execution-units)空闲后才发送输入。每次都检查恰好记录一次输入、事件为 trusted、时间差非负；trusted 仍不表示输入来自真实用户。

处理函数记录 `performance.now() - event.timeStamp`。该时间差受事件时间戳精度和自动化环境影响，只用于当前对照。RAF 回调另存回调实际执行时的 performance.now()，不用 RAF 参数时间戳判断“是否在计算期间运行”；后者是帧时间口径，不能替代回调执行时刻。相关口径见 [Event.timeStamp](https://developer.mozilla.org/en-US/docs/Web/API/Event/timeStamp) 与 [requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)。

## 本次实际结果

下表是每种模式 3 次记录的中位数；“期间”指计算开始到完成之间。完整单次数据见[原始 JSON](../../../examples/browser_long_tasks/results/results.json)，不丢弃较慢样本。

| 模式 | 完成时间中位数（ms） | pointerdown 等待中位数（ms） | 各次长任务数 | 输入 / RAF / 零时延定时器在计算期间运行 |
| --- | --- | --- | --- | --- |
| sync | 636.9 | 593.2 | 1 / 1 / 1 | 否 / 否 / 否 |
| microtask | 594.6 | 527.0 | 1 / 1 / 1 | 否 / 否 / 否 |
| yield | 691.8 | 5.0 | 0 / 0 / 0 | 是 / 是 / 否 |
| timer | 1101.7 | 10.5 | 0 / 0 / 0 | 是 / 是 / 是 |
| heavy | 540.3 | 481.8 | 1 / 1 / 1 | 否 / 否 / 否 |

15 次 checksum 均为 1228158337。同步、微任务链与单个重 job 各次都被 Long Tasks API 记录为至少 50 ms 的长任务，输入在工作结束后才处理。两种真正让出的模式在本次记录中允许输入及 RAF 回调穿插；代价是总完成时间增加，定时器回退尤其明显。

原生 yield 模式的零时延定时器仍等到工作结束。这与“让出后任何[排队](../../glossary/performance.md#performance.queueing)任务都会立即运行”不同：不同任务及续执行的调度优先级会影响顺序。应分别记录输入、RAF 与定时器，不能只用其中一个推断所有工作都得到公平调度。[scheduler.yield 文档](https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/yield)说明了续执行的优先级语义。

第三次 microtask 完成时间为 1819.1 ms，明显高于另外两次。样本和机器负载不足以归因；这里保留它并使用中位数描述本次记录，不由此宣称某个模式稳定快几倍。未观察到 ≥50 ms 长任务也不等于每帧流畅，RAF 回调获得机会不等于像素已经呈现到屏幕。

## 断言与时间线

运行器 6 组汇总检查均通过：业务校验和一致；同步/微任务/重 job 的定时器延后；timer 回退允许其他任务；单个重 job 超过 8 ms；[阻塞](../../glossary/systems.md#systems.blocking)模式产生长任务；页面无脚本错误。输入是否穿插、RAF 时机、各模式毫秒值与无长任务数属于本次观察，没有设成通用性能门槛。

每次保存包含脚本、事件、样式/布局与 [Paint](../../glossary/frontend.md#frontend.render-pipeline) 事件的 Chrome 时间线，可在 DevTools Performance 中导入对应 JSON。事件存在不代表已经定位某个业务瓶颈，也不等于已经测量完整呈现延迟。

| 模式 | 第一轮 | 第二轮 | 第三轮 |
| --- | --- | --- | --- |
| sync | [记录 1](../../../examples/browser_long_tasks/results/1-sync.trace.json) | [记录 2](../../../examples/browser_long_tasks/results/2-sync.trace.json) | [记录 3](../../../examples/browser_long_tasks/results/3-sync.trace.json) |
| microtask | [记录 1](../../../examples/browser_long_tasks/results/1-microtask.trace.json) | [记录 2](../../../examples/browser_long_tasks/results/2-microtask.trace.json) | [记录 3](../../../examples/browser_long_tasks/results/3-microtask.trace.json) |
| yield | [记录 1](../../../examples/browser_long_tasks/results/1-yield.trace.json) | [记录 2](../../../examples/browser_long_tasks/results/2-yield.trace.json) | [记录 3](../../../examples/browser_long_tasks/results/3-yield.trace.json) |
| timer | [记录 1](../../../examples/browser_long_tasks/results/1-timer.trace.json) | [记录 2](../../../examples/browser_long_tasks/results/2-timer.trace.json) | [记录 3](../../../examples/browser_long_tasks/results/3-timer.trace.json) |
| heavy | [记录 1](../../../examples/browser_long_tasks/results/1-heavy.trace.json) | [记录 2](../../../examples/browser_long_tasks/results/2-heavy.trace.json) | [记录 3](../../../examples/browser_long_tasks/results/3-heavy.trace.json) |

## 自检与后续边界

为什么微任务模式有很多 await，仍没有让输入穿插？为何 heavy 模式配置了 8 ms，却出现数百毫秒的 job？如果某个浏览器不支持 scheduler.yield，应该重新测回退路径的哪些成本？

下一步可换真实业务 job、目标设备与可见窗口，测完整交互到呈现，再比较 Worker 和框架初始化。当前证据只支持这个合成页面与所记录版本，不把 headless 自动输入结果外推为真实用户 INP 改善。

来源核查日期：2026-10-19。

- [MDN：PerformanceLongTaskTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceLongTaskTiming)
- [MDN：Scheduler.yield](https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/yield)
- [web.dev：Optimize long tasks](https://web.dev/articles/optimize-long-tasks)
- [Playwright：CDPSession](https://playwright.dev/docs/api/class-cdpsession)
- [渲染与 Hydration](rendering-and-hydration.md)：显示、绑定与呈现属于不同阶段，本实验没有框架接管过程。
