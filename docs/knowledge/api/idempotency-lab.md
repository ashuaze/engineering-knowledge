---
id: "kb-api-idempotency-lab"
title: "实验：验证本地订单写入的幂等性"
kind: "lab"
domain: "api"
status: "evolving"
summary: "用 SQLite 和故障注入验证并发去重、回滚与提交后响应丢失。"
created: "2026-10-16"
updated: "2026-10-16"
last_verified: "2026-10-16"
verification: "tested"
prerequisites: ["kb-api-idempotency"]
related: ["kb-api-idempotency", "kb-messaging-outbox"]
tags: ["transactions", "testing"]
---

# 实验：验证本地订单写入的幂等性

## 实验目标与范围

验证同一 scope + key 在本地数据库中最多创建一个订单；相同键不同请求被拒绝；提交后丢失响应可以重试读取同一结果。

实验只使用 Python 标准库 SQLite，不发起网络调用，不模拟真实扣款。它没有实现生产 HTTP 服务、保留期清理或外部支付事务。

## 环境和运行

从仓库根目录执行，要求 Python 3.10+，使用 Python 自带 sqlite3：

```bash
python3 examples/idempotency/lab.py
python3 -m unittest discover -s examples/idempotency -p 'test_*.py' -v
```

实验在临时目录建库并自动清理，不修改你的业务数据库。代码见[实验实现](../../../examples/idempotency/lab.py)与[测试断言](../../../examples/idempotency/test_lab.py)。演示命令会打印 Python/SQLite 版本和运行结果。

## 实现约束

数据库初始化使用 WAL；每次调用建立自己的连接，以 `BEGIN IMMEDIATE` 获取写事务。SQLite 同一时刻只允许一个写事务，其他写连接需要等待或超时。这使实验中的“检查旧结果 → 写订单 → 写结果”受到同一个写事务保护。它不是每个幂等键的细粒度锁方案。

实验仅接受 item 非空字符串和 amount_minor 正整数，先规范化已校验字段再计算指纹。scope 参数在这里由测试传入；真实服务必须在认证授权后由服务端推导。

## 测试断言

| 用例 | 必须保持的不变量 |
| --- | --- |
| 相同键重复请求 | 同一 order_id，数据库只有一行 |
| 八个并发调用同一键 | 所有响应一致，数据库只有一行 |
| 相同键不同金额 | 冲突，原有订单和结果不变 |
| 同键不同 scope | 分别形成独立结果 |
| 写订单后注入异常 | 业务行与幂等结果同时回滚 |
| 提交后模拟响应丢失 | 再次调用读取原结果，订单只有一行 |
| 无效输入 | 不产生任何订单 |
| 规范化后等价输入 | 字段顺序与 item 首尾空白不改变结果，数据库仍只有一行 |

## 已有执行结果与未覆盖边界

2026-10-16 的复核记录为 Python 3.13.13 / SQLite 3.50.4，8 项测试通过，覆盖上表用例。执行范围与临时目录处理见[验证记录](../../../VALIDATION.md)。

测试中的异常注入用于验证事务边界；尚未覆盖进程被强杀、磁盘损坏、断电持久性、忙超时和网络故障。并发测试通过仅证明这些用例在当前环境满足断言，不是全场景证明。

## 下一步实验

将相同业务约束迁移到 PostgreSQL，比较唯一约束竞争、等待时间和事务中止处理；再加入 Outbox relay，验证 Broker 接收后 relay 崩溃的重复窗口。完成前，不给它们标记“已验证”。

## 相关与来源

- [API 幂等性](idempotency.md)
- [SQLite：Transactions](https://www.sqlite.org/lang_transaction.html)
- [Python：sqlite3](https://docs.python.org/3/library/sqlite3.html)

实验机制资料核查日期：2026-10-16；来源机制核查与上述测试执行分别记录。
