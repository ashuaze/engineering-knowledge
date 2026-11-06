---
id: "kb-engineering-dependency-governance"
title: "依赖锁定与 SBOM：版本固定了，为什么还不能证明交付可信"
kind: "concept"
domain: "engineering"
status: "evolving"
summary: "区分版本约束、解析锁定、安装与交付清单，说明传递依赖、SemVer、摘要、SBOM、来源证明及更新证据的范围。"
created: "2026-10-20"
updated: "2026-10-26"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-devops-delivery-lifecycle", "kb-engineering-contract-compatibility"]
related: ["kb-engineering-static-analysis", "kb-engineering-code-review", "kb-architecture-refactoring-debt", "kb-devops-container-boundaries", "kb-runtime-modules-cycles"]
tags: ["dependencies", "lockfile", "sbom", "semver", "provenance"]
---

# 依赖锁定与 SBOM：版本固定了，为什么还不能证明交付可信

学习入口：[锁文件](../../glossary/engineering.md#engineering.supply-chain)没有变化，为什么不同环境仍可能运行不同内容？生成 SBOM 或核对哈希后，是否就能宣布组件安全？前置：[制品与交付](../devops/build-deploy-rollback.md)、[版本兼容](contract-testing-and-compatibility.md)。本文以 npm 11 文档作具体参照，SBOM 与来源证明参照 CycloneDX 和 [SLSA](../../glossary/devops.md#devops.provenance) v1.2；包名、版本与依赖图为虚构设计，没有安装、更新或扫描真实组件。

## 声明、解析、安装和交付是不同集合

依赖声明表达允许使用的版本或来源；解析器结合约束、仓库及规则形成依赖图；安装再受平台、可选依赖、配置与脚本等影响；最终[打包](../../glossary/frontend.md#frontend.bundling)和运行还可能移除、生成或动态取得组件。直接依赖由项目声明，传递依赖由依赖继续引入，不能只看顶层清单判断全部影响。

纸面图为 App 直接依赖 Render 2.1.0 和 Report 1.3.0，Render 引入 Parse 1.0.0，Report 引入 Parse 2.0.0。两个 Parse 可以是同名的不同组件版本，不一定冲突，也不能擅自合成一条记录。若漏洞只影响 Parse 1.0.0，需要找到引入路径、相关制品与实际上下文；只更新顶层 Report 未必触及那条路径。

| 记录 | 主要回答 | 尚不能单独回答 |
| --- | --- | --- |
| 依赖声明 | 项目接受哪些版本或来源 | 本次实际解析到了什么 |
| 锁文件 | 该解析模型固定了哪些条目与来源 | 最终制品确实包含什么、是否无缺陷 |
| 安装记录 | 此环境安装或生成了什么 | 发布时保留了哪些组件 |
| 制品关联的组件清单 | 声明范围内交付内容及关系 | 内容来自谁、是否可利用、行为是否兼容 |

## 锁文件减少解析漂移，不冻结所有环境

npm 的 [package-lock.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json/)记录解析结果，包括版本、来源和适用条目的完整性信息；[npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)要求已有锁文件，声明与锁不匹配会失败，而不是替你更新锁。它也有安装选项与依赖树形状前提，不能把命令名当作一切条件都固定的保证。

同一锁文件不自动固定操作系统、CPU、[运行时](../../glossary/runtime.md#runtime.virtual-machine)、[编译器](../../glossary/runtime.md#runtime.compilation)、注册源配置、安装脚本下载、环境变量或外部构建输入。可选组件与原生扩展尤其需要说明平台。锁中包含某条目，也不表示它在每个目标上都安装或进入最终产物。

因此更新依赖时，要把声明、锁及实际解析差异一起阅读，而不是只改顶层版本号或手工删掉一段锁文件来消除告警。锁文件也应核对来源变化、脚本与传递图；本篇没有执行 `npm ci` 或修改仓库依赖。

## 版本号表达兼容性意图，仍需本项目验证

[SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)以声明的公共 API 为基础区分主、次、修订版本；0.y.z 与预发布另有稳定性前提。它不能证明发布者没有错误，也不能替你判断依赖了哪些未承诺的内部行为。补丁号增加，不等于任意应用都能无风险升级。

升级要核对本项目真实使用方式、迁移说明、支持环境和失败路径，再选择相应契约、集成及业务验证。强行覆盖传递版本可能满足扫描器的版本条件，却破坏上游依赖的假设；需要明确解析变化与兼容证据。回退也受数据和配置约束，不能承诺恢复旧锁就撤回已经执行的写入。

## SBOM 是有范围和身份的材料清单

SBOM（Software Bill of Materials）以机器可读方式描述组件、版本和依赖关系，定义参照 [CycloneDX SBOM](https://cyclonedx.org/capabilities/sbom/)。实用清单还应说明对应产品/制品、生成阶段、工具、时间、覆盖与已知缺口。源码解析、构建、打包后扫描或运行时观察各有不同视角，不能仅因文件扩展名相同就认为范围相同。

组件身份应足以区分生态、命名空间、名称、版本与适用来源，不能只按一个短包名匹配。纸面例中，若最终制品只包含 Render 路径，Report 的声明记录不能据此自动当作已交付内容；若另有[镜像](../../glossary/devops.md#devops.containers)系统包、复制进来的库或运行时下载，则仅由语言锁生成的清单可能缺项。没有枚举到某组件，不等于已经证明它不在产物中。

制品摘要和清单之间需要明确关联：B1 的清单不能直接解释 B2，即使两者使用同一个可变标签。完整性、覆盖和更新条件决定清单的解释范围；SBOM 本身不是无漏洞、许可审查完成或业务兼容的证书。

## 摘要、签名、来源证明各自需要可信前提

摘要帮助判断拿到的字节是否与预期内容一致，但预期摘要本身必须可信；攻击者若同时替换包和从同一不可信位置取得的摘要，二者一致也没有解决来源问题。锁文件中的 integrity 不自动表明发布者可靠，内容相同也不等于内容无恶意。

来源证明（provenance）描述制品如何、由什么过程产生。SLSA v1.2 的[制品验证说明](https://slsa.dev/spec/v1.2/verifying-artifacts)要求把证明与目标摘要、可信构建身份及预期参数关联。核验成功的签名支持所核对身份与指定内容之间的签署关系，仍需判断该身份是否值得信任、所签声明是否满足预期。存在一份签名文本，不等于已经检查签名、身份和适用制品；验证来源也不等于证明所有依赖和业务代码无缺陷。

[可复现构建](https://reproducible-builds.org/docs/definition/)另要求在声明的源码、环境与指令条件下得到逐字节相同的指定制品；拥有锁文件、来源证明或一次构建成功，都不单独构成这个重建对照。

## 清单帮助定位，处置仍需上下文

把组件版本与漏洞信息匹配，得到的是调查入口；匹配是否准确、漏洞代码是否存在、适用配置和攻击路径仍需证据。[CycloneDX VEX](https://cyclonedx.org/capabilities/vex/)用于表达特定上下文中的受影响/可利用性信息，不应将“尚未发现可达路径”当成已经证明不受影响。旧的判断也不能直接覆盖更新后的制品和配置。

维护记录可保留引入路径、当前版本与来源、目标变更、影响制品、验证证据、未决问题及重评条件。依赖维护不仅是发现告警后升级，也包括移除不用的组件、处理停止维护或不支持的环境、明确替换与回退责任；具体发布流程接回[交付生命周期](../devops/build-deploy-rollback.md)。

自检：看的是允许范围、解析结果、安装还是最终制品？同名不同版本是否被合并丢失？锁、清单和证明对应哪份内容？摘要与身份的可信依据是什么？扫描命中与真实受影响之间还缺什么？升级和回退分别验证了哪些行为？

2026-10-20 核查 npm 11 锁文件与 `npm ci`、SemVer 2.0.0、CycloneDX SBOM/VEX、SLSA v1.2 与可复现构建定义，状态为 source-checked；文档参照不代表本机执行环境。App/Render/Report/Parse 与 B1/B2 均为纸面模型，未安装/升级包、生成或扫描 SBOM、验证签名/来源、分析漏洞可达性、重建制品或执行发布。
