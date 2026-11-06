---
id: "kb-runtime-virtual-machines"
title: "语言虚拟机与宿主：字节码怎样执行，可移植与隔离各到哪里"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "区分语言虚拟机、引擎、运行时与宿主，沿 JVM 和 Wasm 说明验证、装载、执行状态和能力边界，区分格式可移植与完整应用兼容。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-runtime-compilation-jit", "kb-runtime-modules-cycles"]
related: ["kb-runtime-ffi-boundaries", "kb-runtime-exception-propagation", "kb-runtime-gc", "kb-devops-container-boundaries", "kb-runtime-types-validation"]
tags: ["vm", "bytecode", "jvm", "webassembly", "host"]
---

# 语言虚拟机与宿主：字节码怎样执行，可移植与隔离各到哪里

学习入口：同一份字节码为什么换环境仍可能运行失败；放进 [VM](../../glossary/runtime.md#runtime.virtual-machine) 后为什么也不能直接执行任意不可信插件？前置：[编译、解释与 JIT](compilation-interpretation-jit-and-deoptimization.md)、[模块系统](modules-bindings-and-circular-dependencies.md)。本文以 Java SE 25 JVM 规范、Wasm 核心和 Node.js 24.16.0 为参照，比较的是层次与责任，未启动虚拟机或沙箱实验。

## 语言 VM 定义执行模型，宿主提供环境

| 名称 | 本文使用范围 | 需要另行区分 |
| --- | --- | --- |
| 语言虚拟机 | 指令、类型、控制流和运行状态的抽象机器及实现 | 不一定模拟完整 CPU 或操作系统 |
| 引擎 | 实现语言执行的组件，可能含[解释器](../../glossary/runtime.md#runtime.compilation)/JIT/[GC](../../glossary/runtime.md#runtime.gc) | 不自动带全部浏览器或服务端 API |
| Runtime | 执行所需的库、内存、错误与调度等整体能力，产品用法会有差异 | 无统一“必须内置[事件循环](../../glossary/runtime.md#runtime.event-loop)”的定义 |
| 宿主 | 嵌入执行引擎、提供文件/网络/时间等交互接口的环境 | 权限、资源和调度策略要单独约定 |
| 系统虚拟机 | 为客体操作系统提供虚拟硬件环境 | 与语言 VM 的指令和隔离范围不同 |

V8 可以嵌入不同宿主；JavaScript 语义相同不意味着浏览器 [DOM](../../glossary/frontend.md#frontend.render-tree) 与 Node 文件 API 一样。语言 VM 也可以依靠解释、AOT、JIT 或其组合实现，使用 VM 不等于每次逐指令解释。容器与系统隔离继续见[镜像、容器与资源边界](../devops/images-containers-and-resource-isolation.md)。

## JVM 把格式、运行状态和阶段分别规定

[JVMS 25 第 2 章](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html)规定 class 文件、值类型、帧与运行时数据区等抽象，不指定唯一对象布局、GC 或机器码优化算法。教学方法 `sum(a,b)` 可在一帧中从局部变量取 3 和 4，操作数栈由空变成 `[3] → [3,4] → [7]`，再把结果交还调用者；这只是抽象状态，不表示真实寄存器和内存一定这样摆放。

JVM 每个[线程](../../glossary/systems.md#systems.execution-units)有自己的执行栈，堆在虚拟机线程间共享；局部变量位于帧中，不代表其引用的对象也属于线程私有。抽象操作数栈也不等于开发者经取地址操作得到的连续原生栈内存。对象持有、回收与进程内存继续见[GC 与可达性](reachability-and-garbage-collection.md)。

[JVMS 第 5 章](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html)区分装载、链接和初始化：找到字节表示之后，还要验证、准备及解析相应符号，初始化又可能执行代码并失败。阶段可以按规范允许的方式延后或组合，不能把“文件已读入”当作全部符号和初始化都成功。

相同二进制类名配不同定义类加载器可形成不同运行时类型身份，插件交接时只比类名字符串不够。格式版本、依赖库、模块可见性及本地库也影响运行结果；可移植的是约定层，不是整个应用的所有环境假设。

## Wasm 模块、实例与线性内存分别持有身份

Wasm 核心定义虚拟指令与二进制格式、验证和执行；与具体环境交互由嵌入 API 定义。相关范围见[核心引言](https://webassembly.github.io/spec/core/intro/introduction.html)与[运行结构](https://webassembly.github.io/spec/core/exec/runtime.html)。模块是代码与声明，实例把其导入/导出关联到具体函数、内存等状态。

同一模块实例化两次，可以得到独立内存；若宿主给两者导入同一个内存对象，则可能共享状态。因此“两个实例”本身不证明内存独立。实例 A 中 offset=100 的含义依赖其关联内存，不能直接当成 B 的同一对象，更不能当成任意原生指针；细节见[FFI 与 Wasm 边界](ffi-abi-ownership-and-runtime-boundaries.md)。

验证检查模块是否符合相应类型与结构规则，不证明业务算法正确、一定终止或内存需求足够小。导入不匹配、越界 trap 与应用失败又属于不同阶段。Wasm 的类型和线性内存边界有明确价值，但模块内部的不安全源语言仍可能破坏同一线性内存里的相邻对象；依据见[验证约定](https://webassembly.github.io/spec/core/valid/conventions.html)与[安全模型](https://webassembly.org/docs/security/)。

## 安全取决于暴露能力与运行边界

自选插件接口 `read_config(handle)` 与 `open_any_path(path)`：前者可由宿主把 handle 限定到一份配置，后者若直接开放任意宿主路径，就扩张了可访问范围。模块本身不能凭空取得所有系统接口，但宿主导入可能把强能力交给它；需要沿每个导入检查输入、对象身份、权限、资源限额和退出。

同样，不同 Realm、上下文或全局对象并不必然构成安全沙箱。Node.js 24.16.0 的 [node:vm 文档](https://nodejs.org/download/release/v24.16.0/docs/api/vm.html)明确说明它不是安全机制。不能用方法名中带 VM，或能设置脚本超时，代替对[异步](../../glossary/runtime.md#runtime.async)任务、宿主函数与进程隔离的完整设计。

若资源或依赖超出某层控制范围，应扩大隔离与恢复设计，而不是从“字节码验证通过”推导文件、网络或 CPU 使用都已受限。实际方案还需确认实现版本、可用特性、宿主配置、原生扩展和升级兼容组合。

## 自检

1. 引擎、Runtime、宿主与系统虚拟机分别承担什么，为什么 V8 不自动提供 DOM？
2. sum 的操作数栈过程说明什么，为什么不能据此推断真实机器布局？
3. class 文件已经装载，为何仍可能在链接、初始化或类型身份上失败？
4. 两个 Wasm 实例什么时候共享内存，offset=100 为什么不自带跨实例身份？
5. 模块验证通过还缺哪些宿主权限、资源与业务正确性证据？

## 来源与核查

- [JVMS Java SE 25 第 2 章](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html)、[第 5 章](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html)，2026-10-23 核查固定规范；覆盖抽象机器、帧/数据区、装载/链接/初始化与类型身份。
- [Wasm 核心引言](https://webassembly.github.io/spec/core/intro/introduction.html)、[运行结构](https://webassembly.github.io/spec/core/exec/runtime.html)、[验证约定](https://webassembly.github.io/spec/core/valid/conventions.html)，2026-10-23 核查当日 3.0 草案；本文仅取核心层次与传统数值/内存例子，不宣称全部部署支持草案新增特性。
- [WebAssembly 安全模型](https://webassembly.org/docs/security/)，2026-10-23 核查；覆盖宿主交互与线性内存内部风险，页面的未来特性措辞不作为版本支持表。
- [Node.js 24.16.0 node:vm](https://nodejs.org/download/release/v24.16.0/docs/api/vm.html)，2026-10-23 核查固定版本；覆盖上下文用途与安全边界。

本文为 source-checked 概念说明。没有执行 JVM 装载/初始化、类加载器、Wasm 验证/实例/导入、沙箱逃逸、资源限额或宿主权限实验。
