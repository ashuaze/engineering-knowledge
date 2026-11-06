---
id: "kb-runtime-compilation-jit"
title: "编译、解释与 JIT：程序怎样执行，优化假设失效后怎样继续"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "区分程序表示、编译时机与执行策略，解释分层编译、反馈、守卫和退优化，以及启动与稳态性能的不同成本。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-runtime-types-validation"]
related: ["kb-runtime-virtual-machines", "kb-runtime-modules-cycles", "kb-performance-benchmarking", "kb-performance-profiling", "kb-frontend-bundling-splitting"]
tags: ["compiler", "interpreter", "jit", "deoptimization"]
---

# 编译、解释与 JIT：程序怎样执行，优化假设失效后怎样继续

学习入口：同一函数重复调用后变快，换一种输入又变慢，是语言规则变了吗？前置：函数、类型与基本性能计量。本文区分执行机制与语言语义，以 V8 的历史设计资料、CPython 3.13 和 Clang 文档为例；层级名称不视作所有版本的固定管线，代码与成本均为纸面推演。

## 先问转换到什么，再问什么时候转换

编译把一种程序表示转换成另一种表示；[解释器](../../glossary/runtime.md#runtime.compilation)读取某种表示并执行其操作。编译的目标可以是字节码、中间表示、另一种源码或机器码，不要求直接生成可执行文件。解释也不要求每次重新逐行读取源码。

| 机制 | 主要动作 | 不能由名称推出 |
| --- | --- | --- |
| 编译器 | 解析、检查并转换程序表示，可能进行优化 | 必然产生机器码，或所有错误都能提前发现 |
| 解释器 | 按表示中的指令推进计算和控制流 | 从不编译，或每条指令都对应一行源码 |
| AOT，提前编译 | 在目标运行之前完成相应编译工作 | 不需要动态库、内存管理或宿主能力 |
| JIT，即时编译 | 在运行期间把部分程序编译成可执行代码 | 必然先解释、必然优化，或所有代码都会被编译 |

这些维度可以组合：源码先编译成字节码，再由解释器执行；运行中也可以把字节码编译成机器码。CPython 的 [dis 文档](https://docs.python.org/3.13/library/dis.html)明确把字节码列为实现细节，不能将某版 opcode 当成所有 Python 实现的规范。

[Clang 命令指南](https://clang.llvm.org/docs/CommandGuide/clang.html)把预处理、语法与语义分析、代码生成、汇编、链接区分为阶段。目标文件生成成功与最终符号链接成功是两件事；某个符号只能在程序执行期间加载时找到，也不等于编译器“没有做类型检查”。模块的查找、链接和求值继续见[模块系统](modules-bindings-and-circular-dependencies.md)。

## 分层执行用启动成本换取后续收益

解释器便于尽快开始执行，代价可能包括指令分派和通用值处理；快速基线编译器可以较少分析地生成机器码；优化编译器则花更多时间分析与特化。不同实现会选择不同组合。

V8 的 [Ignition](https://v8.dev/docs/ignition)是字节码解释器；2021 年 [Sparkplug 说明](https://v8.dev/blog/sparkplug)展示从字节码快速生成机器码的基线层；2023 年 [Maglev 说明](https://v8.dev/blog/maglev)展示介于快速基线与高优化层之间的取舍。这里引用的是各篇设计的机制，不宣称当前浏览器都按同一阈值经过全部层级。

JIT 不是“优化”的同义词。Sparkplug 是运行中编译，却明确减少复杂优化；解释器也可自适应地使用专门指令。AOT 同样可以优化，也可以使用此前采集的反馈。执行策略应按具体实现、构建选项和工作负载判断。

## 反馈、守卫与退优化必须一起理解

下面是 JavaScript 教学片段，只讨论普通数值或字符串，没有 getter 等副作用：

```javascript
function addOne(value) {
  return value + 1;
}
// addOne(7) 的语义结果为 8；addOne('7') 的语义结果为 '71'。
```

假设一类优化根据此前输入选择整数加法，它必须在所需位置确认类型、溢出等前提，或依赖可失效的动态事实。收到字符串不能继续把它当整数处理。实现可以选择通用慢路径、使专门代码失效，或退优化；此例不预测某个 V8 版本一定在第几次调用触发哪种行为。

退优化把优化后的执行状态映射到能够继续按原语言语义运行的状态。Maglev 资料说明其通过保存的帧状态映射重建未优化状态。优化中可能内联函数、移除中间对象，因此恢复不是只改一个函数指针，更不能随便从函数开头重跑已经发生的写入。

守卫失败本身通常是执行策略调整；语言要求抛出的[异常](../../glossary/runtime.md#runtime.errors)仍应抛出。把退优化、业务错误和[进程](../../glossary/systems.md#systems.execution-units)崩溃混为一谈，会误判性能记录。实现若无法维持语义则属于实现缺陷，不能用“动态语言”解释错误结果。

## 用完整成本判断优化是否值得

自选成本模型：基线路径每次 10 微秒，优化路径每次 2 微秒，新增编译成本 8 毫秒，忽略其他差异。节省每次 8 微秒，第 1000 次恰好抵消 8000 微秒编译成本，超过后才净受益。执行 200 次只节省执行时间 1.6 毫秒，扣编译后反而多花 6.4 毫秒；执行 2000 次节省执行时间 16 毫秒，扣编译后净省 8 毫秒。这不是实测，也没计入守卫、采样、退优化、代码缓存和内存压力。

真实工作可能主要等待 I/O，或在服务启动后很快退出。测量应同时保留冷启动、预热过程、稳态、输入分布、[尾延迟](../../glossary/performance.md#performance.percentiles)和 CPU/内存成本，并记录引擎版本、优化开关和采样范围。不要只挑热循环，也不要先改变业务语义来追求稳定类型。方法见[基准测试](../performance/benchmarks-workloads-and-speedup.md)与[Profiling](../performance/profiling-stacks-and-flame-graphs.md)。

## 自检

1. 程序先变成字节码再解释，为什么仍包含编译阶段？
2. AOT/JIT 与是否优化分别描述什么，为什么不能按语言名字二选一？
3. 只观察到数值输入能否允许 addOne 永远忽略字符串语义？
4. 退优化为什么需要状态映射，为什么不能任意重放外部写入？
5. 在本文成本模型中，200 与 2000 次调用各省多少，结论还缺什么实际证据？

## 来源与核查

- [Clang 命令指南](https://clang.llvm.org/docs/CommandGuide/clang.html)，2026-10-23 核查滚动文档；覆盖编译驱动阶段与输出。
- [CPython 3.13 dis](https://docs.python.org/3.13/library/dis.html)，2026-10-23 核查；覆盖字节码的实现属性与自适应表示。
- [V8 Ignition](https://v8.dev/docs/ignition)、[Sparkplug（2021）](https://v8.dev/blog/sparkplug)、[Maglev（2023）](https://v8.dev/blog/maglev)，2026-10-23 核查；覆盖解释、基线编译、反馈、守卫及退优化，不引用其跑分作为本文结果。

本文为 source-checked 概念说明。没有执行编译器、反汇编、优化跟踪、退优化触发或性能对照；站点构建不验证这些机制。
