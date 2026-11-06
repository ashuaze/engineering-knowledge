---
id: "kb-engineering-test-portfolio"
title: "测试金字塔与证据组合：覆盖率很高，为什么仍会漏掉关键失败"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "按风险、真实边界和反馈成本组合测试，区分语句/分支覆盖、有效断言、变异测试及未覆盖的产品要求。"
created: "2026-10-27"
updated: "2026-10-27"
last_verified: "2026-10-27"
verification: "source-checked"
prerequisites: ["kb-engineering-test-scopes"]
related: ["kb-engineering-tdd-bdd", "kb-engineering-test-stability", "kb-engineering-property-state-models", "kb-engineering-contract-compatibility"]
tags: ["test-pyramid", "risk", "coverage", "mutation-testing"]
---

# 测试金字塔与证据组合：覆盖率很高，为什么仍会漏掉关键失败

学习入口：有几千条[单元测试](../../glossary/engineering.md#engineering.tests)，代码覆盖率也很高，为什么真实数据库升级或权限变更仍会出错？数量、执行过的代码和能够发现的错误，是不同的观察对象。

前置：[测试范围与替身](test-scopes-and-doubles.md)。本文参照 Ham Vocke、Coverage.py 7.11.0 与 PIT 的说明，表格和代码均为纸面示例；未运行覆盖率、变异测试或测量测试套件。

## 金字塔提示成本分布，不规定固定比例

[The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)讨论不同粒度的自动检查。较小范围通常更容易快速运行与定位；真实依赖和整体路径能检查更宽的协作，也带来环境、数据和诊断成本。

这些是组织测试的经验，不是必须采用某个数量比例。集成风险高的适配器需要真实边界证据；纯计算规则可以主要用聚焦测试。把同一条 UI 流程复制一百次，不能替代一次关键数据库兼容或对象权限检查。

## 从风险映射到最有解释力的边界

| 风险 | 适合先放在哪里检查 | 仍需补什么 |
| --- | --- | --- |
| 金额舍入规则错误 | 聚焦规则测试及边界例子 | 实际存储/传输的单位与精度 |
| 驱动改变事务行为 | 真实数据库集成 | 代表性并发与恢复历史 |
| 提供方改变响应字段 | 消费/提供双方契约检查 | 实际部署、权限与业务状态 |
| 登录后无法完成付款 | 声明范围的关键用户路径 | 回调、重试及外部效果恢复 |

同一风险可以需要多种证据；“更多真实依赖”也不自动更强。若端到端只断言页面有标题，没有核对扣款和订单状态，仍没证明付款目标。

## 覆盖率先回答执行到了哪里

考虑以下未执行的示意代码，要求是仅对正数接受：

```text
accept(x):
    if x > 0:
        return true
    return false
```

只检查 `x=1` 与 `x=-1`，可以经过这里的两个结果分支，却遗漏 `x=0`。若实现意外变为 `x>=0`，这两项仍通过。分支被经过，不等于分界点和所有输入都被检查。

[Coverage.py 7.11.0](https://coverage.readthedocs.io/en/7.11.0/branch.html)说明语句执行和分支跳转的测量区别；工具的排除规则、生成代码和结构化分支处理影响分母。报告应说明范围，不能跨不同配置直接比较百分比。

覆盖也不等于有效断言。执行到拒绝逻辑却没有核对状态未变化，可能遗漏副作用；实现中根本缺少某项要求时，它也不会自动出现在代码覆盖率的分母中。

## 变异测试检查某类变化是否会被发现

[PIT 的机制说明](https://pitest.org/)描述修改程序后再运行测试：如果测试因变化而失败，就发现了这一变异；仍通过则需要分析测试范围、输入、断言或等价变化。

在前例中，`>` 变成 `>=` 的变异可由 `x=0` 揭示，但实际工具是否生成它依所用算子。未运行的变异、超时、无覆盖与等价变异需按报告口径区分；不能把全部存活项都认定为产品缺陷，也不能把变异得分当作真实缺陷发现率。

## 同时管理反馈成本和证据缺口

优先把明确风险放到能快速、稳定提供所需证据的边界；关键流程保留整体检查，并监控首轮失败、执行耗时与维护成本。隔离或删除[间歇失败测试](../../glossary/engineering.md#engineering.flaky-tests)时，记录丢失了哪条验证，再补替代证据，见[测试稳定性](flaky-tests-isolation-and-evidence.md)。

选择先运行哪些测试时，还要处理依赖分析遗漏、共享配置变化及必要的完整检查。快速全绿只证明本次选择的范围，不能把没有运行解释为已通过。

## 自检

1. 为什么[测试金字塔](../../glossary/engineering.md#engineering.pyramid)不能直接转成固定的数量比例？
2. [数据库事务](../../glossary/database.md#database.isolation)和付款流程分别需要什么边界的证据？
3. `x=1/-1` 都通过，为什么仍可能漏掉 `>` 变成 `>=`？
4. 分支覆盖、有效断言和变异结果各回答什么？
5. 为了更快而隔离测试、缩小执行范围时，应保留哪些记录？

## 来源与核查

2026-10-27 核查 Vocke 的测试金字塔文章、Coverage.py 7.11.0 分支说明与 PIT 基本机制。本文为 source-checked；未运行示例、测量任何覆盖率/变异分数、比较测试比例或验证选择性执行算法。
