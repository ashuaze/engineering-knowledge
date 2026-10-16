# 发布工程知识库

配置日期：2026-10-16。仓库已配置 VitePress 1.6.4、中文本地搜索和 GitHub Pages 工作流。源码位于 [ashuaze/engineering-knowledge](https://github.com/ashuaze/engineering-knowledge)，Pages 发布目标为[工程知识库网站](https://ashuaze.github.io/engineering-knowledge/)。本地构建通过不代表公开部署成功，发布状态以 Actions 结果与线上访问为准。

## 本地阅读与预览

直接阅读 Markdown 不需要安装依赖。站点使用 Node.js 24，内容校验与实验要求 Python 3.10+；持续集成固定使用 Python 3.13。

在仓库根目录安装锁定的依赖，然后启动开发预览：

```bash
npm ci
npm run docs:dev
```

默认访问 `http://localhost:5173/engineering-knowledge/`，以终端实际输出为准。开发服务只监听本机。

验收发布结果使用构建预览：

```bash
python scripts/validate.py
python scripts/generate_indexes.py --check
npm run site:test
npm run docs:build
npm run docs:check
npm run docs:preview
```

构建预览默认位于 `http://localhost:4173/engineering-knowledge/`。检查器会遍历生成 HTML 的本地链接、锚点和静态资源，并确认它们没有遗漏项目路径前缀。它不访问外部链接，也不代替浏览器中的搜索、手机阅读和跳转检查。

## 首次发布到 GitHub Pages

1. 创建你选择的 GitHub 仓库，上传当前内容。仓库名可以改变；不需要把它命名为用户站点专用仓库。
2. 在仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
3. 在 Actions 中选择 **Deploy GitHub Pages**，从仓库默认分支执行 **Run workflow**。
4. 工作流读取 Pages 的实际网址，再依次执行元数据与链接校验、生成索引检查、25 项实验测试、站点配置测试、网站构建和生成页面检查。
5. 所有检查通过后上传构建产物，部署任务直接发布同一份产物。实际网址显示在部署结果与 `github-pages` 环境中。

首次发布采用手动触发。普通 push 和 pull request 只运行 **Content and site checks**，不会上线。部署工作流只允许从默认分支执行，不要求默认分支一定叫 `main`。

Pages 发布只使用 GitHub 提供的临时令牌与 OIDC，不需要在仓库中保存个人访问令牌。检查任务只有读取内容的权限，部署任务具有 Pages 写入权限。

## 仓库地址与网址

配置优先读取环境变量，不在源码中假定你的 GitHub 用户名：

| 变量 | 用途 | 默认行为 |
| --- | --- | --- |
| `SITE_REPOSITORY` | `owner/repository` 或完整 GitHub HTTPS 仓库地址 | 在 Actions 中使用 `GITHUB_REPOSITORY`；本地未填写则提供源码预览 |
| `SITE_BASE` | 以 `/` 开头和结尾的部署路径 | 按实际仓库名生成；本地无仓库信息时为 `/engineering-knowledge/` |
| `SITE_URL` | 包含项目路径的完整 HTTPS 网站地址 | 未填写时不生成 canonical 与 sitemap，避免发布错误网址 |
| `SITE_SOURCE_REF` | 源码链接对应的分支或提交 | Actions 构建提交；本地使用 `HEAD` |

正式部署时，工作流通过 GitHub 的 Pages 配置自动传入 `SITE_BASE` 与 `SITE_URL`，支持项目站点、用户站点和独立域名。仅运行检查工作流时，也可以通过仓库 Variables 中的同名变量覆盖路径与网址。

本地模拟根路径部署可在 PowerShell 中执行：

```powershell
$env:SITE_BASE = '/'
npm run docs:build
npm run docs:check
npm run docs:preview
```

改变环境变量后需要重新启动开发服务，或重新构建并预览。模拟完成后用 `Remove-Item Env:SITE_BASE` 恢复默认值。若填写 `SITE_URL`，它的路径必须与 `SITE_BASE` 一致。

## 内容源与站点边界

正文继续保存在 `docs/`，领域和文章侧栏从 `data/domains.json` 及文章元数据读取，不复制正文。中文与英文搜索使用同一套分词规则，搜索结果支持“幂等性”“重试预算”“协程”“Outbox”等查询；维护手册、许可说明和变更记录不进入概念搜索。

文章顶部显示内容类型、成熟度、验证方式、更新时间与核查日期，直接使用已有元数据。构建时间和 Git 提交时间不会刷新核查日期。

`VALIDATION.md` 和实验代码位于仓库根目录。站点渲染时会把这些链接转换成实际 GitHub 仓库中的文件链接，指向当前构建提交；Markdown 原文仍使用相对路径，便于在 GitHub 和本地阅读。

没有仓库地址的本地预览使用 `/_source/` 下的纯文本副本。导出范围由 `docs/.vitepress/site.mjs` 中的 `sourceFiles` 明确列出，只包含验证记录和三个实验的实现与测试。新增站点外链接时同步维护这份清单；无法识别的站点外链接会让构建失败。

`docs/rights.md` 引用根目录的 `RIGHTS.md`，不另存使用条件。原创正文、图表与术语资料采用 CC BY 4.0，原创代码采用 MIT；标准全文分别保存在根目录的 `LICENSE-CONTENT` 与 `LICENSE-CODE`。站点页脚展示两种许可并链接使用条件。

更新记录、写作审阅规范、选题输出进度和内部设计蓝图通过 `srcExclude` 排除，不生成站点页面；这些文件继续保留在仓库供维护使用。首页、问题导航、学习路径与生成索引不再链接被排除的页面。`drafts/`、`personal/`、模板、缓存与环境文件不进入网站。

## 上线验收与后续更新

首次发布后检查首页、领域入口、文章直接打开与刷新、404、搜索、代码块、长表格、手机导航，以及文章中的 GitHub 源码链接。独立域名在仓库 Pages 设置中配置并启用 HTTPS；部署流程会读取更新后的网址。

确认首版表现后，可以给 `.github/workflows/deploy.yml` 的 `on` 增加针对实际默认分支的 `push` 触发器，保留现有检查和手动入口。无需为自动发布维护第二套构建流程。

更正正文仍按贡献规范维护。移动页面前提供旧地址兼容入口；回退版本后重新执行发布工作流，不直接修改生成文件。

## 官方说明

- [VitePress 1.x 部署指南](https://vuejs.github.io/vitepress/v1/guide/deploy)
- [VitePress 本地搜索配置](https://vuejs.github.io/vitepress/v1/reference/default-theme-search)
- [GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [GitHub Pages 自定义域名](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)
