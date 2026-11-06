---
id: "kb-engineering-static-analysis"
title: "静态分析与告警：检查全绿，为什么仍可能有缺陷"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "区分 Lint、类型检查与数据流分析，解释分析范围、规则模型、误报漏报、基线和告警处置的证据边界。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-engineering-test-scopes"]
related: ["kb-runtime-types-validation", "kb-engineering-code-review", "kb-architecture-refactoring-debt", "kb-engineering-dependency-governance", "kb-engineering-property-state-models"]
tags: ["static-analysis", "lint", "false-positive", "false-negative", "baseline"]
---

# 静态分析与告警：检查全绿，为什么仍可能有缺陷

学习入口：[Lint](../../glossary/engineering.md#engineering.analysis)、类型检查和扫描都通过，能否判断代码正确？告警很多时，怎样决定修复还是抑制？前置：[测试范围](test-scopes-and-doubles.md)。本文以 ESLint、TypeScript 与 CodeQL 官方资料说明概念，不安装或运行这些检查；场景与处置流程为教学设计。

## 静态分析检查代码模型中的性质

静态分析从源码、语法树、类型或程序关系等表示推断性质，不靠给目标程序逐一输入业务请求来观察结果。生成分析表示的过程仍可能编译代码或运行构建；“静态”不等于扫描过程绝不执行任何工具或脚本，具体环境需另行约束。

不同工具和规则拥有不同目标：

| 类别 | 可关注的问题 | 不能直接推出 |
| --- | --- | --- |
| Lint 与约定规则 | 未使用变量、可疑写法、格式或团队约定 | 所有规则都是执行时缺陷检查 |
| 类型检查 | 声明与推断类型是否满足相应规则 | 外部实际数据已经校验、业务规则正确 |
| 控制流/数据流分析 | 某类值沿调用或分支流向危险操作 | 模型覆盖了全部动态行为与框架语义 |

这些类别可以交叉。ESLint 的[核心概念](https://eslint.org/docs/latest/use/core-concepts/)把规则、配置、插件和解析器区分开；规则可能发现 bug，也可能只表达约定。[类型系统](../../glossary/runtime.md#runtime.type-system)也有设计取舍，[TypeScript 文档](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#a-note-on-soundness)明确其并非完全健全；不能把所有静态工具都当作一种“程序正确性证明器”。

## 无告警首先要核对分析是否真的完成

解释结果至少需要工具与规则版本、实际分析的源码版本、语言/文件、配置与排除项、生成或构建情况，以及分析是否成功完成。空报告可能来自没有适用问题，也可能来自漏扫、任务失败、过滤或没有启用相应规则。

例如只扫描服务目录，却把共同校验函数移到未扫描的插件目录；主目录无告警，不能推出新布局没有原来的问题。分析报告上传成功，也不自动表示每个预期文件都已成功提取。GitHub 的[工具状态说明](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/manage-your-configuration/use-the-tools-status-page-for-code-scanning)提供实际文件、规则与错误的查看方式；文件覆盖也不等于所有路径或所有缺陷种类都被证明安全。

同名检查在不同语言或规则版本上未必含义相同。改变严格程度、框架模型和扫描范围后，告警数量可能变化；比较前后数量之前先固定口径，不能将增加排除目录或缩小扫描范围造成的“清零”算成缺陷修复。

## 误报、漏报与真实问题按同一性质判断

误报是分析报告某问题，但依据该规则要判断的性质与实际前提复核后不成立；漏报是实际存在相应问题，却没有报告。格式规则命中一处格式差异，并不会仅因“不影响运行”就成为误报——它本来检查的是约定，是否值得阻断是另一项策略选择。

纸面例：分析认为不可信字符串可到达文件路径。若它未识别某个确实完整约束输入域的校验函数，可能多报；若它把一个实际上只检查后缀的函数当作完整校验，又可能漏报。不能仅因代码里出现名为 sanitize 的函数就裁定安全；需要看输入、校验条件、传播、编码和最终操作的实际语义。这里没有给出真实漏洞或已运行扫描结果。

提高覆盖可能增加不确定的候选，较保守的规则选择也可能遗漏问题。CodeQL 的[查询套件说明](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-query-suites)区分 default 与 security-extended 的精确性取舍；不是每个工具都有相同的调节方式，更不能用一组已发现告警计算未知的全部漏报数。

## 抑制与基线改变报告，不改变代码事实

基线通常用于标记已有发现，让团队区分新增项与历史项；它不是“这些发现都安全”的结论。只阻断新问题能帮助逐步接入检查，但已有高影响风险仍需要独立处理，不能因为较早存在就无限期忽略。

抑制某条发现应说明规则、具体位置、判断依据、适用条件、责任人和复查时机。大范围关闭规则会同时隐藏未来命中，修改框架、配置或输入来源后，原误报判断也可能失效。由代码移动或指纹变化造成旧发现消失、重新出现，不等于风险被消除或新增；需要回到同一问题核对。

“确认真实但暂时接受风险”和“证明确为误报”是不同决定。暂时接受仍需说明限制和后续处理；如果还缺证据，应保留待确认状态，不能为了让报表变绿就归为误报。

## 自动修复也有契约与复查边界

有的规则提供设计上保持逻辑的自动修复，有的只提供需要人判断的建议。ESLint 区分 fixes 与 suggestions：建议可能改变逻辑，不能把所有灯泡提示视为可无条件应用的格式化。自定义规则或工具本身也可能有缺陷，实际仍需阅读变更及做相应范围验证。

删除看似未使用的导入可能触及模块副作用，调整判断可能改变短路求值；是否安全要看具体规则和语言语义。本篇没有声称某个 ESLint 内置规则会做这些错误转换，而是说明判断自动修改时不能只看标签。

可把处置组织为：确认分析完成与范围 → 理解规则及路径 → 找反例或支持证据 → 修代码、补模型或记录有限抑制 → 按相同口径复查。工具更新或规则集升级也应单独记录，避免把业务修改与检查口径变化混成一项结果。

自检：全绿对应哪个源码、哪些文件和规则？这是约定、类型还是数据流结论？抑制是误报证明、风险接受还是尚未确认？修复改变了什么可观察行为？谁在条件变化后复查？

2026-10-20 核查 ESLint 核心概念、TypeScript [类型兼容性](../runtime/type-systems-and-runtime-validation.md)与 CodeQL 套件/工具状态文档，状态为 source-checked；这些在线文档不等于本机安装版本。路径校验、目录变更和告警处置为纸面设计，未执行 Lint、类型检查、CodeQL、自定义模型或自动修复实验。
