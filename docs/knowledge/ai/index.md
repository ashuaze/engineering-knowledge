<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# LLM、RAG 与 Agent 工程

建议优先级：P1。目标：把模型能力接入有状态、有权限、可[评测](../../glossary/ai.md#ai.evals)的业务系统。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

工具已成功执行但 [Runtime](../../glossary/runtime.md#runtime.virtual-machine) 未记录，重启后怎么办？

## 已有正文

- [持久化预算与失败收敛：恢复以后怎样避免无限重试](durable-budgets-and-failure-convergence.md)：区分步骤、尝试、期限、并发与费用预算，用共享账本、预留和终止分支约束[交接](../../glossary/ai.md#ai.planning)及恢复后的工作。
- [Evals 与失败分析：怎样判断 AI 应用真的变好了](evals-and-failure-analysis.md)：用任务定义、样本集、[评分规则](../../glossary/ai.md#ai.eval-rubric)和版本对照评价 AI 应用，区分检索、生成、权限与工具执行失败。
- [微调与蒸馏：模型学会示例，为什么仍需独立评估](fine-tuning-distillation-and-evaluation-boundaries.md)：区分提示、检索、参数适配及教师信号，说明全量/低秩更新、软目标、数据划分和质量成本验证。
- [MCP 与能力协商：工具能被发现，为什么仍不能直接执行](mcp-hosts-capabilities-and-execution-boundaries.md)：沿宿主、客户端和服务器解释初始化、工具/资源/提示原语，区分协议成功、[授权](../../glossary/security.md#security.identity)与真实业务结果。
- [记忆权限、撤销与删除：不可检索为什么不等于彻底清除](memory-access-revocation-and-deletion.md)：区分当前授权、逻辑删除、派生清理与备份留存，解释撤权、迟到回填和恢复后重现的边界。
- [记忆治理实验：版本、过期、撤权与删除后的检索](memory-governance-lab.md)：用权威记录、派生索引与缓存的独立 SQLite 文件，验证来源准入、版本冲突、过期、撤权和删除边界。
- [记忆版本、冲突与失效：旧事实怎样被新事实替换](memory-versions-conflicts-and-expiry.md)：用版本条件、来源修订与读取时有效性检查约束旧写入、派生索引、缓存和过期内容。
- [记忆写入与来源：哪些内容值得成为长期记录](memory-writing-and-provenance.md)：区分用户陈述、模型推断和工具观察，为记忆建立写入准入、来源关联与可信范围。
- [提示词与指令层级：文字写进上下文，为什么不等于获得执行权](prompts-message-roles-and-instruction-boundaries.md)：区分任务说明、参考数据、示例与宿主约束，说明角色、请求状态、外部内容和实际权限之间的边界。
- [RAG：检索到了资料，为什么仍会答错](rag-retrieval-and-grounding.md)：区分索引、召回、[重排](../../glossary/cache-search.md#cache-search.hybrid)、上下文组装与生成，解释相关性、来源支持、权限及新鲜度的不同保证。
- [可恢复 Agent Runtime：从工具结果未知开始设计](recoverable-runtime.md)：围绕工具副作用的故障窗口设计状态、恢复和人工介入。
- [结构化输出与校验：合法 JSON 为什么仍不能直接执行](structured-outputs-and-validation.md)：区分解析、Schema、业务条件、授权与结果事实，处理拒绝、不完整输出和格式修复的边界。
- [温度与采样：输出更稳定，为什么仍可能稳定地答错](temperature-sampling-and-reproducibility.md)：用下一[token](../../glossary/ai.md#ai.context)分布解释[温度](../../glossary/ai.md#ai.sampling)、候选过滤与逐步选取，区分随机性、事实质量和运行可复现性。
- [Token、上下文与记忆：模型为什么会忘记前面说过的话](tokens-context-and-memory.md)：区分 Token 编码、上下文预算、会话历史、持久记忆与业务状态，解释截断、压缩及缓存的边界。
- [工具授权与不可信结果：外部文字为什么不能变成执行许可](tool-authorization-and-untrusted-results.md)：区分可信身份、对象授权、动作审批和外部数据，解释[提示注入](../../glossary/ai.md#ai.injection)、审批绑定、恢复复查与最小能力。
- [工具调用契约：模型提出动作以后由谁执行](tool-calling-and-execution-contracts.md)：区分调用候选、运行时准入、工具受理和业务确认，说明标识、依赖、预算与未知结果的责任。
- [工具执行边界实验：从候选调用到可核实结果](tool-execution-boundaries-lab.md)：用固定候选、受控工具和两个独立 SQLite 文件，验证校验、授权、审批绑定、未知结果与查询恢复。
- [路由与交接契约：下一步交给谁，责任怎样转移](workflow-routing-and-handoff-contracts.md)：区分任务规划、路径选择、子任务委派与控制权交接，约束输入证据、结果责任和失败回退。
- [编排状态与检查点：保存进度后为什么仍可能重做](workflow-state-and-checkpoints.md)：区分模型上下文、流程状态、检查点与外部效果，解释恢复、重放、版本兼容和当前授权。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Token / Context Window](../../glossary/ai.md#ai.context) | 模型处理单元及单次可处理的上下文范围。 |
| [Prompt / System Instruction](../../glossary/ai.md#ai.instructions) | 任务输入、约束和应用定义的指令边界。 |
| [Temperature / Sampling](../../glossary/ai.md#ai.sampling) | 生成时的分布变换和采样方法。 |
| [Structured Output / JSON Schema](../../glossary/ai.md#ai.structured) | 按结构约束生成并校验结果。 |
| [Tool Calling / Function Calling](../../glossary/ai.md#ai.tools) | 模型提出工具请求，由宿主校验和执行。 |
| [Embedding / Vector Store](../../glossary/ai.md#ai.embeddings) | 内容向量化与相应检索存储。 |
| [RAG / Retrieval Pipeline](../../glossary/ai.md#ai.rag) | 获取相关证据并供生成使用的流程。 |
| [Chunking / Reranking / Grounding](../../glossary/ai.md#ai.grounding) | 文档切分、候选重排和答案证据约束。 |
| [Agent Loop](../../glossary/ai.md#ai.loop) | 决策、行动、观察与停止控制循环。 |
| [Planning / Routing / Handoff](../../glossary/ai.md#ai.planning) | 任务分解、处理路径选择和控制权移交。 |
| [Harness / Orchestration](../../glossary/ai.md#ai.harness) | 围绕模型的执行、工具、状态和控制体系。 |
| [MCP](../../glossary/ai.md#ai.mcp) | 模型应用连接工具和上下文的协议体系。 |
| [Agent State / Checkpoint](../../glossary/ai.md#ai.state) | 执行状态及可用于恢复的持久化进度。 |
| [Short-term / Long-term Memory](../../glossary/ai.md#ai.memory) | 区分当前任务上下文与跨任务保留的信息，并为长期记录约束来源、版本、权限及生命周期。 |
| [Semantic / Episodic Memory](../../glossary/ai.md#ai.memory-types) | 按事实知识、情境经历等用途理解记忆；用途分类不能替代来源核实或权限。 |
| [Human-in-the-loop](../../glossary/ai.md#ai.human) | 在特定决策或执行点引入人工参与。 |
| [Prompt Injection / Tool Security](../../glossary/ai.md#ai.injection) | 外部内容诱导越权与工具访问控制。 |
| [Evals / Golden Dataset](../../glossary/ai.md#ai.evals) | 系统化评测任务、数据、指标和判定。 |
| [Tracing / Token Cost / Latency](../../glossary/ai.md#ai.cost) | 执行可观测性和费用、时延预算。 |
| [Fine-tuning / Distillation](../../glossary/ai.md#ai.training) | 参数适配和用教师信号训练学生模型。 |
| [Context Compaction](../../glossary/ai.md#ai.compaction) | 用较少 Token 续接所需上下文，表示与保留规则依实现而异，不代替业务执行记录。 |
| [Eval Rubric / Model Grader](../../glossary/ai.md#ai.eval-rubric) | 将任务目标转为可判定标准，并核查自动评分与参考判断是否一致。 |
| [Development / Held-out Eval Set](../../glossary/ai.md#ai.eval-splits) | 区分反复调试样本和相对独立检查样本，避免据熟悉题目调优后高估泛化。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
