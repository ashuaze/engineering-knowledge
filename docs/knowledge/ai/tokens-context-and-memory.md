---
id: "kb-ai-context"
title: "Token、上下文与记忆：模型为什么会忘记前面说过的话"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "区分 Token 编码、上下文预算、会话历史、持久记忆与业务状态，解释截断、压缩及缓存的边界。"
created: "2026-10-19"
updated: "2026-10-27"
last_verified: "2026-10-19"
verification: "source-checked"
prerequisites: []
related: ["kb-ai-rag", "kb-ai-evals", "kb-ai-recoverable-runtime", "kb-cache-search-cache-aside", "kb-ai-memory-provenance", "kb-ai-memory-versioning", "kb-ai-memory-access-deletion", "kb-ai-memory-lab", "kb-ai-workflow-state", "kb-ai-instruction-boundaries", "kb-ai-sampling-decoders", "kb-ai-training-distillation"]
tags: ["tokens", "context", "memory"]
---

# Token、上下文与记忆：模型为什么会忘记前面说过的话

学习入口：应用保存了聊天记录，模型为什么仍答不出之前确认过的接口版本？前置知识：请求、响应与持久化数据。本文讨论文本生成应用的输入组织与[状态管理](../../glossary/frontend.md#frontend.state)，使用官方文档说明机制；不绑定具体模型容量、价格或 SDK，也不讨论完整的训练和注意力实现。

输入来源见[提示词与指令边界](prompts-message-roles-and-instruction-boundaries.md)，输出选择见[温度、采样与复现](temperature-sampling-and-reproducibility.md)，参数学习及教师信号见[微调、蒸馏与评估](fine-tuning-distillation-and-evaluation-boundaries.md)；上下文变化不自动更新训练权重。

## Token 是处理单位，不是固定字数

文本进入模型前会经过编码，形成 [Token](../../glossary/ai.md#ai.context) 序列。Token 可对应常见字符片段、单词的一部分或其他编码单元，并不总等于一个汉字或一个英文单词。具体切分取决于编码器与输入内容，代码、空格和不同语言的计数也可能不同。[OpenAI Key concepts](https://developers.openai.com/api/docs/concepts#tokens)提供了 Token 的入门定义。

因此，不能把文件字节数、编辑器字数或某种语言的平均比例直接当作准确 Token 数。要估算请求大小，应使用目标模型或服务对应的计数方式，并保留请求包装、工具定义和其他结构的开销。本文不展示未经编码器执行的“真实分词结果”。

Token 与 [Embedding](../../glossary/ai.md#ai.embeddings) 也不是同一个概念：前者在这里是文本编码后的处理单位，后者是数据的向量表示。给一段资料生成向量，既不会让生成模型自动获得原文，也不会把资料写进它的参数；仍需设计查询、取回与输入路径。

## 上下文窗口限制一次处理的范围

上下文包含本次处理所用的指令、用户输入、选入的历史、工具结果和外部资料等。窗口容量是资源上限，不能当作对全部输入都能正确利用的保证。输入与输出上限如何约束、推理 Token 是否占用相应预算，需要按模型及 API 核查。[Conversation state](https://developers.openai.com/api/docs/guides/conversation-state#managing-the-context-window)说明了这种预算关系。

教学设定：一个虚构服务把本次可安排的总预算按 8,000 Token 规划，留出输出和格式余量；数字只演示分配，不是任何产品规格或实测计数。

| 用途 | 教学预算 | 组织依据 |
| --- | --- | --- |
| 指令与工具说明 | 500 | 保留当前任务需要的约束 |
| 历史与状态摘要 | 1,500 | 保留已确认条件与未决问题 |
| 检索资料 | 2,500 | 优先保留能支持当前问题的证据 |
| 当前问题及必要输入 | 500 | 保留版本、对象与动作等约束 |
| 生成输出 | 2,000 | 预留回答空间，而非输入塞满窗口 |
| 格式与其他余量 | 1,000 | 由实际协议、计数及误差决定用途 |

这些分配相加为 8,000，但不能替代真实请求计数。若工具返回超长日志，下一步可能超限；若为容纳它而删掉“只讨论 2.4 版”这一条件，请求即使成功也可能回答错版本。是否拒绝、截断或压缩取决于服务设置，不能把成功返回视为原始历史完整保留。

## 聊天历史、工作上下文与持久状态各做什么

| 保存位置或表示 | 保存的东西 | 不自动具备的能力 |
| --- | --- | --- |
| 聊天记录或会话存储 | 历次输入、输出与事件 | 不代表全部记录都进入当前上下文 |
| 当前工作上下文 | 本次选入或恢复的内容 | 不保证下一次请求仍带上它 |
| 应用的[长期记忆](../../glossary/ai.md#ai.memory) | 经策略保存的偏好、事实或经验及来源 | 不代表内容正确、仍新鲜或对当前主体可见 |
| 权威业务状态与执行记录 | 订单、权限、动作意图和可核实结果 | 不能由模型回忆或聊天摘要直接替代 |

“短期记忆”和“长期记忆”常是应用架构中的称呼，不是一套所有产品都统一的存储机制。应用可自行传入历史，也可使用服务端的会话衔接能力；这不等于每轮请求改变了模型参数。实现应能解释当前请求用了哪些历史、摘要或状态，而不是只告诉读者“模型自己记着”。

同一用户过去偏好中文，可以作为有来源和更新规则的记忆；“创建工单成功”则需要工具结果或权威查询支持。摘要里写着“已创建”不能补出缺失的事务证据。业务效果与恢复状态见[可恢复 Runtime](recoverable-runtime.md)。

## 截断、摘要、检索与缓存解决不同问题

| 方法 | 可以帮助什么 | 需要承担的代价 |
| --- | --- | --- |
| 选择或截断历史 | 限制输入长度，减少无关内容 | 可能丢掉条件、决定与[工具调用](../../glossary/ai.md#ai.tools)关系 |
| 应用生成文本摘要 | 用较短表示保留选定信息 | 摘要可能遗漏限定条件，也可能写错 |
| 按需检索外部记录 | 只取当前任务所需资料 | 取回内容取决于查询、权限、索引和更新 |
| [Prompt](../../glossary/ai.md#ai.instructions) 缓存 | 复用重复前缀的计算 | 不自动保存新的业务事实或扩大上下文上限 |

摘要应带着保留目标设计，例如已确认的版本、来源、未完成动作与未知结果，而不是只追求短。对仍有工具调用关联的历史，还应遵守对应协议的消息与结果结构，不能机械删除一半。

厂商提供的 [Compaction](../../glossary/database.md#database.lsm) 也不能统一理解为可读文本摘要。例如 [OpenAI Compaction 文档](https://developers.openai.com/api/docs/guides/compaction)描述了不透明的压缩表示及相应续接规则。那是上下文续接能力，不是应用自己可随意解释的业务日志；具体输出应按该接口约定处理。

[Prompt caching 文档](https://developers.openai.com/api/docs/guides/prompt-caching)说明了重复输入前缀的复用及其与新输出的关系。命中缓存不表示上一次回答已被固定，也不证明权限或知识仍有效。把派生信息当权威状态的问题，可对照[缓存与失效](../cache-search/cache-aside-and-invalidation.md)。

## 用一次版本问答检查记忆设计

教学场景：用户先确认“查询 2.4 版接口”，随后提供很多日志，最后问“撤销何时生效”。以下都是故障假设，没有调用真实模型。

1. 会话存储有版本约束，但请求组装没选入：检查输入选择与衔接，不能仅检查数据库是否保存过聊天。
2. 摘要只保留“讨论撤销”，丢掉 2.4：检查摘要保留规则，并回看原始来源。
3. 条件仍在，但检索返回 1.9 文档：进入检索与版本过滤排查，不把所有错误归为上下文不足。
4. 版本和资料都正确，回答仍套用旧规则：进入生成与评价排查，不能用“已经放进上下文”证明理解正确。

若需澄清版本或重新查询，应让工作流显式做出决定。对用户偏好、知识资料和业务状态使用不同的更新、过期与权限规则，也便于定位“忘记”发生在哪个环节。

模型可见历史也不同于[编排状态与检查点](workflow-state-and-checkpoints.md)：前者服务当前输入，后者记录流程恢复边界，两者都不能替代外部业务证据。

## 长期记忆的后续治理

继续读[写入与来源](memory-writing-and-provenance.md)、[版本与失效](memory-versions-conflicts-and-expiry.md)和[权限与删除](memory-access-revocation-and-deletion.md)。独立[记忆治理实验](memory-governance-lab.md)已验证本地来源与生命周期时序；它没有调用模型，不改变本文 Token、长上下文和模型恢复的未测范围。

## 自检与核查范围

试着解释：数据库里有完整历史为什么不等于模型当前看到完整历史？Token 数为何不能按中文字符数直接计算？缓存命中为何不等于长期记忆？压缩后的“工具已完成”为什么不能独立证明外部副作用成功？

核查日期：2026-10-19。本文查阅官方概念、会话、压缩和缓存说明；预算为纸面计算，没有运行分词计数、模型请求、长上下文或记忆恢复实验。诊断时可保存版本、输入组成与来源引用，并按数据策略控制明细保存范围；不需要把敏感原文全部写入日志。

- [RAG 与依据](rag-retrieval-and-grounding.md)：把当前问题所需资料按边界取回上下文。
- [Evals 与失败分析](evals-and-failure-analysis.md)：区分上下文选择、检索与生成失败。
- [可恢复 Agent Runtime](recoverable-runtime.md)：将模型可见内容与权威执行证据分开。
