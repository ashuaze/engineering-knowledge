---
id: "kb-devops-container-boundaries"
title: "镜像、容器与资源隔离：同一镜像为什么仍表现不同"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "区分镜像内容与运行实例，解释标签和摘要、Linux 命名空间与 cgroup、可写层和挂载，以及资源限制的保证边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-devops-delivery-lifecycle", "kb-systems-execution-units"]
related: ["kb-devops-declarative-health", "kb-reliability-fault-domains-recovery", "kb-performance-backpressure", "kb-runtime-gc"]
tags: ["image", "container", "namespace", "cgroup"]
---

# 镜像、容器与资源隔离：同一镜像为什么仍表现不同

学习入口：测试与生产使用同一个[镜像](../../glossary/devops.md#devops.containers)，为什么生产仍会变慢、缺文件或被终止？前置：[构建、部署与回滚](build-deploy-rollback.md)与[进程](../../glossary/systems.md#systems.execution-units)概念。本文限定共享 Linux 内核的进程型容器；Kubernetes 以 v1.36 文档为参照，资源机制以 [cgroup v2](../../glossary/devops.md#devops.isolation) 为例。表格和故障情形为教学分析，未构建或运行容器。

## 镜像固定内容，容器形成一次运行

镜像提供用于创建容器的文件系统内容和配置；容器是[运行时](../../glossary/runtime.md#runtime.virtual-machine)创建的隔离执行环境，其中运行进程。镜像不是正在执行的进程，也不包含运行后所有外部状态。普通 Linux 容器共享其所在宿主环境的内核，虚拟机有自己的客户机内核；容器也可以运行在虚拟机内。[Docker 容器说明](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/#containers-versus-virtual-machines-vms)解释了这层关系。

“同一个镜像”只固定了部分输入。启动参数、环境配置、挂载数据、服务身份、宿主内核、平台与依赖服务仍会改变行为。桌面系统中的 Linux 容器还可能实际运行在一层 Linux 虚拟机里，不能直接把客户端电脑的内核当作容器所在内核。

| 需要记录的输入 | 教学反例 |
| --- | --- |
| 镜像的确定身份及目标平台 | 同名 tag 指向已变，或不同架构选择不同平台镜像 |
| 参数、配置和凭证版本 | 程序相同，但开启了不同路径或访问不同数据库 |
| 文件系统挂载与权限 | 外部挂载覆盖镜像中的目录，或运行用户不能读取文件 |
| 内核、运行时与资源策略 | CPU 配额不同，[系统调用](../../glossary/systems.md#systems.privilege)或权限策略不同 |
| 外部状态与依赖 | 同样请求遇到不同数据库内容、[延迟](../../glossary/performance.md#performance.latency-throughput)或配额 |

因此，交付记录应覆盖有效运行输入，而不只保存镜像名字。记录凭证的引用与版本时，也不应把凭证原文写进公开日志。

## 标签与摘要怎样标识制品

tag 是镜像引用中的可读标签，仓库中的指向可能变化；digest 按内容标识相应镜像对象。固定摘要可以避免同一标签后来指向新内容，但摘要本身不证明发布者可信、构建过程安全或程序没有漏洞。[Kubernetes v1.36 Images](https://v1-36.docs.kubernetes.io/docs/concepts/containers/images/#image-names)说明了标签和摘要的区别。

多平台镜像还存在镜像索引与具体平台镜像的层次。固定同一个索引摘要后，运行时仍可能按节点平台选择不同的成员镜像；比较运行内容时应同时记录平台和实际解析结果。相应模型见 [Kubernetes 多架构镜像说明](https://v1-36.docs.kubernetes.io/docs/concepts/containers/images/#multi-architecture-images-with-image-indexes)。

保留已验证镜像再推进到下一环境，有利于减少重建变化；它与“重建后字节完全一致”的可复现构建是不同证据。镜像拉取策略也不能替代版本身份：每次查询可变标签，不会使标签自动不可变。

## Namespace 约束视图，cgroup 管理资源

Linux namespace 把某类全局资源放入特定视图，例如进程 ID、挂载或网络。某个进程在自己的 PID namespace 中看到自己为 1，并不表示宿主环境里只有这一个进程。类型与语义见 [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)。Kubernetes 的 Namespace 是另一层 API 命名与组织范围，不能和这些内核机制混为一谈。

| 机制 | 主要问题 | 不能单独保证什么 |
| --- | --- | --- |
| PID namespace | 能看到哪些进程标识 | [CPU 时间](../../glossary/performance.md#performance.cpu-metrics)与内存额度 |
| Mount namespace | 看到怎样的挂载树 | 外部挂载内容永远不变或永远安全 |
| Network namespace | 使用哪组网络设备、路由等资源视图 | 业务调用权限、所有网络隔离策略 |
| cgroup | 对一组进程记账、分配或限制资源 | 文件内容隔离、业务[授权](../../glossary/security.md#security.identity)和性能目标 |

cgroup v2 采用层次结构，具体控制器及祖先约束共同影响实际可用资源。CPU 带宽上限、内存限制等有各自语义，不能把“容器隔离”当作所有资源已独占。控制器定义见 [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)。

这些机制可以组合，也可能按配置共享部分视图。权限、capabilities、系统调用限制和宿主访问还会影响边界；高权限或敏感宿主挂载会扩大暴露面。安全控制的分工见 [Kubernetes Linux 内核安全约束](https://kubernetes.io/docs/concepts/security/linux-kernel-security-constraints/)。本文没有验证任何容器逃逸防护或不可信代码沙箱。

## CPU、内存与调度请求不能按同一种方式理解

在 Kubernetes 中，资源 request 参与调度等资源安排，limit 约束运行时用量。request 不等于普通配置下获得一组专用 CPU 核；有余量时，容器也可能使用超过 request 的资源。Linux 上的 CPU 限制通常表现为节流，内存压力和限制可能触发 OOM 终止，不能理解为两者都会平滑降速。机制见 [Kubernetes v1.36 资源管理](https://v1-36.docs.kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits)。

教学反例：同一批计算在测试环境拥有充足 CPU 时间，在生产环境受较低配额约束，[尾延迟](../../glossary/performance.md#performance.percentiles)可能增加。若[健康探针](../../glossary/reliability.md#reliability.probes)也在相同资源压力下[超时](../../glossary/api.md#api.retries)，再触发重启，就可能进一步损失容量。需要结合实际节流、内存事件、进程退出原因和请求延迟判断，不能只看整台机器平均 CPU。

资源上限也不自动约束业务[排队](../../glossary/performance.md#performance.queueing)。容器最多能用多少 CPU，与应用允许堆积多少请求是不同问题；还需[背压与有界队列](../performance/backpressure-and-bounded-queues.md)。运行时堆大小也未必代表全部容器内存，解释可达对象与堆回收见[可达性与 GC](../runtime/reachability-and-garbage-collection.md)。

## 可写层、挂载与实例替换决定数据去向

容器通常在镜像只读层之上拥有自己的可写层。单纯重启容器内的应用进程，不会自行创建一个新的容器文件系统；Docker 停止后再启动同一个未删除的容器，也可以保留该容器的可写层。删除容器再创建则不会自动继承它。[Docker 存储说明](https://docs.docker.com/engine/storage/)区分了可写层、卷、绑定挂载等方式。

Kubernetes 所说的容器重启会由 kubelet 重新创建相应容器，容器文件系统按新实例处理，不能套用上面的 Docker 同一容器停止后启动语义。卷提供另一层生命周期：

| Kubernetes 中的数据位置 | 同一 [Pod](../../glossary/devops.md#devops.k8s) 内容器重建 | Pod 被替换 |
| --- | --- | --- |
| 容器可写层 | 不作为应保留数据的路径 | 不继承 |
| emptyDir 等随 Pod 的临时卷 | 可保留；容器崩溃不等于 Pod 被移除 | 新 Pod 不继承原 emptyDir |
| 持久卷 | 可跨容器重建保留 | 可跨 Pod 生命周期，但仍受绑定、访问、存储与回收策略约束 |

卷与 emptyDir 的定义见 [Kubernetes v1.36 Volumes](https://v1-36.docs.kubernetes.io/docs/concepts/storage/volumes/#how-volumes-work)。跨节点故障时能否使用数据，还需要存储系统自己的证据。

外部挂载的数据具有自己的生命周期和[故障域](../../glossary/reliability.md#reliability.fault-domains)。命名卷、Pod 临时卷与持久卷并非相同承诺；把目录挂出来，也不等于已经有备份、跨节点可用或经过业务一致性验证。应明确谁拥有数据、何时清理、怎样恢复，而不是笼统说“容器无状态”。

教学练习：应用把上传文件写到实例可写层，随后部署系统用相同摘要创建新实例。程序版本没有变化，文件仍可能丢失；若将文件改写共享存储，还需设计访问权限、[并发](../../glossary/systems.md#systems.concurrency)和恢复，不能把问题视作已经全部解决。

## 自检与验证范围

为一次交付列出镜像摘要、平台、配置、挂载、身份和资源约束，再分别改变一项，预测可能影响什么。解释：同一 tag 为什么不足以证明运行相同内容？PID 视图隔离为什么不能证明 CPU 独占？容器被替换后，哪类数据仍需要外部恢复路径？

2026-10-20 核查 Docker、Linux 手册、内核文档及 Kubernetes 文档；涉及调度与镜像的具体说明限定 v1.36 文档。状态为 source-checked，没有执行镜像构建、摘要解析、资源节流、OOM、挂载或隔离实验。实例如何按期望状态替换及接流量，继续见[声明式部署与健康探针](declarative-deployments-and-health-probes.md)。
