---
id: "kb-runtime-ffi-boundaries"
title: "跨语言调用与 FFI：ABI、内存归属和错误怎样越过边界"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "沿调用约定、数据布局、所有权和线程解释 FFI，区分原生指针、Runtime 句柄与 Wasm 内存偏移，以及异常与性能边界。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-runtime-types-validation", "kb-runtime-gc"]
related: ["kb-runtime-serialization", "kb-runtime-exception-propagation", "kb-runtime-virtual-machines", "kb-performance-benchmarking", "kb-systems-ipc"]
tags: ["ffi", "abi", "ownership", "webassembly"]
---

# 跨语言调用与 FFI：ABI、内存归属和错误怎样越过边界

学习入口：函数名与参数类型都对，为什么跨语言调用仍会崩溃，或在回调时读到已释放内存？前置：[类型校验](type-systems-and-runtime-validation.md)、[可达性与 GC](reachability-and-garbage-collection.md)。本文以 C 风格接口、Rust、Node.js 24.16.0 中的 Node-API 和 memory32 Wasm 为例；Node-API 自身有独立版本号。签名和时间线是教学契约，未编译或链接原生库。

## API 描述操作，ABI 约定二进制怎样配合

[FFI](../../glossary/runtime.md#runtime.ffi-wasm) 是外部函数接口，连接不同语言的调用和数据表示。ABI（应用二进制接口）涉及调用约定、参数/返回值传递、符号和数据布局等。两个库都声明一个整数参数，不证明位宽、符号、对齐、结构体布局和调用约定一致。

[Rust 类型布局参考](https://doc.rust-lang.org/reference/type-layout.html)区分默认布局与 C 表示；`repr(C)` 为相应类型采用 C 布局规则，不会把内部 String、Vec 或对象引用自动变成通用 C 数据。平台相关的 C ABI 也不是单一跨 CPU/操作系统协议。包装层应显式采用固定宽度字段、长度、编码和不透明句柄，并核对工具链与库版本。

跨[进程](../../glossary/systems.md#systems.execution-units) [RPC](../../glossary/api.md#api.styles) 可以连接不同语言，但需消息传输、编解码与独立故障处理；不能把一个进程的地址直接当成另一个进程的可用指针。与[IPC](../systems/ipc-channels-shared-memory-and-ownership.md)及[序列化](serialization-representations-schemas-and-identity.md)的边界应分别设计。

## 一个指针还缺长度、寿命与释放责任

以下为自选 C 风格[同步](../../glossary/runtime.md#runtime.async)契约，不是某个库的实现：

```c
int encode(const uint8_t *input, size_t input_len,
           uint8_t **output, size_t *output_len);
void free_output(uint8_t *output);
```

约定 input 仅在本次调用期间借用且不被保存；成功返回 0，并给出库分配的 output 与长度，调用者只能用同一库的 free_output 释放一次；失败返回非零，并将 output 设为空、长度设为零。零长度输入与空指针能否组合也必须明确。签名本身没有表达这些约束，包装器需要按契约检查并保证各分支清理。

| 资源 | 正常责任 | 失败反例 |
| --- | --- | --- |
| 借用输入 | 调用期间保持存活，按约定避免[并发](../../glossary/systems.md#systems.concurrency)修改 | 返回后原生库继续用已经释放的输入 |
| 拥有的输出 | 记录分配方、长度、释放函数 | 用另一套 allocator 释放，或重复释放 |
| 注册回调与上下文 | 保持引用，注销并等待在途回调结束 | 只删除本地对象，库仍在另一个线程回调 |
| [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 对象句柄 | 按宿主要求保留/释放引用 | 把临时句柄当作永久地址缓存 |

Rust 的 [FFI 指南](https://doc.rust-lang.org/nomicon/ffi.html)说明原始声明正确性与安全包装责任。原生指针非空不证明可访问；[GC](../../glossary/runtime.md#runtime.gc) 也不知道某个裸指针需要延长哪个对象寿命。跨边界应在复制、借用、转移之间明确选择，而非只追求“零拷贝”。

## 线程、回调和错误有各自的通道

Node-API 用不透明句柄表达 JavaScript 值，并提供句柄生存范围、持久引用和受控跨线程通知。后台工作不能任意操作 JS 对象，需按 API 的允许范围返回 JS 线程。ABI 稳定性只涵盖选定的 Node-API 契约；直接依赖 V8、Node C++ 或外部库仍有独立兼容性。依据见[固定版本 Node-API](https://nodejs.org/download/release/v24.16.0/docs/api/n-api.html)。

错误码、待处理 JS [异常](../../glossary/runtime.md#runtime.errors)、Rust panic 和 C++ exception 不能无约定地混用。Rust 的非 unwind ABI 上，Rust panic 跨出会终止进程，外部异常进入 Rust 会有未定义行为；允许展开时也需相应 ABI 和编译配置，`panic=abort` 不因外层 catch 变成可恢复异常。稳妥的边界通常在各自语言侧处理受支持失败，再转成明确的状态与数据；不能假定 catch_unwind 捕获所有外部异常。

## Wasm 偏移与原生地址是不同的东西

memory32 的常见约定用整数 offset 和 length 标识某个特定线性内存中的字节范围，不是宿主进程的任意地址。传字符串还需约定 UTF-8 等编码、分配/释放导出和有效期；Wasm 核心数值接口不会自动理解应用字符串协议。

教学范围检查设内存长度 M=65536、p=65530、n=10。起点在内存内，但剩余仅 6 字节，范围仍越界。先确保 p/n 是约定范围的非负整数，再检查 `p ≤ M` 且 `n ≤ M-p`，避免在有限整数类型中只检查可能溢出的 `p+n`。范围合法也不证明该片区域属于这个对象，或仍未被释放。

宿主若缓存 TypedArray 视图，memory.grow 之后还要遵循对应内存种类的更新规则。对于非共享、固定长度 ArrayBuffer 暴露方式，增长会分离旧 buffer，应重新取得 memory.buffer 并建立视图；共享或可调整大小的变体要另查规则。本文依据 [Wasm JS API 的 memory buffer 规则](https://www.w3.org/TR/wasm-js-api-2/)，不推广成所有 buffer 都同样失效。

## 性能取舍要算边界完整成本

自选模型：边界固定开销每次 2 微秒，原生计算每项 1 微秒。1000 次单项调用共 3000 微秒；一次批量处理 1000 项共 1002 微秒，尚未计复制、分配、[排队](../../glossary/performance.md#performance.queueing)和[延迟](../../glossary/performance.md#performance.latency-throughput)。批量可能摊薄调用开销，却增加单次内存与等待；原生实现快不保证完整链路快。

验证应覆盖空输入、长度边界、分配失败、错误输出、重复释放防护、注销后在途回调、线程退出与异常转换，并记录架构、ABI、Runtime 和 native 库组合。机制可以先解释，内存安全与兼容保证仍需实际实现证据。

## 自检

1. API 相同为什么不代表 ABI 相同，repr(C) 又解决了哪部分问题？
2. encode 成功与失败分别由谁拥有、释放哪些资源？
3. 为什么注销回调后还要等待在途调用，GC 为什么不能自动替代这项约定？
4. p=65530、n=10 为什么不合法，合法偏移为何也不证明对象仍存活？
5. 1000 次单项与一次批量的模型成本各是多少，哪些实际成本还没算？

## 来源与核查

- [Rust Reference：Type layout](https://doc.rust-lang.org/reference/type-layout.html)、[Rustonomicon：FFI](https://doc.rust-lang.org/nomicon/ffi.html)，2026-10-23 核查滚动文本；覆盖布局、原始接口、安全包装、回调与展开。
- [Node.js 24.16.0 Node-API](https://nodejs.org/download/release/v24.16.0/docs/api/n-api.html)，2026-10-23 核查固定版本；覆盖 ABI 范围、句柄、引用、线程与异常状态。
- [Wasm JS API](https://www.w3.org/TR/wasm-js-api-2/)，2026-10-23 核查当日 Candidate Recommendation Draft；覆盖内存 buffer 更新，不代表全部引擎已支持所有新变体。

本文为 source-checked 概念说明。没有执行 ABI/工具链对照、原生调用、allocator/回调故障注入、Wasm 内存增长或跨语言性能实验。
