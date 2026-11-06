---
id: "kb-networking-connections-lab"
title: "连接生命周期实验：复用、池等待与超时后的状态"
kind: "lab"
domain: "networking"
status: "evolving"
summary: "用真实回环 HTTP/1.1 连接对照七类生命周期场景，保存连接标识、正文摘要和客户端服务端事件。"
created: "2026-10-19"
updated: "2026-10-22"
last_verified: "2026-10-19"
verification: "tested"
prerequisites: ["kb-networking-https-request", "kb-networking-http-pools"]
related: ["kb-networking-dns-caching", "kb-networking-connection-states", "kb-reliability-retry-budgets", "kb-performance-backpressure", "kb-api-idempotency"]
tags: ["http", "connection-pool", "timeout", "lab"]
---

# 连接生命周期实验：复用、池等待与超时后的状态

问题：同一个 HTTP 客户端何时复用连接，什么时候还在池里等待，[超时](../../glossary/api.md#api.retries)后哪一端的状态改变了？本实验于 2026-10-19 在 Node.js 24.16.0 / Windows 11 x64 实际执行七类场景各三次。它使用真实回环 [TCP](../../glossary/networking.md#networking.transport) 与明文 [HTTP/1.1](../../glossary/networking.md#networking.http-versions)；没有 [DNS](../../glossary/networking.md#networking.dns)、[TLS](../../glossary/networking.md#networking.tls)、代理、抓包、HTTP/2/3 或生产压测。

## 装置与控制边界

服务只绑定 `127.0.0.1`，每个场景申请独立临时端口。一个 http.Agent 显式开启 keepAlive，maxSockets、maxTotalSockets、maxFreeSockets 都设为 1；逐次关闭场景另用不复用的请求。服务端为每次实际接受的 [socket](../../glossary/systems.md#systems.fd-socket) 编号，响应头携带这个编号；不能仅凭“连接阶段很快”推断复用。记录中的 req.reusedSocket 是 Node API 提供的标记：池内[排队](../../glossary/performance.md#performance.queueing)后接到前一请求连接的路径也可能为 false，不能单独据此认定没有复用；本实验以服务端连接编号作为判据。

短响应为 `ok:请求标识`，大响应为 65,536 字节的 x。每项完整响应都对照服务端预期长度与 SHA256，并核对状态为 200、协议为 1.1。记录服务端接受连接、收到请求、写出完成或提前关闭，以及客户端取得 socket、收到头、消费正文、结束或错误的事件。

为了控制顺序，暂缓正文的场景在服务端保留显式释放函数；未消费正文的场景由客户端显式开始读取。服务端 keepAliveTimeout 设为 60 秒以避免短实验期间自动空闲回收；空闲关闭实验直接调用 closeIdleConnections，不等待这个时钟到期。空闲通知配置 25ms，每个异步阶段另有 5 秒失败保护。所有数字都是实验参数，不是线上推荐。

## 怎样复现与核对文件

在仓库根目录运行，只需 Node.js 24，无需第三方包或已有服务器：

```bash
node examples/connection_lifecycle/lab.mjs
node examples/connection_lifecycle/lab.mjs --check
```

第一条执行三次重复并覆盖 results.json；第二条每类执行一次，只校验、不覆盖基线，适合持续检查。先备份本轮记录再重新运行。保存最终运行输出后，使用 `node examples/connection_lifecycle/lab.mjs --freeze-manifest` 冻结实现与记录的字节数和 SHA256；摘要匹配只证明文件一致。

- [实验实现](../../../examples/connection_lifecycle/lab.mjs)。
- [原始结果](../../../examples/connection_lifecycle/results/results.json)：环境、参数、21 组请求与服务端记录、连接标识、事件序列和检查状态。
- [最终运行输出](../../../examples/connection_lifecycle/results/run.txt)与[摘要清单](../../../examples/connection_lifecycle/results/manifest.json)。

本轮在获准的沙盒外运行回环监听，未访问远程服务。每组最后释放暂缓响应、销毁客户端 Agent、关闭自建服务与连接，并等待本组服务端 socket 的 close 事件。清理没有修改系统 DNS、hosts 或任何现有服务。

## 七类场景的实际观察

表中每行均重复三次，所列结果每次一致。连接数是该场景服务端实际接受的 TCP socket 数，独立场景间不复用。

| 场景 | 每次请求数 / TCP 连接数 | 关键观察 |
| --- | --- | --- |
| reuse，顺序复用 | 3 / 1 | 完整消费三个响应，服务端连接标识相同 |
| close_each，逐次关闭 | 3 / 3 | 三个请求各自使用不同连接 |
| pool_wait，池内等待 | 2 / 1 | A 正文暂缓时，B 在 Agent [队列](../../glossary/algorithms.md#algorithms.queues)中，未分配 socket，也未到服务端 |
| unread_body，正文未消费 | 2 / 1 | A 已收到头但未消费正文，B 等待；读完 64KiB 后归还名额并复用 |
| idle_close，空闲关闭 | 2 / 2 | 服务端显式关闭空闲连接，客户端观察 close 并移出池后，新请求建立另一连接 |
| timeout_notice，仅通知 | 1 / 1 | 空闲超时触发通知，请求未被销毁；释放暂缓正文后仍正常完成 |
| timeout_destroy，显式销毁 | 1 / 1 | 超时回调显式 destroy，客户端报 LAB_TIMEOUT；服务端响应提前关闭，内存标记仍存在 |

累计发起 42 个请求，39 个完整消费正文，3 个按设计主动销毁；服务端接受 30 个连接。21 组共保存 144 个检查状态，全部通过。该数量是各组断言结果总数，不表示 144 类独立网络故障；没有以耗时快慢作为通过条件。正常场景要求所有请求完整完成且没有错误；只有 timeout_destroy 接受指定的 LAB_TIMEOUT，避免把其他正文失败误算成通过。

## 池等待与正文消费怎样得到证据

pool_wait 先取得 A 的响应头，服务端暂缓正文，再创建 B。此时直接快照 agent.requests 中有一个等待项，B 尚未取得 socket，服务端没有 B 的请求记录。显式结束 A 后，A、B 均正确完成，且 B 的 socket 分配时间不早于 A 的正文 end 事件。

unread_body 使用完整的大正文响应，客户端收到头后不启动消费。快照记录 readableEnded=false、没有 consume 事件，B 也还在队列中。随后显式读取 A，校验 65,536 字节正文与摘要，B 才借到同一个连接。快照没有证明所有正文已经到达客户端或服务端已经写出完成；可支持的结论是“尚未消费完成的响应仍占住该 Agent 的名额”。

这些顺序使用回调与显式释放协调，未靠“先睡几十毫秒”猜测排队状态。它们验证这套 Node.js HTTP/1.1 API 的资源归还契约，不能直接推出浏览器、HTTP/2 会话、数据库池或其他 SDK 的规则。

## 空闲关闭与超时分别证明什么

idle_close 在第一个响应完全消费且 Agent 空闲池有一条连接后，由服务端主动关闭空闲连接。等客户端观察到 close、确认原 socket 已销毁且空闲池为空，才发下一个请求。它验证“已观察到关闭后重连”，没有制造“复用与关闭同时发生”的竞争，也没有测真实空闲超时、[NAT](../../glossary/networking.md#networking.nat) 黑洞或自动重试。

timeout_notice 在服务端暂缓正文、客户端已收到头之后设置 request.setTimeout(25)。通知发生时，记录 destroyed=false、completed=false、服务端仍暂缓响应；回调关闭该计时，随后释放正文并完整读取。这证明通知本身不自动终止这个请求，不证明它覆盖池等待、DNS、安全握手或端到端总时间。

timeout_destroy 使用 POST，先让服务端把标记写入本[进程](../../glossary/systems.md#systems.execution-units) Map，然后发送响应头并暂缓正文。空闲通知回调显式 destroy；记录客户端错误和服务端响应 close 时 writableFinished=false，再核对 Map 中仍有 applied-in-memory 标记。标记写入、收到头、断开和核对的先后均在事件序列里。

标记只是进程内状态，没有[数据库事务](../../glossary/database.md#database.isolation)、持久化、真实付款或业务回滚。它用一个最小反例说明“客户端关闭连接”不具有自动撤销已发生服务端动作的普遍保证；真实副作用仍需按[幂等与结果查询](../api/idempotency.md)处理。

## 记录口径与局限

at_ms 等时间字段使用同一 Node 进程中、每组从零开始的单调计时；只用于核对本组因果顺序，没有把不同组的时间当作同一时间线。server response finish 表示本机将响应交给传输路径，不是客户端已收到；因此完整消费还要看客户端 end、字节数与摘要。

正文结束、请求错误、服务端响应 close 和 socket close 是不同事件。部分失败会产生后续错误，记录保留首次客户端错误及 additional_errors，不用一个事件替代所有状态。最终服务和 socket 清理依赖[运行时](../../glossary/runtime.md#runtime.virtual-machine)事件等待；保留的事件和断言不等于内核状态快照。

本轮未实测 DNS TTL/负缓存、地址切换、TLS/证书/0-RTT、[TCP 握手](../../glossary/networking.md#networking.tcp-handshake)报文、FIN/RST 类型、半关闭、TIME_WAIT、丢包与拥塞、HTTP/2/3、代理排空或生产吞吐。本机[延迟](../../glossary/performance.md#performance.latency-throughput)没有外推为公网性能。尤其不能把 server response close 直接叫作抓到了某种 FIN 或 RST。

## 关联阅读与来源

- [DNS 缓存与地址选择](dns-caching-and-address-selection.md)：本实验固定 IP，没有名称查询证据。
- [TCP 与 TLS 连接状态](tcp-tls-and-connection-states.md)：区分传输关闭、安全协商与业务结果。
- [HTTP 复用与连接池](http-reuse-pools-and-timeouts.md)：从局部观察回到协议和等待边界。
- [Node.js 24.16.0 HTTP API](https://nodejs.org/download/release/v24.16.0/docs/api/http.html)：API 语义核查日期 2026-10-19，运行时版本、实际顺序与结果以随附记录为准。
