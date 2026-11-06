---
id: "kb-reliability-availability-models"
title: "可用性与可靠性：服务大部分时间在线，为什么长任务仍容易失败"
kind: "concept"
domain: "reliability"
status: "evolving"
summary: "区分某时刻可用、连续完成能力及恢复，说明时间型/事件型比例、观察窗口、均值与相关故障的限制。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-reliability-slos"]
related: ["kb-reliability-fault-domains-recovery", "kb-reliability-red-use", "kb-reliability-chaos-experiments", "kb-api-graceful-shutdown"]
tags: ["availability", "reliability", "repair", "measurement-window"]
---

# 可用性与可靠性：服务大部分时间在线，为什么长任务仍容易失败

学习入口：实例每次故障都很快重启，在线比例很高，为什么一个需要持续运行几小时的任务仍容易中断？是否能恢复服务，与是否能持续满足某段任务的要求，是不同问题。

前置：[SLI、SLO与错误预算](slis-slos-and-error-budgets.md)。本文解释服务与经典[可靠性](../../glossary/reliability.md#reliability.availability)模型的口径，数值为纸面观察输入；未测服务可用性、估计真实失效分布或执行故障恢复。

## 可用、持续工作与可恢复分别提问

| 概念视角 | 本文提问方式 | 必须补充的条件 |
| --- | --- | --- |
| 可用性 | 指定时刻或窗口内，要求的能力是否可获得 | 对谁、何种能力、测量边界 |
| 可靠性 | 给定条件与时间内，能否持续履行规定功能 | 任务时长、失败定义和环境 |
| 恢复/可维护性 | 失败后怎样恢复，需多久及什么资源 | 检测、修复、状态与业务验收 |

[NIST reliability 词条](https://csrc.nist.gov/glossary/term/reliability)强调规定条件和时间。在软件/SRE语境，“可靠性”也常作涵盖用户服务质量的上位词；不能只凭词名认定某个报告采用了同一个数学指标。

频繁短中断可以与较高在线比例并存，却破坏不中断运行的要求。若任务支持检查点、[幂等](../../glossary/api.md#api.idempotency)恢复并最终按期正确完成，它的失败定义又可能不同；应先声明任务契约。

## 时间型与请求型比例使用不同分母

教学时间窗口为6小时，即21600秒；按已定义的二元可用标准观察到两次各30秒中断，合计60秒，不计重叠：

```text
时间型观测可用比例 = (21600 - 60) / 21600 ≈ 99.7222%
```

另给同窗口的请求计数：10000个合格请求中9990个按声明标准成功，则请求型比例为99.9%。这是额外给定的数据，不能由60秒中断自动推出；请求在时间上的分布和受影响范围可能不均匀。

[Google SRE Embracing Risk](https://sre.google/sre-book/embracing-risk/)解释了时间型与请求成功比例的取舍。分布式服务常部分可用，单台实例在线或某地域全绿，都不能代替所有用户的结果。

还需分开路由、租户与关键操作观察。总体比例可能掩盖某小群体持续失败；反之，维护窗口是否排除需按明确约定，不能为了提高数字临时改变分母。

## 连续存活概率不能直接拿在线比例代替

[NIST 的 survival function](https://www.itl.nist.gov/div898/handbook/apr/section1/apr122.htm)用 `R(t)=P(T>t)` 描述一个单元首次失效时间超过t的概率。它基于指定总体与模型，不是拿一次在线比例直接预测任意持续时间的任务成功率。

前面的6小时历史有两次中断，只能描述该观测记录；要估计未来连续工作概率，还需失败样本、条件、任务恢复语义和模型假设。这里不假定软件失效独立、恒定发生，也不套用特定分布。

## 故障与恢复的均值各有范围

MTBF涉及故障之间的时间及统计总体，MTTR可能指修复、恢复或其他团队约定的时间。必须说明起止、计入哪些故障及窗口；同名缩写不保证口径相同。

平均恢复快不代表每次都快，长尾和某次严重中断仍可能违反用户要求；一个没有观察到故障的实例也不足以证明总体永不失败。把经典长期平均公式用于软件服务时，应先检查稳态、修复过程和故障独立性等适用条件，本文未用它们估计实际能力。

## 恢复在线还需要正确状态

[进程](../../glossary/systems.md#systems.execution-units)启动、路由切回和探针成功只提供局部证据。若丢失已确认写入、任务重复执行或返回过期权限数据，就需按业务正确性和恢复目标处理；不能仅凭返回200宣布恢复完成。

[冗余](../../glossary/reliability.md#reliability.fault-domains)还要核对共同依赖、剩余容量与恢复路径，见[故障域与恢复目标](failure-domains-redundancy-and-recovery.md)。报告应同时保留统计口径和具体用户影响，避免一个百分比掩盖关键差异。

## 自检

1. 高在线比例为什么可以与持续作业频繁中断同时出现？
2. 6小时、两次30秒中断得到什么比例？9990/10000又是什么口径？
3. 为什么不能从60秒中断推导请求失败比例？
4. `R(t)`、MTBF与MTTR各需声明什么条件？
5. 进程恢复后，还要怎样确认业务状态及用户结果？

## 来源与核查

2026-10-27 核查 NIST reliability 词条、可靠性/存活函数说明与 Google SRE 风险章节。本文为 source-checked；未估计实际可靠性参数、采集可用率、检验分布/独立性或执行持续作业及恢复实验。
