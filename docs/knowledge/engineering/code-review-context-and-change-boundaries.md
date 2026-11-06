---
id: "kb-engineering-code-review"
title: "代码评审与小步变更：有人看过，为什么仍不能保证可发布"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "解释评审上下文、完整变更单元与风险分工，区分必须修复、建议、最终版本证据和发布兼容责任。"
created: "2026-10-20"
updated: "2026-10-27"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-engineering-test-scopes", "kb-architecture-module-boundaries"]
related: ["kb-engineering-static-analysis", "kb-architecture-refactoring-debt", "kb-engineering-contract-compatibility", "kb-devops-delivery-lifecycle", "kb-engineering-dependency-governance", "kb-engineering-trunk-flags", "kb-engineering-design-documents", "kb-engineering-specification-traceability"]
tags: ["code-review", "change", "context", "risk", "maintainability"]
---

# 代码评审与小步变更：有人看过，为什么仍不能保证可发布

学习入口：提交已经 LGTM，测试也绿了，为什么合并或发布后仍会出问题？前置：[测试边界](test-scopes-and-doubles.md)、[模块依赖](../architecture/module-boundaries-and-dependencies.md)。本文建立评审范围和证据的概念，参照 Google Engineering Practices；示例为教学方案，没有向真实仓库提交评审或执行发布。

评审所依赖的背景、备选和决定记录见[设计文档与决策记录](design-docs-rfcs-adrs-and-decision-lifecycles.md)；预期行为与本次证据的对应见[规格驱动与验收追溯](specifications-contracts-traceability-and-acceptance.md)。

## 评审是理解变更及其后果

[代码评审](../../glossary/engineering.md#engineering.review)由其他人检查变更的意图、实现、影响和维护成本，帮助发现作者遗漏并传播上下文。它是有限时间和知识范围内的判断，不是对全部状态与输入的证明。自动检查、人工阅读、实际行为验证和发布控制分别提供证据，不能用一个“通过”代替其他边界。

Google 的[评审标准](https://google.github.io/eng-practices/review/reviewer/standard.html)强调持续改善整体代码健康，同时区分关键问题与个人偏好；这是其工程实践依据，不是所有组织必须照搬的流程。风格约定可以机械检查，设计与[兼容性](../../glossary/api.md#api.versioning)则需要结合问题讨论。

## 作者需要给出能独立理解的上下文

评审者首先要知道：具体触发场景、要求的前后行为、为什么要改、实际改了哪些边界，以及验证了什么、仍有什么限制。变更描述不应只说“优化代码”，也不应要求读者先补完整聊天历史。

纸面变更说明可写成：“重复保存订单会产生第二条记录；本次使相同请求标识返回原结果，并拒绝相同标识对应不同请求内容。已覆盖的本地事务与 HTTP 路径分别列证据。”这比只列“新增三张表、五个函数”更容易核对目标；这里没有宣称该示例已实现或测过。

阅读差异还需返回调用者、被调函数、配置、错误路径和历史约束。一个条件表达式虽然只改一行，也可能放宽对象访问范围。生成文件、[锁文件](../../glossary/engineering.md#engineering.supply-chain)与迁移脚本也需要相应来源与含义，不能因为不是手写业务逻辑就完全略过。[Google 的评审关注项](https://google.github.io/eng-practices/review/reviewer/looking-for.html)覆盖设计、功能、复杂度、测试、文档和上下文。

## 小变更应是完整的推理单元

小步变更通常更容易理解、比较和撤回，但“小”主要指意图集中、依赖可见且结果可成立，不是强制某个行数。把一个变更拆到只看到声明、看不到任何使用方式，也可能更难判断。依据见 [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)。

纸面例：把内部方法重命名、改变金额舍入、切换数据库字段和全库格式化放进同一份差异，会同时需要结构、业务、数据和格式四种判断。可把无语义整理与有意行为修改分开，让每一步的目标和验证可说明；跨文件的原子修改则可能必须保持在同一个完整单元中。

拆分不等于让中间版本临时坏掉，也不等于拆成多次发布。对于不兼容格式，可先准备兼容读者，再启用新写法，最后在窗口结束后清理；每一阶段分别评审，依赖顺序和新旧共存矩阵仍需整体可见。具体责任见[交付与回滚](../devops/build-deploy-rollback.md)，不能靠 PR 数量推导回退安全。

## 评审意见要说明依据和阻断原因

| 意见类型 | 要表达的内容 | 例子 |
| --- | --- | --- |
| 必须修复 | 可指出的错误、违反契约或不可接受风险 | 先提交后鉴权会留下未[授权](../../glossary/security.md#security.identity)写入 |
| 需要澄清 | 当前证据不足以判断 | 旧消费者是否仍会读这个字段 |
| 非阻断建议 | 可改进但不影响本次接受条件 | 可采用另一命名，并说明只是建议 |

“我更喜欢这种写法”和“这个顺序会改变错误路径”不是同一种意见。涉及关键接受条件的澄清，在证据补齐前仍可能阻断接受，不能一概视为非阻断建议。应给出触发条件、后果或设计依据；作者可以用证据解释替代方案。设计分歧无法解决时，找负责该边界的人做决定并保留理由，不能仅靠来回改写或批准人数消除分歧。

检查分工也要明确：某人只看权限、某人只看迁移，则总体验收仍要覆盖其余行为。多人都以为别人看过，可能留下空白；一位评审者对陌生领域点头，也不自动补齐专门知识。

## 批准对应的是被检查的版本与范围

评审应能对应具体源码状态。批准后再改关键逻辑、变更基础分支、解决冲突或更新依赖，可能使原判断的前提失效；是否需要重审取决于实际影响，不能仅因界面保留了旧批准就认定新内容已看过。对合并结果及相应版本运行检查，才能说明测试对应哪份内容。

这并不要求对任何字符变动都重做全部工作，而是把证据与变更关联。可以根据差异补查受影响部分；构建或测试跑的是另一提交、另一个配置时，必须先解释关联。工具可协助标记失效批准和检查状态，但团队策略与配置需要单独核对，本篇不声称某个平台默认启用了某项保护。

频繁合并与未完成功能的开放条件，见[主干开发与功能开关](trunk-based-development-and-feature-flags.md)；短分支仍需完整评审单元。

## 评审完成与发布就绪分别判断

源码可接受后，还可能需要数据迁移、混合版本兼容、配置准备、运行资源和业务观测。LGTM 不会回退数据库，也不会确认线上流量只经过新实现。[契约兼容](contract-testing-and-compatibility.md)和部署证据说明的是具体边界，不能从“有人看过”直接推到整条发布链路。

维护质量也不是评论越多或批准越快越好。评审等待、返工和遗漏可帮助发现过程问题，但单独用评论数给个人排名，容易把讨论密度当成缺陷数量。更可复查的产出是：意图、关键约束、已处理问题、证据版本、范围及剩余限制能够被后来维护者理解。

自检：作者意图与用户需要是否一致？这份差异能否独立理解？哪些意见阻断、依据是什么？每个关键边界由谁看过？批准和测试是否仍对应最终内容？发布还欠哪类证据？

2026-10-20 核查 Google Engineering Practices 的标准、关注项与 Small CLs，状态为 source-checked。订单、拆分、评审分工和版本关联为本文教学综合；没有向外部仓库发送评论、批准、合并、触发流水线或发布，也没有测量评审效果。
