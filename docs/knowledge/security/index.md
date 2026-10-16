<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 身份、安全与权限

建议优先级：P0。目标：以信任边界、身份和最小权限设计系统。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

已登录用户为何仍不能直接访问任意租户数据？

## 已有正文

- [对象级授权：已登录为何仍不能访问这份数据](object-level-authorization.md)：将主体、动作、对象和租户关系写成可验证的访问规则，覆盖详情、列表和写入。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Authentication / Authorization | 证明身份与判断访问权。 |
| Session / Cookie | 会话状态和浏览器保存、发送的数据。 |
| OAuth 2.0 / OpenID Connect | 委托授权框架与其上的身份层。 |
| JWT / JWS / JWK | 声明容器、签名格式和密钥表示。 |
| RBAC / ABAC | 按角色或属性判断权限。 |
| Access Token / Refresh Token | 访问凭据和更新访问凭据的机制。 |
| CORS / Same-Origin Policy | 浏览器同源边界与跨源响应访问机制。 |
| XSS / CSRF / SSRF | 脚本注入、跨站请求伪造和服务端请求伪造。 |
| SQL Injection / Parameterized Query | 查询结构注入与参数绑定防护。 |
| Hash / Salt / KDF | 哈希、随机盐和适合口令的派生机制。 |
| mTLS / Certificate | 连接两端的证书身份校验。 |
| Secrets Management | 敏感凭据的保存、分发与轮换。 |
| Least Privilege / Zero Trust | 最小授权和持续验证访问条件。 |
| Threat Modeling / OWASP | 识别攻击面并参考应用安全研究与规范。 |
| Tenant Isolation / Object-level Authorization | 租户边界与逐对象访问检查。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
