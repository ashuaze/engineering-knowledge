---
id: "kb-devops-iac-state"
title: "IaC 与状态漂移：代码没变，为什么计划仍要修改资源"
kind: "concept"
domain: "devops"
status: "evolving"
summary: "以 Terraform 区分配置、状态记录与远端观测，解释计划、漂移、锁、导入、敏感数据和部分失败后的协调责任。"
created: "2026-10-22"
updated: "2026-10-26"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-devops-declarative-health"]
related: ["kb-devops-delivery-lifecycle", "kb-engineering-dependency-governance", "kb-reliability-incident-response", "kb-database-schema-migrations", "kb-devops-cloud-network", "kb-devops-trusted-progressive-delivery"]
tags: ["iac", "terraform", "state", "drift", "change-plan"]
---

# IaC 与状态漂移：代码没变，为什么计划仍要修改资源

学习入口：昨天已经执行成功，今天源码没有变化，为什么基础设施计划仍然显示修改或替换？前置：[声明式部署](declarative-deployments-and-health-probes.md)。本文以 [Terraform](../../glossary/devops.md#devops.iac) 在线文档说明概念；副本数量和计划表为纸面模型，没有运行 Terraform、访问云账户或创建/修改真实资源。

配置的访问路径见[云网络与访问边界](cloud-networks-subnets-routes-and-security-groups.md)；产物来源及发布观察另见[可信制品与渐进发布](artifact-provenance-verification-and-progressive-delivery.md)，计划文件本身不证明两者已生效。

## 配置、状态记录和远端观测分别代表什么

基础设施即代码（IaC）用版本化声明描述资源及关系，让变更可讨论、比较和重复安排。它仍需工具、提供方（provider）和远端 API 才能落实；提交代码不会自动使实际资源一致。Terraform 通常在计划/执行时协调，不应与始终运行的 Kubernetes [控制循环](../../glossary/devops.md#devops.k8s)混为一谈。

为理解一次计划，可使用三个教学符号：

| 符号 | 本文含义 | 不能据此推出的结论 |
| --- | --- | --- |
| C：配置 | 本次源码、变量、模块及相关设置表达的要求 | 不保证已经执行或符合业务意图 |
| S：状态记录 | 资源地址与远端对象的绑定、已知属性及元数据 | 不是完整云资源清单，也不是业务数据备份 |
| R：远端观测 | 本次通过提供方读取到的对象情况 | 只覆盖相应权限、模型及读取时点 |

[Terraform 状态文档](https://developer.hashicorp.com/terraform/language/state)说明状态的核心作用是维护配置资源实例和远端对象的绑定。S 不是另一份“应该是什么”的配置：同一对象在外部变化后，刷新可更新已知属性，C 仍然表达自己的要求。

R 也不是全知的实时真相。API、权限、提供方可读取字段及[并发](../../glossary/systems.md#systems.concurrency)变化都影响观察范围；未纳入管理的资源不因一次计划无变化就被检查完。零差异只说明当前模型和输入下没有计划动作，不证明业务正确、安全配置完整或环境没有其他变化。

## 计划比较当前要求与观测，执行才改变资源

[正常计划](https://developer.hashicorp.com/terraform/cli/commands/plan)默认读取远端对象，再提出使受管资源符合配置的动作。禁用或缩小刷新会改变能看到的漂移范围。计划中的创建、原地更新、替换和销毁是不同影响；有些值只能在执行后确定，不能把 unknown 当作空值或已通过的检查。

计划阶段尚未落实拟议的资源变更，但仍会运行提供方及相关读取逻辑、访问 API，不应把它理解成纯文本比较。本文仅解释机制，不提供可直接作用于生产资源的操作步骤。

审查计划要把环境/账户、状态后端、源码、变量、模块/提供方版本和实际动作连起来。保存计划有助于审查与执行对应，但远端状态仍可能在其后变化；不能据此承诺执行必然成功或不会产生新的冲突。重新生成了不同计划，就应确认原审批依据是否仍然成立。

资源名称或地址变化也可能导致替换或错误的身份判断。是否原地修改取决于具体资源和提供方模型；文本只有一行变化，不代表影响只有一行。[重构](../../glossary/architecture.md#architecture.debt)地址时需有受支持的迁移安排，不能通过直接篡改状态文件掩盖差异。

## 漂移先判断变更意图与所有权

假设 C 要求 3 个副本，S 上次记录也是 3；某个外部自动扩缩器把实际数量调成 5，本次 R 观察到 5。为简化模型，假定该字段受 Terraform 配置管理，提供方允许原地调整且没有其他差异。

| 纸面选择 | C / 记录如何安排 | 后续需要判断什么 |
| --- | --- | --- |
| 维持固定 3 个 | 保留 C＝3，审查将实际数量调回的计划 | 缩容是否符合当前容量需求 |
| 接受固定 5 个 | 将声明改为 5，并重新核对计划 | 为什么改变目标，谁承担容量和成本 |
| 由扩缩器持续管理 | 明确此字段交给另一控制者，采用工具支持的忽略/委托机制 | Terraform 管理边界、扩缩上下限和观测责任 |

这不是 Terraform 某个真实资源的运行输出。它说明：外部差异既可能是意外修改，也可能是合理应急或另一个控制器的正常行为。“有漂移就恢复原值”可能撤销有效止损；“全部忽略”则可能丢掉应有控制。应先确定每项配置由谁负责、允许怎样变化，再选择修正实际资源、修改声明或划出委托边界。

refresh-only 模式用于使状态记录和根模块输出反映外部变化；接受相应计划不会把远端对象恢复为旧值，也不会自动改写 C。前例若仅把 S 更新为 5，C 仍为 3，下次正常计划仍可能提出调回 3。刷新记录、接受新的业务目标和改变资源是三种不同动作。

## 状态锁与资源归属限制并发边界

[状态锁](https://developer.hashicorp.com/terraform/language/state/locking)依赖后端支持，用来协调遵守同一锁机制的状态操作。它不能阻止控制台人员、自动扩缩器或另一份独立状态同时修改同一个远端对象。因而需要核对账户/环境、后端、工作空间和资源归属，不能只凭“拿到了锁”推断独占整个云环境。

已有远端对象还可通过[导入](https://developer.hashicorp.com/terraform/language/import)建立管理关联。导入不是重新创建对象，也不能证明补写的配置已与真实属性完全一致；后续计划仍可能要求修改或替换。一个对象被多个独立状态争相管理时，双方都可能认为自己有权修正它，造成来回覆盖。

应急操作可以暂时绕过原交付路径，但应记录意图、对象及恢复条件，并在事后协调回声明和归属。直接恢复旧状态文件可能让绑定和实际对象脱节；状态版本恢复、资源重建与业务数据恢复需要分别设计，不能把状态文件备份当作全部灾备。

## 部分失败和敏感数据需要单独处理

执行一组资源变更通常不是覆盖所有远端系统的单一事务。部分资源完成、另一些失败后，应先核对实际对象及状态，再决定继续、修正或恢复；不能假定报错代表“什么都没有发生”。回退代码也不自动撤回已删数据、已轮换凭据或已经发生的外部影响，见[构建与回滚](build-deploy-rollback.md)。

[敏感数据文档](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)说明，状态与保存的计划可能含有敏感值。`sensitive` 主要控制相应显示，并不意味着值不会进入文件或自动获得加密；可用的临时值、只写参数及限制取决于版本与提供方。需核对后端访问控制、加密、保留与日志/制品分发范围，不能只看终端有没有显示明文。

自检：只刷新 S 能永久接受外部目标 5 吗？不能，C 未改变。拿到状态锁能阻止控制台修改吗？不能。导入成功后能跳过下一份计划吗？不能。执行失败能证明所有资源仍是旧状态吗？不能。

## 关联阅读与核查范围

- [声明式部署与健康探针](declarative-deployments-and-health-probes.md)：期望状态、观测及持续控制的区别。
- [依赖锁定与 SBOM](../engineering/dependency-resolution-lockfiles-and-sbom.md)：固定工具输入与实际交付内容分别核对。
- [事故响应与复盘](../reliability/incident-response-recovery-and-postmortems.md)：应急变更的证据、交接及遗留风险。
- [数据迁移与兼容](../database/schema-migrations-and-compatibility.md)：代码回退与数据恢复的不同前提。

截至 2026-10-22 核查上述 HashiCorp 在线文档；具体资源和后端行为仍须对照所用版本与提供方。本文没有真实状态文件、计划输出、远端刷新、锁竞争、导入、敏感数据检查或故障恢复实验。
