<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 编程语言与 Runtime

建议优先级：P0。目标：解释语言抽象如何映射到任务、内存与错误。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么给 CPU 密集函数加 [async](../../glossary/runtime.md#runtime.async) 后仍会[阻塞](../../glossary/systems.md#systems.blocking)？

## 已有正文

- [同步、异步与阻塞：先说清观察边界](async-and-blocking.md)：分清结果交付、[线程](../../glossary/systems.md#systems.execution-units)等待和 CPU 工作，解释为什么 async 仍可能阻塞。
- [闭包与词法绑定：回调为什么读到旧值](closures-and-lexical-bindings.md)：沿定义位置、环境实例和读取时刻解释[闭包](../../glossary/runtime.md#runtime.closure)，区分共享绑定、提前计算的值与框架渲染快照。
- [编译、解释与 JIT：程序怎样执行，优化假设失效后怎样继续](compilation-interpretation-jit-and-deoptimization.md)：区分程序表示、编译时机与执行策略，解释分层编译、反馈、守卫和退优化，以及启动与稳态性能的不同成本。
- [事件循环与微任务：回调为什么还没有执行](event-loop-and-microtasks.md)：区分当前执行、任务、[微任务](../../glossary/runtime.md#runtime.microtasks)和渲染机会，解释 Promise 续体、定时器与宿主差异。
- [异常传播与资源清理：失败怎样跨调用栈和异步边界](exceptions-unwinding-cleanup-and-async-boundaries.md)：沿调用、清理与异步完成区分[异常](../../glossary/runtime.md#runtime.errors)传播，解释原因链、finally 覆盖、取消和状态恢复，以及捕获与业务回滚的边界。
- [跨语言调用与 FFI：ABI、内存归属和错误怎样越过边界](ffi-abi-ownership-and-runtime-boundaries.md)：沿调用约定、数据布局、所有权和线程解释 [FFI](../../glossary/runtime.md#runtime.ffi-wasm)，区分原生指针、[Runtime](../../glossary/runtime.md#runtime.virtual-machine) 句柄与 Wasm 内存偏移，以及异常与性能边界。
- [模块系统与循环依赖：找到模块为什么仍读不到值](modules-bindings-and-circular-dependencies.md)：区分模块解析、链接与求值，解释 [ESM](../../glossary/runtime.md#runtime.modules) 活绑定、初始化顺序、CommonJS 循环和模块身份的边界。
- [可达性与垃圾回收：对象不用了，内存为什么还在增长](reachability-and-garbage-collection.md)：用对象引用图解释 JavaScript 内存持有、[GC](../../glossary/runtime.md#runtime.gc) 与泄漏，区分 Node.js 堆、外部内存和 RSS 的诊断口径。
- [序列化与反序列化：怎样保留数值、类型、身份与版本语义](serialization-representations-schemas-and-identity.md)：区分对象、数据模型与字节表示，解释 JSON 数值、字段存在性、对象共享、格式演进和不可信输入的边界。
- [类型系统与运行时校验：类型检查通过为什么仍会出错](type-systems-and-runtime-validation.md)：以 TypeScript 区分静态约束、推导、结构兼容和运行时数据验证，解释 unknown、any、断言与[泛型](../../glossary/runtime.md#runtime.generics)的信任边界。
- [语言虚拟机与宿主：字节码怎样执行，可移植与隔离各到哪里](virtual-machines-bytecode-hosts-and-isolation.md)：区分语言虚拟机、引擎、运行时与宿主，沿 JVM 和 Wasm 说明验证、装载、执行状态和能力边界，区分格式可移植与完整应用兼容。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Compiler / Interpreter / JIT](../../glossary/runtime.md#runtime.compilation) | 程序表示转换、解释执行与运行期间编译。 |
| [Runtime / VM](../../glossary/runtime.md#runtime.virtual-machine) | 执行语言所需的调度、内存和宿主能力。 |
| [Event Loop](../../glossary/runtime.md#runtime.event-loop) | 协调任务、I/O 完成事件和回调执行。 |
| [Sync / Async / Promise / Async-Await](../../glossary/runtime.md#runtime.async) | 调用结果的交付与异步控制流。 |
| [Task / Microtask](../../glossary/runtime.md#runtime.microtasks) | 宿主调度任务和微任务，具体规则依 Runtime 而异。 |
| [Closure / Scope](../../glossary/runtime.md#runtime.closure) | 词法作用域和对外部绑定的访问。 |
| [GC / Reference Counting](../../glossary/runtime.md#runtime.gc) | 自动内存回收策略及其代价。 |
| [Type System / Type Inference](../../glossary/runtime.md#runtime.type-system) | 类型约束和自动类型推导。 |
| [Generics / Structural Typing](../../glossary/runtime.md#runtime.generics) | 参数化类型与按结构兼容的类型关系。 |
| [Serialization / Deserialization](../../glossary/runtime.md#runtime.serialization) | 在运行时对象和交换格式间转换。 |
| [Exception / Error Propagation](../../glossary/runtime.md#runtime.errors) | 失败信号、传播边界与资源清理。 |
| [Module System / Dependency](../../glossary/runtime.md#runtime.modules) | 模块加载、依赖解析和初始化。 |
| [FFI / WebAssembly](../../glossary/runtime.md#runtime.ffi-wasm) | 语言边界调用与可移植字节码执行。 |
| [Reachability / Retention](../../glossary/runtime.md#runtime.reachability) | 从根沿引用路径能否到达对象，以及哪些持有关系延长其生命周期。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
