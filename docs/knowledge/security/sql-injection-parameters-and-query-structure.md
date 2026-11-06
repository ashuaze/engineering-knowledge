---
id: "kb-security-sql-injection"
title: "SQL 注入与参数化查询：值怎样与查询结构分开"
kind: "concept"
domain: "security"
status: "evolving"
summary: "区分绑定值、受控查询结构与对象权限，用 Psycopg 教学例解释动态排序、模式与列表语义、二次注入，以及预处理和计划复用的范围。"
created: "2026-10-22"
updated: "2026-10-22"
last_verified: "2026-10-22"
verification: "source-checked"
prerequisites: ["kb-security-sessions-tokens", "kb-security-object-authorization"]
related: ["kb-runtime-types-validation", "kb-database-indexes-plans", "kb-database-isolation-mvcc", "kb-api-admission-controls", "kb-security-secret-lifecycle"]
tags: ["sql-injection", "parameterization", "query-structure", "authorization", "prepared-statements"]
---

# SQL 注入与参数化查询：值怎样与查询结构分开

学习入口：搜索词已经是字符串，查询也只执行一条 `SELECT`，为什么仍可能改变查询含义？关键不在输入是否“像攻击”，而在程序是否把数据拼进了 SQL 语法。绑定值、选择查询结构和判定资源权限，需要分别完成。

前置：[认证与会话](authentication-sessions-and-tokens.md)、[对象级授权](object-level-authorization.md)及基本 `SELECT`。本文用 PostgreSQL 18 与 Psycopg 3 的经典 `execute()` 接口说明机制；Python 和 SQL 片段均未执行，没有连接数据库或发起攻击请求。

## 数据何时越过了 SQL 语法边界

[SQL 注入](../../glossary/security.md#security.sql-injection)发生在不可信数据被作为查询结构解释时。直接把姓名、过滤表达式或排序片段拼入语句，会让解析器看到一份已经混合的文本；输入中的标点可能成为语法，而非字段值。参数化查询让语句结构与值分别交给相应接口处理，防止值改写原本结构。核心原则见 [OWASP：SQL 注入防护](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)。

以 Psycopg 默认游标为例，`execute(query, parameters)` 使用 `%s` 等值占位符，值放在第二参数序列或映射中。这里的 `%s` 不是让 Python 先执行字符串格式化；不要自己用 `%`、`+` 或 f-string 把值填回 SQL，也不要给占位符加 SQL 引号。单个位置参数仍需序列，例如 `(value,)`。接口与分开发送机制见 [Psycopg：传递参数](https://www.psycopg.org/psycopg3/docs/basic/params.html)。

业务[输入校验](../../glossary/api.md#api.validation)仍有价值，例如拒绝无效 ID、过长文本和不允许的选项；但它与绑定的责任不同。合法姓名可以带单引号，不能靠删除标点来代替 SQL 边界。静态类型也不证明外部数据或身份可信，见[类型与运行时校验](../runtime/type-systems-and-runtime-validation.md)。

## 值、标识符与语法选项要分开处理

| 动态部分 | 适合的处理方式 | 不能据此推导 |
| --- | --- | --- |
| 姓名、对象 ID、时间、适用位置的行数上限 | 绑定值参数 | 值合法或用户有权访问该对象 |
| 表名、列名、限定名称 | 优先固定；确需动态时先按业务允许映射选择，再使用标识符引用 API | 任意引用正确的表或列都可开放 |
| `ASC`、`DESC`、运算符、完整过滤子句 | 选择由程序定义的有限语法片段 | 普通值占位符能替代任意语法 |

Psycopg 的 `sql.Identifier` 处理标识符规则，`sql.SQL` 表达 SQL 片段；两者不是字符串值绑定的替代品。`sql.SQL` 不会替任意传入字符串做安全引用，外部原文不应直接交给它。组合 API 见 [Psycopg：SQL composition](https://www.psycopg.org/psycopg3/docs/api/sql.html)。

允许映射是在定义产品能力，例如只开放“按新旧”和“按标题”两种排序。即便 `sql.Identifier` 能正确引用某个敏感列名，查询该列仍可能违反权限或暴露数据；语法安全与访问许可不是同一种保证。

## 教学例：可信主体、租户范围与排序同时约束

设 `app.documents` 的 `id` 是主键，包含 `tenant_id`、`owner_id`、`title`、`created_at`；`app.memberships` 包含 `tenant_id`、`user_id` 和布尔 `active`。本例策略是：主体必须是当前有效租户成员，并且只能列出自己拥有的文档。

调用链的前提是：服务端先完成[会话](../../glossary/security.md#security.sessions)或令牌验证，再由内部中间件建立 `auth_context`；`require_authenticated_subject_id()` 从这份已验证上下文取整数主体 ID，缺失或失效时拒绝。它不是客户端传入的对象，也不从请求中的 `user_id` 构造。数据库连接 `conn` 同样来自服务端配置。本例展示这些依赖的使用契约，不实现身份协议；给对象起名或加类型注解本身不会使它可信。

以下为完整的说明性查询函数，采用默认 Psycopg 游标；没有执行记录：

```python
from psycopg import sql

SORTS = {
    "newest": (sql.Identifier("d", "created_at"), sql.SQL("DESC")),
    "title": (sql.Identifier("d", "title"), sql.SQL("ASC")),
}

def list_my_documents(conn, auth_context, tenant_id, sort_key, limit=50):
    subject_id = auth_context.require_authenticated_subject_id()
    if type(tenant_id) is not int or tenant_id <= 0:
        raise ValueError("invalid tenant")
    if not isinstance(sort_key, str) or sort_key not in SORTS:
        raise ValueError("unsupported sort")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("invalid limit")

    order_column, order_direction = SORTS[sort_key]
    query = sql.SQL("""
        SELECT d.id, d.title, d.created_at
        FROM app.documents AS d
        WHERE d.tenant_id = %s
          AND d.owner_id = %s
          AND EXISTS (
              SELECT 1
              FROM app.memberships AS m
              WHERE m.tenant_id = d.tenant_id
                AND m.user_id = %s
                AND m.active
          )
        ORDER BY {} {}, d.id ASC
        LIMIT %s
    """).format(order_column, order_direction)

    with conn.cursor() as cur:
        cur.execute(query, (tenant_id, subject_id, subject_id, limit))
        return cur.fetchall()
```

这里由客户端选择的 `tenant_id` 只是目标选择，数据库内的成员关系与 `owner_id` 条件才限定本次可读范围。两个主体参数都来自可信上下文；排序列和方向只来自固定映射；所有筛选值与 `limit` 经绑定传递。`d.id` 是固定的并列次序补充，不让相同时间或标题的记录天然具有随机次序。

纸面判断：有效成员甲请求同租户时只得到自己的文档；把租户选择改成甲不是成员的租户，`EXISTS` 不成立；传入未定义的排序名称，在生成查询前拒绝。这些是由教学策略推导的预期，不是测试输出。若权限在并发事务中变化，当前查询的可见状态仍受[事务隔离](../../glossary/database.md#database.isolation)和[授权](../../glossary/security.md#security.identity)撤销协议约束。

## 绑定安全不等于模式与列表语义正确

`LIKE` 把 `%` 当作任意长度的通配，把 `_` 当作单字符通配。将 `100%` 安全绑定为模式后，它仍表示以 `100` 开头的一组字符串；这不是 SQL 注入，却可能不符合“搜索字面百分号”的需求。要字面匹配，应按固定 `ESCAPE` 约定处理模式元字符，并继续绑定结果。定义见 [PostgreSQL 18：`LIKE`](https://www.postgresql.org/docs/18/functions-matching.html#FUNCTIONS-LIKE)。

纸面例：对于 `LIKE %s ESCAPE '!'`，参数 `100!%%` 表示以字面 `100%` 开头；其中 `!%` 表示百分号本身，最后一个 `%` 才是前缀搜索的通配。要将任意输入作为字面前缀，可在这一固定约定下先把 `!` 替换为 `!!`，再把 `%` 替换为 `!%`、`_` 替换为 `!_`，最后追加一个 `%`，并继续绑定整个模式。先处理转义符，才能避免再次转义后续步骤新加的 `!`。

`IN` 列表也不是“给一个占位符传逗号分隔字符串”。Psycopg 可把同类 Python `list` 适配成 PostgreSQL 数组，使用 `id = ANY(%s)` 绑定该列表；另一种设计是由程序生成有限数量的值占位符，再逐项绑定，不能连接外部原文。驱动范围见 [Psycopg：列表适配](https://www.psycopg.org/psycopg3/docs/basic/adapt.html#lists-adaptation)。

还要定义空集合、重复项、`NULL` 与长度上限。作为成员筛选谓词，`id = ANY(...)` 对每行产生一次判断，列表中的重复匹配项不会额外复制该外层行；输入是否去重、计数或报告重复项，仍由业务契约决定。PostgreSQL 的 `ANY` 对空数组为假，而包含空值时可能得到未知结果；`NOT IN` 遇到空值也可能不按直觉返回真，见 [PostgreSQL 18：行与数组比较](https://www.postgresql.org/docs/18/functions-comparisons.html)。语法边界没有越界，不代表筛选结果和资源成本已满足契约。

## ORM、存储过程与已保存数据仍会遇到新边界

ORM 的参数化构造通常能保留值边界，但原生 SQL、文本表达式或手动拼接仍需单独审查。例如 SQLAlchemy 的 `text()` 支持 `:name` 绑定参数；如果调用前已经把外部值拼成完整 SQL，之后加一层包装不会恢复原来的值边界。API 见 [SQLAlchemy 2.0：`text()`](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text)。

存储过程把代码放在数据库里，不自动消除动态拼接。PL/pgSQL `EXECUTE` 的 `USING` 可提供数据值，动态表名或列名则需先获允许，再用 `format()` 的 `%I` 等正确引用；二者不能互换。见 [PostgreSQL 18：执行动态命令](https://www.postgresql.org/docs/18/plpgsql-statements.html#PLPGSQL-STATEMENTS-EXECUTING-DYN)。若函数以 `SECURITY DEFINER` 权限运行，还需审查执行授权、可信 `search_path` 与对象解析，见[安全编写定义者权限函数](https://www.postgresql.org/docs/18/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY)。

二次注入的关键是后来再次把数据解释成语法。教学路径：用户名称先经绑定保存，后台报表再把读出的名称拼进另一条 SQL。第一次保存安全，不会让名称永久变成可信 SQL。应沿“入口 → 存储 → 读取 → 最终执行”追踪，每次重新建立值与结构的边界；来自旧记录、内部接口或 ORM 返回值都不是免检理由。

## 参数化、服务端准备与计划复用不在同一层

| 层次 | 回答的问题 |
| --- | --- |
| 参数化接口 | 哪些内容是固定结构，哪些作为值传递？ |
| 绑定发生的位置 | 由驱动在客户端适配，还是把查询和值分开发往服务器？ |
| 服务端[预处理语句](../../glossary/database.md#database.prepared) | 是否在数据库会话中保存已准备的语句？ |
| 执行计划选择 | 本次使用通用计划，还是按参数形成定制计划？ |

Psycopg 的默认 `Cursor` 使用服务端绑定，但还有客户端绑定的 `ClientCursor`；不能只看到 `%s` 就判断服务器使用何种准备或执行机制。客户端绑定也不等于手工插值，仍应使用驱动规定的接口。范围见 [Psycopg：游标类型](https://www.psycopg.org/psycopg3/docs/advanced/cursors.html#client-side-binding-cursors)。

Psycopg 可按连接上的执行次数阈值自动准备语句，也可显式控制；其准备使用协议级机制，不是简单发送 SQL `PREPARE` 命令，见 [Psycopg：预处理语句](https://www.psycopg.org/psycopg3/docs/advanced/prepare.html)。

PostgreSQL SQL `PREPARE` 在当前数据库会话保存服务器对象，结束会话后不再存在；它并不保证每次使用同一份计划。PostgreSQL 18 可选择通用或定制计划，参数分布、统计信息与重规划会影响成本，见 [`PREPARE` 文档](https://www.postgresql.org/docs/18/sql-prepare.html)。所以参数化的安全作用不能推导成“所有接口都服务端预编译”或“计划始终最优”；性能分析继续见[索引与执行计划](../database/indexes-and-query-plans.md)。

## 参数化之外还有哪些责任

[对象授权](object-level-authorization.md)决定谁可读写哪些行和字段，[事务隔离](../database/isolation-and-mvcc.md)处理可见性和并发业务约束；参数绑定不会自动添加租户条件、解决检查后写入的竞态，或保持跨行[不变量](../../glossary/systems.md#systems.atomicity)。

应用数据库角色也应只拥有必要的表、列与操作权限，不以超级用户或迁移账号承载普通请求；数据库权限是另一层保护，见 [PostgreSQL 18：权限](https://www.postgresql.org/docs/18/ddl-priv.html)。连接凭据的保存、轮换与撤销继续见[密钥与凭证生命周期](secrets-credentials-rotation-and-revocation.md)，不能因查询已绑定就放宽凭据权限。

合法参数也可能导致大范围扫描、昂贵排序或过大的列表。示例的 `limit` 只限制返回行数，不是所有中间工作量的上限。应用仍需输入大小、查询与锁等待预算、结果大小及[接纳限制](../api/rate-limits-concurrency-and-quotas.md)；数据库的 `statement_timeout`、`lock_timeout` 各有计时范围，见 [PostgreSQL 18：客户端连接默认项](https://www.postgresql.org/docs/18/runtime-config-client.html)。本例未实现或验证这些资源策略。

## 自检与核查范围

审查一条查询时，逐项标出：可信主体来自哪里，目标对象如何限定，哪些位置是值参数，哪些结构来自允许映射，哪些值之后还会被其他查询再次解释。再用合法标点、未知排序、其他租户、空列表和模式通配各写一个预期，分别判断语法安全、权限与业务结果。

核查日期：2026-10-22。实际浏览 [OWASP](../../glossary/security.md#security.threats) SQL Injection Prevention、Psycopg 3 参数/组合/列表/游标/准备文档、PostgreSQL 18 上述章节与 SQLAlchemy 2.0 `text()` 参考。Psycopg 为当日滚动文档，页面标记 `3.3.7.dev1`，不代表本机已安装该版本；本文采用经典参数接口，没有测试开发版或其他版本。身份上下文、表结构、允许映射、报表路径和查询函数都是教学设计，状态为 `source-checked`；未连接数据库、执行 SQL、运行代码/业务测试、发起攻击请求，亦未验证计划、角色授权、并发撤销、[连接池](../../glossary/api.md#api.pool)或驱动兼容性。
