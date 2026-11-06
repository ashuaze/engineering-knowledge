---
id: "kb-ai-sampling-decoders"
title: "温度与采样：输出更稳定，为什么仍可能稳定地答错"
kind: "concept"
domain: "ai"
status: "evolving"
summary: "用下一token分布解释温度、候选过滤与逐步选取，区分随机性、事实质量和运行可复现性。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-ai-context"]
related: ["kb-ai-instruction-boundaries", "kb-ai-evals", "kb-ai-structured-output", "kb-ai-training-distillation"]
tags: ["temperature", "sampling", "top-p", "reproducibility"]
---

# 温度与采样：输出更稳定，为什么仍可能稳定地答错

学习入口：把[温度](../../glossary/ai.md#ai.sampling)降低，回答格式更一致了，为什么事实错误没有消失？解码决定怎样从模型给出的候选分布选输出，不直接验证候选是否符合现实。

前置：[Token与上下文](tokens-context-and-memory.md)。本文解释一般自回归生成机制，参照Transformers与研究论文；服务是否支持某个参数、范围和组合需逐项核对。数字为纸面概率，没有加载模型或运行解码器。

## 下一token分布与整段质量是不同对象

模型根据已有前缀产生候选[token](../../glossary/ai.md#ai.context)的分数，解码过程再处理并选择下一项。选出的token改变后续前缀，因此一次早期选择可以改变整段输出。

较高概率不等于事实正确或满足业务规则。词表token也不一定是完整词语；某位置的置信分布不能直接当作整段回答正确概率。

## 温度改变分布的集中程度

一般模型对logit应用 `softmax(z/T)`，这里要求 `T>0`。等价地，在其他处理保持不变时，可以把T=1时原概率的 `1/T` 次方重新归一化。正温度不改变logit排序，但会改变抽样时各候选的相对机会。

教学分布A/B/C为0.5/0.3/0.2。当T=0.5时，平方得到0.25/0.09/0.04，总和0.38，归一化约为0.6579/0.2368/0.1053。A更集中，并没有因此变得更真实。

[Transformers生成工具](https://huggingface.co/docs/transformers/main/en/internal/generation_utils)说明温度及候选过滤。T=0不适用于上述除法；有些API以特殊值表示贪心等行为，有些不接受，不能直接套用这条公式或假定所有模型都支持同一设置。

## top-k与top-p过滤不同的集合

`top-k`按候选数量保留最高的k项；top-p通常按概率从高到低，保留累计质量达到阈值的较小候选集合，再从中选择。具体边界、最低保留数量和处理顺序依实现。

仍用原分布0.5/0.3/0.2：top-p=0.7需保留A和B，总质量0.8；在保留集合中重新归一化为0.625/0.375。它不是“保留70%的候选数量”。本例 `top-k=2` 恰好得到相同集合，不说明两种方法一般等价。

[Holtzman等人的原论文](https://arxiv.org/abs/1904.09751)研究开放式生成退化并提出nucleus sampling。这里借用候选截断思想，不复现论文实验，也不把某个解码方法视为所有任务的最优选择。

## 贪心、低温度和固定种子有不同承诺

贪心按当前分数选最高候选；低正温度仍可能抽到其他候选。随机种子约束随机数过程，但模型版本、输入、硬件、[并行](../../glossary/systems.md#systems.concurrency)计算和库配置也可能改变结果。

[PyTorch可复现性说明](https://docs.pytorch.org/docs/2.14/notes/randomness.html)讨论跨版本/平台及确定性算法的限制。即使一次运行完全可复现，也只是重复相同过程，不证明输出正确；供应商服务还需核对其实际公开承诺。

## 参数调节需要与目标和评估相连

创意多样性、结构稳定、任务正确率和[延迟](../../glossary/performance.md#performance.latency-throughput)/成本可能有不同目标。约束输出语法、提供可信资料和验证业务结果，分别解决不同问题，不能全归结为调温度。

比较时固定任务集、模型和上下文等条件，记录多次运行及失败类型。不要只选一条看起来更好的回答；真实效果需要实测，本篇未生成任何回答或给出通用参数推荐。

## 自检

1. 下一token概率为什么不能直接当作回答正确概率？
2. 原分布0.5/0.3/0.2在T=0.5时约变成什么？
3. top-p=0.7为什么保留A/B，归一化后又是多少？
4. 贪心、低正温度和固定随机种子分别能约束什么？
5. 为什么稳定输出、可复现和业务正确必须分别验证？

## 来源与核查

2026-10-27 核查Transformers生成工具、Holtzman论文摘要/方法及PyTorch2.14可复现性说明。Transformers main为滚动文档，本文不提供其完整运行配置。本文为source-checked；未加载模型、运行采样、测量概率或检验跨服务复现性。
