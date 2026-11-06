<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 编程语言与 Runtime词汇表

本页解释 14 组术语，按[完整术语索引](../glossary.md#runtime)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [编程语言与 Runtime文章](../knowledge/runtime/index.md)

## 本页术语

- [Compiler / Interpreter / JIT](#runtime.compilation)
- [Runtime / VM](#runtime.virtual-machine)
- [Event Loop](#runtime.event-loop)
- [Sync / Async / Promise / Async-Await](#runtime.async)
- [Task / Microtask](#runtime.microtasks)
- [Closure / Scope](#runtime.closure)
- [GC / Reference Counting](#runtime.gc)
- [Type System / Type Inference](#runtime.type-system)
- [Generics / Structural Typing](#runtime.generics)
- [Serialization / Deserialization](#runtime.serialization)
- [Exception / Error Propagation](#runtime.errors)
- [Module System / Dependency](#runtime.modules)
- [FFI / WebAssembly](#runtime.ffi-wasm)
- [Reachability / Retention](#runtime.reachability)

<a id="runtime.compilation"></a>

## Compiler / Interpreter / JIT

**ID：** `runtime.compilation` · **建议优先级：** P0

**别名 / 检索词：** Compiler、Interpreter、JIT、编译器、解释器、即时编译

**简释：** 程序表示转换、解释执行与运行期间编译。

编译器转换程序表示，解释器执行程序表示；AOT/JIT 区分目标运行前与运行中编译，不等同是否优化。分层实现可利用反馈、守卫和状态映射退优化，同一语言可有多种执行策略。

**例子：** 虚拟机先解释执行，再对热点函数编译并在假设失效时回退。

**深入阅读：** [编译、解释与 JIT：程序怎样执行，优化假设失效后怎样继续](../knowledge/runtime/compilation-interpretation-jit-and-deoptimization.md)

<a id="runtime.virtual-machine"></a>

## Runtime / VM

**ID：** `runtime.virtual-machine` · **建议优先级：** P0

**别名 / 检索词：** Runtime、VM、运行时、虚拟机

**简释：** 执行语言所需的调度、内存和宿主能力。

运行时提供执行程序所需的内存、调度、异常和宿主接口等能力；语言 VM 执行特定中间表示。这里的 VM 与运行完整客体操作系统的系统虚拟机不同。

**例子：** 同一段字节码依赖 VM 的对象模型和宿主接口才能运行。

**深入阅读：** [语言虚拟机与宿主：字节码怎样执行，可移植与隔离各到哪里](../knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md)

<a id="runtime.event-loop"></a>

## Event Loop

**ID：** `runtime.event-loop` · **建议优先级：** P0

**别名 / 检索词：** Event Loop、事件循环

**简释：** 协调任务、I/O 完成事件和回调执行。

事件循环根据宿主规则选取任务并推进回调、I/O 及相关队列。单线程回调若长时间执行，会推迟其他任务；事件循环本身不让计算自动并行。

**例子：** 回调连续计算一秒，期间已到达的网络事件也可能等待处理。

**深入阅读：** [同步、异步与阻塞：先说清观察边界](../knowledge/runtime/async-and-blocking.md) · [浏览器长任务：页面已显示为何仍点不动](../knowledge/frontend/long-tasks-and-responsiveness.md) · [事件循环与微任务：回调为什么还没有执行](../knowledge/runtime/event-loop-and-microtasks.md)

<a id="runtime.async"></a>

## Sync / Async / Promise / Async-Await

**ID：** `runtime.async` · **建议优先级：** P0

**别名 / 检索词：** Sync、Async、Promise、Async-Await、同步、异步

**简释：** 调用结果的交付与异步控制流。

同步调用在返回前交付约定结果；异步调用通过稍后的完成信号交付结果。Promise 表示完成状态，async/await 组织控制流，不保证计算或底层调用不会阻塞。

**例子：** await 网络请求可让出执行机会，await 之前的大循环仍会占用线程。

**深入阅读：** [同步、异步与阻塞：先说清观察边界](../knowledge/runtime/async-and-blocking.md) · [事件循环与微任务：回调为什么还没有执行](../knowledge/runtime/event-loop-and-microtasks.md)

<a id="runtime.microtasks"></a>

## Task / Microtask

**ID：** `runtime.microtasks` · **建议优先级：** P0

**别名 / 检索词：** Task、Microtask、微任务

**简释：** 宿主调度任务和微任务，具体规则依 Runtime 而异。

Task 与 Microtask 是宿主定义的调度单元；浏览器会在规定检查点排空微任务队列。递归追加微任务可推迟后续任务和渲染，其他运行时规则需单独核对。

**例子：** 反复链式执行 Promise 回调并不能保证浏览器获得绘制机会。

**深入阅读：** [事件循环与微任务：回调为什么还没有执行](../knowledge/runtime/event-loop-and-microtasks.md)

<a id="runtime.closure"></a>

## Closure / Scope

**ID：** `runtime.closure` · **建议优先级：** P0

**别名 / 检索词：** Closure、Scope、闭包、作用域

**简释：** 词法作用域和对外部绑定的访问。

闭包让函数继续访问定义位置的词法绑定；捕获绑定不一定是复制当时的值。外部引用还可能延长相关对象生命周期。

**例子：** 循环中注册回调时，要分清多个回调共享一个绑定还是各自持有独立绑定。

**深入阅读：** [可达性与垃圾回收：对象不用了，内存为什么还在增长](../knowledge/runtime/reachability-and-garbage-collection.md) · [闭包与词法绑定：回调为什么读到旧值](../knowledge/runtime/closures-and-lexical-bindings.md)

<a id="runtime.gc"></a>

## GC / Reference Counting

**ID：** `runtime.gc` · **建议优先级：** P0

**别名 / 检索词：** GC、Reference Counting、垃圾回收、引用计数

**简释：** 自动内存回收策略及其代价。

垃圾回收按运行时规则回收不可继续使用的内存；追踪式回收通常基于可达性，引用计数基于引用数量。循环、暂停和资源终结行为取决于具体实现。

**例子：** 对象仍被全局集合引用时，即使业务不再需要，也通常不会被回收。

**深入阅读：** [可达性与垃圾回收：对象不用了，内存为什么还在增长](../knowledge/runtime/reachability-and-garbage-collection.md)

<a id="runtime.type-system"></a>

## Type System / Type Inference

**ID：** `runtime.type-system` · **建议优先级：** P0

**别名 / 检索词：** Type System、Type Inference、Type Assertion、Type Guard、unknown、any、类型断言、运行时校验、类型系统、类型推导

**简释：** 类型约束和自动类型推导。

类型系统表达并检查程序约束，类型推导从上下文确定类型。编译期通过不证明网络输入满足约定；类型断言通常也不执行运行时验证。

**例子：** 把 JSON 断言为订单类型前，仍应检查必填字段、取值和业务条件。

**深入阅读：** [类型系统与运行时校验：类型检查通过为什么仍会出错](../knowledge/runtime/type-systems-and-runtime-validation.md)

<a id="runtime.generics"></a>

## Generics / Structural Typing

**ID：** `runtime.generics` · **建议优先级：** P0

**别名 / 检索词：** Generics、Structural Typing、泛型、结构类型

**简释：** 参数化类型与按结构兼容的类型关系。

泛型用类型参数复用算法和容器，结构类型按成员结构判断兼容性。泛型约束表达可用操作，不意味着运行时保留全部类型信息或自动验证输入。

**例子：** 接收带 id 成员的对象，可以无需共享继承父类；外部数据仍需校验。

**深入阅读：** [类型系统与运行时校验：类型检查通过为什么仍会出错](../knowledge/runtime/type-systems-and-runtime-validation.md)

<a id="runtime.serialization"></a>

## Serialization / Deserialization

**ID：** `runtime.serialization` · **建议优先级：** P0

**别名 / 检索词：** Serialization、Deserialization、序列化、反序列化

**简释：** 在运行时对象和交换格式间转换。

序列化把对象或状态编码成可传输表示，反序列化重建约定结构。格式需处理版本、数值范围、身份与循环引用；不可信数据不应触发任意代码构造。

**例子：** 日期经 JSON 变成字符串后，需要明确时区与解析规则才能还原语义。

**深入阅读：** [序列化与反序列化：怎样保留数值、类型、身份与版本语义](../knowledge/runtime/serialization-representations-schemas-and-identity.md)

<a id="runtime.errors"></a>

## Exception / Error Propagation

**ID：** `runtime.errors` · **建议优先级：** P0

**别名 / 检索词：** Exception、Error Propagation、异常、错误传播

**简释：** 失败信号、传播边界与资源清理。

异常或错误返回值把失败传到有能力处理的边界。传播时要保存原因并执行资源清理，重试前还需判断副作用是否已发生。

**例子：** 捕获写入超时后，先查询提交状态，不能把所有错误都视作未执行。

**深入阅读：** [异常传播与资源清理：失败怎样跨调用栈和异步边界](../knowledge/runtime/exceptions-unwinding-cleanup-and-async-boundaries.md)

<a id="runtime.modules"></a>

## Module System / Dependency

**ID：** `runtime.modules` · **建议优先级：** P0

**别名 / 检索词：** Module System、Dependency、ESM、CommonJS、Live Binding、Circular Dependency、活绑定、循环依赖、模块系统

**简释：** 模块加载、依赖解析和初始化。

模块系统定义名称导出、依赖解析和初始化。ESM 的实时绑定与 CommonJS 的导出行为不同；循环依赖可能暴露尚未初始化或尚未完成的状态。

**例子：** A 初始化时读取 B，而 B 又提前读取 A 的导出，可能遇到初始化顺序问题。

**深入阅读：** [模块系统与循环依赖：找到模块为什么仍读不到值](../knowledge/runtime/modules-bindings-and-circular-dependencies.md)

<a id="runtime.ffi-wasm"></a>

## FFI / WebAssembly

**ID：** `runtime.ffi-wasm` · **建议优先级：** P0

**别名 / 检索词：** FFI、WebAssembly、外部函数接口

**简释：** 语言边界调用与可移植字节码执行。

FFI 连接不同语言的调用约定和数据表示；WebAssembly 定义可移植执行格式及受约束的宿主交互。跨边界仍需处理内存所有权、错误和权限。

**例子：** 把字符串传给原生库时，必须约定编码、长度以及由谁释放缓冲区。

**深入阅读：** [跨语言调用与 FFI：ABI、内存归属和错误怎样越过边界](../knowledge/runtime/ffi-abi-ownership-and-runtime-boundaries.md) · [语言虚拟机与宿主：字节码怎样执行，可移植与隔离各到哪里](../knowledge/runtime/virtual-machines-bytecode-hosts-and-isolation.md)

<a id="runtime.reachability"></a>

## Reachability / Retention

**ID：** `runtime.reachability` · **建议优先级：** P1

**别名 / 检索词：** Reachability、Retention、可达性、引用持有

**简释：** 从根沿引用路径能否到达对象，以及哪些持有关系延长其生命周期。

可达性表示从根沿引用能否到达对象；保留关系解释哪个所有者延长其生命。内存高不必然是回收器故障，常需追查仍存活的引用路径。

**例子：** 未移除的事件监听器经闭包持有大对象，导致页面离开后仍不能回收。

**深入阅读：** [可达性与垃圾回收：对象不用了，内存为什么还在增长](../knowledge/runtime/reachability-and-garbage-collection.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [MDN：JavaScript 语言机制](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
