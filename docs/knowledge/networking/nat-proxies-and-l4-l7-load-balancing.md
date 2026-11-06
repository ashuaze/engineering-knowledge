---
id: "kb-networking-nat-proxy-lb"
title: "NAT、代理与负载均衡：流量经过入口后谁在与谁通信"
kind: "concept"
domain: "networking"
status: "evolving"
summary: "区分地址转换、连接代理与流量分配，沿元组、TLS、健康探测、摘流和来源信任链解释入口的能力与失败边界。"
created: "2026-10-22"
updated: "2026-10-26"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-https-request", "kb-networking-connection-states"]
related: ["kb-networking-ip-routing", "kb-networking-http-pools", "kb-security-ssrf", "kb-api-idempotency", "kb-devops-declarative-health", "kb-security-mtls-service-identity", "kb-api-styles-gateway", "kb-networking-cdn-waf", "kb-networking-policy-convergence"]
tags: ["nat", "proxy", "load-balancing", "tls", "forwarded"]
---

# NAT、代理与负载均衡：流量经过入口后谁在与谁通信

学习入口：客户端只连一个入口地址，为什么应用日志里的来源地址、连接数和 [TLS](../../glossary/networking.md#networking.tls) 对端都可能改变？先分开三个问题：数据包的地址是否被改写，连接由谁终止，以及下一份流量分配给哪个后端。一个设备可以同时承担这些职责，名字不能代替实际路径。

前置：[HTTPS 请求链路](https-request-lifecycle.md)、[TCP 与 TLS 连接状态](tcp-tls-and-connection-states.md)。地址、子网与[下一跳](../../glossary/networking.md#networking.routing)的关系可对照[网络分层、IP 与路由](network-layers-ip-subnets-and-routing.md)。本文以 IPv4、[TCP](../../glossary/networking.md#networking.transport) 与 HTTP 的常见部署为主；地址与端口均为纸面教学数据，没有发起目标请求、配置网络或部署代理。

多出口选路与异步更新见[策略与动态路由](policy-routing-control-planes-and-convergence.md)。转发表改变不自动迁移 [NAT](../../glossary/networking.md#networking.nat) 状态或现存连接。

## NAT 改写包的定位信息，不自动成为应用代理

[NAT](../../glossary/networking.md#networking.nat) 在地址域之间转换地址；基本 NAT 主要转换 IP 地址，NAPT 还转换 TCP/UDP 端口，使多个内部端点能够共用外部地址。本文采用 [RFC 2663](https://www.rfc-editor.org/rfc/rfc2663.html)与 [RFC 3022](https://www.rfc-editor.org/rfc/rfc3022.html)的传统 IPv4 模型，不把它们当成所有现代 NAT 行为的完整规范。

工程中的 SNAT 表示改写源地址，DNAT 表示改写目的地址；转换也可能涉及端口，二者还能按路径组合。它们描述改了哪一侧字段，NAPT 则强调地址与端口共同转换，并非互斥分类。术语与连接关联处理可参考 [Netfilter NAT HOWTO](https://www.netfilter.org/documentation/HOWTO/NAT-HOWTO-5.html)；该资料面向历史 Linux 2.4，只用来解释机制，不提供当前配置命令。

纸面 NAPT 映射如下，所有行均为 TCP，远端固定为 `203.0.113.20:443`：

| 方向与观察位置 | 源端点 | 目的端点 |
| --- | --- | --- |
| 主机甲出站，转换前 | `10.0.0.8:51000` | `203.0.113.20:443` |
| 主机甲出站，转换后 | `198.51.100.10:40001` | `203.0.113.20:443` |
| 主机乙出站，转换后 | `198.51.100.10:40002` | `203.0.113.20:443` |
| 甲的响应到达转换器 | `203.0.113.20:443` | `198.51.100.10:40001` |
| 甲的响应还原后 | `203.0.113.20:443` | `10.0.0.8:51000` |

设乙的内部端点是 `10.0.0.9:51000`。两台主机可以使用相同内部端口，但本例为同一远端分配不同外部端口，返回时才能找到相应映射；不能只靠外部 IP 区分甲乙。

传统有状态 NAT 需要保存转换关联并处理返回流量，相关头部校验和也需调整。若回程经过不具备相应状态的节点，或[故障切换](../../glossary/reliability.md#reliability.dr)丢失状态，已有通信可能失效；NAT 本身不为两端另建两条 TCP 字节流。返回路径与状态共享限制见 [RFC 3022 §1、§3–4](https://www.rfc-editor.org/rfc/rfc3022.html#section-3)。映射与连接跟踪状态也不是业务会话或用户身份；地址隐藏不能替代访问策略。

转换状态还有自己的生命周期：端点仍显示连接已建立，不代表中间 NAT 尚保留空闲连接的映射。TCP NAT 的状态维护与空闲超时要求见 [RFC 5382 §5](https://www.rfc-editor.org/rfc/rfc5382.html#section-5)；具体设备的容量、超时与保活行为仍需按实现核对，本文不提供通用参数值。

## 代理改变连接边界，负载均衡描述分配职责

HTTP [正向代理](../../glossary/networking.md#networking.proxy)通常由客户端选择；反向代理在客户端看来代表服务端接收请求，再访问后端。RFC 的 gateway 在这一语境也称反向代理，与 IP 路由里的默认网关不是同一种职责。HTTP tunnel 则在连接之间盲转发数据，不参与隧道内的 HTTP 消息解释。定义见 [RFC 9110 §3.7](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.7)。

TCP 全代理可以接受客户端连接，再建立独立的后端连接：两段有各自的序号、缓冲、关闭和超时。HTTP 反向代理还能在应用层转发请求，并复用后端连接；因此前端连接数、后端连接数与请求数不必一一相等。HAProxy 的 `mode tcp` 与 `mode http` 分别提供流转发和 HTTP 分析能力，见 [HAProxy 3.2.26 配置手册：代理模式](https://docs.haproxy.org/3.2/configuration.html#4)。

“[L4](../../glossary/networking.md#networking.load-balancer) 负载均衡”主要指使用地址、端口、协议及连接相关信息分配流量；“L7”可按 HTTP 的主机、路径或头部等应用信息选择目标。它们不是“是否一定新建 TCP 连接”的分类：

| 实现方式 | 转发与返回路径要点 |
| --- | --- |
| 基于 NAT 的分流 | 改写目的端点，必要时再改源端点；返回方向要经过相应转换 |
| TCP 全代理 | 接受前段连接，再连接后端；响应经代理返回 |
| 直接服务器返回（DSR） | 典型直接路由方案保留 VIP，后端接受该 VIP 并直接向客户端返回 |
| 隧道分流 | 将原包封装送给后端；后端解封装后处理，返回路径按所选方案设计 |

Linux Virtual Server 的[直接路由原理](https://www.linuxvirtualserver.org/VS-DRouting.html)和 [IP 隧道原理](https://www.linuxvirtualserver.org/VS-IPTunneling.html)提供了后两种一手例子；它们是历史架构说明，内核构建步骤不在本文适用范围。DSR 的 VIP 接收、二层邻居应答与回程路由都有部署条件，不能只把“返回绕过入口”当成随时可切换的优化。

## 用同一个 VIP 比较 DNAT 与全代理

纸面设定：客户端为 `198.51.100.25:52000`，虚拟服务地址 VIP 为 `203.0.113.10:443`，本次选中的后端为 `10.0.0.21:8443`。

| 模式 | 客户端发出的连接目标 | 后端观察到的端点 |
| --- | --- | --- |
| 仅 DNAT，且回程经转换器 | `198.51.100.25:52000 → 203.0.113.10:443` | `198.51.100.25:52000 → 10.0.0.21:8443` |
| 普通 TCP 全代理，本例不启用透明源地址 | 同上 | `10.0.0.5:41000 → 10.0.0.21:8443` |

DNAT 行的后端响应先发往客户端；经过转换器后，响应源恢复为 `203.0.113.10:443`。若后端绕过转换直接以 `10.0.0.21:8443` 返回，便不满足本例客户端原来连接的远端元组。全代理行则由后端回复代理，再由代理通过前段连接交付；`10.0.0.5:41000` 只是示例中分配的出站端点。

这是两种已限定的模型，不是所有产品的默认值。透明代理、额外 SNAT、DSR 与封装会改变观察结果。排查前应同时记录每段协议、源/目的地址及端口，再核对实际路由与转换状态。

若把同一 VIP 例子改为上述典型 DSR，且没有另加地址或端口转换，后端接收的仍是 `198.51.100.25:52000` → `203.0.113.10:443`；它需要接纳 VIP 的 443 端口，不能直接沿用 DNAT 例的 `10.0.0.21:8443`。保留原包的 IP 隧道方案在解封装后也看到这个内层元组，外层 IP 才负责把包送到选中的后端；回程按相应方案设计。这是根据 [LVS 直接路由的帧改写机制](https://www.linuxvirtualserver.org/VS-DRouting.html)与 [IP 隧道的原包封装机制](https://www.linuxvirtualserver.org/VS-IPTunneling.html)所作的纸面推演，不涵盖另加的重定向或透明代理策略。

## TCP 终止与 TLS 终止需要分别画线

| 安全层模式 | TLS 对端与入口可见内容 |
| --- | --- |
| TLS 透传 | TLS 在客户端与后端之间建立；即使中途有 TCP 全代理，入口也不因此取得 HTTP 明文 |
| 入口终止 TLS，后段明文 | 客户端[认证](../../glossary/security.md#security.identity)入口；入口可处理 HTTP，后段不受这条 TLS 连接保护 |
| 入口终止，再对后端建立 TLS | 两段独立安全连接；入口仍可见明文，后段必须单独验证后端身份 |

TLS 保护的是其端点之间的通信，不会因某一段加密而自动覆盖整条代理链，见 [RFC 8446 §1](https://www.rfc-editor.org/rfc/rfc8446.html#section-1)。重新加密还需核对信任根、预期服务名称与认证策略；不能把“使用 HTTPS 访问后端”直接当作认证配置正确。NGINX 分别提供 `proxy_ssl_verify`、`proxy_ssl_name` 与 `proxy_ssl_server_name` 等配置，见 [HTTP 代理模块](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_ssl_verify)。

透传也不等于所有信息完全不可见：在 ClientHello 字段可见的条件下，可按 SNI 或客户端声明的 ALPN 做预读选择，而无需解密 HTTP。NGINX 的 [`ssl_preread` 模块](https://nginx.org/en/docs/stream/ngx_stream_ssl_preread_module.html)说明了这种能力；它不授予按加密后的 URL 路径路由的能力，也不应假定每种部署都能看到相同字段。

## 分配算法、健康和会话保持有各自的盲区

| 机制 | 分配依据或收益 | 剩余限制 |
| --- | --- | --- |
| 轮询 | 轮流选择合格后端 | 请求成本不等时，数量接近不代表负载相等 |
| 权重 | 调整预期分配比例 | 不是每段短窗口的严格比例，也不是实时剩余容量 |
| 最少连接 | 优先活动连接较少的后端 | 连接数不等于 CPU、[排队](../../glossary/performance.md#performance.queueing)或多路复用请求数 |
| 会话保持 | 用 [Cookie](../../glossary/security.md#security.sessions)、源地址等线索偏向原后端 | 可能加剧倾斜；不能复制状态或使后端故障后的会话自动恢复 |

基本选择机制见 [NGINX：HTTP 负载均衡](https://nginx.org/en/docs/http/load_balancing.html)；具体 `least_conn` 与服务器组行为见 [NGINX upstream 模块](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#least_conn)。表中的成本判断是对这些选择依据的工程推论，不是性能对照结果。共享 NAT 后的许多用户可能拥有同一外部 IP，因此基于 IP 的保持也不等于按用户公平分配。

主动探测按约定间隔发送测试，被动探测从实际流量错误取得信号；连续失败与恢复阈值会影响摘除和恢复时间。TCP 端口可连接只覆盖较窄的条件，HTTP 检查也只检查它经过的路径。HAProxy 的[健康检查说明](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/)分别描述这些机制；探测通过不能保证所有业务依赖、租户或下一请求均正常。部署侧的就绪、存活与[启动探针](../../glossary/reliability.md#reliability.probes)继续见[声明式部署与健康探针](../devops/declarative-deployments-and-health-probes.md)。

## 摘流不是立即结束已有工作

摘流应明确停止的是新连接、新 HTTP 请求还是新流，以及会话保持是否仍能选择该后端。例如 HAProxy 3.2.26 手册的 `drain` 状态仍允许经持久性选择的新连接，不能把状态名称理解为“从此零流量”，见[服务器管理状态](https://docs.haproxy.org/3.2/configuration.html#5.2-agent-check)。已有 TCP [长连接](../../glossary/networking.md#networking.keepalive)、[WebSocket](../../glossary/frontend.md#frontend.realtime) 或 [HTTP/2](../../glossary/networking.md#networking.http-versions) 流不会仅因调整权重就自动迁到另一后端。

可按业务制定“停止新接纳 → 等待在途工作 → 到期处理剩余连接”的排空协议，并观察每段池、连接和请求状态。[连接池与超时](http-reuse-pools-and-timeouts.md)解释了旧连接为何可能继续访问旧实例；停止本地等待也不证明后端操作已撤销。

代理[重试](../../glossary/api.md#api.retries)还可能放大重复副作用：后端已写入，但入口未收到响应时，换一台后端再发请求仍可能重复执行。NGINX 的 `proxy_next_upstream` 对已发送的非[幂等](../../glossary/api.md#api.idempotency)方法有专门控制，见[重试条件](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream)；具体配置不能取代[应用幂等与结果查询](../api/idempotency.md)。入口超时或返回错误，只说明某段等待失败，不能直接宣布原操作没有发生。

## 来源地址与 Forwarded 是信任链问题

后端看到的 [socket](../../glossary/systems.md#systems.fd-socket) 对端通常是最近一跳；在部分 NAT、透明或 DSR 路径中也可能保留客户端地址。`Forwarded` 可记录 `for`、`by`、`proto`、`host` 等信息，但客户端和中间节点都能影响它。字段名存在不等于内容可信；即使最后一跳可信，它接手之前的整段列表也不自动可信。完整性与保护链路的要求见 [RFC 7239 §8.1](https://www.rfc-editor.org/rfc/rfc7239.html#section-8.1)。

一种可审查的入口策略是：清除或按契约覆盖不可信客户端自带的来源字段，由已验证的入口重新生成；后续仅接收明确受信任中间节点的声明，并限制应用被绕过入口直接访问的路径。使用 `X-Forwarded-For` 等约定也要有相同边界，不能盲取最左值；它与 `Forwarded` 的语法不同，解析规则须分别核对。NGINX 的 [`set_real_ip_from` 与递归处理](https://nginx.org/en/docs/http/ngx_http_realip_module.html)展示了可信发送方配置，但不是所有框架通用的头部解析算法。

客户端 IP 可以作为网络线索，不能替代用户或服务身份。共享出口、地址变化与代理都会改变它；记录可信地址链也不等于获得业务授权。若反向代理允许外部输入任意选择上游，还需要检查 [SSRF 的出口与凭据边界](../security/ssrf-url-resolution-and-egress-boundaries.md)。

代理终止后的服务身份证据见[mTLS 与服务身份](../security/mtls-service-identities-and-trust-boundaries.md)，API 入口如何处理契约与流量见[API 风格与网关](../api/api-styles-contracts-and-gateway-boundaries.md)。转发连接与身份声明各有信任条件，入口治理不能代替执行服务的业务检查。

边缘缓存复用、应用层防护与源站路径的责任继续见[CDN 与 WAF](cdn-edge-caches-and-waf-boundaries.md)。访问入口是否经过防护、缓存命中时谁检查权限，都需要独立核对。

## 自检与核查范围

自检时画出每段源/目的元组、TCP 端点、TLS 端点、路由选择和信任来源，再说明：响应如何返回？后端被摘除后哪些工作仍在？错误发生时谁能证明业务结果？

[CDN](../../glossary/networking.md#networking.cdn-waf) 常涉及边缘缓存与内容分发，WAF 涉及应用请求防护策略；本篇只指出它们可能与代理入口组合，不能从“有负载均衡”推出缓存、攻击识别或访问授权已经成立。缓存键、源站信任、规则误报与绕过路径已在 CDN/WAF 专题展开；实际产品配置与防护效果仍需验证。

核查日期：2026-10-22。实际浏览 RFC 2663/3022 的传统 NAT、RFC 5382 的 TCP NAT 状态、RFC 9110 的代理术语、RFC 7239 的来源链完整性、RFC 8446 的 TLS 端点，以及 HAProxy 3.2.26 配置手册。NGINX 引用为当日滚动文档，未绑定某个二进制版本；Netfilter 与 Linux Virtual Server 页面仅用于历史机制说明，不据此推荐现行操作命令。元组、VIP 和负载限制为纸面模型与工程推论，状态为 `source-checked`；未执行公网或其他目标请求、网络变更、代理部署、抓包、故障注入、性能或跨版本配置验证。
