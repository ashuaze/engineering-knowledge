<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 后端 API 与服务

建议优先级：P0。目标：定义契约、失败语义、[幂等](../../glossary/api.md#api.idempotency)和资源边界。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

请求成功但响应丢失，客户端如何安全[重试](../../glossary/api.md#api.retries)？

## 已有正文

- [API 风格与网关：接口形状怎样连接契约与执行边界](api-styles-contracts-and-gateway-boundaries.md)：以订单需求区分 [REST](../../glossary/api.md#api.styles)、RPC、gRPC 与 GraphQL 的抽象层，说明契约、查询成本、流式调用及网关和业务服务的责任边界。
- [HTTP 条件请求：缓存验证与并发更新怎样共用版本依据](conditional-requests-and-cache-validation.md)：用 [ETag](../../glossary/api.md#api.conditionals)、If-None-Match 与 If-Match 区分 304 缓存验证和 412 条件更新，解释强弱验证器、原子比较及身份缓存边界。
- [HTTP 契约与分页：接口能调用，为什么仍会漏数据](contracts-and-pagination.md)：从方法语义和输入输出契约出发，解释[稳定排序](../../glossary/algorithms.md#algorithms.sorting-search)、Offset 与[游标分页](../../glossary/api.md#api.pagination)、并发变化及[兼容性](../../glossary/api.md#api.versioning)边界。
- [优雅关闭与请求排空：停止接流为什么仍有请求进来](graceful-shutdown-draining-and-inflight-outcomes.md)：区分摘流传播、本地接纳、连接排空和业务完成，解释终止预算、GOAWAY、超期处置与不确定结果。
- [实验：验证本地订单写入的幂等性](idempotency-lab.md)：用 SQLite 和故障注入验证并发去重、回滚与提交后响应丢失。
- [幂等性：给重复请求一个稳定的业务结果](idempotency.md)：在明确的作用域、保留期和事务边界内，避免重试产生重复业务效果。
- [限流、并发限制与配额：分别在限制什么](rate-limits-concurrency-and-quotas.md)：区分接纳速率、同时占用与累计用量，解释突发、身份、分布式计数及拒绝重试的契约。
- [资源模型与输入边界：字段合法为什么仍不能保存](resource-models-input-validation-and-write-boundaries.md)：区分资源身份、表示、操作与异步任务，分层检查输入形状、字段权限、状态转换及上下文处理。
- [Webhook 签名与重放：验签成功，为什么还不能直接执行业务](webhook-signatures-replay-and-delivery.md)：沿签名覆盖字节、密钥轮换与时间窗口区分来源验证和防重放，再用持久接纳、幂等消费及响应丢失解释可靠回调。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| [REST / RPC / GraphQL / gRPC](../../glossary/api.md#api.styles) | API 架构约束、调用模型、查询规范与框架的对照组。 |
| [Resource Modeling](../../glossary/api.md#api.resource-model) | 资源标识、状态变化与操作语义。 |
| [HTTP Method / Status Code](../../glossary/api.md#api.http-semantics) | 方法意图和响应结果的协议表达。 |
| [Idempotency](../../glossary/api.md#api.idempotency) | 同一操作重复执行时约束业务效果。 |
| [Pagination / Cursor](../../glossary/api.md#api.pagination) | 按偏移或位置边界分页。 |
| [API Versioning / Compatibility](../../glossary/api.md#api.versioning) | 契约演进与调用方兼容。 |
| [OpenAPI / Protobuf / JSON Schema](../../glossary/api.md#api.contracts) | 接口描述与结构约束。 |
| [Validation / Sanitization](../../glossary/api.md#api.validation) | 校验输入及按上下文处理危险内容。 |
| [Timeout / Retry / Backoff / Jitter](../../glossary/api.md#api.retries) | [截止时间](../../glossary/reliability.md#reliability.retry-budget)、重试和随机退避。 |
| [Rate Limiting / Quota](../../glossary/api.md#api.limits) | 速率约束与时间窗口内的用量额度。 |
| [API Gateway](../../glossary/api.md#api.gateway) | 在边界统一承接路由、凭证验证和流量治理的入口层。 |
| [Webhook](../../glossary/api.md#api.webhook) | 基于 HTTP 回调的异步事件通知。 |
| [Connection Pool](../../glossary/api.md#api.pool) | 复用有限连接并控制等待。 |
| [Graceful Shutdown](../../glossary/api.md#api.shutdown) | 停止接流、处理在途任务和释放资源。 |
| [Problem Details](../../glossary/api.md#api.problem-details) | HTTP API 的结构化问题详情表示，以稳定的问题类型关联机器处理与人类说明。 |
| [ETag / Conditional Request](../../glossary/api.md#api.conditionals) | 以表示验证器表达读取或修改的前提，区分缓存验证与条件保存；不替代[授权](../../glossary/security.md#security.identity)、幂等协议或跨资源不变量。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
