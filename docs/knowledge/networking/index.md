<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机网络与协议

建议优先级：P0。目标：从域名解析到应用响应，分层解释连接和传输。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

为什么客户端超时不能证明后端执行失败？

## 已有正文

- [HTTPS 请求链路：从地址输入到响应可用经历了什么](https-request-lifecycle.md)：把解析、连接、安全传输、HTTP、服务端处理与页面呈现分层，建立请求排查的共同语言。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| OSI / TCP-IP Model | 网络职责分层和封装。 |
| IP / TCP / UDP | 寻址、字节流可靠传输和数据报。 |
| DNS / TTL | 域名解析与记录缓存有效期。 |
| TCP Handshake | 连接建立及连接状态。 |
| Flow Control / Congestion Control | 接收方能力约束与网络拥塞调节。 |
| TLS / HTTPS / PKI | 传输加密、身份校验与证书信任。 |
| HTTP/1.1 / HTTP/2 / HTTP/3 | HTTP 传输机制和多路复用差异。 |
| QUIC | 基于 UDP、集成安全机制的传输协议。 |
| Keep-Alive / Connection Reuse | 连接复用、空闲管理和连接成本。 |
| Proxy / Reverse Proxy | 代理客户端或服务端接收请求。 |
| Load Balancer / L4 / L7 | 按传输层或应用层信息分发流量。 |
| CDN / WAF | 内容边缘分发与应用层请求防护。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
