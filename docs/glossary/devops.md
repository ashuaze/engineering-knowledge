<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# Linux、云与交付词汇表

本页解释 15 组术语，按[完整术语索引](../glossary.md#devops)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [Linux、云与交付文章](../knowledge/devops/index.md)

## 本页术语

- [Linux Process / Signal / Permission](#devops.linux)
- [Namespace / cgroups](#devops.isolation)
- [Image / Container](#devops.containers)
- [Pod / Deployment / Service](#devops.k8s)
- [Ingress / Gateway API](#devops.entry)
- [Service Discovery](#devops.discovery)
- [VPC / Subnet / Security Group](#devops.cloud-network)
- [IaC / Terraform](#devops.iac)
- [CI / CD](#devops.cicd)
- [Rolling / Blue-Green / Canary](#devops.rollout)
- [Feature Flag](#devops.flags)
- [Immutable Infrastructure](#devops.immutable)
- [Autoscaling / HPA](#devops.autoscaling)
- [Multi-AZ / Multi-Region](#devops.regions)
- [Artifact Digest / Build Provenance](#devops.provenance)

<a id="devops.linux"></a>

## Linux Process / Signal / Permission

**ID：** `devops.linux` · **建议优先级：** P1

**别名 / 检索词：** Linux Process、Signal、Permission、进程信号、文件权限

**简释：** 进程生命周期、信号与访问权限。

Linux 进程有生命周期与凭据，信号用于通知或请求控制，权限决定资源访问。信号处理有上下文限制，停止请求也不自动完成业务清理。

**例子：** 服务收到 SIGTERM 后停止接流并排空在途工作，仍需受关闭期限约束。

**深入阅读：** [Linux 信号、取消与退出：收到停止请求后由谁完成清理](../knowledge/systems/signals-cancellation-and-shutdown.md)

<a id="devops.isolation"></a>

## Namespace / cgroups

**ID：** `devops.isolation` · **建议优先级：** P1

**别名 / 检索词：** Namespace、cgroups、cgroup v2、资源隔离、命名空间、控制组

**简释：** 资源视图隔离和用量限制。

Namespace 改变进程可见的资源视图，cgroups 对资源使用实施计量与控制。二者不等价于完整安全边界，容器仍依赖内核及其他隔离机制。

**例子：** 进程看到独立 PID 视图，并不说明它拥有独立内核或无限 CPU。

**深入阅读：** [镜像、容器与资源隔离：同一镜像为什么仍表现不同](../knowledge/devops/images-containers-and-resource-isolation.md)

<a id="devops.containers"></a>

## Image / Container

**ID：** `devops.containers` · **建议优先级：** P1

**别名 / 检索词：** Image、Container、镜像、容器

**简释：** 文件系统与配置模板及其运行实例。

镜像描述分层文件系统和运行配置，容器是以其为输入的运行实例。可写层、挂载与运行参数会影响实际状态，持久数据需明确外置与备份。

**例子：** 相同镜像在不同挂载和环境配置下，仍可能表现出不同行为。

**深入阅读：** [镜像、容器与资源隔离：同一镜像为什么仍表现不同](../knowledge/devops/images-containers-and-resource-isolation.md)

<a id="devops.k8s"></a>

## Pod / Deployment / Service

**ID：** `devops.k8s` · **建议优先级：** P1

**别名 / 检索词：** Pod、Deployment、Service、Reconciliation、Desired State、声明式部署、控制循环

**简释：** 工作单元、声明式副本管理与服务访问。

Pod 是 Kubernetes 的基本工作单元，Deployment 协调副本更新，Service 提供稳定访问抽象。控制器持续使实际状态接近期望状态，过程不是瞬时事务。

**例子：** 更新 Deployment 后，新旧 Pod 可能在一段时间内同时运行。

**深入阅读：** [声明式部署与健康探针：实例存活为什么仍不能接流量](../knowledge/devops/declarative-deployments-and-health-probes.md)

<a id="devops.entry"></a>

## Ingress / Gateway API

**ID：** `devops.entry` · **建议优先级：** P1

**别名 / 检索词：** Ingress、Gateway API、集群入口

**简释：** 集群入口路由与流量管理接口。

Ingress与Gateway API表达入口路由意图，控制器实现转发。监听器允许Route绑定和目标拥有者允许跨命名空间引用是两道许可，均不替代业务鉴权；需核对实现、TLS与字段支持。

**例子：** 同一条路径路由在不同控制器上的扩展配置不一定可移植。

**深入阅读：** [集群入口与服务发现：域名能解析为什么请求仍到不了服务](../knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md)

<a id="devops.discovery"></a>

## Service Discovery

**ID：** `devops.discovery` · **建议优先级：** P1

**别名 / 检索词：** Service Discovery、服务发现

**简释：** 通过名称或逻辑身份查找服务地址或候选端点信息。

服务发现将名称或逻辑身份映射到服务地址或候选端点，可通过DNS、注册中心或平台接口实现。普通ClusterIP与headless返回的信息不同；缓存和健康传播有延迟，发现结果不保证即时可用，客户端仍需处理连接失败。

**例子：** 实例已被摘除时，客户端缓存的旧地址可能暂时继续被尝试。

**深入阅读：** [集群入口与服务发现：域名能解析为什么请求仍到不了服务](../knowledge/devops/ingress-gateway-api-service-discovery-and-endpoints.md)

<a id="devops.cloud-network"></a>

## VPC / Subnet / Security Group

**ID：** `devops.cloud-network` · **建议优先级：** P1

**别名 / 检索词：** VPC、Subnet、Security Group、云私有网络、子网、安全组

**简释：** 云网络边界和访问控制。

VPC划逻辑网络、子网划地址范围、路由选择下一跳，过滤规则另约束流量。AWS例中安全组有状态、网络ACL无状态；私网和可达性都不替代应用身份与对象权限，其他平台需分别核对。

**例子：** 服务位于同一 VPC 不代表端口必然可达，还需检查路由与安全规则。

**深入阅读：** [云网络与访问边界：私有子网为什么不等于应用可信](../knowledge/devops/cloud-networks-subnets-routes-and-security-groups.md)

<a id="devops.iac"></a>

## IaC / Terraform

**ID：** `devops.iac` · **建议优先级：** P1

**别名 / 检索词：** IaC、Terraform、基础设施即代码

**简释：** 以版本化声明管理基础设施。

IaC 以版本化声明管理基础设施，Terraform 是实现工具之一。应区分配置、状态绑定和远端观测，再审查计划、漂移归属、锁及敏感数据；刷新记录不自动改变声明或资源。

**例子：** 修改资源名称可能被提供方解释为替换，不能只按文本差异判断影响。

**深入阅读：** [IaC 与状态漂移：代码没变，为什么计划仍要修改资源](../knowledge/devops/iac-state-drift-and-change-plans.md)

<a id="devops.cicd"></a>

## CI / CD

**ID：** `devops.cicd` · **建议优先级：** P1

**别名 / 检索词：** CI、CD、持续集成、持续交付、持续部署

**简释：** 持续集成、交付或自动部署。

CI 通过频繁集成和自动检查缩短反馈；CD 可指持续交付或持续部署，是否自动进入生产需明确。制品来源、环境配置和审批条件构成交付链。

**例子：** 同一经过验证的制品逐级推广，可减少重新构建带来的差异。

**深入阅读：** [构建、部署与回滚：为什么换回旧程序还不够](../knowledge/devops/build-deploy-rollback.md) · [可信制品与渐进发布：签名通过为什么仍要验证线上行为](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md)

<a id="devops.rollout"></a>

## Rolling / Blue-Green / Canary

**ID：** `devops.rollout` · **建议优先级：** P1

**别名 / 检索词：** Rolling、Blue-Green、Canary、滚动发布、蓝绿发布、金丝雀发布

**简释：** 不同发布替换和流量迁移策略。

滚动逐步替换实例，蓝绿切入口，金丝雀逐步暴露部分请求/用户；需观测和停止条件。副本比例不保证精确请求比例，换回旧程序不撤销已提交数据及外部效果。

**例子：** 先让小比例用户使用新版本，观察业务错误与尾延迟再扩大流量。

**深入阅读：** [构建、部署与回滚：为什么换回旧程序还不够](../knowledge/devops/build-deploy-rollback.md) · [可信制品与渐进发布：签名通过为什么仍要验证线上行为](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md)

<a id="devops.flags"></a>

## Feature Flag

**ID：** `devops.flags` · **建议优先级：** P1

**别名 / 检索词：** Feature Flag、特性开关、功能开关

**简释：** 按条件启用行为并管理开关生命周期。

功能开关按配置与上下文选择已部署代码的行为。需管理默认值、权限、观测和清理；关闭开关不能自动撤销数据与外部动作，也不能代替服务端访问控制。

**例子：** 新计价逻辑先只对测试租户启用，确认后再扩大并移除旧分支。

**深入阅读：** [主干开发与功能开关：代码已合并，为什么功能还不能开放](../knowledge/engineering/trunk-based-development-and-feature-flags.md) · [构建、部署与回滚：为什么换回旧程序还不够](../knowledge/devops/build-deploy-rollback.md)

<a id="devops.immutable"></a>

## Immutable Infrastructure

**ID：** `devops.immutable` · **建议优先级：** P1

**别名 / 检索词：** Immutable Infrastructure、不可变基础设施

**简释：** 通过替换实例交付新配置。

不可变基础设施以替换实例交付变更，减少手工修补造成的漂移。持久数据与外部状态仍需独立管理，替换过程要验证健康和兼容。

**例子：** 修复系统依赖后构建新镜像并替换实例，而非逐台在线修改。

**深入阅读：** [声明式部署与健康探针：实例存活为什么仍不能接流量](../knowledge/devops/declarative-deployments-and-health-probes.md)

<a id="devops.autoscaling"></a>

## Autoscaling / HPA

**ID：** `devops.autoscaling` · **建议优先级：** P1

**别名 / 检索词：** Autoscaling、HPA、自动扩缩容

**简释：** 基于观测信号调整资源或副本数。

HPA按观测建议副本，CPU利用百分比通常相对相应request；原始比例还受缺失指标、就绪、容忍及稳定规则影响。采样、调度和预热有延迟，期望数量不等于立即就绪能力。

**例子：** 流量突然暴涨而新实例尚未就绪时，需要靠现有余量与拒绝策略保护服务。

**深入阅读：** [容量规划与自动扩缩容：副本增加为什么不等于能力立即增加](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md)

<a id="devops.regions"></a>

## Multi-AZ / Multi-Region

**ID：** `devops.regions` · **建议优先级：** P1

**别名 / 检索词：** Multi-AZ、Multi-Region、多可用区、多地域

**简释：** 跨可用区与跨地域部署。

多可用区和多地域部署针对不同故障范围，并增加复制、路由和运营成本。地域分散不自动建立独立性，仍需检查共享控制面与数据依赖。

**例子：** 应用跨区但全部依赖单区数据库，仍可能因该区故障整体不可用。

**深入阅读：** [故障域、冗余与恢复目标：有副本为什么仍可能恢复不了](../knowledge/reliability/failure-domains-redundancy-and-recovery.md)

<a id="devops.provenance"></a>

## Artifact Digest / Build Provenance

**ID：** `devops.provenance` · **建议优先级：** P1

**别名 / 检索词：** Artifact Digest、Build Provenance、SLSA、制品摘要、构建来源证明

**简释：** 绑定具体产物内容、受信构建者、源码来源及构建参数的验证信息。

摘要标识内容，签名与身份条件连接声明者，构建来源证明连接产物、来源和构建过程。核验须按预先受控的信任根及期望策略执行；有效签名不自动证明许可、无漏洞或线上业务正确。

**例子：** 审批和部署关联同一摘要，并检查受信构建者、仓库、版本引用及参数；可变标签不能单独保证运行的就是已核验产物。

**深入阅读：** [可信制品与渐进发布：签名通过为什么仍要验证线上行为](../knowledge/devops/artifact-provenance-verification-and-progressive-delivery.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Kubernetes：工作负载、网络与控制器概念](https://kubernetes.io/docs/concepts/)
- [OpenFeature：开关评价与默认值](https://openfeature.dev/specification/sections/flag-evaluation/)
- [HashiCorp：Terraform 状态与绑定](https://developer.hashicorp.com/terraform/language/state)
- [Kubernetes v1.36 DNS](https://v1-36.docs.kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Service](https://v1-36.docs.kubernetes.io/docs/concepts/services-networking/service/)
- [Gateway API Overview](https://gateway-api.sigs.k8s.io/docs/concepts/api-overview/)
- [Gateway API Security](https://gateway-api.sigs.k8s.io/docs/concepts/security/)
- [Amazon VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [路由表](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
- [安全组](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [网络 ACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [SLSA v1.2 Build 验证](https://slsa.dev/spec/v1.2/verifying-artifacts)
- [Sigstore 验签说明](https://docs.sigstore.dev/cosign/verifying/verify/)
- [SLSA 的 provenance 定义](https://slsa.dev/spec/v1.2/provenance)
- [Kubernetes v1.36 Deployment](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Argo Rollouts 金丝雀说明](https://argo-rollouts.readthedocs.io/en/stable/features/canary/)
- [AWS：子网与路由分类](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
