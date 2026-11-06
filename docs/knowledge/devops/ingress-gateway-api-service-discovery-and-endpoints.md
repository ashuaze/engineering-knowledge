---
id: "kb-devops-entry-discovery"
title: "集群入口与服务发现：域名能解析为什么请求仍到不了服务"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "区分 DNS、Service、端点、Ingress/Gateway 声明与数据平面，说明控制器、就绪、跨命名空间引用和旧连接。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-devops-declarative-health", "kb-networking-dns-caching", "kb-networking-nat-proxy-lb"]
related: ["kb-api-styles-gateway", "kb-api-graceful-shutdown", "kb-devops-cloud-network", "kb-security-trust-threat-models"]
tags: ["ingress", "gateway-api", "service-discovery", "endpoints"]
---

# 集群入口与服务发现：域名能解析为什么请求仍到不了服务

学习入口：服务名字已解析、路由对象也已创建，为什么仍出现无后端、404 或超时？要逐步确认名字、规则、实现、端点与实际连接，而非把一次 API 接受当作整条链路已通。

前置：[声明式部署](declarative-deployments-and-health-probes.md)、[DNS](../networking/dns-caching-and-address-selection.md)、[代理与负载均衡](../networking/nat-proxies-and-l4-l7-load-balancing.md)。本文使用 Kubernetes v1.36 普通 [Service](../../glossary/devops.md#devops.k8s)/[DNS](../../glossary/networking.md#networking.dns) 与 [Gateway API](../../glossary/devops.md#devops.entry) 的公开模型，不给出特定控制器安装或路由配置。所有对象关系为纸面设计，没有创建集群资源或发送请求。

## 名字、选择和转发不是同一个对象

| 层次 | 解决什么 | 尚不能证明 |
| --- | --- | --- |
| DNS / [服务发现](../../glossary/devops.md#devops.discovery) | 以名字找到相应服务地址或端点信息 | 后端仍就绪、端口/[TLS](../../glossary/networking.md#networking.tls)/权限正确 |
| Service 与 EndpointSlice | 组织服务访问与候选后端 | 每个代理已使用最新列表，旧连接已迁移 |
| Ingress / Gateway 路由声明 | 表达主机、路径、监听器及后端等意图 | 存在兼容实现并已完成数据平面配置 |
| 真实连接与应用处理 | 经过具体地址、端口和协议完成调用 | 所有其他来源、版本和业务动作也可用 |

普通 ClusterIP Service 的名字通常解析到服务地址；headless Service 可以通过 DNS 暴露后端地址。具体记录与就绪影响见 [Kubernetes v1.36 DNS](https://v1-36.docs.kubernetes.io/docs/concepts/services-networking/dns-pod-service/)。不能把两种模式都解释成“DNS 返回一个当前最健康的 Pod”。

## 服务发现还要处理缓存、就绪与连接寿命

带 selector 的 [Service](https://v1-36.docs.kubernetes.io/docs/concepts/services-networking/service/)通常通过相关端点表示后端集合，实际转发由集群网络实现。无 selector、外部名字等情形有不同机制；本文不把常见模型当成全部服务类型。

Pod 就绪变化后，控制器、端点消费者和代理逐步更新；客户端还可能缓存名字、地址或复用连接。列表删除某个实例，不代表所有已经建立的连接已结束。选择规则、拓扑策略与连接保持也会影响实际流向。

教学排查：域名解析到 Service 地址，但没有符合条件的就绪端点；这时反复修改 DNS 不能产生后端。另一种情形是端点正确，客户端仍走旧连接；需要区分发现结果与连接使用，见[连接池](../networking/http-reuse-pools-and-timeouts.md)。

## 路由 API 需要实现和状态反馈

Ingress 描述常见 HTTP(S) 入口规则，需匹配的控制器实现；Gateway API 进一步按职责组织 GatewayClass、Gateway 与各类 Route。资源模型和绑定关系见 [Gateway API Overview](https://gateway-api.sigs.k8s.io/docs/concepts/api-overview/)。

GatewayClass 关联实现与基础设施策略；Gateway 表达监听等配置；HTTPRoute 表达 HTTP 匹配和后端。对象能写入 API 不意味着控制器支持所有字段；应检查归属、监听器、路由绑定与后端引用的状态，并验证实际链路。

这套 API 不自动完成公网 DNS、证书发放、网络放通或业务鉴权，也不等同于[应用 API 网关](../api/api-styles-contracts-and-gateway-boundaries.md)的全部策略能力。

## 跨命名空间绑定与后端引用分别授权

Gateway 的 `allowedRoutes` 等机制限制哪些 Route 可以关联监听器；跨 Kubernetes `namespace` 引用后端或 Secret 等资源，还需目标资源所属空间中的 `ReferenceGrant` 等相应引用许可。不能以“Route 被允许接入”推出它可以引用任何其他空间的服务，见 [Gateway API Security](https://gateway-api.sigs.k8s.io/docs/concepts/security/)。

教学例：团队 A 的 HTTPRoute 获准绑定平台 Gateway，但其目标 Service 在团队 B。仍需目标拥有者允许相应跨空间引用，并满足 API 的具体约束；这种许可不是客户端访问 B 的业务[授权](../../glossary/security.md#security.identity)。控制资源的 [RBAC](../../glossary/security.md#security.access-control)、引用权限、网络策略与应用权限分别负责不同边界。

## 用一条请求串起证据

依次记录域名与缓存、到达的监听器、实际主机/路径匹配、绑定状态、端点/端口和应用结果。重写、TLS 终止或转发头可能改变下游看到的请求；不要用伪造来源头替代可信身份。

当请求失败时先定位是哪一段拒绝或没有推进，再核对该段控制状态与真实流量。升级控制器、改变路由和排空旧连接的效果，仍需按版本、来源与协议单独验证。

## 自检

1. ClusterIP 与 headless Service 的 DNS 结果通常有何不同？
2. 为什么端点更新不等于旧连接自动迁移？
3. Ingress/Gateway 对象创建成功，还需核对哪些实现和数据平面事实？
4. Route 获准绑定 Gateway，为何不能自动引用其他团队空间的一切资源？
5. 路由引用许可与客户端业务授权分别由谁负责？

## 来源与核查

2026-10-26 核查 Kubernetes v1.36 Service/DNS 与 Gateway API 模型/安全文档；后者为滚动资料，具体通道、控制器支持与版本需另核对。本文为 source-checked 概念文章，未安装控制器或验证解析、引用授权、转发、TLS 与摘流。
