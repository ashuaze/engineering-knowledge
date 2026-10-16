---
id: "kb-devops-delivery-lifecycle"
title: "构建、部署与回滚：为什么换回旧程序还不够"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "区分制品、配置、数据契约与流量状态，理解持续交付和可回滚的条件。"
created: "2026-10-16"
updated: "2026-10-16"
last_verified: "2026-10-16"
verification: "source-checked"
prerequisites: []
related: ["kb-engineering-test-scopes", "kb-database-concurrent-inventory", "kb-security-object-authorization"]
tags: ["delivery", "compatibility", "rollback"]
---

# 构建、部署与回滚：为什么换回旧程序还不够

学习入口：新版本出问题后已恢复旧镜像，业务为什么仍然异常？前置知识：源代码、运行配置与持久化数据。本文面向开发、测试、运维和平台人员，解释交付概念与兼容边界，不执行任何部署。

## 先区分构建、部署、发布与回退

构建把指定输入转换为可分发制品；部署把制品和配置放到目标运行环境；发布常指让某项能力对用户生效，可能通过流量或功能开关独立控制。回滚则需要说明恢复哪部分状态，以及恢复后是否仍能处理当前数据与请求。

CI 强调频繁集成后的自动反馈。CD 可能指持续交付，也可能指持续部署：前者强调变更保持可发布状态，后者进一步自动推进到生产；团队需明确自己的审批与自动化边界。流水线跑完不自动等于用户侧目标已达成。

## 回滚涉及的四类状态

| 状态维度 | 应记录什么 | 回退时要问什么 |
| --- | --- | --- |
| 制品 | 源码版本、依赖、构建环境、制品摘要 | 取回的是不是原先验证过的那份字节 |
| 配置 | 配置版本、开关、环境差异 | 旧程序是否支持当前配置与依赖 |
| 数据与协议 | 表结构、序列化格式、API/事件契约 | 旧版本是否能读取新版本已写入的数据 |
| 流量与实例 | 新旧版本分布、路由、后台任务 | 混合运行期间是否互相兼容 |

[Reproducible Builds 定义](https://reproducible-builds.org/docs/definition/)要求在声明的源码、环境与指令条件下重建相同制品字节。固定依赖或“同一提交再次构建”本身并不能证明可复现。保留已验证制品并在环境间推进，可以避免临时重建引入新的变化。

混合版本是滚动部署时需要考虑的状态。[Kubernetes Deployment 文档](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)明确其回滚只回退 Deployment 的 Pod 模板；数据库和外部系统状态不因此恢复。

## 交付链路与停止条件

说明性交付链路如下，不绑定某个平台：

```text
指定源码和依赖 → 构建制品并记录摘要
→ 校验制品及接口/数据兼容性 → 部署相同制品与版本化配置
→ 检查实例健康与业务信号 → 按策略放量
→ 达到停止条件时暂停、回退或向前修复
```

每次变更记录制品、配置、数据契约和流量阶段。摘要用于标识制品内容，不单独证明来源可信或构建正确。停止条件除进程存活外，还应覆盖关键业务结果与错误；返回健康不等于业务兼容。

## 兼容矩阵决定能退到哪个版本

对数据格式变化，先让所有相关读者具备兼容能力，再启用新写法，最后在确认回退窗口与旧消费者处理完毕后清理兼容代码。[AWS 回滚安全说明](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)讨论了准备与启用分阶段的做法。

教学推演：旧格式为 A、新格式为 B；不考虑其他写入者时，可用下表讨论兼容路径：

| 版本 | 能读取 | 会写入 |
| --- | --- | --- |
| v1 | A | A |
| v2（准备） | A、B | A |
| v3（启用） | A、B | B |

v3 写入 B 以后，回退到能读取 B 的 v2 与回退到只读 A 的 v1，后果不同。纸面练习是列出所有在线服务、后台任务和离线消费者，判断谁必须先具备兼容能力，并指出何时恢复 v1 已不安全。

本例是机制推演，未构建镜像、部署集群或执行数据迁移。验收：能为一次变更写出输入与制品身份、兼容矩阵、暴露阶段、停止条件和可回退范围。

## 发布策略的取舍与常见失败

- 滚动发布能逐步替换实例，需要新旧版本共存；具体容量和故障行为取决于策略与环境。
- 蓝绿或流量分阶段切换便于控制暴露面，但需要额外环境、路由与兼容管理；切回流量也不会撤销已完成的写入。
- 功能开关可把功能启用与部署解耦，但开关状态本身也需要版本、授权和清理策略。
- 自动回滚可缩短某些故障处理时间，但前提是信号可靠、回退路径有效，且旧版本仍与当前状态兼容。

回滚、恢复备份、补偿业务与向前修复处理的对象不同。是否可以逆转，必须由数据与业务语义决定，不能统一归为“回滚代码”。

| 错误 | 影响 | 处理方向 |
| --- | --- | --- |
| 用可变标签代替确定制品 | 同名版本实际运行不同内容 | 记录并核对制品摘要和来源 |
| 新写法上线前仍有旧读者 | 部分实例或消费者解析失败 | 先验证兼容读者覆盖范围 |
| 恢复旧镜像却保留不兼容配置或数据 | 回退后继续故障 | 逐项检查运行状态与契约 |
| 删除旧字段后才演练回滚 | 旧程序缺少必需数据 | 分阶段演进并明确不可逆点 |
| 只看进程存活 | 静默业务错误未触发停止 | 同时观察关键业务结果与用户影响 |

## 关联阅读

- [测试层次与替身](../engineering/test-scopes-and-doubles.md)：用不同范围的证据检查逻辑、协议与关键流程。
- [库存并发](../database/concurrent-inventory.md)：数据约束和事务行为不随应用版本回退而自动恢复。
- [对象级授权](../security/object-level-authorization.md)：部署与开关权限之外，运行中的对象访问仍需校验。

## 来源与核查

核查日期：2026-10-16。制品可复现定义依据 Reproducible Builds；Deployment 回退范围依据 Kubernetes 文档，未依赖某个命令版本或默认参数；阶段兼容思路依据 AWS。交付记录与矩阵为教学设计，无部署实测。

- [Reproducible Builds：Definitions](https://reproducible-builds.org/docs/definition/)
- [Kubernetes：Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [AWS：Ensuring rollback safety during deployments](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)
