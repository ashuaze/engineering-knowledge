# 工程知识库 · Engineering Fieldnotes

面向技术工程人员的长期知识库，涵盖软件开发、测试、运维与平台、数据、安全、架构及 AI 工程等方向：从概念出发，在机制、失败和取舍中形成判断。

内容围绕计算机基础、软件系统、数据与生产工程展开，17 个领域均已建立正文入口。当前阶段优先分批补充跨领域核心概念，具体进度见[概念补全路线图](docs/handbook/concept-roadmap.md)。中文正文，保留英文术语便于检索，读者可按岗位、已有基础和当前任务选择学习重点。

把领域与术语清单作为知识索引，从[实际工程问题](docs/problems.md)进入学习。[七维学习框架](docs/handbook/editorial.md#concept-learning-template)提供定义、原理、取舍、实现、失败、实践与关联七个思考角度；文章按目的选用、合并或调整，不固定章节名称、数量和顺序。长期积累的重点是底层原理、系统设计、故障诊断和技术权衡能力，以解释、实现、观测和决策证据检验学习成果。

## 从这里开始

| 你的目的 | 入口 |
| --- | --- |
| 了解这套知识库 | [首页](docs/index.md) · [设计蓝图](docs/handbook/design.md) |
| 从实际工程问题开始 | [问题导航](docs/problems.md) |
| 查一个概念 | [术语索引](docs/glossary.md) |
| 系统学习 | [学习路径](docs/paths/index.md) |
| 阅读正文与跟进选题 | [文章目录](docs/articles.md) · [概念路线图](docs/handbook/concept-roadmap.md) · [选题进度](docs/handbook/topics.md) |
| 运行实验 | [幂等性](docs/knowledge/api/idempotency-lab.md) · [重试预算](docs/knowledge/reliability/timeouts-and-retry-budgets.md) · [对象授权](docs/knowledge/security/object-level-authorization.md) |
| 贡献、订正与持续维护 | [维护规范](CONTRIBUTING.md) · [写作规范](docs/handbook/editorial.md) |
| 准备对外发布 | [发布方案](docs/handbook/publishing.md) |

## 当前内容范围

目前有 18 篇正文，涵盖概念、对比、模式、案例、实验与决策。最新一批补入进程/线程/协程、HTTPS 请求链路、复杂度与结构选择、缓存失效、一致性与复制、交付生命周期、测试层次七篇核心概念文章。17 个领域均有正文入口，其中 15 个领域已有概念类正文；架构与性能的核心概念列为下一批优先项。

同一主题可覆盖多个术语。索引中的“已收录”表示有简释，“有正文”表示连接了相关深入文章；具体解释深度以正文为准。当前优先概念、原理与边界，实践维度保留必要示例和自检，独立实验按后续阶段推进。

## 本地使用

本仓库无需安装依赖即可阅读 Markdown；维护脚本要求 Python 3.10+。

网站使用 Node.js 24。在仓库根目录运行：

```bash
npm ci
npm run docs:dev
```

按终端提示打开本地网址，默认路径为 `/engineering-knowledge/`。正式构建与验收：

```bash
npm run site:test
npm run docs:build
npm run docs:check
npm run docs:preview
```

网站包括中文本地搜索、领域导航和文章核查信息。完整配置与首次上线步骤见[发布手册](docs/handbook/publishing.md)。

```bash
python3 scripts/validate.py
python3 -m unittest discover -s examples/idempotency -p 'test_*.py' -v
python3 -m unittest discover -s examples/retry_budget -p 'test_*.py' -v
python3 -m unittest discover -s examples/object_authorization -p 'test_*.py' -v
python3 scripts/generate_indexes.py --check
```

修改 `data/terms.json`、新增正文后，运行 `python3 scripts/generate_indexes.py` 更新生成的领域页、文章目录和术语索引。生成页请通过源数据修改。GitHub Actions 会运行结构校验、索引一致性检查、实验测试和网站构建验收；Pages 发布从默认分支手动触发。

## 仓库边界

- `docs/`：读者可直接阅读的公共内容。
- `data/`：领域和术语的唯一索引数据；正文只保存于所属领域。
- `templates/`：六类写作模板。
- `examples/`：与正文对应的可运行实验。
- `scripts/`：索引生成、元数据与内部文件链接校验。
- `drafts/`、`personal/`：仅保留说明文件，具体草稿和个人评估由 Git 忽略。

本版已提供网站与 GitHub Pages 发布配置，尚未关联远程仓库或部署公开网站。原创正文、图表与术语资料采用 CC BY 4.0，原创代码采用 MIT。使用与转载条件见 [RIGHTS.md](RIGHTS.md)，协议全文分别保存在 `LICENSE-CONTENT` 和 `LICENSE-CODE`。
