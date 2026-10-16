<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 编程语言与 Runtime

建议优先级：P0。目标：解释语言抽象如何映射到任务、内存与错误。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么给 CPU 密集函数加 async 后仍会阻塞？

## 已有正文

- [同步、异步与阻塞：先说清观察边界](async-and-blocking.md)：分清结果交付、线程等待和 CPU 工作，解释为什么 async 仍可能阻塞。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Compiler / Interpreter / JIT | 编译、解释与运行期间的编译优化。 |
| Runtime / VM | 执行语言所需的调度、内存和宿主能力。 |
| Event Loop | 协调任务、I/O 完成事件和回调执行。 |
| Sync / Async / Promise / Async-Await | 调用结果的交付与异步控制流。 |
| Task / Microtask | 宿主调度任务和微任务，具体规则依 Runtime 而异。 |
| Closure / Scope | 词法作用域和对外部绑定的访问。 |
| GC / Reference Counting | 自动内存回收策略及其代价。 |
| Type System / Type Inference | 类型约束和自动类型推导。 |
| Generics / Structural Typing | 参数化类型与按结构兼容的类型关系。 |
| Serialization / Deserialization | 在运行时对象和交换格式间转换。 |
| Exception / Error Propagation | 失败信号、传播边界与资源清理。 |
| Module System / Dependency | 模块加载、依赖解析和初始化。 |
| FFI / WebAssembly | 语言边界调用与可移植字节码执行。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
