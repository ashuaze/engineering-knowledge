# 维护与贡献

## 修改已有文章

指出具体段落、观察到的反例、适用版本和一手来源。涉及行为改变的实验，提供最小复现及运行命令。维护者确认后更新正文和变更记录。

## 新增正文

1. 从一个实际工程问题出发，在知识索引中选择主领域和关联概念，检查是否已有相同问题。
2. 从 `templates/` 选择类型，在本地 `drafts/` 起草；按文章目的参考[七维学习框架](docs/handbook/editorial.md#concept-learning-template)，可增删、拆合、改名和调整章节顺序，无需写满七项。复制后删除模板说明并调整相对链接。
3. 填写元数据；id、slug 采用稳定英文名称；状态初始为 evolving。
4. 核查关键结论及适用范围；涉及方案或保证时说明关键失败风险，涉及实现或验证时明确实测与待验证项，然后移至 `docs/knowledge/<domain>/`。
5. 在 `data/terms.json` 的相应术语 `articles` 中添加正文路径；如果出现新术语，先给简释与别名。
6. 必要时手动更新问题导航与学习路径，避免用不存在文章制造链接。
7. 运行 `python3 scripts/generate_indexes.py`，再执行 README 中的校验命令。

可复用的独立实验放在 `examples/`。校验不会自动验证技术结论、远程链接或代码的生产可用性。

发布网站前还需运行 `npm run site:test`、`npm run docs:build` 和 `npm run docs:check`，并用 `npm run docs:preview` 检查中文搜索、手机阅读和文章跳转。侧栏根据领域和文章元数据生成，无需另写文章清单。新增指向 `docs/` 外的源码链接时，在 `docs/.vitepress/site.mjs` 的 `sourceFiles` 中加入允许导出的公共文件；不要关闭断链检查。

## 发布与更正

实质更正在 `docs/changelog.md` 说明影响。格式调整只更新 updated，不能刷新 last_verified。移动页面先设置兼容入口，避免破坏已分发链接。

建议提交主题：`content: ...`、`fix: ...`、`lab: ...`、`meta: ...`。提交贡献表示你有权提供相应内容，并同意按本项目对应许可分发：原创文字、图表与术语资料采用 CC BY 4.0，原创代码采用 MIT。保留已有署名与第三方许可，不提交无权授权的材料。具体范围见 [RIGHTS.md](RIGHTS.md)。
