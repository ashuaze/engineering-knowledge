---
id: "kb-reliability-chaos-experiments"
title: "混沌工程与受控故障：注入成功，为什么还不能宣布系统可靠"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "用可反驳的稳态假设组织故障实验，区分作用确认、用户结果、影响限制、停止注入与业务恢复。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-reliability-slos", "kb-reliability-fault-domains-recovery"]
related: ["kb-reliability-red-use", "kb-reliability-availability-models", "kb-reliability-incident-response", "kb-performance-capacity-autoscaling", "kb-api-graceful-shutdown"]
tags: ["chaos-engineering", "hypothesis", "blast-radius", "recovery"]
---

# 混沌工程与受控故障：注入成功，为什么还不能宣布系统可靠

学习入口：工具显示实例已停止，剩余实例也存活，为什么仍不知道系统是否扛住了故障？需要先提出系统行为假设，再确认故障真正作用到目标，并检查用户结果与恢复。

前置：[服务目标](slis-slos-and-error-budgets.md)、[故障域与恢复](failure-domains-redundancy-and-recovery.md)。本文仅设计纸面实验，不包含执行命令，没有停止[进程](../../glossary/systems.md#systems.execution-units)、改变网络/云资源、注入故障或接触真实用户流量。

## 实验从假设和观测开始

[Principles of Chaos Engineering](https://principlesofchaos.org/)从可测稳态、控制/实验比较、现实扰动和试图推翻假设组织实验。稳态是负载与环境条件下的可接受输出，不是所有曲线保持不变。

“停止一个实例”是动作；“在给定负载下失去一个实例后，合格请求和恢复仍满足约定”才是待检验假设。检查内部存活有帮助，但不能替代正确结果、时长和状态完整性。

## 一张实验卡明确问题与边界

| 要素 | 教学设计示例 |
| --- | --- |
| 适用条件 | 固定版本/依赖、代表性请求，先确认基线满足目标 |
| 假设 | 失去一个服务实例，其他容量和恢复路径仍能满足本例目标 |
| 扰动 | 仅指定实验组中的一个实例，限时且可确认作用 |
| 观测 | 用户结果、完成时长、在途/积压、剩余容量、数据与外部效果 |
| 比较 | 明确基线和对照，记录共享依赖及其他[并行](../../glossary/systems.md#systems.concurrency)变化 |
| 停止与恢复 | 超阈值/关键检查失败/失去观测时停止后续注入并启动停止/撤除流程，确认业务恢复 |

这些是教学安排，不是可直接用于某个环境的参数。对照组也可能被共同数据库、[重试](../../glossary/api.md#api.retries)或流量迁移影响；没有独立性时要报告污染，不能仅凭两条曲线变化断言原因。

## 作用确认与系统结果是两种证据

目标实例是否真的受到扰动、持续多久、有无选错对象，属于作用确认。若权限不足而动作没有生效，即使业务全绿，也没有验证“失去实例仍满足目标”。

反过来，动作成功只证明发生了扰动。剩余实例可能正在耗尽连接或积压任务，需要同时检查目标、后续恢复及观测覆盖。随机选目标可以探索未知条件，也需要保留版本、选择、时序和动作记录。

## 停止条件需要能被可靠观测和执行

教学设定每次评估滚动60秒中的合格结果，若不合格比例达到0.5%，或关键状态检查失败，则请求停止实验并进入恢复核对。某次窗口有10000项、40项不合格，比例为0.4%；达到50项才是该分母下的0.5%。

0.4%只说明这一条阈值未到，不证明[延迟](../../glossary/performance.md#performance.latency-throughput)、数据和其他条件满足目标。该设定不是生产阈值建议；若结果尚未完成、观测延迟或分母很小，需在实验设计中说明怎样收敛，不能等待失效仪表证明安全。

[AWS FIS stop conditions](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html)以 CloudWatch alarm 触发停止作为具体平台机制。它不是所有工具共同的接口；采样、告警、停止请求和动作响应均可能有延迟，应在所用平台上独立验证。

## 停止注入以后仍要恢复业务

撤除网络扰动不保证旧连接立即重建；停止动作不撤销已经提交的写入、重复任务或外部付款。需要确认在途工作、积压、数据、权限及依赖已恢复，而不只看实验工具进入 stopped。

[Google SRE Testing for Reliability](https://sre.google/sre-book/testing-reliability/)讨论恢复工具和随机测试记录的证据限制。记录随机种子有帮助，但依赖、时序和真实环境不一定能完整重现；重新运行一次没有失败，也不能独自证明根因已修复。

## 把结果变成有范围的结论

报告具体版本、负载、目标、动作、时序、观测缺口与恢复结果；区分假设被支持、被反驳以及因扰动/观测失效而无结论。发现问题后形成可复现检查、改进责任和重新验证范围。

一次单实例实验不覆盖节点、区域、控制面或共同凭证失效。原则文档讨论了生产代表性，也要求限制影响范围；选择何种环境、怎样逐步扩大需有真实条件与能力，本篇只交付上述教学设计。

## 自检

1. 注入动作和可以被反驳的系统假设有什么区别？
2. 动作未生效但业务全绿，为什么不能验证假设？
3. 40/10000与50/10000各是多少？前者为什么不等于实验整体通过？
4. 停止注入后，为什么仍要核对连接、积压、数据和外部效果？
5. 一次实验结束后应保留什么，哪些结论仍不能推广？

## 来源与核查

2026-10-27 核查[混沌工程](../../glossary/reliability.md#reliability.chaos)原则、AWS FIS停止条件与Google SRE[可靠性](../../glossary/reliability.md#reliability.availability)测试章节。本文为 source-checked；未使用故障注入工具、接入告警、运行对照、测量停止延迟或验证业务恢复，不把实验计划当作演练结果。
