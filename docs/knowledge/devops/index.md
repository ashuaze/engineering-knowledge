<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# Linux、云与交付

建议优先级：P1。目标：让环境、构建、发布与恢复可重复。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

发布回滚了应用，为什么数据库仍可能不兼容？

## 已有正文

- [构建、部署与回滚：为什么换回旧程序还不够](build-deploy-rollback.md)：区分制品、配置、数据契约与流量状态，理解持续交付和可回滚的条件。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Linux Process / Signal / Permission | 进程生命周期、信号与访问权限。 |
| Namespace / cgroups | 资源视图隔离和用量限制。 |
| Image / Container | 文件系统与配置模板及其运行实例。 |
| Pod / Deployment / Service | 工作单元、声明式副本管理与服务访问。 |
| Ingress / Gateway API | 集群入口路由与流量管理接口。 |
| Service Discovery | 查找当前可用服务实例。 |
| VPC / Subnet / Security Group | 云网络边界和访问控制。 |
| IaC / Terraform | 以版本化声明管理基础设施。 |
| CI / CD | 持续集成、交付或自动部署。 |
| Rolling / Blue-Green / Canary | 不同发布替换和流量迁移策略。 |
| Feature Flag | 按条件启用行为并管理开关生命周期。 |
| Immutable Infrastructure | 通过替换实例交付新配置。 |
| Autoscaling / HPA | 基于观测信号调整资源或副本数。 |
| Multi-AZ / Multi-Region | 跨可用区与跨地域部署。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
