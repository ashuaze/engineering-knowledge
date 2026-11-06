<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# LLM、RAG 与 Agent 工程词汇表

本页解释 23 组术语，按[完整术语索引](../glossary.md#ai)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [LLM、RAG 与 Agent 工程文章](../knowledge/ai/index.md)

## 本页术语

- [Token / Context Window](#ai.context)
- [Prompt / System Instruction](#ai.instructions)
- [Temperature / Sampling](#ai.sampling)
- [Structured Output / JSON Schema](#ai.structured)
- [Tool Calling / Function Calling](#ai.tools)
- [Embedding / Vector Store](#ai.embeddings)
- [RAG / Retrieval Pipeline](#ai.rag)
- [Chunking / Reranking / Grounding](#ai.grounding)
- [Agent Loop](#ai.loop)
- [Planning / Routing / Handoff](#ai.planning)
- [Harness / Orchestration](#ai.harness)
- [MCP](#ai.mcp)
- [Agent State / Checkpoint](#ai.state)
- [Short-term / Long-term Memory](#ai.memory)
- [Semantic / Episodic Memory](#ai.memory-types)
- [Human-in-the-loop](#ai.human)
- [Prompt Injection / Tool Security](#ai.injection)
- [Evals / Golden Dataset](#ai.evals)
- [Tracing / Token Cost / Latency](#ai.cost)
- [Fine-tuning / Distillation](#ai.training)
- [Context Compaction](#ai.compaction)
- [Eval Rubric / Model Grader](#ai.eval-rubric)
- [Development / Held-out Eval Set](#ai.eval-splits)

<a id="ai.context"></a>

## Token / Context Window

**ID：** `ai.context` · **建议优先级：** P1

**别名 / 检索词：** Token、Context Window、上下文窗口

**简释：** 模型处理单元及单次可处理的上下文范围。

Token 是模型分词后的处理单位，不等于一个汉字或英文单词；上下文窗口限制一次处理可容纳的信息。输入、工具结果和输出占用规则依模型接口而异。

**例子：** 长文档与工具返回共同挤占上下文，需要先选取与当前任务相关的内容。

**深入阅读：** [Token、上下文与记忆：模型为什么会忘记前面说过的话](../knowledge/ai/tokens-context-and-memory.md)

<a id="ai.instructions"></a>

## Prompt / System Instruction

**ID：** `ai.instructions` · **建议优先级：** P1

**别名 / 检索词：** Prompt、System Instruction、提示词、系统指令

**简释：** 任务输入、约束和应用定义的指令边界。

提示包含任务、参考数据和示例，角色或应用指令机制表达来源及优先关系。外部文字不能自授执行权，宿主仍需检查真实身份、权限和结果；实际角色及状态继承依模型/接口核对。

**例子：** 检索到的网页要求泄露凭据时，应把这句话作为不可信内容处理。

**深入阅读：** [提示词与指令层级：文字写进上下文，为什么不等于获得执行权](../knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)

<a id="ai.sampling"></a>

## Temperature / Sampling

**ID：** `ai.sampling` · **建议优先级：** P1

**别名 / 检索词：** Temperature、Sampling、温度、采样

**简释：** 生成时的分布变换和采样方法。

温度改变下一token分布的集中程度，top-k按数量、top-p按累计概率限制候选。低随机性、贪心和固定种子分别约束选择过程，均不证明事实正确或跨版本/硬件/服务完全复现。

**例子：** 结构稳定但事实错误的答案，不能单靠把温度降为零来修复。

**深入阅读：** [温度与采样：输出更稳定，为什么仍可能稳定地答错](../knowledge/ai/temperature-sampling-and-reproducibility.md)

<a id="ai.structured"></a>

## Structured Output / JSON Schema

**ID：** `ai.structured` · **建议优先级：** P1

**别名 / 检索词：** Structured Output、JSON Schema、结构化输出

**简释：** 按结构约束生成并校验结果。

结构化输出按约定格式约束生成，JSON Schema 可表达类型与部分结构规则。合法 JSON 或符合 Schema 仍不证明字段真实、业务可执行或用户有权限。

**例子：** 输出金额是数字后，仍需检查币种、范围、来源与支付授权。

**深入阅读：** [结构化输出与校验：合法 JSON 为什么仍不能直接执行](../knowledge/ai/structured-outputs-and-validation.md)

<a id="ai.tools"></a>

## Tool Calling / Function Calling

**ID：** `ai.tools` · **建议优先级：** P1

**别名 / 检索词：** Tool Calling、Function Calling、工具调用、函数调用

**简释：** 模型提出工具请求，由宿主校验和执行。

模型生成工具名称和参数候选，宿主负责校验、授权、执行和记录结果。提出调用不代表已执行，返回成功也需对应可核实的业务证据。

**例子：** 模型请求删除记录后，执行器仍须检查主体权限与目标范围。

**深入阅读：** [工具调用契约：模型提出动作以后由谁执行](../knowledge/ai/tool-calling-and-execution-contracts.md) · [工具执行边界实验：从候选调用到可核实结果](../knowledge/ai/tool-execution-boundaries-lab.md)

<a id="ai.embeddings"></a>

## Embedding / Vector Store

**ID：** `ai.embeddings` · **建议优先级：** P1

**别名 / 检索词：** Embedding、Vector Store、向量存储

**简释：** 内容向量化与相应检索存储。

Embedding 把内容映射为向量，Vector Store 存储向量与相关元数据并支持检索。编码版本、过滤权限、更新与删除传播决定实际可用性。

**例子：** 升级嵌入模型后通常需管理新旧索引兼容，不能直接混用不同向量空间。

**深入阅读：** [RAG：检索到了资料，为什么仍会答错](../knowledge/ai/rag-retrieval-and-grounding.md)

<a id="ai.rag"></a>

## RAG / Retrieval Pipeline

**ID：** `ai.rag` · **建议优先级：** P1

**别名 / 检索词：** RAG、Retrieval Pipeline、检索增强生成

**简释：** 获取相关证据并供生成使用的流程。

RAG 在生成前检索外部材料并作为依据，流程包含解析、索引、召回、选择和答案检查。检索命中不保证答案受到支持，资料权限和时效也需保留。

**例子：** 答案引用一段检索材料后，还要核对该段是否真正支持相应结论。

**深入阅读：** [RAG：检索到了资料，为什么仍会答错](../knowledge/ai/rag-retrieval-and-grounding.md)

<a id="ai.grounding"></a>

## Chunking / Reranking / Grounding

**ID：** `ai.grounding` · **建议优先级：** P1

**别名 / 检索词：** Chunking、Reranking、Grounding、文档切分、依据约束

**简释：** 文档切分、候选重排和答案证据约束。

Chunking 决定检索片段边界，Reranking 调整候选顺序，Grounding 约束答案与证据的关系。较高相关分数不自动代表充分证据，片段还应保留来源和上下文。

**例子：** 规则被切在两个片段时，需要把条件与结论一起提供给生成步骤。

**深入阅读：** [RAG：检索到了资料，为什么仍会答错](../knowledge/ai/rag-retrieval-and-grounding.md)

<a id="ai.loop"></a>

## Agent Loop

**ID：** `ai.loop` · **建议优先级：** P1

**别名 / 检索词：** Agent Loop、智能体循环

**简释：** 决策、行动、观察与停止控制循环。

Agent Loop 反复执行决策、行动和观察，并依据完成条件或预算停止。工具错误、结果不确定和重复行动必须显式处理，不能依赖无限自我重试收敛。

**例子：** 执行失败后先分类原因，再决定修参、查询状态、请求人工参与或终止。

**深入阅读：** [可恢复 Agent Runtime：从工具结果未知开始设计](../knowledge/ai/recoverable-runtime.md) · [路由与交接契约：下一步交给谁，责任怎样转移](../knowledge/ai/workflow-routing-and-handoff-contracts.md) · [持久化预算与失败收敛：恢复以后怎样避免无限重试](../knowledge/ai/durable-budgets-and-failure-convergence.md)

<a id="ai.planning"></a>

## Planning / Routing / Handoff

**ID：** `ai.planning` · **建议优先级：** P1

**别名 / 检索词：** Planning、Routing、Handoff、任务规划、路由、交接

**简释：** 任务分解、处理路径选择和控制权移交。

Planning 分解目标与依赖，Routing 选择下一处理路径，Handoff 移交控制和必要状态。交接契约需携带目标、权限、证据和剩余预算。

**例子：** 把数据库问题交给专门处理者时，同时传入已核实事实与尚未解决的约束。

**深入阅读：** [路由与交接契约：下一步交给谁，责任怎样转移](../knowledge/ai/workflow-routing-and-handoff-contracts.md)

<a id="ai.harness"></a>

## Harness / Orchestration

**ID：** `ai.harness` · **建议优先级：** P1

**别名 / 检索词：** Harness、Orchestration、编排、执行框架

**简释：** 围绕模型的执行、工具、状态和控制体系。

Harness 或编排层围绕模型提供工具、状态、调度、权限、恢复和观测。模型决定候选步骤，宿主仍是执行与约束的责任边界。

**例子：** 服务重启后，编排层依据持久记录恢复未完成工作并避免重复副作用。

**深入阅读：** [工具调用契约：模型提出动作以后由谁执行](../knowledge/ai/tool-calling-and-execution-contracts.md) · [路由与交接契约：下一步交给谁，责任怎样转移](../knowledge/ai/workflow-routing-and-handoff-contracts.md) · [编排状态与检查点：保存进度后为什么仍可能重做](../knowledge/ai/workflow-state-and-checkpoints.md) · [持久化预算与失败收敛：恢复以后怎样避免无限重试](../knowledge/ai/durable-budgets-and-failure-convergence.md)

<a id="ai.mcp"></a>

## MCP

**ID：** `ai.mcp` · **建议优先级：** P1

**别名 / 检索词：** MCP、模型上下文协议

**简释：** 模型应用连接工具和上下文的协议体系。

MCP按版本组织宿主、客户端和服务器的能力协商，提供工具、资源和提示原语。协议连通和发现不等于本次业务授权；传输凭据、对象权限、协议/工具错误和最终业务效果分别检查。

**例子：** 发现一个可调用工具后，仍要根据当前用户权限决定能否执行。

**深入阅读：** [MCP 与能力协商：工具能被发现，为什么仍不能直接执行](../knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)

<a id="ai.state"></a>

## Agent State / Checkpoint

**ID：** `ai.state` · **建议优先级：** P1

**别名 / 检索词：** Agent State、Checkpoint、智能体状态、检查点

**简释：** 执行状态及可用于恢复的持久化进度。

Agent State 保存推进任务所需的信息，Checkpoint 记录可恢复进度。检查点与外部副作用若不在同一原子边界，就需独立操作标识和结果核对。

**例子：** 工具执行后、检查点写入前崩溃时，恢复应先确认工具结果。

**深入阅读：** [可恢复 Agent Runtime：从工具结果未知开始设计](../knowledge/ai/recoverable-runtime.md) · [工具执行边界实验：从候选调用到可核实结果](../knowledge/ai/tool-execution-boundaries-lab.md) · [编排状态与检查点：保存进度后为什么仍可能重做](../knowledge/ai/workflow-state-and-checkpoints.md)

<a id="ai.memory"></a>

## Short-term / Long-term Memory

**ID：** `ai.memory` · **建议优先级：** P1

**别名 / 检索词：** Short-term、Long-term Memory、短期记忆、长期记忆

**简释：** 区分当前任务上下文与跨任务保留的信息，并为长期记录约束来源、版本、权限及生命周期。

短期记忆服务当前任务，长期记忆跨任务保留信息；二者都是系统设计概念。长期记录应带来源、版本、期限和访问规则，写入不等于内容已核实。

**例子：** 用户修改偏好后，新版本应替代旧版本，并防止迟到任务回填旧值。

**深入阅读：** [Token、上下文与记忆：模型为什么会忘记前面说过的话](../knowledge/ai/tokens-context-and-memory.md) · [记忆写入与来源：哪些内容值得成为长期记录](../knowledge/ai/memory-writing-and-provenance.md) · [记忆版本、冲突与失效：旧事实怎样被新事实替换](../knowledge/ai/memory-versions-conflicts-and-expiry.md) · [记忆权限、撤销与删除：不可检索为什么不等于彻底清除](../knowledge/ai/memory-access-revocation-and-deletion.md) · [记忆治理实验：版本、过期、撤权与删除后的检索](../knowledge/ai/memory-governance-lab.md)

<a id="ai.memory-types"></a>

## Semantic / Episodic Memory

**ID：** `ai.memory-types` · **建议优先级：** P1

**别名 / 检索词：** Semantic、Episodic Memory、语义记忆、情景记忆

**简释：** 按事实知识、情境经历等用途理解记忆；用途分类不能替代来源核实或权限。

语义记忆偏向事实与规则，情景记忆偏向特定经历和上下文。它们可采用不同表示，但用途分类不能替代证据校验、隐私与权限管理。

**例子：** 过去一次购买记录是情境信息，不能未经确认推断成永久用户偏好。

**深入阅读：** [记忆写入与来源：哪些内容值得成为长期记录](../knowledge/ai/memory-writing-and-provenance.md)

<a id="ai.human"></a>

## Human-in-the-loop

**ID：** `ai.human` · **建议优先级：** P1

**别名 / 检索词：** Human-in-the-loop、人在回路、人工参与

**简释：** 在特定决策或执行点引入人工参与。

Human-in-the-loop 在指定决策或执行点引入人工判断。请求应给出具体动作、目标、影响和已知证据；批准应绑定明确范围，变更后重新判断有效性。

**例子：** 人工批准向某收款方支付特定金额，不能被复用到另一金额或对象。

**深入阅读：** [工具授权与不可信结果：外部文字为什么不能变成执行许可](../knowledge/ai/tool-authorization-and-untrusted-results.md)

<a id="ai.injection"></a>

## Prompt Injection / Tool Security

**ID：** `ai.injection` · **建议优先级：** P1

**别名 / 检索词：** Prompt Injection、Tool Security、提示注入、工具安全

**简释：** 外部内容诱导越权与工具访问控制。

提示注入试图让外部内容改变系统行为或诱导越权；工具安全通过权限、隔离和执行校验约束影响。仅提示模型忽略恶意文字不能替代执行端防护。

**例子：** 工具结果包含外传文件的命令时，不应把它升级为用户授权。

**深入阅读：** [工具授权与不可信结果：外部文字为什么不能变成执行许可](../knowledge/ai/tool-authorization-and-untrusted-results.md) · [工具执行边界实验：从候选调用到可核实结果](../knowledge/ai/tool-execution-boundaries-lab.md)

<a id="ai.evals"></a>

## Evals / Golden Dataset

**ID：** `ai.evals` · **建议优先级：** P1

**别名 / 检索词：** Evals、Golden Dataset、评测、黄金数据集

**简释：** 系统化评测任务、数据、指标和判定。

Evals 用任务样本、判定规则和指标评估系统；黄金数据集提供经核对的参考。需要覆盖失败类型和运行条件，单一总分可能掩盖高风险错误。

**例子：** 分别记录答案错误、证据不足与工具越权，避免只报告平均完成率。

**深入阅读：** [Evals 与失败分析：怎样判断 AI 应用真的变好了](../knowledge/ai/evals-and-failure-analysis.md)

<a id="ai.cost"></a>

## Tracing / Token Cost / Latency

**ID：** `ai.cost` · **建议优先级：** P1

**别名 / 检索词：** Tracing、Token Cost、Latency、Token 成本

**简释：** 执行可观测性和费用、时延预算。

追踪把模型、检索和工具步骤关联起来，成本与延迟预算限制整体执行。费用按实际服务计价与用量记录核算，重试和后台步骤也应计入。

**例子：** 一次用户请求触发多轮工具循环，应累计所有模型调用的消耗。

**深入阅读：** [持久化预算与失败收敛：恢复以后怎样避免无限重试](../knowledge/ai/durable-budgets-and-failure-convergence.md) · [日志、指标与链路：怎样把一次故障的证据连起来](../knowledge/reliability/logs-metrics-and-traces.md)

<a id="ai.training"></a>

## Fine-tuning / Distillation

**ID：** `ai.training` · **建议优先级：** P1

**别名 / 检索词：** Fine-tuning、Distillation、微调、蒸馏

**简释：** 参数适配和用教师信号训练学生模型。

微调以任务数据更新参数或适配结构，蒸馏用教师分布/输出等信号训练学生。提示、检索、参数适配和训练信号各有范围，效果须用防泄漏的独立数据及实际质量/成本验证，不能替代实时事实和访问控制。

**例子：** 希望模型遵循特定输出风格可考虑微调，最新业务库存仍应查询可信数据源。

**深入阅读：** [微调与蒸馏：模型学会示例，为什么仍需独立评估](../knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md)

<a id="ai.compaction"></a>

## Context Compaction

**ID：** `ai.compaction` · **建议优先级：** P1

**别名 / 检索词：** Context Compaction、上下文压缩

**简释：** 用较少 Token 续接所需上下文，表示与保留规则依实现而异，不代替业务执行记录。

上下文压缩用摘要或重组减少继续任务所需 Token，但可能丢失细节。需保留目标、约束、证据位置和未完成事项；压缩摘要不能替代业务执行日志。

**例子：** 摘要记载已发起转账但无确认时，恢复不能把它当作已成功。

**深入阅读：** [Token、上下文与记忆：模型为什么会忘记前面说过的话](../knowledge/ai/tokens-context-and-memory.md)

<a id="ai.eval-rubric"></a>

## Eval Rubric / Model Grader

**ID：** `ai.eval-rubric` · **建议优先级：** P1

**别名 / 检索词：** Eval Rubric、Model Grader、评分规则、模型评分器

**简释：** 将任务目标转为可判定标准，并核查自动评分与参考判断是否一致。

评分规则把质量目标拆成可判断标准，模型评分器按规则辅助评估。要用参考判断核对偏差、一致性和对提示变化的敏感性。

**例子：** 区分事实正确、证据充分和格式合法，避免格式好掩盖内容错误。

**深入阅读：** [Evals 与失败分析：怎样判断 AI 应用真的变好了](../knowledge/ai/evals-and-failure-analysis.md)

<a id="ai.eval-splits"></a>

## Development / Held-out Eval Set

**ID：** `ai.eval-splits` · **建议优先级：** P1

**别名 / 检索词：** Held-out Eval Set、Development Set、评价保留集

**简释：** 区分反复调试样本和相对独立检查样本，避免据熟悉题目调优后高估泛化。

开发集可反复用于调试，保留集用于较独立地检查泛化。频繁依据保留集修改系统会造成泄漏，数据还需按来源和时间等避免近重复。

**例子：** 同一文档改写出的近似题目分别进入两组，可能高估真实泛化能力。

**深入阅读：** [Evals 与失败分析：怎样判断 AI 应用真的变好了](../knowledge/ai/evals-and-failure-analysis.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Model Context Protocol：工具与上下文协议](https://modelcontextprotocol.io/specification/2025-11-25)
- [Retrieval-Augmented Generation：原始论文](https://arxiv.org/abs/2005.11401)
- [OpenAI Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OWASP Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [OpenAI reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)
- [Transformers生成工具](https://huggingface.co/docs/transformers/main/en/internal/generation_utils)
- [Holtzman等人的原论文](https://arxiv.org/abs/1904.09751)
- [PyTorch可复现性说明](https://docs.pytorch.org/docs/2.14/notes/randomness.html)
- [MCP Architecture](https://modelcontextprotocol.io/specification/2025-11-25/architecture)
- [Lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
- [Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [Resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)
- [Prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)
- [Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [Transformers Fine-tuning](https://huggingface.co/docs/transformers/main/en/training)
- [PEFT LoRA说明](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)
- [Hinton、Vinyals与Dean原论文](https://arxiv.org/pdf/1503.02531)
- [Kim与Rush的序列级蒸馏研究](https://arxiv.org/abs/1606.07947)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
