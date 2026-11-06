---
id: "kb-runtime-modules-cycles"
title: "模块系统与循环依赖：找到模块为什么仍读不到值"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "区分模块解析、链接与求值，解释 ESM 活绑定、初始化顺序、CommonJS 循环和模块身份的边界。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-runtime-closures", "kb-architecture-module-boundaries"]
related: ["kb-runtime-types-validation", "kb-frontend-bundling-splitting", "kb-runtime-event-loop", "kb-frontend-routing-cache", "kb-runtime-compilation-jit", "kb-runtime-virtual-machines"]
tags: ["module", "esm", "binding", "circular-dependency"]
---

# 模块系统与循环依赖：找到模块为什么仍读不到值

模块解析/求值与程序表示的转换分别见[编译、解释与 JIT](compilation-interpretation-jit-and-deoptimization.md)；JVM 装载/链接/初始化及宿主依赖继续见[语言虚拟机](virtual-machines-bytecode-hosts-and-isolation.md)。不同模型的术语需按各自规范理解，本次关联不新增模块运行实测。

学习入口：文件和导出名都存在，为什么启动时仍出现“初始化之前无法访问”？前置：[词法绑定](closures-and-lexical-bindings.md)与[模块边界](../architecture/module-boundaries-and-dependencies.md)。本文以 JavaScript [ESM](../../glossary/runtime.md#runtime.modules) 为主，CommonJS 对照限定 Node.js 24.16.0 文档；多文件片段为教学推演，没有执行模块加载实验。

## 源码依赖需要经过解析、链接和求值

源码中的 import 先建立依赖关系，宿主还要把模块说明符解析为具体模块身份并取得源码。解析语法、建立导入导出的关联，与执行模块体是不同工作；找到文件并不能说明模块体已经完成初始化。

| 概念阶段 | 要解决什么 | 可能失败在哪里 |
| --- | --- | --- |
| 解析说明符与加载 | ./a.mjs 或包名具体指向什么，从哪里取得 | 路径、包导出、URL、权限、网络与响应类型 |
| 解析语法与链接 | 哪些名字被导出，导入绑定关联到哪里 | 语法不合法、缺少导出或重导出歧义 |
| 求值 | 执行模块体及其依赖的初始化 | 过早读取、顶层[异常](../../glossary/runtime.md#runtime.errors)或[异步](../../glossary/runtime.md#runtime.async)初始化失败 |

这是帮助定位的概念分层，不表示宿主必须串行执行每一步。[ECMAScript 模块规范](https://tc39.es/ecma262/multipage/ecmascript-language-scripts-and-modules.html#sec-modules)定义模块记录、链接与求值；具体路径和加载规则还由宿主参与。

浏览器原生 ESM 与 Node 的说明符规则不能直接互换。例如浏览器中的裸包名通常需要 import map 等映射或构建处理；Node 还依据自己的包与文件规则解析。相关区别见 [MDN 模块指南](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)与 [Node.js 24.16.0 ESM](https://nodejs.org/download/release/v24.16.0/docs/api/esm.html#resolution-and-loading-algorithm)。

## ESM 导入关联的是活绑定

ESM 的具名导入关联导出方的绑定。导出方更新绑定后，导入方后续读取可以观察到新值；导入方不能因此随意给该导入名字重新赋值。导入导出的绑定语义见 [ECMAScript Module Environment Records](https://tc39.es/ecma262/multipage/executable-code-and-execution-contexts.html#sec-module-environment-records)。

下面两个独立文件的片段仅供推演，假设入口只在这些语句之后读取，且没有其他写入者：

```javascript
// counter.mjs
export let count = 0;
export function advance() { count += 1; }

// main.mjs
import { count, advance } from './counter.mjs';
const saved = count;
advance();
console.log(count, saved); // 推演为 1、0
```

count 是后续读取的导入绑定，saved 是初始化时读取后保存的数字值。若导出值是对象，导入绑定只读也不等于对象被冻结；对象属性能否修改还需看对象本身和约定。这与[闭包](../../glossary/runtime.md#runtime.closure)篇“绑定”和“提前计算结果”的区分相通。

静态 import 不因写在模块体靠后位置，就等待上方语句先运行；依赖图的链接与求值有自己的规则。不要把它按普通函数调用逐行解释，更不能通过移动几行 import 来可靠地修复初始化依赖。

## 循环是否失败，取决于何时读取什么

教学入口是导入 a.mjs，两个文件均无顶层 await：

```javascript
// a.mjs
import { b } from './b.mjs';
export const a = 1;
export const fromB = b;

// b.mjs
import { a } from './a.mjs';
export const b = a + 1;
```

a 依赖 b，b 又依赖 a。在这条求值路径中，b 的初始化读取 a 时，a 的 const 绑定尚未初始化，会产生 ReferenceError。文件存在、导出名正确和链接成功，都不能消除这个时间窗口。[MDN Cyclic imports](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#cyclic_imports)解释了循环与过早读取的关系。

循环并非一定立即报错。如果只是建立函数，而读取发生在相关绑定完成初始化之后，可能正常工作；声明种类与顶层执行内容也会影响结果。不能把某个延后读取的成功例子推广为任意循环安全。

排查时画出“谁依赖谁”以及“谁在顶层读取谁”。如果环来自两个职责共享初始化状态，可以将共同约定移入第三个模块、重新分配职责，或建立显式初始化入口。机械加入定时器、改成动态 import 或切换文件格式，可能只是改变失败时刻，还需确认依赖与错误处理真正闭合。

## CommonJS 循环可能暴露尚未完成的导出

Node.js 的 CommonJS 按模块执行结果提供 module.exports。循环 require 时，为避免无限递归，参与者可能拿到另一模块尚未执行完成的导出对象，因而观察到缺失或中间状态。机制见 [Node.js 24.16.0 Cycles](https://nodejs.org/download/release/v24.16.0/docs/api/modules.html#cycles)。

CommonJS 中从返回对象解构一个数字属性，会保存当时的值，不能直接当成 ESM 的具名活绑定；后续替换 module.exports 也可能与早先持有的对象形成区别。应分别追踪导出对象、对象属性及其读取时刻。

两者提供不同机制，互操作又受 Node 版本和模块条件影响。Node 24.16.0 的 require 可加载符合识别规则的同步 ESM：例如 .mjs，或由最近 package.json 的 type: module 标识的 .js；没有 type: commonjs 且包含 ESM 语法的 .js 也有对应识别规则。被加载模块及其导入依赖图须不含顶层 await；普通加载流程遇到这种异步依赖会抛出 ERR_REQUIRE_ASYNC_MODULE，应改用适当的异步加载流程。规则见 [Loading ECMAScript modules using require()](https://nodejs.org/download/release/v24.16.0/docs/api/modules.html#loading-ecmascript-modules-using-require)。

没有顶层 await 也不表示任意循环都被允许：CommonJS 与 ESM 的互操作边参与即时循环时，还可能触发 [ERR_REQUIRE_CYCLE_MODULE](https://nodejs.org/download/release/v24.16.0/docs/api/errors.html#err_require_cycle_module)。因此不能沿用“一律不能 require ESM”的结论，也不能从支持同步 ESM 推导所有混合环都安全。本文不提供完整跨格式迁移配置。

## 模块身份与缓存不等于全局唯一实例

“只执行一次”需要限定模块系统、解析后的身份和执行环境。Node 的 CommonJS 缓存与解析文件名相关，ESM 使用自己的模块身份与缓存；同一份源码经不同身份进入、不同[进程](../../glossary/systems.md#systems.execution-units)或执行环境中加载，都不能据此假定共享一份状态。

例如 Node ESM 中，不同 query 或 fragment 的 file URL 可以产生不同加载身份，见 [Node.js ESM URLs](https://nodejs.org/download/release/v24.16.0/docs/api/esm.html#urls)。不要靠不断拼接随机 query 当作无代价的“刷新”：它可能同时建立新的状态与持有关系。CommonJS 的缓存范围见 [Caching](https://nodejs.org/download/release/v24.16.0/docs/api/modules.html#caching)。

模块求值缓存、浏览器 HTTP 缓存和应用数据缓存分别保存不同对象。下载命中缓存不等于所有执行环境共用一个模块实例，清理查询缓存也不等于重建模块。相关分层见[前端路由与缓存](../frontend/routing-state-and-cache-lifecycles.md)。

## 动态导入与顶层异步仍需明确依赖

import() 是在运行中请求模块的表达式，通过 Promise 提供结果；它不是“晚一点执行这行静态 import”的纯文本替换。普通模块成功加载并完成求值后，Promise 才以相应[命名空间](../../glossary/devops.md#devops.isolation)对象兑现；已有模块可能被复用，请求模块不必然产生新的网络请求。加载或求值失败会进入相应异步错误流程，依据见 [MDN import()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)。

顶层 await 可以让模块求值涉及异步依赖，依赖它的模块不能简单按同步初始化推算；等待链还可能因设计不当而无法推进。本文的循环反例刻意排除顶层 await，没有列出所有异步环形等待情形。动态 import 是否形成独立输出文件，则是[打包与代码分割](../frontend/bundling-tree-shaking-and-code-splitting.md)要分析的另一层问题。

自检：错误发生在找模块、链接名字还是执行初始化？读到的是导入绑定、对象属性还是保存的值？相同源码是否解析为同一模块身份？顶层读取可否移入明确的初始化/调用阶段，又由谁保证顺序？

2026-10-20 核查 ECMAScript、MDN 与 Node.js 24.16.0 文档，状态为 source-checked。片段和依赖路径为纸面推演；未运行 ESM/CommonJS、顶层 await、模块缓存或多环境对照实验，也未把本站构建当作这些语言反例的实测。
