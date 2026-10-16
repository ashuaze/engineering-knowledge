<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# LLM、RAG 与 Agent 工程

建议优先级：P1。目标：把模型能力接入有状态、有权限、可评测的业务系统。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

工具已成功执行但 Runtime 未记录，重启后怎么办？

## 已有正文

- [可恢复 Agent Runtime：从工具结果未知开始设计](recoverable-runtime.md)：围绕工具副作用的故障窗口设计状态、恢复和人工介入。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Token / Context Window | 模型处理单元及单次可处理的上下文范围。 |
| Prompt / System Instruction | 任务输入、约束和应用定义的指令边界。 |
| Temperature / Sampling | 生成时的分布变换和采样方法。 |
| Structured Output / JSON Schema | 按结构约束生成并校验结果。 |
| Tool Calling / Function Calling | 模型提出工具请求，由宿主校验和执行。 |
| Embedding / Vector Store | 内容向量化与相应检索存储。 |
| RAG / Retrieval Pipeline | 获取相关证据并供生成使用的流程。 |
| Chunking / Reranking / Grounding | 文档切分、候选重排和答案证据约束。 |
| Agent Loop | 决策、行动、观察与停止控制循环。 |
| Planning / Routing / Handoff | 任务分解、处理路径选择和控制权移交。 |
| Harness / Orchestration | 围绕模型的执行、工具、状态和控制体系。 |
| MCP | 模型应用连接工具和上下文的协议体系。 |
| Agent State / Checkpoint | 执行状态及可用于恢复的持久化进度。 |
| Short-term / Long-term Memory | 当前任务上下文和跨任务持久信息。 |
| Semantic / Episodic Memory | 可复用事实知识和情境经历记录。 |
| Human-in-the-loop | 在特定决策或执行点引入人工参与。 |
| Prompt Injection / Tool Security | 外部内容诱导越权与工具访问控制。 |
| Evals / Golden Dataset | 系统化评测任务、数据、指标和判定。 |
| Tracing / Token Cost / Latency | 执行可观测性和费用、时延预算。 |
| Fine-tuning / Distillation | 参数适配和用教师信号训练学生模型。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
