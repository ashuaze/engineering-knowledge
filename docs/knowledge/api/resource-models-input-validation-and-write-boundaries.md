---
id: "kb-api-resource-validation"
title: "资源模型与输入边界：字段合法为什么仍不能保存"
kind: "concept"
domain: "api"
status: "evolving"
summary: "区分资源身份、表示、操作与异步任务，分层检查输入形状、字段权限、状态转换及上下文处理。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-api-contracts-pagination", "kb-security-object-authorization"]
related: ["kb-api-conditional-requests", "kb-api-idempotency", "kb-security-trust-threat-models", "kb-runtime-types-validation", "kb-security-sql-injection"]
tags: ["resource-modeling", "validation", "sanitization", "mass-assignment"]
---

# 资源模型与输入边界：字段合法为什么仍不能保存

学习入口：JSON 符合 Schema，用户也已登录，为什么仍不能把请求直接绑定到数据库对象？资源身份、可写字段、状态转换和并发条件仍需独立判断。

前置：[HTTP 契约](contracts-and-pagination.md)、[对象级授权](../security/object-level-authorization.md)。本文以请求式 API 为范围，Google AIP 作为一种具体设计规则参照，[OWASP](../../glossary/security.md#security.threats) 用于输入边界；不把某个 URL 风格当作所有 API 的强制规范。对象、请求和任务均为纸面设计，未启动服务或执行攻击测试。

## 资源不是数据库行的直接投影

资源标识指向稳定的业务对象，表示是某次交互中可见的数据。数据库结构、表示字段和允许动作可以有不同边界。资源导向的组织与标准/自定义方法参照 [AIP-121](https://google.aip.dev/121)，不等于所有业务动作都能任意改写一个 `status` 字段。

例如订单的“取消”需要检查履约进度、权限及关联效果。允许调用者直接保存 `status=cancelled`，可能绕过这些规则。可使用明确动作或受约束的状态更新；关键是定义合法转换、结果及失败，命名方式不能代替这些约束。

耗时导出还可以创建操作资源，区分已接纳、执行中、成功和失败，并提供查询结果的方法，参照 [AIP-151](https://google.aip.dev/151)。返回任务标识不表示导出已经完成；取消请求也需说明作用范围与是否已发生不可撤销效果。

## 输入检查是一串不同职责

| 层次 | 要检查什么 | 不能由这一层替代 |
| --- | --- | --- |
| 解析和资源限制 | 编码、格式、长度、深度、解压后大小等 | 当前主体权限 |
| 结构与类型 | 必填、类型、枚举、范围、未知字段规则 | 对象存在与业务状态合法 |
| 身份与字段权限 | 主体能否访问对象、能改哪些字段 | 并发写入时仍满足规则 |
| 业务与并发条件 | 状态转换、不变量、版本/条件保存 | 输出到 HTML/SQL 等上下文时的处理 |

[OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)区分校验与数据使用时所需防护。客户端校验可改善体验，服务端仍需执行；同一输入经过不同解析器或重复解码时，应明确规范化与解释顺序，不能用简单黑名单代替准确语法和上下文。

## 自动绑定会扩大可写能力

教学请求只应允许修改昵称，却额外携带 `is_admin=true` 或 `tenant_id=other`。若框架把全部字段直接绑定到持久对象，结构上可解析的数据便可能越过字段[授权](../../glossary/security.md#security.identity)。使用明确可写字段/输入对象并按动作检查，见 [OWASP Mass Assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)。

客户端的资源 ID、租户字段、角色名都不是可信授权事实。服务端计算的价格、拥有者、审计时间等字段，应按契约由可信路径产生。未知字段是拒绝还是忽略也要稳定定义；不能依赖“当前版本碰巧没用它”保护将来新增的敏感字段。

## 校验、净化与输出处理不能混作一次清洗

合法昵称可能包含引号和非 ASCII 字符。把它们全部删除，可能损坏业务数据，也不能保证其他上下文安全。SQL 使用参数化，HTML 使用对应上下文的输出编码；允许富文本时再采用明确的内容[净化](../../glossary/api.md#api.validation)策略。分别见 [SQL 参数化](../security/sql-injection-parameters-and-query-structure.md)与[XSS 输出边界](../security/xss-contexts-sinks-and-browser-defenses.md)。

类型检查通过也不证明时间范围、单位和关联条件正确。例如 `start <= end` 是关系条件，订单总额与明细一致是业务条件。并发下“先查合法，再无条件保存”仍可能使用已过期事实，需要事务、版本或条件更新保护，见[条件请求](conditional-requests-and-cache-validation.md)。

## 用反例验证每一层的承诺

选取类型正确但无权限、权限正确但状态过期、合法文本进入不同输出上下文、任务已接纳但最终失败等情形。每种失败应有稳定错误含义与恢复方式；不要把任何校验错误都写成内部异常，也不要在响应中泄露不应公开的对象或内部细节。

## 自检

1. 资源标识、表示、数据库行和业务动作为何不必一一对应？
2. 导出任务返回标识后，调用方还需确认什么状态？
3. Schema 通过为什么不能证明字段授权和状态转换合法？
4. 自动绑定 `is_admin` 的风险在哪一层？未知字段规则为何重要？
5. 为什么删除所有引号不能代替参数化、输出编码或并发条件保存？

## 来源与核查

2026-10-26 核查 AIP-121/151 与 OWASP 输入校验、批量赋值说明，范围为所引模型和边界。本文为 source-checked 概念文章；未执行解析器对照、字段越权、净化器、数据库并发或异步任务[集成测试](../../glossary/engineering.md#engineering.tests)。
