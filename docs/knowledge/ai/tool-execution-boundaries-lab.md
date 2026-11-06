---
id: "kb-ai-tools-lab"
title: "工具执行边界实验：从候选调用到可核实结果"
kind: "lab"
domain: "ai"
status: "evolving"
summary: "用固定候选、受控工具和两个独立 SQLite 文件，验证校验、授权、审批绑定、未知结果与查询恢复。"
created: "2026-10-19"
updated: "2026-10-20"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-ai-tool-contracts", "kb-ai-structured-output", "kb-ai-tool-security"]
related: ["kb-ai-recoverable-runtime", "kb-ai-evals", "kb-api-idempotency", "kb-security-object-authorization"]
tags: ["tool-calling", "authorization", "recovery", "lab"]
---

# 工具执行边界实验：从候选调用到可核实结果

问题：参数看起来正确、工具声称成功或[运行时](../../glossary/runtime.md#runtime.virtual-machine)中途结束时，怎样判断可以执行、已经完成还是需要保留未知？本实验于 2026-10-19 在 Python 3.13.13 / SQLite 3.50.4 / Windows 11 x64 执行。输入是固定候选，工具是本地替身；没有调用模型、OpenAI API、[MCP](../../glossary/ai.md#ai.mcp) 服务或外部业务系统。

## 装置与可信输入

运行时只注册 tickets.create.v1，参数为 project_id、title、priority。候选带有协议关联 call_id；业务 operation_id 由实验的可信运行时调用路径提供。真实系统仍须保护这条路径，本实验没有[认证](../../glossary/security.md#security.identity)服务器。

可信测试会话为主体 u1、租户 t1；p1 属于 t1 且开放，p2 属于 t2，p3 属于 t1 但关闭。会话权限和项目数据是受控夹具。跨租户场景特意把 p2 放进 grant 集合，仍因租户不匹配拒绝，避免同时被另一个条件拒绝而掩盖租户检查。

每个场景建立两个独立 SQLite 文件：backend 保存工单和工具操作账本，journal 保存运行时意图、参数指纹、状态与结果。工具侧的事务只覆盖 backend；它不与 journal 形成一个事务。两个文件仍在同一[进程](../../glossary/systems.md#systems.execution-units)和磁盘，不代表真实分布式工具。

## 怎样复现与核对证据

在仓库根目录运行，无需第三方依赖：

```bash
python examples/ai_tool_boundaries/lab.py
python examples/ai_tool_boundaries/lab.py --check
```

第一条执行全部场景并覆盖本地结果，第二条只检查，不覆盖已存 JSON。重新运行前先保存需要的基线；保存最终运行输出后，使用 `python examples/ai_tool_boundaries/lab.py --freeze-manifest` 冻结实现及记录摘要。

- [实验实现](../../../examples/ai_tool_boundaries/lab.py)。
- [原始结果 JSON](../../../examples/ai_tool_boundaries/results/results.json)：环境、24 类场景、观察状态、工具表、运行时表和带顺序号的阶段事件。
- [最终运行输出](../../../examples/ai_tool_boundaries/results/run.txt)与[字节数及 SHA256 清单](../../../examples/ai_tool_boundaries/results/manifest.json)。

临时文件限定在仓库 .cache/ai-tool-boundaries 下，清理前核对解析后的路径仍在该目录。每组关闭连接后删除临时数据库，只保留文本记录。最初系统临时目录受 Windows 沙盒权限限制，最终改用仓库缓存目录完成执行；下述结果均来自该最终实现。

## 准入与审批怎样工作

运行时先检查完整候选和工具白名单，再解析、校验参数，随后检查当前主体、租户、项目权限及开放状态。它拒绝重复 JSON 键、解析后无法编码为 UTF-8 的字段、额外身份或审批字段、错误类型、过长参数和不完整文本；这是限定字段的显式规则，不是完整 [JSON Schema](../../glossary/ai.md#ai.structured) 验证器。

写入还要求一条可信夹具生成的审批记录，绑定主体、租户、工具版本、operation_id 和参数摘要。审批有效期使用可控制的[逻辑时钟](../../glossary/distributed.md#distributed.clocks)，不是实际等候或生产审批服务。模型参数中的 approved=true 不能生成此记录；参数变更或逻辑期限耗尽后停在 waiting_approval。

每次 execute 与 recover 消耗一个本实例步骤名额；本轮预算场景设为一，第二次入口被停止。预算没有持久化，重开 Runtime 会重置名额，不是跨恢复总预算或 [Token](../../glossary/ai.md#ai.context)/费用限制。事件顺序号仅用于本组记录，不是独立 attempt_id；本轮没有实现后者。

## 24 类场景的结果

表中分组用于阅读，具体独立场景名和断言见原始记录。所有拒绝和等待审批的首次准入场景，工具调度次数与工单数量均为零。

| 场景组 | 场景数 | 实际观察 |
| --- | --- | --- |
| 正常创建 | 1 | 已核实结果与工单、操作账本对应，confirmed |
| 参数与工具入口 | 6 | 不完整 JSON、无法编码的 Unicode、重复键、额外身份/审批字段、错误类型、禁用工具均在调度前拒绝 |
| 业务与身份边界 | 2 | 同租户关闭项目、跨租户目标均拒绝 |
| 候选终态 | 2 | incomplete 与 refusal 夹具不作为完整调用执行 |
| 审批与执行前撤权 | 4 | 缺失、改参数、到期等待审批；审批后撤权拒绝 |
| 顺序重放与冲突 | 1 | call_id 改变但同动作只调度一次；同 operation_id 换参数拒绝 |
| 受理未完成 | 1 | 工具登记 pending，初次与恢复查询都不变成 confirmed |
| 错误回执、结果丢失 | 2 | 先 unknown；按稳定动作查询后 confirmed，没有再次创建 |
| 受控中断后重开 | 1 | 工具已提交，journal 仍 prepared；重开后查询确认，不重新调度 |
| 无法查询 | 1 | 工具已有工单，结果丢失且查询不可用，保持 unknown/人工对账 |
| 不可信结果文字 | 1 | note 中的 admin.delete 仍是带来源的数据；固定禁用工具候选被拒绝 |
| 步骤预算 | 1 | 首次确认，后续入口 stopped，没有新增工具效果 |
| 恢复前撤权 | 1 | 工具已有工单但本次恢复被拒绝，未查询或再次执行 |

合计 24 类、128 个检查结果通过。各场景独立的工具数据库累计创建九条工单，均在 p1；这些不是某个共享项目中的业务总量。每类检查数量不同，部分“没有越权效果”检查在零工单时自然成立；检查结果数不等于独立攻击或模型评价样本数。

## 怎样区分回执和权威记录

正常工具返回结构化状态、operation_id、ticket_id 和 note。[运行时校验](../../glossary/runtime.md#runtime.type-system)回执后，按可信作用域与稳定动作标识查询受控工具账本，比对参数摘要、状态与工单标识；记录 confirmed 后才返回可核实结果。实验另逐项核对每个 confirmed 观察结果和 journal 结果都匹配同一 key、参数摘要及实际工单的 ID、项目和标题，避免只核状态或数量。说明性 note 保持 untrusted_tool_data 标签，不会被自动当作调度指令。

错误回执场景先在 backend 实际提交，再返回格式正确但不匹配的 ticket_id=999999。运行时不能确认这份回执，保留 unknown；恢复查询取得该动作的真实记录才确认。若工具只返回 accepted，运行时保存 pending，查询也仍为 pending，不把受理当成完成。

本实验的账本与工单在同一个受控 backend 事务中写入，因此可以用它核对本动作；不能假设任意远程工具的 success 字段具有相同契约。note 标记也只说明来源，不是模型注入防护机制。

## 两种结果缺口怎样恢复

结果丢失场景在工具侧事务提交之后抛出受控 LostResult，运行时保存 unknown。恢复只查询原 operation_id，核对结果并保存 confirmed；原始工单数仍为一。

中断场景在[工具调用](../../glossary/ai.md#ai.tools)返回之后、journal 保存结果之前抛出明确的测试异常。此时检查 journal 仍为 prepared，关闭两个连接，再打开同名文件并重建两个对象。新的工具对象从数据库中查到已提交动作，运行时保存 confirmed，重开后的工具创建调用次数为零。事件记录保留准备、调度、中断、查询和确认顺序。

这是受控异常与数据库重开，不是进程强杀、断电或 SDK [Checkpoint](../../glossary/ai.md#ai.state) 故障注入。它只验证一处已选择窗口。prepared 不自动重新执行；实际生产恢复仍需识别更多状态和不可用情形。

## 权限与未知不能被恢复绕过

恢复只在当前身份仍允许访问时查询。恢复前撤权场景先产生一条工单并丢失返回，再使身份失效；recover 返回拒绝，工具查询计数仍为零。此时 journal 保持 unknown，权限撤销没有撤销原工单。

本地恢复查询不创建新工单，也不复用旧审批去发起写入。真实系统若连查询也需要额外审批，应配置相应协议。身份、项目和审批检查与工具执行并未原子结合；权限[并发](../../glossary/systems.md#systems.concurrency)变化、对象转移和远程凭证均未测试。

## 证据边界与后续验证

输入候选、refusal/incomplete 标签、逻辑时钟、权限和恶意 note 均为固定夹具；它们不是模型的真实响应或供应商协议适配器。工具端是本地 SQLite 替身，没有网络、认证、远程审批、MCP、并发工作者、真实用户副作用或模型注入测量。

因此，本轮不提供模型选工具成功率、约束解码通过率、[提示注入](../../glossary/ai.md#ai.injection)抵抗率、费用或[延迟](../../glossary/performance.md#performance.latency-throughput)结果，也不证明多进程 exactly-once、跨系统原子提交、完整恢复预算或生产级安全。旧[可恢复 Runtime](recoverable-runtime.md)只增加局部实验入口，仍保留 design-proposal。

继续阅读[工具调用契约](tool-calling-and-execution-contracts.md)、[结构化输出校验](structured-outputs-and-validation.md)与[工具授权](tool-authorization-and-untrusted-results.md)。资料核查与执行日期为 2026-10-19；本轮机制示意与实际断言分别由概念页和随附实现承担。
