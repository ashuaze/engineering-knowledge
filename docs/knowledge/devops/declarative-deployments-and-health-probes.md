---
id: "kb-devops-declarative-health"
title: "声明式部署与健康探针：实例存活为什么仍不能接流量"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "用 Kubernetes 控制循环区分期望状态、运行状态和用户结果，说明滚动替换、三类探针及优雅终止的边界。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-devops-delivery-lifecycle", "kb-devops-container-boundaries"]
related: ["kb-reliability-slos", "kb-reliability-failure-isolation", "kb-networking-http-pools", "kb-api-idempotency", "kb-reliability-fault-domains-recovery", "kb-devops-iac-state", "kb-api-graceful-shutdown", "kb-performance-capacity-autoscaling", "kb-devops-entry-discovery"]
tags: ["declarative", "deployment", "health-probe", "shutdown"]
---

# 声明式部署与健康探针：实例存活为什么仍不能接流量

学习入口：部署请求已经被接受，[进程](../../glossary/systems.md#systems.execution-units)也在运行，为什么用户仍看到错误？前置：[交付生命周期](build-deploy-rollback.md)与[镜像、容器和资源隔离](images-containers-and-resource-isolation.md)。本文以 Kubernetes v1.36 的普通长期运行服务为例，解释声明式控制、流量就绪与终止；流程和算例为纸面推演，没有执行集群部署。

退出阶段见[优雅关闭与请求排空](../api/graceful-shutdown-draining-and-inflight-outcomes.md)，期望副本与就绪能力见[容量规划与自动扩缩容](../performance/capacity-planning-scaling-and-autoscaling-feedback.md)，[服务发现](../../glossary/devops.md#devops.discovery)及入口传播见[集群入口与服务发现](ingress-gateway-api-service-discovery-and-endpoints.md)。

## 期望状态通过控制循环逐步落实

命令式操作常强调执行某一步；声明式接口描述希望系统处于什么状态。API 接受声明之后，还需控制器、调度器、节点和[运行时](../../glossary/runtime.md#runtime.virtual-machine)共同推进。控制器观察当前状态，比较期望，再执行或请求相应变化；成功接受声明不等于这些变化已经完成。[Kubernetes Controllers](https://v1-36.docs.kubernetes.io/docs/concepts/architecture/controller/)说明了[控制循环](../../glossary/devops.md#devops.k8s)模型。

```text
提交期望状态 → API 接受并保存
                 ↓
持续观察当前状态 → 比较差异 → 请求创建、替换或删除
                 ↑                    ↓
                 └────── 再观察执行结果 ──┘
```

调和（reconciliation）可能反复发生，并受到容量、权限、[镜像](../../glossary/devops.md#devops.containers)拉取和依赖[可用性](../../glossary/reliability.md#reliability.availability)限制。设计外部控制动作时要考虑重复观察与[重试](../../glossary/api.md#api.retries)，不能假设回调只执行一次；某个控制器也不负责整个业务的全部状态。

Kubernetes 中，Pod 是容器共同运行的工作单元，Deployment 管理适合其模型的副本与版本替换；典型带 selector 的 Service 提供相对稳定的访问入口，并通过相应端点关联实例。它们分别管理执行、期望副本和访问，不能用某个对象“存在”来代替另一个层次的验收。

[不可变基础设施](../../glossary/devops.md#devops.immutable)常通过创建和替换实例交付变更，以减少在旧实例上临时修改造成的漂移。这不表示所有运行状态都不可写；持久数据、配置来源和实例外依赖仍有各自的生命周期。声明式控制也不自动禁止手工修改，应明确哪些状态由谁管理以及偏离后如何处理。

## 部署状态与用户结果之间还有几层检查

| 已观察到的证据 | 可据此说明什么 | 仍不能自动说明什么 |
| --- | --- | --- |
| 声明被接受 | API 接受该次期望变更 | 实例已经调度或启动 |
| Pod 处于 Running 阶段 | 已绑定节点，所有容器已创建，且至少一个仍在运行或启动/重启中 | 所有容器就绪、所有依赖可用 |
| [readiness](../../glossary/reliability.md#reliability.probes) 满足 | 满足配置的流量就绪判断 | 所有代理已同步，真实业务一定正确 |
| Deployment 完成滚动更新 | 期望数量的副本均已更新到目标版本并可用，旧版本副本已退出活动副本集合 | 数据兼容、正确率和[延迟](../../glossary/performance.md#performance.latency-throughput)目标达成 |
| 关键用户旅程符合目标 | 在约定测量范围内结果合格 | 未覆盖路径和未来故障也都安全 |

Pod phase 是较粗的生命周期摘要，不能替代容器状态和条件；相关定义见 [Pod Lifecycle](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase)。进一步验收用户结果，需要[SLI/SLO](../reliability/slis-slos-and-error-budgets.md)和业务检查，而不是只读取一个健康端点。

Ready 与 Deployment 计数中的 Available 也有区别：minReadySeconds 可以要求新 Pod 在没有容器崩溃的情况下持续就绪一段时间，才计为可用。还需确认状态对应本次目标版本，而不是读取上一次更新的完成标识。定义见 [Deployment 完成条件](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/#complete-deployment)与 [Min Ready Seconds](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/#min-ready-seconds)。

## 滚动替换受容量与就绪条件共同约束

Deployment 的 RollingUpdate 策略以 Pod 副本计数：maxSurge 限定替换期间允许的额外副本量，maxUnavailable 约束期望副本中允许不可用的量，并结合就绪与可用性条件推进。约束适用于控制器的更新规则，不是现实环境永远不会额外故障的承诺。具体定义见 [Kubernetes v1.36 Rolling Update](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment)。

教学设定：期望 3 个副本，maxSurge=1、maxUnavailable=0，可调度资源足够，且没有其他故障。控制器可以先创建新副本，满足可用条件后再逐步缩减旧副本。如果没有容纳额外实例的资源，新版本可能无法推进；“不主动降低可用量”与“有能力创建新实例”是两项条件。

本例不能把 3+1 当作包括终止中对象在内的实际 Pod 数硬上限：旧 Pod 的终止可能仍在进行，额外占用资源。Pod 数也不是进程数，一个 Pod 本来就可能包含多个容器和进程。滚动窗口需要同时考虑启动、就绪等待、排空、配额和剩余承载能力。新旧版本之间的数据与协议兼容仍需在[交付与回滚设计](build-deploy-rollback.md)中验证。

进展超时可以产生 ProgressDeadlineExceeded 状态，原生 Deployment 不因此自动回滚；更高层发布系统可以根据该信号另行决策。规则见 [Failed Deployment](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/#failed-deployment)。流量分批、金丝雀评估和自动回退也需要各自的信号与实现，不能从“用了 Deployment”推导已经具备。

## 三类探针选择的是不同动作

| 探针 | 判断的问题 | 失败处理的主要方向 |
| --- | --- | --- |
| startup | 应用是否完成启动 | 连续失败达到阈值后终止该容器，后续受重启策略约束 |
| readiness | 当前是否适合接收常规服务流量 | 影响 Pod 就绪和匹配 Service 的流量候选，不因这一结果直接重启容器 |
| liveness | 是否进入需要重启恢复的状态 | 连续失败达到阈值后终止该容器，按适用策略处理重启 |

配置 startup probe 时，在它成功前不执行 liveness/readiness probe；启动完成后，另外两种才按配置工作。failureThreshold 计算连续失败，readiness 失败后的恢复还受连续成功阈值 successThreshold 影响；liveness/startup 的成功阈值必须为 1。一次失败不必然触发重启，本文也不把周期乘阈值当作所有情况下的精确动作时间。机制见 [Kubernetes v1.36 Probes](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/probes/)。

选择探测内容应从失败动作倒推。若共享数据库短暂变慢，所有实例都把它当作 liveness 失败而重启，数据库没有因此恢复，应用反而可能失去热缓存并重复初始化。readiness 也要谨慎：把所有可选依赖都设为必要条件，可能让全部实例同时退出流量；完全不检查必需能力，则可能继续接收无法处理的请求。按业务可降级能力设计，参见[熔断、隔离与降级](../reliability/circuit-breakers-isolation-and-degradation.md)。

探针本身应有明确成本与超时。健康端点返回成功，最多说明通过了它实现的检查；不能证明任意[授权](../../glossary/security.md#security.identity)、订单状态、依赖链或[尾延迟](../../glossary/performance.md#performance.percentiles)都满足要求。

## 优雅终止需要处理传播与在途工作

实例退出不是一个全网原子动作。Pod 终止过程中，节点开始关闭容器，控制平面也会调整端点的就绪信息；代理、客户端[连接池](../../glossary/api.md#api.pool)和在途请求各有传播与生命周期。不能假设 readiness 变为失败后，所有旧连接立即消失。

在通常终止流程中，preStop hook 先于相应停止信号执行，并占用同一终止宽限窗口；停止信号、容器顺序和最终强制终止还有配置及平台细节。生命周期规则见 [Pod Termination](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)。长时间 sleep 不是免费的额外排空时间，也不能单独证明流量已切完。

下面是应用需要落实的教学顺序，实际步骤可以重叠，不表示 Kubernetes 已自动完成：

```text
进入停止接纳状态，并使流量入口逐步移除该实例
→ 在预算内处理已有请求、连接、消费任务和后台写入
→ 保存明确的业务进度，释放资源，正常退出
→ 超出宽限的剩余工作按强制结束与结果未知处理
```

宽限时间需要覆盖实际工作，还要留出入口传播与清理成本；无限等待会[阻塞](../../glossary/systems.md#systems.blocking)替换，过短则会切断在途请求。HTTP 连接与响应体的责任见[连接池与生命周期](../networking/http-reuse-pools-and-timeouts.md)。即使连接被切断，服务端修改也可能已经提交；重试仍要遵守[幂等契约](../api/idempotency.md)。

声明与实际资源的差异如何被观察和处理，见[IaC 与状态漂移](iac-state-drift-and-change-plans.md)；[Terraform](../../glossary/devops.md#devops.iac) 的计划/执行与持续控制循环应分别理解。

## 自检与验证范围

为一个启动较慢的服务写出：启动完成证据、接流量条件、需要重启的故障、停止接纳和在途请求的处置。再推演新实例始终不就绪、依赖整体变慢、旧实例[长连接](../../glossary/networking.md#networking.keepalive)未退出、成功响应丢失四种情形，分别指出谁有权触发什么动作。

2026-10-20 核查 Kubernetes v1.36 控制器、Deployment、Pod 和探针文档，状态为 source-checked。未运行集群、探针阈值、滚动替换、端点传播或优雅停机实验；未把声明接受、控制器完成和业务目标达成混为同一证据。跨[故障域](../../glossary/reliability.md#reliability.fault-domains)与完整恢复的目标见[故障域、冗余与恢复目标](../reliability/failure-domains-redundancy-and-recovery.md)。
