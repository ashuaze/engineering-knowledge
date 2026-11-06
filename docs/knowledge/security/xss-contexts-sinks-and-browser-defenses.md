---
id: "kb-security-xss"
title: "XSS：不可信数据何时变成浏览器代码"
kind: "concept"
domain: "security"
status: "evolving"
summary: "沿数据源、危险汇与解析上下文解释 XSS，区分输出编码、HTML 净化、安全 DOM API、Trusted Types 和 CSP 的防护职责。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-security-origin-csrf", "kb-security-sessions-tokens"]
related: ["kb-security-object-authorization", "kb-frontend-rendering-hydration", "kb-security-ssrf"]
tags: ["xss", "output-encoding", "sanitization", "trusted-types", "csp"]
---

# XSS：不可信数据何时变成浏览器代码

学习入口：评论已经通过[输入校验](../../glossary/api.md#api.validation)，页面也使用现代框架，为什么展示评论时仍可能出现 [XSS](../../glossary/security.md#security.web-attacks)？关键问题是：数据最后交给哪个 API、进入哪种解析上下文，应用是否让它获得了代码的含义。

前置：[同源、CORS 与 CSRF](origins-cors-and-csrf.md)、[认证与 Cookie 会话](authentication-sessions-and-tokens.md)。本文讨论普通 Web 页面中的内容注入防护；例子是无害的纸面数据流，没有执行注入代码或跨浏览器实验。

## 从来源追到最后一次解释

XSS 是让目标页面在自己的执行上下文中运行非预期代码。脚本此时具有该页面的能力，可能读取页面数据、修改界面或发起带用户凭证的请求；浏览器看到的执行来源仍是目标页面。定义与能力范围见 [MDN：XSS](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)。

审查时，把一条路径写完整：**可控数据源 → 保存或转换 → 输出位置 → 解释它的 API**。请求参数、数据库内容、第三方接口和消息都需要建立来源边界；“来自数据库”只说明保存位置，不证明内容可信。

| 常见名称 | 主要观察什么 | 无害教学情形 |
| --- | --- | --- |
| 存储型 XSS | 数据保存后被后续页面使用 | 用户简介进入数据库，管理员稍后查看 |
| 反射型 XSS | 请求数据进入当前响应 | 搜索词被服务端插回搜索结果页 |
| [DOM](../../glossary/frontend.md#frontend.render-tree) 型 XSS | 浏览器脚本把可控值送进危险 DOM 操作 | 脚本读取 URL 片段，再赋给 `innerHTML` |

前两项描述数据如何到达页面，DOM 型强调客户端注入路径，不能把三项当作完全互斥的分类。已保存的数据也可能在浏览器中经危险 DOM 操作解释。分类交叉关系见 [OWASP：XSS 类型](https://community.owasp.org/Types_of_Cross-Site_Scripting)。

危险汇（sink）是会把值解释成 HTML、脚本等主动内容的入口。`innerHTML` 接受的是 HTML 结构，不是普通文字；输入中没有显式的 `script` 元素，也不能据此确认安全，其他主动内容同样可能造成执行。见 [MDN：`innerHTML` 安全考虑](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML#security_considerations)。

## 编码要对应输出上下文

输入校验负责业务允许什么值；输出编码负责让值在指定语法位置保持数据含义。相同字符串进入 HTML、属性、URL 或 JavaScript 时，解析规则不同，不能在入口统一“转义一次”后到处复用。

| 最终位置 | 防护重点 |
| --- | --- |
| 普通元素中的文字 | 使用框架文本绑定或 HTML 文本编码，避免被识别成标签 |
| 固定名称的普通属性，如 `title` | 属性值始终加引号，使用属性上下文编码；不让输入决定属性名 |
| `href` 等 URL 属性 | 先验证允许的方案和目标；动态查询值按 URL 组件编码，再满足外层 HTML 属性要求 |
| JavaScript 字符串或事件处理器 | 优先移出动态代码拼接；确需模板化时同时处理 JavaScript 与外层 HTML 上下文，不能靠 HTML 编码代替 |

这张表依据 [OWASP：上下文输出编码](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#output-encoding)归纳。URL 编码只处理表示方式，不会把危险方案变成允许的方案；事件属性、动态标签名和其他代码位置，应优先消除该动态入口，而不是再叠一层通用转义。

## 需要文字时，选择不会解析 HTML 的 API

下面是针对固定普通展示元素的说明性 JavaScript，未执行；输入只有无害标记：

```js
const displayName = "<b>小林</b>";
const target = document.querySelector("#display-name");
target.textContent = displayName;
```

这里的目标是显示完整文字，包括尖括号。`textContent` 不把字符串当作 HTML 解析，因而比拼接后赋给 `innerHTML` 更符合任务。该结论针对普通展示节点；不能进一步推导为“把任意值放到任意元素的文本里都安全”，例如构造脚本元素仍属于主动代码路径。API 差异见 [MDN：`textContent` 与 `innerHTML`](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent#differences_from_innerhtml)。

需要结构时，可以用固定的标签创建元素、用文本节点填充内容，再组合节点。`setAttribute` 是否安全仍取决于固定的属性名及其语义：普通文字属性、事件属性和 URL 属性不能混为一类。避免将字符串交给隐式求值、HTML 渲染等操作；安全 DOM 构造原则见 [OWASP：DOM 型 XSS 防护](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html#rule-6---populate-the-dom-using-safe-javascript-functions-or-properties)。

## 富文本和框架的显式出口需要单独处理

当产品确实允许一部分 HTML，全部显示成文字不满足需求。这时需要 HTML 净化：按明确策略保留允许的元素、属性与 URL，去除不允许的结构。采用持续维护的解析型净化器，并核对它的运行环境与配置。净化后的内容再被拼接、改写或交给会改变标记的组件，可能破坏原先的保证。相关使用边界见 [DOMPurify 官方说明](https://github.com/cure53/DOMPurify#is-there-any-foot-gun-potential)。

框架的普通文本绑定通常提供转义，但这不覆盖绕过绑定后直接操作 DOM 的路径。以 React 为例，`dangerouslySetInnerHTML` 明确让应用提供原始 HTML，必须由调用方建立内容可信条件；属性名里有“dangerously”也不代表框架完成了净化。见 [React：直接设置 HTML](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)。

可把组件契约分成“纯文本”和“受约束富文本”两种输入。转换发生在哪里、允许哪些结构、净化后还能否修改，都应可追踪；不要只在变量名上加 `safe` 就把普通字符串当成可信 HTML。

## Trusted Types 与 CSP 分别约束什么

[Trusted Types](../../glossary/security.md#security.trusted-types) 可以让受管控的危险汇要求 `TrustedHTML` 等类型，由集中策略产生相应值。`require-trusted-types-for 'script'` 控制相应汇的类型要求，`trusted-types` 控制策略创建。策略仍需正确净化或验证；原样返回输入的策略只是给不可信内容套上类型。它也不负责防御已主动恶意的第一方代码。机制与限制见 [W3C Trusted Types 草案](https://www.w3.org/TR/trusted-types/)。

CSP 为页面资源加载与脚本执行施加额外约束，可用适当的 `script-src`、`nonce` 或哈希设计减少部分注入的执行机会。`nonce` 需按响应正确生成并只授予预期脚本；放宽内联执行、动态求值或过宽信任来源，会削弱策略。`Content-Security-Policy-Report-Only` 只监测，不阻止执行。CSP 是纵深防护，不能替代正确的内容处理；见 [W3C CSP Level 3](https://www.w3.org/TR/CSP3/)。

两者都有部署与兼容成本：既有组件可能依赖字符串 HTML 或动态脚本，需要先盘点调用路径并检查报告，再在目标浏览器实施阻断验证。类型约束、净化与执行策略的保护范围不能仅靠“响应里有安全头”判断。

## HttpOnly 保护凭证读取，不阻止页面动作

`HttpOnly` 限制脚本通过 `document.cookie` 等接口读取相应 [Cookie](../../glossary/security.md#security.sessions)；浏览器仍会按 Cookie 规则把它附加到脚本发起的请求。因而恶意同源脚本即使读不到会话值，也可能借当前会话执行操作。属性的这一边界见 [MDN：`HttpOnly`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie#httponly)。

这也解释了为何 [CSRF 防护](origins-cors-and-csrf.md)依赖的“页面脚本可信”假设会被 XSS 破坏。服务端仍须做[对象与动作授权](object-level-authorization.md)，但合法用户权限内的恶意动作，不能指望对象[授权](../../glossary/security.md#security.identity)自动识别为用户不想做。

## 用一条纸面路径检查遗漏

以下是教学模型，不是漏洞复现或测试结果：用户简介原本通过文本绑定显示；后来产品增加加粗功能，组件改为接收 HTML；另一个插件又在净化之后追加标记。

| 变化 | 需要重新回答的问题 |
| --- | --- |
| 文本绑定改为 HTML 输入 | 哪一步开始解析结构，输入契约是否改变？ |
| 加入净化器 | 允许的内容、运行环境及版本由谁维护？ |
| 净化后交给插件 | 插件能否引入新结构或改变解析上下文？ |
| 加入 Trusted Types 或 CSP | 是否真正阻断，哪些路径仍在其范围外？ |

自检：为什么“数据库里的值”仍需追踪来源？URL 组件编码为什么不能替代方案校验？为什么已设置 `HttpOnly` 仍必须修复 XSS？解释时分别指出数据来源、危险汇、解析上下文与执行后的权限。

## 关联与核查范围

[渲染与 Hydration](../frontend/rendering-and-hydration.md)解释页面结构如何由服务端与客户端共同建立；两段渲染路径都需要追踪输出上下文。[SSRF](ssrf-url-resolution-and-egress-boundaries.md)讨论服务端被借用的网络能力，与浏览器内执行的 XSS 边界不同。

2026-10-22 实际联网核查上述 [OWASP](../../glossary/security.md#security.threats)、MDN、React、DOMPurify 与 W3C 一手资料。Trusted Types 采用 2026-10-07 工作草案，CSP Level 3 采用 2026-09-16 工作草案，两者均仍在演进。本文状态为 `source-checked`，核查覆盖分类、上下文编码、安全 API 与浏览器防护机制；未执行净化器、框架、CSP、Trusted Types 或浏览器兼容实验，也不证明具体应用已满足这些边界。
