---
id: "kb-security-ssrf"
title: "SSRF：服务端代发请求怎样守住网络出口"
kind: "concept"
domain: "security"
status: "evolving"
summary: "沿 URL 解析、DNS 候选地址、实际连接、重定向与代理出口解释 SSRF，说明允许列表、凭据隔离、元数据保护和响应限额的边界。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-https-request", "kb-networking-dns-caching"]
related: ["kb-security-origin-csrf", "kb-security-xss", "kb-security-object-authorization", "kb-reliability-retry-budgets", "kb-networking-nat-proxy-lb"]
tags: ["ssrf", "url-validation", "dns", "egress", "redirects"]
---

# SSRF：服务端代发请求怎样守住网络出口

学习入口：一个“输入图片地址，服务端替我下载”的功能，为什么需要检查服务器的内网权限？因为用户只应选择业务资源，不能因此获得服务端能够访问的所有网络目的地。

前置：[HTTPS 请求链路](../networking/https-request-lifecycle.md)、[DNS 与地址选择](../networking/dns-caching-and-address-selection.md)。本文只讨论防御性机制，域名和地址类别均为纸面模型；没有向示例、内网、元数据服务或任何其他目标发送请求。

## 先写清楚借用了谁的能力

[SSRF](../../glossary/security.md#security.web-attacks) 发生在服务端根据外部可影响的数据发起非预期请求时。URL 预览、远程图片、回调地址等功能可能成为入口；真正跨越的是“外部选择”到“服务端网络权限”的边界。即使不把响应体返回给用户，请求仍可能造成访问或副作用。问题定义与常见入口见 [OWASP API7:2023](https://api-security.owasp.org/editions/2023/en/0xa7-server-side-request-forgery/)。

| 问题 | 需要明确的约束 |
| --- | --- |
| 谁可触发抓取？ | 当前主体是否有权使用该功能、目标是否属于其业务范围 |
| 可以访问什么？ | 业务允许的方案、主机、端口、地址及必要路径 |
| 用谁的身份？ | 抓取[进程](../../glossary/systems.md#systems.execution-units)权限、服务凭据、代理身份与云角色 |
| 请求后发生什么？ | 重定向、重试、响应处理和下游渲染 |

固定合作方的抓取，优先让用户提交资源标识，由服务端选择已登记目标；必须接收 URL 时采用明确允许列表。面向任意公网资源的抓取无法靠小型主机允许列表解决，需要更严格的独立出口和[资源隔离](../../glossary/devops.md#devops.isolation)。这两类需求及应用层、网络层组合见 [OWASP：SSRF 防护](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。

## URL 是结构，不是一段可以随意匹配的文字

使用成熟解析器取得方案、主机、端口和用户信息等字段，并让校验和实际请求使用一致的解析语义。主机规范化、IPv4/IPv6、国际化域名、相对 URL 与分隔符处理都有规则；简单正则、“包含允许域名”或字符串前缀判断，都不能替代结构化解析与目标[授权](../../glossary/security.md#security.identity)。URL 结构与解析规则见 [WHATWG URL Standard](https://url.spec.whatwg.org/)。该标准描述 Web URL；具体服务端客户端是否采用相同规则，仍要核对其实现。

一种便于审查的业务策略是：仅接受绝对 [HTTPS](../../glossary/networking.md#networking.tls) URL，拒绝不需要的用户信息部分，限制端口，按规范化后的主机精确匹配已登记目标。HTTPS 保护传输并按配置验证对端身份，本身不授予服务端访问某个目的地的业务权限。若业务允许子域，要明确定义域名标签边界和子域控制权；“长得像合作方域名”不构成许可。这是策略示例，不是完整 URL 校验实现。

名称许可之后，还要检查实际地址。公网抓取通常需要排除回环、链路本地、私有及其他不允许的特殊用途地址；同时纳入组织自己的内部地址和路由。仅拦截几个常见私网前缀会遗漏类别。地址分类可参考 [IANA IPv4 特殊用途注册表](https://www.iana.org/assignments/iana-ipv4-special-registry/)与 [IPv6 注册表](https://www.iana.org/assignments/iana-ipv6-special-registry/)，但注册表不是业务授权表，也不保证某地址在具体网络中如何路由。

## DNS 检查必须延续到实际连接

域名通过允许列表，并不保证以后始终解析到相同地址。[DNS](../../glossary/networking.md#networking.dns) 重绑定改变名称与地址的对应关系；校验时解析一次，HTTP 客户端连接时再独立解析一次，就会出现“检查的是甲、使用的是乙”的竞态。需要检查 A、AAAA 的所有候选地址，并约束客户端只连接被当前策略允许的地址；重试和地址回退也在范围内。见 [OWASP：域名校验与连接时约束](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html#domain-name)。

以下为不含实际地址的纸面反例：

```text
检查阶段：预览域名 → 候选地址甲 → 被判定允许
连接阶段：同一域名再次解析 → 候选地址乙 → 不在允许范围
若连接仍使用乙，前一次检查没有约束这次请求
```

实现上需要把“已校验地址集合”交给真正建立连接的机制，而不是只把域名再次传下去。GitLab 的 URL 校验说明也强调：忽略校验返回的安全目标，便会失去相应的重绑定保护，见 [GitLab：URL 校验与使用时机](https://docs.gitlab.com/development/secure_coding_guidelines/ruby/#url-blocker--validation-libraries)。

例如 libcurl 的 `CURLOPT_RESOLVE` 支持为指定主机与端口提供地址，但这只是连接配置能力，调用方仍要完成地址授权、有效期、[连接复用](../../glossary/networking.md#networking.keepalive)与重试策略，见 [libcurl：自定义解析](https://curl.se/libcurl/c/CURLOPT_RESOLVE.html)。保留原主机用于 HTTP 与 TLS 身份验证，不能以关闭证书校验来迁就地址固定；相关身份行为见 [curl：指定名称的连接地址](https://everything.curl.dev/usingcurl/connections/name.html#provide-a-custom-ip-address-for-a-name)。

对于“一个域名返回多个地址”的情况，可以按产品策略整组拒绝混合结果，或确保仅已允许候选进入连接调度；无论选择哪种，未校验地址都不能在自动回退时被悄悄采用。没有验证连接层行为的“一次 DNS 检查通过”，不是完备防线。

## 每次跳转都可能改变目的地

最简单的策略是禁用自动重定向。业务确需跟随时，把每一跳当作新目标：解析相对或绝对 `Location`，重新核对方案、主机、端口、地址、策略规定的业务路径和实际连接约束，同时限制跳数及总期限。初始 URL 被允许，不代表它指向的[下一跳](../../glossary/networking.md#networking.routing)也被允许。

重定向还可能改变请求方法、重新发送请求体，或影响凭据传递。libcurl 官方文档明确说明这些行为和相应控制；不能将一种客户端对 `Authorization` 或 `Cookie` 的默认处理外推为所有库、所有自定义头都安全。见 [libcurl：重定向与凭据范围](https://curl.se/libcurl/c/CURLOPT_FOLLOWLOCATION.html)。

因此，抓取请求应从最小的出站头集合构造，避免复制用户的入站 [Cookie](../../glossary/security.md#security.sessions)、服务端令牌或内部认证头。需要合作方凭据时，在确认最终许可目标后按专用契约提供，并核对后续跳转的传递规则。凭据是否有效，与该目标是否应收到凭据，是两项检查。

## 代理和网络出口也属于策略执行路径

若请求经代理发出，应用连到的可能只是代理地址；最终主机解析与目的地连接可能发生在代理一侧。此时本地校验或记录“对端是可信代理”，不足以证明最终目标被限制。固定代理配置、检查绕过规则，并让代理承担最终目标策略；以 libcurl 为例，代理环境变量与 `NO_PROXY` 会影响实际路径。见 [libcurl：代理配置](https://curl.se/libcurl/c/CURLOPT_PROXY.html)。

抓取组件适合独立部署，以[最小权限](../../glossary/security.md#security.trust)运行，出口默认拒绝后按需开放目的地和 DNS；业务内部服务也继续验证身份和动作。网络配置必须在实际承载流量的位置生效。例如 Kubernetes `NetworkPolicy` 依赖支持它的网络实现；创建资源本身不代表流量已被隔离，出口规则与入口规则也不同。见 [Kubernetes：网络策略](https://kubernetes.io/docs/concepts/services-networking/network-policies/)。

云元数据服务需要单独审查。AWS IMDSv2 使用会话令牌机制，并可要求实例仅接受 IMDSv2；它增加保护层，但不能据此推导所有服务端代发能力都安全。仍需按需限制元数据可达性与实例[角色权限](../../glossary/security.md#security.access-control)，见 [AWS：IMDS 机制](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)。Google Cloud 同样提醒：能查询元数据的进程可以访问其中的值，不应具有该能力的进程需要隔离，见 [Google Cloud：元数据安全考虑](https://docs.cloud.google.com/compute/docs/metadata/overview#metadata_security_considerations)。

## 允许请求之后，还要限制响应成本和使用方式

目标被允许，不代表可无限下载或信任响应。抓取应有总期限、连接与读取预算、跳转上限、[并发](../../glossary/systems.md#systems.concurrency)限额、传输和解压后大小上限，并限制接受的媒体类型。响应头声明的大小或类型只是输入，处理方仍要在流式读取与解析阶段执行实际限额。这些是把资源消耗原则应用到抓取器的设计建议；一般资源限额依据见 [OWASP API4:2023](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/)。

不要把远端响应中的凭据、内部诊断信息或全部响应头原样返给调用者。若把抓取的内容进一步显示成 HTML，还会进入 [XSS 的输出边界](xss-contexts-sinks-and-browser-defenses.md)。这说明“目的地允许”“内容可处理”“内容可展示”需要分别判断。

代理连接、地址转换和转发头的职责继续见[NAT、代理与负载均衡](../networking/nat-proxies-and-l4-l7-load-balancing.md)；网络分流和客户端地址元数据不能替代目的地策略或业务身份。

## 纸面自检与关联

对一个虚构的图片预览功能，先写预期策略，再逐项回答：

| 教学情形 | 应检查的边界 |
| --- | --- |
| 主机在允许列表，但某个 AAAA 候选不被允许 | 全部候选与回退地址是否受约束 |
| 第一次解析允许，连接前解析发生变化 | 实际连接是否仍只使用已许可地址 |
| 允许的目标返回另一主机的重定向 | 下一跳是否重新授权，头和请求体是否会重发 |
| 出站代理按自己的 DNS 连接目标 | 最终策略由谁执行，是否存在直接出口 |
| 目标持续返回压缩数据 | 期限、解压后大小与处理资源是否有界 |

自检：为什么仅检查 URL 字符串或一次 DNS 结果不充分？为什么只允许 HTTPS 仍不能替代目的地授权？为什么禁用重定向之后仍需出口与凭据隔离？

[同源与 CSRF](origins-cors-and-csrf.md)解释浏览器的请求边界，[CORS](../../glossary/security.md#security.origin) 不为一般服务端客户端提供同样的限制。[对象级授权](object-level-authorization.md)决定用户是否能触发具体业务动作；[超时与重试预算](../reliability/timeouts-and-retry-budgets.md)约束请求成本，重试仍需延续当前目的地策略。

## 核查范围

2026-10-22 实际联网核查上述 [OWASP](../../glossary/security.md#security.threats)、WHATWG、IANA、GitLab、curl、Kubernetes、AWS 与 Google Cloud 一手资料。本文为 `source-checked`，核查覆盖信任边界、解析与连接职责、重定向、出口、元数据及资源限制；纸面策略是综合设计说明。没有执行 URL/DNS/代理绕过测试、目标请求、云端访问或网络策略实验，也未验证任何具体 HTTP 客户端配置已构成完整防护。
