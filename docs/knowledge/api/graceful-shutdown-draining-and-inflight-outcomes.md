---
id: "kb-api-graceful-shutdown"
title: "优雅关闭与请求排空：停止接流为什么仍有请求进来"
kind: "concept"
domain: "api"
status: "evolving"
summary: "区分摘流传播、本地接纳、连接排空和业务完成，解释终止预算、GOAWAY、超期处置与不确定结果。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-http-pools", "kb-devops-declarative-health"]
related: ["kb-systems-signals-shutdown", "kb-api-idempotency", "kb-reliability-retry-budgets", "kb-devops-entry-discovery", "kb-devops-trusted-progressive-delivery"]
tags: ["graceful-shutdown", "draining", "deadlines", "goaway"]
---

# 优雅关闭与请求排空：停止接流为什么仍有请求进来

学习入口：实例已标为不就绪，为什么旧连接还在送请求？停止[进程](../../glossary/systems.md#systems.execution-units)以后，调用方报错是否说明写入没成功？需要分别管理流量传播、连接使用、在途工作与业务结果。

前置：[HTTP 连接池](../networking/http-reuse-pools-and-timeouts.md)、[声明式部署与健康探针](../devops/declarative-deployments-and-health-probes.md)。本文以普通长期运行服务为范围，参照 Kubernetes v1.36、[HTTP/2](../../glossary/networking.md#networking.http-versions) 和 [gRPC](../../glossary/api.md#api.styles) 的公开机制；时序和预算为教学设计，未摘流、发送信号或关闭真实服务。

## 摘流是传播过程，本地也需要接纳边界

| 工作 | 主要作用 | 不能单独保证 |
| --- | --- | --- |
| 宣告不再就绪 | 让发现/[负载均衡](../../glossary/networking.md#networking.load-balancer)逐步停止选择本实例 | 所有客户端立刻获知，旧连接全部停止 |
| 本地停止接纳新工作 | 在服务自身建立关闭边界 | 已接纳工作已经完成 |
| 连接/流排空 | 允许符合策略的在途工作结束，引导新工作改路 | 业务副作用一定未发生或已经确认 |
| 清理资源并退出 | 完成允许的收尾，释放本地资源 | 超期强杀后的外部状态自动回滚 |

Kubernetes 的[普通 Pod 终止流程](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)中，端点变化和节点关闭[并行](../../glossary/systems.md#systems.concurrency)推进；传播与实际代理使用仍需验证。不就绪不是全网同步屏障，固定等待几秒也不能证明所有旧引用已消失。

## 一个连接还可能承载多个请求或流

HTTP/1.1 复用和 HTTP/2 多流使“连接已存在”与“业务请求已接纳”不同。HTTP/2 的 [GOAWAY，RFC 9113 §6.8](https://www.rfc-editor.org/rfc/rfc9113.html#section-6.8)帮助对端判断连接收尾及部分流的处理范围，但仍须按帧语义、流编号和客户端行为判断，不能统一把连接关闭后的所有请求视为可安全重放。

[gRPC 的优雅关闭](https://grpc.io/docs/guides/server-graceful-stop/)允许在途 RPC 继续、拒绝新 RPC，并需要[超时](../../glossary/api.md#api.retries)后的强制关闭安排。具体函数、是否阻塞以及取消传播依语言实现；长流还需应用协议定义恢复位置与结束条件。

关闭监听端口不一定阻止现存连接送入新工作；只关闭现存连接，又可能提前打断已经接纳的请求。本地接纳状态、连接协议与入口传播要协同设计。

## 总预算包括关闭前的准备

教学假设终止总预算为 30 秒，各阶段在本例中串行：准备/预停 5 秒、排空最多 18 秒、清理最多 4 秒，则已分配 `5+18+4=27` 秒，保留 3 秒余量。余量是预算，不是证明所有工作一定能在期限内结束。

Kubernetes 的 `preStop` 通常消耗同一个终止宽限期，不能先睡 30 秒，再期待完整的 30 秒收尾时间。不同终止路径、sidecar 顺序和强制删除有额外规则；强制删除不承诺完成本例的预停、排空和清理时序，本篇不把普通流程推广到所有退出方式。

在期限到达之前，应明确不能完成的工作如何处理：拒绝尚未接纳的任务、停止领取新消息、保存可恢复位置、取消允许取消的计算，或留下持久待完成记录。无限等待与直接丢弃都不是由“优雅”二字自动决定的策略。

## 业务提交与响应交付分开确认

教学窗口：服务已提交订单，正在发送响应时进入强制终止。调用方看到断开，业务却可能成功。取消、[TCP](../../glossary/networking.md#networking.transport) 断开或容器退出不能据此证明数据库回滚；重试应沿用操作身份并核对结果，见[幂等性](idempotency.md)。

消费者也不能在实际处理完成前先提交消费位置，再把剩余工作留给即将退出的内存任务。可靠接纳、业务提交、完成位置和响应属于不同确认边界，应在关闭协议中明确。

## 验证关闭需要覆盖正常与超期路径

至少区分新连接、旧连接新请求、正在运行的写入、长流、后台任务和依赖很慢的情形。观察停止接纳时刻、最后业务提交、结果确认、强制终止及恢复位置；实例成功退出只证明进程结束，不证明用户没有看到不确定结果。本文没有执行这些实验。

## 自检

1. 为什么不就绪不能保证旧连接不再发送新请求？
2. 连接排空、本地停止接纳与业务完成有什么区别？
3. 30 秒预算分配 5/18/4 秒后还剩多少？preStop 是否另有完整宽限期？
4. 订单提交后响应中断，调用方能否自动认定失败并换 ID 重做？
5. 为什么只检查退出码不能证明[优雅关闭](../../glossary/api.md#api.shutdown)的业务效果？

## 来源与核查

2026-10-26 核查 Kubernetes v1.36 [Pod](../../glossary/devops.md#devops.k8s) 终止、RFC 9113 GOAWAY 与 gRPC graceful shutdown 说明。本文为 source-checked 概念文章；未验证特定框架、代理、信号/取消传播、长流、超期强杀或业务恢复。
