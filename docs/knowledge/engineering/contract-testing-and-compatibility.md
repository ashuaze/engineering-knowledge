---
id: "kb-engineering-contract-compatibility"
title: "契约测试与版本兼容：双方测试通过为什么仍接不上"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "区分接口描述、消费者期望和提供方验证，解释版本矩阵、匹配规则、失败交互及契约证据的适用边界。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-engineering-test-scopes", "kb-api-contracts-pagination"]
related: ["kb-architecture-module-boundaries", "kb-architecture-aggregates-invariants", "kb-devops-delivery-lifecycle", "kb-engineering-property-state-models", "kb-security-object-authorization", "kb-engineering-code-review", "kb-engineering-dependency-governance", "kb-messaging-event-evolution"]
tags: ["contract-testing", "compatibility", "consumer", "provider"]
---

# 契约测试与版本兼容：双方测试通过为什么仍接不上

学习入口：客户端与服务端各自测试都通过，上线后却因字段、错误或版本不一致而失败，缺了哪份证据？前置：[测试层次与替身](test-scopes-and-doubles.md)、[HTTP 契约](../api/contracts-and-pagination.md)。本文以 HTTP 请求响应和 [Pact](../../glossary/engineering.md#engineering.contracts) 的消费者驱动模型为参照，解释协作验证；教学交互没有运行 Pact、[Broker](../../glossary/messaging.md#messaging.roles) 或真实接口。

## 契约描述协作，测试检查选定的协作行为

契约需要说明调用方发送什么、提供方怎样理解、返回什么，以及调用方如何处理。字段结构只是其中一部分，[状态码](../../glossary/api.md#api.http-semantics)、错误、缺省值、单位、枚举和鉴权前提都会影响[兼容性](../../glossary/api.md#api.versioning)。

| 证据 | 能支持什么 | 剩余边界 |
| --- | --- | --- |
| [OpenAPI](../../glossary/api.md#api.contracts) 等接口描述 | 声明路径、参数、输入输出结构及相应约定 | 文件存在不证明双方[运行时](../../glossary/runtime.md#runtime.virtual-machine)已经遵守 |
| 按 Schema 验证响应 | 验证被检查的结构与约束 | 不自动证明客户端正确解释单位和业务状态 |
| 消费者与提供方契约测试 | 检查已建模交互在相应版本中的兼容 | 不自动覆盖所有消费者、业务流程与真实依赖 |
| 选定的集成与端到端验证 | 检查其范围内的真实协作路径 | 未覆盖环境、故障与负载仍没有证据 |

[OpenAPI 3.1.2](https://spec.openapis.org/oas/v3.1.2.html)提供接口描述结构。契约测试可以围绕描述或实际消费者需要组织，不等于所有团队都必须采用消费者驱动方式；本文用 Pact 展开其中一种机制。

## 消费者测试要真正经过消费代码

Pact 的消费者测试先声明预期交互，再让实际消费代码向测试中的模拟提供方发送请求，核对请求并返回约定响应；测试还要验证消费者正确理解结果。完成后形成可用于提供方验证的契约材料。流程见 [How Pact works](https://docs.pact.io/getting_started/how_pact_works)。

```text
消费者版本 C1 的实际适配代码
  → 模拟提供方：核对它发送的请求
  ← 约定响应：检查 C1 的解析、错误分支与对外结果
  → 保存对应交互契约，标识生成它的消费者版本
```

如果测试绕过真实适配代码，直接手写一段 HTTP 请求，就可能只证明测试作者与模拟服务彼此一致。客户端实际拼错参数、遗漏请求头或错误处理字段的缺陷仍可能漏掉。消费者测试写法见 [Pact Consumer tests](https://docs.pact.io/consumer)。

教学例子：消费者读取订单状态，只依赖 order_id 和 state。测试应调用真正负责请求与解析的那层代码，并验证返回的领域结果；不必把所有提供方内部字段都固定成精确快照。

## 提供方验证把同一份交互交回实现

提供方验证对相应版本的实现发出契约中的请求，将实际响应与交互要求比较。它补上“模拟提供方是否反映实际实现”的关键一侧，不能只验证模拟服务两遍。机制见 [Pact Provider verification](https://docs.pact.io/provider)。

不同交互需要明确 provider state，例如“订单已提交”“订单不存在”“该主体不能访问订单”。状态准备应可独立执行和清理，不依赖上一条测试恰好创建了对象。这里的状态是测试前提，不是要求客户端把一句状态描述发给生产服务。

实际接入了哪些依赖仍须声明。提供方测试可以使用受控数据库或依赖替身；验证真实 HTTP 实现并不自动证明真实支付、数据库隔离或生产身份校验都已执行。权限交互也要核对拒绝后的数据与副作用，不能仅凭返回了 403 就认定所有[授权](../../glossary/security.md#security.identity)路径正确。

## 匹配规则既可能过严，也可能过宽

匹配规则决定哪些差异算破坏契约。把与消费者无关的生成 ID、时间戳或附加字段全部精确锁定，会制造不必要的失败；只要求“任意整数”又可能漏掉单位和范围变化。规则与请求/响应的差别见 [Pact Matching](https://docs.pact.io/getting_started/matching)。

| 教学变化 | 要检查的实际假设 |
| --- | --- |
| 响应增加可选字段 | 当前客户端是否忽略未知字段，匹配策略是否允许 |
| 枚举增加状态 | 老客户端是否支持未知值或有明确失败策略 |
| 同为整数，金额从分改为元 | 结构检查可能通过，但业务解释已经变化 |
| 资源不存在改为另一种错误响应 | 消费者对应分支是否仍能识别与处理 |

“只新增字段必然兼容”并非通用结论，严格[反序列化](../../glossary/runtime.md#runtime.serialization)、精确匹配与客户端行为都可能改变结果。契约也可能根本没有表达某项语义；应写清单位和状态含义，并用合适的业务断言补充，不能把文件里的示例值当作全部规则。

除了成功交互，还应选择真实消费路径依赖的失败情形，例如不存在、无权访问和输入被拒绝。[超时](../../glossary/api.md#api.retries)、连接中断、响应丢失及重试的副作用通常还需要其他范围的测试，不能由一份 HTTP 响应契约覆盖。

## 兼容性判断需要具体版本组合

消费者 C2 与提供方 P2 的交互通过，不说明仍在线的 C1 也兼容 P2；回退到 P1 时同样需要检查。

| 教学验证矩阵 | P1 | P2 |
| --- | --- | --- |
| C1，仍在线 | 已验证通过 | 未验证 |
| C2，待发布 | 不兼容 | 已验证通过 |

假设两代消费者会混合运行，不能只凭右下角通过就放行 P2。还需要补齐 C1/P2 的适用验证，或明确旧版本退出与发布次序。发布 C2 前也要确保它不会访问仍在线的 P1；若允许 P2 回退，同样需解决 C2/P1 的已知不兼容，检查实际可能出现的所有组合。

Pact Broker 的矩阵和部署记录能把已发布验证结果与应用版本、目标环境关联，用于相应兼容性判断；它依赖契约、结果和环境版本记录准确。机制见 [Pact Can I Deploy](https://docs.pact.io/pact_broker/can_i_deploy)。未知消费者、缺失验证、不同配置或部署后变更，不会因矩阵里有绿色记录而自动获得证据。

语义版本号表达公开 API 的兼容意图：在 SemVer 的相应稳定版本规则下，不兼容变更提升主版本，兼容功能提升次版本，兼容修复提升补丁版本；项目需先声明公开 API。依据见 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)。版本号不能替代具体组合的行为验证，尤其不能单凭“只升了补丁版本”断定消费者安全。

异步事件的 writer/reader 矩阵、历史范围与混合部署，继续见[事件格式演进](../messaging/event-contracts-schema-evolution-and-replay.md)。编码格式可解析之外，还需验证默认值、金额单位、中继未知字段、权限和回放副作用。

## 把契约证据接到边界与交付

维护过程继续读[代码评审](code-review-context-and-change-boundaries.md)和[依赖锁定与 SBOM](dependency-resolution-lockfiles-and-sbom.md)。批准要对应版本，组件升级也要核对本项目契约；版本号和清单不能替代真实兼容证据。新文没有新增本文消费者/提供方验证。

一份可复查记录应包含消费代码和提供方的版本、契约身份、匹配规则、交互前提、实际依赖、验证结果及目标环境版本。失败时先定位是规则改变、前提错误、实现缺陷还是遗漏版本，避免直接放宽匹配到变绿。

在[领域与聚合设计](../architecture/domain-models-aggregates-and-invariants.md)中，业务含义由明确维护者定义；接口契约负责跨边界表达这些含义。它不能证明整个聚合[不变量](../../glossary/systems.md#systems.atomicity)、跨服务事务、容量与恢复都已正确。发布次序和回退兼容继续见[构建、部署与回滚](../devops/build-deploy-rollback.md)。

自检：测试是否真的经过消费代码？谁验证同一份契约的提供方？仍在线的消费者版本有哪些？新增字段、未知枚举和错误分支分别会发生什么？已通过的测试究竟用了哪些真实依赖？

2026-10-20 核查 Pact、OpenAPI 3.1.2 与 SemVer 官方资料，状态为 source-checked。交互草图、错误情形和版本矩阵为教学设计；未安装 Pact、运行消费者/提供方验证、配置 Broker 或执行发布门禁实验，未把已有单元与站点测试当作这些机制的集成证据。
