<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useData, useRoute, withBase } from 'vitepress';
import KnowledgeSidebar from './components/KnowledgeSidebar.vue';
import KnowledgeSearch from './components/KnowledgeSearch.vue';
import ThemeIcon from './components/ThemeIcon.vue';

const { page, theme, frontmatter, isDark, site } = useData();
const route = useRoute();
const drawer = ref();
const mobileOutline = ref();
const main = ref();
const activeHeading = ref('');
const showTop = ref(false);
let drawerTrigger;
let restoreDrawerFocus = true;
let observer;
let tableObserver;
const isHome = computed(() => page.value.relativePath === 'index.md');
const domain = computed(() => theme.value.fieldnotes.domains.find(item => page.value.relativePath.startsWith(`knowledge/${item.id}/`)));
const links = computed(() => theme.value.nav.filter(item => item.link));
const repository = computed(() => theme.value.socialLinks?.find(item => item.icon === 'github')?.link);
const headings = computed(() => (page.value.headers || []).flatMap(header => [header, ...(header.children || [])])
  .filter(header => header.level <= 3).map(header => ({ ...header, title: header.title.replace(/<[^>]*>/g, '') })));
const adjacent = computed(() => {
  if (!frontmatter.value.id) return {};
  const articles = theme.value.sidebar.flatMap(group => group.items || []).filter(item => /^\/knowledge\/.+\.html$/.test(item.link || ''));
  const current = decodeURI(route.path).replace(site.value.base, '/');
  const index = articles.findIndex(item => item.link === current);
  return index < 0 ? {} : { previous: articles[index - 1], next: articles[index + 1] };
});

function openDrawer(event) {
  drawerTrigger = event.currentTarget;
  restoreDrawerFocus = true;
  drawer.value.showModal();
  document.documentElement.classList.add('has-dialog');
}
function closeDrawer(restore = true) {
  restoreDrawerFocus = restore;
  drawer.value?.close();
}
function afterDrawerClose() {
  if (!document.querySelector('dialog[open]')) document.documentElement.classList.remove('has-dialog');
  if (restoreDrawerFocus && drawerTrigger?.isConnected) drawerTrigger.focus({ preventScroll: true });
}
function drawerBackdrop(event) {
  if (event.target !== drawer.value) return;
  const box = drawer.value.getBoundingClientRect();
  if (event.clientX > box.right || event.clientY > box.bottom) closeDrawer();
}
function updateScroll() { showTop.value = window.scrollY > 1000; }
function focusContent() {
  let target = main.value;
  try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))) || target; } catch { /* A malformed fragment still reaches the main content. */ }
  if (!target) return;
  if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: true });
}
function hashNavigation() { requestAnimationFrame(focusContent); }
function watchHeadings() {
  observer?.disconnect();
  observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (visible[0]) activeHeading.value = visible[0].target.id;
  }, { rootMargin: '-80px 0px -55% 0px' });
  main.value?.querySelectorAll('h2[id],h3[id]').forEach(element => observer.observe(element));
  tableObserver?.disconnect();
  tableObserver = new ResizeObserver(entries => {
    for (const { target } of entries) {
      const overflow = target.scrollWidth > target.clientWidth + 1;
      target.toggleAttribute('data-overflow', overflow);
      target.tabIndex = overflow ? 0 : -1;
      target.setAttribute('aria-label', overflow ? '可横向滚动的数据表格' : '数据表格');
    }
  });
  main.value?.querySelectorAll('.table-region').forEach(element => tableObserver.observe(element));
}
watch(() => route.path, async () => {
  closeDrawer(false);
  if (mobileOutline.value) mobileOutline.value.open = false;
  activeHeading.value = '';
  await nextTick();
  watchHeadings();
  focusContent();
});
watch(isDark, dark => {
  if (typeof document !== 'undefined') document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#111113' : '#ffffff');
});
onMounted(() => {
  watchHeadings();
  updateScroll();
  window.addEventListener('scroll', updateScroll, { passive: true });
  window.addEventListener('hashchange', hashNavigation);
});
onBeforeUnmount(() => { observer?.disconnect(); tableObserver?.disconnect(); window.removeEventListener('scroll', updateScroll); window.removeEventListener('hashchange', hashNavigation); });
</script>

<template>
  <div class="fieldnotes-shell" :class="{ 'is-home': isHome }">
    <a class="skip-link" href="#main-content">跳到正文</a>
    <header class="site-header">
      <div class="site-header-inner">
        <a class="site-brand" :href="withBase('/')"><ThemeIcon name="book" :size="24" /><span>工程知识库</span></a>
        <nav class="primary-nav" aria-label="主要导航"><a v-for="link in links" :key="link.link" :href="withBase(link.link)" :aria-current="decodeURI(route.path).replace(site.base, '/') === link.link ? 'page' : undefined">{{ link.text }}</a></nav>
        <div class="header-actions">
          <KnowledgeSearch />
          <button class="icon-button theme-toggle" type="button" :aria-label="isDark ? '切换浅色模式' : '切换深色模式'" @click="isDark = !isDark"><ThemeIcon :name="isDark ? 'sun' : 'moon'" /></button>
          <button class="icon-button navigation-toggle" type="button" aria-label="打开知识目录" aria-haspopup="dialog" @click="openDrawer"><ThemeIcon name="menu" /></button>
        </div>
      </div>
    </header>
    <div v-if="!isHome" class="mobile-reading-bar">
      <button type="button" @click="openDrawer"><ThemeIcon name="menu" :size="16" />知识目录</button>
      <details v-if="headings.length" ref="mobileOutline" class="mobile-outline"><summary>本页目录<ThemeIcon name="down" :size="16" /></summary>
        <nav aria-label="本页目录"><a v-for="heading in headings" :key="heading.slug" :href="heading.link || `#${heading.slug}`" :class="{ nested: heading.level === 3 }" @click="mobileOutline.open = false">{{ heading.title }}</a></nav>
      </details>
    </div>
    <div class="reading-layout">
      <aside v-if="!isHome" class="desktop-sidebar"><KnowledgeSidebar /></aside>
      <main id="main-content" ref="main" tabindex="-1">
        <template v-if="page.isNotFound">
          <div class="not-found"><h1>没有找到这一页</h1><p>页面可能已移动。可以返回首页，或通过搜索寻找相关概念。</p><a :href="withBase('/')">返回首页<ThemeIcon name="arrow" :size="18" /></a></div>
        </template>
        <template v-else>
          <nav v-if="domain" class="article-breadcrumb" aria-label="当前位置"><a :href="withBase(`/knowledge/${domain.id}/`)">{{ domain.title }}</a><ThemeIcon name="chevron" :size="14" /><span>{{ frontmatter.kind === 'lab' ? '实验' : '正文' }}</span></nav>
          <Content :class="isHome ? 'home-content' : 'vp-doc'" />
          <nav v-if="adjacent.previous || adjacent.next" class="article-pager" aria-label="相邻文章">
            <a v-if="adjacent.previous" :href="withBase(adjacent.previous.link)"><small>上一篇</small><span>{{ adjacent.previous.text }}</span></a><span v-else />
            <a v-if="adjacent.next" :href="withBase(adjacent.next.link)" class="next"><small>下一篇</small><span>{{ adjacent.next.text }}</span></a>
          </nav>
          <footer id="来源与使用" class="reading-footer"><a :href="withBase('/rights.html')">正文 CC BY 4.0 · 代码 MIT</a><a :href="withBase('/updates.html')">阅读更新</a><a v-if="repository" :href="repository">GitHub 仓库</a><a v-if="theme.editLink && frontmatter.id" :href="theme.editLink.pattern.replace(':path', page.relativePath)">提出更正</a><span>Engineering Fieldnotes</span></footer>
        </template>
      </main>
      <aside v-if="!isHome && headings.length" class="desktop-outline"><nav aria-label="本页目录"><h2>本页目录</h2><a v-for="heading in headings" :key="heading.slug" :href="heading.link || `#${heading.slug}`" :class="{ nested: heading.level === 3 }" :aria-current="activeHeading === heading.slug ? 'location' : undefined">{{ heading.title }}</a></nav><a class="outline-top" href="#main-content">返回顶部<ThemeIcon name="up" :size="14" /></a></aside>
    </div>
    <ClientOnly>
      <Teleport to="body">
        <dialog ref="drawer" class="mobile-drawer" aria-labelledby="drawer-heading" @close="afterDrawerClose" @cancel.prevent="closeDrawer()" @keydown.esc.prevent="closeDrawer()" @click="drawerBackdrop">
          <header><h2 id="drawer-heading">知识目录</h2><button type="button" class="icon-button" aria-label="关闭知识目录" @click="closeDrawer()"><ThemeIcon name="close" /></button></header>
          <KnowledgeSidebar @navigate="closeDrawer(false)" />
        </dialog>
      </Teleport>
    </ClientOnly>
    <a v-if="showTop" class="back-to-top icon-button" href="#main-content" aria-label="返回顶部"><ThemeIcon name="up" /></a>
  </div>
</template>
