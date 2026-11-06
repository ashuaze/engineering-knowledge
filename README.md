# 工程知识库 · Engineering Fieldnotes

面向技术工程人员的长期知识库，涵盖软件开发、测试、运维与平台、数据、安全、架构及 AI 工程等方向：从概念出发，在机制、失败和取舍中形成判断。

内容围绕计算机基础、软件系统、数据与生产工程展开，17 个领域均已建立正文入口。当前阶段优先分批补充跨领域核心概念，具体进度见[概念补全路线图](docs/handbook/concept-roadmap.md)。中文正文，保留英文术语便于检索，读者可按岗位、已有基础和当前任务选择学习重点。

把领域与术语清单作为知识索引，从[实际工程问题](docs/problems.md)进入学习。[七维学习框架](docs/handbook/editorial.md#concept-learning-template)提供定义、原理、取舍、实现、失败、实践与关联七个思考角度；文章按目的选用、合并或调整，不固定章节名称、数量和顺序。长期积累的重点是底层原理、系统设计、故障诊断和技术权衡能力，以解释、实现、观测和决策证据检验学习成果。

## 从这里开始

| 你的目的 | 入口 |
| --- | --- |
| 了解这套知识库 | [首页](docs/index.md) · [设计蓝图](docs/handbook/design.md) |
| 从实际工程问题开始 | [问题导航](docs/problems.md) |
| 查一个概念 | [术语索引](docs/glossary.md) · [分类词汇表](docs/glossary/index.md) |
| 系统学习 | [学习路径](docs/paths/index.md) |
| 阅读正文与跟进选题 | [文章目录](docs/articles.md) · [概念路线图](docs/handbook/concept-roadmap.md) · [选题进度](docs/handbook/topics.md) |
| 跟进内容更新安排 | [四周更新计划](UPDATE_PLAN.md) |
| 运行实验 | [幂等性](docs/knowledge/api/idempotency-lab.md) · [重试预算](docs/knowledge/reliability/timeouts-and-retry-budgets.md) · [对象授权](docs/knowledge/security/object-level-authorization.md) · [查询计划](docs/knowledge/database/query-plans-lab.md) · [长任务](docs/knowledge/frontend/long-tasks-lab.md) · [库存并发](docs/knowledge/database/inventory-concurrency-lab.md) · [备份恢复](docs/knowledge/database/backup-recovery-lab.md) · [过载控制](docs/knowledge/performance/overload-control-lab.md) · [连接生命周期](docs/knowledge/networking/connection-lifecycle-lab.md) · [工具执行边界](docs/knowledge/ai/tool-execution-boundaries-lab.md) · [记忆治理实验](docs/knowledge/ai/memory-governance-lab.md) |
| 贡献、订正与持续维护 | [维护规范](CONTRIBUTING.md) · [写作规范](docs/handbook/editorial.md) |
| 准备对外发布 | [发布方案](docs/handbook/publishing.md) |

## 当前内容范围

目前有 201 篇正文，17 个领域均有概念入口。本批补齐遗留八组：[BFF与前端适配](docs/knowledge/frontend/backends-for-frontends-projections-and-service-boundaries.md)、[复制与读副本](docs/knowledge/distributed/consistency-and-replication.md)、[分布式锁与缓存租约](docs/knowledge/distributed/leases-heartbeats-and-fencing.md)、[队列、发布订阅与事件流](docs/knowledge/messaging/queues-pubsub-event-streams-and-retention.md)、[提示词与指令边界](docs/knowledge/ai/prompts-message-roles-and-instruction-boundaries.md)、[温度、采样与复现](docs/knowledge/ai/temperature-sampling-and-reproducibility.md)、[MCP与能力协商](docs/knowledge/ai/mcp-hosts-capabilities-and-execution-boundaries.md)、[微调、蒸馏与评估](docs/knowledge/ai/fine-tuning-distillation-and-evaluation-boundaries.md)。六篇新文配合两篇既有专题增补，补齐最后八组词条关联；313组现有词条都有正文入口，具体子概念、产品机制和真实验证继续保留缺口。当前范围见[概念路线图](docs/handbook/concept-roadmap.md)和[三条主线覆盖清单](docs/handbook/concept-coverage.md)，验收见[更新计划](UPDATE_PLAN.md)。

同一主题可覆盖多个术语。每组均有分类词汇表解释，包含定义、区别与边界和说明性例子；索引中的“有正文”表示另有相关深入文章。读者页面中的首次明确术语提及链接到解释，具体版本与验证深度以正文为准。当前优先概念、原理与边界，实践维度保留必要示例和自检，独立实验按后续阶段推进。

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
python3 scripts/link_glossary.py --check
python3 -m unittest discover -s scripts -p 'test_*.py' -v
node examples/connection_lifecycle/lab.mjs --check
python3 examples/ai_tool_boundaries/lab.py --check
python3 examples/memory_governance/lab.py --check
```

修改 `data/terms.json`、新增正文后，先运行 `python3 scripts/link_glossary.py` 补充读者页面的术语链接，再运行 `python3 scripts/generate_indexes.py` 更新领域页、文章目录、术语索引和 `docs/glossary/` 分类解释。生成页请通过源数据修改。GitHub Actions 会运行结构校验、索引与术语链接一致性检查、实验测试和网站构建验收；Pages 发布从默认分支手动触发。

## 仓库边界

- `docs/`：读者可直接阅读的公共内容。
- `data/`：领域和术语的唯一索引数据；正文只保存于所属领域。
- `docs/glossary/`：按领域生成的词汇解释，每组术语用稳定 ID 定位。
- `templates/`：六类写作模板。
- `examples/`：与正文对应的可运行实验。
- `scripts/`：索引生成、元数据与内部文件链接校验。
- `drafts/`、`personal/`：仅保留说明文件，具体草稿和个人评估由 Git 忽略。

源码位于 [ashuaze/engineering-knowledge](https://github.com/ashuaze/engineering-knowledge)，Pages 发布目标为[工程知识库网站](https://ashuaze.github.io/engineering-knowledge/)。站点从默认分支手动发布，检查通过后部署同一份构建产物。

原创正文、图表与术语资料采用 CC BY 4.0，原创代码采用 MIT。使用与转载条件见 [RIGHTS.md](RIGHTS.md)，协议全文分别保存在 `LICENSE-CONTENT` 和 `LICENSE-CODE`。
