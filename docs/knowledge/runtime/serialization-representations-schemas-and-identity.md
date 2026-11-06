---
id: "kb-runtime-serialization"
title: "序列化与反序列化：怎样保留数值、类型、身份与版本语义"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "区分对象、数据模型与字节表示，解释 JSON 数值、字段存在性、对象共享、格式演进和不可信输入的边界。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-runtime-types-validation", "kb-api-contracts-pagination"]
related: ["kb-messaging-event-evolution", "kb-runtime-ffi-boundaries", "kb-runtime-exception-propagation", "kb-engineering-contract-compatibility", "kb-api-webhook-signatures"]
tags: ["serialization", "json", "schema", "identity"]
---

# 序列化与反序列化：怎样保留数值、类型、身份与版本语义

学习入口：同一个订单对象发出去再读回来，ID 为什么变了，日期为什么成了字符串，共享的子对象为什么不再共享？前置：[类型与运行时校验](type-systems-and-runtime-validation.md)、[接口契约](../api/contracts-and-pagination.md)。本文以 JSON、[Protobuf](../../glossary/api.md#api.contracts) 和浏览器结构化克隆说明表示边界，示例为纸面推演，未执行编码器。

## 传出去的是约定表示

[序列化](../../glossary/runtime.md#runtime.serialization)按规则把值或对象结构转换成可保存、传输的表示，反序列化依据规则重建。协议可以分成三层：业务含义、数据模型、字节编码。`amount=100` 到底是元还是分，不能由整数编码决定；字符串日期的时区也不由 UTF-8 决定。

| 层次 | 要约定什么 | 常见遗漏 |
| --- | --- | --- |
| 业务含义 | 单位、身份、时间含义、有效范围 | 金额换了单位却只保留字段名 |
| 数据模型 | 类型、缺失/null/默认值、集合与关联 | 把“没提供”当成显式零值 |
| 表示与编码 | 字段标识、数字格式、字符编码、长度/帧边界 | 文本能解析却已经失真 |

[进程](../../glossary/systems.md#systems.execution-units)内地址、类方法、锁、打开的文件和有效[授权](../../glossary/security.md#security.identity)，都不能只靠复制字段自动重建。资源句柄要重新申请或通过受控协议转交；业务 ID 相同也不证明当前调用者有权使用。

## JSON 的 number 不保证每个接收端都精确

[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html)规定 JSON 的语法和互操作建议，但允许实现限制数值精度。采用 binary64 的接收端在 `[-(2^53)+1, (2^53)-1]` 整数范围内能取得一致精确值；这不是 JSON 语法能写出的所有数字范围。

教学输入 `{"id":9007199254740993}`：它处于 binary64 可表示的 9007199254740992 和 9007199254740994 中间，按通常 JavaScript Number 的最近值、偶数舍入规则得到前者，身份信息已经丢失。`2^53=9007199254740992` 本身可精确表示，却不能保证其相邻整数仍可区分。事后把 Number 转字符串无法恢复。可以把 ID 约定为十进制字符串，并限制符号、长度、前导零与范围；也可以使用双方真正支持的精确整数表示。单把字段写成 int64 还需检查生成代码和 JSON 映射。

同样要约定非有限数、负零、十进制金额、Unicode、重复字段和时间格式。JSON 不包含日期类型；`{"occurred_at":"2026-10-23T08:00:00Z"}` 是字符串，解析与时区解释仍属于应用契约。对象成员重复时不同解码器可能拒绝或选择不同值，安全敏感入口不应依赖“大家都取最后一个”的假设。

## 能解码、类型相符与语义兼容是三道关

原始字节先受长度、嵌套深度与解码成本限制；解析得到结构后，再做字段和业务校验。JSON 解析成功不证明 quantity 在 1–99，也不证明 SKU 存在。反序列化过程若允许构造任意类或调用钩子，检查“最终字段正确”可能已经太晚。

Python 的 [pickle 文档](https://docs.python.org/3.13/library/pickle.html)明确说明反序列化可执行任意代码，只应处理可信数据。签名能证明来自某个持钥方且未被篡改，也不让其任意对象构造自动安全；仍要限制可接受来源与行为。纯数据格式更便于限定结构，但仍需资源上限、业务校验和输出使用约束。

版本演进还要分别考虑旧写新读、新写旧读和历史回放。Protobuf 的[proto3 指南](https://protobuf.dev/programming-guides/proto3/)以字段编号表达 wire 身份，删除后应保留编号，不能仅因新字段名字不同就重用。存在性也有差异：隐式存在的数值零通常无法区分“没提供”与“显式设零”；需要这种区分时应选择支持显式存在的字段设计。历史与混合版本继续见[事件契约演进](../messaging/event-contracts-schema-evolution-and-replay.md)。

## 值相同、共享引用与字节相同分别判断

自选对象图：根的 left 与 right 都指向同一个 `{count:1}`。用普通 JSON 树表示 `{"left":{"count":1},"right":{"count":1}}`，两个值相同，却没有编码“两条边指向同一个节点”。解码后修改 left.count 不要求 right.count 跟着变。若业务依赖共享身份，应显式编码节点 ID 与引用，或选支持对象图的机制。

浏览器[结构化克隆](https://html.spec.whatwg.org/multipage/structured-data.html)可处理受支持的共享引用与循环，目标图仍是新图；它不会把任意用户类的原型方法完整复制成原对象。ArrayBuffer 转移还涉及源缓冲区分离与资源归属变化，不等同普通深拷贝，更不是通用网络格式。

反过来，语义相同的值也未必序列化为相同字节。空格、字段顺序或未知字段可能影响结果；Protobuf 官方单列[非规范化说明](https://protobuf.dev/programming-guides/serialization-not-canonical/)，确定性输出不能直接推广为跨版本/实现的唯一规范表示。计算签名、缓存键或去重摘要前，要明确是在验证原始字节还是某个固定的规范化协议；重序列化后验原始签名可能失败，见 [Webhook 签名](../api/webhook-signatures-replay-and-delivery.md)。

## 用小矩阵检查交换契约

可以准备精确整数边界、缺失/null/零、未知字段、旧字段编号、共享引用、循环和超深输入作为候选。逐项写明源值、编码、目标表示、允许的变化与拒绝原因，再检查多个语言和版本组合。可解析不应成为唯一验收条件；文本与二进制的体积、速度和分配成本也应在相同数据与配置下比较。

## 自检

1. JSON number 语法合法，为什么订单 ID 仍可能在解码时改变？
2. 缺失、null 与显式零值为什么不能随意互换？
3. 两个字段原先共享一个对象，值相同的 JSON 树保留了什么、丢了什么？
4. 类型检查为什么阻止不了不可信 pickle 在构造阶段执行代码？
5. 同一业务值为什么可能有不同字节，签名与去重应先约定哪层身份？

## 来源与核查

- [RFC 8259 §4/6/8/9](https://www.rfc-editor.org/rfc/rfc8259.html)，2026-10-23 核查；覆盖 JSON 成员、数值互操作、编码与解析限制。
- [ECMAScript Number 类型](https://tc39.es/ecma262/multipage/ecmascript-data-types-and-values.html#sec-ecmascript-language-types-number-type)，2026-10-23 滚动草案核查；覆盖 binary64 可表示值与中点舍入，文中大整数为据此复算。
- [Protobuf proto3](https://protobuf.dev/programming-guides/proto3/)、[Serialization Is Not Canonical](https://protobuf.dev/programming-guides/serialization-not-canonical/)，2026-10-23 滚动文档核查；覆盖字段身份、存在性和字节稳定性，不推广到所有格式。
- [WHATWG 结构化数据](https://html.spec.whatwg.org/multipage/structured-data.html)，2026-10-23 核查当日 Living Standard；覆盖对象图、可克隆范围与转移。
- [Python 3.13 pickle](https://docs.python.org/3.13/library/pickle.html)，2026-10-23 核查；覆盖对象重建与不可信输入风险。

本文为 source-checked 概念说明。没有执行编解码、混合版本、签名、对象转移、恶意输入或格式性能实验。
