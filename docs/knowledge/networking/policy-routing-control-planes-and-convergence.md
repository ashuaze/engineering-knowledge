---
id: "kb-networking-policy-convergence"
title: "策略与动态路由：选路、转发与收敛为什么是三件事"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分策略规则、路由信息与转发表，用双出口推演解释跨表选择、BGP 本地策略、异步收敛及现存连接边界。"
created: "2026-10-26"
updated: "2026-10-26"
last_verified: "2026-10-26"
verification: "source-checked"
prerequisites: ["kb-networking-ip-routing"]
related: ["kb-networking-nat-proxy-lb", "kb-networking-ipv6-source-protection", "kb-networking-path-mtu", "kb-reliability-fault-domains-recovery"]
tags: ["policy-routing", "bgp", "control-plane", "convergence"]
---

# 策略与动态路由：选路、转发与收敛为什么是三件事

学习入口：主[路由表](../../glossary/networking.md#networking.routing)里明明有更精确的路由，为什么流量走了另一个出口？[BGP](../../glossary/networking.md#networking.policy-routing) 已经收到备用路径，为什么业务还没有恢复？需要分别回答：本次查询用什么规则、设备实际安装了什么、沿途各节点是否都已完成更新。

前置：[网络分层、IP 与路由](network-layers-ip-subnets-and-routing.md)。本文以 Linux 普通单播策略查询和 RFC 4271 的 BGP 基础模型为范围；不提供设备配置模板，也不穷举 IGP、BGP 扩展或厂商选路顺序。表格、地址和时序是纸面设计，没有修改路由、建立 BGP 会话或执行切流。

## 先区分信息、选择与实际转发

控制平面（control plane）学习路由并按策略选择；数据平面（data plane）使用已安装状态处理分组。RIB（Routing Information Base）表达路由信息，FIB（Forwarding Information Base）表达用于转发的查找结果。具体产品可能融合数据结构或使用多个软硬件表，不能从两个缩写推出两个独立[进程](../../glossary/systems.md#systems.execution-units)。

| 观察对象 | 能回答的问题 | 尚不能证明 |
| --- | --- | --- |
| 协议收到的候选路径 | 邻居向本机通告了什么 | 已被本机接受或选中 |
| 本地策略选出的路由 | 本机愿意使用哪条路径 | 硬件下发完成、下一跳可达 |
| 生效的转发表与策略规则 | 给定查询条件会选择什么出口 | 回包能返回、服务能响应 |
| 邻居状态、实际收发与端到端结果 | 分组在哪一段继续或停止 | 任意其他来源、大小、协议也同样可用 |

BGP 的 Adj-RIBs-In、Loc-RIB、Adj-RIBs-Out 分别对应输入、当地选择和对外通告的概念视图；不要求实现保存三份完整副本，见 [RFC 4271 §3.2](https://www.rfc-editor.org/rfc/rfc4271.html#section-3.2)。FIB 下发与业务恢复仍要按具体设备观测。

## 最长前缀匹配有查询上下文

Linux 的 RPDB（Routing Policy Database，路由策略数据库）先按规则优先级检查选择器和动作，数字越小越先检查。源地址、目的地址、入接口、标记等都可能影响查询。一次表查询若没有得到终止结果，可以继续后续规则；成功得到普通单播路由时便停止。依据见 [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html#DESCRIPTION)。

下面明确假设：分组源地址已经是 `192.0.2.10`，目的地址为 `203.0.113.9`；最前面的 local 表没有匹配；没有 VRF、额外标记规则、抑制器、throw 或拒绝路由；网关能在对应链路解析。

| 规则顺序 | 匹配条件与动作 | 对应表中的普通单播路由 |
| --- | --- | --- |
| 100 | 源属于 `192.0.2.0/24`，查询表 100 | `0.0.0.0/0` 经出口 A |
| 32766 | 任意分组，查询 main 表 | `203.0.113.0/24` 经出口 B，以及默认路由 |

本次查询先匹配规则 100，在表 100 找到默认路由，结果是出口 A。main 表的 `/24` 不参加一次跨表“谁最长”的全局竞赛。如果表 100 没有匹配且允许继续，才可能走到 main。`throw`、`blackhole`、`unreachable` 等动作含义不同，见 [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html#DESCRIPTION)。

这个例子也不能直接预测一个未绑定源地址的本机新连接：源地址选择、接口和路由查询可能互相影响。诊断时应记录源/目的地址、网络命名空间、规则、表、标记以及本机发出还是转发。`ip route get` 可表达指定条件下的一次解析，但查询结果不等于已经发包或验证回程。

## BGP 传播可达性，按本地政策选择

BGP（Border Gateway Protocol）在自治系统之间交换前缀可达性和路径属性。AS_PATH 是经过的自治系统信息，不能当作逐台路由器轨迹、物理距离或 RTT。接受策略、偏好、下一跳可解析性和决胜规则共同约束选择；“AS 数更少”并非一条全网统一的最高优先级承诺。基础范围见 [RFC 4271 §3、§5、§9.1](https://www.rfc-editor.org/rfc/rfc4271.html#section-9.1)。

例如本机有两条到同一前缀的候选：A 路径三个 AS，B 路径两个 AS。仅给这两个数字，无法推出选 B。题目还必须给出接收政策、本地偏好、下一跳状态及实现所用决胜规则；若讨论对外通告，再检查导出政策。BGP 的本地政策选路与 Linux 的按源查询表是不同层次的机制，可以出现在同一台设备上，不能互相替代。

## 收敛是多节点、多阶段的过程

假设 A 出口失效，备用 B 仍可用。以下是教学分解，实际阶段可以重叠：

1. 链路或协议先发现变化；物理链路正常不代表远端前缀仍可达。
2. 本机撤销失效候选、重选下一跳，并把结果安装到转发状态。
3. 邻居按各自收到的信息、政策和时机重选；相关更新继续传播。
4. 去程、回程、访问控制与有状态中间设备共同决定业务是否恢复。

RFC 4271 的选择、通告和更新过程不提供全网同时生效的事务。由这个模型可推演：某设备已经更新时，另一设备仍可能用旧下一跳，出现短暂丢包、绕行，特定拓扑还可能形成暂态环路。不能把一次撤销消息的时间直接当作业务中断时长，也不能仅靠缩短一个计时器保证恢复上界。

切到 B 后，旧 [TCP](../../glossary/networking.md#networking.transport) 连接是否继续还取决于地址、[NAT](../../glossary/networking.md#networking.nat)/防火墙状态和两端协议状态。新出口能发包不会自动复制 A 的连接跟踪，回程也未必经过同一处，见 [NAT 与代理](nat-proxies-and-l4-l7-load-balancing.md)。应把“控制选择完成”“转发完成”“新连接成功”“旧连接继续”作为不同验收项。

## 如何组织排查证据

把同一次业务尝试的查询条件和时间线放在一起：候选到达、政策接受、下一跳解析、实际安装、首个成功双向报文与应用结果。逐段判断证据支持哪一步。不要为了让路由表看起来一致就删除规则或反复重启会话；配置变更的效果需要独立验证。

## 自检

1. 纸面双出口例子中为什么选择 A，main 的 `/24` 为什么没有胜出？
2. 同样的目的地址，换来源地址或网络命名空间，结果为什么可能不同？
3. 两条 BGP 路径分别有三个和两个 AS，现有信息能否决定选路？还缺什么？
4. 邻居已经收到路由撤销，能否证明所有设备的转发状态已经切换？
5. 新出口上的新连接成功，为什么不能证明经旧 NAT 的连接可以继续？

## 来源与核查

2026-10-26 核查以上 Linux 手册与 RFC 4271 的规则查询、RIB、属性和决策过程。Linux 手册为滚动文档，具体系统与路由工具版本需另行核对；RFC 仅用于所引基础模型。本文为 source-checked 概念文章，未执行真实查询、路由下发、协议收敛或业务故障实验。
