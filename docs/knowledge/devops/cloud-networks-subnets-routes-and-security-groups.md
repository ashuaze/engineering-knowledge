---
id: "kb-devops-cloud-network"
title: "云网络与访问边界：私有子网为什么不等于应用可信"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "以 AWS VPC 为具体参照，区分地址前缀、路由、互联网/NAT 出口、安全组与网络 ACL，解释可达性和应用身份的不同边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-ip-routing", "kb-networking-nat-proxy-lb"]
related: ["kb-devops-entry-discovery", "kb-security-trust-threat-models", "kb-security-ssrf", "kb-devops-iac-state"]
tags: ["vpc", "subnet", "routing", "security-group", "network-acl"]
---

# 云网络与访问边界：私有子网为什么不等于应用可信

学习入口：实例放进私有[子网](../../glossary/devops.md#devops.cloud-network)、入站仅开放 443，为什么仍不能保证服务可用或访问安全？网络地址、路由、过滤规则、连接状态和应用身份是不同层面的条件。

前置：[IP 与路由](../networking/network-layers-ip-subnets-and-routing.md)、[NAT 与代理](../networking/nat-proxies-and-l4-l7-load-balancing.md)。本文明确以 AWS VPC 的公开机制举例，不把同名能力推广到所有云。地址与访问路径为文档假设，没有创建 VPC、修改安全组或验证真实连接。

## VPC、子网和路由各表达什么

[Amazon VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)提供逻辑隔离的虚拟网络；子网使用相应地址范围并具有部署范围。地址空间互不重叠、具有路由和允许转发都需分别满足，不能把“在同一 VPC”当作应用互信。

| 对象 | 主要作用 | 不负责的保证 |
| --- | --- | --- |
| [地址前缀](../../glossary/networking.md#networking.ip-prefix)/子网 | 地址分配与网络归属 | 用户身份与对象权限 |
| [路由表](../../glossary/networking.md#networking.routing) | 给定目的地应走哪个目标 | 目标健康、过滤放通、回程可用 |
| Internet Gateway / [NAT](../../glossary/networking.md#networking.nat) 等出口 | 按具体机制连接外部网络 | 默认提供业务[认证](../../glossary/security.md#security.identity)或允许任意入站回调 |
| 安全组 / 网络 ACL | 在各自作用点约束网络流量 | 内容、SQL、租户与字段授权 |

[路由表](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)中的目标只是转发选择。连接还要满足实际地址映射、目标存在、返回路由与过滤条件；安全组允许也不会自动添加路由。

## 公有与私有是路径属性，不能只看实例名称

在 AWS 的常见 IPv4 模型中，[子网类型](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html#subnet-types)按路由区分，直接指向 Internet Gateway 是公有子网的分类条件；实例要经此直连互联网，还需公网地址等条件。仅把子网叫 `public`、仅给实例公网地址或仅开放端口，都不足以单独建立完整双向通信。

私有子网可经相应 NAT 出口发起外部连接，但不因能收到该连接的响应，就获得互联网任意主机主动连接它的能力。IPv6、私有端点、混合网络与不同 NAT 类型另有规则，不能机械沿用 IPv4 的所有假设。

教学排查：应用 A 的外部调用超时，应分别检查目的解析、出口路由、NAT/地址、过滤和回程；不能直接通过扩大入站来源来修复未知原因。

## 安全组与 ACL 的状态语义不同

AWS [安全组](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)对关联资源的网络接口等边界执行允许规则，并采用有状态机制；符合已允许连接的响应通常不需对称的反向规则。具体连接跟踪、例外流量与规则变化对现存连接的效果需依服务文档核对。

[网络 ACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)在子网边界提供无状态的规则评估，因此应分别考虑两个方向及相应端口。不能把安全组的响应行为套给 ACL，也不能认为增加一个更宽的安全组就可以覆盖 ACL 的拒绝。

某安全组允许客户端网段访问 [TCP](../../glossary/networking.md#networking.transport) 443，只表示符合这些条件的网络流量可通过相应检查。实例仍需监听正确地址/端口，[TLS](../../glossary/networking.md#networking.tls) 配置要正确，应用还需认证和授权。来源安全组引用也不是用户账号或工作负载完整身份的替代品。

## 网络隔离还要覆盖出口与实际调用者

内网某服务被滥用后，网络上可达的数据库或管理端点仍可能成为目标。限制不必要出口、使用当前身份与对象权限、隔离管理能力，分别减少不同风险；[最小权限](../../glossary/security.md#security.trust)与威胁假设见[信任边界](../security/trust-boundaries-least-privilege-and-threat-modeling.md)。

应用根据用户输入访问 URL 时，不能只因部署在私有网络就省略目标解析与出口校验，见[SSRF](../security/ssrf-url-resolution-and-egress-boundaries.md)。网络规则是防线的一部分，并不理解全部应用动作。

基础设施代码计划也不证明当前数据平面与声明一致；排查和变更后要核对实际关联、传播及流量结果，见[IaC 与漂移](iac-state-drift-and-change-plans.md)。本文没有执行这些操作。

## 自检

1. VPC、子网、路由与应用权限分别回答什么？
2. 为什么单有公网地址、路由或开放 443 都不足以证明完整访问？
3. NAT 发起连接并收到响应，为什么不等于允许任意入站回调？
4. 有状态安全组与无状态 ACL 对返回流量的判断有什么差异？
5. 私有网络部署为什么不能替代对象授权和 [SSRF](../../glossary/security.md#security.web-attacks) 出口边界？

## 来源与核查

2026-10-26 核查 AWS VPC、路由表、安全组和网络 ACL 官方文档，限定基础职责与状态语义，不覆盖所有联网类型与例外。本文为 source-checked 概念文章，未验证云资源配置、连接跟踪、规则传播或应用隔离效果。
