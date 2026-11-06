# 工程知识库 · Impeccable 审查

审查日期：2026-11-06（Asia/Shanghai）。对象为当前本地工作区的正式构建，未将结果外推到已发布网站。

方法：[Impeccable 4.8.0 的 audit 流程](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/audit.md)，配合官方检测器 engine 0.1.18、axe-core 4.11.0，以及 Playwright / Chromium 151.0.7922.34 的页面与交互检查。页面类型按 Read（阅读）判断。

## 实现一致性结论

**通过：站点具有一致、适合中文工程文档的阅读体系。** 自定义主题集中使用 VitePress 颜色变量，正文、文章信息、导航与深浅主题保持一致；抽查的内容数量与元数据一致。没有发现虚构证明、装饰性仪表板或需要推倒重做的结构问题。

主要欠账在默认组件继承的无障碍语义、代码语言标签的颜色，以及搜索索引的首次加载。源码扫描没有命中机械规则，渲染检查和交互复核仍发现以下问题。

## 健康评分

评分是本次抽查的工程判断，不是 WCAG 合规认证。

| 维度 | 分数 | 依据 |
| --- | ---: | --- |
| 可访问性 | 2/4 | 目录和搜索存在嵌套交互，展开状态及焦点恢复不完整；代码标签对比度不足 |
| 性能 | 2/4 | 搜索索引原文件约 5.87 MB，冷缓存搜索等待明显，缺少加载反馈 |
| 主题 | 3/4 | 深浅主题主体正常，代码标签继承的弱文字颜色需要补齐 |
| 响应式 | 3/4 | 8 页 × 6 个宽度无整页横向溢出；手机目录模拟触摸可用，部分控件小于 44 px 的舒适目标 |
| 实现一致性 | 4/4 | 主题、组件和文档模式一致，真实内容与证据标识明确 |
| **合计** | **14/20** | **良好，优先补可访问性和首次搜索体验** |

共归并 **4 项 P1**；本次范围内未发现 P0。相同根因的重复节点合并计数，不将 18 个目录分组或 16 条搜索结果分别计为问题。

## 需要优先处理的问题

### 1. [P1] 目录折叠控件包含嵌套按钮，未暴露展开状态

- **位置**：[目录配置](docs/.vitepress/config.mts#L77)、[领域目录生成](docs/.vitepress/site.mjs#L150)。根因来自 [VitePress 的 VPSidebarItem](https://github.com/vuejs/vitepress/blob/v1.6.4/src/client/theme-default/components/VPSidebarItem.vue)。
- **类别**：可访问性。
- **证据**：正文和术语页稳定状态下均有 18 个 `nested-interactive` 节点。分组外层是可聚焦的 `div[role=button]`，内部还有可聚焦的箭头 `div[role=button]`。以“分类词汇表”为例，Space 不展开，Enter 可以展开，但操作前后都没有 `aria-expanded`。
- **影响**：读屏用户难以获得分组展开状态，焦点重复且按钮的键盘行为不完整。普通鼠标点击可用不代表该导航完整可访问。
- **标准**：WCAG 4.1.2（名称、角色、值）；按钮的 Space/Enter 行为参照 WAI-ARIA 按钮模式。
- **建议**：采用一个原生按钮承担分组展开，提供动态 `aria-expanded` 和必要的 `aria-controls`，箭头作为非交互装饰；移除嵌套焦点。通过受控主题组件或经验证的依赖升级解决，不直接修改 `node_modules`。
- **建议命令**：`$impeccable harden`。

### 2. [P1] 搜索弹窗语义与焦点恢复不完整

- **位置**：[本地搜索配置](docs/.vitepress/config.mts#L106)。根因来自 [VPLocalSearchBox 模板](https://github.com/vuejs/vitepress/blob/v1.6.4/src/client/theme-default/components/VPLocalSearchBox.vue)。
- **类别**：可访问性。
- **证据**：弹窗最外层使用 `role=button`，内部包括搜索输入、操作按钮和结果列表。独立扫描搜索容器得到 17 个 `nested-interactive` 节点：外层容器 1 个，以及带可聚焦链接的 `role=option` 结果项 16 个。通过键盘从搜索按钮打开后，按 Escape 关闭，焦点落到 `BODY`；下一次 Tab 回到“跳到正文”，没有回到搜索触发按钮。
- **影响**：辅助技术获得的交互结构与实际弹窗不一致；键盘用户关闭搜索后丢失原来的操作位置。
- **标准**：WCAG 4.1.2；焦点恢复参照 WAI-ARIA 模态对话框模式。本次将焦点丢失作为同一组件的相关问题合并记录，没有仅凭这一现象断言完整的焦点顺序合规情况。
- **建议**：为弹窗采用带名称的对话框语义；统一输入与结果的交互模型，避免在非交互后代约束的角色中嵌入焦点控件。关闭和取消时恢复触发点，结果跳转时将焦点交给目标正文。覆盖 Enter 打开、方向键选结果、Escape 关闭及再次 Tab 的完整路径。
- **建议命令**：`$impeccable harden`。

### 3. [P1] 代码语言标签在两种主题下均未达到文字对比度要求

- **位置**：[主题变量](docs/.vitepress/theme/style.css#L1)。继承值见 [VitePress 的代码变量](https://github.com/vuejs/vitepress/blob/v1.6.4/src/client/theme-default/styles/vars.css)；渲染元素为代码块内的 `span.lang`。
- **类别**：可访问性 / 主题。
- **证据**：幂等性正文中的 `text` 语言标签为 12 px 普通文字。浅色主题 `#929295` / `#f6f6f7`，对比度 **2.87:1**；深色主题 `#6a6a71` / `#121b26`，对比度 **3.23:1**。Impeccable 的桌面、手机检测与稳定状态下的 axe 复核相符。
- **影响**：低视力读者难以辨识代码块的语言类型；该标签不是大号文字，不能套用 3:1 门槛。
- **标准**：WCAG 1.4.3，普通文字至少 4.5:1。
- **建议**：在项目主题中显式设置浅色与深色的 `--vp-code-lang-color`，可从已具有足够对比度的次级文字变量开始验证；同时检查行号等弱文字，但不要未经测量批量改色。
- **建议命令**：`$impeccable colorize`。

### 4. [P1] 首次搜索加载等待明显，期间没有状态反馈

- **位置**：[搜索入口与索引配置](docs/.vitepress/config.mts#L106)、[全文索引渲染范围](docs/.vitepress/config.mts#L125)。默认组件同步装载索引的路径见 [VPLocalSearchBox](https://github.com/vuejs/vitepress/blob/v1.6.4/src/client/theme-default/components/VPLocalSearchBox.vue)。
- **类别**：性能 / 交互状态。
- **证据**：正式构建生成 `@localSearchIndexroot.DBsFudZZ.js`，原文件 **5,868,200 字节**；本地浏览器响应压缩后 **943,914 字节**，解码后仍为上述体积。一个未限速、冷浏览器缓存的本机样本中，打开搜索至“幂等性”结果出现约 **14.2 秒**，包含约 734 ms 的长任务。另一轮模拟 1.6 Mbps 下载、150 ms 延迟、CPU 4 倍减速的样本约 **38.2 秒**，弹窗约 1.0 秒就已出现，但等待索引期间没有加载文字、进度或失败提示。暖缓存的后续查询样本约 **1.0 秒**。
- **影响**：首次访客可能将空白结果区判断为搜索失效，退出主要查找路径。随着文章和术语增加，冷启动成本还可能增长。
- **标准**：性能与状态反馈问题；这些本机与模拟样本不作为生产站点的 Core Web Vitals 或真实设备承诺。
- **建议**：先为索引加载增加明确的等待、失败与重试状态；再减少重复索引内容、评估按领域拆分或增量装载，并考虑将解析和检索放入 Worker。当前响应已经压缩，单纯建议“打开压缩”不能解决问题。以冷缓存和暖缓存分别验收。
- **建议命令**：`$impeccable optimize`，配合 `$impeccable harden` 补充状态。

## 另一个值得安排的阅读体验改进

首页的[“建议先读”](docs/index.md)实际累计了 **42 段**推荐与批次说明；在 375 px 宽度下整页约 **10,889 px** 高。它越来越接近更新记录，对首次访客的选读指引不够集中。

这是内容层次观察，未计入上面的技术缺陷数量和评分。建议后续用 `$impeccable distill` 将首页保留为少量按任务分类的入口，把批次说明集中到更新页。无需为此增加营销式首屏、装饰卡片或动画。

## 误报处理与保持项

- **排除主题切换瞬间的批量对比度误报**：初轮立即切换主题后扫描，捕获到大量过渡色。等待至少 650 ms 后重测，首页两种主题均无所选 WCAG 规则违规；术语页没有稳定存在的颜色违规。仅保留上述代码语言标签问题。
- **排除截图中的移动目录过渡状态**：首轮连续调整视口时截到了侧栏滑动途中；稳定状态重新截图和模拟触摸验证后，没有发现侧栏固定错位。
- **品牌标识不升级为技术缺陷**：Impeccable 手机检测标记首页 `ENGINEERING FIELDNOTES` 为 `kicker-above-heading`。它是实际英文名称，未发现其阻碍阅读或操作，本次仅记录该风格规则命中。
- **未把 44 px 舒适目标直接当成 AA 违规**：部分目录链接和按钮小于 44 px，但需结合 WCAG 2.5.8 的 24 px 下限、间距和例外判断；本次未据此追加 AA 违规。
- **保留现有优势**：6 档宽度的页面根节点均无横向溢出；宽表格局部滚动，未把整页撑宽；主导航 Tab 顺序与可见焦点正常；手机目录模拟触摸展开及 Escape 关闭正常；空搜索结果有中文建议；抽查页面无 JavaScript 运行错误；构建通过。

## 验证范围与证据

- 页面：首页、问题导航、学习路径、知识地图、文章目录、术语索引、幂等性正文、三线覆盖清单，共 8 页。
- 响应式宽度：320 / 375 / 414 / 768 / 1024 / 1440 CSS px，共 48 个页面与宽度组合。
- 稳定状态无障碍扫描：首页、正文、术语索引的深浅主题，以及搜索结果容器；另测移动目录、键盘和模拟触摸。
- 浏览器：Chromium headless；触摸为 Playwright 合成触摸，不是真机。没有进行屏幕阅读器人工朗读、Firefox/WebKit 全矩阵、完整站点逐页或真实设备测试。修改根字号的补充检查不等同于浏览器真实 200% 缩放，未据此宣称通过文字放大合规。
- 官方源码扫描结果为空；桌面渲染检测命中代码标签对比度，手机渲染检测另命中英文名称样式规则。其余问题由 axe、DOM 和交互复核确认。

原始材料保存在 .cache/impeccable-audit（本机缓存：`.cache/impeccable-audit`）：

| 材料 | 文件 |
| --- | --- |
| Impeccable 桌面检测 | detector-desktop.json（本机缓存：`.cache/impeccable-audit/detector-desktop.json`） |
| Impeccable 手机检测 | detector-mobile.json（本机缓存：`.cache/impeccable-audit/detector-mobile.json`） |
| 初轮页面与性能观察 | observations.json（本机缓存：`.cache/impeccable-audit/observations.json`） |
| 排除过渡状态后的稳定复核 | verification.json（本机缓存：`.cache/impeccable-audit/verification.json`） |
| 搜索独立复核 | search-verification.json（本机缓存：`.cache/impeccable-audit/search-verification.json`） |
| 等待索引时的搜索界面 | search-early.png（本机缓存：`.cache/impeccable-audit/search-early.png`） |
| 代码语言标签，浅色 / 深色 | 浅色截图（本机缓存：`.cache/impeccable-audit/code-language-contrast-light.png`） / 深色截图（本机缓存：`.cache/impeccable-audit/code-language-contrast-dark.png`） |

## 建议执行顺序

1. **P1 — `$impeccable harden`**：修目录和搜索的语义、展开状态及焦点恢复。
2. **P1 — `$impeccable colorize`**：补齐代码语言标签在两种主题中的颜色。
3. **P1 — `$impeccable optimize`**：降低搜索冷启动成本，配合 harden 补齐等待与失败状态。
4. **可选 — `$impeccable distill`**：精简首页“建议先读”，另行收纳批次说明。
5. **`$impeccable polish`**：处理修复后的间距、焦点和主题细节。
6. **`$impeccable audit`**：重跑原场景，比较冷 / 暖缓存样本与稳定主题结果。

可逐项或整批执行。后续复审应使用同一组页面与条件，以便比较。

参考：[WCAG 文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[名称、角色、值](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html)、[最小目标尺寸](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)、[WAI-ARIA 按钮模式](https://www.w3.org/WAI/ARIA/apg/patterns/button/)、[模态对话框模式](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)。

## 实施后复核 · 2026-11-06

用户随后授权实施 Mintlify 配色的阅读主题。本报告前文保留为实施前的审查记录。

上述四项问题已在项目主题中处理：目录改用原生折叠控件；搜索改用具名 dialog 并恢复焦点；代码语言颜色使用深浅主题的可读变量；全文搜索使用压缩数据和 Worker，并补齐加载、错误与重试状态。首页的批次说明已移入阅读更新页。

实施后 Impeccable 检测为空；9 页、6 档宽度无整页横向溢出；抽查的深浅主题和搜索弹窗未发现所选 axe 规则违规。Chromium 和 Firefox 的相关交互通过。具体条件、限制和原始证据位置见 [主题实施验证](THEME_VALIDATION.md)，不将本次抽查表述为完整 WCAG 或全浏览器认证。
