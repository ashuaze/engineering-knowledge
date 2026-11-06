---
id: "kb-security-mtls-service-identity"
title: "mTLS 与服务身份：双向验证为何仍需授权边界"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分证书链、预期身份与私钥证明，解释工作负载授权、代理逐跳和证书轮换的信任边界。"
created: "2026-10-22"
updated: "2026-10-23"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-networking-connection-states", "kb-security-sessions-tokens"]
related: ["kb-security-object-authorization", "kb-security-secret-lifecycle", "kb-security-oauth-oidc", "kb-networking-nat-proxy-lb", "kb-api-styles-gateway", "kb-security-authorization-models", "kb-security-service-delegation"]
tags: ["mtls", "service-identity", "trust-boundaries", "certificate-rotation"]
---

# mTLS 与服务身份：双向验证为何仍需授权边界

学习入口：服务 A 和服务 B 已经完成[双向 TLS](../../glossary/security.md#security.mtls)，为什么 A 仍不该读取任意租户的数据；经过网关后，B 验证的又是谁？前置：[TLS 连接状态](../networking/tcp-tls-and-connection-states.md)、[认证与令牌](authentication-sessions-and-tokens.md)。mTLS 让连接双方按约定验证证书身份和对应私钥的持有证明；应用还要判断这个主体是否是预期调用方，以及当前动作是否被允许。

本文以 [TLS](../../glossary/networking.md#networking.tls) 1.3 中 CA 签发的 X.509 证书[认证](../../glossary/security.md#security.identity)路径为基础，区分普通服务证书、SPIFFE [工作负载身份](../../glossary/security.md#security.workload-identity)与 [OAuth](../../glossary/security.md#security.oauth) 证书绑定令牌。逐跳图和时间线都是纸面教学推演；没有签发证书、运行代理、抓包或进行撤销实验。

## 双向验证需要哪些不同证据

证书把身份信息和公钥绑定在签发者的签名下。证书通常可以公开传输，拿到证书文件不等于掌握对应私钥。以下检查表和角色表限定采用 CA 信任链的普通 PKIX 证书身份配置；后文另说明 OAuth 中不同的证书信任方式。对每个方向，可以分别问四个问题：

| 问题 | 验证内容 | 单独成立仍缺少什么 |
| --- | --- | --- |
| 谁为这把公钥背书 | 按已配置的信任锚构建并验证叶证书与中间链，处理签名、期限、约束和证书状态 | 不等于这是目标服务 |
| 证书适合此次用途吗 | 按证书配置规范处理 Key Usage、扩展密钥用途 EKU、CA 与路径长度等约束；存在的用途限制必须满足 | 不等于名称匹配或有业务权限 |
| 对端是预期主体吗 | 用事先确定的身份规则匹配证书中的相应身份 | 不证明当前连接者持有私钥 |
| 当前对端掌握密钥吗 | 验证握手中的 CertificateVerify 签名，并完成 Finished 等协议检查 | 不等于当前动作被允许 |

信任锚是验证方接受的信任输入；对端附送一张自签名根证书，不会让它自动可信。以自签名根证书提供信任锚时，该根不作为普通证书纳入这条待验证路径；根的信任、期限和撤销配置需按本地策略与所用配置规范另行核对。[RFC 5280 §6](https://www.rfc-editor.org/rfc/rfc5280.html#section-6)规定路径验证及其输入；[§4.2.1.9–§4.2.1.12](https://www.rfc-editor.org/rfc/rfc5280.html#section-4.2.1.9)说明基本约束、名称约束和 EKU。EKU 若存在，就只能用于允许的用途；应用配置规范还可要求它必须存在，例如要求相应的 serverAuth 或 clientAuth。不能用“证书没过期”代替这些检查。

在证书认证的 TLS 1.3 握手中，CertificateVerify 将对应私钥产生的签名绑定到此次握手上下文，从而提供私钥持有证明；[RFC 8446 §4.4.3–§4.4.4](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.4.3)还区分了签名与 Finished 的密钥确认、握手完整性职责。验证库应执行协议与证书规则，应用负责提供正确的信任材料、目标身份和接受策略，不能把“库没有报错”当作这些输入均已正确配置。

| 连接角色 | 必须明确的责任 |
| --- | --- |
| TLS 客户端，例如调用 B 的 A | 验证 B 的服务端证书路径、适用用途、预期服务身份及握手证明；需要客户端认证时，提供自己的证书和私钥证明 |
| TLS 服务端，例如接收 A 的 B | 配置何时请求及要求客户端证书，验证客户端证书路径、适用用途和握手证明，再按所用身份体系识别 A；把该主体交给授权策略 |

客户端证书不是每条 TLS 连接的默认步骤。本文的 TLS 1.3 证书型主握手中，服务端在 EncryptedExtensions 后可选发送 CertificateRequest，随后发送自己的 Certificate、CertificateVerify 和 Finished；客户端验证服务端消息后，再完成自己的认证消息。客户端只有收到请求才发送客户端 Certificate，没有合适证书时发送空列表。协议允许服务端选择终止，或继续一条未认证客户端的连接，因此业务要求 mTLS 的入口必须拒绝未认证主体。以 PSK 认证的主握手不能发送该请求；握手后客户端认证另有协商条件，不能假设任意 HTTP 请求都能临时补做。见 [RFC 8446 §4.3.2、§4.4.2、§4.6.2](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.3.2)。

## “证书可信”与“身份匹配”怎样分开

普通 HTTPS 客户端应先从请求目标与协议规则得到可接受的参考身份，再和服务端呈现的身份匹配，不能看了证书后再把期望改成它的名字。[RFC 9525 §1.2、§1.4、§6](https://datatracker.ietf.org/doc/html/rfc9525#section-6)讨论的是其作用域内的服务端身份：[DNS](../../glossary/networking.md#networking.dns) 名匹配相应的 dNSName SAN，[IP](../../glossary/networking.md#networking.transport) 参考身份匹配 iPAddress SAN；不能因 DNS 解析得到某个 IP，就把原来的域名认证任意改为该 IP。该规范不使用 Subject Common Name 中类似域名的字符串，因此不能默认启用 CN 回退。

RFC 9525 不定义客户端或端用户的身份匹配，也不负责通用 URI 路径的业务语义。服务 B 接受客户端证书时，要按实际客户端身份配置规范匹配；不能把服务端 DNS 名检查机械套到所有客户端身份，也不能仅凭“来自同一家 CA”就识别成 A。

工作负载身份标识运行中的服务或[进程](../../glossary/systems.md#systems.execution-units)主体。例如 [SPIFFE Identity 规范 §2–§3](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)用 `spiffe://prod.example/orders/reader` 这样的 URI 表示身份：`prod.example` 是信任域名称，路径的意义由管理方约定。信任域名称不是一次 DNS 查询或公网域名所有权证明；路径里出现 `reader` 也不会自行产生读取权限。

[X.509-SVID 规范 §2、§4–§5](https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md)定义这种身份怎样进入 X.509 证书：恰有一个 URI SAN 承载 SPIFFE ID，再结合证书路径和该配置规范的叶证书规则验证。验证方还须按对端的信任域选择已信任的 bundle，并按应用策略接受预期 SPIFFE ID，不能把所有信任域的根简单合在一起后接受任意 URI。该 bundle 选择规则见 [Workload API §4.6](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Workload_API.md#46-federated-bundles)。这与 RFC 9525 的 DNS/IP 参考身份匹配是两套有不同作用域的规则。

这里的 SPIFFE 三份规范均指官方仓库 `main` 在 2026-10-22 读取的 Stable 文档快照；本文不推定某个语言库或服务网格已经实现全部规则。

## 从工作负载身份到租户、动作和对象

握手后可得到一个经过验证的连接主体。应用策略再把它映射到允许的租户集合、动作和资源范围；请求里的 tenant 或 resource 只是待核对输入。[对象级授权](object-level-authorization.md)仍应在实际读写路径执行。

纸面反例：B 验证出 `spiffe://prod.example/orders/reader`，策略只允许它读取租户 T1 的订单。它发送 `tenant=T2, action=delete, resource=order-7` 时，链可信和私钥证明都不能补足租户、动作和对象权限。身份到权限的映射也应有自己的更新与失效策略，不能把证书签发时的角色状态永久当作当前权限。

若 A 代表用户 U 调 B，还要另行核实委托：凭证是否用于 B、声明和受众是否正确、U 的当前权限是否覆盖该对象，以及 A 是否允许代表 U 执行该动作。A 的服务证书不会自动认证 U；也不能把 U 的[访问令牌](../../glossary/security.md#security.token-lifecycle)当作 A 的证书身份。相关协议关系见 [OAuth 与 OIDC](oauth-oidc-and-pkce.md)。

[RFC 8705 §1–§3](https://www.rfc-editor.org/rfc/rfc8705.html#section-3)定义了可分别部署的两种机制：OAuth 客户端用 mTLS 向授权服务器认证，以及访问令牌与客户端证书绑定。后者要求资源端把令牌绑定信息与此连接使用的证书比较；其 [JWT](../../glossary/security.md#security.tokens) 表示可使用 `cnf` 中的 `x5t#S256`。仅开启普通 mTLS，不会使现有 Bearer 令牌自动获得这种绑定，也不能替代访问令牌本身及当前权限的验证。

这也不要求所有客户端证书都由 CA 链认证：[RFC 8705 §2.2、§6.2](https://www.rfc-editor.org/rfc/rfc8705.html#section-2.2)允许专门的预注册自签名客户端证书方法，资源端也可仅用证书及私钥证明核对令牌绑定。这些方式的接受依据分别是预注册材料或已验证令牌的绑定，不能据此让普通服务身份跳过前面的 CA 路径检查。绑定的是具体证书，C1 的令牌换到 C2 的连接会不匹配，即使两张证书使用同一公钥；换证时应按协议取得匹配的新令牌，见 [§6.3](https://www.rfc-editor.org/rfc/rfc8705.html#section-6.3)。

## 代理终止 TLS 后，B 实际验证谁

下面假设 P 终止入站 TLS，并用自己的证书重新连接 B；这是两段独立的 mTLS 连接：

```text
A 的证书身份 ── mTLS 连接 1 ──> P
                               P 的证书身份 ── mTLS 连接 2 ──> B
```

P 在连接 1 验证 A；B 在连接 2 验证的是 P。第二段的握手不会自动向 B 证明 A 持有私钥。若 P 只是透传 TLS 字节流，边界又不同，需要先确认真正的 TLS 终止点，见 [NAT、代理与负载均衡](../networking/nat-proxies-and-l4-l7-load-balancing.md)。

若 B 需要原始身份，P 可以通过约定字段传递已验证的证书或身份，但 B 此时依赖的是 P 的可信断言。P 必须清理外部请求中伪造的同名字段；B 只能从可信代理路径接受这些字段，代理到 B 的传递还必须防窃听和篡改，并避免绕过代理直接注入。否则攻击者即使没通过 A 的认证，也可能写一个身份请求头骗过 B。[RFC 9440 §2.4、§4](https://www.rfc-editor.org/rfc/rfc9440.html#section-2.4)对 Client-Cert 等证书转发字段给出这些处理边界；其字段机制不是端到端重做 A 的 TLS 握手。

教学反例：外部客户端自行发送 `Client-Cert`，P 原样转发，B 信任该值。即使 P 到 B 的 mTLS 配置正确，B 也只证明“这个请求由 P 发送”，未证明该字段由 P 验证后产生。[API 风格与网关边界](../api/api-styles-contracts-and-gateway-boundaries.md)继续解释入口契约和业务执行责任。

## 轮换何时改变旧能力

轮换至少涉及三种不同对象：信任根或中间签发链、叶证书、对应私钥。重新签发证书可以继续使用同一公钥，因此“证书变了”不一定表示私钥已更换；移除本地文件也不删除进程内存、备份或已泄露副本。恢复旧[镜像](../../glossary/devops.md#devops.containers)、快照或秘密备份后，还要防止旧材料重新进入分发与接受路径，继续见[密钥与凭证生命周期](secrets-credentials-rotation-and-revocation.md)。

以下为正常迁移的纸面时间线，不是泄露后的完整处置方案：

| 时间 | 变更 | 尚不能据此断言的事 |
| --- | --- | --- |
| t0 | B 接受旧根 R1；A 使用叶证书 C1、私钥 K1，已有连接 L1 | 未来策略不会变化 |
| t1 | 验证方开始分发 R2，与 R1 暂时重叠 | 每个实例、代理及验证缓存均已更新 |
| t2 | A 换用 R2 链下的 C2 与新私钥 K2，新的完整握手通过 | C1/K1 已失效，或 L1 已重新认证 |
| t3 | 验证方按迁移策略移除 R1、停止接受 C1，并处理旧连接与恢复状态 | 其他副本、恢复出来的实例和在途业务均已同步完成 |

轮换顺序要在连接可用性与旧信任暴露窗口间取舍；若 R1 或 K1 已泄露，不能把等待平稳迁移当成唯一处置。撤销信息需要真正抵达并被验证方执行。[RFC 5280 §3.3、§6.1.3](https://www.rfc-editor.org/rfc/rfc5280.html#section-3.3)说明到期前撤销及证书状态检查；具体系统是否检查、数据新鲜度、缓存和检查失败如何处理，都要按部署确认，不能从“使用 mTLS”推出即时撤销。

已建立连接不会因为磁盘上的证书换了就自动完成新的证书认证；应明确何时排空或关闭旧连接、何时要求新的完整握手，以及业务是否需要逐请求复查身份状态。TLS 1.3 没有旧式重协商，KeyUpdate 更新的是连接流量密钥，不能当作换证或重新认证。[TLS 会话恢复](../networking/tcp-tls-and-connection-states.md)还会涉及先前建立的密钥材料；[RFC 8446 §4.6.1–§4.6.3](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.6.1)建议限制相关密钥材料的总寿命，并考虑证书期限、可能的撤销及距上次私钥证明的时间。本文不扩展到 0-RTT 的使用方案。

SPIFFE Workload API 的 X.509-SVID 接口可持续推送身份材料和 bundle 更新；客户端仍需及时接收并应用，不能把“控制面已推送”当成所有连接均已更换身份。[Workload API §4.1–§4.4、§5.2](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Workload_API.md#4-client-and-server-behavior)也把本地调用方识别、完整更新和撤回材料后的客户端行为列为责任。谁能领取哪个 ID，要绑定到受控的工作负载识别证据，不能由请求者自报一个身份字符串决定；X.509-SVID 承载身份、公钥与签发者签名，私钥作为单独材料保护。自动发证减少手工分发负担，同时增加对身份签发、调用方识别和更新通道的依赖；被控制的工作负载若仍有资格领取新证书，短有效期本身不能停止冒用。

从可信服务身份继续推导对象操作资格，见[权限模型与策略传播](authorization-models-policy-distribution-and-revocation.md)。规则、关系事实、允许结果与最终执行都有独立版本和时间边界，连接身份校验不负责将它们同步更新。

服务替用户执行下一跳动作，继续见[跨服务委托](service-delegation-token-exchange-and-audience.md)。mTLS 客户端认证、证书绑定令牌与用户委托是不同机制；连接可信还需核对当前主体、执行者、目标受众和具体对象动作。

## 五道自检

1. B 收到同一受信任 CA 给另一个服务签发的证书时，路径检查、身份匹配和授权分别应在哪一步拒绝什么？
2. A 访问域名解析出的 IP、B 验证客户端 URI SAN、应用识别端用户，为什么不能复用同一套名称匹配规则？
3. P 终止 A 的 TLS 并重新连接 B 时，B 分别凭什么信任 P 的连接身份和 P 转发的 A 身份？
4. 换发叶证书但保留私钥，与更换私钥、移除旧根、撤销叶证书相比，各自还留下哪些旧能力和传播窗口？
5. 证书 C1 绑定的访问令牌被带到使用 C2 的连接时，资源端应检查哪些额外条件；为什么普通 mTLS 不会自动做这件事？

## 来源与核查

核查日期：2026-10-22。本文为来源核查，不是配置验证或互操作测试。表格中的业务策略、逐跳反例与轮换顺序是基于机制的教学综合；没有执行 CA 签发、证书路径验证、SPIFFE 部署、代理头清理、TLS 恢复、连接排空或多节点撤销实验。

| 一手资料与版本 | 本文实际核查范围 |
| --- | --- |
| [RFC 8446，TLS 1.3，2018-08](https://www.rfc-editor.org/rfc/rfc8446.html) | §4.3.2、§4.4.2–§4.4.4 的请求、证书与私钥证明；§4.6.1–§4.6.3 的恢复材料、握手后认证与 KeyUpdate；版本限定为 TLS 1.3 |
| [RFC 5280，2008-05](https://www.rfc-editor.org/rfc/rfc5280.html) | §3.3 撤销；§4.2.1.9–§4.2.1.12 约束与 EKU；§6.1–§6.2 路径验证、信任输入和应用附加要求；未核查具体库的撤销默认值 |
| [RFC 9525，2023-11](https://datatracker.ietf.org/doc/html/rfc9525) | §1.2–§1.4 作用域、SAN 与 CN；§6.1–§6.4 参考身份与 DNS/IP 匹配；不推广为客户端或 SPIFFE 完整 URI 的匹配规范 |
| [RFC 8705，2020-02](https://www.rfc-editor.org/rfc/rfc8705.html) | §1–§3 及 §6.2–§6.3、§6.5：OAuth 客户端认证、证书绑定访问令牌及 TLS 终止边界；未验证授权服务器实现 |
| [RFC 9440，2023-07，Informational](https://www.rfc-editor.org/rfc/rfc9440.html) | §1、§2.4、§4：TLS 终止代理、转发字段清理和可信路径；未提供可复制部署配置 |
| [SPIFFE Identity](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE-ID.md)、[X.509-SVID](https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md)、[Workload API](https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Workload_API.md) | 官方 `main`，2026-10-22 读取，三者标为 Stable；分别核查 Identity §2–§3/§4.1，X.509-SVID §2/§4–§5，Workload API §4/§5 的身份、信任域、证书约束与更新责任；不声称已验证任一产品版本 |
