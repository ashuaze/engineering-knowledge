---
id: "kb-cache-object-storage"
title: "对象存储与预签名访问：文件上传后怎样成为可用的业务对象"
kind: "concept"
domain: "cache-search"
status: "evolving"
summary: "区分对象键、版本、校验、上传完成与业务发布，解释单键一致性、条件写、分段上传及预签名访问的授权和期限。"
created: "2026-10-23"
updated: "2026-10-23"
last_verified: "2026-10-23"
verification: "source-checked"
prerequisites: ["kb-security-object-authorization", "kb-api-conditional-requests"]
related: ["kb-security-secret-lifecycle", "kb-networking-cdn-waf", "kb-database-models-access-patterns", "kb-database-backups-pitr", "kb-api-idempotency", "kb-messaging-outbox", "kb-cache-search-index-cutover"]
tags: ["object-storage", "versions", "multipart", "presigned-url", "publication"]
---

# 对象存储与预签名访问：文件上传后怎样成为可用的业务对象

学习入口：浏览器显示上传完成，为什么附件还不能下载？删除业务记录后，旧链接为什么仍可能可用？对象字节、存储版本、业务归属和访问能力分别由不同机制维护；上传完成只是其中一项结果。

前置：[对象级授权](../security/object-level-authorization.md)、[HTTP 条件请求](../api/conditional-requests-and-cache-validation.md)。本文以 Amazon S3 的通用桶（general purpose bucket）及官方文档为具体参照，不将它的接口、一致性、目录或签名规则推广到所有[对象存储](../../glossary/cache-search.md#cache-search.objects)，也不涵盖目录桶的特殊能力。核查日期为 2026-10-23，资料是当日滚动页面；以下地址、时间、上传流程和发布协议为教学设计，未访问实际桶或执行云端操作。

## 存储身份不等于文件路径或业务身份

| 概念 | 定位或证明什么 | 不能代替什么 |
| --- | --- | --- |
| bucket 与 key | 在存储命名范围定位当前对象 | 业务附件归属、用户权限或不可变版本 |
| version ID | 启用版本机制后，定位某个保存版本 | 业务审批状态、全局递增时间或内容校验值 |
| [ETag](../../glossary/api.md#api.conditionals) | 服务给出的对象内容验证器，可用于条件请求 | 通用的整文件 MD5、version ID 或全部元数据变更序号 |
| checksum | 按明确算法和范围核对字节完整性 | 上传者身份、内容合法性或业务允许发布 |
| 附件记录 / manifest | 应用定义的对象引用、归属、状态与发布集合 | 对象字节已经存在或所有读者有权读取的证明 |

S3 通用桶中的 key 是完整名称，`tenant/T1/report.pdf` 的斜杠可用于前缀组织，不会自动创建文件系统目录和权限继承；依据见[对象命名说明](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html)。不能因为 key 含租户编号就信任调用者自报的该编号。业务层仍应验证对象归属，并控制允许操作的完整 key 或版本。

普通通用桶的移动/重命名可通过复制后删除实现，见[复制、移动与重命名](https://docs.aws.amazon.com/AmazonS3/latest/userguide/copy-object.html)。这是两个存储动作：复制成功而删除失败，会留下两份；删除之前还可能有并发写入。不能用文件系统的原子 rename 直觉安排发布，实际其他桶类型的专门 API 需另行核对。

## 单键强一致不提供多键共同发布

[S3 一致性模型](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel)说明对象 PUT/DELETE 后的读写一致性，以及单键更新的[原子性](../../glossary/systems.md#systems.atomicity)：读者不会读到一次对象替换中的半份数据。这里指相应 S3 接口与已确认操作；应用缓存、[CDN](../../glossary/networking.md#networking.cdn-waf) 和另一套业务数据库不因此同时更新。

假设模型由 `weights.bin`、`config.json` 两个键组成，直接先后覆盖它们，读者可能取到新权重和旧配置。两个对象各自完整，不代表组合属于同一个发布代次；S3 不提供任意跨 key 的共同原子更新。

一种教学发布协议是：先写带新代次的不可变键，核对全部对象与校验信息，再发布指向这一组的 manifest 或业务指针；读者固定该次引用的 key/version，不能每读一项都重新选择“最新”。并发发布还需在实际接受指针的位置检查前置版本，旧代次回收必须等过在途读取、回退和保留窗口。它与[索引重建与切换](index-rebuild-watermarks-and-cutover.md)共享“准备完整集合后再发布引用”的思路，但不是所有对象存储自带的事务。

如果业务指针在数据库，上传与修改记录仍是两个系统动作。对象存在但记录未提交、记录已提交但后续处理未完成，都需要可恢复的状态和核对责任；可在本地事务内记录需要继续推进的意图，见[Transactional Outbox](../messaging/transactional-outbox.md)。[数据库事务](../../glossary/database.md#database.isolation)不会自动包住 S3 上传或后续防护检查。

## 条件写检查当前对象，不是先读后写的承诺

[S3 条件写](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)提供写入时的前置条件。`If-None-Match: *` 可以保护“当前不存在时才创建”；`If-Match` 根据当前 ETag 比较后更新。单独 HEAD 查不到再 PUT，没有把判断与写入连起来，两个写者都可能看到不存在。

教学设定：当前对象 ETag 为 E1，A、B 都读到它；A 带 If-Match E1 更新并成功，当前 ETag 变成 E2 且 E2 不同于 E1；随后 B 仍带 E1，前置条件失败。B 应重新读取并按业务规则合并或拒绝，不能删除条件后盲写。实际并发删除、分段完成等路径还可能产生不同错误，处理需按 API 与客户端核对。

ETag 应作为不透明验证器使用，不能假定它是递增版本，或可以检测每次修改及所有元数据变化；重复内容等情形也不能靠一个验证器证明完整变更历史。[完整性文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html)解释 multipart、加密方式与元数据变化下的 ETag 限制。要确认完整字节，指定校验算法与覆盖范围；要读取不可变版本，则明确 version ID，而不是把这些标识互换。

## 分段上传要跨过完成边界，再谈业务可见

Multipart upload 通过 upload ID 组织多片上传，完成请求按 part number 拼成对象；片传输顺序不等于最终对象顺序。机制见[分段上传概览](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)。教学例子：200 MiB 拆成四片，每片 50 MiB，前三个已成功片中的某一片无需因另一片失败而全部重传；若仅第 3 片需要重试且其余三片仍可复用，重传的是 50 MiB，未计协议开销或其他失败。

| 阶段 | 应记录的状态 | 尚不能声明的结果 |
| --- | --- | --- |
| 创建上传 | 业务上传身份、目标 key、upload ID、预期内容范围 | 对象已经完整可读 |
| 上传各片 | part number、对应 ETag/校验、重试进度 | 所有片都被接受，或附件已发布 |
| 完成上传 | 完整片清单、完成操作结果、所得对象/版本信息 | 业务内容已检查、数据库记录已提交 |
| 业务发布 | 所有者、校验结果、允许的对象版本和可见状态 | 任意旧链接、缓存和副本已被撤销 |

所有片传完也不等于完成请求已成功。尤其 [CompleteMultipartUpload API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)可以先返回 HTTP 200 响应头，再在响应内容中表示错误；直接调用需要解析完整结果，使用 SDK 也要按其最终结果处理。若响应中断而结果未知，先用 upload ID、目标版本和业务操作记录核对，不能直接判失败后发布另一次重复业务动作。

片的 ETag、最终对象 ETag和全对象 checksum也不是同一个量；multipart ETag 不能通用地当作整文件 MD5。未完成上传的片需要主动完成或中止，并安排遗留上传清理；它们不会因为浏览器关掉就自动完成业务回滚。容量、在途片数、重试与保留期都要有界。

## 预签名 URL 转移一种受限请求能力

[预签名 URL 文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)将这种 URL 视为持有者可使用的访问能力。签名绑定请求的目标、方法及相关签名参数；最终访问还受签发主体的有效凭据和当前存储策略约束。它不是让下载者成为该签发主体的完整登录会话，也不会自动查询业务数据库中的最新对象权限。

因此服务应在签发时检查当前用户、租户、对象、动作及目标版本，限制可用期限与请求范围。签发凭据有权写整个桶，不意味着业务用户也可任选 key；上传到已存在的同名 key 还可能覆盖对象。上传入口可使用受控的新 key 和对应业务上传记录，完成后按实际对象重新核对版本、大小、内容与归属，再转为可发布状态。客户端声明的文件名或 Content-Type 不能单独证明内容符合业务规则。

预签名 URL 通常可在有效期间重复使用，不能仅凭“含签名”声明一次性。复制到日志、聊天或分析参数中，也会把该能力一同传播。已经下载的字节不会因后来链接到期被追回；若前方还有 CDN，缓存身份、复用和失效另见[CDN 与 WAF](../networking/cdn-edge-caches-and-waf-boundaries.md)。

## 到期、撤销和正在下载需要不同判断

纸面设定：以服务检查的时间为准，12:00 签发一个写明 12:10 到期的 GET URL，但签发临时凭据在 12:06 到期；没有其他更早拒绝条件。它用于发起新请求的有效期受两者较早时间约束，为 6 分钟，而不是 10 分钟。存储策略或凭据被撤销还可能让请求更早被拒绝，不能把配置期限解释成必然可用时长。

S3 在请求时检查期限：12:05:59 已开始并被接受的大文件下载，可能在 12:06 之后继续；连接断开后 12:06:01 才重新发起的请求则已超出此示例凭据期限。这个结论依据[预签名期限与在途下载说明](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html#PresignedUrl-Expiration)，不是实测，也不承诺所有其他故障下传输都完成。

只在业务数据库中撤销用户权限，若下载直接由 S3 接受且存储策略/凭据未变，不会自动让已签 URL 同步失效。若业务要求更快撤销，需要设计更短能力期限、受控下载入口或可实际作用于存储接受面的拒绝策略，并测量传播与在途行为；见[密钥与凭证生命周期](../security/secrets-credentials-rotation-and-revocation.md)。“不再签发新链接”“拒绝旧链接的新请求”“终止已接受传输”是三项不同验收。

## 版本保留也不是完整备份或业务删除

[S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)可保留同一 key 的多个版本。启用版本的桶中，不指定具体版本的一般删除会建立 delete marker；旧版本可能仍在，有相应权限的版本读取仍须单独治理。删除某个具体版本、暂停版本机制、生命周期清理又是其他操作，不能用一条“已删除”概括所有状态。

版本保留可以帮助恢复覆盖错误，但不证明独立[故障域](../../glossary/reliability.md#reliability.fault-domains)备份、受损凭据无法删除历史、跨系统记录一致或恢复目标已经达标，见[备份与时间点恢复](../database/backups-and-point-in-time-recovery.md)。业务软删除、存储版本清理、缓存撤回与审计保留期应协调；不得因需要恢复就无限保留可被旧能力访问的敏感内容。

## 五道自检与核查范围

1. bucket/key、version ID、ETag、checksum 和业务附件 ID 各定位什么？为什么前缀文件夹与复制后删除不等于文件系统原子重命名？
2. 两个对象各自强一致，为什么读者仍会读到混合发布？不可变键、manifest 和数据库指针各需什么发布与回收边界？
3. A/B 都读取 E1 时，先 HEAD 再 PUT 与 If-Match 有什么差别？为什么 ETag 既不能通用当 MD5，也不能当完整变更历史？
4. 四片各 50 MiB 的上传为什么可只重传一片，却不能以“片全传完”或“看到 HTTP 200 头”宣称成功？upload ID、完成结果和业务发布各需什么记录？
5. 12:00/12:10 URL 与 12:06 凭据到期的例子中，新请求窗口是多少？旧能力、在途下载、业务撤销和 delete marker 又各留下哪些访问或恢复责任？

核查日期：2026-10-23。以下均为 AWS 官方滚动页面的当日快照，只取 S3 通用桶的相关机制；没有核查某个 SDK 版本、桶配置或 S3 兼容服务的实际符合性。

| 一手资料 | 实际核查部分 |
| --- | --- |
| [对象命名](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html)、[复制与移动](https://docs.aws.amazon.com/AmazonS3/latest/userguide/copy-object.html) | key/前缀、平面命名与复制/删除步骤，未扩展目录桶特定重命名能力 |
| [S3 一致性模型](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel) | 对象 PUT/DELETE/GET/LIST、单键原子与跨键限制，不把桶配置传播、CDN或数据库并入同一保证 |
| [条件写](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)、[完整性校验](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html) | 当前对象前置条件、并发错误、ETag/元数据及 multipart/加密差异、checksum 范围 |
| [Multipart 概览](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)、[CompleteMultipartUpload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html) | upload ID/片序号/片清单、完成/清理，以及 200 头内嵌错误；未调用 API |
| [预签名 URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) | 可重复能力、签发主体权限、期限/临时凭据、请求开始与在途下载边界 |
| [Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) | 新旧版本、一般删除标记、版本保留与生命周期，未执行恢复 |

200 MiB、50 MiB、E1/E2、时间点及发布流程为教学假设。未创建桶/凭据、签发或使用真实 URL、上传/复制/删除对象、执行条件竞争、分段重试/清理、版本恢复、策略撤销或 CDN/数据库集成；未测量成本、吞吐、传播时间和恢复结果。
