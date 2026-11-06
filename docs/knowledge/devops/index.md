<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# Linux、云与交付

建议优先级：P1。目标：让环境、构建、发布与恢复可重复。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

发布回滚了应用，为什么数据库仍可能不兼容？

## 已有正文

- [可信制品与渐进发布：签名通过为什么仍要验证线上行为](artifact-provenance-verification-and-progressive-delivery.md)：连接[制品摘要](../../glossary/devops.md#devops.provenance)、受信构建来源和发布策略，区分内容身份、来源证明、流量暴露、观察与业务回退。
- [构建、部署与回滚：为什么换回旧程序还不够](build-deploy-rollback.md)：区分制品、配置、数据契约与流量状态，理解[持续交付](../../glossary/devops.md#devops.cicd)和可回滚的条件。
- [云网络与访问边界：私有子网为什么不等于应用可信](cloud-networks-subnets-routes-and-security-groups.md)：以 AWS [VPC](../../glossary/devops.md#devops.cloud-network) 为具体参照，区分[地址前缀](../../glossary/networking.md#networking.ip-prefix)、路由、互联网/[NAT](../../glossary/networking.md#networking.nat) 出口、安全组与网络 ACL，解释可达性和应用身份的不同边界。
- [声明式部署与健康探针：实例存活为什么仍不能接流量](declarative-deployments-and-health-probes.md)：用 Kubernetes [控制循环](../../glossary/devops.md#devops.k8s)区分期望状态、运行状态和用户结果，说明滚动替换、三类探针及[优雅终止](../../glossary/reliability.md#reliability.probes)的边界。
- [IaC 与状态漂移：代码没变，为什么计划仍要修改资源](iac-state-drift-and-change-plans.md)：以 [Terraform](../../glossary/devops.md#devops.iac) 区分配置、状态记录与远端观测，解释计划、漂移、锁、导入、敏感数据和部分失败后的协调责任。
- [镜像、容器与资源隔离：同一镜像为什么仍表现不同](images-containers-and-resource-isolation.md)：区分[镜像](../../glossary/devops.md#devops.containers)内容与运行实例，解释标签和摘要、Linux [命名空间](../../glossary/devops.md#devops.isolation)与 cgroup、可写层和挂载，以及资源限制的保证边界。
- [集群入口与服务发现：域名能解析为什么请求仍到不了服务](ingress-gateway-api-service-discovery-and-endpoints.md)：区分 [DNS](../../glossary/networking.md#networking.dns)、Service、端点、[Ingress](../../glossary/devops.md#devops.entry)/Gateway 声明与数据平面，说明控制器、就绪、跨命名空间引用和旧连接。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [Linux Process / Signal / Permission](../../glossary/devops.md#devops.linux) | [进程](../../glossary/systems.md#systems.execution-units)生命周期、信号与访问权限。 |
| [Namespace / cgroups](../../glossary/devops.md#devops.isolation) | 资源视图隔离和用量限制。 |
| [Image / Container](../../glossary/devops.md#devops.containers) | 文件系统与配置模板及其运行实例。 |
| [Pod / Deployment / Service](../../glossary/devops.md#devops.k8s) | 工作单元、声明式副本管理与服务访问。 |
| [Ingress / Gateway API](../../glossary/devops.md#devops.entry) | 集群入口路由与流量管理接口。 |
| [Service Discovery](../../glossary/devops.md#devops.discovery) | 通过名称或逻辑身份查找服务地址或候选端点信息。 |
| [VPC / Subnet / Security Group](../../glossary/devops.md#devops.cloud-network) | 云网络边界和访问控制。 |
| [IaC / Terraform](../../glossary/devops.md#devops.iac) | 以版本化声明管理基础设施。 |
| [CI / CD](../../glossary/devops.md#devops.cicd) | 持续集成、交付或自动部署。 |
| [Rolling / Blue-Green / Canary](../../glossary/devops.md#devops.rollout) | 不同发布替换和流量迁移策略。 |
| [Feature Flag](../../glossary/devops.md#devops.flags) | 按条件启用行为并管理开关生命周期。 |
| [Immutable Infrastructure](../../glossary/devops.md#devops.immutable) | 通过替换实例交付新配置。 |
| [Autoscaling / HPA](../../glossary/devops.md#devops.autoscaling) | 基于观测信号调整资源或副本数。 |
| [Multi-AZ / Multi-Region](../../glossary/devops.md#devops.regions) | 跨可用区与跨地域部署。 |
| [Artifact Digest / Build Provenance](../../glossary/devops.md#devops.provenance) | 绑定具体产物内容、受信构建者、源码来源及构建参数的验证信息。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
