---
id: "kb-runtime-types-validation"
title: "类型系统与运行时校验：类型检查通过为什么仍会出错"
kind: "concept"
domain: "runtime"
status: "evolving"
summary: "以 TypeScript 区分静态约束、推导、结构兼容和运行时数据验证，解释 unknown、any、断言与泛型的信任边界。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-runtime-closures", "kb-api-contracts-pagination"]
related: ["kb-runtime-modules-cycles", "kb-frontend-bundling-splitting", "kb-security-object-authorization", "kb-engineering-contract-compatibility", "kb-engineering-property-state-models", "kb-engineering-static-analysis", "kb-security-sql-injection", "kb-runtime-compilation-jit", "kb-runtime-serialization"]
tags: ["type-system", "typescript", "validation", "generics"]
---

# 类型系统与运行时校验：类型检查通过为什么仍会出错

学习入口：响应已经写了类型，为什么字段仍可能是错误值？前置：JavaScript 值、对象、函数与[接口契约](../api/contracts-and-pagination.md)。本文以 TypeScript Handbook 为参照，说明[静态检查](../../glossary/engineering.md#engineering.analysis)与数据边界；片段假定启用 strict，提供 ES2015 及以上标准库和相应运行能力，均未执行[编译器](../../glossary/runtime.md#runtime.compilation)或[运行时](../../glossary/runtime.md#runtime.virtual-machine)测试，也不把 TypeScript 的设计推广到所有[类型系统](../../glossary/runtime.md#runtime.type-system)。

## 静态类型表达代码被允许怎样使用

静态类型检查根据源码、声明、推导和编译选项判断使用是否符合规则。类型推导可以从初始化和上下文得出类型，不要求每个变量都写注解；缺少注解不等于完全没有静态检查。

| 观察层次 | 回答什么 | 仍需什么证据 |
| --- | --- | --- |
| 静态类型 | 按当前声明与规则，代码能否这样使用一个值 | 外部数据是否符合声明、实际运行环境是否满足假设 |
| 运行时校验 | 当前收到的值是否符合执行的检查 | 检查是否完整、规则是否符合业务、之后是否改变 |
| 业务与权限判断 | 当前主体、对象与状态是否允许操作 | 可信身份、当前权威数据和相应原子边界 |

类型注解、interface 和类型断言等通常不作为运行时校验保留在输出 JavaScript 中；断言错误也不会自动生成一次验证失败。依据见 [TypeScript Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)。这不表示所有 TypeScript 语法都完全不生成代码，例如某些 enum 等语法有运行时表示，本文不展开其编译选项。

启用 [strict](https://www.typescriptlang.org/tsconfig/strict.html)会打开一组更严格的检查，但只在实际执行了相应检查、处理错误并约束发布流程时才形成有效反馈。单纯“构建成功”可能只是完成转译，不能推导类型检查也已执行。

## 类型断言不改变数据

下面是 TypeScript 教学片段，JSON 文本的实际字段与断言不符：

```typescript
type ReservationInput = { sku: string; quantity: number };

const candidate = JSON.parse('{"sku":7,"quantity":"2"}') as ReservationInput;
candidate.sku.toUpperCase();
```

as 让检查器按指定类型理解表达式，没有把数字 7 转成字符串；按片段中的实际值推演，调用不存在的字符串方法会失败。这里没有运行日志，也不把编译器接受断言当作数据正确的证明。

非空断言也不会在运行时替你检查 null。声明文件可以描述外部库 API，若描述过期或不符合实现，静态检查仍可能建立在错误前提上。接口、类型别名和[泛型](../../glossary/runtime.md#runtime.generics)返回类型都需要相应真实边界来支持。

## unknown、any 与窄化承担不同责任

any 允许很多未经检查的操作，可能让错误类型沿调用继续传播；unknown 要求先通过窄化等方式，才能在检查器允许的范围内使用。两者都不会把运行时值自动转换或清洗。

typeof、相等判断、判别字段与控制流可以帮助窄化。例如先排除 null 再按对象读取，才不会把 typeof null 的结果误当成可安全取字段。机制见 [TypeScript Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)。

自定义 type guard 或断言函数的签名也是一种承诺，检查器不会自动证明函数实现确实覆盖了全部业务规则。一个永远返回 true 的守卫不能成为可信验证器；仍需检查实际逻辑，并用错误输入验证拒绝路径。

## 结构兼容与泛型不证明业务身份

TypeScript 的很多兼容判断依据所需成员的结构，而不只看类型名字。同样以字符串表示的订单 ID 与客户 ID，可能在静态结构上兼容，却在业务含义上不能互换；新鲜对象字面量的额外属性检查又有自己的规则，不能把结构兼容简化为“任意字段都可随便传”。设计与边界见 [Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)。

泛型可表达输入、输出或[容器](../../glossary/devops.md#devops.containers)元素之间的类型关系。例如保留输入类型的 `identity<T>`，与把任意外部 JSON 声称为 T，不是相同证据。一个 `parseJson<T>` 只有类型参数而没有验证逻辑时，不能证明收到的数据真的属于 T。泛型机制见 [TypeScript Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)。

可以用不同包装或标记帮助区分静态业务类型，但来源、真实性与权限仍需相应验证。TypeScript 在设计上也并不追求完全健全的类型证明；不能把通过检查解释为排除了所有运行时错误。

## 在外部边界验证实际值

教学调用前提：入口把 JSON 文本经 JSON.parse 得到的数据作为 unknown 直接交给此函数，不把任意 [Proxy](../../glossary/networking.md#networking.proxy)、getter 或继承了业务字段的对象传进来。函数本身不验证对象来源，也不保证拒绝这些前提之外的对象。字段契约是 sku 长度大于零的字符串（本例允许空白字符串，未做 trim），quantity 为 1–99 的整数；下面检查并重建一份仅含这两个字段的对象，额外字段按本例策略丢弃：

```typescript
function parseReservation(value: unknown): ReservationInput {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error('invalid reservation');
  }
  const record = value as Record<string, unknown>;
  if (
    typeof record.sku !== 'string' || record.sku.length === 0 ||
    typeof record.quantity !== 'number' ||
    !Number.isInteger(record.quantity) ||
    record.quantity < 1 || record.quantity > 99
  ) {
    throw new Error('invalid reservation');
  }
  return { sku: record.sku, quantity: record.quantity };
}
```

片段未执行。Record 断言只是为了按 unknown 属性继续检查，不证明字段合法；成功分支依赖的是随后的运行时条件。JSON 文本本身是否合法还由解析步骤处理，格式解析与结构验证不能互相替代。

这个函数没有确认 SKU 存在、库存充足或主体有权预订；这些是服务端业务与[对象授权](../security/object-level-authorization.md)的责任。它也不限制文本字节数、字段复杂度或处理成本，输入大小和资源上限还需单独约定。

选择成熟的 Schema 工具可以减少手写检查，但仍要明确未知字段、缺省值、类型转换和错误报告策略，并管理 Schema 与静态类型的一致性。自动生成类型或校验器也需要验证其覆盖与版本，不能由“用了同一个名字”推导语义一致。

通过运行时类型校验的字符串，仍不能直接混入查询语法。数据库输出边界继续见[SQL 注入与参数化查询](../security/sql-injection-parameters-and-query-structure.md)，区分业务输入规则、绑定值与结构片段。

## 校验之后仍有状态与时间边界

静态检查与执行策略的关系见[编译、解释与 JIT](compilation-interpretation-jit-and-deoptimization.md)；外部数据在字节、字段和值之间怎样保留精度、存在性和身份，见[序列化与反序列化](serialization-representations-schemas-and-identity.md)。两篇补充概念边界，未增加本文类型工具或输入拒绝实测。

其他代码检查继续见[静态分析与告警](../engineering/static-analysis-rules-and-findings.md)：类型规则、数据流模型、实际扫描范围与业务输入验证分别分析。新文为来源核查和教学设计，没有新增本文编译、校验或扫描实测。

校验说明某个时刻的值通过了相应规则。若内部共享对象随后被修改，或业务权限和库存已经变化，旧校验结果不会自动更新。readonly 常用于静态限制，也不等同于运行时深度冻结或[并发](../../glossary/systems.md#systems.concurrency)控制。

[输入校验](../../glossary/api.md#api.validation)、可信身份、对象权限和原子业务提交需要组合。客户端表单通过检查也不替代服务端；错误分支、字段变化及版本组合，可用[契约测试](../engineering/contract-testing-and-compatibility.md)验证相应范围，再用[属性测试](../engineering/property-testing-and-state-models.md)探索输入反例。

自检：哪个值来自可信代码，哪个来自网络或存储？as 有没有实际检查？unknown 在哪里变成已验证数据？泛型保留了哪段类型关系？校验通过后仍缺少哪些身份、状态或资源条件？

2026-10-20 核查 TypeScript 官方类型、窄化、[兼容性](../../glossary/api.md#api.versioning)、泛型与 strict 文档，状态为 source-checked。类型片段、预订字段与验证器为教学设计；未运行 tsc、Schema 工具、类型用例或输入拒绝实验，也未把本站构建视为其静态和运行时验证。
