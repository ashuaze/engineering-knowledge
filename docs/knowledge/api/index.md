<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 后端 API 与服务

建议优先级：P0。目标：定义契约、失败语义、幂等和资源边界。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

请求成功但响应丢失，客户端如何安全重试？

## 已有正文

- [实验：验证本地订单写入的幂等性](idempotency-lab.md)：用 SQLite 和故障注入验证并发去重、回滚与提交后响应丢失。
- [幂等性：给重复请求一个稳定的业务结果](idempotency.md)：在明确的作用域、保留期和事务边界内，避免重试产生重复业务效果。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| REST / RPC / GraphQL / gRPC | API 风格、查询模型与调用协议。 |
| Resource Modeling | 资源标识、状态变化与操作语义。 |
| HTTP Method / Status Code | 方法意图和响应结果的协议表达。 |
| Idempotency | 同一操作重复执行时约束业务效果。 |
| Pagination / Cursor | 按偏移或位置边界分页。 |
| API Versioning / Compatibility | 契约演进与调用方兼容。 |
| OpenAPI / Protobuf / JSON Schema | 接口描述与结构约束。 |
| Validation / Sanitization | 校验输入及按上下文处理危险内容。 |
| Timeout / Retry / Backoff / Jitter | 截止时间、重试和随机退避。 |
| Rate Limiting / Quota | 速率约束与时间窗口内的用量额度。 |
| API Gateway | 统一流量入口和横切治理。 |
| Webhook | 基于 HTTP 回调的异步事件通知。 |
| Connection Pool | 复用有限连接并控制等待。 |
| Graceful Shutdown | 停止接流、处理在途任务和释放资源。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
