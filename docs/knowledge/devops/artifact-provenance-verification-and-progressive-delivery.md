---
id: "kb-devops-trusted-progressive-delivery"
title: "可信制品与渐进发布：签名通过为什么仍要验证线上行为"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "连接制品摘要、受信构建来源和发布策略，区分内容身份、来源证明、流量暴露、观察与业务回退。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-devops-delivery-lifecycle", "kb-devops-declarative-health"]
related: ["kb-security-trust-threat-models", "kb-api-graceful-shutdown", "kb-devops-entry-discovery", "kb-reliability-slos"]
tags: ["provenance", "artifact-digest", "progressive-delivery", "canary", "rollback"]
---

# 可信制品与渐进发布：签名通过为什么仍要验证线上行为

学习入口：流水线显示签名验证成功，为什么仍可能部署了错误分支，或在上线后出现业务回归？需要先说明“哪个内容由谁怎样构建”，再观察它在实际环境中的行为。

前置：[构建、部署与回滚](build-deploy-rollback.md)、[声明式部署与健康探针](declarative-deployments-and-health-probes.md)。本文核查 [SLSA](../../glossary/devops.md#devops.provenance) v1.2 Build 验证、Sigstore、Argo Rollouts 与 Kubernetes v1.36 文档；仅作概念解释和纸面推演，未签名、验签、部署或控制真实流量。

## 内容、来源与质量是三类证据

| 证据 | 回答的问题 | 仍不能自动推出 |
| --- | --- | --- |
| 内容摘要 | 取到的字节是否与指定内容一致 | 内容来自受信作者或没有漏洞 |
| 签名及身份核验 | 声明是否由被接受的身份作出、载荷是否完整 | 该身份符合本次构建策略、业务行为正确 |
| 构建来源证明 | 产物与哪些来源、构建者和参数关联 | 依赖清单完整、源码无恶意或运行无故障 |
| 测试及发布观察 | 特定环境、样本和窗口内表现怎样 | 未观察场景也满足全部目标 |

[镜像](../../glossary/devops.md#devops.containers)标签可能被重新指向；审批、扫描、来源核验与部署应关联同一摘要，避免检查一个产物、运行另一个产物。[SBOM](../../glossary/engineering.md#engineering.supply-chain) 记录组件清单，与“如何构建”和“是否符合要求”有不同用途；三者应关联，不能互相替代。

## 签名通过后，还要按受信策略检查来源

[SLSA v1.2 Build 验证](https://slsa.dev/spec/v1.2/verifying-artifacts)要求把来源证明与具体产物及预先配置的信任根关联，并核对构建身份、来源和参数期望。教学检查顺序为：

1. 从受控策略取得允许的构建者、签名身份/信任根及来源要求，不能直接相信产物随附的任意公钥。
2. 核验签名及相应身份条件；核对证明的 `subject` 摘要与待部署产物一致，证明类型符合预期。
3. 检查构建者、规范源码仓库、允许的版本引用及构建类型/外部参数。可信构建者也可能被要求构建未经批准的分支。
4. 保留验证结果与产物身份，防止核验后又按可变标签选择其他字节；策略及信任根变更也需治理。

[Sigstore 验签说明](https://docs.sigstore.dev/cosign/verifying/verify/)将基于身份的验证与预期证书身份、[OIDC](../../glossary/security.md#security.oauth) issuer 关联，并解释默认镜像摘要核对。具体命令和信任根依所用版本与流程配置，不能把“任意有效签名”当作组织许可。

[SLSA 的 provenance 定义](https://slsa.dev/spec/v1.2/provenance)区分各轨道的来源信息；这里讨论构建来源，并未评估平台达到哪个等级。信任构建平台是显式假设，来源证明也不等于代码安全审计。

## 发布策略控制替换与暴露

| 机制 | 主要控制 | 需要另行解决 |
| --- | --- | --- |
| 滚动更新 | 逐步替换实例、限制不可用与额外实例 | 版本混合兼容、业务观察和状态迁移 |
| 蓝绿切换 | 保留两套环境并切换入口 | 双份成本、现存连接和共享数据兼容 |
| [金丝雀发布](../../glossary/devops.md#devops.rollout) | 先暴露部分请求或用户，再决定扩大 | 分群偏差、观察窗口和停止条件 |
| [功能开关](../../glossary/devops.md#devops.flags) | 控制已部署代码中的能力暴露 | 开关组合、[授权](../../glossary/security.md#security.identity)、数据语义及清理 |

[Kubernetes v1.36 Deployment](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/)描述滚动替换及 `maxUnavailable`、`maxSurge`。实例就绪只通过已配置的检查，不证明支付、权限或后台处理等完整业务流程正确；[Deployment](../../glossary/devops.md#devops.k8s) 本身也不等于完整金丝雀分析系统。

[Argo Rollouts 金丝雀说明](https://argo-rollouts.readthedocs.io/en/stable/features/canary/)提供权重与暂停步骤；没有流量管理时，通过副本比例尽量近似权重。设置 10% 或运行一个新副本，不保证每个窗口实际正好有 10% 请求，更不保证[长连接](../../glossary/networking.md#networking.keepalive)、重请求或用户分布相同。

## 纸面观察：零错误样本不等于零风险

假设一个教学窗口恰有 2000 个请求，其中新版本得到 200 个、旧版本得到 1800 个；新版本观察到 0 次失败，旧版本 9 次：

```text
新版本观测失败比例 = 0 / 200 = 0%
旧版本观测失败比例 = 9 / 1800 = 0.5%
整体观测失败比例 = 9 / 2000 = 0.45%
```

这是人为给定的分配，不是权重设置的必然结果。0/200 不能证明真实失败概率为零，也不能仅凭这一个窗口认定新版本更好。需比较请求类型、用户范围、资源成本、[延迟](../../glossary/performance.md#performance.latency-throughput)、业务结果和足够的观察时间；只看整体平均值可能掩盖新版本少量用户的严重失败。

## 停止暴露不等于状态已经回退

事先定义扩大、暂停与撤回的信号，检查观测缺失时是否停止推进。撤回可能包含切断新流量、处理现存连接、排空在途请求和确认业务结果，见[优雅关闭](../api/graceful-shutdown-draining-and-inflight-outcomes.md)。

换回旧镜像不会撤销已提交的数据、已发消息或外部付款。数据库格式、[事件契约](../../glossary/messaging.md#messaging.event-contract)和功能开关都要考虑旧版本是否仍能读取与执行；存在不可逆效果时，需前滚修复或独立恢复方案。制品可信、替换完成与业务恢复分别留证。

## 自检

1. 摘要、签名、来源证明与 SBOM 分别回答什么？
2. 为什么受信构建者签出的产物仍需检查仓库、版本及构建参数？
3. 滚动、蓝绿、金丝雀和功能开关分别控制什么？
4. 2000 个请求的三个失败比例是多少？为什么不能宣布新版本零风险？
5. 为什么切回旧镜像不能自动撤销数据变更及外部付款？

## 来源与核查

2026-10-26 核查上述 SLSA v1.2、Sigstore、Argo Rollouts 与 Kubernetes v1.36 官方资料。本文为 source-checked；未执行制品构建/签名/策略验证、供应链评估、真实流量分配、统计显著性分析、滚动/蓝绿/金丝雀、功能开关或数据恢复实验。
