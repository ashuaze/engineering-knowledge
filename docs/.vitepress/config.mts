import { defineConfig } from 'vitepress';
import {
  getSiteSettings, getDomains, getDomainNavigation,
  repositoryLinks, supportingSources, copySupportingSources
} from './site.mjs';
import { tokenize } from './search.mjs';

const settings = getSiteSettings();
const domains = getDomains();

export default defineConfig({
  lang: 'zh-CN',
  title: '工程知识库',
  description: '理解原理，解释故障，做出有依据的工程取舍。',
  base: settings.base,
  cleanUrls: false,
  // Keep maintainer references in Git; do not emit public pages for them.
  srcExclude: ['changelog.md', 'handbook/editorial.md', 'handbook/topics.md', 'handbook/design.md'],
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${settings.base}favicon.svg` }],
    ['meta', { name: 'theme-color', content: '#176b75' }]
  ],
  markdown: {
    config(md) { md.use(repositoryLinks(settings)); }
  },
  vite: { plugins: [supportingSources(settings)] },
  buildEnd(config) { copySupportingSources(config.outDir); },
  transformPageData(page) {
    if (page.frontmatter.summary) page.description = page.frontmatter.summary;
    if (page.relativePath === 'index.md') {
      Object.assign(page.frontmatter, { sidebar: false, aside: false, pageClass: 'fieldnotes-home' });
    }
    if (page.relativePath.startsWith('handbook/') || ['rights.md', 'changelog.md'].includes(page.relativePath)) {
      // Keep writing and publishing instructions out of readers' concept searches.
      page.frontmatter.search = false;
    }
  },
  ...(settings.siteUrl ? {
    sitemap: { hostname: `${settings.siteUrl}/` },
    transformHead({ pageData }) {
      if (pageData.isNotFound) return [];
      const route = pageData.relativePath.replace(/index\.md$/, '').replace(/\.md$/, '.html');
      const canonical = `${settings.siteUrl}/${route}`;
      return [
        ['link', { rel: 'canonical', href: canonical }],
        ['meta', { property: 'og:title', content: pageData.title }],
        ['meta', { property: 'og:description', content: pageData.description }],
        ['meta', { property: 'og:url', content: canonical }]
      ];
    }
  } : {}),
  themeConfig: {
    siteTitle: '工程知识库',
    nav: [
      { text: '问题导航', link: '/problems.html' },
      { text: '学习路径', link: '/paths/' },
      { text: '知识地图', link: '/map.html' },
      { text: '文章', link: '/articles.html' },
      { text: '更多', items: [
        { text: '术语索引', link: '/glossary.html' },
        { text: '概念路线图', link: '/handbook/concept-roadmap.html' },
        { text: '使用与转载条件', link: '/rights.html' },
        ...(settings.repositoryUrl ? [{ text: 'GitHub 仓库', link: settings.repositoryUrl }] : [])
      ] }
    ],
    sidebar: [
      { text: '阅读入口', items: [
        { text: '从这里开始', link: '/' },
        { text: '问题导航', link: '/problems.html' },
        { text: '学习路径', link: '/paths/' },
        { text: '知识地图', link: '/map.html' },
        { text: '术语索引', link: '/glossary.html' },
        { text: '全部文章', link: '/articles.html' }
      ] },
      ...domains.map(getDomainNavigation)
    ],
    ...(settings.repositoryUrl ? {
      socialLinks: [{ icon: 'github', link: settings.repositoryUrl }],
      editLink: {
        pattern: `${settings.repositoryUrl}/edit/HEAD/docs/:path`,
        text: '在 GitHub 上提出修改'
      }
    } : {}),
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    sidebarMenuLabel: '阅读目录',
    returnToTopLabel: '返回顶部',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换浅色模式',
    darkModeSwitchTitle: '切换深色模式',
    skipToContentLabel: '跳到正文',
    notFound: {
      title: '没有找到这一页',
      quote: '页面可能已移动。可以返回首页，或通过搜索寻找相关概念。',
      linkLabel: '返回首页', linkText: '返回首页'
    },
    footer: {
      message: `<a href="${settings.base}rights.html">正文 CC BY 4.0 · 代码 MIT · 使用与转载条件</a>`,
      copyright: 'Engineering Fieldnotes · 持续维护的工程笔记'
    },
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: { tokenize },
          searchOptions: { combineWith: 'AND', prefix: true, fuzzy: false }
        },
        translations: {
          button: { buttonText: '搜索知识库', buttonAriaLabel: '搜索知识库' },
          modal: {
            displayDetails: '显示摘要',
            resetButtonTitle: '清空搜索',
            backButtonTitle: '关闭搜索',
            noResultsText: '没有找到相关内容，试试中文术语或英文名称。',
            footer: {
              selectText: '选择', navigateText: '切换', closeText: '关闭'
            }
          }
        },
        _render(src, env, md) {
          const html = md.render(src, env);
          if (env.frontmatter?.search === false || env.relativePath.startsWith('handbook/') || ['rights.md', 'changelog.md'].includes(env.relativePath)) return '';
          return html;
        }
      }
    }
  }
});
