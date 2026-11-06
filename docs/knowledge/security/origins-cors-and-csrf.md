---
id: "kb-security-origin-csrf"
title: "同源、CORS 与 CSRF：请求发得出为什么仍读不到响应"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分 origin 与 site、跨源读取与发送、CORS 预检和自动凭证，说明 CSRF 与 Cookie 属性的防护边界。"
created: "2026-10-20"
updated: "2026-10-22"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-networking-https-request", "kb-security-sessions-tokens"]
related: ["kb-security-oauth-oidc", "kb-security-object-authorization", "kb-api-conditional-requests", "kb-frontend-routing-cache", "kb-security-xss"]
tags: ["origin", "cors", "csrf", "browser"]
---

# 同源、CORS 与 CSRF：请求发得出为什么仍读不到响应

学习入口：控制台显示 [CORS](../../glossary/security.md#security.origin) 错误，为什么服务端的修改却已发生？前置：HTTP 请求、浏览器脚本和[Cookie 会话](authentication-sessions-and-tokens.md)。本文围绕普通 [HTTPS](../../glossary/networking.md#networking.tls) 页面讨论浏览器来源边界，参考 HTML、Fetch 与 [OWASP](../../glossary/security.md#security.threats)；例子是纸面请求，没有启动跨站服务。

## origin 与 site 用来回答不同问题

普通 HTTPS URL 的 origin 由协议、主机和端口共同确定，路径不参与；默认 HTTPS 端口 443 与显式写出的 443 不构成两个来源。来源模型见 [HTML Standard](https://html.spec.whatwg.org/multipage/browsers.html#origin)。

现代浏览器语境中的 schemeful site 主要依据协议与可注册域，和 origin 的粒度不同。下表以普通域名和同一协议为例，不讨论不透明来源、file URL 与特殊部署：

| 页面与目标 | 同源？ | 同站？ |
| --- | --- | --- |
| https://app.example.test/a → 同主机的 /b | 是 | 是 |
| https://app.example.test → https://api.example.test | 否，主机不同 | 是，协议及可注册域相同 |
| https://app.example.test → https://app.example.test:8443 | 否，端口不同 | 是，site 不以端口区分 |
| https://app.example.test → https://other.test | 否 | 否 |

因此，同站子域也可能跨源；SameSite [Cookie](../../glossary/security.md#security.sessions) 与同源策略不能互相替代。站点计算与同站关系见 [HTML Standard 的 same site 定义](https://html.spec.whatwg.org/multipage/browsers.html#same-site)。

## 同源策略不等于所有跨源请求都发不出去

同源策略限制来源之间的交互，尤其是脚本读取另一来源的数据。导航、部分嵌入和表单提交可以跨源发生，各自还有额外规则；不能从“脚本读不到响应”推导“请求没有发送”。[MDN 同源策略](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy#cross-origin_network_access)区分了跨源写入、嵌入与读取。

教学情形：用户已登录业务站点，恶意页面诱导浏览器向它提交表单。如果 Cookie 规则允许携带凭证，服务端又直接执行修改，浏览器最后拒绝让恶意页面读取响应，也不会撤销已经发生的修改。这正是理解 [CSRF](../../glossary/security.md#security.web-attacks) 时需要分开的两步：请求是否能形成有效操作，以及脚本是否能看见结果。

## CORS 为跨源读取建立显式许可

CORS 是浏览器执行的跨源响应共享协议。服务端通过允许的来源、方法、请求头等信息表达许可，浏览器据此决定是否把结果交给调用脚本。普通命令行客户端不会因 CORS 头缺失而自动受到同样的读取限制；服务端仍需[认证](../../glossary/security.md#security.identity)和对象授权。

有些请求满足 CORS safelist 条件，可以直接发送；不满足条件的跨源请求通常需要先做 OPTIONS 预检，确认目标允许实际请求。POST 不必然触发预检，方法、请求头、媒体类型及值的限制都参与判断。普通 JSON Content-Type 或自定义请求头常会使请求需要预检。具体规则见 [Fetch：CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)。

| 教学情形 | 实际请求与脚本结果 |
| --- | --- |
| 满足 safelist 的请求，响应缺少允许来源 | 实际请求可能已发送，脚本仍无法读取结果 |
| 必需的预检失败 | 浏览器不继续发送对应实际请求；服务端的 OPTIONS 处理也应遵守安全方法语义，不产生业务修改 |
| 预检成功，实际响应的共享检查失败 | 实际操作可能已发生，但脚本仍读不到响应 |

预检结果还可能被缓存，并非每次都看得到 OPTIONS。把请求改成 mode: no-cors 也不能获取任意 API 数据，它会受到请求约束，并得到脚本不能正常读取的 opaque 响应；这不是修复服务端 CORS 契约的方法。

需要预检的 API 应在预检响应中明确允许实际方法和请求头；让脚本读取 [ETag](../../glossary/api.md#api.conditionals) 等不在响应 safelist 中的字段，则要在实际响应使用 Access-Control-Expose-Headers。允许发送某个请求头与允许读取某个响应头是两份不同许可，不能只设置 Allow-Origin 就认定两者都已成立。

## 允许凭证不等于允许任意来源

跨源 fetch 的 credentials 模式与 Cookie 是否符合发送规则都需要考虑；设置 include 不会越过 SameSite 或浏览器其他 Cookie 限制。服务端若允许凭证模式下的响应共享，应返回明确允许的 origin，并按协议使用 Access-Control-Allow-Credentials: true，不能用 Access-Control-Allow-Origin: * 代替。凭证与通配符规则见 [Fetch：credentials](https://fetch.spec.whatwg.org/#cors-protocol-and-credentials)。

教学响应片段仅说明许可方向，不是完整服务器配置：

```http
Access-Control-Allow-Origin: https://app.example.test
Access-Control-Allow-Credentials: true
Vary: Origin
```

这里的 origin 必须先经过服务端的可信允许列表判断；收到什么 Origin 就无条件反射什么，会把许可给到不应信任的页面。响应随 Origin 改变时，还要让缓存正确区分这些变化，详见[条件请求与缓存验证](../api/conditional-requests-and-cache-validation.md)。

即使来源被允许，用户也可能没有当前对象权限。反过来，Cookie 有效也不说明发起操作的页面可信。CORS、身份认证、对象授权和 CSRF 防护分别回答不同问题。

## CSRF 防护关注浏览器借用了谁的凭证

CSRF 利用用户浏览器已有的认证上下文，让业务站点收到非用户所期望的操作。攻击者不一定需要读出会话 Cookie，浏览器自动发送它就可能足够。把 Cookie 内的值从 Session ID 换成 [JWT](../../glossary/security.md#security.tokens)，不会改变这种自动携带机制。

对于使用 Cookie 认证的状态修改，优先采用框架成熟的 CSRF 防护，并按部署验证。常见设计包括与会话绑定的不可预测 CSRF Token、严格的来源校验，以及按策略使用 Fetch Metadata；无状态双提交方案也需正确绑定和保护，不能简单认为“两个位置字符串一样”就充分。依据见 [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#token-based-mitigation)。

校验 Origin/Referer 时应依据可信的目标来源，考虑[反向代理](../../glossary/networking.md#networking.proxy)与缺失值的明确策略，避免字符串包含判断。SameSite 可以减少一部分跨站自动凭证，但同站兄弟子域未必可信，不能把 same-site 当作 same-origin。Fetch Metadata 也是按来源上下文制定策略的补充，不是用户身份凭证。

| 设计或属性 | 能帮助什么 | 剩余边界 |
| --- | --- | --- |
| GET 不承载业务修改 | 减少导航、预取等触发修改的风险 | 写请求仍需有效防护 |
| SameSite | 限制部分跨站 Cookie 发送 | 同站子域、导航方式及部署[兼容性](../../glossary/api.md#api.versioning)仍需判断 |
| HttpOnly | 限制脚本通过 Cookie 接口读取凭证 | 恶意同源脚本仍可能代表用户发送请求 |
| 自定义认证请求头 | 不像会话 Cookie 那样由浏览器自动附加任意请求 | 凭证如何保存、脚本是否被攻陷仍需考虑 |

XSS 是恶意内容在受信任页面中执行脚本，可绕过许多依赖“同源脚本可信”的假设；CSRF 关注借用认证上下文发起操作；SSRF 则关注服务端被诱导发起请求。三者的执行位置和控制边界不同，本文只展开 CSRF，不覆盖完整 XSS、SSRF 防护。

同源脚本注入的输出与执行边界见[XSS 与浏览器输出边界](xss-contexts-sinks-and-browser-defenses.md)；跨源策略和 CSRF 防护不能代替这些控制。

## 自检与验证范围

用表格分别写明：页面 origin、目标 origin、是否同站、凭证能否自动携带、是否需要预检、服务端怎样拒绝非法操作、响应能否被脚本读取。先判断写入是否发生，再判断页面能否读到结果。

试着解释：同站的两个子域为什么仍需要 CORS？预检失败与实际响应共享失败为什么不能等同？HttpOnly 为什么不能消除 XSS 的操作能力？可信页面的 CORS 许可为什么不能替代对象授权？

2026-10-20 核查 HTML、Fetch、MDN 与 OWASP 来源，状态为 source-checked。本文未执行双站点 CORS/CSRF、Cookie 策略、代理缓存、XSS 或 SSRF 实验；未将纸面请求当作真实浏览器结果。认证回调的交易关联见 [OAuth 与 OIDC](oauth-oidc-and-pkce.md)。
