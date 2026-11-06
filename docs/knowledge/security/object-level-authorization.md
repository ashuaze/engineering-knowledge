---
id: "kb-security-object-authorization"
title: "对象级授权：已登录为何仍不能访问这份数据"
kind: "concept"
domain: "security"
status: "evolving"
summary: "将主体、动作、对象和租户关系写成可验证的访问规则，覆盖详情、列表和写入。"
created: "2026-10-16"
updated: "2026-10-26"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-api-idempotency", "kb-ai-recoverable-runtime", "kb-security-sessions-tokens", "kb-api-contracts-pagination", "kb-ai-rag", "kb-ai-evals", "kb-ai-tool-security", "kb-ai-tools-lab", "kb-security-ssrf", "kb-security-sql-injection", "kb-security-mtls-service-identity", "kb-api-styles-gateway", "kb-security-authorization-models", "kb-cache-object-storage", "kb-security-trust-threat-models", "kb-api-resource-validation"]
tags: ["security", "authorization", "tenancy"]
---

# 对象级授权：已登录为何仍不能访问这份数据

学习入口：用户修改一个文档 ID 后，为什么能读到别人的内容？前置知识：请求参数、身份[认证](../../glossary/security.md#security.identity)与基本 SQL。本文适合开发、测试、安全和平台人员；本地实验只验证授权策略，不包含登录或令牌校验。

AI 工具侧可继续读[工具授权](../ai/tool-authorization-and-untrusted-results.md)和[本地边界实验](../ai/tool-execution-boundaries-lab.md)：候选参数、旧审批或恢复记录均不能替代当前权限。实验没有实现登录或远程凭证验证。

从单次对象权限继续看[信任边界与威胁建模](trust-boundaries-least-privilege-and-threat-modeling.md)与[资源模型与输入边界](../api/resource-models-input-validation-and-write-boundaries.md)，同时检查入口、租户范围和可写字段。

## Definition：定义与问题

认证回答当前请求代表谁；授权回答这个主体能否对某个对象执行某种动作。登录成功后仍需判断租户、归属、角色和对象状态等规则。[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)明确区分了两者，并建议默认拒绝和逐请求校验。

[对象级授权](../../glossary/security.md#security.tenant-isolation)失败（BOLA）发生在访问对象时缺少相应权限判断。可猜测的 ID 使问题容易暴露，但换成 [UUID](../../glossary/distributed.md#distributed.uuid) 也不能替代授权。[OWASP API1:2023](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)将检查重点放在主体是否有权对请求对象执行该动作。

## Principles：工作机制与核心原理

先把业务规则写成明确的判定：`允许 = 有效身份 ∧ 有效租户成员关系 ∧ 对象属于所选租户 ∧ 对象关系满足要求 ∧ 动作被允许`。这是本文教学策略，具体产品可能允许团队共享、委托或审批，须另行定义。

实验规定：有效成员只能读取自己在该租户的文档；只有 editor 成员可以修改自己的文档；reader 可读自己的文档。请求携带的租户只是选择目标，服务器仍要验证成员关系。即使两个租户恰好存在相同 owner_id，也不能跨租户读取。

在取得受保护内容或执行写入的服务端路径检查规则。详情、列表、下载、导出、批量接口和后台任务都需要覆盖；页面按钮隐藏只影响界面。策略复用有助于一致性，规则的变化仍要通过测试验证。

## Trade-offs：优势、限制与适用边界

| 设计 | 收益 | 成本与边界 |
| --- | --- | --- |
| 查询中加入租户和对象关系条件 | 在读取前缩小数据范围 | 需要与业务规则、索引和所有查询路径保持一致 |
| 角色与对象归属组合判断 | 可区分“能编辑”和“能编辑谁的对象” | 规则比单一角色判断复杂，需明确冲突处理 |
| 缓存授权结果 | 减少重复判定成本 | 必须定义权限撤销、版本和失效窗口 |
| 对缺失与无权对象采用相近外部响应 | 减少直接暴露存在性 | 调试需依赖内部审计；不能据此承诺无信息侧信道 |

上述是本知识库的设计取舍。示例不实现跨租户管理员、共享文档或数据库行级安全，也不评价某个认证框架是否安全。

## Implementation：代码或架构实现

架构流程为：验证身份 → 解析目标与动作 → 从可信数据验证成员关系 → 执行受约束查询或写入 → 输出允许的字段 → 记录必要审计信息。

下面是与本地实验等价的说明性读取流程，参数必须绑定，principal 来自已验证的服务端身份：

```sql
SELECT d.id, d.title
FROM documents d
JOIN memberships m
  ON m.tenant_id = d.tenant_id AND m.user_id = :principal_id
WHERE m.active = 1
  AND d.tenant_id = :selected_tenant
  AND d.owner_id = :principal_id
  AND d.id = :document_id;
```

写入同样把角色、成员关系、租户和归属放进 UPDATE 条件，并核对影响行数。列表先在数据库约束范围，再分页与统计，避免先取出未授权内容后才过滤。实际 Python / SQLite 代码见[授权实验](../../../examples/object_authorization/lab.py)。其中 `Principal` 只是服务端身份的[测试替身](../../glossary/engineering.md#engineering.doubles)，禁止把客户端传来的 user_id 直接构造成可信身份。

## Failure Modes：常见错误与故障模式

| 错误 | 表现 | 修正方向 |
| --- | --- | --- |
| 只验证令牌有效 | 登录用户可访问任意对象 ID | 再校验对象与动作 |
| 只比 owner_id，忽略租户关系 | 同名身份或错误租户选择导致越界 | 同时限定成员关系与对象租户 |
| 详情有检查，列表或导出遗漏 | 页面正常，批量接口仍泄露内容或计数 | 共用访问范围并覆盖全部入口 |
| 读取允许就默认写入允许 | reader 可以更改自己的文档 | 对读、改、删等动作分别定义权限 |
| [长任务](../../glossary/frontend.md#frontend.long-tasks)只在启动时检查 | 权限撤销后旧任务仍继续操作 | 执行时重新确认；明确撤销生效边界 |

“先检查、后修改”之间还可能发生权限或对象状态变化。实验把写入条件放在同一条 SQL 中，但没有验证多连接下[并发](../../glossary/systems.md#systems.concurrency)撤销与写入的先后语义；生产系统须根据[事务隔离](../../glossary/database.md#database.isolation)、锁和策略存储定义边界。

## Practice：工程案例、测试与验证

从仓库根目录运行，要求 Python 3.10+，仅使用内存 SQLite：

```bash
python3 examples/object_authorization/lab.py
python3 -m unittest discover -s examples/object_authorization -p 'test_*.py' -v
```

2026-10-16 在 Python 3.13.13 / SQLite 3.50.4 执行，10 项测试通过。预期与观察一致：Alice 读取自己的 tenant-a 文档；同租户 Bob 的文档被拒绝；即使 owner_id 相同，tenant-b 文档也被拒绝；列表仅返回允许的对象；撤销成员关系后下一次调用被拒绝；reader 可读不可改；未授权写入没有改变标题。

这套测试的身份与对象均为本地虚构数据，不调用真实服务。未覆盖真实[会话](../../glossary/security.md#security.sessions)、[JWT](../../glossary/security.md#security.tokens) 校验、策略缓存、共享授权、分页与导出实现、并发撤销及生产审计。返回相同异常类型只验证应用行为，不证明 HTTP 响应时间或大小相同。

自检：为一个实际对象列出“本人、同租户他人、其他租户、权限已撤销、匿名”五类主体及读写动作，先写允许矩阵，再构造拒绝用例，并检查拒绝后业务状态。

当业务会代表用户抓取外部地址时，还需控制服务端请求可以到达哪里，见[SSRF 与服务端请求边界](ssrf-url-resolution-and-egress-boundaries.md)。

参数化隔离值与 SQL 结构，但不能替代这里的对象和租户权限，继续见[SQL 注入与参数化查询](sql-injection-parameters-and-query-structure.md)。

服务调用方的证书身份与权限映射见[mTLS 与服务身份](mtls-service-identities-and-trust-boundaries.md)，入口认证及不同查询/调用契约的执行边界见[API 风格与网关](../api/api-styles-contracts-and-gateway-boundaries.md)。连接可信或请求通过入口，都仍需对应的对象与动作检查。

判断依据与更新生效继续见[权限模型与策略传播](authorization-models-policy-distribution-and-revocation.md)，下载能力的签发与期限见[对象存储与预签名访问](../cache-search/object-storage-versions-uploads-and-presigned-access.md)。角色或关系变化、存储请求能力和已接受下载分别有撤销边界。

## Related Concepts：关联概念

- [RAG 与依据](../ai/rag-retrieval-and-grounding.md)：在片段进入模型与引用预览前限定当前访问范围。
- [Evals 与失败分析](../ai/evals-and-failure-analysis.md)：单独观察权限边界样本，不能用平均分掩盖越权。

- [认证、会话与令牌](authentication-sessions-and-tokens.md)：解释可信主体来自哪里，以及会话和令牌何时失效。
- [HTTP 契约与分页](../api/contracts-and-pagination.md)：分页与统计继续使用当前授权范围，游标不能替代权限判断。

- [幂等性](../api/idempotency.md)：重放旧结果仍需执行当前授权，缓存结果不能跨身份返回。
- [可恢复 Agent Runtime](../ai/recoverable-runtime.md)：恢复工具动作时重新确认权限与业务前提。

## 来源与核查

核查日期：2026-10-16。[OWASP](../../glossary/security.md#security.threats) API Security Top 10 使用 2023 版；Cheat Sheet 用于身份与授权区分、逐请求检查、默认拒绝和测试原则。成员与 owner 组合策略、数据模型及异常类型为本知识库教学设计；测试范围限于随附本地策略。

- [OWASP：API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [OWASP：Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
